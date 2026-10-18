"""Execução local V4.3-A/B, separada da CLI pública e da interface Streamlit."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess

from .dataset import (FEATURE_NAMES, TASK_ID, TASK_VERSION, WINDOW, Example,
                      QuantitativePrediction, SupervisedDataset, build_dataset, digest)
from .models import evaluate_predictions, fit_regressions
from .paths import execution_code_hashes, project_root

TRAIN_END = "2016-02-06"
VALIDATION_END = "2016-04-03"
TEST_START = "2016-04-09"
MODEL_IDS = ("historical_mean", "combined_means", "linear", "ridge")


@dataclass(frozen=True)
class TemporalSplits:
    train: tuple[Example, ...]
    validation: tuple[Example, ...]
    test: tuple[Example, ...]


def split_examples(examples, *, train_end=TRAIN_END, validation_end=VALIDATION_END,
                   test_start=TEST_START) -> TemporalSplits:
    """Limites fixos antes de y; datas inteiras nunca são divididas."""
    if not date.fromisoformat(train_end) < date.fromisoformat(validation_end) < date.fromisoformat(test_start):
        raise ValueError("Fronteiras temporais incompatíveis.")
    rows = tuple(sorted(examples, key=lambda e: (e.features.fixture.match_date, e.features.fixture.match_id)))
    if len({e.features.fixture.match_id for e in rows}) != len(rows):
        raise ValueError("Partida duplicada nas partições.")
    groups = {"train": [], "validation": [], "test": []}
    for row in rows:
        day = row.features.fixture.match_date
        if day <= train_end:
            groups["train"].append(row)
        elif day <= validation_end:
            groups["validation"].append(row)
        elif day >= test_start:
            groups["test"].append(row)
        else:
            raise ValueError("Partida no intervalo entre validação e teste; rever protocolo antes de treinar.")
    return TemporalSplits(*(tuple(groups[k]) for k in ("train", "validation", "test")))


def _period(rows):
    days = [e.features.fixture.match_date for e in rows]
    teams = sorted({tid for e in rows for tid in (e.features.fixture.home_team_id, e.features.fixture.away_team_id)})
    return {"n": len(rows), "start": min(days) if days else None, "end": max(days) if days else None,
            "team_ids": teams, "team_count": len(teams), "match_ids": [e.features.fixture.match_id for e in rows]}


def _deltas(metrics):
    result = {}
    for model_id, values in metrics.items():
        result[model_id] = {}
        for baseline_id in MODEL_IDS[:2]:
            reference = metrics[baseline_id]["mae"]
            delta = values["mae"] - reference
            result[model_id][baseline_id] = {"mae_difference": delta,
                "mae_difference_percent": 100 * delta / reference if reference else None}
    return result


def evaluate_dataset(dataset: SupervisedDataset) -> dict:
    """Recebe dataset congelado; fit recebe SOMENTE as linhas do treino.

    Validação e teste são avaliação, sem seleção/tuning ou reajuste de escala.
    Histórico prequential é atualizado por partidas já ocorridas; pesos fixos.
    """
    splits = split_examples(dataset.examples)
    periods = {k: _period(getattr(splits, k)) for k in ("train", "validation", "test")}
    if len(splits.train) < 30 or len(splits.validation) < 10 or len(splits.test) < 20:
        return {"status": "blocked", "reason": "Mínimos pré-fixados: treino30/validação10/teste20; não certificados como poder estatístico.",
                "partitions": periods}
    models = fit_regressions([e.features.values for e in splits.train], [e.label.home_shots for e in splits.train],
              match_ids=[e.features.fixture.match_id for e in splits.train],
              match_dates=[e.features.fixture.match_date for e in splits.train], train_end=TRAIN_END)
    fitted = {m.model_id: m for m in models}
    predictions = []
    scores = {}
    for partition in ("validation", "test"):
        rows = getattr(splits, partition)
        y = [e.label.home_shots for e in rows]
        values = {key: [] for key in MODEL_IDS}
        raw_values = {key: [] for key in MODEL_IDS}
        for row in rows:
            a, b = row.features.values
            raw = {"historical_mean": a, "combined_means": (a + b) / 2,
                   **{k: fitted[k].raw_predict(row.features.values) for k in fitted}}
            sources = tuple(sorted({source for h in (*row.features.home_history, *row.features.away_history) for source in h.sources}))
            for model_id in MODEL_IDS:
                if not math.isfinite(raw[model_id]):
                    raise ValueError("Previsão não finita; não preencher artificialmente.")
                value = max(0.0, raw[model_id])
                pred = QuantitativePrediction(model_id, row.features.fixture.match_id, row.features.fixture.match_date,
                          value, row.features.fingerprint, sources)
                values[model_id].append(value)
                raw_values[model_id].append(raw[model_id])
                predictions.append({**asdict(pred), "partition": partition, "observed": row.label.home_shots,
                                    "raw_prediction": raw[model_id], "error": value - row.label.home_shots})
        metrics = {key: evaluate_predictions(y, values[key]) for key in MODEL_IDS}
        monthly = {}
        for month in sorted({e.features.fixture.match_date[:7] for e in rows}):
            indices = [i for i, e in enumerate(rows) if e.features.fixture.match_date.startswith(month)]
            monthly[month] = {"n": len(indices), "interpretation": "descritivo; não demonstra robustez por período",
                             "metrics": {k: evaluate_predictions([y[i] for i in indices], [values[k][i] for i in indices])
                                         for k in MODEL_IDS} if len(indices) >= 10 else None}
        scores[partition] = {"metrics": metrics, "mae_comparisons": _deltas(metrics), "monthly": monthly,
                            "negative_predictions_clipped": {k: sum(v < 0 for v in raw_values[k]) for k in MODEL_IDS}}
    return {"status": "evaluated", "partitions": periods, "fitted_models": [asdict(m) for m in models],
            "evaluation": scores, "predictions": predictions,
            "limitations": ["Estimativas observacionais com poucas partidas e dependência temporal/equipes.",
                            "Sem margem mínima útil pré-aprovada nem intervalo de incerteza estimado; diferença numérica não demonstra superioridade.",
                            "Prever finalizações não avalia tática ideal nem eficácia causal de estratégia."]}


def _git(path, *args):
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def run_experiment(data_root: str | Path, output_dir: str | Path) -> Path:
    """Cria somente run.json em destino novo; nunca publica ou sobrescreve."""
    data_root, output_dir = Path(data_root).resolve(), Path(output_dir).resolve()
    project = project_root()
    data_protected = data_root.parent if (data_root.parent / ".git").exists() else data_root
    protected = (data_protected, project / "src", project / "tests", project / "docs",
                 project / "scripts", project / "outputs" / "statsbomb_eda_20261002_exec6",
                 project / "outputs" / "mvp_demo_city_arsenal",
                 project / "outputs" / "v3_demo_city_arsenal",
                 project / "outputs" / "v3_demo_real_madrid_barcelona")
    project_destination_invalid = output_dir.is_relative_to(project) and not output_dir.is_relative_to(project / "outputs" / "runs")
    if project_destination_invalid or output_dir.exists() or any(output_dir == p or output_dir.is_relative_to(p) for p in protected):
        raise ValueError("Resultado exige diretório novo fora dos dados, código e artefatos protegidos.")
    # Configuração/limites predefinidos, antes de construir ou avaliar labels.
    protocol = {"task_id": TASK_ID, "task_version": TASK_VERSION, "competition_id": 2, "season_id": 27,
                "window": WINDOW, "minimum_history": WINDOW, "feature_names": FEATURE_NAMES,
                "train_end": TRAIN_END, "validation_end": VALIDATION_END, "test_start": TEST_START,
                "models": MODEL_IDS, "ridge_alpha": 1.0, "preprocessing": "zscore população somente treino; constante scale1",
                "negative_prediction_policy": "max(0, raw), todos modelos; sem arredondamento",
                "intraday_policy": "dia inteiro excluído do histórico; empate de calendário por ID",
                "evaluation_mode": "prequential com pesos/transformadores congelados; validação somente avaliação",
                "delta_convention": "MAE modelo menos MAE baseline; negativo é menor erro; percentual null se referência zero",
                "minimum_partition_sizes": {"train": 30, "validation": 10, "test": 20}}
    dataset = build_dataset(data_root)
    result = evaluate_dataset(dataset)
    code_hashes = execution_code_hashes()
    artifact = {"artifact_version": "1.0.0", "protocol": protocol, "protocol_fingerprint": digest(protocol),
                "dataset": dataset.to_dict(), "dataset_fingerprint": digest(dataset.to_dict()), "results": result,
                "reproduction": {"code_head": _git(project, "rev-parse", "HEAD"),
                  "git_status": _git(project, "status", "--short"), "code_sha256": code_hashes,
                  "pyproject_sha256": sha256((project / "pyproject.toml").read_bytes()).hexdigest(),
                  "data_head": _git(data_root.parent, "rev-parse", "HEAD"),
                  "dependencies": {"python": platform.python_version(), "numpy": importlib.metadata.version("numpy")},
                  "platform": platform.platform(), "randomness": "nenhuma seleção/embaralhamento/treino estocástico",
                  "solvers": {"linear": "numpy.linalg.lstsq rcond=None", "ridge": "numpy.linalg.solve alpha1"}},
                "data_terms": {"attribution": "StatsBomb Open Data", "purpose": "experimento local de pesquisa não comercial",
                  "restrictions": "Dados/derivados não publicados; conferir LICENSE.pdf antes de distribuição ou uso comercial."}}
    raw = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    output_dir.mkdir(parents=True, exist_ok=False)
    destination = output_dir / "run.json"
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(raw)
    return destination


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_experiment(args.data_root, args.output_dir)
    print(json.dumps({"artifact": str(result)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
