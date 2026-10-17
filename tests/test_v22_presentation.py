"""Política V2.2 de apresentação, com perfis sintéticos explicitamente controlados."""
from copy import deepcopy
from dataclasses import replace

from managerai.pipeline import analyze
from managerai.presentation.coach_report import (
    build_coach_report, core_evidence_warnings, insufficient_core_evidence,
    period, render_coach_markdown,
)
from managerai.presentation.terminology import CORE_METRICS, TERMS, count, measure
from test_managerai import LocalFixture


class V22PresentationTests(LocalFixture):
    def controlled_report(self, own_count=10, opponent_count=10):
        """Perfis de apresentação; não são medições de clubes reais."""
        report = analyze(self.root, self.request)
        for profile, n in ((report.team_profile, own_count), (report.opponent_profile, opponent_count)):
            profile.match_ids = list(range(1, n + 1))
            profile.period_start = "2020-01-01" if n else None
            profile.period_end = f"2020-01-{n:02d}" if n else None
            profile.sample_status = "limitada" if n >= 5 else "insuficiente"
            for key, metric in list(profile.metrics.items()):
                value = metric.value
                if key in CORE_METRICS and value is None and n:
                    value = 50.0  # Test-only calculable pass accuracy for the synthetic opponent.
                profile.metrics[key] = replace(
                    metric, value=value if n else None, sample_size=n,
                    match_ids=list(profile.match_ids), per_match=[
                        {"match_id": i, "match_date": f"2020-01-{i:02d}", "value": value}
                        for i in profile.match_ids],
                )
        return report

    def test_one_versus_ten_keeps_values_but_suppresses_comparative_conclusions(self):
        report = self.controlled_report(1, 10)
        before = report.to_json()
        view = build_coach_report(report)
        self.assertTrue(insufficient_core_evidence(report))
        self.assertEqual(view.summary, [])
        self.assertEqual(view.hypotheses, [])
        self.assertEqual(len(view.comparison), 8)
        self.assertIn("1 jogo", view.warnings[0])
        self.assertNotIn("1 jogos", render_coach_markdown(report))
        self.assertEqual(before, report.to_json())
        text = render_coach_markdown(report)
        self.assertLess(text.index("Amostra insuficiente"), text.index("Visão geral"))
        table_heading = text.index("## Indicadores observados")
        self.assertIn("Amostra insuficiente", text[table_heading:text.index("| Indicador")])
        self.assertIn("não interpretar diferenças como superioridade", text)

    def test_ten_versus_ten_preserves_hypotheses_and_summary(self):
        report = self.controlled_report()
        before = deepcopy(report.to_dict())
        view = build_coach_report(report)
        self.assertFalse(insufficient_core_evidence(report))
        self.assertEqual(len(view.summary), 5)
        self.assertEqual(len(view.hypotheses), len(report.tactical_hypotheses))
        self.assertEqual(report.to_dict(), before)
        self.assertTrue(view.hypotheses)
        for source, presented in zip(report.tactical_hypotheses, view.hypotheses):
            self.assertEqual(source.evidence_metrics, presented.evidence_paths)

    def test_each_core_metric_must_have_five_calculable_games(self):
        for key in CORE_METRICS:
            with self.subTest(metric=key):
                report = self.controlled_report()
                metric = report.opponent_profile.metrics[key]
                report.opponent_profile.metrics[key] = replace(metric, sample_size=4)
                self.assertTrue(insufficient_core_evidence(report))
                self.assertEqual(build_coach_report(report).summary, [])
                self.assertEqual(build_coach_report(report).hypotheses, [])
                self.assertIn("4 jogos", core_evidence_warnings(report)[0])
        report = self.controlled_report(5, 5)
        self.assertFalse(insufficient_core_evidence(report))

    def test_missing_core_value_is_insufficient_even_with_many_profile_games(self):
        report = self.controlled_report()
        metric = report.opponent_profile.metrics["xg_for"]
        report.opponent_profile.metrics["xg_for"] = replace(metric, value=None)
        self.assertTrue(insufficient_core_evidence(report))
        self.assertIn("0 jogos", core_evidence_warnings(report)[0])

    def test_zero_history_is_unavailable_not_numeric_zero(self):
        report = self.controlled_report(0, 0)
        view = build_coach_report(report)
        for row in view.comparison:
            self.assertEqual(row[report.team_profile.team_name], "indisponível")
            self.assertEqual(row["Período (meu time)"], "sem informação calculável")
        self.assertEqual(view.summary, [])
        self.assertEqual(view.hypotheses, [])

    def test_table_contains_metric_specific_sample_and_dates(self):
        report = self.controlled_report()
        metric = report.team_profile.metrics["box_entries"]
        report.team_profile.metrics["box_entries"] = replace(
            metric, sample_size=1, per_match=[{"match_date": "2020-01-03"}])
        row = next(r for r in build_coach_report(report).comparison if r["Indicador"] == TERMS["box_entries"].title)
        self.assertEqual(row["Jogos com informação (meu time / adversário)"], "1 / 10")
        self.assertEqual(row["Período (meu time)"], "03/01/2020 a 03/01/2020")
        self.assertEqual(row["Período (adversário)"], "01/01/2020 a 10/01/2020")

    def test_portuguese_terms_percent_and_singular(self):
        self.assertEqual(count(1, "jogo"), "1 jogo")
        self.assertEqual(count(0, "partida"), "0 partidas")
        self.assertEqual(count(2, "partida"), "2 partidas")
        self.assertEqual(measure(83.79, "%"), "83,79%")
        self.assertEqual(measure(None, "%"), "indisponível")
        self.assertEqual(TERMS["xg_for"].title, "Gols esperados a favor")
        self.assertEqual(TERMS["xg_against"].title, "Gols esperados concedidos")
        self.assertEqual(TERMS["pressures"].title, "Tentativas de pressão registradas")
        report = self.controlled_report(1, 10)
        self.assertIn("1 jogo,", period(report.team_profile))
        report = self.controlled_report()
        text = render_coach_markdown(report)
        self.assertNotRegex(text, r"\d\s+%")
        self.assertIn("xG estima a qualidade das finalizações", text)
        self.assertIn("Não alteram o cálculo", text)
        for code in ("R01_PROGRESSAO", "xg_against", "Pressure", "team_profile.metrics"):
            self.assertNotIn(code, text)
