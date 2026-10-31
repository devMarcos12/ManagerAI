"""CORE-03: avaliação pré-fixada entre competições; nunca promoção automática."""
import argparse
from dataclasses import asdict
from pathlib import Path
import time

from ..explanation import canonical, fingerprint
from ..statsbomb_provisioning import verify_snapshot
from .dataset import build_shots_dataset
from .models import fit_regressions, evaluate_predictions
from .artifacts import new_run_dir
from .paths import execution_code_hashes


def run(root, protocol_path, destination):
    import json
    protocol = json.loads(Path(protocol_path).read_text())
    cfg = protocol["quantitative"]
    out = new_run_dir(destination, data_root=root)
    code_hashes = execution_code_hashes()
    started = time.monotonic()
    verification = verify_snapshot(root)
    if verification["status"] != "compatível":
        raise ValueError("Snapshot incompatível.")
    train_data = build_shots_dataset(root, *cfg["train_pair"])
    test_data = build_shots_dataset(root, *cfg["test_pair"])
    train = [e for e in train_data.examples if e.features.fixture.match_date <= cfg["train_end"]]
    test = [e for e in test_data.examples if e.features.fixture.match_date >= cfg["test_start"]]
    ids = lambda rows: [e.features.fixture.match_id for e in rows]
    if set(ids(train)) & set(ids(test)) or len(test) < cfg["minimum_test_matches"]:
        raise ValueError("Partições inválidas ou teste insuficiente.")
    fitted = fit_regressions([e.features.values for e in train], [e.label.home_shots for e in train],
                             match_ids=ids(train), match_dates=[e.features.fixture.match_date for e in train],
                             train_end=cfg["train_end"])
    rows = []
    for e in test:
        a, b = e.features.values
        values = {"B0": a, "B1": (a+b)/2, **{m.model_id: m.predict(e.features.values) for m in fitted}}
        rows.append({"match_id": e.features.fixture.match_id, "date": e.features.fixture.match_date,
                     "observed": e.label.home_shots, "features_fingerprint": e.features.fingerprint,
                     "predictions": values})
    metrics = {key: evaluate_predictions([r["observed"] for r in rows], [r["predictions"][key] for r in rows])
               for key in rows[0]["predictions"]}
    for r in rows:
        r["paired_absolute_error_difference_vs_B1"] = {
            k: abs(v-r["observed"])-abs(r["predictions"]["B1"]-r["observed"])
            for k, v in r["predictions"].items()}
    monthly = {}
    for month in sorted({r["date"][:7] for r in rows}):
        group = [r for r in rows if r["date"].startswith(month)]
        monthly[month] = {"n": len(group), "metrics": {
            k: evaluate_predictions([r["observed"] for r in group], [r["predictions"][k] for r in group]) for k in metrics}}
    decisions = {}
    for m in fitted:
        gain = metrics["B1"]["mae"] - metrics[m.model_id]["mae"]
        decisions[m.model_id] = {"absolute_gain": gain, "relative_gain": gain/metrics["B1"]["mae"],
            "useful_threshold_met": gain >= cfg["minimum_useful_gain_absolute"] and gain/metrics["B1"]["mae"] >= cfg["minimum_useful_gain_relative"],
            "production": False, "reason": "Sem validação esportiva; previsão não avalia decisões táticas."}
    result = {"protocol": protocol, "protocol_fingerprint": fingerprint(protocol), "code_sha256": code_hashes,
        "train": {"ids": ids(train), "audit": train_data.audit, "excluded": [asdict(e) for e in train_data.excluded],
                  "dataset_fingerprint": fingerprint(train_data.to_dict()), "sources": train_data.source_hashes},
        "test": {"ids": ids(test), "audit": test_data.audit, "excluded": [asdict(e) for e in test_data.excluded],
                 "dataset_fingerprint": fingerprint(test_data.to_dict()), "sources": test_data.source_hashes},
        "models": [asdict(m) for m in fitted], "metrics": metrics, "monthly": monthly,
        "predictions": rows, "decisions": decisions, "duration_seconds": time.monotonic()-started,
        "limitations": [cfg["interpretation"], "Auditoria específica do alvo de contagem; não certifica V3.",
                         "Sem IC/p-valor IID; janelas e equipes dependentes."]}
    (out/"evaluation.json").write_text(canonical(result), encoding="utf-8")
    return {"train_n": len(train), "test_n": len(test), "metrics": metrics, "decisions": decisions}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--protocol", required=True)
    p.add_argument("--output-dir", required=True)
    a = p.parse_args()
    print(canonical(run(a.data_root, a.protocol, a.output_dir)))
