"""Robustez em fixtures sintéticas; não constitui evidência esportiva."""
from dataclasses import asdict, replace
from datetime import date, timedelta
from importlib.util import find_spec
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from managerai.experiments.dataset import SupervisedDataset, build_pre_match_features
from managerai.experiments.robustness import (
    MonthlyWindow, evaluate_robustness, evaluate_window, fixed_windows,
    project_features, select_window, run_robustness,
)
from test_experimental_models import example


HAS_NUMPY = find_spec("numpy") is not None
MODEL_IDS = {
    "historical_mean", "combined_means", "training_mean", "linear", "ridge",
    "linear_home_only", "ridge_home_only", "linear_away_only", "ridge_away_only",
}


def rows():
    result = []
    for start, count in ((date(2015, 9, 1), 60), (date(2015, 11, 1), 20),
                         (date(2015, 12, 1), 20)):
        for offset in range(count):
            result.append(example(len(result) + 1, (start + timedelta(days=offset)).isoformat()))
    return tuple(result)


def first_window():
    return fixed_windows()[0]


def alter_feature(row, component, amount):
    features = row.features
    if component == 0:
        home = tuple(replace(h, shots_for=h.shots_for + amount) for h in features.home_history)
        away = features.away_history
    else:
        home = features.home_history
        away = tuple(replace(h, shots_against=h.shots_against + amount) for h in features.away_history)
    return replace(row, features=build_pre_match_features(features.fixture, home, away))


