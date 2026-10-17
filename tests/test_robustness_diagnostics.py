"""Synthetic fixed predictions validate arithmetic, not sporting performance."""
from copy import deepcopy
from datetime import date, timedelta
import json
import math
import unittest

from managerai.experiments.robustness_diagnostics import (
    paired_comparison, stability_diagnostics,
)


def rows():
    return [
        {"match_id": 3, "match_date": "2016-01-02", "home_team_id": 1,
         "away_team_id": 2, "observed": 30,
         "predictions": {"combined_means": 34, "linear": 36}},
        {"match_id": 1, "match_date": "2015-12-02", "home_team_id": 1,
         "away_team_id": 3, "observed": 10,
         "predictions": {"combined_means": 12, "linear": 11}},
        {"match_id": 2, "match_date": "2015-12-02", "home_team_id": 2,
         "away_team_id": 3, "observed": 20,
         "predictions": {"combined_means": 17, "linear": 20}},
    ]


class PairedDiagnosticTests(unittest.TestCase):
    def test_manual_metrics_differences_and_wins(self):
        result = paired_comparison([10, 20, 30],
                                  {"combined_means": [12, 17, 34],
                                   "linear": [11, 20, 36]})
        self.assertEqual(result["n"], 3)
        linear = result["models"]["linear"]
        self.assertAlmostEqual(linear["metrics"]["mae"], 7 / 3)
        self.assertAlmostEqual(linear["delta_mae"], -2 / 3)
        self.assertAlmostEqual(linear["delta_rmse"], math.sqrt(37 / 3) - math.sqrt(29 / 3))
        self.assertAlmostEqual(linear["delta_bias"], 4 / 3)
        self.assertEqual((linear["wins"], linear["ties"], linear["losses"]), (2, 0, 1))
        self.assertEqual(linear["absolute_error_difference_distribution"]["signed"]["median"], -1)
        self.assertEqual(linear["absolute_error_difference_distribution"]["absolute"]["median"], 2)
        reference = result["models"]["combined_means"]
        self.assertEqual((reference["delta_mae"], reference["wins"], reference["ties"]), (0, 0, 3))

    def test_ties_compare_absolute_not_signed_error(self):
        result = paired_comparison([10], {"combined_means": [8], "other": [12]})
        self.assertEqual(result["models"]["other"]["ties"], 1)
        self.assertEqual(result["models"]["other"]["delta_bias"], 4)

    def test_custom_reference_and_model_key_order(self):
        result = paired_comparison([1], {"z": [2], "a": [1]}, reference="z")
        self.assertEqual(list(result["models"]), ["a", "z"])
        self.assertEqual(result["models"]["a"]["delta_mae"], -1)

    def test_invalid_and_misaligned_comparisons_fail(self):
        cases = [([], {"combined_means": []}), ([1], {}),
                 ([1], {"unknown": [1]}), ([1], {"combined_means": []}),
                 ([1], {"combined_means": [1, 2]}),
                 ([1], {"combined_means": [-1]}),
                 ([1], {"combined_means": [float("nan")]}),
                 ([1], {"combined_means": [float("inf")]}),
                 ([-1], {"combined_means": [1]}),
                 ([True], {"combined_means": [1]}),
                 ([1], {"combined_means": [False]}),
                 ([1], {"combined_means": [1], "": [1]}),
                 (None, {"combined_means": [1]})]
        for actual, predictions in cases:
            with self.subTest(actual=actual, predictions=predictions), self.assertRaises(ValueError):
                paired_comparison(actual, predictions)


