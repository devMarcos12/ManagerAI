"""Testes funcionais opcionais da interface, com fixtures locais explícitas."""
from datetime import date
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest
from managerai.ui_support import available_catalog, friendly_error, match_options, run_analysis
from managerai.data_inventory import load_season
from managerai.data_loader import DataError, LocalData
from test_managerai import LocalFixture

HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None
if HAS_STREAMLIT:
    import streamlit as st
    from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


class AdapterTests(LocalFixture):
    def test_metadata_options_exclude_score_and_identical_teams(self):
        self.matches[0].update(home_score=99, away_score=88)
        self.write("matches/2/27.json", self.matches)
        season = load_season(LocalData(self.root), 2, 27)
        matches = match_options(season, 1, 2)
        self.assertEqual(len(matches), 9)
        self.assertTrue(all("score" not in json.dumps(m) for m in matches))
        self.assertEqual(match_options(season, 1, 1), [])
        self.assertEqual(len(available_catalog(self.root)), 1)

    def test_ui_adapter_equals_cli_pipeline(self):
        self.assertEqual(run_analysis(self.root, self.request).to_json(), analyze(self.root, self.request).to_json())

    def test_errors_are_readable(self):
        with self.assertRaises(DataError) as ctx:
            available_catalog(self.root / "ausente")
        self.assertIn("dados locais", friendly_error(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            AnalysisRequest(2, 27, 1, 1, target_match_id=1)
        self.assertIn("diferentes", friendly_error(ctx.exception))


@unittest.skipUnless(HAS_STREAMLIT, "Interface opcional: instale '.[ui]' no Python usado pelos testes")
class StreamlitTests(LocalFixture):
    def setUp(self):
        super().setUp()
        self.env = patch.dict(os.environ, {"MANAGERAI_DATA_ROOT": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def app(self):
        return AppTest.from_file(str(APP), default_timeout=30).run()

    def submit(self, app):
        return app.button(key="FormSubmitter:analysis_form-Analisar confronto").click().run()

    def test_names_distinct_opponents_and_no_pre_submit_event_reads(self):
        with patch("managerai.data_loader.LocalData.events", side_effect=AssertionError("Eventos lidos antes de analisar")):
            app = self.app()
            self.assertFalse(app.exception)
            team = app.selectbox(key="team_2_27")
            self.assertEqual(team.options, ["Equipe sintética A", "Equipe sintética B"])
            self.assertNotIn("Equipe sintética A", app.selectbox(key="opponent_2_27_1").options)
            app.selectbox(key="team_2_27").set_value(2).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key="opponent_2_27_2").value, 1)

    def test_submit_matches_pipeline_and_downloads_have_correct_payload(self):
        app = self.app()
        app.selectbox(key="match_2_27_1_2").set_value(8).run()
        with patch("streamlit.download_button", wraps=st.download_button) as downloads:
            self.submit(app)
        self.assertFalse(app.exception)
        expected = analyze(self.root, self.request)
        self.assertEqual(app.session_state["report"].to_json(), expected.to_json())
        self.assertEqual(downloads.call_count, 2)
        self.assertIn("Preparação pré-jogo", downloads.call_args_list[0].args[1].decode())
        self.assertEqual(json.loads(downloads.call_args_list[1].args[1]), json.loads(expected.to_json()))
        self.assertEqual(downloads.call_args_list[1].kwargs["mime"], "application/json")
        self.assertEqual(len(app.get("download_button")), 2)
        self.assertTrue(all(d.proto.url for d in app.get("download_button")))
        with patch("managerai.streamlit_ui.run_analysis", side_effect=AssertionError("Download recalculou o pipeline")):
            app.get("download_button")[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["report"].to_json(), expected.to_json())

    def test_empty_history_and_small_window_abstain(self):
        app = self.app()
        app.radio(key="reference_mode").set_value("Data de corte livre").run()
        app.date_input(key="cutoff_2_27").set_value(date(2020, 1, 1)).run()
        self.submit(app)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["report"].team_profile.match_ids, [])
        self.assertEqual(app.session_state["report"].tactical_hypotheses, [])
        self.assertTrue(any("insuficiente" in w.value for w in app.warning))
        app.radio(key="reference_mode").set_value("Partida histórica").run()
        app.number_input(key="window").set_value(2)
        self.submit(app)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["report"].team_profile.match_ids), 2)
        self.assertEqual(app.session_state["report"].tactical_hypotheses, [])

    def test_missing_data_error_without_traceback(self):
        with patch.dict(os.environ, {"MANAGERAI_DATA_ROOT": str(self.root / "ausente")}):
            app = self.app()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertIn("dados locais", app.error[0].value)

    def test_wrong_target_error_clears_stale_result(self):
        app = self.app()
        self.submit(app)
        with patch("managerai.streamlit_ui.run_analysis", side_effect=DataError("Partida-alvo não corresponde ao confronto e recorte selecionados.")):
            self.submit(app)
        self.assertFalse(app.exception)
        self.assertIn("Partida-alvo", app.error[0].value)
        self.assertEqual(len(app.get("download_button")), 0)

    def test_selection_change_clears_report_without_recalculation(self):
        app = self.app()
        self.submit(app)
        with patch("managerai.streamlit_ui.run_analysis", side_effect=AssertionError("Mudança de campo recalculou o pipeline")):
            app.radio(key="reference_mode").set_value("Data de corte livre").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("download_button")), 0)


@unittest.skipUnless(HAS_STREAMLIT and os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração real UI opcional")
class StreamlitLocalIntegrationTests(unittest.TestCase):
    def test_city_arsenal_by_name_equals_v1_and_cli(self):
        root = APP.parent / "open-data/data"
        with patch.dict(os.environ, {"MANAGERAI_DATA_ROOT": str(root)}):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key="team_2_27").value, 36)
            self.assertEqual(app.selectbox(key="opponent_2_27_36").value, 1)
            self.assertEqual(app.selectbox(key="match_2_27_36_1").value, 3754314)
            app.button(key="FormSubmitter:analysis_form-Analisar confronto").click().run()
        self.assertFalse(app.exception)
        expected = (APP.parent / "outputs/mvp_demo_city_arsenal/report.json").read_text()
        self.assertEqual(app.session_state["report"].to_json(), expected)
