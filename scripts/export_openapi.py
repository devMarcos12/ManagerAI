"""Gerar/conferir OpenAPI sem servidor, dataset, provedor ou rede."""
import argparse
import json
from pathlib import Path
from managerai.api import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="frontend/openapi.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(create_app().openapi(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    target = Path(args.output)
    if args.check:
        if not target.exists() or target.read_text() != content:
            raise SystemExit("OpenAPI divergente: execute scripts/export_openapi.py e npm run types.")
        print("OpenAPI corresponde ao backend.")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
