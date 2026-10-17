"""Indicadores por jogo: eventos observáveis, sem interpretação causal."""
from __future__ import annotations

from collections import Counter
import math
from statistics import median, stdev
from typing import Any

from .data_inventory import team_ids
from .data_loader import DataError, LocalData
from .report_schema import MetricEvidence, TeamProfile

FORMULA_VERSION = "1.0.0"
MIN_SAMPLE = 5

# Aggregation is explicit: mean per match, pooled rate per 90, or pooled ratio.
METRICS = {
    "xg_for": ("xG a favor", "xG/jogo", "mean", "xg_for", None),
    "xg_against": ("xG contra", "xG/jogo", "mean", "xg_against", None),
    "shots_for": ("Finalizações a favor", "eventos/jogo", "mean", "shots_for", None),
    "shots_against": ("Finalizações contra", "eventos/jogo", "mean", "shots_against", None),
    "xg_per_shot": ("xG por chute", "xG/chute", "ratio", "xg_for", "shots_for"),
    "pass_accuracy": ("Acerto de passe", "%", "ratio", "passes_completed", "passes"),
    "pass_accuracy_under_pressure": ("Acerto com pressão marcada", "%", "ratio", "pressure_completed", "pressure_passes"),
    "pass_accuracy_explicit_no_pressure": ("Acerto com ausência explícita de pressão", "%", "ratio", "no_pressure_completed", "no_pressure_passes"),
    "pass_accuracy_unmarked_pressure": ("Acerto com pressão não marcada", "%", "ratio", "unmarked_completed", "unmarked_passes"),
    "final_third_entries": ("Entradas no terço final por passe completo/condução", "eventos/90", "rate", "final_third_entries", "minutes"),
    "final_third_attempts": ("Tentativas de entrada no terço final", "eventos/90", "rate", "final_third_attempts", "minutes"),
    "box_entries": ("Entradas na área por passe completo/condução", "eventos/90", "rate", "box_entries", "minutes"),
    "pressures": ("Eventos de pressão", "eventos/90", "rate", "pressures", "minutes"),
    "pressure_high_share": ("Pressões no terço ofensivo", "%", "ratio", "pressure_high", "pressure_located"),
    "counterpressures": ("Pressure com contrapressão marcada", "eventos/90", "rate", "counterpressures", "minutes"),
    "recoveries": ("Eventos de recuperação", "eventos/90", "rate", "recoveries", "minutes"),
    "interceptions": ("Eventos de interceptação", "eventos/90", "rate", "interceptions", "minutes"),
    "duel_tackles": ("Duelos do tipo Tackle", "eventos/90", "rate", "duel_tackles", "minutes"),
    "lane_low_y": ("Ações localizadas em y menor que 80/3", "%", "ratio", "lane_low_y", "located"),
    "lane_central": ("Ações localizadas no corredor central", "%", "ratio", "lane_central", "located"),
    "lane_high_y": ("Ações localizadas em y maior ou igual a 160/3", "%", "ratio", "lane_high_y", "located"),
}


def finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def point(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, list) or len(value) < 2:
        return None
    x, y = value[:2]
    return (x, y) if finite(x) and finite(y) and 0 <= x <= 120 and 0 <= y <= 80 else None


def in_box(p: tuple[float, float]) -> bool:
    return p[0] >= 102 and 18 <= p[1] <= 62


def seconds(timestamp: str) -> float:
    try:
        h, m, s = timestamp.split(":")
        result = int(h) * 3600 + int(m) * 60 + float(s)
        if not math.isfinite(result) or result < 0 or not 0 <= int(m) < 60 or not 0 <= float(s) < 60:
            raise ValueError()
        return result
    except (AttributeError, TypeError, ValueError) as exc:
        raise DataError("Timestamp de evento inválido.") from exc


