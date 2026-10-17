"""Prévia sem leitura de eventos e suficiência por métricas, incluindo casos locais."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from managerai.coverage import CORE_METRICS, preview_coverage, report_sufficiency
from managerai.data_loader import LocalData
from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest
from test_managerai import fixture_events, fixture_lineups, fixture_match


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.write("competitions.json", [{"competition_id": 2, "season_id": 27,
                                        "competition_name": "Teste", "season_name": "2020"}])
        self.write("matches/2/27.json", [fixture_match(i, i) for i in range(1, 10)])
        for i in range(1, 10):
            events = fixture_events(i)
            events.append({"id": f"synthetic-{i}-11", "index": 11, "period": 1,
                           "timestamp": "00:02:00.000", "team": {"id": 2},
                           "player": {"id": 201}, "type": {"name": "Pass"},
                           "location": [40, 40], "pass": {"end_location": [50, 40]}})
            self.write(f"events/{i}.json", events)
            self.write(f"lineups/{i}.json", fixture_lineups())
        self.request = AnalysisRequest(2, 27, 1, 2, target_match_id=8, recent_matches_window=3)

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_preview_uses_only_calendar_and_file_presence(self):
        data = LocalData(self.root)
        with patch.object(data, "events", side_effect=AssertionError("Não ler eventos")), \
             patch.object(data, "lineups", side_effect=AssertionError("Não ler escalações")):
            preview = preview_coverage(data, self.request)
        self.assertEqual(preview.team.calendar_matches_before_cutoff, 7)
        self.assertEqual(preview.team.selected_match_ids, (5, 6, 7))
        self.assertEqual(preview.team.event_match_ids, (5, 6, 7))
        self.assertEqual(preview.team.available_period_start, "2020-01-01")
        self.assertEqual(preview.team.selected_period_start, "2020-01-05")
        self.assertEqual(set(data.sources), {"competitions.json", "matches/2/27.json"})
        self.assertIn("comparação não confiável", preview.warnings[0])

    def test_missing_files_never_expand_window(self):
        # Temporary synthetic file only; originals are never modified.
        (self.root / "events/6.json").unlink()
        preview = preview_coverage(LocalData(self.root), self.request)
        self.assertEqual(preview.team.selected_matches, 3)
        self.assertEqual(preview.team.matches_with_events, 2)
        self.assertEqual(preview.team.event_match_ids, (5, 7))
        self.assertEqual(preview.team.missing_event_match_ids, (6,))
        self.assertIn("a janela não será ampliada", " ".join(preview.warnings))

    def test_empty_history_has_no_period_and_not_zero_observation(self):
        req = replace(self.request, target_match_id=None, cutoff_date="2020-01-01")
        preview = preview_coverage(LocalData(self.root), req)
        self.assertEqual(preview.team.event_match_ids, ())
        self.assertIsNone(preview.team.event_period_start)
        self.assertIsNone(preview.team.selected_period_start)

    def test_same_day_excluded_and_corrupt_event_content_not_read(self):
        self.write("matches/2/27.json", [fixture_match(1, 1), fixture_match(2, 8), fixture_match(8, 8)])
        (self.root / "events/1.json").write_text("invalid JSON", encoding="utf-8")
        preview = preview_coverage(LocalData(self.root), self.request)
        self.assertEqual(preview.team.event_match_ids, (1,))
        self.assertEqual(preview.team.event_period_start, "2020-01-01")
        self.assertIn("apenas 1 jogo anterior", preview.team.warnings[0])
        self.assertNotIn("1 jogos", preview.team.warnings[0])

    def test_report_sufficiency_uses_metric_samples_without_mutation(self):
        report = analyze(self.root, replace(self.request, recent_matches_window=7))
        frozen = report.to_json()
        self.assertTrue(report_sufficiency(report).sufficient)
        self.assertEqual(report.to_json(), frozen)
        report.team_profile.metrics["xg_for"] = replace(report.team_profile.metrics["xg_for"], sample_size=1)
        status = report_sufficiency(report)
        self.assertFalse(status.sufficient)
        self.assertEqual(status.status, "amostra insuficiente")
        self.assertEqual(status.team.insufficient_metrics, ("xg_for",))
        self.assertEqual(status.team.minimum_sample_size, 1)

    def test_missing_or_null_core_metric_is_insufficient(self):
        report = analyze(self.root, replace(self.request, recent_matches_window=7))
        metric = report.team_profile.metrics["xg_for"]
        report.team_profile.metrics["xg_for"] = replace(metric, value=None)
        self.assertEqual(report_sufficiency(report).team.sample_sizes["xg_for"], 0)
        del report.team_profile.metrics["xg_for"]
        self.assertEqual(report_sufficiency(report).team.sample_sizes["xg_for"], 0)

    def test_minimum_is_configurable_but_positive(self):
        report = analyze(self.root, self.request)
        self.assertFalse(report_sufficiency(report).sufficient)
        self.assertTrue(report_sufficiency(report, minimum_matches=3).sufficient)
        for invalid in (0, -1, True):
            with self.assertRaises(ValueError):
                preview_coverage(LocalData(self.root), self.request, minimum_matches=invalid)
            with self.assertRaises(ValueError):
                report_sufficiency(report, minimum_matches=invalid)
        with self.assertRaises(ValueError):
            report_sufficiency(report, core_metrics=())


ROOT = Path(__file__).resolve().parents[1] / "open-data/data"


@unittest.skipUnless(os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração local opcional")
class RealCoverageTests(unittest.TestCase):
    def test_city_arsenal_balanced_coverage(self):
        request = AnalysisRequest(2, 27, 36, 1, target_match_id=3754314)
        preview = preview_coverage(LocalData(ROOT), request)
        self.assertEqual((preview.team.matches_with_events, preview.opponent.matches_with_events), (10, 10))
        self.assertEqual(preview.warnings, ())
        report = analyze(ROOT, request)
        self.assertTrue(report_sufficiency(report).sufficient)
        for profile in (report.team_profile, report.opponent_profile):
            self.assertTrue(all(profile.metrics[key].sample_size == 10 for key in CORE_METRICS))

    def test_real_madrid_barcelona_partial_coverage(self):
        request = AnalysisRequest(11, 90, 220, 217, cutoff_date="2021-04-10")
        preview = preview_coverage(LocalData(ROOT), request)
        self.assertEqual((preview.team.matches_with_events, preview.opponent.matches_with_events), (1, 10))
        self.assertEqual(preview.team.event_period_start, "2020-10-24")
        self.assertTrue(preview.warnings)
        report = analyze(ROOT, request)
        status = report_sufficiency(report)
        self.assertFalse(status.sufficient)
        self.assertEqual((status.team.minimum_sample_size, status.opponent.minimum_sample_size), (1, 10))
        self.assertEqual(report.tactical_hypotheses, [])


if __name__ == "__main__":
    unittest.main()
