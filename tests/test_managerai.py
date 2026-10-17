"""Testes sem rede: fixtures sintéticas explícitas, sem simular dados reais."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from managerai.cli import main
from managerai.data_inventory import inventory, load_season
from managerai.data_loader import DataError, LocalData
from managerai.feature_engineering import aggregate, match_features
from managerai.pipeline import analyze, audit
from managerai.report_renderer import render_markdown
from managerai.report_schema import AnalysisRequest
from managerai.temporal import select_history


def fixture_match(mid: int, day: int) -> dict:
    return {"match_id": mid, "match_date": f"2020-01-{day:02d}", "kick_off": "15:00:00.000",
            "competition": {"competition_id": 2}, "season": {"season_id": 27},
            "home_team": {"home_team_id": 1, "home_team_name": "Equipe sintética A"},
            "away_team": {"away_team_id": 2, "away_team_name": "Equipe sintética B"}}


def fixture_lineups() -> list:
    return [{"team_id": 1, "lineup": [{"player_id": 101}]}, {"team_id": 2, "lineup": [{"player_id": 201}]}]


def fixture_events(mid: int) -> list:
    events = []

    def add(typ: str, tid: int = 1, **kwargs) -> None:
        i = len(events) + 1
        events.append({"id": f"synthetic-{mid}-{i}", "index": i, "period": 1, "timestamp": "00:01:00.000",
                       "team": {"id": tid}, "player": {"id": 101 if tid == 1 else 201},
                       "type": {"name": typ}, "location": [70, 40], **kwargs})

    add("Pass", location=[75, 30], **{"pass": {"end_location": [90, 30]}, "under_pressure": True})
    add("Pass", location=[75, 30], **{"pass": {"end_location": [90, 30], "outcome": {"name": "Incomplete"}}})
    add("Carry", location=[110, 10], carry={"end_location": [110, 20]})
    add("Duel", duel={"type": {"name": "Tackle"}})
    add("Pressure", tid=2, location=[90, 40], counterpress=True)
    add("Pressure", location=[60, 40])
    add("Shot", location=[110, 40], shot={"statsbomb_xg": 0.4})
    add("Shot", tid=2, location=[110, 40], shot={"statsbomb_xg": 0.2})
    add("Half End", timestamp="00:45:00.000")
    add("Half End", tid=2, period=2, timestamp="00:45:00.000")
    return events


class LocalFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "data"
        self.matches = [fixture_match(mid, mid) for mid in range(1, 10)]
        self.write("competitions.json", [{"competition_id": 2, "season_id": 27, "competition_name": "Competição sintética", "season_name": "2020"}])
        self.write("matches/2/27.json", self.matches)
        for m in self.matches:
            self.write(f"events/{m['match_id']}.json", fixture_events(m["match_id"]))
            self.write(f"lineups/{m['match_id']}.json", fixture_lineups())
        self.request = AnalysisRequest(2, 27, 1, 2, target_match_id=8)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, value) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")


class ContractTests(unittest.TestCase):
    def test_requires_exactly_one_reference_and_distinct_teams(self):
        for kwargs in ({}, {"cutoff_date": "2020-01-08", "target_match_id": 8}):
            with self.assertRaises(ValueError):
                AnalysisRequest(2, 27, 1, 2, **kwargs)
        with self.assertRaises(ValueError):
            AnalysisRequest(2, 27, 1, 1, target_match_id=8)

    def test_rejects_invalid_context_date_and_window(self):
        request = AnalysisRequest(2, 27, 1, 2, cutoff_date="2020-01-08")
        for kwargs in ({"recent_matches_window": 0}, {"venue": "inferido"}, {"cutoff_date": "2020-02-30"}, {"team_id": True}, {"unavailable_player_ids": (-1,)}):
            with self.assertRaises(ValueError):
                replace(request, **kwargs)


class InventoryTests(LocalFixture):
    def test_orphans_never_enter_catalog(self):
        self.write("events/999.json", [])
        result = inventory(LocalData(self.root))
        self.assertEqual(result["total_matches"], 9)
        self.assertEqual(result["unreferenced_file_ids"]["events"], ["999"])
        self.assertEqual(result["seasons"][0]["coverage"]["three-sixty"], 0)

    def test_rejects_duplicates_and_incompatible_metadata(self):
        self.write("matches/2/27.json", self.matches + [self.matches[0]])
        with self.assertRaises(DataError):
            load_season(LocalData(self.root), 2, 27)
        wrong = deepcopy(self.matches)
        wrong[0]["season"]["season_id"] = 999
        self.write("matches/2/27.json", wrong)
        with self.assertRaises(DataError):
            load_season(LocalData(self.root), 2, 27)

    def test_unknown_competition_and_unsafe_loader_path(self):
        with self.assertRaises(DataError):
            load_season(LocalData(self.root), 999, 27)
        with self.assertRaises(DataError):
            LocalData(self.root).read("../outside.json")


class TemporalTests(LocalFixture):
    def test_window_and_target_exclusion(self):
        season = load_season(LocalData(self.root), 2, 27)
        histories, _ = select_history(season, replace(self.request, recent_matches_window=3))
        self.assertEqual([m["match_id"] for m in histories[1]], [5, 6, 7])
        self.assertEqual([m["match_id"] for m in histories[2]], [5, 6, 7])

    def test_date_cutoff_excludes_same_day(self):
        request = replace(self.request, target_match_id=None, cutoff_date="2020-01-08")
        season = load_season(LocalData(self.root), 2, 27)
        histories, _ = select_history(season, request)
        self.assertEqual([m["match_id"] for m in histories[1]], list(range(1, 8)))

    def test_target_excludes_earlier_fixture_on_same_day(self):
        self.matches[6]["match_date"] = "2020-01-08"
        self.matches[6]["kick_off"] = "10:00:00.000"
        self.write("matches/2/27.json", self.matches)
        report = analyze(self.root, self.request)
        self.assertNotIn(7, report.team_profile.match_ids)

    def test_first_match_has_no_fabricated_zero_metrics(self):
        report = analyze(self.root, replace(self.request, target_match_id=1))
        self.assertEqual(report.team_profile.match_ids, [])
        self.assertEqual(report.team_profile.sample_status, "insuficiente")
        self.assertIsNone(report.team_profile.metrics["xg_for"].value)
        self.assertEqual(report.tactical_hypotheses, [])
        self.assertEqual(report.key_findings, [])

    def test_small_sample_abstains(self):
        report = analyze(self.root, replace(self.request, target_match_id=3))
        self.assertEqual(report.team_profile.sample_status, "insuficiente")
        self.assertEqual(report.tactical_hypotheses, [])

    def test_unknown_team_and_wrong_target(self):
        for request in (replace(self.request, team_id=999), replace(self.request, target_match_id=999)):
            with self.assertRaises(DataError):
                analyze(self.root, request)

    def test_target_and_future_events_lineups_are_never_read(self):
        before = analyze(self.root, self.request).to_json()
        for mid in (8, 9):
            for kind in ("events", "lineups"):
                (self.root / kind / f"{mid}.json").write_text("INVALID JSON", encoding="utf-8")
        after = analyze(self.root, self.request).to_json()
        self.assertEqual(before, after)


class FeatureTests(unittest.TestCase):
    def calculate(self, events=None):
        return match_features(fixture_match(1, 1), events or fixture_events(1), fixture_lineups())

    def test_entries_require_success_and_include_lateral_box_entry(self):
        rows, _ = self.calculate()
        self.assertEqual(rows[1]["final_third_attempts"], 2)
        self.assertEqual(rows[1]["final_third_entries"], 1)
        self.assertEqual(rows[1]["box_entries"], 1)
        self.assertEqual(rows[1]["minutes"], 90)

    def test_xg_is_attributed_to_correct_opponent(self):
        rows, _ = self.calculate()
        self.assertEqual(rows[1]["xg_for"], 0.4)
        self.assertEqual(rows[1]["xg_against"], 0.2)
        self.assertEqual(rows[2]["xg_against"], 0.4)

    def test_missing_xg_does_not_become_zero_or_partial_sum(self):
        events = fixture_events(1)
        next(e for e in events if e["type"]["name"] == "Shot")["shot"] = {}
        rows, q = self.calculate(events)
        self.assertIsNone(rows[1]["xg_for"])
        self.assertIsNone(rows[2]["xg_against"])
        self.assertEqual(q["shots_missing_or_invalid_xg"], 1)

    def test_unmarked_pressure_is_separate_and_counterpress_is_top_level(self):
        rows, _ = self.calculate()
        self.assertEqual(rows[1]["unmarked_passes"], 1)
        self.assertEqual(rows[1]["no_pressure_passes"], 0)
        self.assertEqual(rows[2]["counterpressures"], 1)
        self.assertEqual(rows[1]["duel_tackles"], 1)

    def test_invalid_coordinates_exclude_only_spatial_measurement(self):
        events = fixture_events(1)
        events[0]["location"] = [120.7, 1]
        rows, q = self.calculate(events)
        self.assertEqual(q["locations_invalid"], 1)
        self.assertEqual(rows[1]["passes"], 2)
        self.assertEqual(rows[1]["final_third_entries"], 0)

    def test_exposure_sums_periods_and_excludes_extra_time(self):
        events = fixture_events(1)
        events[-2]["timestamp"] = "00:47:00.000"
        events[-1]["timestamp"] = "00:49:00.000"
        extra = deepcopy(events[6])
        extra.update(id="extra", index=99, period=3)
        events.append(extra)
        rows, q = self.calculate(events)
        self.assertEqual(rows[1]["minutes"], 96)
        self.assertEqual(rows[1]["shots_for"], 1)
        self.assertEqual(q["events_excluded_other_periods"], 1)

    def test_negative_duration_is_reported_without_discarding_action(self):
        events = fixture_events(1)
        events[0]["duration"] = -2000
        rows, q = self.calculate(events)
        self.assertEqual(q["durations_invalid"], 1)
        self.assertEqual(rows[1]["passes"], 2)
        self.assertEqual(rows[1]["minutes"], 90)

    def test_duplicate_event_and_foreign_team_fail(self):
        events = fixture_events(1)
        events[1]["id"] = events[0]["id"]
        with self.assertRaises(DataError):
            self.calculate(events)
        events = fixture_events(1)
        events[0]["team"]["id"] = 999
        with self.assertRaises(DataError):
            self.calculate(events)

    def test_pooled_rates_and_ratios_use_exposure_and_attempts(self):
        rows, _ = self.calculate()
        first, second = dict(rows[1]), dict(rows[1])
        first.update(match_id=1, minutes=90, passes=2, passes_completed=1)
        second.update(match_id=2, minutes=45, passes=8, passes_completed=8)
        p = aggregate(1, "Sintética", [first, second], {})
        self.assertEqual(p.metrics["pass_accuracy"].value, 90)
        self.assertAlmostEqual(p.metrics["final_third_entries"].value, 2 * 90 / 135)
        self.assertEqual(p.metrics["final_third_entries"].sample_size, 2)


class PipelineTests(LocalFixture):
    def test_reproducibility_provenance_and_grounded_hypotheses(self):
        first = analyze(self.root, self.request)
        self.assertEqual(first.to_json(), analyze(self.root, self.request).to_json())
        self.assertGreaterEqual(len(first.key_findings), 2)
        self.assertGreaterEqual(len(first.tactical_hypotheses), 2)
        result = first.to_dict()
        for h in first.tactical_hypotheses:
            for path in h.evidence_metrics:
                value = result
                for segment in path.split("."):
                    value = value[segment]
                self.assertIsNotNone(value["value"])
                self.assertGreaterEqual(value["sample_size"], 5)
        sources = first.methodology["sources"]
        self.assertNotIn("events/8.json", [s["path"] for s in sources])
        self.assertEqual(first.formation_options, [])
        self.assertEqual(first.lineup_options, [])
        self.assertNotIn("NaN", first.to_json())

    def test_missing_events_not_replaced_with_older_matches(self):
        (self.root / "events/7.json").unlink()
        report = analyze(self.root, replace(self.request, recent_matches_window=3))
        self.assertEqual(report.team_profile.match_ids, [5, 6])
        self.assertEqual(report.metadata["matches_requested_team"], 3)

    def test_manual_unavailability_requires_prior_own_team_observation(self):
        analyze(self.root, replace(self.request, unavailable_player_ids=(101,)))
        for pid in (999, 201):
            with self.assertRaises(DataError):
                analyze(self.root, replace(self.request, unavailable_player_ids=(pid,)))

    def test_missing_lineups_are_reported_without_fabricated_players(self):
        (self.root / "lineups/7.json").unlink()
        report = analyze(self.root, self.request)
        self.assertEqual(report.team_profile.quality["missing_lineup_files"], 1)
        self.assertEqual(report.lineup_options, [])

    def test_renderer_preserves_numbers_and_marks_notes_as_unverified(self):
        report = analyze(self.root, replace(self.request, notes="Nota sintética do treinador"))
        text = render_markdown(report)
        self.assertIn("0,40", text)
        self.assertIn("texto do treinador, não verificado", text)
        self.assertIn("> Nota sintética do treinador", text)
        self.assertIn("Não suportado pelos dados atuais", text)

    def test_audit_checks_entire_slice_and_reports_missing_files(self):
        (self.root / "events/9.json").unlink()
        result = audit(self.root, 2, 27)
        self.assertEqual(result["matches_checked"], 8)
        self.assertEqual(result["missing_event_match_ids"], [9])
        self.assertEqual(result["status"], "com_lacunas")

    def test_cli_creates_reports_preserves_inputs_and_refuses_overwrite(self):
        out = Path(self.tmp.name) / "report"
        raw_before = (self.root / "events/1.json").read_bytes()
        args = ["--data-root", str(self.root), "analyze", "--competition-id", "2", "--season-id", "27",
                "--team-id", "1", "--opponent-id", "2", "--target-match-id", "8", "--output-dir", str(out)]
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(main(args), 0)
            generated = (out / "report.json").read_bytes()
            self.assertEqual(main(args), 2)
        self.assertEqual((out / "report.json").read_bytes(), generated)
        self.assertEqual((self.root / "events/1.json").read_bytes(), raw_before)
        self.assertTrue((out / "report.md").is_file())

    def test_cli_rejects_output_inside_raw_data(self):
        args = ["--data-root", str(self.root), "analyze", "--competition-id", "2", "--season-id", "27",
                "--team-id", "1", "--opponent-id", "2", "--target-match-id", "8", "--output-dir", str(self.root / "output")]
        with redirect_stderr(StringIO()):
            self.assertEqual(main(args), 2)
        self.assertFalse((self.root / "output").exists())


if __name__ == "__main__":
    unittest.main()
