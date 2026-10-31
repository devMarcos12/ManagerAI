"""Consolidar evidência histórica pequena; não treina, avalia ou copia pesos."""
import argparse
from hashlib import sha256
import json
from pathlib import Path


def file_hash(path):
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def collect(root):
    runs = root/"outputs/runs"
    result = {"kind": "historical_artifacts_integrity_check", "new_training_or_evaluation": False, "artifacts": []}
    for relative in ("core_ai_lora_20261031", "core_ai_independent_installed_20261031"):
        folder = runs/relative
        evaluation = folder/"evaluation.json"
        entry = {"path": str(evaluation.relative_to(root)), "available": evaluation.is_file()}
        if evaluation.is_file():
            data = json.loads(evaluation.read_text())
            entry["evaluation_sha256"] = file_hash(evaluation)
            if "training" in data:
                manifest = folder/"manifest.json"
                entry["manifest_sha256"] = file_hash(manifest)
                config = json.loads(manifest.read_text())
                entry.update(model=config["model"], revision=config["revision"],
                    configuration=config["protocol"]["explanation"]["training"],
                    steps=data["training"]["steps"],
                    splits={k:len(v) for k,v in config["partitions"].items()},
                    metrics={key:{"n":data[key]["n"],"exact_validity_and_coverage":data[key]["exact_validity_and_coverage"],
                                  "human_reviews":data[key]["human_clarity_or_utility_reviews"]} for key in ("base","fine_tuned","validation")},
                    promoted=data["promoted"], adapter_hashes={})
                for name, expected in data["artifacts_sha256"].items():
                    path = folder/name
                    found = file_hash(path) if path.is_file() else None
                    entry["adapter_hashes"][name] = {"sha256":found,"matches_stored":found==expected}
                dataset = json.loads((folder/"dataset.json").read_text())
                canonical = json.dumps(dataset, ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(",",":"))
                entry["dataset_matches_manifest"] = sha256(canonical.encode()).hexdigest()==config["dataset_fingerprint"]
            else:
                entry.update(protocol_fingerprint=data["protocol_fingerprint"], train_n=len(data["train"]["ids"]),
                             test_n=len(data["test"]["ids"]),metrics={k:{"mae":v["mae"],"n":v["n"]} for k,v in data["metrics"].items()},
                             decisions=data["decisions"])
        result["artifacts"].append(entry)
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="docs/research_evidence.json")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    text=json.dumps(collect(root),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    target=root/args.output
    if args.check:
        if not target.is_file() or target.read_text()!=text:
            raise SystemExit("Evidência local diverge; confira disponibilidade/hashes antes de atualizar.")
        print("Evidência histórica e hashes conferidos, sem novo treinamento.")
    else:
        target.write_text(text,encoding="utf-8")
        print(target)