def match_features(match: dict[str, Any], events: list[dict[str, Any]], lineups: list[dict[str, Any]] | None) -> tuple[dict[int, dict[str, Any]], dict[str, int]]:
    tids = team_ids(match)
    quality: Counter[str] = Counter()
    if not events:
        raise DataError(f"Partida {match['match_id']} sem eventos.")
    if lineups is None:
        quality["missing_lineup_files"] += 1
        roster = None
    else:
        if len(lineups) != 2 or {x.get("team_id") for x in lineups} != set(tids):
            raise DataError("Equipes de escalação incompatíveis com a partida.")
        roster = {}
        for team in lineups:
            players = team.get("lineup")
            if not isinstance(players, list):
                raise DataError("Escalação deve conter uma lista de jogadores.")
            ids = [p.get("player_id") for p in players]
            if any(type(x) is not int or x <= 0 for x in ids) or len(set(ids)) != len(ids):
                raise DataError("IDs de jogadores ausentes, inválidos ou duplicados na escalação.")
            roster[team["team_id"]] = set(ids)
    rows = {tid: Counter() for tid in tids}
    seen_ids, seen_index = set(), set()
    ends: dict[int, float] = {}
    xg_missing = Counter()
    for e in events:
        eid, index = e.get("id"), e.get("index")
        if not isinstance(eid, str) or not eid or eid in seen_ids:
            raise DataError("ID de evento ausente ou duplicado na partida.")
        if type(index) is not int or index in seen_index:
            raise DataError("Índice de evento inválido ou duplicado na partida.")
        seen_ids.add(eid); seen_index.add(index)
        tid = (e.get("team") or {}).get("id")
        if tid not in rows:
            raise DataError("Equipe de evento incompatível com a partida.")
        if e.get("possession_team") and e["possession_team"].get("id") not in tids:
            raise DataError("Equipe de posse incompatível com a partida.")
        pid = (e.get("player") or {}).get("id")
        if pid is not None and roster is not None and pid not in roster[tid]:
            quality["event_player_not_in_match_lineup"] += 1
        if e.get("period") not in (1, 2):
            quality["events_excluded_other_periods"] += 1
            continue
        period = e["period"]
        clock = seconds(e.get("timestamp"))
        duration = e.get("duration", 0)
        if duration is None:
            duration = 0
        if not finite(duration) or duration < 0:
            # Preserve the action, but never extend exposure using bad duration.
            quality["durations_invalid"] += 1
            duration = 0
        ends[period] = max(ends.get(period, 0), clock + duration)
        r = rows[tid]
        r["events"] += 1
        typ = (e.get("type") or {}).get("name")
        if not isinstance(typ, str) or not typ:
            raise DataError("Tipo de evento ausente ou inválido.")
        start = point(e.get("location"))
        if e.get("location") is None:
            quality["locations_missing"] += 1
        elif start is None:
            quality["locations_invalid"] += 1
        if start:
            r["located"] += 1
            r["lane_low_y" if start[1] < 80/3 else "lane_central" if start[1] < 160/3 else "lane_high_y"] += 1
        if typ == "Shot":
            r["shots_for"] += 1
            xg = (e.get("shot") or {}).get("statsbomb_xg")
            if finite(xg) and 0 <= xg <= 1:
                r["xg_for"] += xg
            else:
                xg_missing[tid] += 1
                quality["shots_missing_or_invalid_xg"] += 1
        if typ == "Pass":
            payload = e.get("pass")
            if not isinstance(payload, dict):
                raise DataError("Evento Pass sem objeto pass.")
            completed = not bool(payload.get("outcome"))
            r["passes"] += 1
            r["passes_completed"] += completed
            pressure = e.get("under_pressure")
            if pressure is not None and type(pressure) is not bool:
                raise DataError("under_pressure deve ser booleano ou ausente.")
            prefix = "pressure" if pressure is True else "no_pressure" if pressure is False else "unmarked"
            r[f"{prefix}_passes"] += 1
            r[f"{prefix}_completed"] += completed
        elif typ == "Carry":
            payload = e.get("carry")
            if not isinstance(payload, dict):
                raise DataError("Evento Carry sem objeto carry.")
            completed = True
        else:
            payload = None
            completed = False
        if payload is not None:
            end = point(payload.get("end_location"))
            if payload.get("end_location") is None:
                quality["movement_end_missing"] += 1
            elif end is None:
                quality["movement_end_invalid"] += 1
            if start and end:
                crossed = start[0] < 80 <= end[0]
                r["final_third_attempts"] += crossed
                r["final_third_entries"] += crossed and completed
                r["box_entries"] += not in_box(start) and in_box(end) and completed
        if typ == "Pressure":
            r["pressures"] += 1
            r["counterpressures"] += e.get("counterpress") is True
            if start:
                r["pressure_located"] += 1
                r["pressure_high"] += start[0] >= 80
        r["recoveries"] += typ == "Ball Recovery"
        r["interceptions"] += typ == "Interception"
        r["duel_tackles"] += typ == "Duel" and (e.get("duel", {}).get("type") or {}).get("name") == "Tackle"
    if set(ends) != {1, 2} or any(ends[p] <= 0 for p in ends):
        raise DataError("Partida sem exposição válida nos dois tempos regulamentares.")
    minutes = sum(ends.values()) / 60
    result = {}
    for tid, opponent in (tids, tids[::-1]):
        r = dict(rows[tid])
        if not r.get("events"):
            raise DataError("Equipe sem eventos regulamentares.")
        # Initialize zero counts only after validating the event stream.
        for _, _, _, num, den in METRICS.values():
            r.setdefault(num, 0)
            if den:
                r.setdefault(den, 0)
        r["xg_for"] = None if xg_missing[tid] else rows[tid]["xg_for"]
        r["xg_against"] = None if xg_missing[opponent] else rows[opponent]["xg_for"]
        r["shots_against"] = rows[opponent]["shots_for"]
        r.update(match_id=match["match_id"], match_date=match["match_date"], minutes=minutes)
        result[tid] = r
    return result, dict(quality)


