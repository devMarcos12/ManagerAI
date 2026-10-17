"""Catálogo suportado é definido por metadados, nunca por JSONs órfãos."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, time
from typing import Any

from .data_loader import DataError, LocalData


@dataclass(frozen=True)
class Season:
    competition_id: int
    season_id: int
    competition: str
    season: str
    matches: list[dict[str, Any]]
    teams: dict[int, str]


def team_ids(match: dict[str, Any]) -> tuple[int, int]:
    return match["home_team"]["home_team_id"], match["away_team"]["away_team_id"]


def load_season(data: LocalData, competition_id: int, season_id: int) -> Season:
    catalog = data.read("competitions.json")
    entries = [c for c in catalog if (c.get("competition_id"), c.get("season_id")) == (competition_id, season_id)]
    if len(entries) != 1:
        raise DataError("Competição/temporada inexistente ou duplicada no catálogo local.")
    comp = entries[0]
    matches = data.read(f"matches/{competition_id}/{season_id}.json")
    seen: set[int] = set()
    teams: dict[int, str] = {}
    for m in matches:
        try:
            mid = m["match_id"]
            if type(mid) is not int or mid <= 0 or mid in seen:
                raise ValueError("match_id inválido ou duplicado")
            seen.add(mid)
            if m["competition"]["competition_id"] != competition_id or m["season"]["season_id"] != season_id:
                raise ValueError("competição/temporada incompatível")
            date.fromisoformat(m["match_date"])
            if m.get("kick_off"):
                time.fromisoformat(m["kick_off"])
            h, a = team_ids(m)
            if h == a:
                raise ValueError("confronto da equipe consigo mesma")
            for side, tid in (("home", h), ("away", a)):
                name = m[f"{side}_team"][f"{side}_team_name"]
                if type(tid) is not int or tid <= 0 or not isinstance(name, str) or not name:
                    raise ValueError("equipe inválida")
                if tid in teams and teams[tid] != name:
                    raise ValueError("nome inconsistente para team_id")
                teams[tid] = name
        except (KeyError, TypeError, ValueError) as exc:
            raise DataError(f"Metadados de partida inválidos: {exc}") from exc
    return Season(competition_id, season_id, comp["competition_name"], comp["season_name"], matches, teams)


def inventory(data: LocalData) -> dict[str, Any]:
    catalog = data.read("competitions.json")
    seen_pairs: set[tuple[int, int]] = set()
    all_ids: set[int] = set()
    rows: list[dict[str, Any]] = []
    for c in catalog:
        pair = c.get("competition_id"), c.get("season_id")
        if pair in seen_pairs:
            raise DataError("Par competição/temporada duplicado no catálogo.")
        seen_pairs.add(pair)
        season = load_season(data, *pair)
        mids = {m["match_id"] for m in season.matches}
        if all_ids & mids:
            raise DataError("Partida duplicada entre temporadas.")
        all_ids.update(mids)
        coverage = {k: sum(data.exists(k, mid) for mid in mids) for k in ("events", "lineups", "three-sixty")}
        counts = Counter(t for m in season.matches for t in team_ids(m))
        rows.append({"competition_id": pair[0], "season_id": pair[1], "competition": season.competition,
                     "season": season.season, "matches": len(mids), "coverage": coverage,
                     "analyzable_matches": sum(data.exists("events", mid) for mid in mids),
                     "teams": [{"team_id": tid, "name": name, "matches": counts[tid]} for tid, name in sorted(season.teams.items())]})
    files = {k: {p.stem for p in (data.root / k).glob("*.json")} for k in ("events", "lineups", "three-sixty")}
    known = set(map(str, all_ids))
    return {"seasons": rows, "total_matches": len(all_ids),
            "file_counts": {k: len(v) for k, v in files.items()},
            "unreferenced_file_ids": {k: sorted(v - known) for k, v in files.items()},
            "scope": "Presença de arquivos; conteúdo de eventos/escalações validado ao analisar ou auditar o recorte."}
