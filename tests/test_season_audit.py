"""Gates portáveis CORE-02; fixtures explícitas não representam StatsBomb real."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from managerai.data_loader import DataError, LocalData
from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest
from managerai.season_audit import audit_candidate, audit_game_taxonomy, audit_orientation, build_coverage_matrix, main
from test_managerai import LocalFixture, fixture_events, fixture_lineups, fixture_match


class MatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "data"
        self.root.mkdir()
        self.matches = [fixture_match(mid, day) for mid, day in enumerate(range(1, 13), 1)]
        self.write("competitions.json", [{"competition_id": 2, "season_id": 27,
             "competition_name": "Liga sintética", "season_name": "2020",
             "competition_gender": "female", "competition_youth": False,
             "competition_international": False}])
        self.write("matches/2/27.json", self.matches)
        self.contract = {"source": {"revision": "sintético"},
                         "coverage": {"seasons": [{"competition_id": 2, "season_id": 27,
                           "matches": 12, "events": 12, "lineups": 12,
                           "three_sixty": 0, "calendar_sha256": "sintético"}]}}
        for mid in range(1, 13):
            self.write(f"events/{mid}.json", [])
            self.write(f"lineups/{mid}.json", [])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, data: object) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def matrix(self) -> dict:
        return build_coverage_matrix(LocalData(self.root), audit_date="2026-10-25",
                                     contract=self.contract,
                                     verification={"status": "incompatível", "issues": [{"code": "TEST"}]})

    def test_deterministic_calendar_counts_and_no_certification(self) -> None:
        first, second = self.matrix(), self.matrix()
        self.assertEqual(first, second)
        row = first["rows"][0]
        self.assertEqual(row["domain"], "feminino; adulto; clubes")
        self.assertEqual(row["bilateral_targets"]["h5_calendar"], 7)
        self.assertEqual(row["bilateral_targets"]["h10_calendar"], 2)
        self.assertIsNone(row["bilateral_targets"]["h5_calculable"])
        self.assertEqual(row["status"], "inconclusivo")
        self.assertEqual(first["snapshot_status"], "incompatível")
        self.assertEqual([(c["competition_id"], c["season_id"]) for c in first["candidate_priority"]],
                         [(11, 27), (12, 27), (7, 27)])
        json.dumps(first, ensure_ascii=False, allow_nan=False)

    def test_partial_empty_and_missing_file_are_explicit(self) -> None:
        (self.root / "events/12.json").unlink()
        row = self.matrix()["rows"][0]
        self.assertEqual(row["files"]["events_missing"], 1)
        self.assertEqual(row["bilateral_targets"]["h5_calendar"], 7)
        self.assertTrue(any("ausentes" in reason for reason in row["reasons"]))
        self.write("matches/2/27.json", [])
        self.contract["coverage"]["seasons"][0].update(matches=0, events=0, lineups=0)
        row = self.matrix()["rows"][0]
        self.assertEqual(row["status"], "inelegível")
        self.assertIsNone(row["first_date"])

    def test_bad_catalog_and_contract_mismatch_fail(self) -> None:
        bad = deepcopy(self.matches)
        bad[0]["season"]["season_id"] = 99
        self.write("matches/2/27.json", bad)
        with self.assertRaises(DataError):
            self.matrix()
        self.write("matches/2/27.json", self.matches)
        self.contract["coverage"]["seasons"] = []
        with self.assertRaises(DataError):
            self.matrix()

    def test_mixed_metadata_versions_and_same_day_exclusion(self) -> None:
        matches = deepcopy(self.matches)
        matches[10]["match_date"] = matches[9]["match_date"]
        matches[0]["metadata"] = {"data_version": "1.0.3"}
        matches[1]["metadata"] = {"data_version": "1.1.0", "xy_fidelity_version": "2"}
        self.write("matches/2/27.json", matches)
        row = self.matrix()["rows"][0]
        self.assertEqual(len(row["metadata_versions"]), 3)
        self.assertEqual(row["bilateral_targets"]["h10_calendar"], 1)

    def test_destination_existing_or_inside_raw_refused(self) -> None:
        output = self.root / "matrix.json"
        with self.assertRaises(SystemExit) as caught:
            main(["--data-root", str(self.root), "--output", str(output),
                  "--audit-date", "2026-10-25"])
        self.assertEqual(caught.exception.code, 2)

    def test_candidate_requires_compatible_snapshot_and_reports_sources(self) -> None:
        with self.assertRaises(DataError):
            audit_candidate(LocalData(self.root), 2, 27,
                            audit_date="2026-10-25",
                            verification={"status": "incompatível"})
        for mid in range(1, 13):
            self.write(f"events/{mid}.json", fixture_events(mid))
            self.write(f"lineups/{mid}.json", fixture_lineups())
        verification = {"status": "compatível", "source": {"revision": "sintética"}}
        first = audit_candidate(LocalData(self.root), 2, 27, audit_date="2026-10-25", verification=verification)
        second = audit_candidate(LocalData(self.root), 2, 27, audit_date="2026-10-25", verification=verification)
        self.assertEqual(first, second)
        self.assertEqual(first["matches_read"], 12)
        self.assertEqual(first["matches_diagnosed"], 12)
        self.assertEqual(first["target_counts"]["h5_calculable"], 0)
        self.assertEqual(len(first["sources"]), 26)
        self.assertEqual(first["status"], "inconclusivo")

    def test_candidate_detects_cross_match_duplicate_event_ids(self) -> None:
        for mid in range(1, 13):
            events = fixture_events(mid)
            if mid == 2:
                events[0]["id"] = fixture_events(1)[0]["id"]
            self.write(f"events/{mid}.json", events)
            self.write(f"lineups/{mid}.json", fixture_lineups())
        result = audit_candidate(LocalData(self.root), 2, 27,
                                 audit_date="2026-10-25",
                                 verification={"status": "compatível", "source": {"revision": "sintética"}})
        self.assertEqual(result["status"], "reprovado")
        self.assertTrue(any("duplicado entre partidas" in failure["reason"]
                            for failure in result["structural_or_taxonomy_failures"]))

    def test_candidate_rejects_invalid_consumed_geometry(self) -> None:
        for mid in range(1, 13):
            events = fixture_events(mid)
            if mid == 1:
                events[0]["location"] = [121, 40]
            self.write(f"events/{mid}.json", events)
            self.write(f"lineups/{mid}.json", fixture_lineups())
        result = audit_candidate(LocalData(self.root), 2, 27,
                                 audit_date="2026-10-25",
                                 verification={"status": "compatível", "source": {"revision": "sintética"}})
        self.assertEqual(result["status"], "reprovado")
        self.assertEqual(result["quality_counts"]["core.locations_invalid"], 1)


def orientation_games(kind: str, count: int = 10) -> list[tuple[dict, list[dict]]]:
    games = []
    for mid in range(1, count + 1):
        events = []
        for team in (1, 2):
            for period in (1, 2):
                reverse = kind == "reverse" or kind == "mixed" and mid == count
                shot_x = 20 if reverse else 100
                for _ in range(3):
                    events.append({"team": {"id": team}, "period": period,
                                   "type": {"name": "Shot"}, "location": [shot_x, 40]})
                for _ in range(10):
                    events.append({"team": {"id": team}, "period": period,
                                   "type": {"name": "Pass"}, "location": [60, 40],
                                   "pass": {"end_location": [50 if reverse else 70, 40]}})
        games.append((fixture_match(mid, mid), events))
    return games


class OrientationTests(unittest.TestCase):
    def test_coherent_inverted_mixed_and_insufficient(self) -> None:
        self.assertEqual(audit_orientation(orientation_games("normal"))["status"], "coerente")
        self.assertEqual(audit_orientation(orientation_games("reverse"))["status"], "invertida")
        self.assertEqual(audit_orientation(orientation_games("mixed"))["status"], "mista")
        self.assertEqual(audit_orientation(orientation_games("normal", 9))["status"], "inconclusiva")

    def test_out_of_bounds_is_not_direction_evidence(self) -> None:
        games = orientation_games("normal")
        for _, events in games:
            for event in events:
                event["location"] = [121, 40]
        result = audit_orientation(games)
        self.assertEqual(result["status"], "inconclusiva")
        self.assertEqual(result["group_counts"], {"inconclusivo": 40})


class TaxonomyTests(unittest.TestCase):
    def test_unknown_type_is_observed_and_current_metrics_run(self) -> None:
        events = fixture_events(1)
        events.insert(0, {"id": "extra", "index": 99, "period": 1,
                          "timestamp": "00:01:00.000", "team": {"id": 1},
                          "type": {"id": 9999, "name": "Novo Evento"}})
        result = audit_game_taxonomy(fixture_match(1, 1), events, fixture_lineups())
        self.assertEqual(result["failures"], [])
        self.assertIn({"id": "9999", "name": "Novo Evento"}, result["types"])
        self.assertEqual((result["legacy_metric_count"], result["v3_metric_count"]), (21, 26))
        self.assertEqual(len(result["teams"]), 2)

    def test_consumed_payload_type_fails_without_fabricating_zero(self) -> None:
        events = fixture_events(1)
        events[0]["pass"] = "incorreto"
        result = audit_game_taxonomy(fixture_match(1, 1), events, fixture_lineups())
        self.assertIn("Pass sem objeto pass.", result["failures"])
        self.assertEqual(result["teams"], [])
        events = fixture_events(1)
        events[0]["under_pressure"] = "false"
        result = audit_game_taxonomy(fixture_match(1, 1), events, fixture_lineups())
        self.assertTrue(any("under_pressure" in failure for failure in result["failures"]))

    def test_spatial_and_xg_lacunas_are_reported(self) -> None:
        events = fixture_events(1)
        events[0]["location"] = [121, 40]
        events[6]["shot"] = {}
        result = audit_game_taxonomy(fixture_match(1, 1), events, fixture_lineups())
        self.assertEqual(result["gaps"]["Pass sem geometria válida"], 1)
        self.assertEqual(result["gaps"]["Shot sem xG válido"], 1)
        self.assertEqual(result["failures"], [])
        self.assertNotIn("xg_for", result["teams"][0]["legacy_calculable"])


class TemporalCore02Tests(LocalFixture):
    def setUp(self) -> None:
        super().setUp()
        self.matches = [fixture_match(mid, mid) for mid in range(1, 15)]
        self.matches[11]["match_date"] = self.matches[12]["match_date"]
        self.matches[11]["kick_off"] = "10:00:00.000"
        self.matches.reverse()  # calendário fora de ordem
        self.write("matches/2/27.json", self.matches)
        self.write("matches/2/28.json", [dict(fixture_match(99, 1), season={"season_id": 28})])
        self.write("competitions.json", [
            {"competition_id": 2, "season_id": 27, "competition_name": "Sintética", "season_name": "2020"},
            {"competition_id": 2, "season_id": 28, "competition_name": "Sintética", "season_name": "outra"},
        ])
        for mid in range(10, 15):
            self.write(f"events/{mid}.json", fixture_events(mid))
            self.write(f"lineups/{mid}.json", fixture_lineups())
        self.request = AnalysisRequest(2, 27, 1, 2, target_match_id=13)

    def _read_paths(self, request: AnalysisRequest, *, v3: bool = False) -> tuple[object, list[str]]:
        paths = []
        original = LocalData.read

        def observed(data: LocalData, relative: str):
            paths.append(relative)
            return original(data, relative)

        with patch.object(LocalData, "read", observed):
            report = analyze(self.root, request, include_v3=v3)
        return report, paths

    def test_target_future_same_day_and_other_season_never_opened(self) -> None:
        for window in (1, 5, 10):
            request = replace(self.request, recent_matches_window=window)
            report, paths = self._read_paths(request, v3=True)
            expected = list(range(1, 12))[-window:]
            self.assertEqual(report.team_profile.match_ids, expected)
            self.assertEqual(report.opponent_profile.match_ids, expected)
            self.assertFalse(any(f"/{mid}.json" in path for path in paths
                                 for mid in (12, 13, 14, 99)))
            self.assertFalse(any("matches/2/28" in path for path in paths))
        for mid in (12, 13, 14):
            for kind in ("events", "lineups"):
                (self.root / kind / f"{mid}.json").write_text("INVALID JSON", encoding="utf-8")
        report, paths = self._read_paths(self.request, v3=True)
        self.assertEqual(report.team_profile.match_ids, list(range(2, 12)))
        self.assertFalse(any(f"/{mid}.json" in path for path in paths
                             for mid in (12, 13, 14)))

    def test_free_cut_first_day_and_missing_history(self) -> None:
        target, _ = self._read_paths(replace(self.request, recent_matches_window=5))
        free, _ = self._read_paths(AnalysisRequest(2, 27, 1, 2,
                                                   cutoff_date="2020-01-13", recent_matches_window=5))
        self.assertEqual(target.team_profile.match_ids, free.team_profile.match_ids)
        first, paths = self._read_paths(replace(self.request, target_match_id=1))
        self.assertEqual(first.team_profile.match_ids, [])
        self.assertFalse(any(path.startswith(("events/", "lineups/")) for path in paths))
        (self.root / "events/11.json").unlink()
        short, paths = self._read_paths(replace(self.request, recent_matches_window=1))
        self.assertEqual(short.team_profile.match_ids, [])
        self.assertIn("Partida 11", " ".join(short.data_gaps))
        self.assertNotIn("events/10.json", paths)

    def test_target_must_match_selected_pair_and_teams(self) -> None:
        with self.assertRaises(DataError):
            self._read_paths(replace(self.request, target_match_id=99))
        with self.assertRaises(DataError):
            self._read_paths(replace(self.request, season_id=28, target_match_id=13))


if __name__ == "__main__":
    unittest.main()
