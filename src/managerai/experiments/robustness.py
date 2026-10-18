"""V4.3-C: walk-forward e ablação descritivos; nenhum novo teste independente.

Protocolo fixo: meses completos novembro/2015–maio/2016, expansão e janela
móvel de 90 dias. Todos os períodos já pertencem à análise A/B conhecida.
Não seleciona configuração, hiperparâmetro ou modelo vencedor pelos erros.
"""
from __future__ import annotations

import argparse
import calendar
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from hashlib import sha256
import importlib.metadata
import json
import math
from pathlib import Path
import platform

from .dataset import FEATURE_NAMES, SupervisedDataset, build_dataset, digest
from .models import _date, _pair, fit_regressions
from .paths import execution_code_hashes, project_root
from .robustness_diagnostics import paired_comparison, stability_diagnostics
from .runner import _git, _period

REFERENCE_SHA256 = "29688df92f7e06aadb393eec5c8c469a3b9ef9d07732055f95401d33812889a5"
REFERENCE_PROTOCOL = "36e230673236e7ec9ca73d6a0dc00cf6fda48f5c21600cd53006ec458c06b8bb"
REFERENCE_DATASET = "7b05d8df08b8f55388b9a5b73220dba7b33e77447c1d9fd39b8bc6bf988a99c5"
REFERENCE_RESULTS = "8875cafd996379f643c0064bd8c470846a27f4ad97dec4eb64b6d8fa788b1c94"
MODEL_IDS = ("historical_mean", "combined_means", "training_mean", "linear", "ridge",
             "linear_home_only", "ridge_home_only", "linear_away_only", "ridge_away_only")


def numerical_signature(value):
    """Assinatura com oito casas decimais para ruído numérico de BLAS.

    Não altera previsões ou métricas armazenadas. A assinatura inclui todos os
    resultados, IDs e evidências, e só ignora precisão inferior à registrada
    por essa regra. Metadados Git/ambiente ficam fora de results na A/B.
    """
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Resultado não finito na referência.")
        return round(value, 8)
    if isinstance(value, list):
        return [numerical_signature(v) for v in value]
    if isinstance(value, dict):
        return {k: numerical_signature(v) for k, v in value.items()}
    return value


