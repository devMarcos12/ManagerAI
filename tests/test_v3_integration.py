"""Compatibilidade, exclusão temporal e artefatos novos V3."""
from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
import json
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from managerai.cli import main
from managerai.pipeline import analyze
from managerai.report_renderer import render_markdown
from managerai.report_schema import AnalysisRequest
from test_managerai import LocalFixture


class V3Integration(LocalFixture):
    def test_additive_schema_preserves_every_original_field(self):
        old = analyze(self.root, self.request)
        new = analyze(self.root, self.request, include_v3=True)
        values = new.to_dict()
        self.assertEqual(values.pop('schema_version'), '1.1.0')
        payload = values.pop('tactical_v3')
        expected = old.to_dict()
        expected.pop('schema_version')
        self.assertEqual(values, expected)
        self.assertEqual(payload['formula_version'], '3.0.0')
        self.assertEqual(len(payload['team_profile']['match_ids']), 7)
        self.assertEqual(payload['hypotheses'], [])  # opponent passing missing
        self.assertEqual(new.to_json(), analyze(self.root, self.request, include_v3=True).to_json())

    def test_target_future_events_and_lineups_never_read_or_change_output(self):
        before = analyze(self.root, self.request, include_v3=True).to_json()
        for mid in (8, 9):
            for kind in ('events', 'lineups'):
                (self.root / kind / f'{mid}.json').write_text('INVALID JSON')
        self.matches[-1]['home_score'] = 333
        self.matches[-1]['away_score'] = 222
        # Calendar source hash changes when edited, so compare before changing its bytes.
        self.assertEqual(before, analyze(self.root, self.request, include_v3=True).to_json())

    def test_empty_and_single_match_remain_unavailable_or_uncertain(self):
        empty = analyze(self.root, replace(self.request, target_match_id=1), include_v3=True)
        for p in ('team_profile', 'opponent_profile'):
            self.assertTrue(all(m['value'] is None and m['sample_size'] == 0
                                for m in empty.tactical_v3[p]['metrics'].values()))
        single = analyze(self.root, replace(self.request, recent_matches_window=1), include_v3=True)
        self.assertEqual(single.tactical_v3['hypotheses'], [])
        self.assertTrue(all(m['standard_deviation'] is None
                            for m in single.tactical_v3['team_profile']['metrics'].values()))
        self.assertNotIn('1 jogos', render_markdown(single))

    def test_v3_rejects_recuts_without_orientation_and_field_audit(self):
        from managerai.v3_pipeline import extend_report
        from managerai.data_loader import DataError
        old = analyze(self.root, self.request)
        old.request = replace(self.request, season_id=999)
        with self.assertRaisesRegex(DataError, 'recorte auditado'):
            extend_report(self.root, old)

    def test_manual_context_does_not_change_indicators_or_rules(self):
        old = analyze(self.root, self.request, include_v3=True)
        new = analyze(self.root, replace(self.request, venue='fora', match_context='eliminatório',
                                        strategic_objective='buscar gol', notes='declaração manual'), include_v3=True)
        self.assertEqual(old.team_profile, new.team_profile)
        self.assertEqual(old.opponent_profile, new.opponent_profile)
        self.assertEqual(old.tactical_v3, new.tactical_v3)

    def test_data_changed_between_versions_is_rejected(self):
        from managerai.v3_pipeline import extend_report
        from managerai.data_loader import DataError
        old = analyze(self.root, self.request)
        events = json.loads((self.root / 'events/1.json').read_text())
        events[0]['location'] = [74, 30]
        self.write('events/1.json', events)
        with self.assertRaises(DataError):
            extend_report(self.root, old)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Visualizações opcionais: requirements-v3.txt")
    def test_cli_writes_new_artifacts_and_refuses_overwrite(self):
        output = self.root.parent / 'new-report'
        args = ['--data-root', str(self.root), 'analyze', '--competition-id', '2', '--season-id', '27',
                '--team-id', '1', '--opponent-id', '2', '--target-match-id', '8', '--v3', '--output-dir', str(output)]
        with redirect_stdout(StringIO()):
            self.assertEqual(main(args), 0)
        report = json.loads((output / 'report.json').read_text())
        self.assertEqual(report['schema_version'], '1.1.0')
        self.assertEqual(len(list(output.glob('*.png'))), 2)
        self.assertTrue(all(p.stat().st_size > 1000 for p in output.glob('*.png')))
        before = {p.name: p.read_bytes() for p in output.iterdir()}
        from contextlib import redirect_stderr
        with redirect_stderr(StringIO()):
            self.assertEqual(main(args), 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})


@unittest.skipUnless(os.environ.get('MANAGERAI_RUN_LOCAL_TESTS') == '1', 'Dataset real opcional')
class V3RealIntegration(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_city_baseline_exact_and_new_metrics_hypotheses_traceable(self):
        request = AnalysisRequest(2, 27, 36, 1, target_match_id=3754314)
        old = analyze(self.root / 'open-data/data', request)
        self.assertEqual(old.to_json(), (self.root / 'outputs/mvp_demo_city_arsenal/report.json').read_text())
        report = analyze(self.root / 'open-data/data', request, include_v3=True)
        self.assertEqual(report.team_profile, old.team_profile)
        self.assertEqual(report.opponent_profile, old.opponent_profile)
        self.assertEqual(report.tactical_hypotheses, old.tactical_hypotheses)
        self.assertGreaterEqual(len(report.tactical_v3['hypotheses']), 1)
        for h in report.tactical_v3['hypotheses']:
            self.assertTrue(h['observation'] and h['risks'] and h['preconditions'] and h['limitations'])
            for path in h['evidence_metrics']:
                value = report.to_dict()
                for part in path.split('.'):
                    value = value[part]
                self.assertGreaterEqual(value['sample_size'], 5)
                self.assertIsNotNone(value['value'])

    def test_real_madrid_barcelona_abstains_with_one_versus_ten(self):
        request = AnalysisRequest(11, 90, 220, 217, target_match_id=3773497)
        report = analyze(self.root / 'open-data/data', request, include_v3=True)
        self.assertEqual(len(report.team_profile.match_ids), 1)
        self.assertEqual(len(report.opponent_profile.match_ids), 10)
        self.assertEqual(report.tactical_v3['hypotheses'], [])
        self.assertIn('Amostra insuficiente', render_markdown(report))
        self.assertNotIn('1 jogos', render_markdown(report))
