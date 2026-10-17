"""Regras V3: limiares, amostras e denominadores explícitos."""
from copy import deepcopy
from dataclasses import replace
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from managerai.coverage import CORE_METRICS
from managerai.report_schema import MetricEvidence
from managerai.v3_rules import hypotheses_v3


def core_report():
    def profile():
        return SimpleNamespace(metrics={k: MetricEvidence(k, 1, "unidade", 10, list(range(10)))
                                        for k in CORE_METRICS})
    return SimpleNamespace(team_profile=profile(), opponent_profile=profile())


def tactical_profile(name):
    def metric(value):
        return dict(value=value, sample_size=5, match_ids=[1, 2, 3, 4, 5], denominator=450)
    return dict(team_name=name, metrics={"final_third_pass_entries": metric(6),
                                       "final_third_carry_entries": metric(4),
                                       "shots_box_share": metric(60), "xg_box": metric(1.2)})


class V3RuleTests(unittest.TestCase):
    def setUp(self):
        self.report = core_report()
        self.own = tactical_profile("Equipe sintética")
        self.opponent = tactical_profile("Adversário sintético")

    def run_rules(self):
        return hypotheses_v3(self.report, self.own, self.opponent)

    def test_threshold_exactly_60_and_every_reference_grounded(self):
        hypotheses = self.run_rules()
        self.assertEqual({h["rule_id"] for h in hypotheses}, {"V3_ENTRADAS_PASSE", "V3_CHUTES_AREA"})
        for hypothesis in hypotheses:
            self.assertTrue(hypothesis["risks"])
            self.assertTrue(hypothesis["limitations"])
            self.assertTrue(hypothesis["preconditions"])
            for ref in hypothesis["evidence_metrics"]:
                _, side, _, key = ref.split(".")
                profile = self.own if side == "team_profile" else self.opponent
                self.assertGreaterEqual(profile["metrics"][key]["sample_size"], 5)
        self.assertIn("60,00%", hypotheses[0]["observation"])
        self.assertIn("90 min", hypotheses[0]["observation"])
        self.assertIn("por jogo", hypotheses[1]["observation"])

    def test_below_threshold_abstains(self):
        self.opponent["metrics"]["final_third_pass_entries"]["value"] = 5.999
        self.opponent["metrics"]["shots_box_share"]["value"] = 59.999
        self.assertEqual(self.run_rules(), [])

    def test_every_cited_metric_requires_five_games(self):
        for side, key in (("own", "final_third_pass_entries"), ("opponent", "final_third_pass_entries"),
                          ("opponent", "final_third_carry_entries"), ("own", "shots_box_share"),
                          ("opponent", "shots_box_share"), ("opponent", "xg_box")):
            with self.subTest(side=side, key=key):
                own, opponent = deepcopy(self.own), deepcopy(self.opponent)
                profile = own if side == "own" else opponent
                profile["metrics"][key]["sample_size"] = 4
                rules = hypotheses_v3(self.report, own, opponent)
                expected = "V3_ENTRADAS_PASSE" if "entries" in key else "V3_CHUTES_AREA"
                self.assertNotIn(expected, {h["rule_id"] for h in rules})

    def test_insufficient_central_metric_blocks_all_rules(self):
        self.report.team_profile.metrics["xg_for"] = replace(self.report.team_profile.metrics["xg_for"], sample_size=1)
        self.assertEqual(self.run_rules(), [])

    def test_share_requires_same_match_ids_and_exposure(self):
        carry = self.opponent["metrics"]["final_third_carry_entries"]
        carry["match_ids"] = [2, 3, 4, 5, 6]
        self.assertNotIn("V3_ENTRADAS_PASSE", {h["rule_id"] for h in self.run_rules()})
        carry["match_ids"] = [1, 2, 3, 4, 5]
        carry["denominator"] = 451
        self.assertNotIn("V3_ENTRADAS_PASSE", {h["rule_id"] for h in self.run_rules()})

    def test_null_values_and_missing_metrics_do_not_emit(self):
        self.opponent["metrics"]["xg_box"]["value"] = None
        del self.opponent["metrics"]["final_third_carry_entries"]
        self.assertEqual(self.run_rules(), [])

    def test_missing_or_invalid_denominator_abstains(self):
        for denominator in (None, 0, -1, float("nan")):
            with self.subTest(denominator=denominator):
                own, opponent = deepcopy(self.own), deepcopy(self.opponent)
                for profile in (own, opponent):
                    for metric in profile["metrics"].values():
                        metric["denominator"] = denominator
                self.assertEqual(hypotheses_v3(self.report, own, opponent), [])

    def test_zero_entry_total_cannot_form_share(self):
        for key in ("final_third_pass_entries", "final_third_carry_entries"):
            self.opponent["metrics"][key]["value"] = 0
        self.assertNotIn("V3_ENTRADAS_PASSE", {h["rule_id"] for h in self.run_rules()})

    def test_nonfinite_values_cannot_support_hypotheses(self):
        for value in (float("nan"), float("inf"), True):
            with self.subTest(value=value):
                opponent = deepcopy(self.opponent)
                opponent["metrics"]["shots_box_share"]["value"] = value
                opponent["metrics"]["final_third_pass_entries"]["value"] = value
                self.assertEqual(hypotheses_v3(self.report, self.own, opponent), [])

    def test_configured_minimum_is_enforced_and_validated(self):
        self.assertEqual(hypotheses_v3(self.report, self.own, self.opponent, minimum_matches=6), [])
        for minimum in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                hypotheses_v3(self.report, self.own, self.opponent, minimum_matches=minimum)


@unittest.skipUnless(os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração local opcional")
class V3RealRuleTests(unittest.TestCase):
    def test_city_generates_grounded_new_hypotheses(self):
        from managerai.pipeline import analyze
        from managerai.report_schema import AnalysisRequest
        from managerai.v3_pipeline import extend_report
        root = Path(__file__).resolve().parents[1] / "open-data/data"
        report = extend_report(root, analyze(root, AnalysisRequest(2, 27, 36, 1, target_match_id=3754314)))
        self.assertGreaterEqual(len(report.tactical_v3["hypotheses"]), 1)
        for h in report.tactical_v3["hypotheses"]:
            for ref in h["evidence_metrics"]:
                _, side, _, key = ref.split(".")
                metric = report.tactical_v3[side]["metrics"][key]
                self.assertGreaterEqual(metric["sample_size"], 5)
                self.assertIsNotNone(metric["value"])
                self.assertGreater(metric["denominator"], 0)


if __name__ == "__main__":
    unittest.main()
