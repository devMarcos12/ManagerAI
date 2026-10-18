"""Descriptive paired diagnostics; no fitting, IID inference or model selection.

Each input row represents one fixture. Team summaries overlap (each fixture
appears for both teams); neither these summaries nor temporal sensitivities
create additional independent observations. Sensitivities remove already
computed predictions, without refitting or choosing models on their results.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date
import math

from .models import _distribution, evaluate_predictions


def paired_comparison(observed, predictions, *, reference="combined_means"):
    """Compare aligned, finite nonnegative predictions on the same fixtures.

    Negative deltas favor the model numerically. Wins/ties/losses compare
    absolute errors exactly (no arbitrary significance/tolerance threshold).
    All distributions are descriptive, with the AB linear quantile convention.
    """
    if (not isinstance(predictions, Mapping) or not predictions
            or any(not isinstance(k, str) or not k.strip() for k in predictions)
            or reference not in predictions):
        raise ValueError("Named predictions and an available reference are required.")
    try:
        actual = tuple(observed)
        estimates = {key: tuple(predictions[key]) for key in sorted(predictions)}
    except TypeError as exc:
        raise ValueError("Observations and predictions must be aligned sequences.") from exc
    metrics = {key: evaluate_predictions(actual, values)
               for key, values in estimates.items()}
    n = len(actual)
    ref = estimates[reference]
    result = {}
    for key, values in estimates.items():
        differences = tuple(abs(float(p) - float(y)) - abs(float(r) - float(y))
                            for y, p, r in zip(actual, values, ref))
        result[key] = {
            "metrics": metrics[key],
            "delta_mae": math.fsum(d / n for d in differences),
            "delta_rmse": metrics[key]["rmse"] - metrics[reference]["rmse"],
            "delta_bias": metrics[key]["bias"] - metrics[reference]["bias"],
            "absolute_error_difference_distribution": {
                "signed": _distribution(differences),
                "absolute": _distribution(tuple(abs(d) for d in differences)),
            },
            "wins": sum(d < 0 for d in differences),
            "ties": sum(d == 0 for d in differences),
            "losses": sum(d > 0 for d in differences),
        }
    return {"n": n, "reference": reference, "models": result}


def _canonical_rows(rows, reference):
    try:
        items = tuple(rows)
    except TypeError as exc:
        raise ValueError("Rows must be a nonempty sequence.") from exc
    if not items:
        raise ValueError("Rows must be a nonempty sequence.")
    seen, keys, canonical = set(), None, []
    for row in items:
        if not isinstance(row, Mapping):
            raise ValueError("Each row must be a mapping.")
        try:
            match_id, day = row["match_id"], row["match_date"]
            home, away = row["home_team_id"], row["away_team_id"]
            predictions, observed = row["predictions"], row["observed"]
        except KeyError as exc:
            raise ValueError("Missing fixture or prediction field.") from exc
        if (any(type(v) is not int or v <= 0 for v in (match_id, home, away))
                or home == away or match_id in seen):
            raise ValueError("Expected unique positive fixture IDs and distinct teams.")
        if not isinstance(day, str):
            raise ValueError("Expected canonical ISO fixture date.")
        try:
            if date.fromisoformat(day).isoformat() != day:
                raise ValueError("Noncanonical date.")
        except ValueError as exc:
            raise ValueError("Expected canonical ISO fixture date.") from exc
        if not isinstance(predictions, Mapping):
            raise ValueError("Named predictions required.")
        current_keys = frozenset(predictions)
        if keys is not None and current_keys != keys:
            raise ValueError("Every fixture must contain the same models.")
        # Reuse AB validators; booleans, NaNs, infinities and negatives fail.
        paired_comparison([observed], {k: [v] for k, v in predictions.items()},
                          reference=reference)
        seen.add(match_id)
        keys = current_keys
        canonical.append({"match_id": match_id, "match_date": day,
                          "home_team_id": home, "away_team_id": away,
                          "observed": float(observed),
                          "predictions": {k: float(predictions[k])
                                          for k in sorted(predictions)}})
    return sorted(canonical, key=lambda row: (row["match_date"], row["match_id"]))


def stability_diagnostics(rows, *, reference="combined_means"):
    """Summarize fixed predictions, dependencies and deletion sensitivities.

    All months, including n=1, are reported with their sample size; no inference
    is made from small groups. Top-5% deletion requires n>=20, uses ceil(.05*n)
    and ranks reference absolute error descending, date and ID ascending. These
    deletions expose influence, never correct or hide the original evaluation.
    """
    ordered = _canonical_rows(rows, reference)
    model_ids = tuple(ordered[0]["predictions"])

    def compare(subset):
        return paired_comparison(
            [r["observed"] for r in subset],
            {model: [r["predictions"][model] for r in subset] for model in model_ids},
            reference=reference)

    monthly = {}
    for month in sorted({r["match_date"][:7] for r in ordered}):
        subset = [r for r in ordered if r["match_date"][:7] == month]
        monthly[month] = {"n": len(subset), "match_ids": [r["match_id"] for r in subset],
                          "comparison": compare(subset)}
    teams = {}
    for team in sorted({r[role] for r in ordered
                        for role in ("home_team_id", "away_team_id")}):
        subset = [r for r in ordered if team in (r["home_team_id"], r["away_team_id"])]
        teams[str(team)] = {"n": len(subset), "comparison": compare(subset)}

    if len(monthly) > 1:
        leave_month = {"status": "computed", "results": {
            month: compare([r for r in ordered if r["match_date"][:7] != month])
            for month in monthly}}
    else:
        leave_month = {"status": "omitted", "reason": "Only one calendar month available."}

    n = len(ordered)
    if n >= 20:
        ranked = sorted(ordered, key=lambda r: (
            -abs(r["predictions"][reference] - r["observed"]),
            r["match_date"], r["match_id"]))
        count = math.ceil(n / 20)
        excluded = [r["match_id"] for r in ranked[:count]]
        excluded_ids = set(excluded)
        top = {"status": "computed", "excluded_count": count,
               "reference_outlier_ids": excluded,
               "comparison": compare([r for r in ordered if r["match_id"] not in excluded_ids])}
    else:
        top = {"status": "omitted", "reason": "At least 20 fixtures required for top-5% deletion."}

    if n > 1:
        # Recompute retained means directly to avoid subtraction cancellation
        # and overflow of unscaled sums. No refit or CI/p-value is implied.
        ranges = {}
        for model in model_ids:
            differences = [abs(r["predictions"][model] - r["observed"])
                           - abs(r["predictions"][reference] - r["observed"])
                           for r in ordered]
            leave_one = [math.fsum(d / (n - 1) for j, d in enumerate(differences)
                                   if j != excluded) for excluded in range(n)]
            ranges[model] = {"min_delta_mae": min(leave_one),
                             "max_delta_mae": max(leave_one)}
        leave_match = {"status": "computed", "models": ranges}
    else:
        leave_match = {"status": "omitted", "reason": "At least two fixtures required."}

    return {
        "n": n, "descriptive_only": True,
        "dependence_warning": "Fixtures share teams and historical windows. Team exposures overlap; "
                              "their sum is twice n, not additional independent observations. "
                              "Deletion sensitivities reuse fixed predictions without refitting. "
                              "No confidence intervals, p-values or causal claims are produced.",
        "match_ids": [r["match_id"] for r in ordered],
        "aggregate": compare(ordered), "monthly": monthly, "team_exposure": teams,
        "sensitivity": {"leave_one_month_out": leave_month,
                        "exclude_reference_top_five_percent": top,
                        "leave_one_match_out": leave_match},
    }
