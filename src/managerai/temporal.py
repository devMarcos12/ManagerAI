"""Seleção histórica conservadora, independente dos resultados do alvo."""
from __future__ import annotations

from typing import Any

from .data_inventory import Season, team_ids
from .data_loader import DataError
from .report_schema import AnalysisRequest


def history_before(season: Season, team_id: int, cutoff_date: str, window: int,
                   excluded_match_id: int | None = None) -> list[dict[str, Any]]:
    """Últimas N partidas do calendário; nunca repõe ausências de eventos."""
    if team_id not in season.teams:
        raise DataError("Equipe não pertence à competição/temporada selecionada.")
    previous = [m for m in season.matches if team_id in team_ids(m)
                and m["match_date"] < cutoff_date[:10] and m["match_id"] != excluded_match_id]
    previous.sort(key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
    return previous[-window:]


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

    histories = {tid: history_before(season, tid, target_date, request.recent_matches_window,
                                     request.target_match_id)
                 for tid in (request.team_id, request.opponent_id)}
    return histories, cutoff
