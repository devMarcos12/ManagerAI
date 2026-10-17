"""Três famílias observáveis; sem causalidade, tracking ou troca de orientação.

Contrato adicional V3. O fluxo V1/V2 permanece a fonte da exposição observada.
Uma lacuna espacial torna indisponíveis os contadores dependentes daquele tipo
de evento na partida; não transforma movimentos desconhecidos em zero.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from math import hypot
from statistics import median, stdev
from typing import Any

from .feature_engineering import finite, in_box, point
from .report_schema import MetricEvidence

FORMULA_VERSION = "3.0.0"
PROGRESSIVE_DISTANCE = 10.0
V3_METRICS: dict[str, dict[str, str]] = {}


def _register(key: str, label: str, family: str, definition: str, mode: str = "rate") -> None:
    V3_METRICS[key] = {"label": label, "family": family, "definition": definition,
                       "unit": "%" if mode == "share" else "xG/chute" if mode == "ratio" else
                               "xG/jogo" if mode == "mean" else "eventos/90",
                       "aggregation": mode}


for kind, title in (("pass", "passe completo"), ("carry", "condução")):
    _register(f"progressive_{kind}es" if kind == "pass" else "progressive_carries",
              f"Progressões por {title}", "progression",
              f"{title.capitalize()} com início/fim válidos e redução de pelo menos 10 unidades "
              "na distância euclidiana à meta registrada (120,40); unidades StatsBomb, não metros.")
    _register(f"final_third_{kind}_entries", f"Avanços ao terço de ataque por {title}", "progression",
              f"{title.capitalize()}: início x<80 e destino x>=80, com coordenadas válidas.")
    _register(f"box_{kind}_entries", f"Entradas na área por {title}", "progression",
              f"{title.capitalize()}: início fora da área e destino em x>=102, 18<=y<=62.")
for lane, title in (("low", "faixa de y baixo"), ("central", "faixa central"), ("high", "faixa de y alto")):
    _register(f"entry_lane_{lane}_share", f"Avanços ao terço de ataque pela {title}", "progression",
              "Proporção dos destinos dos avanços ao terço de ataque por passe completo/condução. "
              "Faixas: y<80/3, 80/3<=y<160/3, y>=160/3; sem significado de esquerda/direita.", "share")
    _register(f"pressure_lane_{lane}_share", f"Tentativas de pressão na {title}", "pressure",
              "Proporção das localizações de Pressure pelas faixas y<80/3, 80/3<=y<160/3, y>=160/3. "
              "Não mede sucesso nem posicionamento contínuo.", "share")
for zone, title in (("box", "dentro da área"), ("outside", "fora da área")):
    _register(f"shots_{zone}_share", f"Finalizações {title}", "shots",
              "Proporção de finalizações localizadas na zona; área x>=102, 18<=y<=62.", "share")
    _register(f"xg_{zone}", f"Gols esperados em finalizações {title}", "shots",
              "Soma de xG válido dos chutes na zona por partida; lacuna espacial ou de xG invalida a soma.", "mean")
_register("xg_per_located_shot", "Qualidade média das finalizações localizadas", "shots",
          "Soma de xG / chutes localizados; exige localização e xG válidos em todos os chutes da partida.", "ratio")
for zone, title in (("low", "terço de origem"), ("middle", "terço intermediário"), ("high", "terço de ataque")):
    _register(f"pressures_{zone}_third_share", f"Tentativas de pressão no {title}", "pressure",
              "Proporção das localizações de Pressure pelos intervalos x<40, 40<=x<80 e x>=80. "
              "A tentativa registrada não comprova êxito.", "share")
    _register(f"pressures_{zone}_third", f"Tentativas de pressão no {title} por 90", "pressure",
              "Contagem de Pressure localizado no intervalo espacial por exposição observada de 90 minutos.")
for suffix, title, definition in (
    ("recorded", "Recuperações registradas", "Eventos Ball Recovery, sem inferir posse consolidada."),
    ("explicit_failure", "Recuperações com falha explícita", "Ball Recovery com recovery_failure=True."),
    ("explicit_nonfailure", "Recuperações sem falha explicitamente marcada", "Ball Recovery com recovery_failure=False; ausência da marcação não equivale a False."),
):
    _register(f"recoveries_{suffix}", title, "pressure", definition)


def _lane(y: float) -> str:
    return "low" if y < 80/3 else "central" if y < 160/3 else "high"


def analyze_match_v3(match: dict, events: list, team_id: int,
                     exposure_minutes: float | None) -> dict:
    """Eventos do próprio time, apenas períodos 1/2; nunca acessa outros arquivos."""
    counts: Counter = Counter()
    quality: Counter = Counter()
    invalid: set[str] = set()
    shots = []
    observed_team_events = 0
    movement_keys = {kind: (f"progressive_{kind}es" if kind == "pass" else "progressive_carries",
                            f"final_third_{kind}_entries", f"box_{kind}_entries") for kind in ("pass", "carry")}
    entry_keys = {key for key in V3_METRICS if key.startswith("entry_lane_")}
    pressure_keys = {key for key in V3_METRICS if key.startswith("pressure")}
    shot_keys = {key for key in V3_METRICS if key.startswith("shots_") or key.startswith("xg_")}
    for event in events:
        if not isinstance(event, dict):
            quality["non_object_events"] += 1
            continue
        team = event.get("team")
        if not isinstance(team, dict) or team.get("id") != team_id:
            continue
        if event.get("period") not in (1, 2):
            quality["events_excluded_other_periods"] += 1
            continue
        observed_team_events += 1
        typ = event.get("type")
        name = typ.get("name") if isinstance(typ, dict) else None
        if name in ("Pass", "Carry"):
            kind = name.lower()
            payload = event.get(kind)
            if not isinstance(payload, dict):
                quality[f"{kind}_payload_missing"] += 1
                invalid.update(movement_keys[kind]); invalid.update(entry_keys)
                continue
            if name == "Pass" and payload.get("outcome"):
                continue
            start, end = point(event.get("location")), point(payload.get("end_location"))
            if start is None or end is None:
                quality[f"{kind}_geometry_missing_or_invalid"] += 1
                invalid.update(movement_keys[kind]); invalid.update(entry_keys)
                continue
            counts[f"valid_{kind}_movements"] += 1
            progressive, third, box = movement_keys[kind]
            counts[progressive] += hypot(120-start[0], 40-start[1]) - hypot(120-end[0], 40-end[1]) >= PROGRESSIVE_DISTANCE
            entered = start[0] < 80 <= end[0]
            counts[third] += entered
            counts[box] += not in_box(start) and in_box(end)
            if entered:
                counts["entries_located"] += 1
                counts[f"entry_lane_{_lane(end[1])}_share"] += 1
        elif name == "Shot":
            location = point(event.get("location"))
            payload = event.get("shot")
            xg = payload.get("statsbomb_xg") if isinstance(payload, dict) else None
            valid_xg = finite(xg) and 0 <= xg <= 1
            if not valid_xg:
                quality["shots_xg_missing_or_invalid"] += 1
                invalid.update({"xg_box", "xg_outside", "xg_per_located_shot"})
            if location is None:
                quality["shots_geometry_missing_or_invalid"] += 1
                invalid.update(shot_keys)
                continue
            zone = "box" if in_box(location) else "outside"
            counts["shots_located"] += 1
            counts[f"shots_{zone}_share"] += 1
            if valid_xg:
                counts[f"xg_{zone}"] += xg
                counts["xg_per_located_shot"] += xg
            shots.append({"id": event.get("id"), "match_id": match["match_id"], "team_id": team_id,
                          "period": event["period"], "x": location[0], "y": location[1],
                          "xg": xg if valid_xg else None})
        elif name == "Pressure":
            location = point(event.get("location"))
            if location is None:
                quality["pressures_geometry_missing_or_invalid"] += 1
                invalid.update(pressure_keys)
                continue
            counts["pressures_located"] += 1
            x, y = location
            zone = "low" if x < 40 else "middle" if x < 80 else "high"
            counts[f"pressures_{zone}_third"] += 1
            counts[f"pressures_{zone}_third_share"] += 1
            counts[f"pressure_lane_{_lane(y)}_share"] += 1
        elif name == "Ball Recovery":
            counts["recoveries_recorded"] += 1
            payload = event.get("ball_recovery")
            failure = payload.get("recovery_failure") if isinstance(payload, dict) else None
            if failure is True:
                counts["recoveries_explicit_failure"] += 1
            elif failure is False:
                counts["recoveries_explicit_nonfailure"] += 1
            elif failure is not None:
                quality["recovery_failure_invalid"] += 1
                invalid.update({"recoveries_explicit_failure", "recoveries_explicit_nonfailure"})
            else:
                quality["recovery_failure_unmarked"] += 1
        elif not name:
            quality["event_type_missing"] += 1
            invalid.update(V3_METRICS)
    if not observed_team_events:
        quality["team_events_unavailable"] += 1
        invalid.update(V3_METRICS)
    exposure = exposure_minutes if finite(exposure_minutes) and exposure_minutes > 0 else None
    if exposure is None:
        quality["exposure_missing_or_invalid"] += 1
    metrics = {}
    for key, meta in V3_METRICS.items():
        mode = meta["aggregation"]
        denominator = exposure if mode == "rate" else 1 if mode == "mean" else (
            counts["entries_located"] if key.startswith("entry_lane") else
            counts["pressures_located"] if "pressure" in key else counts["shots_located"])
        numerator = None if key in invalid else counts[key]
        multiplier = 90 if mode == "rate" else 100 if mode == "share" else 1
        value = multiplier * numerator / denominator if numerator is not None and denominator else None
        metrics[key] = {"value": value, "numerator": numerator, "denominator": denominator}
    return {"match_id": match["match_id"], "match_date": match["match_date"], "team_id": team_id,
            "minutes": exposure, "metrics": metrics, "shots": shots, "quality": dict(quality)}


def aggregate_v3(team_id: int, team_name: str, rows: list[dict]) -> dict:
    """Taxas/proporções por soma dos denominadores; n é específico por métrica."""
    if any(row["team_id"] != team_id for row in rows):
        raise ValueError("Linha V3 de outra equipe.")
    if len({row["match_id"] for row in rows}) != len(rows):
        raise ValueError("Partida repetida no agregado V3.")
    rows = sorted(rows, key=lambda row: (row["match_date"], row["match_id"]))
    metrics = {}
    for key, meta in V3_METRICS.items():
        valid = [(row, row["metrics"].get(key)) for row in rows]
        valid = [(row, m) for row, m in valid if m and m["value"] is not None
                 and m["numerator"] is not None and m["denominator"] is not None and m["denominator"] > 0]
        numerator = sum(m["numerator"] for _, m in valid) if valid else None
        denominator = sum(m["denominator"] for _, m in valid) if valid else None
        mode = meta["aggregation"]
        multiplier = 90 if mode == "rate" else 100 if mode == "share" else 1
        values = [m["value"] for _, m in valid]
        metrics[key] = asdict(MetricEvidence(
            metric_id=key, value=multiplier*numerator/denominator if valid else None,
            unit=meta["unit"], sample_size=len(valid), match_ids=[row["match_id"] for row, _ in valid],
            numerator=numerator, denominator=denominator,
            median=median(values) if values else None,
            standard_deviation=stdev(values) if len(values) > 1 else None,
            per_match=[{"match_id": row["match_id"], "match_date": row["match_date"], **m} for row, m in valid],
            formula_version=FORMULA_VERSION))
    quality: Counter = Counter()
    for row in rows:
        quality.update(row["quality"])
    return {"team_id": team_id, "team_name": team_name, "match_ids": [row["match_id"] for row in rows],
            "period_start": rows[0]["match_date"] if rows else None,
            "period_end": rows[-1]["match_date"] if rows else None, "metrics": metrics,
            "shots": [shot for row in rows for shot in row["shots"]], "quality": dict(quality)}