class StabilityDiagnosticTests(unittest.TestCase):
    def test_canonical_order_same_day_and_reproducibility(self):
        original = rows()
        before = deepcopy(original)
        first = stability_diagnostics(original)
        second = stability_diagnostics(list(reversed(original)))
        self.assertEqual(first["match_ids"], [1, 2, 3])
        self.assertEqual(first["monthly"]["2015-12"]["match_ids"], [1, 2])
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(original, before)

    def test_monthly_metrics_are_manual_and_team_counts_overlap(self):
        result = stability_diagnostics(rows())
        december = result["monthly"]["2015-12"]["comparison"]["models"]["linear"]
        self.assertEqual(december["metrics"]["mae"], .5)
        self.assertEqual(december["delta_mae"], -2)
        self.assertEqual(sum(group["n"] for group in result["team_exposure"].values()), 6)
        self.assertEqual(result["team_exposure"]["1"]["comparison"]["models"]["linear"]["metrics"]["mae"], 3.5)
        self.assertTrue(result["descriptive_only"])
        self.assertIn("overlap", result["dependence_warning"])
        self.assertNotIn("confidence_interval", result)

    def test_leave_one_month_out_reuses_fixed_predictions(self):
        result = stability_diagnostics(rows())["sensitivity"]["leave_one_month_out"]
        self.assertEqual(result["status"], "computed")
        december_deleted = result["results"]["2015-12"]
        self.assertEqual(december_deleted["n"], 1)
        self.assertEqual(december_deleted["models"]["linear"]["delta_mae"], 2)
        self.assertEqual(result["results"]["2016-01"]["models"]["linear"]["delta_mae"], -2)

    def test_leave_one_match_out_range_matches_manual_deltas(self):
        result = stability_diagnostics(rows())["sensitivity"]["leave_one_match_out"]
        self.assertEqual(result["models"]["linear"],
                         {"min_delta_mae": -2., "max_delta_mae": .5})

    def test_one_fixture_omits_undefined_deletions(self):
        result = stability_diagnostics(rows()[:1])
        self.assertEqual(result["aggregate"]["n"], 1)
        for sensitivity in result["sensitivity"].values():
            self.assertEqual(sensitivity["status"], "omitted")
            self.assertTrue(sensitivity["reason"])

    def test_small_sample_keeps_metrics_but_omits_top_five_percent(self):
        result = stability_diagnostics(rows())
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["sensitivity"]["exclude_reference_top_five_percent"]["status"], "omitted")

    def test_top_five_percent_uses_ceil_and_reference_errors_only(self):
        sample = []
        for index in range(21):
            sample.append({"match_id": index + 1,
                           "match_date": (date(2016, 1, 1) + timedelta(days=index)).isoformat(),
                           "home_team_id": 1, "away_team_id": 2,
                           "observed": 0,
                           "predictions": {"combined_means": index, "linear": 20 - index}})
        result = stability_diagnostics(sample)["sensitivity"]["exclude_reference_top_five_percent"]
        self.assertEqual(result["excluded_count"], 2)
        self.assertEqual(result["reference_outlier_ids"], [21, 20])
        self.assertEqual(result["comparison"]["n"], 19)
        twenty = stability_diagnostics(sample[:20])["sensitivity"]["exclude_reference_top_five_percent"]
        self.assertEqual(twenty["excluded_count"], 1)

    def test_outlier_ties_rank_date_then_match_id(self):
        sample = [dict(rows()[0], match_id=i, match_date="2016-01-02") for i in range(1, 21)]
        result = stability_diagnostics(list(reversed(sample)))["sensitivity"]["exclude_reference_top_five_percent"]
        self.assertEqual(result["reference_outlier_ids"], [1])

    def test_empty_duplicate_ids_and_incomplete_models_rejected(self):
        cases = [[], [rows()[0], rows()[0]], [None], [{}]]
        changed = rows()
        changed[0]["predictions"] = {"combined_means": 1}
        cases.append(changed)
        for sample in cases:
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                stability_diagnostics(sample)

    def test_invalid_fixture_metadata_rejected(self):
        for key, value in (("match_id", True), ("home_team_id", 0),
                           ("away_team_id", 1), ("match_date", "20160102"),
                           ("match_date", "2016-02-30"), ("match_date", None),
                           ("observed", math.nan), ("predictions", [])):
            sample = rows()
            sample[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                stability_diagnostics(sample)

    def test_leave_one_match_out_avoids_overflow_for_finite_large_means(self):
        sample = [dict(rows()[0], match_id=i, observed=0,
                       predictions={"combined_means": 0, "linear": 1e308}) for i in (1, 2)]
        result = stability_diagnostics(sample)["sensitivity"]["leave_one_match_out"]["models"]["linear"]
        self.assertEqual(result["min_delta_mae"], 1e308)
        self.assertEqual(result["max_delta_mae"], 1e308)


if __name__ == "__main__":
    unittest.main()
