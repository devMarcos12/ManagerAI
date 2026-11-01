"""Projeção de qualidade e contratos; sem alterar relatórios congelados."""
from copy import deepcopy
from dataclasses import replace
import importlib.util
import json
from unittest.mock import patch
import unittest

from managerai.data_loader import DataError, LocalData
from managerai.explanation import fingerprint
from managerai.pipeline import analyze
from managerai.quality_report import apply_quality_policy, QUALITY_CORE_METRICS
from managerai.season_audit import audit_orientation, review_orientation
from managerai.service import build_service_report, render_service_markdown
from managerai.service_schema import ServiceRequest, ServiceError, RosterEntry
from test_season_audit import orientation_games
from test_service import ServiceFixture


class QualityTests(ServiceFixture):
    def quality(self, **kwargs):
        return build_service_report(self.root, ServiceRequest(self.request, data_policy="quality_v1", **kwargs))

    def test_default_preserves_legacy_and_opt_in_keeps_original_report(self):
        legacy = analyze(self.root, self.request).to_dict()
        default = build_service_report(self.root, ServiceRequest(self.request))
        result = self.quality()
        self.assertNotIn("data_quality", default)
        identity_request = ServiceRequest(self.request).to_dict();identity_request.pop("data_policy")
        self.assertEqual(default["report_id"], fingerprint({"request": identity_request, "legacy": legacy}))
        self.assertEqual(default["legacy_report"], legacy)
        self.assertEqual(result["legacy_report"], legacy)
        self.assertEqual(result["data_quality"]["required_core_metrics"], list(QUALITY_CORE_METRICS))
        self.assertEqual(result["provenance"]["engine"]["engine_id"], "deterministic-quality")
        self.assertEqual(result, self.quality())

    def test_bad_duration_filters_rates_but_preserves_counts_and_ratios(self):
        for mid in (1, 2):
            events = json.loads((self.root / f"events/{mid}.json").read_text())
            events[0]["duration"] = -10
            self.write(f"events/{mid}.json", events)
        before = {p: p.read_bytes() for p in self.root.glob("events/*.json")}
        result = self.quality()
        for side in ("team_profile", "opponent_profile"):
            rate = result["evidence"][f"{side}.metrics.pressures"]
            count = result["evidence"][f"{side}.metrics.shots_for"]
            accuracy = result["evidence"][f"{side}.metrics.pass_accuracy"]
            self.assertEqual(rate["sample_size"], 5)
            self.assertEqual(rate["match_ids"], [3, 4, 5, 6, 7])
            self.assertEqual(count["sample_size"], 7)
            self.assertEqual(accuracy["sample_size"], 7)
            self.assertAlmostEqual(rate["value"], 90 * rate["numerator"] / rate["denominator"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.glob("events/*.json")})

    def test_weighted_passing_ratio_is_not_mean_of_match_percentages(self):
        events = json.loads((self.root / "events/1.json").read_text())
        event = deepcopy(events[0]); event.update(id="extra-pass", index=100)
        events.append(event); self.write("events/1.json", events)
        result = self.quality()
        metric = result["evidence"]["team_profile.metrics.pass_accuracy"]
        self.assertAlmostEqual(metric["value"], 100 * metric["numerator"] / metric["denominator"])
        self.assertNotAlmostEqual(metric["value"], sum(r["value"] for r in metric["per_match"]) / len(metric["per_match"]))

    def test_unavailable_and_zero_remain_distinct(self):
        result = self.quality()
        metric = result["evidence"]["team_profile.metrics.pass_accuracy_explicit_no_pressure"]
        self.assertIsNone(metric["value"]); self.assertEqual(metric["sample_size"], 0)
        for mid in range(1, 8):
            events = json.loads((self.root / f"events/{mid}.json").read_text())
            events = [e for e in events if e["type"]["name"] != "Shot"]
            self.write(f"events/{mid}.json", events)
        result = self.quality()
        self.assertEqual(result["evidence"]["team_profile.metrics.shots_for"]["value"], 0)
        self.assertEqual(result["evidence"]["team_profile.metrics.shots_for"]["sample_size"], 7)

    def test_uncertified_spatial_metrics_cannot_support_plans(self):
        catalog = json.loads((self.root / "competitions.json").read_text())
        catalog.append({"competition_id": 3, "season_id": 7, "competition_name": "Sintética", "season_name": "2020"})
        self.write("competitions.json", catalog)
        matches = deepcopy(self.matches)
        for m in matches:
            m["competition"]["competition_id"], m["season"]["season_id"] = 3, 7
        self.write("matches/3/7.json", matches)
        request = replace(self.request, competition_id=3, season_id=7)
        result = build_service_report(self.root, ServiceRequest(request, data_policy="quality_v1"))
        self.assertFalse(result["data_quality"]["spatial_season_certified"])
        self.assertTrue(result["sufficiency"]["sufficient"])
        self.assertEqual([p["plan_id"] for p in result["plans"]], ["R03_CHANCES"])
        self.assertIsNone(result["evidence"]["team_profile.metrics.final_third_entries"]["value"])
        rows = result["data_quality"]["metrics"]
        row = next(r for r in rows if r["evidence_id"] == "team_profile.metrics.final_third_entries")
        self.assertEqual(row["reason_counts"]["season_not_certified"], 7)
        for plan in result["plans"]:
            for ref in plan["evidence_ids"]:
                self.assertGreaterEqual(result["evidence"][ref]["sample_size"], 5)

    def test_insufficient_and_restrictions_keep_abstention(self):
        short = build_service_report(self.root, ServiceRequest(replace(self.request, recent_matches_window=1), data_policy="quality_v1"))
        self.assertFalse(short["plans"]); self.assertFalse(short["sufficiency"]["sufficient"])
        result = self.quality(blocked_plan_ids=("R03_CHANCES",))
        self.assertFalse(result["plans"])
        self.assertTrue(result["excluded_plans"])

    def test_future_target_and_same_day_files_are_not_read(self):
        for mid in (8, 9):
            (self.root / f"events/{mid}.json").write_text("INVALID FUTURE")
        paths = []
        original = LocalData.read
        def observed(data, relative):
            paths.append(relative);return original(data, relative)
        with patch.object(LocalData, "read", observed):
            self.quality()
        self.assertFalse(any(p.endswith(("/8.json", "/9.json")) for p in paths))

    def test_source_change_between_reads_is_rejected(self):
        report = analyze(self.root, self.request)
        events = json.loads((self.root / "events/1.json").read_text());events[0]["location"][0] += 1
        self.write("events/1.json", events)
        with self.assertRaises(DataError):apply_quality_policy(self.root, report)

    def test_missing_event_game_with_declared_player_is_not_replaced(self):
        (self.root / "events/1.json").unlink()
        request = replace(self.request, unavailable_player_ids=(101,))
        roster = (RosterEntry(101, 1, ("goleiro",), "unavailable", "Declaração sintética", "2020-01-01"),)
        result = build_service_report(self.root, ServiceRequest(request, data_policy="quality_v1", roster=roster))
        metric = result["evidence"]["team_profile.metrics.shots_for"]
        self.assertEqual(metric["match_ids"], [2, 3, 4, 5, 6, 7])
        row = next(r for r in result["data_quality"]["metrics"] if r["evidence_id"] == "team_profile.metrics.shots_for")
        self.assertEqual(row["selected_matches"], 7)
        self.assertEqual(row["excluded_match_ids"], [1])
        self.assertEqual(row["reason_counts"], {"not_diagnosed": 1})

    def test_incompatible_or_unknown_policy_is_explicit(self):
        for kwargs, code in (({"include_v3": True, "data_policy": "quality_v1"}, "INCOMPATIBLE_DATA_POLICY"),
                             ({"data_policy": "unknown"}, "INVALID_DATA_POLICY")):
            with self.assertRaises(ServiceError) as error:ServiceRequest(self.request, **kwargs)
            self.assertEqual(error.exception.code, code)

    def test_markdown_contains_filtered_samples_and_reasons(self):
        result = self.quality()
        text = render_service_markdown(result)
        self.assertIn("Qualidade dos dados", text)
        self.assertIn("amostra original=", text)
        self.assertIn("não certificam", text)


