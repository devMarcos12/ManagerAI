"""Comparações descritivas; unidades e amostras acompanham cada diferença."""
from __future__ import annotations

from .feature_engineering import METRICS
from .report_schema import TeamProfile


def compare(own: TeamProfile, opponent: TeamProfile) -> list[dict]:
    result = []
    for key in METRICS:
        a, b = own.metrics[key], opponent.metrics[key]
        result.append({"metric_id": key, "label": METRICS[key][0], "unit": a.unit,
                       "team_value": a.value, "opponent_value": b.value,
                       "difference_team_minus_opponent": a.value - b.value if a.value is not None and b.value is not None else None,
                       "team_sample_size": a.sample_size, "opponent_sample_size": b.sample_size,
                       "evidence_metrics": [f"team_profile.metrics.{key}", f"opponent_profile.metrics.{key}"]})
    return result


def findings(comparison: list[dict]) -> list[dict]:
    keys = {"xg_for", "xg_against", "final_third_entries", "pressures"}
    return [{"kind": "observação", "description": f"Comparação descritiva: {row['label'].lower()}.",
             "metric_id": row["metric_id"], "team_value": row["team_value"], "opponent_value": row["opponent_value"],
             "unit": row["unit"], "evidence_metrics": row["evidence_metrics"],
             "limitations": ["Janelas podem ter adversários e datas distintos; diferença não implica superioridade tática."]}
            for row in comparison if row["metric_id"] in keys and row["team_value"] is not None and row["opponent_value"] is not None]
