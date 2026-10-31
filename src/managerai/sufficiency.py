"""Política comum; mínimos operacionais não representam confiança estatística."""
MIN_SAMPLE = 5
CORE_METRICS = ("xg_for", "xg_against", "shots_for", "shots_against",
                "pass_accuracy", "final_third_entries")


def insufficient_core_evidence(report) -> bool:
    return any(profile.metrics.get(key) is None or profile.metrics[key].value is None
               or profile.metrics[key].sample_size < MIN_SAMPLE
               for profile in (report.team_profile, report.opponent_profile)
               for key in CORE_METRICS)
