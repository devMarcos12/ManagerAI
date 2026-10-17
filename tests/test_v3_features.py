"""Geometria, lacunas e denominadores V3 usando eventos sintéticos explícitos."""
from copy import deepcopy
import json
from math import hypot
import os
from pathlib import Path
import unittest

from managerai.v3_features import V3_METRICS, aggregate_v3, analyze_match_v3


MATCH = {"match_id": 1, "match_date": "2020-01-01"}


def event(kind, location=None, team=1, period=1, **kwargs):
    return {"id": f"synthetic-{kind}", "type": {"name": kind}, "team": {"id": team},
            "period": period, "location": location, **kwargs}


def metric(row, key):
    return row["metrics"][key]["value"]


class V3FeatureTests(unittest.TestCase):
    def test_progression_distance_inclusive_boundary_and_incomplete_exclusion(self):
        events = [event("Pass", [50, 40], **{"pass": {"end_location": [60, 40]}}),
                  event("Pass", [50, 40], **{"pass": {"end_location": [59.99, 40]}}),
                  event("Pass", [50, 40], **{"pass": {"end_location": [100, 40], "outcome": {"name": "Incomplete"}}}),
                  event("Carry", [120, 0], carry={"end_location": [120, 10]}),
                  event("Carry", [100, 40], carry={"end_location": [90, 40]})]
        row = analyze_match_v3(MATCH, events, 1, 90)
        self.assertEqual(metric(row, "progressive_passes"), 1)
        self.assertEqual(metric(row, "progressive_carries"), 1)

    def test_entries_segmented_by_movement_and_destination_lane(self):
        events = [event("Pass", [79, 25], **{"pass": {"end_location": [80, 0]}}),
                  event("Carry", [70, 40], carry={"end_location": [90, 80/3]}),
                  event("Carry", [70, 40], carry={"end_location": [90, 160/3]}),
                  event("Carry", [80, 40], carry={"end_location": [90, 40]}),
                  event("Pass", [110, 10], **{"pass": {"end_location": [110, 18]}}),
                  event("Carry", [102, 62], carry={"end_location": [110, 40]})]
        row = analyze_match_v3(MATCH, events, 1, 90)
        self.assertEqual(metric(row, "final_third_pass_entries"), 1)
        self.assertEqual(metric(row, "final_third_carry_entries"), 2)
        self.assertEqual(metric(row, "box_pass_entries"), 1)
        self.assertEqual(metric(row, "box_carry_entries"), 0)
        for lane in ("low", "central", "high"):
            self.assertAlmostEqual(metric(row, f"entry_lane_{lane}_share"), 100/3)

    def test_spatial_lacuna_does_not_invent_zero_and_other_type_remains_valid(self):
        row = analyze_match_v3(MATCH, [event("Pass", [50, 40], **{"pass": {"end_location": [121, 40]}}),
                                      event("Carry", [50, 40], carry={"end_location": [70, 40]})], 1, 90)
        self.assertIsNone(metric(row, "progressive_passes"))
        self.assertIsNone(metric(row, "final_third_pass_entries"))
        self.assertIsNone(metric(row, "entry_lane_low_share"))
        self.assertEqual(metric(row, "progressive_carries"), 1)
        self.assertEqual(row["quality"]["pass_geometry_missing_or_invalid"], 1)

    def test_shot_zones_boundaries_and_xg(self):
        events = [event("Shot", [102, 18], shot={"statsbomb_xg": 0.4}),
                  event("Shot", [110, 62], shot={"statsbomb_xg": 0.2}),
                  event("Shot", [101.99, 40], shot={"statsbomb_xg": 0.1})]
        row = analyze_match_v3(MATCH, events, 1, 90)
        self.assertAlmostEqual(metric(row, "shots_box_share"), 200/3)
        self.assertAlmostEqual(metric(row, "xg_box"), 0.6)
        self.assertAlmostEqual(metric(row, "xg_outside"), 0.1)
        self.assertAlmostEqual(metric(row, "xg_per_located_shot"), 0.7/3)
        self.assertEqual(len(row["shots"]), 3)
        self.assertEqual(row["shots"][0]["period"], 1)
        self.assertEqual(row["shots"][0]["team_id"], 1)

    def test_missing_xg_preserves_counts_and_point_but_not_fake_sum(self):
        row = analyze_match_v3(MATCH, [event("Shot", [110, 40], shot={})], 1, 90)
        self.assertEqual(metric(row, "shots_box_share"), 100)
        self.assertIsNone(metric(row, "xg_box"))
        self.assertIsNone(metric(row, "xg_per_located_shot"))
        self.assertIsNone(row["shots"][0]["xg"])

    def test_missing_shot_geometry_invalidates_zone_estimates(self):
        row = analyze_match_v3(MATCH, [event("Shot", None, shot={"statsbomb_xg": 0.4})], 1, 90)
        self.assertIsNone(metric(row, "shots_box_share"))
        self.assertIsNone(metric(row, "xg_box"))
        self.assertEqual(row["shots"], [])

    def test_pressure_boundaries_and_no_success_claim(self):
        events = [event("Pressure", [0, 0]), event("Pressure", [40, 80/3]),
                  event("Pressure", [80, 160/3]), event("Pressure", [120, 80])]
        row = analyze_match_v3(MATCH, events, 1, 45)
        self.assertEqual(metric(row, "pressures_low_third_share"), 25)
        self.assertEqual(metric(row, "pressures_middle_third_share"), 25)
        self.assertEqual(metric(row, "pressures_high_third_share"), 50)
        self.assertEqual(metric(row, "pressures_high_third"), 4)
        self.assertEqual(metric(row, "pressure_lane_high_share"), 50)
        self.assertFalse(any("success" in key for key in row["metrics"]))

    def test_recovery_missing_flag_is_not_explicit_nonfailure(self):
        events = [event("Ball Recovery", ball_recovery={"recovery_failure": True}),
                  event("Ball Recovery", ball_recovery={"recovery_failure": False}),
                  event("Ball Recovery"), event("Pressure", [80, 40])]
        row = analyze_match_v3(MATCH, events, 1, 90)
        self.assertEqual(metric(row, "recoveries_recorded"), 3)
        self.assertEqual(metric(row, "recoveries_explicit_failure"), 1)
        self.assertEqual(metric(row, "recoveries_explicit_nonfailure"), 1)
        self.assertEqual(row["quality"]["recovery_failure_unmarked"], 1)

    def test_team_and_period_filter_and_input_is_unchanged(self):
        events = [event("Carry", [70, 40], carry={"end_location": [90, 40]}),
                  event("Carry", [70, 40], team=2, carry={"end_location": [90, 40]}),
                  event("Carry", [70, 40], period=3, carry={"end_location": [90, 40]})]
        frozen = deepcopy(events)
        row = analyze_match_v3(MATCH, events, 1, 90)
        self.assertEqual(metric(row, "progressive_carries"), 1)
        self.assertEqual(events, frozen)

    def test_null_exposure_and_zero_denominator_remain_unavailable(self):
        events = [event("Carry", [50, 40], carry={"end_location": [70, 40]})]
        for exposure in (None, 0, -1, float("nan")):
            row = analyze_match_v3(MATCH, events, 1, exposure)
            self.assertIsNone(metric(row, "progressive_carries"))
            self.assertIsNone(metric(row, "entry_lane_low_share"))
            self.assertIsNone(metric(row, "xg_per_located_shot"))

    def test_aggregation_weights_denominators_and_specific_sample_sizes(self):
        first = analyze_match_v3(MATCH, [event("Carry", [50, 40], carry={"end_location": [70, 40]})], 1, 45)
        second = analyze_match_v3({"match_id": 2, "match_date": "2020-01-02"},
                                  [event("Carry", [50, 40], carry={"end_location": [70, 40]})], 1, 90)
        invalid = analyze_match_v3({"match_id": 3, "match_date": "2020-01-03"},
                                   [event("Carry", None, carry={})], 1, 90)
        profile = aggregate_v3(1, "Sintético", [second, first, invalid])
        m = profile["metrics"]["progressive_carries"]
        self.assertAlmostEqual(m["value"], 90*2/135)
        self.assertEqual(m["sample_size"], 2)
        self.assertEqual(m["match_ids"], [1, 2])
        self.assertEqual(m["formula_version"], "3.0.0")
        self.assertIsNotNone(m["standard_deviation"])
        self.assertEqual(m["per_match"][0]["match_date"], "2020-01-01")
        self.assertEqual(profile["quality"]["carry_geometry_missing_or_invalid"], 1)

    def test_empty_aggregate_and_single_observation(self):
        empty = aggregate_v3(1, "Sintético", [])
        self.assertIsNone(empty["period_start"])
        self.assertTrue(all(m["value"] is None and m["sample_size"] == 0 for m in empty["metrics"].values()))
        row = analyze_match_v3(MATCH, [event("Pressure", [10, 10])], 1, 90)
        profile = aggregate_v3(1, "Sintético", [row])
        self.assertTrue(all(m["standard_deviation"] is None for m in profile["metrics"].values()))
        self.assertGreaterEqual(len(V3_METRICS), 10)
        self.assertEqual({meta["family"] for meta in V3_METRICS.values()}, {"progression", "shots", "pressure"})

    def test_aggregate_rejects_team_mismatch_and_duplicates(self):
        row = analyze_match_v3(MATCH, [], 1, 90)
        with self.assertRaises(ValueError):
            aggregate_v3(2, "Outra equipe", [row])
        with self.assertRaises(ValueError):
            aggregate_v3(1, "Sintético", [row, row])

    def test_no_team_events_are_not_zero_observations(self):
        row = analyze_match_v3(MATCH, [], 1, 90)
        self.assertTrue(all(m["value"] is None for m in row["metrics"].values()))
        self.assertEqual(row["quality"]["team_events_unavailable"], 1)


