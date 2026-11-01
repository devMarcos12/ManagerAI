"""Fluxo por equipe: equivalência, limites temporais e contratos sem dados reais."""
from copy import deepcopy
from dataclasses import asdict, replace
import importlib.util
import json
import unittest
from unittest.mock import patch

from managerai.coach_service import TeamRequest, analyze_team, coach_catalog, team_preview
from managerai.data_loader import DataError, LocalData
from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest
from test_managerai import LocalFixture, fixture_events


class CoachTests(LocalFixture):
    def request_team(self, **kwargs):
        return TeamRequest(2, 27, 1, '2020-01-08', **kwargs)

    def test_individual_profile_equals_existing_core_without_opponent(self):
        result = analyze_team(self.root, self.request_team())
        legacy = analyze(self.root, AnalysisRequest(2, 27, 1, 2, cutoff_date='2020-01-08'))
        self.assertEqual(result['profile'], asdict(legacy.team_profile))
        self.assertNotIn('opponent_id', result['request'])
        self.assertNotIn('plans', result)
        self.assertEqual(result, analyze_team(self.root, self.request_team()))
        self.assertTrue(result['methodology']['sources'])
        self.assertEqual(len(result['profile']['metrics']), 21)

    def test_cutoff_day_future_and_missing_files_never_fill_window(self):
        # A data futura e o dia inteiro do corte contêm JSON inválido: não podem ser lidos.
        for mid in (8, 9):
            (self.root / f'events/{mid}.json').write_text('invalid JSON')
        (self.root / 'events/7.json').unlink()
        request = self.request_team(recent_matches_window=2)
        preview = team_preview(self.root, request)
        self.assertEqual(preview['team']['selected_match_ids'], (6, 7))
        self.assertEqual(preview['team']['missing_event_match_ids'], (7,))
        result = analyze_team(self.root, request)
        self.assertEqual(result['profile']['match_ids'], [6])
        self.assertEqual(result['profile']['metrics']['shots_for']['match_ids'], [6])
        self.assertEqual(result['sample_status'], 'amostra insuficiente')
        self.assertFalse(any(s['path'] in ['events/8.json', 'events/9.json', 'events/5.json'] for s in result['methodology']['sources']))

    def test_empty_history_preserves_nulls_and_does_not_read_events(self):
        with patch.object(LocalData, 'events', side_effect=AssertionError('leitura indevida')):
            result = analyze_team(self.root, replace(self.request_team(), cutoff_date='2020-01-01'))
        self.assertEqual(result['profile']['match_ids'], [])
        self.assertTrue(all(m['value'] is None and m['sample_size'] == 0 for m in result['profile']['metrics'].values()))

    def test_catalog_aggregates_team_identity_but_keeps_seasons_separate(self):
        catalog = json.loads((self.root/'competitions.json').read_text())
        catalog.append({**catalog[0], 'season_id': 28, 'season_name': '2021'})
        self.write('competitions.json', catalog)
        matches = deepcopy(self.matches)
        for m in matches:
            m['match_id'] += 100
            m['match_date'] = m['match_date'].replace('2020', '2021')
            m['season']['season_id'] = 28
        self.write('matches/2/28.json', matches)
        with patch.object(LocalData, 'events', side_effect=AssertionError('catálogo não lê eventos')):
            index = coach_catalog(self.root)
        self.assertEqual(len(index['teams']), 2)
        self.assertEqual([r['season_id'] for r in index['teams'][0]['recuts']], [28, 27])
        self.assertEqual(index['teams'][0]['recuts'][0]['event_matches'], 0)
        self.assertEqual(analyze_team(self.root, self.request_team())['profile']['match_ids'], list(range(1, 8)))
        self.assertEqual(analyze_team(self.root, TeamRequest(2, 28, 1, '2021-01-08'))['profile']['match_ids'], [])

    def test_unrelated_invalid_calendar_warns_and_does_not_hide_valid_teams(self):
        catalog = json.loads((self.root/'competitions.json').read_text())
        self.write('competitions.json', catalog + [{**catalog[0], 'season_id': 28}])
        self.write('matches/2/28.json', [{'invalid': True}])
        result = coach_catalog(self.root)
        self.assertEqual(len(result['teams']), 2)
        self.assertEqual(len(result['warnings']), 1)
        with self.assertRaises(DataError):
            analyze_team(self.root, TeamRequest(2, 27, 999, '2020-01-08'))

    def test_preview_does_not_read_content_and_reports_missing_event_files(self):
        (self.root/'events/7.json').unlink()
        with patch.object(LocalData, 'events', side_effect=AssertionError('prévia não lê eventos')):
            result = team_preview(self.root, self.request_team())
        self.assertEqual(result['team']['event_match_ids'], tuple(range(1, 7)))
        self.assertEqual(result['team']['missing_event_match_ids'], (7,))

    def test_missing_xg_is_not_zero_and_remains_metric_specific(self):
        events = fixture_events(7)
        next(e for e in events if e['type']['name'] == 'Shot')['shot'].pop('statsbomb_xg')
        self.write('events/7.json', events)
        result = analyze_team(self.root, self.request_team())
        self.assertEqual(result['profile']['metrics']['shots_for']['sample_size'], 7)
        self.assertEqual(result['profile']['metrics']['xg_for']['sample_size'], 6)
        self.assertAlmostEqual(result['profile']['metrics']['xg_for']['value'], .4)

    def test_validation_rejects_invalid_dates_types_and_windows(self):
        for delta in ({'team_id': True}, {'cutoff_date': '2020-02-30'}, {'cutoff_date': '20200108'},
                      {'recent_matches_window': 0}, {'recent_matches_window': 21}, {'recent_matches_window': True}):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                replace(self.request_team(), **delta)


@unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'), 'API opcional')
class CoachAPITests(LocalFixture):
    def setUp(self):
        super().setUp()
        from fastapi.testclient import TestClient
        from managerai.api import create_app
        self.client = TestClient(create_app(data_root=self.root))
        self.body = asdict(TeamRequest(2, 27, 1, '2020-01-08'))

    def test_catalog_preview_analysis_and_typed_contract(self):
        self.assertEqual(self.client.get('/v1/coach/teams').status_code, 200)
        self.assertEqual(self.client.post('/v1/team-coverage', json=self.body).status_code, 200)
        response = self.client.post('/v1/team-analyses', json=self.body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['profile']['match_ids'], list(range(1, 8)))
        schema = self.client.get('/openapi.json').json()
        self.assertIn('TeamReportBody', schema['components']['schemas'])
        self.assertIn('/v1/analyses', schema['paths'])

    def test_strict_validation_and_invalid_team_do_not_fabricate_opponent(self):
        for delta in ({'opponent_id': 2}, {'team_id': True}, {'recent_matches_window': 21},
                      {'cutoff_date': '2020-02-30'}, {'team_id': 999}, {'cutoff_date': None}):
            response = self.client.post('/v1/team-analyses', json={**self.body, **delta})
            self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.client.post('/v1/team-analyses', content='x'*65000).status_code, 413)

    def test_shared_rate_limit_with_comparison_and_released_slot_after_error(self):
        from managerai.data_loader import DataError
        with patch('managerai.api.analyze_team', side_effect=DataError('fixture')):
            self.assertEqual(self.client.post('/v1/team-analyses', json=self.body).status_code, 422)
        for _ in range(9):
            self.assertEqual(self.client.post('/v1/team-analyses', json=self.body).status_code, 200)
        pair = {'analysis': {**self.body, 'opponent_id': 2}}
        self.assertEqual(self.client.post('/v1/analyses', json=pair).status_code, 429)
        self.assertEqual(self.client.post('/v1/team-analyses', json=self.body).status_code, 429)
