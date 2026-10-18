"""Regressões experimentais pequenas, isoladas do runtime tático legado.

OLS e Ridge (alpha=1) usam dois atributos, intercepto e padronização ajustados
exclusivamente nos exemplos fornecidos de treinamento. Não há tuning ou ajuste
na validação/teste. NumPy só é importado quando se solicita treinamento.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import math
from numbers import Real
from typing import Sequence


def _number(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label}: esperado número real finito.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label}: esperado número real finito.")
    return result


def _pair(values, label: str) -> tuple[float, float]:
    try:
        result = tuple(values)
    except TypeError as exc:
        raise ValueError(f"{label}: esperados dois atributos.") from exc
    if len(result) != 2:
        raise ValueError(f"{label}: esperados dois atributos.")
    return (_number(result[0], label), _number(result[1], label))


def _date(value, label: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{label}: esperada data ISO YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}: esperada data ISO YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{label}: esperada data ISO YYYY-MM-DD.")
    return parsed


@dataclass(frozen=True)
class LinearModel:
    """Modelo congelado; coeficientes operam sobre (X-mean)/scale.

    O intercepto não é penalizado. ``raw_predict`` permite auditar a regressão;
    ``predict`` aplica a regra pré-fixada max(0, previsão) a qualquer modelo.
    IDs identificam os únicos exemplos usados para ajustar pesos e escalas.
    """

    model_id: str
    intercept: float
    coefficients: tuple[float, float]
    mean: tuple[float, float]
    scale: tuple[float, float]
    training_match_ids: tuple[int, ...]
    train_end: str
    ridge_alpha: float

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id obrigatório.")
        _number(self.intercept, "intercept")
        for name in ("coefficients", "mean", "scale"):
            value = getattr(self, name)
            if not isinstance(value, tuple):
                raise ValueError(f"{name}: esperada tupla imutável.")
            _pair(value, name)
        if any(s <= 0 for s in self.scale):
            raise ValueError("Escalas devem ser estritamente positivas.")
        ids = self.training_match_ids
        if (not isinstance(ids, tuple) or len(ids) < 3
                or any(type(i) is not int or i <= 0 for i in ids)
                or len(set(ids)) != len(ids)):
            raise ValueError("Esperados ao menos três IDs positivos únicos.")
        _date(self.train_end, "train_end")
        if _number(self.ridge_alpha, "ridge_alpha") < 0:
            raise ValueError("ridge_alpha não pode ser negativo.")

    def raw_predict(self, values: Sequence[float]) -> float:
        """Calcula a previsão finita sem truncar resultados negativos."""
        pair = _pair(values, "features")
        try:
            result = float(self.intercept + math.fsum(
                coefficient * ((value - mean) / scale)
                for value, mean, scale, coefficient in zip(
                    pair, self.mean, self.scale, self.coefficients)))
        except (OverflowError, ValueError) as exc:
            raise ValueError("Previsão não finita.") from exc
        if not math.isfinite(result):
            raise ValueError("Previsão não finita.")
        return result

    def predict(self, values: Sequence[float]) -> float:
        """Retorna previsão contínua não negativa; não arredonda contagens."""
        return max(0.0, self.raw_predict(values))


def fit_regressions(x_train, y_train, *, match_ids, match_dates,
                    train_end: str = "2016-02-06") -> tuple[LinearModel, LinearModel]:
    """Ajusta OLS e Ridge alpha=1 somente nas linhas de treino recebidas.

    Exige Nx2 finito, N>=3, y não negativo e metadados alinhados. Toda data deve
    ser <=train_end. A função não recebe validação/teste nem escolhe parâmetros.
    Constantes recebem escala 1; desvio populacional usa ddof=0. OLS usa mínimos
    quadrados SVD; Ridge resolve o sistema regularizado com intercepto separado.
    """
    cutoff = _date(train_end, "train_end")
    try:
        rows = tuple(_pair(row, "X_train") for row in x_train)
        targets = tuple(_number(y, "y_train") for y in y_train)
        ids, dates = tuple(match_ids), tuple(match_dates)
    except TypeError as exc:
        raise ValueError("Treino e metadados devem ser sequências alinhadas.") from exc
    if len(rows) < 3 or any(len(values) != len(rows) for values in (targets, ids, dates)):
        raise ValueError("Esperados N>=3 exemplos e metadados alinhados.")
    if any(y < 0 for y in targets):
        raise ValueError("Alvos não podem ser negativos.")
    if any(type(i) is not int or i <= 0 for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("IDs devem ser inteiros positivos únicos.")
    if any(_date(d, "match_date") > cutoff for d in dates):
        raise ValueError("Treinamento contém partida posterior ao limite permitido.")

    import numpy as np

    x, y = np.asarray(rows, dtype=float), np.asarray(targets, dtype=float)
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            mean = x.mean(axis=0)
            scale = x.std(axis=0, ddof=0)
            scale = np.where(scale == 0.0, 1.0, scale)
            z = (x - mean) / scale
            design = np.column_stack((np.ones(len(rows)), z))
            ols, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
            y_mean = y.mean()
            ridge = np.linalg.solve(z.T @ z + np.eye(2), z.T @ (y - y_mean))
        except (FloatingPointError, np.linalg.LinAlgError) as exc:
            raise ValueError("Ajuste numérico inválido; não produzir modelo substituto.") from exc
    common = dict(mean=tuple(float(v) for v in mean),
                  scale=tuple(float(v) for v in scale),
                  training_match_ids=ids, train_end=train_end)
    return (
        LinearModel("linear", float(ols[0]), tuple(float(v) for v in ols[1:]),
                    ridge_alpha=0.0, **common),
        LinearModel("ridge", float(y_mean), tuple(float(v) for v in ridge),
                    ridge_alpha=1.0, **common),
    )


def _distribution(values: Sequence[float]) -> dict[str, float]:
    """Quantil linear: posição (n-1)*p, interpolação entre vizinhos ordenados."""
    ordered = sorted(values)

    def quantile(p):
        position = (len(ordered) - 1) * p
        lo, hi = math.floor(position), math.ceil(position)
        fraction = position - lo
        return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction

    return {"min": ordered[0], "p10": quantile(.10), "p25": quantile(.25),
            "median": quantile(.50), "p75": quantile(.75),
            "p90": quantile(.90), "max": ordered[-1]}


def evaluate_predictions(observed, predicted) -> dict:
    """Calcula erros em chutes/jogo; viés positivo significa superestimação.

    Distribuições assinada/absoluta usam quantis lineares definidos acima. Não
    estima intervalos IID: partidas e históricos compartilhados são dependentes.
    """
    try:
        targets = tuple(_number(v, "observed") for v in observed)
        estimates = tuple(_number(v, "predicted") for v in predicted)
    except TypeError as exc:
        raise ValueError("Observados e previstos devem ser sequências.") from exc
    if not targets or len(targets) != len(estimates):
        raise ValueError("Esperadas sequências não vazias e de mesmo tamanho.")
    if any(v < 0 for v in (*targets, *estimates)):
        raise ValueError("Observações e previsões devem ser não negativas.")
    errors = tuple(p - y for y, p in zip(targets, estimates))
    absolute = tuple(abs(e) for e in errors)
    n = len(errors)
    try:
        # Dividir antes de somar evita overflow de somas com resultado finito.
        mae = math.fsum(v / n for v in absolute)
        bias = math.fsum(v / n for v in errors)
        rmse = math.hypot(*(v / math.sqrt(n) for v in errors))
    except (OverflowError, ValueError) as exc:
        raise ValueError("Métricas não finitas.") from exc
    if not all(math.isfinite(v) for v in (mae, bias, rmse)):
        raise ValueError("Métricas não finitas.")
    return {"n": n, "mae": mae, "rmse": rmse, "bias": bias,
            "distribution": {"signed": _distribution(errors),
                             "absolute": _distribution(absolute)}}
