"""Projeção opt-in de evidências; preserva o relatório legado e seus brutos."""
from copy import deepcopy
from dataclasses import asdict, replace
from statistics import median, stdev

from .coverage import report_sufficiency
from .data_inventory import load_season
from .data_loader import DataError, LocalData
from .explanation import fingerprint
from .feature_engineering import METRICS, aggregate, match_features
from .metric_eligibility import FAMILIES, DIRECTIONAL, assess_game, quality_issues
from .recommendation_engine import hypotheses
from .season_audit import audit_orientation
from .temporal import select_history
from .v3_schema import VALIDATED_RECUTS


POLICY_VERSION = "quality-report-1"
QUALITY_CORE_METRICS = ("xg_for", "xg_against", "shots_for", "shots_against", "pass_accuracy")
REASON_TEXT = {
    "invalid_duration": "Duração inválida em evento da partida.",
    "invalid_location": "Localização inválida ou ausente para o indicador.",
    "invalid_movement_end": "Destino de movimento inválido ou ausente.",
    "orientation_not_established": "Orientação não estabelecida pela guarda operacional.",
    "season_not_certified": "Temporada sem certificação espacial; indicador direcional bloqueado.",
    "lineup_inconsistent": "Inconsistência entre jogador e escalação histórica.",
    "metric_unavailable": "Valor ou denominador indisponível no jogo.",
    "not_diagnosed": "Arquivo de eventos ausente na janela selecionada.",
}


def _filtered_metric(metric, allowed):
    rows = [deepcopy(row) for row in metric.per_match if row["match_id"] in allowed]
    numerator = sum(row["numerator"] for row in rows) if rows else None
    denominator = sum(row["denominator"] for row in rows) if rows else None
    _, unit, mode, _, _ = METRICS[metric.metric_id]
    multiplier = 90 if mode == "rate" else 100 if unit == "%" else 1
    values = [row["value"] for row in rows]
    return replace(metric, value=multiplier * numerator / denominator if rows else None,
                   sample_size=len(rows), match_ids=[row["match_id"] for row in rows],
                   numerator=numerator, denominator=denominator, median=median(values) if rows else None,
                   standard_deviation=stdev(values) if len(rows) > 1 else None, per_match=rows)


def apply_quality_policy(root, report):
    """Relê somente a janela selecionada e confere hashes antes de usar máscaras.

    A suficiência própria exige cinco jogos nos cinco indicadores básicos.
    Cada regra mantém suas exigências específicas. Não promove novos recortes V3.
    """
    if report.schema_version != "1.0.0":
        raise ValueError("A projeção de qualidade requer relatório básico.")
    data = LocalData(root)
    season = load_season(data, report.request.competition_id, report.request.season_id)
    histories, _ = select_history(season, report.request)
    expected = {s["path"]: s["sha256"] for s in report.methodology["sources"]}
    assessments = {}
    for mid, match in sorted({m["match_id"]: m for history in histories.values() for m in history}.items()):
        if not data.exists("events", mid):
            if f"events/{mid}.json" in expected:
                raise DataError("Os dados mudaram entre análise e filtro de qualidade.")
            # O legado pode ler essa escalação para validar indisponíveis,
            # mesmo quando o jogo está sem eventos. Conferir a mesma fonte.
            if f"lineups/{mid}.json" in expected:
                data.lineups(mid)
            continue
        events = data.events(mid)
        lineups = data.lineups(mid) if data.exists("lineups", mid) else None
        features, checks = match_features(match, events, lineups)
        diagnosis = {"core_quality": checks, "teams": []}
        for tid in features:
            profile = aggregate(tid, str(tid), [features[tid]], checks)
            diagnosis["teams"].append({"team_id": tid,
                "legacy_calculable": [k for k, m in profile.metrics.items() if m.value is not None],
                "v3_calculable": [], "sequence_calculable": []})
        assessments[mid] = assess_game(match, diagnosis, quality_issues(match, events),
                                       audit_orientation([(match, events)])["groups"], active_metrics=set(METRICS))
    if data.sources != expected:
        raise DataError("Os dados mudaram entre análise e filtro de qualidade; execute novamente.")
    certified = (report.request.competition_id, report.request.season_id) in VALIDATED_RECUTS
    filtered = deepcopy(report)
    details = []
    family_by_metric = {key: family for family, keys in FAMILIES.items() for key in keys}
    for side in ("team_profile", "opponent_profile"):
        profile = getattr(filtered, side)
        for key, original in getattr(report, side).metrics.items():
            family = family_by_metric[key]
            allowed, excluded, reasons = set(), [], {}
            for match in histories[profile.team_id]:
                mid = match["match_id"]
                row = assessments.get(mid, {}).get(profile.team_id)
                codes = list(row["blocked_families"].get(family, [])) if row else ["not_diagnosed"]
                if not certified and family in DIRECTIONAL:
                    codes.append("season_not_certified")
                if codes:
                    excluded.append(mid)
                    for code in set(codes):
                        reasons[code] = reasons.get(code, 0) + 1
                else:
                    allowed.add(mid)
            metric = _filtered_metric(original, allowed)
            profile.metrics[key] = metric
            details.append({"evidence_id": f"{side}.metrics.{key}", "metric_id": key,
                            "team_id": profile.team_id, "team_name": profile.team_name, "family": family,
                            "original_sample_size": original.sample_size, "usable_sample_size": metric.sample_size,
                            "selected_matches": len(histories[profile.team_id]),
                            "excluded_match_ids": excluded, "reason_counts": dict(sorted(reasons.items()))})
    sufficiency = asdict(report_sufficiency(filtered, core_metrics=QUALITY_CORE_METRICS))
    rules = hypotheses(filtered.team_profile, filtered.opponent_profile) if sufficiency["sufficient"] else []
    quality = {"policy_version": POLICY_VERSION, "applied": True,
               "scope": "selected_history_only", "full_snapshot_status": "not_checked",
               "spatial_season_certified": certified, "minimum_matches": sufficiency["minimum_matches"],
               "required_core_metrics": list(QUALITY_CORE_METRICS), "metrics": details,
               "reason_labels": REASON_TEXT,
               "limitations": ["Filtros locais da janela selecionada; não certificam a temporada nem eficácia tática.",
                               "Indicadores direcionais continuam bloqueados em temporadas não certificadas.",
                               "Ausências não viram zero e jogos excluídos não são repostos.",
                               "Cinco jogos é mínimo operacional, sem confiança estatística calibrada."]}
    mask_hash = fingerprint(quality)
    quality["mask_fingerprint"] = mask_hash
    engine = {"engine_id": "deterministic-quality", "engine_version": POLICY_VERSION,
              "contract": "service-quality-1", "sufficient": sufficiency["sufficient"],
              "input_fingerprint": fingerprint({"team": asdict(filtered.team_profile),
                                                  "opponent": asdict(filtered.opponent_profile), "mask": mask_hash}),
              "hypotheses": [asdict(rule) for rule in rules],
              "provenance": {"data_fingerprint": report.metadata["data_fingerprint"],
                             "sources": report.methodology["sources"], "quality_mask": mask_hash,
                             "core_metrics": list(QUALITY_CORE_METRICS)}}
    return filtered, quality, engine, sufficiency
