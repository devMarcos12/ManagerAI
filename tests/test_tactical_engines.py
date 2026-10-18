"""Contratos V4.1 sobre fixtures sintéticas; não simula modelo especializado."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from managerai.pipeline import analyze
from managerai.report_schema import AnalysisReport, AnalysisRequest, MetricEvidence, TacticalHypothesis, TeamProfile
from managerai.v3_schema import AnalysisReportV3
from managerai.tactical_engine_schema import TacticalEngineOutput, fingerprint, thaw
from managerai.tactical_engines import (
    DeterministicEngine, EngineUnavailableError, build_engine_input, compare_engines,
)
from test_managerai import LocalFixture


class TacticalEngineTests(LocalFixture):
    def setUp(self):
        super().setUp()
        # A fixture compartilhada não tem passes do adversário. Este cenário
        # sintético explícito acrescenta um passe para testar suficiência central.
        for mid in range(1, 10):
            events = json.loads((self.root / f"events/{mid}.json").read_text())
            extra = deepcopy(events[0])
            extra.update(id=f"synthetic-opponent-pass-{mid}", team={"id": 2}, player={"id": 201})
            events.insert(1, extra)
            for index, event in enumerate(events, 1):
                event["index"] = index
            self.write(f"events/{mid}.json", events)

    def report(self, *, v3=False):
        return analyze(self.root, self.request, include_v3=v3)

    def test_baseline_reuses_legacy_hypotheses_without_reading_or_recalculation(self):
        report = self.report()
        original = report.to_json()
        with patch("managerai.data_loader.LocalData.read", side_effect=AssertionError("não reler")), \
             patch("managerai.recommendation_engine.hypotheses", side_effect=AssertionError("não recalcular")):
            result, = compare_engines(report)
        self.assertTrue(result.sufficient)
        self.assertEqual(result.status, "hypotheses")
        self.assertEqual([h.hypothesis_id for h in result.hypotheses], [h.rule_id for h in report.tactical_hypotheses])
        for source, mapped in zip(report.tactical_hypotheses, result.hypotheses):
            self.assertEqual(mapped.action, source.recommendation)
            self.assertEqual(mapped.condition, source.condition)
            self.assertEqual(mapped.evidence_metrics, tuple(source.evidence_metrics))
            self.assertEqual(mapped.risks, tuple(source.risks))
            self.assertEqual(mapped.limitations, tuple(source.limitations))
        self.assertEqual(report.to_json(), original)
        self.assertEqual(report.schema_version, "1.0.0")

    def test_v3_reuses_both_layers_and_keeps_all_legacy_values(self):
        legacy = self.report()
        report = self.report(v3=True)
        before = report.to_json()
        with patch("managerai.v3_rules.hypotheses_v3", side_effect=AssertionError("não recalcular")):
            result, = compare_engines(report)
        self.assertEqual([h.hypothesis_id for h in result.hypotheses if h.origin == "v3"],
                         [h["rule_id"] for h in report.tactical_v3["hypotheses"]])
        self.assertTrue(any(h.origin == "v3" for h in result.hypotheses))
        values = report.to_dict()
        values.pop("tactical_v3")
        values["schema_version"] = "1.0.0"
        self.assertEqual(values, legacy.to_dict())
        self.assertEqual(report.to_json(), before)
        self.assertEqual(result.provenance["v3_formula_version"], "3.0.0")

    def test_input_is_immutable_detached_and_has_no_baseline_labels(self):
        report = self.report(v3=True)
        inputs = build_engine_input(report)
        digest = inputs.input_fingerprint
        with self.assertRaises(TypeError):
            inputs.profiles["team_profile"]["metrics"]["xg_for"]["value"] = 99
        detached = inputs.to_dict()
        detached["profiles"]["team_profile"]["match_ids"].clear()
        report.team_profile.metrics.clear()
        self.assertEqual(inputs.input_fingerprint, digest)
        encoded = json.dumps(inputs.to_dict(), allow_nan=False)
        for forbidden in ("tactical_hypotheses", '"hypotheses"', '"shots"', '"historical"', '"sequences"'):
            self.assertNotIn(forbidden, encoded)

    def test_reproducible_output_and_engine_bound_to_input(self):
        report = self.report()
        first, = compare_engines(report)
        second, = compare_engines(report)
        self.assertEqual(first.to_dict(), second.to_dict())
        engine = DeterministicEngine(report)
        other = build_engine_input(analyze(self.root, replace(self.request, notes="outro cenário")))
        with self.assertRaises(ValueError):
            engine.analyze(other)

    def test_zero_one_and_small_samples_abstain_without_fabricated_metrics(self):
        for target in (1, 2, 4):
            with self.subTest(target=target):
                report = analyze(self.root, replace(self.request, target_match_id=target))
                output, = compare_engines(report)
                self.assertFalse(output.sufficient)
                self.assertEqual(output.status, "abstained")
                self.assertEqual(output.hypotheses, ())
                if target == 1:
                    self.assertIsNone(build_engine_input(report).evidence("team_profile.metrics.xg_for")["value"])

    def test_core_abstention_does_not_remove_raw_legacy_hypotheses(self):
        for mid in range(1, 8):
            events = json.loads((self.root / f"events/{mid}.json").read_text())
            for event in events:
                if event["type"]["name"] == "Shot":
                    event["shot"].pop("statsbomb_xg")
            self.write(f"events/{mid}.json", events)
        report = self.report()
        self.assertTrue(report.tactical_hypotheses)
        before = report.to_json()
        output, = compare_engines(report)
        self.assertEqual(output.status, "abstained")
        self.assertFalse(output.sufficient)
        self.assertEqual(report.to_json(), before)

    def test_sufficient_input_can_have_no_matching_hypotheses(self):
        report = self.report()
        report.tactical_hypotheses.clear()
        output, = compare_engines(report)
        self.assertTrue(output.sufficient)
        self.assertEqual(output.status, "no_hypotheses")

    def test_temporal_selection_and_same_day_remain_excluded(self):
        self.matches[6]["match_date"] = "2020-01-08"
        self.write("matches/2/27.json", self.matches)
        report = analyze(self.root, replace(self.request, recent_matches_window=3))
        inputs = build_engine_input(report)
        self.assertEqual(inputs.profiles["team_profile"]["match_ids"], (4, 5, 6))
        for target in (7, 8, 9):
            self.assertNotIn(f"events/{target}.json", [s["path"] for s in inputs.provenance["sources"]])

    def test_rejects_target_future_dates_inconsistent_sample_and_nonfinite_values(self):
        inputs = build_engine_input(self.report())
        def invalid_profiles(mutate):
            profiles = thaw(inputs.profiles)
            mutate(profiles["team_profile"])
            with self.assertRaises(ValueError):
                replace(inputs, profiles=profiles)
        invalid_profiles(lambda p: p["match_ids"].append(8))
        invalid_profiles(lambda p: p.update(period_end="2020-01-08"))
        invalid_profiles(lambda p: p["metrics"]["xg_for"]["per_match"][0].update(match_date="2020-01-09"))
        invalid_profiles(lambda p: p["metrics"]["xg_for"].update(sample_size=99))
        invalid_profiles(lambda p: p["metrics"]["xg_for"].update(value=float("nan")))
        invalid_profiles(lambda p: p["metrics"]["xg_for"].update(value=float("inf")))
        invalid_profiles(lambda p: p["metrics"]["xg_for"].update(denominator="inválido"))
        invalid_profiles(lambda p: p.pop("sample_status"))
        with self.assertRaises(ValueError):
            replace(inputs, profiles={})
        with self.assertRaises(ValueError):
            replace(inputs, data_gaps="não é sequência de textos")

    def test_rejects_inconsistent_metadata_and_provenance(self):
        report = self.report()
        inputs = build_engine_input(report)
        for mutation in (lambda p: p.update(data_fingerprint="0" * 64),
                         lambda p: p["sources"][0].update(path="../fora.json"),
                         lambda p: p["sources"][0].update(path="."),
                         lambda p: p.update(report_schema_version="4.1.0")):
            provenance = thaw(inputs.provenance)
            mutation(provenance)
            with self.assertRaises(ValueError):
                replace(inputs, provenance=provenance)
        report.metadata["target_match_id"] = 9
        with self.assertRaises(ValueError):
            build_engine_input(report)

    def test_rejects_v3_source_mismatch(self):
        report = self.report(v3=True)
        report.tactical_v3["methodology"]["data_fingerprint"] = "0" * 64
        with self.assertRaises(ValueError):
            build_engine_input(report)

    def test_rejects_target_source_even_with_recomputed_fingerprint(self):
        inputs = build_engine_input(self.report())
        for path in ("events/8.json", "events/./8.json", "events//8.json", "events/9.json"):
            provenance = thaw(inputs.provenance)
            provenance["sources"].append({"path": path, "sha256": "0" * 64})
            provenance["data_fingerprint"] = fingerprint({x["path"]: x["sha256"] for x in provenance["sources"]})
            with self.assertRaises(ValueError):
                replace(inputs, provenance=provenance)

    def test_unknown_model_does_not_fall_back_or_invoke_registered_engines(self):
        report = self.report()
        with patch.object(DeterministicEngine, "analyze", side_effect=AssertionError("não executar")):
            with self.assertRaises(EngineUnavailableError):
                compare_engines(report, engine_ids=("deterministic", "specialized"))
        for selection in ((), ("deterministic", "deterministic")):
            with self.assertRaises(ValueError):
                compare_engines(report, engine_ids=selection)

    def test_explicit_protocol_engine_compares_same_snapshot_without_ranking(self):
        # Test double de contrato, sem pretender ser modelo/recomendação de IA.
        seen = []
        class AbstainingEngine:
            engine_id = "test-abstention"
            engine_version = "test-only"
            def analyze(self, inputs):
                seen.append(inputs.input_fingerprint)
                return TacticalEngineOutput(self.engine_id, self.engine_version, inputs.input_fingerprint,
                    inputs.provenance, inputs.sufficiency.sufficient, "abstained", (), ("Somente teste de contrato.",))
        results = compare_engines(self.report(), engine_ids=("deterministic", "test-abstention"), engines=(AbstainingEngine(),))
        self.assertEqual(seen, [results[0].input_fingerprint])
        self.assertEqual(results[1].status, "abstained")

    def test_rejects_reserved_ids_wrong_output_identity_and_model_errors(self):
        report = self.report()
        with self.assertRaises(ValueError):
            compare_engines(report, engines=(DeterministicEngine(report),))
        class WrongEngine:
            engine_id = "test-wrong"
            engine_version = "test-only"
            def analyze(self, inputs):
                return DeterministicEngine(report).analyze(inputs)
        with self.assertRaises(ValueError):
            compare_engines(report, engine_ids=("test-wrong",), engines=(WrongEngine(),))
        with patch.object(WrongEngine, "analyze", side_effect=RuntimeError("modelo indisponível")):
            with self.assertRaises(RuntimeError):
                compare_engines(report, engine_ids=("test-wrong",), engines=(WrongEngine(),))

    def test_output_rejects_broken_references_insufficient_evidence_and_wrong_snapshot(self):
        report = self.report()
        inputs = build_engine_input(report)
        output, = compare_engines(report)
        hypothesis = output.hypotheses[0]
        for path in ("team_profile.metrics.missing", "provenance.sources", "team_profile.quality.xg_for"):
            invalid = replace(output, hypotheses=(replace(hypothesis, evidence_metrics=(path,)),))
            with self.assertRaises(ValueError):
                invalid.validate_for(inputs)
        with self.assertRaises(ValueError):
            replace(output, input_fingerprint="0" * 64).validate_for(inputs)
        with self.assertRaises(ValueError):
            replace(output, hypotheses=(hypothesis, hypothesis)).validate_for(inputs)
        with self.assertRaises(ValueError):
            replace(output, sufficient=False)
        with self.assertRaises(ValueError):
            replace(output, limitations="texto isolado")
        with self.assertRaises(ValueError):
            replace(hypothesis, evidence_metrics=())
        with self.assertRaises(ValueError):
            replace(hypothesis, risks="texto isolado")

    def test_adapter_snapshot_is_not_changed_by_later_report_mutation(self):
        report = self.report()
        engine = DeterministicEngine(report)
        before = engine.analyze(engine.inputs).to_dict()
        report.tactical_hypotheses[0].risks.append("alteração externa")
        report.data_gaps.append("alteração externa")
        self.assertEqual(before, engine.analyze(engine.inputs).to_dict())


class StoredReportCompatibilityTests(unittest.TestCase):
    def test_adapts_three_real_preserved_reports_without_recalculating(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("mvp_demo_city_arsenal", "v3_demo_city_arsenal", "v3_demo_real_madrid_barcelona"):
            with self.subTest(report=name):
                raw = (root / "outputs" / name / "report.json").read_bytes()
                payload = json.loads(raw)
                request = payload["request"]
                request["unavailable_player_ids"] = tuple(request["unavailable_player_ids"])
                payload["request"] = AnalysisRequest(**request)
                payload["tactical_hypotheses"] = [TacticalHypothesis(**h) for h in payload["tactical_hypotheses"]]
                for side in ("team_profile", "opponent_profile"):
                    values = payload[side]
                    values["metrics"] = {k: MetricEvidence(**v) for k, v in values["metrics"].items()}
                    payload[side] = TeamProfile(**values)
                report_type = AnalysisReportV3 if "tactical_v3" in payload else AnalysisReport
                report = report_type(**payload)
                self.assertEqual(report.to_json().encode(), raw)
                with patch("managerai.data_loader.LocalData.read", side_effect=AssertionError("sem releitura")):
                    output, = compare_engines(report)
                self.assertEqual(report.to_json().encode(), raw)
                self.assertEqual(output.sufficient, name != "v3_demo_real_madrid_barcelona")
                self.assertEqual(output.status, "abstained" if name.endswith("real_madrid_barcelona") else "hypotheses")
