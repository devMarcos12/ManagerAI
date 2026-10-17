"""Prévia reativa antes de executar, sem leitura dos eventos."""
import os
import unittest
from unittest.mock import patch
from test_streamlit_ui import APP, HAS_STREAMLIT
from test_managerai import LocalFixture


@unittest.skipUnless(HAS_STREAMLIT, "Streamlit opcional")
class CoverageUI(LocalFixture):
    def setUp(self):
        super().setUp()
        self.env = patch.dict(os.environ, {"MANAGERAI_DATA_ROOT": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(APP), default_timeout=30).run()

    def test_window_updates_preview_without_event_reads(self):
        with patch("managerai.data_loader.LocalData.events", side_effect=AssertionError("Leitura prematura")):
            app = self.app()
            app.selectbox(key="match_2_27_1_2").set_value(8).run()
            app.number_input(key="window").set_value(1).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("apenas 1 jogo anterior" in w.value for w in app.warning))
        text = " ".join(m.value for m in app.markdown)
        self.assertIn("1 jogo na janela", text)
        self.assertNotIn("1 jogos", text)
        self.assertEqual(len(app.get("download_button")), 0)


@unittest.skipUnless(HAS_STREAMLIT and os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração real opcional")
class PartialCoverageUI(unittest.TestCase):
    def test_real_madrid_barcelona_warns_before_and_after_submit(self):
        from streamlit.testing.v1 import AppTest
        root = APP.parent / "open-data/data"
        with patch.dict(os.environ, {"MANAGERAI_DATA_ROOT": str(root)}):
            app = AppTest.from_file(str(APP), default_timeout=60).run()
            app.selectbox(key="competition").set_value(11).run()
            app.selectbox(key="season_11").set_value(90).run()
            app.selectbox(key="team_11_90").set_value(220).run()
            app.selectbox(key="opponent_11_90_220").set_value(217).run()
            app.selectbox(key="match_11_90_220_217").set_value(3773497).run()
            self.assertFalse(app.exception)
            self.assertTrue(any("Real Madrid: apenas 1 jogo" in w.value for w in app.warning))
            app.button(key="FormSubmitter:analysis_form-Analisar confronto").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Amostra insuficiente" in w.value for w in app.warning))
        self.assertEqual(app.session_state["report"].metadata["matches_analyzed_team"], 1)
        self.assertEqual(app.session_state["report"].tactical_hypotheses, [])
        text = " ".join(m.value for m in app.markdown)
        self.assertNotIn("1 jogos", text)
