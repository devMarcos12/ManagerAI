"""Testes sintéticos de regressões e avaliação; não medem desempenho esportivo."""
from dataclasses import asdict, replace
from datetime import date, timedelta
from importlib.util import find_spec
import math
import unittest

from managerai.experiments.dataset import (
    Example, Fixture, HistoricalEvidence, ObservedLabel, SupervisedDataset,
    build_pre_match_features,
)
from managerai.experiments.models import LinearModel, evaluate_predictions, fit_regressions
from managerai.experiments.runner import evaluate_dataset, split_examples


HAS_NUMPY = find_spec("numpy") is not None


def example(match_id, day, *, observed=None):
    """Constrói evidência anterior fixa; nenhum arquivo real é consultado."""
    home_value = 4 + match_id % 9
    away_value = 3 + (match_id * 3) % 11
    histories = []
    for role, team in enumerate((1, 2)):
        rows = []
        for offset in range(5):
            historical_id = 100000 + match_id * 20 + role * 5 + offset
            rows.append(HistoricalEvidence(
                historical_id, f"2015-08-{offset + 1:02d}", team,
                home_value if role == 0 else 5,
                away_value if role == 1 else 6,
                ((f"events/{historical_id}.json", "a" * 64),), (),
            ))
        histories.append(tuple(rows))
    features = build_pre_match_features(Fixture(match_id, day, 1, 2), *histories)
    label = ObservedLabel(match_id, home_value + away_value if observed is None else observed,
                          ((f"events/{match_id}.json", "b" * 64),))
    return Example(features, label)


def dataset():
    rows = []
    for start, count in ((date(2015, 9, 1), 30), (date(2016, 2, 7), 10),
                         (date(2016, 4, 9), 20)):
        for offset in range(count):
            rows.append(example(len(rows) + 1, (start + timedelta(days=offset)).isoformat()))
    return SupervisedDataset(tuple(rows), (), (), (), {})


