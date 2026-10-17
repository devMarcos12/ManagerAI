"""V3 opcional na UI com o mesmo resultado da API, sem eventos antes do envio."""
import os
import importlib.util
import unittest
from unittest.mock import patch
from test_managerai import LocalFixture
from test_streamlit_ui import APP, HAS_STREAMLIT
from managerai.pipeline import analyze


@unittest.skipUnless(HAS_STREAMLIT and importlib.util.find_spec('matplotlib'), 'UI V3 opcional')
class V3UI(LocalFixture):
    def test_unaudited_season_disables_v3_and_clears_selected_mode(self):
        import json
        from copy import deepcopy
        from streamlit.testing.v1 import AppTest
        competitions = json.loads((self.root / 'competitions.json').read_text())
        competitions.append(dict(competition_id=2, season_id=28, competition_name='Competição sintética', season_name='2021'))
        self.write('competitions.json', competitions)
        matches = deepcopy(self.matches)
        for match in matches:
            match['season']['season_id'] = 28
        self.write('matches/2/28.json', matches)
        with patch.dict(os.environ, {'MANAGERAI_DATA_ROOT': str(self.root)}):
            with patch('managerai.data_loader.LocalData.events', side_effect=AssertionError('Evento antes do envio')):
                app = AppTest.from_file(str(APP), default_timeout=60).run()
                app.selectbox(key='season_2').set_value(27).run()
                app.checkbox(key='include_v3').check().run()
                app.selectbox(key='season_2').set_value(28).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.checkbox(key='include_v3').disabled)
        self.assertFalse(app.checkbox(key='include_v3').value)

    def test_v3_submission_downloads_and_two_figures(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict(os.environ, {'MANAGERAI_DATA_ROOT': str(self.root)}):
            with patch('managerai.data_loader.LocalData.events', side_effect=AssertionError('Evento antes do envio')):
                app = AppTest.from_file(str(APP), default_timeout=60).run()
                app.selectbox(key='match_2_27_1_2').set_value(8).run()
                app.checkbox(key='include_v3').check().run()
            app.button(key='FormSubmitter:analysis_form-Analisar confronto').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['report'].to_json(), analyze(self.root, self.request, include_v3=True).to_json())
            self.assertEqual(len(app.get('download_button')), 2)
            self.assertEqual(len(app.get('image')), 2)
            # Toggling versions clears results rather than changing old report downloads silently.
            app.checkbox(key='include_v3').uncheck().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('download_button')), 0)


@unittest.skipUnless(HAS_STREAMLIT and importlib.util.find_spec('matplotlib') and os.environ.get('MANAGERAI_RUN_LOCAL_TESTS') == '1', 'Dataset real opcional')
class V3RealUI(unittest.TestCase):
    def test_city_and_partial_coverage_v3_in_browser_runtime(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict(os.environ, {'MANAGERAI_DATA_ROOT': str(APP.parent / 'open-data/data')}):
            app = AppTest.from_file(str(APP), default_timeout=60).run()
            app.checkbox(key='include_v3').check().run()
            app.button(key='FormSubmitter:analysis_form-Analisar confronto').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['report'].schema_version, '1.1.0')
            self.assertTrue(app.session_state['report'].tactical_v3['hypotheses'])
            self.assertEqual(len(app.get('image')), 2)
            app.selectbox(key='competition').set_value(11).run()
            app.selectbox(key='season_11').set_value(90).run()
            app.selectbox(key='team_11_90').set_value(220).run()
            app.selectbox(key='opponent_11_90_220').set_value(217).run()
            app.selectbox(key='match_11_90_220_217').set_value(3773497).run()
            app.button(key='FormSubmitter:analysis_form-Analisar confronto').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['report'].tactical_v3['hypotheses'], [])
            self.assertEqual(len(app.get('image')), 2)
            self.assertTrue(any('Amostra insuficiente' in w.value for w in app.warning))
