"""Dependências e janelas; fixtures sintéticas não são validação esportiva."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from managerai.data_inventory import load_season
from managerai.data_loader import LocalData
from managerai.feature_engineering import METRICS
from managerai.metric_eligibility import (FAMILIES, DIRECTIONAL, RATE_FAMILIES,
                                         assess_game, quality_issues, summarize_eligibility)
from managerai.season_audit import audit_candidate, audit_game_taxonomy, audit_orientation
from managerai.v3_features import V3_METRICS
from test_managerai import LocalFixture, fixture_events, fixture_lineups, fixture_match


def coherent_groups():
    return [{"team_id": team, "period": period, "status": "coerente"}
            for team in (1, 2) for period in (1, 2)]


def assess(events, groups=None):
    match = fixture_match(1, 1)
    diagnosis = audit_game_taxonomy(match, events, fixture_lineups())
    issues = quality_issues(match, events)
    return assess_game(match, diagnosis, issues, coherent_groups() if groups is None else groups), issues


class DependencyTests(unittest.TestCase):
    def test_mapping_covers_every_metric_once(self):
        keys = [key for values in FAMILIES.values() for key in values]
        self.assertEqual(len(keys), 50)
        self.assertEqual(len(set(keys)), 50)
        self.assertEqual(set(keys), set(METRICS) | set(V3_METRICS) |
                         {"observed_blocks", "entry_block_share", "shot_block_share"})

    def test_unmarked_pressure_does_not_invalidate_passing_or_shots(self):
        rows, _ = assess(fixture_events(1))
        self.assertIn("passing", rows[1]["eligible_families"])
        self.assertNotIn("passing", rows[2]["eligible_families"])
        for row in rows.values():
            self.assertIn("shot_counts", row["eligible_families"])
            self.assertNotIn("passing_explicit_no_pressure", row["eligible_families"])
            self.assertEqual(row["unavailable_metrics"]["passing_explicit_no_pressure"],
                             ["pass_accuracy_explicit_no_pressure"])

    def test_explicit_false_is_not_the_same_as_absence(self):
        events = fixture_events(1)
        events[1]["under_pressure"] = False
        rows, _ = assess(events)
        self.assertIn("passing_explicit_no_pressure", rows[1]["eligible_families"])
        self.assertNotIn("passing_explicit_no_pressure", rows[2]["eligible_families"])

    def test_duration_invalidates_rates_of_both_sides_but_not_shot_counts(self):
        events = fixture_events(1)
        events[0]["duration"] = -9
        rows, issues = assess(events)
        self.assertEqual(issues[0]["scope"], "match")
        for row in rows.values():
            self.assertIn("shot_counts", row["eligible_families"])
            for family in RATE_FAMILIES:
                self.assertIn("invalid_duration", row["blocked_families"][family])

    def test_geometry_block_is_specific_to_own_team_and_dependent_families(self):
        events = fixture_events(1)
        events[0]["pass"]["end_location"] = [121, 40]
        original = deepcopy(events)
        rows, issues = assess(events)
        self.assertEqual(events, original)
        self.assertEqual(issues[0]["event_id"], events[0]["id"])
        self.assertIn("invalid_movement_end", rows[1]["blocked_families"]["pass_progression"])
        self.assertNotIn("pass_progression", rows[2]["blocked_families"])
        self.assertIn("passing", rows[1]["eligible_families"])
        self.assertIn("shot_counts", rows[1]["eligible_families"])

    def test_incomplete_pass_geometry_does_not_block_complete_pass_progression(self):
        events = fixture_events(1)
        events[1]["pass"]["end_location"] = [121, 40]
        rows, _ = assess(events)
        self.assertIn("pass_progression", rows[1]["eligible_families"])
        self.assertIn("invalid_movement_end", rows[1]["blocked_families"]["movement_rates"])

    def test_missing_direction_blocks_only_direction_dependent_families(self):
        groups = coherent_groups()
        groups[0]["status"] = "inconclusivo"
        rows, _ = assess(fixture_events(1), groups)
        for family in DIRECTIONAL:
            self.assertIn("orientation_not_established", rows[1]["blocked_families"][family])
        self.assertIn("shot_counts", rows[1]["eligible_families"])
        self.assertIn("action_lanes", rows[1]["eligible_families"])

    def test_extra_time_does_not_contaminate_regulation_dependencies(self):
        events = fixture_events(1)
        extra = deepcopy(events[0]);extra.update(id="extra-time", index=99, period=3, duration=-8)
        extra["location"] = [121, 40];events.append(extra)
        self.assertEqual(quality_issues(fixture_match(1, 1), events), [])


class WindowTests(LocalFixture):
    def setUp(self):
        super().setUp()
        self.matches = [fixture_match(mid, mid) for mid in range(1, 13)]
        self.write("matches/2/27.json", self.matches)
        self.season = load_season(LocalData(self.root), 2, 27)
        self.rows = {mid: {tid: {"available_metrics": list(METRICS) + list(V3_METRICS) +
                              ["observed_blocks", "entry_block_share", "shot_block_share"],
                              "eligible_families": list(FAMILIES), "blocked_families": {},
                              "unavailable_metrics": {}} for tid in (1, 2)} for mid in range(1, 13)}

    def test_exact_windows_do_not_replace_missing_games_or_use_target(self):
        self.rows.pop(10)
        result = summarize_eligibility(self.season, self.rows, [])
        windows = result["families"]["shot_counts"]["windows"]
        self.assertEqual(windows["h5"]["target_ids"], list(range(6, 11)))
        self.assertEqual(windows["h10"]["eligible_targets"], 0)
        self.assertEqual(result["families"]["shot_counts"]["blocked_reason_counts"], {"not_diagnosed": 2})

    def test_future_or_same_day_is_not_used(self):
        self.rows.pop(12)
        result = summarize_eligibility(self.season, self.rows, [])
        self.assertEqual(result["families"]["shot_counts"]["windows"]["h5"]["eligible_targets"], 7)
        self.matches[10]["match_date"] = self.matches[9]["match_date"]
        self.write("matches/2/27.json", self.matches)
        season = load_season(LocalData(self.root), 2, 27)
        self.rows.pop(10)
        result = summarize_eligibility(season, self.rows, [])
        self.assertIn(11, result["families"]["shot_counts"]["windows"]["h5"]["target_ids"])

    def test_duplicate_ids_block_both_affected_games(self):
        result = summarize_eligibility(self.season, self.rows, [], {1, 2})
        self.assertEqual(self.rows[1][1]["eligible_families"], [])
        self.assertEqual(self.rows[2][2]["eligible_families"], [])
        self.assertEqual(result["families"]["shot_counts"]["windows"]["h5"]["target_ids"], list(range(8, 13)))

    def test_malformed_json_is_reported_and_other_games_are_diagnosed(self):
        self.write("events/1.json", [])
        (self.root / "events/1.json").write_text("not json")
        result = audit_candidate(LocalData(self.root), 2, 27, audit_date="2026-11-01", content_only=True)
        self.assertEqual(result["status"], "reprovado")
        self.assertTrue(any(x["match_id"] == 1 and x["reason"].startswith("Leitura:")
                            for x in result["structural_or_taxonomy_failures"]))
        self.assertEqual(result["matches_diagnosed"], 8)  # 10–12 também não têm arquivos.
        self.assertEqual(result["family_eligibility"]["status"], "diagnostic_not_certification")


@unittest.skipUnless(os.environ.get("MANAGERAI_CORE02_CONTENT_ROOT"), "Conteúdo real opcional CORE-02")
class RealQualityCases(unittest.TestCase):
    def test_six_real_cases_preserve_count_families_and_raw_bytes(self):
        root = Path(os.environ["MANAGERAI_CORE02_CONTENT_ROOT"])
        season = load_season(LocalData(root), 11, 27)
        selected = {266106, 266467, 266961, 267273, 3825665, 3825875}
        data = LocalData(root)
        duration_cases = set()
        for match in season.matches:
            mid = match["match_id"]
            if mid not in selected:
                continue
            before = (root / "events" / f"{mid}.json").read_bytes()
            events = json.loads(before)
            diagnosis = audit_game_taxonomy(match, events, data.lineups(mid))
            issues = quality_issues(match, events)
            self.assertTrue(issues)
            rows = assess_game(match, diagnosis, issues, audit_orientation([(match, events)])["groups"])
            for row in rows.values():
                self.assertIn("shot_counts", row["eligible_families"])
                self.assertIn("passing", row["eligible_families"])
                if any(i["code"] == "invalid_duration" for i in issues):
                    duration_cases.add(mid)
                    self.assertIn("invalid_duration", row["blocked_families"]["pressure_rates"])
            self.assertEqual(before, (root / "events" / f"{mid}.json").read_bytes())
        self.assertEqual(duration_cases, {3825665, 3825875})
