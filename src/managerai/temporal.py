"""Seleção histórica conservadora, independente dos resultados do alvo."""
from __future__ import annotations

from typing import Any

from .data_inventory import Season, team_ids
from .data_loader import DataError
from .report_schema import AnalysisRequest


def select_history(season: Season, request: AnalysisRequest) -> tuple[dict[int, list[dict[str, Any]]], str]:
    if (request.competition_id, request.season_id) != (season.competition_id, season.season_id):
        raise DataError("Recorte da requisição incompatível com a temporada.")
    if any(t not in season.teams for t in (request.team_id, request.opponent_id)):
        raise DataError("Equipe não pertence à competição/temporada selecionada.")
    if request.target_match_id is not None:
        target = next((m for m in season.matches if m["match_id"] == request.target_match_id), None)
        if target is None or set(team_ids(target)) != {request.team_id, request.opponent_id}:
            raise DataError("Partida-alvo não corresponde ao confronto e recorte selecionados.")
        target_date = target["match_date"]
        target_time = target.get("kick_off")
        cutoff = f"{target_date}T{target_time}" if target_time else target_date
    else:
        target_date = request.cutoff_date
        target_time = None
        cutoff = target_date

    def earlier(m: dict[str, Any]) -> bool:
        if m["match_id"] == request.target_match_id:
            return False
        if m["match_date"] < target_date:
            return True
        # Dates have no verified timezone/end-of-match guarantee in this MVP.
        # Exclude the whole target day, including fixtures with earlier starts.
        return False

    histories = {}
    for tid in (request.team_id, request.opponent_id):
        previous = [m for m in season.matches if tid in team_ids(m) and earlier(m)]
        previous.sort(key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
        histories[tid] = previous[-request.recent_matches_window:]
    return histories, cutoff
