"""Leitura dos JSONs brutos, sem mutação e com digest do conteúdo lido."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


class DataError(ValueError):
    """Dados locais ausentes ou inconsistentes."""


class LocalData:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.sources: dict[str, str] = {}

    def read(self, relative: str) -> list[dict[str, Any]]:
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise DataError("Caminho fora da raiz dos dados.")
        try:
            raw = path.read_bytes()
            data = json.loads(raw)
        except (OSError, ValueError) as exc:
            raise DataError(f"Não foi possível ler {relative}: {exc}") from exc
        if not isinstance(data, list) or any(not isinstance(x, dict) for x in data):
            raise DataError(f"{relative}: esperado array de objetos JSON.")
        self.sources[relative] = sha256(raw).hexdigest()
        return data

    def exists(self, kind: str, match_id: int) -> bool:
        return (self.root / kind / f"{match_id}.json").is_file()

    def events(self, match_id: int) -> list[dict[str, Any]]:
        return self.read(f"events/{match_id}.json")

    def lineups(self, match_id: int) -> list[dict[str, Any]]:
        return self.read(f"lineups/{match_id}.json")

    def fingerprint(self) -> str:
        canonical = json.dumps(self.sources, sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode()).hexdigest()
