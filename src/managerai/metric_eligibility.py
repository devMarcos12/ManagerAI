"""Diagnóstico por família; não certifica temporadas nem altera métricas.

Política posterior à auditoria exploratória, sem validação esportiva. Um valor
calculável só é elegível neste diagnóstico se suas dependências forem íntegras.
"""
from collections import Counter

from .data_inventory import team_ids
from .feature_engineering import METRICS, finite, point
from .report_schema import AnalysisRequest
from .temporal import select_history
from .v3_features import V3_METRICS


POLICY_VERSION = "metric-eligibility-1"
FAMILIES = {
    "shot_counts": ("shots_for", "shots_against"),
    "shot_quality": ("xg_for", "xg_against", "xg_per_shot"),
    "passing": ("pass_accuracy",),
    "passing_marked_pressure": ("pass_accuracy_under_pressure",),
    "passing_unmarked_pressure": ("pass_accuracy_unmarked_pressure",),
    "passing_explicit_no_pressure": ("pass_accuracy_explicit_no_pressure",),
    "movement_rates": ("final_third_entries", "final_third_attempts", "box_entries"),
    "pressure_rates": ("pressures", "counterpressures"),
    "pressure_space": ("pressure_high_share", "pressures_low_third", "pressures_middle_third",
                       "pressures_high_third", "pressures_low_third_share", "pressures_middle_third_share",
                       "pressures_high_third_share", "pressure_lane_low_share",
                       "pressure_lane_central_share", "pressure_lane_high_share"),
    "recovery_rates": ("recoveries", "interceptions", "duel_tackles", "recoveries_recorded",
                       "recoveries_explicit_failure", "recoveries_explicit_nonfailure"),
    "action_lanes": ("lane_low_y", "lane_central", "lane_high_y"),
    "pass_progression": ("progressive_passes", "final_third_pass_entries", "box_pass_entries"),
    "carry_progression": ("progressive_carries", "final_third_carry_entries", "box_carry_entries"),
    "entry_lanes": ("entry_lane_low_share", "entry_lane_central_share", "entry_lane_high_share"),
    "shot_locations": ("shots_box_share", "shots_outside_share", "xg_box", "xg_outside", "xg_per_located_shot"),
    "sequences": ("observed_blocks", "entry_block_share", "shot_block_share"),
}
DIRECTIONAL = frozenset({"movement_rates", "pressure_space", "pass_progression",
                         "carry_progression", "entry_lanes", "shot_locations"})
RATE_FAMILIES = frozenset(
    family for family, keys in FAMILIES.items()
    if any((METRICS[k][2] if k in METRICS else V3_METRICS.get(k, {}).get("aggregation")) == "rate"
           for k in keys)
)


def quality_issues(match, events):
    """Localiza campos problemáticos; sem corrigir/normalizar eventos-fonte."""
    issues = []

    def add(event, code, field, families, scope="team"):
        issues.append({"match_id": match["match_id"], "event_id": event.get("id"),
                       "event_index": event.get("index"), "period": event.get("period"),
                       "team_id": (event.get("team") or {}).get("id"),
                       "code": code, "field": field, "scope": scope,
                       "blocked_families": sorted(families)})

    for event in events:
        if event.get("period") not in (1, 2):
            continue
        duration = event.get("duration")
        if duration is not None and (not finite(duration) or duration < 0):
            add(event, "invalid_duration", "duration", RATE_FAMILIES, "match")
        name = (event.get("type") or {}).get("name")
        location = event.get("location")
        affected_start = {"action_lanes"} if location is not None and point(location) is None else set()
        if name in ("Pass", "Carry"):
            payload = event.get(name.lower())
            if not isinstance(payload, dict):
                continue  # A taxonomia registra a falha estrutural antes deste diagnóstico.
            family = "pass_progression" if name == "Pass" else "carry_progression"
            affected = {"movement_rates"}
            if name == "Carry" or not payload.get("outcome"):
                affected.update((family, "entry_lanes"))
            if point(location) is None:
                affected_start.update(affected)
            if point(payload.get("end_location")) is None:
                add(event, "invalid_movement_end", name.lower() + ".end_location", affected)
        elif name in ("Shot", "Pressure") and point(location) is None:
            family = "shot_locations" if name == "Shot" else "pressure_space"
            affected_start.add(family)
        if affected_start:
            add(event, "invalid_location", "location", affected_start)
    return issues