class ExperimentalMetricTests(unittest.TestCase):
    def test_manual_errors_and_linear_quantiles(self):
        actual = evaluate_predictions([1, 3], [2, 1])
        self.assertEqual(actual["n"], 2)
        self.assertEqual(actual["mae"], 1.5)
        self.assertAlmostEqual(actual["rmse"], math.sqrt(2.5))
        self.assertEqual(actual["bias"], -.5)
        self.assertEqual(actual["distribution"]["signed"]["median"], -.5)
        self.assertAlmostEqual(actual["distribution"]["signed"]["p10"], -1.7)
        self.assertEqual(actual["distribution"]["absolute"]["p25"], 1.25)

    def test_single_observation_distribution(self):
        values = evaluate_predictions([5], [5])
        self.assertEqual(values["mae"], 0)
        self.assertTrue(all(v == 0 for v in values["distribution"]["signed"].values()))

    def test_invalid_metric_inputs_are_refused(self):
        for observed, predicted in (([], []), ([1], []), ([1], [-1]),
                                    ([-1], [0]), ([math.nan], [1]),
                                    ([1], [math.inf]), ([True], [1])):
            with self.subTest(observed=observed, predicted=predicted), self.assertRaises(ValueError):
                evaluate_predictions(observed, predicted)

    def test_nonnegative_predictions_and_immutable_model(self):
        model = LinearModel("linear", -5., (1., 1.), (0., 0.), (1., 1.),
                            (1, 2, 3), "2016-02-06", 0.)
        self.assertEqual(model.raw_predict((1, 1)), -3)
        self.assertEqual(model.predict((1, 1)), 0)
        with self.assertRaises(AttributeError):
            model.intercept = 0
        for values in ((1,), (1, math.nan), (math.inf, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                model.predict(values)


@unittest.skipUnless(HAS_NUMPY, "Regressões experimentais exigem NumPy opcional.")
class ExperimentalRegressionTests(unittest.TestCase):
    def fit(self, x=None, y=None, **kwargs):
        x = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 3)] if x is None else x
        y = [2 + 3 * a + 4 * b for a, b in x] if y is None else y
        args = {"match_ids": list(range(1, len(x) + 1)),
                "match_dates": ["2016-01-01"] * len(x)}
        args.update(kwargs)
        return fit_regressions(x, y, **args)

    def test_known_ols_solution(self):
        linear, ridge = self.fit()
        self.assertEqual((linear.model_id, ridge.model_id), ("linear", "ridge"))
        self.assertAlmostEqual(linear.raw_predict((3, 4)), 27., places=10)
        self.assertEqual(linear.ridge_alpha, 0)
        self.assertEqual(ridge.ridge_alpha, 1)

    def test_ridge_fixed_regularization_and_unpenalized_intercept(self):
        linear, ridge = self.fit(x=[(0, 5), (1, 5), (2, 5)], y=[1, 3, 5])
        self.assertEqual(ridge.intercept, 3)
        self.assertAlmostEqual(ridge.raw_predict((0, 5)), 1.5)
        self.assertAlmostEqual(ridge.raw_predict((2, 5)), 4.5)
        self.assertLess(abs(ridge.coefficients[0]), abs(linear.coefficients[0]))

    def test_training_scaler_population_and_constant(self):
        linear, ridge = self.fit(x=[(0, 7), (1, 7), (2, 7)], y=[1, 2, 3])
        self.assertEqual(linear.mean, (1., 7.))
        self.assertAlmostEqual(linear.scale[0], math.sqrt(2 / 3))
        self.assertEqual(linear.scale[1], 1.)
        self.assertEqual(linear.mean, ridge.mean)
        self.assertEqual(linear.scale, ridge.scale)

    def test_collinear_and_all_constant_features_are_supported(self):
        for x in ([(1, 2), (2, 4), (3, 6)], [(5, 5)] * 3):
            with self.subTest(x=x):
                for model in self.fit(x=x, y=[1, 2, 3]):
                    self.assertTrue(math.isfinite(model.predict((2, 4))))

    def test_fit_rejects_future_dates_and_duplicate_or_boolean_ids(self):
        cases = (
            {"match_dates": ["2016-02-07"] * 5},
            {"match_dates": ["2016-1-1"] * 5},
            {"match_ids": [1, 1, 3, 4, 5]},
            {"match_ids": [True, 2, 3, 4, 5]},
            {"match_ids": [1, 2]},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.fit(**kwargs)

    def test_fit_rejects_dimensions_insufficiency_and_nonfinite_values(self):
        for x, y in (([(1, 2)] * 2, [1, 2]), ([(1, 2, 3)] * 3, [1, 2, 3]),
                     ([(1, math.nan)] * 3, [1, 2, 3]),
                     ([(1, 2)] * 3, [1, math.inf, 3]),
                     ([(1, 2)] * 3, [1, -1, 3])):
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                self.fit(x=x, y=y)

    def test_repeated_fit_is_identical(self):
        first, second = self.fit(), self.fit()
        self.assertEqual(first, second)
        self.assertEqual([m.predict((3, 2)) for m in first],
                         [m.predict((3, 2)) for m in second])


class ExperimentalTemporalSplitTests(unittest.TestCase):
    def test_fixed_dates_never_split_a_day_and_order_is_stable(self):
        rows = (example(4, "2016-04-09"), example(2, "2016-02-06"),
                example(3, "2016-02-07"), example(1, "2016-02-06"))
        splits = split_examples(rows)
        self.assertEqual([r.features.fixture.match_id for r in splits.train], [1, 2])
        self.assertEqual([r.features.fixture.match_id for r in splits.validation], [3])
        self.assertEqual([r.features.fixture.match_id for r in splits.test], [4])
        self.assertEqual(splits, split_examples(tuple(reversed(rows))))

    def test_duplicate_match_or_gap_date_blocks_evaluation(self):
        row = example(1, "2016-02-06")
        with self.assertRaises(ValueError):
            split_examples((row, row))
        with self.assertRaises(ValueError):
            split_examples((example(2, "2016-04-05"),))
        with self.assertRaises(ValueError):
            split_examples((row,), train_end="2016-04-10")

    def test_insufficient_dataset_abstains_before_fit(self):
        data = replace(dataset(), examples=dataset().examples[:3])
        result = evaluate_dataset(data)
        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("fitted_models", result)
        self.assertNotIn("predictions", result)

    @unittest.skipUnless(HAS_NUMPY, "Regressões experimentais exigem NumPy opcional.")
    def test_holdout_labels_do_not_change_weights_scaler_or_predictions(self):
        original = dataset()
        changed = replace(original, examples=tuple(
            replace(row, label=replace(row.label, home_shots=row.label.home_shots + 100))
            if row.features.fixture.match_date > "2016-02-06" else row
            for row in original.examples))
        before, after = evaluate_dataset(original), evaluate_dataset(changed)
        self.assertEqual(before["fitted_models"], after["fitted_models"])
        self.assertEqual([p["prediction"] for p in before["predictions"]],
                         [p["prediction"] for p in after["predictions"]])
        self.assertNotEqual(before["evaluation"], after["evaluation"])
        for model in before["fitted_models"]:
            self.assertEqual(model["training_match_ids"], tuple(range(1, 31)))
            self.assertEqual(model["train_end"], "2016-02-06")

    @unittest.skipUnless(HAS_NUMPY, "Regressões experimentais exigem NumPy opcional.")
    def test_evaluation_reproducibility_and_common_holdout_matches(self):
        original = dataset()
        before = asdict(original)
        first, second = evaluate_dataset(original), evaluate_dataset(original)
        self.assertEqual(first, second)
        self.assertEqual(asdict(original), before)
        self.assertEqual(first["status"], "evaluated")
        self.assertEqual(len(first["predictions"]), 30 * 4)
        for partition, count in (("validation", 10), ("test", 20)):
            metrics = first["evaluation"][partition]["metrics"]
            self.assertEqual(set(metrics), {"historical_mean", "combined_means", "linear", "ridge"})
            self.assertTrue(all(values["n"] == count for values in metrics.values()))
            ids_by_model = [{p["match_id"] for p in first["predictions"]
                             if p["partition"] == partition and p["model_id"] == model}
                            for model in metrics]
            self.assertTrue(all(ids == ids_by_model[0] for ids in ids_by_model))


if __name__ == "__main__":
    unittest.main()