class RobustnessWindowTests(unittest.TestCase):
    def test_protocol_has_fixed_months_and_two_schemes(self):
        windows = fixed_windows()
        self.assertEqual(len(windows), 14)
        self.assertEqual(len({w.window_id for w in windows}), 14)
        self.assertEqual([w.evaluation_start for w in windows[:7]],
                         ["2015-11-01", "2015-12-01", "2016-01-01", "2016-02-01",
                          "2016-03-01", "2016-04-01", "2016-05-01"])
        self.assertTrue(all(w.minimum_training == 50 and w.train_start is None for w in windows[:7]))
        self.assertTrue(all(w.minimum_training == 30 for w in windows[7:]))
        self.assertTrue(all(w.minimum_evaluation == 20 for w in windows))
        for expanding, rolling in zip(windows[:7], windows[7:]):
            self.assertEqual(expanding.evaluation_start, rolling.evaluation_start)
            self.assertEqual(expanding.evaluation_end, rolling.evaluation_end)
            self.assertEqual((date.fromisoformat(rolling.evaluation_start)
                              - date.fromisoformat(rolling.train_start)).days, 90)
        self.assertEqual(windows[-1].evaluation_end, "2016-05-31")

    def test_days_stay_whole_and_order_is_deterministic(self):
        candidates = (example(6, "2015-12-01"), example(5, "2015-11-30"),
                      example(4, "2015-11-01"), example(3, "2015-11-01"),
                      example(2, "2015-10-31"), example(1, "2015-10-31"))
        train, evaluation = select_window(candidates, first_window())
        self.assertEqual([r.features.fixture.match_id for r in train], [1, 2])
        self.assertEqual([r.features.fixture.match_id for r in evaluation], [3, 4, 5])
        self.assertEqual((train, evaluation), select_window(tuple(reversed(candidates)), first_window()))
        self.assertLess(max(r.features.fixture.match_date for r in train),
                        min(r.features.fixture.match_date for r in evaluation))

    def test_rolling_lower_boundary_is_inclusive_and_older_rows_excluded(self):
        window = fixed_windows()[7]
        # Keep synthetic history strictly earlier than these dates.
        custom = replace(window, train_start="2015-09-10", evaluation_start="2015-12-09",
                         evaluation_end="2015-12-31")
        candidates = (example(1, "2015-09-09"), example(2, "2015-09-10"),
                      example(3, "2015-12-08"), example(4, "2015-12-09"))
        train, evaluation = select_window(candidates, custom)
        self.assertEqual([r.features.fixture.match_id for r in train], [2, 3])
        self.assertEqual([r.features.fixture.match_id for r in evaluation], [4])

    def test_duplicate_match_id_is_rejected_even_outside_evaluation(self):
        row = example(1, "2015-09-10")
        with self.assertRaises(ValueError):
            select_window((row, row), first_window())

    def test_window_is_immutable(self):
        with self.assertRaises(AttributeError):
            first_window().minimum_training = 1

    def test_invalid_window_bounds_schemes_and_minimums_are_rejected(self):
        for changes in ({"evaluation_end": "2015-10-31"}, {"scheme": "unknown"},
                        {"minimum_training": 2}, {"minimum_training": True},
                        {"minimum_evaluation": 0}, {"evaluation_start": "2015-11-1"},
                        {"train_start": "2015-11-01"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(first_window(), **changes)
        with self.assertRaises(ValueError):
            replace(fixed_windows()[7], train_start="2015-10-01")

    def test_feature_projection_removes_only_declared_group(self):
        self.assertEqual(project_features((3., 7.), "full"), (3., 7.))
        self.assertEqual(project_features((3., 7.), "home_only"), (3., 0.))
        self.assertEqual(project_features((3., 7.), "away_only"), (0., 7.))

    def test_feature_projection_rejects_unknown_or_invalid_input(self):
        for values, group in (((1, 2), "unknown"), ((1,), "full"),
                              ((1, 2, 3), "home_only"), ((1, math.nan), "away_only"),
                              ((math.inf, 2), "full"), ((True, 2), "full")):
            with self.subTest(values=values, group=group), self.assertRaises(ValueError):
                project_features(values, group)

    def test_small_training_and_evaluation_block_without_fabricated_predictions(self):
        for candidates in ((), rows()[:3], rows()[:65]):
            with self.subTest(n=len(candidates)):
                result = evaluate_window(candidates, first_window())
                self.assertEqual(result["status"], "blocked")
                self.assertIn("reason", result)
                self.assertNotIn("predictions", result)
                self.assertNotIn("fitted_models", result)


class RobustnessOutputGuardsTests(unittest.TestCase):
    def check_rejected_before_build(self, root, reference, output):
        with patch("managerai.experiments.robustness.build_dataset") as build:
            with self.assertRaises(ValueError):
                run_robustness(root, reference, output)
            build.assert_not_called()

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sentinel = root / "keep.txt"
            sentinel.write_text("preservar")
            self.check_rejected_before_build(root / "data", root / "absent.json", root)
            self.assertEqual(sentinel.read_text(), "preservar")

    def test_raw_and_reference_subdirectories_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for output in (root / "data" / "new", root / "ab" / "new"):
                self.check_rejected_before_build(root / "data", root / "ab" / "run.json", output)
                self.assertFalse(output.exists())

    def test_project_source_and_eda_destinations_rejected(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ("src/forbidden_new", "outputs/statsbomb_eda_20261002_exec6/forbidden_new"):
                output = project / relative
                self.check_rejected_before_build(root / "data", root / "ab/run.json", output)
                self.assertFalse(output.exists())

    def test_changed_reference_hash_blocks_without_new_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = root / "ab/run.json"
            reference.parent.mkdir()
            reference.write_text("{}")
            self.check_rejected_before_build(root / "data", reference, root / "new")
            self.assertEqual(reference.read_text(), "{}")
            self.assertFalse((root / "new").exists())


@unittest.skipUnless(HAS_NUMPY, "Robustez quantitativa exige NumPy opcional.")
class RobustnessFitTests(unittest.TestCase):
    def test_all_models_use_exactly_same_unique_matches(self):
        result = evaluate_window(rows(), first_window())
        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(len(result["predictions"]), 20)
        self.assertEqual(len({r["match_id"] for r in result["predictions"]}), 20)
        for row in result["predictions"]:
            self.assertEqual(set(row["predictions"]), MODEL_IDS)
            self.assertTrue(all(math.isfinite(p) and p >= 0 for p in row["predictions"].values()))
            self.assertEqual(len(row["feature_fingerprint"]), 64)

    def test_training_mean_baseline_is_manual_mean_of_training_labels(self):
        candidates = rows()
        result = evaluate_window(candidates, first_window())
        expected = sum(r.label.home_shots for r in candidates[:60]) / 60
        self.assertEqual(result["constant_training_mean"], expected)
        self.assertTrue(all(r["predictions"]["training_mean"] == expected for r in result["predictions"]))

    def test_scaler_uses_only_training_values_with_population_variance(self):
        candidates = rows()
        result = evaluate_window(candidates, first_window())
        model = result["fitted_models"]["linear"]
        for component in (0, 1):
            values = [r.features.values[component] for r in candidates[:60]]
            mean = sum(values) / len(values)
            scale = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
            self.assertAlmostEqual(model["mean"][component], mean)
            self.assertAlmostEqual(model["scale"][component], scale)

    def test_holdout_and_future_labels_cannot_change_models_scaler_or_predictions(self):
        original = rows()
        changed = tuple(replace(r, label=replace(r.label, home_shots=r.label.home_shots + 999))
                        if r.features.fixture.match_date >= "2015-11-01" else r for r in original)
        before = evaluate_window(original, first_window())
        after = evaluate_window(changed, first_window())
        self.assertEqual(before["fitted_models"], after["fitted_models"])
        self.assertEqual(before["constant_training_mean"], after["constant_training_mean"])
        self.assertEqual([r["predictions"] for r in before["predictions"]],
                         [r["predictions"] for r in after["predictions"]])
        self.assertNotEqual(before["comparison"], after["comparison"])
        for model in before["fitted_models"].values():
            self.assertEqual(tuple(model["training_match_ids"]), tuple(range(1, 61)))
            self.assertLess(model["train_end"], "2015-11-01")

    def test_future_features_do_not_change_earlier_window(self):
        original = rows()
        changed = tuple(alter_feature(r, 0, 500) if r.features.fixture.match_date >= "2015-12-01"
                        else r for r in original)
        self.assertEqual(evaluate_window(original, first_window()), evaluate_window(changed, first_window()))

    def test_ablated_feature_does_not_change_fit_or_prediction(self):
        original = rows()
        baseline = evaluate_window(original, first_window())
        for dropped, suffix in ((1, "home_only"), (0, "away_only")):
            changed = tuple(alter_feature(r, dropped, 100) for r in original)
            result = evaluate_window(changed, first_window())
            for family in ("linear", "ridge"):
                model_id = f"{family}_{suffix}"
                self.assertEqual(baseline["fitted_models"][model_id], result["fitted_models"][model_id])
                self.assertEqual([r["predictions"][model_id] for r in baseline["predictions"]],
                                 [r["predictions"][model_id] for r in result["predictions"]])

    def test_input_unchanged_and_repeated_evaluation_identical(self):
        candidates = rows()
        snapshot = [asdict(r) for r in candidates]
        before, after = evaluate_window(candidates, first_window()), evaluate_window(candidates, first_window())
        self.assertEqual(before, after)
        self.assertEqual(snapshot, [asdict(r) for r in candidates])

    def test_rolling_model_fit_contains_only_in_window_training_ids(self):
        window = fixed_windows()[8]
        train, evaluation = select_window(rows(), window)
        result = evaluate_window(rows(), window)
        self.assertEqual(result["status"], "evaluated")
        expected = tuple(r.features.fixture.match_id for r in train)
        eval_ids = {r.features.fixture.match_id for r in evaluation}
        for model in result["fitted_models"].values():
            self.assertEqual(tuple(model["training_match_ids"]), expected)
            self.assertFalse(set(expected) & eval_ids)

    def test_dataset_level_reproduction_and_blocked_months(self):
        data = SupervisedDataset(rows(), (), (), (), {})
        first, second = evaluate_robustness(data), evaluate_robustness(data)
        self.assertEqual(first, second)
        self.assertEqual(len(first["schemes"]), 2)
        for scheme in first["schemes"].values():
            self.assertEqual(scheme["status"], "evaluated")
            self.assertTrue(any(w["status"] == "blocked" for w in scheme["windows"]))
            self.assertTrue(any(w["status"] == "evaluated" for w in scheme["windows"]))


if __name__ == "__main__":
    unittest.main()
