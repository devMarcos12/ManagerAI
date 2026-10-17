"""Relatório e figuras V3 sobre eventos sintéticos, sem rede nem dados reais."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from managerai.pipeline import analyze
from managerai.v3_features import aggregate_v3, analyze_match_v3
from managerai.v3_presentation import render_v3_markdown
from test_managerai import LocalFixture, fixture_events, fixture_match

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from managerai.v3_plots import create_v3_figures
except ImportError:
    plt = None


class V3PresentationTests(LocalFixture):
    def v3_report(self):
        report = analyze(self.root, self.request)
        # Define explicit calculable passes in the opponent presentation fixture.
        source = report.team_profile.metrics["pass_accuracy"]
        report.opponent_profile.metrics["pass_accuracy"] = replace(source, value=50)
        profiles = []
        for tid, name in ((1, "Equipe sintética A"), (2, "Equipe sintética B")):
            rows = [analyze_match_v3(fixture_match(mid, mid), fixture_events(mid), tid, 90)
                    for mid in range(1, 8)]
            profiles.append(aggregate_v3(tid, name, rows))
        report.tactical_v3 = {
            "formula_version": "3.0.0", "team_profile": profiles[0], "opponent_profile": profiles[1],
            "hypotheses": [{"title": "Rever as entradas por passe", "observation": "Há entradas registradas no histórico.",
                            "action": "Selecionar situações de vídeo para ensaiar proteção.",
                            "condition": "Disponibilidade de vídeo das entradas observadas.",
                            "preconditions": ["Rever o vídeo antes do treino."],
                            "risks": ["Ajustes podem abrir outros espaços."],
                            "limitations": ["O registro não demonstra eficácia."],
                            "evidence_metrics": ["tactical_v3.opponent_profile.metrics.final_third_pass_entries"]}],
            "methodology": {},
        }
        return report

    def test_markdown_sections_numbers_periods_and_no_mutation(self):
        report = self.v3_report()
        before, extension = report.to_json(), deepcopy(report.tactical_v3)
        text = render_v3_markdown(report)
        for heading in ("Como o adversário ataca", "Como ele pressiona e recupera a bola", "Padrões observados dos jogadores", "Hipóteses para testar"):
            self.assertIn(heading, text)
        self.assertIn("01/01/2020 a 07/01/2020", text)
        self.assertIn("Jogos com informação", text)
        self.assertIn("1,00 por 90 min", text)
        self.assertIn("Rever as entradas por passe", text)
        self.assertIn("Riscos", text)
        self.assertIn("Limitações", text)
        self.assertIn("Disponibilidade de vídeo das entradas observadas.", text)
        self.assertNotIn("x>=80", text)
        self.assertNotIn("y<80/3", text)
        self.assertNotIn("Pressure", text)
        self.assertNotIn("eventos/90", text)
        self.assertNotIn("tactical_v3.opponent_profile", text)
        self.assertEqual(before, report.to_json())
        self.assertEqual(extension, report.tactical_v3)

    @unittest.skipUnless(plt, "Matplotlib opcional")
    def test_plot_scale_includes_larger_opponent_bar_and_annotation(self):
        report = self.v3_report()
        report.tactical_v3['opponent_profile']['metrics']['final_third_pass_entries']['value'] = 999
        figures = create_v3_figures(report)
        try:
            axes = figures['progression_entries'].axes
            self.assertEqual(axes[0].get_ylim(), axes[1].get_ylim())
            self.assertGreater(axes[0].get_ylim()[1], 999 * 1.1)
        finally:
            for figure in figures.values():
                plt.close(figure)

    def test_missing_extension_is_explicit(self):
        text = render_v3_markdown(SimpleNamespace())
        self.assertIn("Não disponível", text)

    def test_small_core_sample_suppresses_hypotheses_but_preserves_values(self):
        report = self.v3_report()
        metric = report.team_profile.metrics["xg_for"]
        report.team_profile.metrics["xg_for"] = replace(metric, sample_size=1)
        text = render_v3_markdown(report)
        self.assertIn("Amostra insuficiente", text)
        self.assertIn("consulta descritiva", text)
        self.assertIn("1,00 por 90 min", text)
        self.assertNotIn("Rever as entradas por passe", text)
        self.assertIn("Nenhuma hipótese V3 emitida", text)

    def test_missing_metric_has_no_fabricated_zero(self):
        report = self.v3_report()
        metric = report.tactical_v3["opponent_profile"]["metrics"]["progressive_passes"]
        metric.update(value=None, sample_size=0, per_match=[])
        text = render_v3_markdown(report)
        self.assertIn("indisponível | 0 | sem informação calculável", text)

    def test_sequences_show_eligible_period_and_friendly_exclusion_reason(self):
        report = self.v3_report()
        profile = report.tactical_v3["team_profile"]
        profile["sequence_metrics"] = {
            "observed_blocks": {"value": 12.0, "sample_size": 6,
                                "per_match": [{"match_date": "2020-01-02"}, {"match_date": "2020-01-07"}]},
            "entry_block_share": {"value": None, "sample_size": 0, "per_match": []},
        }
        profile["sequences"] = [{"match_id": 1, "match_date": "2020-01-01", "valid_blocks": None,
                                  "quality": {"invalid_or_decreasing_timestamp": 1},
                                  "blocks": [{"event_ids": ["internal-event-id"]}]}]
        before = deepcopy(report.tactical_v3)
        text = render_v3_markdown(report)
        self.assertIn("12,00 blocos observados por jogo | 6 | 02/01/2020 a 07/01/2020", text)
        self.assertIn("01/01/2020: jogo não calculável para sequências", text)
        self.assertIn("horários de ações fora de ordem ou inválidos", text)
        self.assertIn("não representam todas as posses reais", text)
        self.assertIn("não demonstram causalidade", text)
        self.assertNotIn("invalid_or_decreasing_timestamp", text)
        self.assertNotIn("internal-event-id", text)
        self.assertEqual(before, report.tactical_v3)

    def test_history_is_alphabetical_descriptive_and_has_individual_periods(self):
        report = self.v3_report()
        profile = report.tactical_v3["team_profile"]
        profile["historical"] = {
            "match_dates": {"1": "2020-01-01", "3": "2020-01-03"},
            "matches_with_initial_formation": 2,
            "players": [
                {"player_id": 222, "name": "Zeca sintético", "matches_with_actions": 1, "match_ids": [3],
                 "passes": 8, "passes_completed": 5, "carries": 2, "shots": 1, "pressures": 3, "xg": None},
                {"player_id": 111, "name": "Ana sintética", "matches_with_actions": 2, "match_ids": [1, 3],
                 "passes": 2, "passes_completed": 1, "carries": 1, "shots": 0, "pressures": 1, "xg": 0.0},
            ],
            "initial_formations": [{"formation": 433, "matches": 2, "share": 100, "match_ids": [1, 3]}],
            "formation_changes": [{"formation": 442, "match_date": "2020-01-03", "period": 2}],
        }
        before = deepcopy(report.tactical_v3)
        text = render_v3_markdown(report)
        self.assertLess(text.index("Ana sintética"), text.index("Zeca sintético"))
        self.assertIn("Ana sintética | 2 | 01/01/2020 a 03/01/2020", text)
        self.assertIn("Zeca sintético | 1 | 03/01/2020 a 03/01/2020", text)
        self.assertIn("desconhecida", text)
        self.assertIn("sem ranking", text)
        self.assertIn("4-3-3 | 2 | 2 | 100,00%", text)
        self.assertIn("03/01/2020 | 4-4-2 | 2º tempo | 1", text)
        self.assertNotIn("player_id", text)
        self.assertEqual(before, report.tactical_v3)

    @unittest.skipIf(plt is None, "matplotlib não instalado")
    def test_figures_are_exportable_and_leave_report_unchanged(self):
        report = self.v3_report()
        before = deepcopy(report.tactical_v3)
        figures = create_v3_figures(report)
        self.assertEqual(set(figures), {"shot_map", "progression_entries"})
        try:
            axes = figures["progression_entries"].axes
            self.assertEqual(axes[0].get_ylim(), axes[1].get_ylim())
            with tempfile.TemporaryDirectory() as temporary:
                for name, figure in figures.items():
                    target = Path(temporary) / (name + ".png")
                    figure.savefig(target, dpi=60)
                    self.assertGreater(target.stat().st_size, 1000)
                    self.assertIn("Fonte: StatsBomb", " ".join(text.get_text() for text in figure.texts))
            self.assertEqual(before, report.tactical_v3)
        finally:
            for figure in figures.values():
                plt.close(figure)

    @unittest.skipIf(plt is None, "matplotlib não instalado")
    def test_absent_positions_and_progression_are_marked_unavailable(self):
        report = self.v3_report()
        for side in ("team_profile", "opponent_profile"):
            profile = report.tactical_v3[side]
            profile["shots"] = [{"x": 121, "y": 40, "xg": 0.5}]
            for key in ("final_third_pass_entries", "final_third_carry_entries"):
                profile["metrics"][key].update(value=None, sample_size=0, per_match=[])
        figures = create_v3_figures(report)
        try:
            map_text = " ".join(text.get_text() for ax in figures["shot_map"].axes for text in ax.texts)
            bars_text = " ".join(text.get_text() for ax in figures["progression_entries"].axes for text in ax.texts)
            self.assertIn("Sem chutes com posição disponível", map_text)
            self.assertIn("não disponível", bars_text)
        finally:
            for figure in figures.values():
                plt.close(figure)

    @unittest.skipIf(plt is None, "matplotlib não instalado")
    def test_single_game_plot_plural_and_sample_warning(self):
        report = self.v3_report()
        report.tactical_v3["team_profile"]["match_ids"] = [1]
        metric = report.team_profile.metrics["xg_for"]
        report.team_profile.metrics["xg_for"] = replace(metric, sample_size=1)
        figures = create_v3_figures(report)
        try:
            title = figures["shot_map"].axes[0].get_title()
            self.assertIn("n=1 jogo da janela", title)
            self.assertNotIn("1 jogos", title)
            for figure in figures.values():
                self.assertIn("Amostra insuficiente", " ".join(text.get_text() for text in figure.texts))
        finally:
            for figure in figures.values():
                plt.close(figure)

    @unittest.skipIf(plt is None, "matplotlib não instalado")
    def test_unknown_xg_is_drawn_as_hollow_marker(self):
        report = self.v3_report()
        report.tactical_v3["team_profile"]["shots"] = [{"x": 100, "y": 40, "xg": None}]
        figures = create_v3_figures(report)
        try:
            axis = figures["shot_map"].axes[0]
            self.assertEqual(len(axis.collections), 1)
            self.assertEqual(len(axis.collections[0].get_facecolors()), 0)
            self.assertIn("xG não disponível", axis.get_legend().get_texts()[0].get_text())
        finally:
            for figure in figures.values():
                plt.close(figure)