@unittest.skipUnless(os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração local opcional")
class V3IndependentLocalTests(unittest.TestCase):
    def test_direct_raw_counts_match_v3_without_geometry_helpers(self):
        from managerai.data_inventory import load_season
        from managerai.data_loader import LocalData
        from managerai.feature_engineering import match_features
        from managerai.report_schema import AnalysisRequest
        from managerai.temporal import select_history
        root = Path(__file__).resolve().parents[1] / "open-data/data"
        data = LocalData(root)
        season = load_season(data, 2, 27)
        histories, _ = select_history(season, AnalysisRequest(2, 27, 36, 1, target_match_id=3754314))
        match = histories[36][-1]
        events = json.loads((root / "events" / f"{match['match_id']}.json").read_text())
        core, _ = match_features(match, events, data.lineups(match["match_id"]))
        row = analyze_match_v3(match, events, 36, core[36]["minutes"])
        own = [e for e in events if e["team"]["id"] == 36 and e["period"] in (1, 2)]
        # Deliberately independent formulas, using the original JSON arrays.
        passes = [e for e in own if e["type"]["name"] == "Pass" and not e["pass"].get("outcome")]
        progressive = sum(hypot(120-e["location"][0], 40-e["location"][1]) -
                          hypot(120-e["pass"]["end_location"][0], 40-e["pass"]["end_location"][1]) >= 10
                          for e in passes)
        self.assertEqual(row["metrics"]["progressive_passes"]["numerator"], progressive)
        shots = [e for e in own if e["type"]["name"] == "Shot"]
        box_xg = sum(e["shot"]["statsbomb_xg"] for e in shots
                     if e["location"][0] >= 102 and 18 <= e["location"][1] <= 62)
        self.assertAlmostEqual(row["metrics"]["xg_box"]["numerator"], box_xg)
        high = sum(e["type"]["name"] == "Pressure" and e["location"][0] >= 80 for e in own)
        self.assertEqual(row["metrics"]["pressures_high_third"]["numerator"], high)
        third_entries = (row["metrics"]["final_third_pass_entries"]["numerator"] +
                         row["metrics"]["final_third_carry_entries"]["numerator"])
        self.assertEqual(third_entries, core[36]["final_third_entries"])
        self.assertEqual(len(row["shots"]), len(shots))


if __name__ == "__main__":
    unittest.main()
