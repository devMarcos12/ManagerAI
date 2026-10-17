"""Recalcula oito indicadores diretamente dos JSONs e compara com a V3.

Não usa helpers V3 de geometria, contagem ou exposição. Imprime JSON no stdout;
não escreve nem altera dados/artefatos. Executar com PYTHONPATH=src python3 -B.
"""
from hashlib import sha256
import json
from math import hypot, isclose, isfinite
from pathlib import Path

from managerai.v3_features import V3_METRICS, analyze_match_v3


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "open-data/data"


def read(relative):
    raw = (DATA / relative).read_bytes()
    return json.loads(raw), {"path": relative, "sha256": sha256(raw).hexdigest()}


def check(competition, season, team, cutoff, fixed_match=None):
    matches, calendar_source = read(f"matches/{competition}/{season}.json")
    prior = [m for m in matches if team in (m["home_team"]["home_team_id"], m["away_team"]["away_team_id"])
             and m["match_date"] < cutoff]
    match = next(m for m in prior if m["match_id"] == fixed_match) if fixed_match else max(
        prior, key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
    events, event_source = read(f"events/{match['match_id']}.json")
    ends = {}
    for e in events:
        if e["period"] not in (1, 2):
            continue
        h, minute, second = e["timestamp"].split(":")
        seconds = int(h)*3600 + int(minute)*60 + float(second)
        duration = e.get("duration") or 0
        if not isinstance(duration, (int, float)) or not isfinite(duration) or duration < 0:
            duration = 0
        ends[e["period"]] = max(ends.get(e["period"], 0), seconds+duration)
    minutes = sum(ends.values())/60
    own = [e for e in events if e["team"]["id"] == team and e["period"] in (1, 2)]
    passes = [e for e in own if e["type"]["name"] == "Pass" and not e["pass"].get("outcome")]
    carries = [e for e in own if e["type"]["name"] == "Carry"]
    shots = [e for e in own if e["type"]["name"] == "Shot"]
    pressures = [e for e in own if e["type"]["name"] == "Pressure"]
    # The two selected fixtures have valid relevant coordinates/xG; assert this
    # explicitly instead of silently treating absent arrays as zero.
    for e in passes+carries+shots+pressures:
        assert len(e["location"]) >= 2 and 0 <= e["location"][0] <= 120 and 0 <= e["location"][1] <= 80
    for e in passes+carries:
        endpoint = e[e["type"]["name"].lower()]["end_location"]
        assert 0 <= endpoint[0] <= 120 and 0 <= endpoint[1] <= 80
    entries_pass = sum(e["location"][0] < 80 <= e["pass"]["end_location"][0] for e in passes)
    entries_carry = sum(e["location"][0] < 80 <= e["carry"]["end_location"][0] for e in carries)
    progressive = sum(hypot(120-e["location"][0], 40-e["location"][1]) -
                      hypot(120-e["pass"]["end_location"][0], 40-e["pass"]["end_location"][1]) >= 10 for e in passes)
    box_shots = [e for e in shots if e["location"][0] >= 102 and 18 <= e["location"][1] <= 62]
    for e in shots:
        assert 0 <= e["shot"]["statsbomb_xg"] <= 1
    xg_box = sum(e["shot"]["statsbomb_xg"] for e in box_shots)
    high_pressure = sum(e["location"][0] >= 80 for e in pressures)
    specs = {
        "progressive_passes": (progressive, minutes, 90),
        "final_third_pass_entries": (entries_pass, minutes, 90),
        "final_third_carry_entries": (entries_carry, minutes, 90),
        "shots_box_share": (len(box_shots), len(shots), 100),
        "xg_box": (xg_box, 1, 1),
        "xg_per_located_shot": (sum(e["shot"]["statsbomb_xg"] for e in shots), len(shots), 1),
        "pressures_high_third": (high_pressure, minutes, 90),
        "pressures_high_third_share": (high_pressure, len(pressures), 100),
    }
    actual = analyze_match_v3(match, events, team, minutes)
    results = {}
    for key, (numerator, denominator, multiplier) in specs.items():
        value = multiplier*numerator/denominator if denominator else None
        result = actual["metrics"][key]
        assert isclose(result["numerator"], numerator, abs_tol=1e-12), key
        assert isclose(result["denominator"], denominator, abs_tol=1e-12), key
        assert value is None and result["value"] is None or isclose(result["value"], value, abs_tol=1e-12), key
        results[key] = {"numerator": numerator, "denominator": denominator, "multiplier": multiplier,
                        "value": value, "v3_value": result["value"], "passed": True}
    return {"competition_id": competition, "season_id": season, "team_id": team,
            "match_id": match["match_id"], "match_date": match["match_date"], "cutoff_date": cutoff,
            "exposure_minutes": minutes, "sources": [calendar_source, event_source], "metrics": results}


if __name__ == "__main__":
    assert len(V3_METRICS) == 26
    output = {"formula_version": "3.0.0", "metric_catalog_size": len(V3_METRICS),
              "scope": "Conferência independente de oito indicadores em dois jogos, não auditoria estatística de todas as partidas.",
              "cases": [check(2, 27, 36, "2016-05-08"), check(11, 90, 220, "2021-04-10", 3773585)]}
    print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))