def aggregate(tid: int, name: str, rows: list[dict[str, Any]], quality: dict[str, int]) -> TeamProfile:
    metrics = {}
    for mid, (_, unit, mode, num, den) in METRICS.items():
        valid = [r for r in rows if r.get(num) is not None and (den is None or r.get(den, 0) > 0)]
        multiplier = 90 if mode == "rate" else 100 if unit == "%" else 1
        values = [r[num] if mode == "mean" else multiplier * r[num] / r[den] for r in valid]
        numerator = sum(r[num] for r in valid) if valid else None
        denominator = (len(valid) if mode == "mean" else sum(r[den] for r in valid)) if valid else None
        value = multiplier * numerator / denominator if valid else None
        metrics[mid] = MetricEvidence(mid, value, unit, len(valid), [r["match_id"] for r in valid], numerator, denominator,
                                     median(values) if values else None, stdev(values) if len(values) > 1 else None,
                                     [{"match_id": r["match_id"], "match_date": r["match_date"], "value": v,
                                       "numerator": r[num], "denominator": 1 if den is None else r[den]} for r, v in zip(valid, values)], FORMULA_VERSION)
    return TeamProfile(tid, name, [r["match_id"] for r in rows], rows[0]["match_date"] if rows else None,
                       rows[-1]["match_date"] if rows else None, "limitada" if len(rows) >= MIN_SAMPLE else "insuficiente", metrics, quality)


def build_profiles(data: LocalData, histories: dict[int, list[dict[str, Any]]], names: dict[int, str]) -> tuple[dict[int, TeamProfile], list[str]]:
    cache: dict[int, tuple[dict[int, dict[str, Any]], dict[str, int]]] = {}
    global_ids: set[str] = set()
    profiles = {}
    gaps: list[str] = []
    for tid, history in histories.items():
        rows = []
        quality: Counter[str] = Counter()
        for match in history:
            mid = match["match_id"]
            if not data.exists("events", mid):
                quality["missing_event_files"] += 1
                gaps.append(f"Partida {mid}: arquivo de eventos ausente; janela não foi ampliada para compensar.")
                continue
            if mid not in cache:
                events = data.events(mid)
                event_ids = {e.get("id") for e in events}
                if global_ids & event_ids:
                    raise DataError("ID de evento duplicado entre partidas.")
                global_ids.update(event_ids)
                lineups = data.lineups(mid) if data.exists("lineups", mid) else None
                cache[mid] = match_features(match, events, lineups)
            features, checks = cache[mid]
            rows.append(features[tid]); quality.update(checks)
        profiles[tid] = aggregate(tid, names[tid], rows, dict(quality))
    return profiles, sorted(set(gaps))
