"""Orquestração sem dependência de rede, API, Parquet ou treinamento."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import __version__
from .data_inventory import load_season
from .data_loader import DataError, LocalData
from .feature_engineering import FORMULA_VERSION, MIN_SAMPLE, build_profiles, match_features
from .recommendation_engine import RULES_VERSION, hypotheses
from .report_schema import AnalysisReport, AnalysisRequest
from .tactical_analysis import compare, findings
from .temporal import select_history


def analyze(root: str | Path, request: AnalysisRequest, *, include_v3: bool = False) -> AnalysisReport:
    data = LocalData(root)
    season = load_season(data, request.competition_id, request.season_id)
    histories, cutoff = select_history(season, request)
    profiles, gaps = build_profiles(data, histories, season.teams)
    own, opponent = profiles[request.team_id], profiles[request.opponent_id]
    for label, profile in (("Equipe", own), ("Adversário", opponent)):
        if profile.sample_status == "insuficiente":
            gaps.append(f"{label}: amostra insuficiente ({len(profile.match_ids)} jogos; mínimo operacional {MIN_SAMPLE}).")
        for name, count in sorted(profile.quality.items()):
            if count:
                gaps.append(f"{label}: {name}={count}; consultar metodologia e dicionário de dados.")
        for key, metric in profile.metrics.items():
            if metric.sample_size < len(profile.match_ids):
                gaps.append(f"{label}: {key} calculável em {metric.sample_size}/{len(profile.match_ids)} jogos.")
    # Availability IDs must be grounded in this team's prior observed lineups.
    if request.unavailable_player_ids:
        eligible = set()
        for m in histories[request.team_id]:
            if data.exists("lineups", m["match_id"]):
                for t in data.lineups(m["match_id"]):
                    if t.get("team_id") == request.team_id:
                        eligible.update(p.get("player_id") for p in t.get("lineup", []))
        if set(request.unavailable_player_ids) - eligible:
            raise DataError("Jogador indisponível não observado nas escalações anteriores da equipe nesta janela.")
    gaps.extend([
        "Formação e escalação: não suportado pelos dados atuais; formações registradas não comprovam adequação tática ou disponibilidade.",
        "Eventos não equivalem a tracking; a análise não usa dados 360 nem posicionamento integral sem bola.",
        "Orientação preservada como registrada; corredores usam intervalos de y, sem inferir esquerda/direita tática.",
        "Ausência de marcação under_pressure é mantida separada de False explícito.",
        "Não há inferência de lesões, suspensões, rivalidade, importância competitiva ou mando real.",
    ])
    comparison = compare(own, opponent)
    proposed = hypotheses(own, opponent)
    if not proposed:
        gaps.append("Nenhuma hipótese emitida: amostra ou evidências não satisfazem as regras documentadas.")
    target = next((m for m in season.matches if m["match_id"] == request.target_match_id), None)
    report = AnalysisReport(
        metadata={"competition_id": season.competition_id, "season_id": season.season_id,
                  "competition": season.competition, "season": season.season,
                  "team": own.team_name, "opponent": opponent.team_name, "cutoff_date": cutoff,
                  "target_match_id": request.target_match_id,
                  "formal_home_team_id": target["home_team"]["home_team_id"] if target else None,
                  "matches_requested_team": len(histories[request.team_id]),
                  "matches_requested_opponent": len(histories[request.opponent_id]),
                  "matches_analyzed_team": len(own.match_ids), "matches_analyzed_opponent": len(opponent.match_ids),
                  "data_fingerprint": data.fingerprint(), "software_version": __version__},
        request=request, team_profile=own, opponent_profile=opponent, comparison=comparison,
        key_findings=findings(comparison), tactical_hypotheses=proposed,
        formation_options=[], lineup_options=[], data_gaps=sorted(set(gaps)),
        methodology={"baseline": "Determinístico e descritivo; sem treinamento ou inferência causal.",
                     "formula_version": FORMULA_VERSION, "rules_version": RULES_VERSION,
                     "minimum_sample_matches": MIN_SAMPLE,
                     "sample_policy": "Menos de 5 jogos: insuficiente. A partir de 5: evidência limitada, sem confiança probabilística.",
                     "temporal_policy": "Somente datas anteriores ao corte; mesmo dia excluído conservadoramente. Nunca lê eventos ou escalações do alvo.",
                     "window_policy": "Últimas N partidas agendadas anteriores; ausência de eventos não amplia a janela.",
                     "exposure": "Soma do maior timestamp + duration em cada período 1 e 2, em minutos; proxy de exposição observada, inclui acréscimos.",
                     "aggregation": "Médias por jogo para contagens/xG; taxas por 90 e proporções agregadas por soma dos numeradores/denominadores. Mediana e DP entre jogos válidos.",
                     "coordinates": "Plano StatsBomb 120×80, não metros. Coordenadas inválidas excluídas só dos cálculos espaciais.",
                     "context_policy": "Contexto e notas são declarações do treinador, não fatos verificados nem fatores causais.",
                     "player_policy": "Indisponibilidade manual validada nas escalações anteriores da janela; isso não comprova vínculo/aptidão atual.",
                     "sources": [{"path": path, "sha256": digest} for path, digest in sorted(data.sources.items())],
                     "attribution": "Fonte: StatsBomb Open Data; consultar README e LICENSE.pdf do conjunto local.",
                     "reporter": "Template determinístico em português; nenhuma chamada a LLM."})
    report.to_dict()
    if include_v3:
        from .v3_pipeline import extend_report
        return extend_report(root, report)
    return report


def audit(root: str | Path, competition_id: int, season_id: int) -> dict:
    data = LocalData(root)
    season = load_season(data, competition_id, season_id)
    quality: Counter = Counter()
    seen: set[str] = set()
    checked = []
    missing = []
    for match in sorted(season.matches, key=lambda m: m["match_id"]):
        mid = match["match_id"]
        if not data.exists("events", mid):
            missing.append(mid)
            continue
        events = data.events(mid)
        ids = {e.get("id") for e in events}
        if ids & seen:
            raise DataError("ID de evento duplicado entre partidas.")
        seen.update(ids)
        lineup = data.lineups(mid) if data.exists("lineups", mid) else None
        _, checks = match_features(match, events, lineup)
        quality.update(checks)
        quality["events_read"] += len(events)
        checked.append(mid)
    return {"competition_id": competition_id, "season_id": season_id,
            "matches_catalogued": len(season.matches), "matches_checked": len(checked),
            "missing_event_match_ids": missing, "quality": dict(quality),
            "data_fingerprint": data.fingerprint(),
            "status": "com_lacunas" if missing or any(v for k, v in quality.items() if k != "events_read") else "sem_lacunas_detectadas",
            "scope": "Checagens estruturais e de campos usados pelo baseline; não certifica semântica tática nem completude comercial."}
