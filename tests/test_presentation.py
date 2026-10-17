"""Regressão da linguagem e fidelidade dos números, sem Streamlit."""
from dataclasses import replace
import unittest

from managerai.feature_engineering import METRICS
from managerai.pipeline import analyze
from managerai.presentation.coach_report import build_coach_report, render_coach_markdown
from managerai.presentation.terminology import TERMS, number
from managerai.report_renderer import render_markdown, render_technical_markdown
from test_managerai import LocalFixture


class TerminologyTests(unittest.TestCase):
    def test_every_metric_has_title_unit_and_caveat(self):
        self.assertEqual(set(METRICS), set(TERMS))
        self.assertTrue(all(t.title and t.unit and t.explanation for t in TERMS.values()))
        self.assertIn("Não é quantidade de chances", TERMS["xg_for"].explanation)
        self.assertIn("Não significa passes sem pressão", TERMS["pass_accuracy_unmarked_pressure"].explanation)
        for key in ("lane_low_y", "lane_high_y"):
            self.assertIn("orientação não foi validada", TERMS[key].explanation)

    def test_brazilian_format_and_missing_value(self):
        self.assertEqual(number(1234.567), "1.234,57")
        self.assertEqual(number(0), "0,00")
        self.assertEqual(number(None), "indisponível")


class PresentationTests(LocalFixture):
    def test_presentation_does_not_change_report(self):
        report = analyze(self.root, self.request)
        before = report.to_json()
        view = build_coach_report(report)
        render_markdown(report)
        self.assertEqual(before, report.to_json())
        self.assertEqual(len(view.comparison), 8)
        # Missing central passing evidence now suppresses comparative conclusions.
        self.assertEqual(len(view.summary), 0)

    def test_internal_codes_only_in_technical_appendix(self):
        text = render_markdown(analyze(self.root, self.request))
        friendly, appendix = text.split("## Apêndice técnico", 1)
        for code in ("R01_PROGRESSAO", "Pressure", "eventos/90", "evidence_metrics", "team_profile.metrics", "lane_low_y"):
            self.assertNotIn(code, friendly)
        self.assertIn("R02_PRESSAO_ALTA", appendix)
        self.assertIn("team_profile.metrics", appendix)

    def test_hypotheses_only_present_numbers_from_referenced_metrics(self):
        report = analyze(self.root, self.request)
        report.opponent_profile.metrics["pass_accuracy"] = replace(report.team_profile.metrics["pass_accuracy"])
        report.opponent_profile.metrics["pressure_high_share"] = replace(report.opponent_profile.metrics["pressure_high_share"], value=43.217)
        view = build_coach_report(report)
        for original, presented in zip(report.tactical_hypotheses, view.hypotheses):
            self.assertEqual(presented.evidence_paths, original.evidence_metrics)
            self.assertTrue(presented.observed and presented.condition and presented.risks and presented.limitations)
        self.assertIn("43,22", view.hypotheses[0].observed)
        self.assertNotIn("43,22", view.hypotheses[-1].observed)

    def test_xg_context_and_pressure_definitions_are_explicit(self):
        text = render_coach_markdown(analyze(self.root, replace(self.request, notes="Plano manual")))
        self.assertIn("Gols esperados (xG)", text)
        self.assertIn("Não são uma contagem de chances", text)
        self.assertIn("Não alteram o cálculo", text)
        self.assertIn("não informa quantas pressões deram certo", text)
        self.assertIn("> Plano manual", text)

    def test_insufficient_history_has_no_invented_findings_or_hypotheses(self):
        empty = analyze(self.root, replace(self.request, target_match_id=1))
        view = build_coach_report(empty)
        self.assertEqual(view.summary, [])
        self.assertEqual(view.hypotheses, [])
        self.assertTrue(all(row[empty.team_profile.team_name] == "indisponível" for row in view.comparison))
        small = analyze(self.root, replace(self.request, recent_matches_window=2))
        view = build_coach_report(small)
        self.assertEqual(view.hypotheses, [])
        self.assertIn("Histórico insuficiente", view.warnings[0])

    def test_unmarked_pressure_does_not_replace_explicit_false(self):
        report = analyze(self.root, self.request)
        self.assertIsNone(report.team_profile.metrics["pass_accuracy_explicit_no_pressure"].value)
        technical = render_technical_markdown(report)
        self.assertIn("não disponível", technical)
        self.assertIn("Passes certos sem informação de pressão", TERMS["pass_accuracy_unmarked_pressure"].title)