class OrientationReviewTests(unittest.TestCase):
    def test_backward_passes_do_not_prove_inverted_coordinates(self):
        games = orientation_games("normal")
        for _, events in games:
            for event in events:
                if event["type"]["name"] == "Pass":event["pass"]["end_location"] = [50, 40]
        result = audit_orientation(games)
        review = review_orientation(result["groups"])
        self.assertEqual(result["status"], "mista")
        self.assertEqual(review["mixed_with_high_shot_median_but_low_forward_share"], 40)
        self.assertFalse(review["guard_changed"])


@unittest.skipUnless(importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx"), "API opcional")
class QualityAPITests(ServiceFixture):
    def test_typed_api_and_exports_preserve_quality_projection(self):
        from fastapi.testclient import TestClient
        from managerai.api import create_app
        client = TestClient(create_app(data_root=self.root))
        body = {"analysis": {"competition_id": 2, "season_id": 27, "team_id": 1, "opponent_id": 2,
                             "target_match_id": 8}, "data_policy": "quality_v1"}
        self.assertIn("quality_v1", client.get('/v1/capabilities').json()["data_policies"])
        response = client.post('/v1/analyses', json=body)
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json();key = result['report_key']
        self.assertTrue(result['data_quality']['applied'])
        self.assertEqual(client.get(f'/v1/reports/{key}/export').json(), result)
        self.assertIn('Qualidade dos dados', client.get(f'/v1/reports/{key}/export?format=markdown').text)
        response = client.post('/v1/analyses', json={**body, 'include_v3': True})
        self.assertEqual((response.status_code, response.json()['code']), (422, 'INCOMPATIBLE_DATA_POLICY'))