def validate_reference(payload: bytes) -> dict:
    """Aceita A/B reconstruída com ciência congelada e metadados novos.

    O hash binário histórico continua registrado, mas não pode ser exigido de
    um novo clone: HEAD, caminhos e ambiente mudam legitimamente. Protocolo e
    dataset são exatos; resultados completos são conferidos a oito casas.
    """
    try:
        ab = json.loads(payload, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        if (digest(ab["protocol"]) != ab["protocol_fingerprint"]
                or digest(ab["dataset"]) != ab["dataset_fingerprint"]):
            raise ValueError("Fingerprint A/B inválido.")
        if (ab["protocol_fingerprint"] != REFERENCE_PROTOCOL
                or ab["dataset_fingerprint"] != REFERENCE_DATASET
                or digest(numerical_signature(ab["results"])) != REFERENCE_RESULTS):
            raise ValueError("Ciência da referência A/B diverge da versão congelada.")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Referência A/B incompleta ou inválida.") from exc
    return ab


@dataclass(frozen=True)
class MonthlyWindow:
    window_id: str
    scheme: str
    train_start: str | None
    evaluation_start: str
    evaluation_end: str
    minimum_training: int
    minimum_evaluation: int = 20

    def __post_init__(self):
        start = _date(self.evaluation_start, "evaluation_start")
        end = _date(self.evaluation_end, "evaluation_end")
        if end < start or not isinstance(self.window_id, str) or not self.window_id.strip():
            raise ValueError("Janela/data inválida.")
        if self.scheme not in ("expanding", "rolling90"):
            raise ValueError("Esquema desconhecido.")
        if self.train_start is not None and _date(self.train_start, "train_start") >= start:
            raise ValueError("Treino deve anteceder o mês de avaliação.")
        if (self.scheme == "expanding") != (self.train_start is None):
            raise ValueError("Esquema incompatível com início do treino.")
        if self.scheme == "rolling90" and (start - _date(self.train_start, "train_start")).days != 90:
            raise ValueError("Janela móvel exige exatamente 90 dias.")
        if (type(self.minimum_training) is not int or self.minimum_training < 3
                or type(self.minimum_evaluation) is not int or self.minimum_evaluation < 1):
            raise ValueError("Mínimos operacionais inválidos.")


def fixed_windows() -> tuple[MonthlyWindow, ...]:
    windows = []
    months = ((2015, 11), (2015, 12), *((2016, m) for m in range(1, 6)))
    for scheme, minimum in (("expanding", 50), ("rolling90", 30)):
        for year, month in months:
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            train_start = None if scheme == "expanding" else (start - timedelta(days=90)).isoformat()
            windows.append(MonthlyWindow(f"{scheme}_{start:%Y-%m}", scheme, train_start,
                                        start.isoformat(), end.isoformat(), minimum))
    return tuple(windows)


def select_window(examples, window: MonthlyWindow):
    """Seleciona por calendário, sem receber métricas nem escolher datas por y."""
    rows = tuple(sorted(examples, key=lambda e: (e.features.fixture.match_date, e.features.fixture.match_id)))
    if len({e.features.fixture.match_id for e in rows}) != len(rows):
        raise ValueError("Partida duplicada; não inflar a amostra.")
    train = tuple(e for e in rows if e.features.fixture.match_date < window.evaluation_start
                  and (window.train_start is None or e.features.fixture.match_date >= window.train_start))
    evaluation = tuple(e for e in rows if window.evaluation_start <= e.features.fixture.match_date <= window.evaluation_end)
    return train, evaluation


def project_features(values, group: str) -> tuple[float, float]:
    """Remoção experimental de colunas, aplicada antes de scaler/fit e previsão."""
    a, b = _pair(values, "features")
    if min(a, b) < 0:
        raise ValueError("Contagens históricas não negativas obrigatórias.")
    if group == "full":
        return a, b
    if group == "home_only":
        return a, 0.0
    if group == "away_only":
        return 0.0, b
    raise ValueError("Grupo de ablação desconhecido.")


def ablation_comparisons(predictions):
    """Mesmas partidas, comparação pareada de cada remoção com seu modelo completo."""
    return {family: paired_comparison([p["observed"] for p in predictions],
        {key: [p["predictions"][key] for p in predictions]
         for key in (family, f"{family}_home_only", f"{family}_away_only", "training_mean")}, reference=family)
        for family in ("linear", "ridge")}


def evaluate_window(examples, window: MonthlyWindow) -> dict:
    train, evaluation = select_window(examples, window)
    result = {"window": asdict(window), "training": _period(train), "evaluation": _period(evaluation)}
    if len(train) < window.minimum_training or len(evaluation) < window.minimum_evaluation:
        return {**result, "status": "blocked", "reason": "Amostra abaixo dos mínimos operacionais; sem previsões substitutas."}
    cutoff = (date.fromisoformat(window.evaluation_start) - timedelta(days=1)).isoformat()
    fitted = {}
    for group in ("full", "home_only", "away_only"):
        models = fit_regressions([project_features(e.features.values, group) for e in train],
            [e.label.home_shots for e in train], match_ids=[e.features.fixture.match_id for e in train],
            match_dates=[e.features.fixture.match_date for e in train], train_end=cutoff)
        for model in models:
            key = model.model_id if group == "full" else f"{model.model_id}_{group}"
            fitted[key] = (model, group)
    constant = math.fsum(e.label.home_shots / len(train) for e in train)
    predictions, clipped = [], {key: 0 for key in MODEL_IDS}
    for example in evaluation:
        fixture = example.features.fixture
        a, b = example.features.values
        raw = {"historical_mean": a, "combined_means": (a + b) / 2, "training_mean": constant,
               **{key: model.raw_predict(project_features(example.features.values, group))
                  for key, (model, group) in fitted.items()}}
        if not all(math.isfinite(value) for value in raw.values()):
            raise ValueError("Previsão não finita; interromper sem preenchimento.")
        for key, value in raw.items():
            clipped[key] += value < 0
        predictions.append({"match_id": fixture.match_id, "match_date": fixture.match_date,
            "home_team_id": fixture.home_team_id, "away_team_id": fixture.away_team_id,
            "observed": example.label.home_shots, "feature_fingerprint": example.features.fingerprint,
            "predictions": {key: max(0.0, raw[key]) for key in MODEL_IDS}})
    comparison = paired_comparison([p["observed"] for p in predictions],
                         {key: [p["predictions"][key] for p in predictions] for key in MODEL_IDS})
    return {**result, "status": "evaluated", "constant_training_mean": constant,
            "fitted_models": {key: {**asdict(model), "feature_group": group} for key, (model, group) in fitted.items()},
            "predictions": predictions, "comparison": comparison, "negative_predictions_clipped": clipped,
            "ablation_vs_full": ablation_comparisons(predictions)}


def evaluate_robustness(dataset: SupervisedDataset) -> dict:
    results = {}
    for scheme in ("expanding", "rolling90"):
        windows = [evaluate_window(dataset.examples, w) for w in fixed_windows() if w.scheme == scheme]
        predictions = [p for w in windows if w["status"] == "evaluated" for p in w["predictions"]]
        if len({p["match_id"] for p in predictions}) != len(predictions):
            raise ValueError("Origens de avaliação sobrepostas; não agregar previsões repetidas.")
        diagnostics = stability_diagnostics(predictions) if predictions else None
        comparisons = [w["comparison"] for w in windows if w["status"] == "evaluated"]
        stability = {}
        for key in MODEL_IDS:
            deltas = [c["models"][key]["delta_mae"] for c in comparisons]
            stability[key] = {"windows": len(deltas), "lower_mae_than_b1": sum(d < 0 for d in deltas),
                              "min_delta_mae": min(deltas) if deltas else None,
                              "max_delta_mae": max(deltas) if deltas else None}
        results[scheme] = {"status": "evaluated" if predictions else "blocked", "windows": windows,
                           "unique_evaluated_matches": len(predictions), "diagnostics": diagnostics,
                           "window_stability_vs_b1": stability,
                           "ablation_vs_full": ablation_comparisons(predictions) if predictions else None}
    ids_by_scheme = {name: set(value["diagnostics"]["match_ids"]) if value["diagnostics"] else set()
                     for name, value in results.items()}
    return {"schemes": results, "same_evaluation_ids_across_schemes": ids_by_scheme["expanding"] == ids_by_scheme["rolling90"],
            "common_evaluation_matches": len(ids_by_scheme["expanding"] & ids_by_scheme["rolling90"]),
            "interpretation": "Exploratório pós-A/B; não é novo teste independente.",
            "uncertainty": "Descritiva; sem IC/p-valor com poucos blocos e dependência de equipes/janelas.",
            "cross_scheme_policy": "Mesmas partidas em protocolos alternativos; nunca somar os Ns.",
            "no_automatic_selection": True}


def protocol() -> dict:
    return {"version": "4.3-c.1", "task": "pl_home_shots_pre_match", "feature_names": FEATURE_NAMES,
            "history_window": 5, "windows": [asdict(w) for w in fixed_windows()], "models": MODEL_IDS,
            "ridge_alpha": 1.0, "preprocessing": "z-score população por treino; coluna removida zero antes do fit",
            "prediction_policy": "max(0,raw), sem arredondar", "month_policy": "pesos congelados; histórico prequential diário",
            "minimum_sizes_are_not_power_analysis": True, "independent_new_test": False,
            "reference": "combined_means", "outlier_sensitivity": "ceil(5%n) maiores erros absolutos B1; n>=20; empate data/ID",
            "leave_out": "sem reajuste; um mês ou observação de avaliação por vez",
            "inference": "descritiva; sem IC, p-valor, escolha por resultado ou alegação causal"}


def run_robustness(data_root: str | Path, reference_artifact: str | Path, output_dir: str | Path) -> Path:
    """Reconstrói os brutos e referencia A/B; escreve um JSON em diretório novo."""
    root, reference, output = Path(data_root).resolve(), Path(reference_artifact).resolve(), Path(output_dir).resolve()
    project = project_root()
    protected_data = root.parent if (root.parent / ".git").exists() else root
    if (output.exists() or output == protected_data or output.is_relative_to(protected_data)
            or output == reference.parent or output.is_relative_to(reference.parent)
            or output.is_relative_to(project) and not output.is_relative_to(project / "outputs" / "runs")):
        raise ValueError("Resultado exige diretório novo fora dos dados e artefatos anteriores.")
    raw_reference = reference.read_bytes()
    reference_hash = sha256(raw_reference).hexdigest()
    ab = validate_reference(raw_reference)
    # Fixar o protocolo antes da leitura dos novos erros.
    configuration = protocol()
    dataset = build_dataset(root)
    dataset_fingerprint = digest(dataset.to_dict())
    if dataset_fingerprint != ab["dataset_fingerprint"]:
        raise ValueError("Dataset reconstruído diverge da referência A/B; interromper análise.")
    results = evaluate_robustness(dataset)
    code_hashes = execution_code_hashes()
    artifact = {"artifact_version": "4.3-c.1", "protocol": configuration, "protocol_fingerprint": digest(configuration),
        "reference": {"artifact": str(reference.relative_to(project)) if reference.is_relative_to(project) else str(reference), "sha256": reference_hash,
                      "historical_artifact_sha256": REFERENCE_SHA256,
                      "validation": "protocolo/dataset exatos; assinatura de todos resultados arredondados a oito casas",
                      "dataset_fingerprint": dataset_fingerprint, "protocol_fingerprint": ab["protocol_fingerprint"],
                      "sources": len(dataset.source_hashes), "dataset_examples": len(dataset.examples), "excluded": len(dataset.excluded)},
        "results": results, "reproduction": {"code_head": _git(project, "rev-parse", "HEAD"),
            "code_branch": _git(project, "branch", "--show-current"), "git_status": _git(project, "status", "--short"),
            "code_sha256": code_hashes, "pyproject_sha256": sha256((project / "pyproject.toml").read_bytes()).hexdigest(),
            "data_head": _git(root.parent, "rev-parse", "HEAD"), "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"), "platform": platform.platform(),
            "randomness": "nenhuma; solvers/alpha/janelas fixos; threads BLAS=1 no comando documentado"},
        "data_terms": {"source": "StatsBomb Open Data", "scope": "Pesquisa local não comercial; artefato não publicado.",
                       "distribution": "Requer confirmação de direitos própria; não publicar dados/previsões individuais por inferência."}}
    content = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    output.mkdir(parents=True, exist_ok=False)
    path = output / "run.json"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--reference-artifact", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_robustness(args.data_root, args.reference_artifact, args.output_dir)
    print(json.dumps({"artifact": str(result)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