def assess_game(match, diagnosis, issues, orientation, *, active_metrics=None):
    """Separa ausência de valor, problemas de dependência e orientação."""
    assessed = {}
    for team in diagnosis["teams"]:
        tid = team["team_id"]
        available = set(team["legacy_calculable"]) | set(team["v3_calculable"]) | set(team["sequence_calculable"])
        groups = [g for g in orientation if g["team_id"] == tid]
        direction_ok = len(groups) == 2 and {g["period"] for g in groups} == {1, 2} and all(
            g["status"] == "coerente" for g in groups)
        blockers, missing = {}, {}
        active_families = set()
        for family, keys in FAMILIES.items():
            keys = set(keys) if active_metrics is None else set(keys) & set(active_metrics)
            if not keys:
                continue
            active_families.add(family)
            reasons = set()
            absent = sorted(set(keys) - available)
            if absent:
                reasons.add("metric_unavailable")
                missing[family] = absent
            for issue in issues:
                if family in issue["blocked_families"] and (issue["scope"] == "match" or issue["team_id"] == tid):
                    if issue["code"] == "invalid_duration" and not any(
                        (METRICS[k][2] if k in METRICS else V3_METRICS.get(k, {}).get("aggregation")) == "rate"
                        for k in keys):
                        continue
                    reasons.add(issue["code"])
            if diagnosis["core_quality"].get("event_player_not_in_match_lineup", 0):
                reasons.add("lineup_inconsistent")
            if family in DIRECTIONAL and not direction_ok:
                reasons.add("orientation_not_established")
            if reasons:
                blockers[family] = sorted(reasons)
        assessed[tid] = {"available_metrics": sorted(available),
                         "eligible_families": sorted(active_families - blockers.keys()),
                         "blocked_families": blockers, "unavailable_metrics": missing}
    return assessed


def block_duplicate_games(assessments, contaminated):
    """Um UUID compartilhado contamina também a primeira partida, sem fallback."""
    for mid in contaminated:
        for team in assessments.get(mid, {}).values():
            team["eligible_families"] = []
            for family in FAMILIES:
                team["blocked_families"][family] = sorted(
                    set(team["blocked_families"].get(family, [])) | {"cross_match_duplicate_event_id"})


def summarize_eligibility(season, assessments, issues, contaminated=()):
    """Janelas exatas do seletor de produção; lacunas nunca são repostas."""
    keys = [key for metrics in FAMILIES.values() for key in metrics]
    expected = set(METRICS) | set(V3_METRICS) | {"observed_blocks", "entry_block_share", "shot_block_share"}
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Mapeamento de famílias precisa cobrir cada indicador exatamente uma vez.")
    block_duplicate_games(assessments, contaminated)
    ordered = sorted(season.matches, key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
    summaries = {}
    for family, metrics in FAMILIES.items():
        available = eligible = 0
        blocked = Counter()
        for match in ordered:
            for tid in team_ids(match):
                row = assessments.get(match["match_id"], {}).get(tid)
                if row is None:
                    blocked["not_diagnosed"] += 1
                    continue
                available += set(metrics) <= set(row["available_metrics"])
                eligible += family in row["eligible_families"]
                blocked.update(row["blocked_families"].get(family, []))
        summaries[family] = {"metrics": list(metrics), "cataloged_team_games": 2 * len(ordered),
                             "available_team_games": available, "eligible_team_games": eligible,
                             "blocked_reason_counts": dict(sorted(blocked.items())), "windows": {}}
    for window in (5, 10):
        ids = {family: [] for family in FAMILIES}
        for target in ordered:
            home, away = team_ids(target)
            request = AnalysisRequest(season.competition_id, season.season_id, home, away,
                                      target_match_id=target["match_id"], recent_matches_window=window)
            history, _ = select_history(season, request)
            for family in FAMILIES:
                if all(len(history[tid]) == window and all(
                    family in assessments.get(m["match_id"], {}).get(tid, {}).get("eligible_families", [])
                    for m in history[tid]) for tid in (home, away)):
                    ids[family].append(target["match_id"])
        for family in FAMILIES:
            summaries[family]["windows"][f"h{window}"] = {"eligible_targets": len(ids[family]), "target_ids": ids[family]}
    return {"policy_version": POLICY_VERSION, "status": "diagnostic_not_certification",
            "interpretation": "Elegibilidade local por dependências; não libera V3 nem comprova validade esportiva.",
            "window_policy": "Mesma competição/temporada; últimas N partidas anteriores ao dia do alvo, sem reposição.",
            "families": summaries, "quality_issues": issues,
            "games": [{"match_id": mid, "teams": [{"team_id": tid, **row} for tid, row in sorted(teams.items())]}
                      for mid, teams in sorted(assessments.items())]}
