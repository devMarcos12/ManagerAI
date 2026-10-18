"""Dataset supervisionado: somente fixtures sintéticas, sem evidência esportiva."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import math
from unittest.mock import patch

from managerai.data_loader import DataError, LocalData
from managerai.experiments import dataset as supervised
from test_managerai import LocalFixture


class ExperimentalDatasetTests(LocalFixture):
    def setUp(self):
        super().setUp()
        # Extend only this test's temporary files, never the shared fixture helpers.
        self.type_ids = {"Shot": 16, "Pass": 30, "Carry": 43, "Duel": 4,
                         "Pressure": 17, "Half End": 34}
        for match in self.matches:
            events = self.events(match["match_id"])
            for event in events:
                event["type"]["id"] = self.type_ids[event["type"]["name"]]
            self.write(f"events/{match['match_id']}.json", events)

    def events(self, match_id):
        return json.loads((self.root / "events" / f"{match_id}.json").read_text())

    def add_home_shot(self, match_id, *, period=1, outcome="Blocked", shot_type="Open Play"):
        events = self.events(match_id)
        event = deepcopy(next(e for e in events if e["type"]["name"] == "Shot" and e["team"]["id"] == 1))
        event.update(id=f"extra-{match_id}-{len(events)}", index=max(e["index"] for e in events) + 1, period=period)
        event["shot"].update(outcome={"name": outcome}, type={"name": shot_type})
        events.append(event)
        self.write(f"events/{match_id}.json", events)

    def fixture(self, match_id=8):
        return supervised.Fixture(match_id, self.matches[match_id - 1]["match_date"], 1, 2)

    def example(self, dataset, match_id=8):
        return next(e for e in dataset.examples if e.features.fixture.match_id == match_id)

    def test_eligible_counts_order_and_sources_are_reproducible(self):
        first = supervised.build_dataset(self.root)
        self.assertEqual([e.features.fixture.match_id for e in first.examples], [6, 7, 8, 9])
        self.assertEqual([e.match_id for e in first.excluded], [1, 2, 3, 4, 5])
        self.assertEqual(first.to_dict(), supervised.build_dataset(self.root).to_dict())
        self.assertEqual(first.audit["catalogued_matches"], len(first.examples) + len(first.excluded))
        self.assertEqual(len({e.features.fixture.match_id for e in first.examples}), len(first.examples))
        self.assertEqual(first.audit["cross_match_duplicate_event_ids"], 0)

    def test_target_and_future_data_do_not_change_target_features(self):
        original = self.example(supervised.build_dataset(self.root))
        self.add_home_shot(8, outcome="Goal")
        self.add_home_shot(9, outcome="Saved")
        self.matches[7].update(home_score=100, away_score=99)
        self.write("matches/2/27.json", self.matches)
        changed = self.example(supervised.build_dataset(self.root))
        self.assertEqual(original.features, changed.features)
        self.assertEqual(original.features.fingerprint, changed.features.fingerprint)
        self.assertEqual(changed.label.home_shots, original.label.home_shots + 1)
        self.assertNotEqual(original.label.sources, changed.label.sources)

    def test_same_day_is_never_history_even_if_kickoff_is_earlier(self):
        self.matches[6]["match_date"] = self.matches[7]["match_date"]
        self.matches[6]["kick_off"] = "10:00:00.000"
        self.write("matches/2/27.json", self.matches)
        row = self.example(supervised.build_dataset(self.root)).features
        self.assertEqual([r.match_id for r in row.home_history], [2, 3, 4, 5, 6])
        self.assertTrue(all(r.match_date < row.fixture.match_date for r in row.home_history + row.away_history))

    def test_calendar_input_order_does_not_change_output(self):
        before = supervised.build_dataset(self.root)
        self.write("matches/2/27.json", list(reversed(self.matches)))
        after = supervised.build_dataset(self.root)
        self.assertEqual(before.examples, after.examples)
        self.assertEqual(before.excluded, after.excluded)
        # Source hashes legitimately differ when calendar bytes are reordered.

    def test_all_feature_builds_finish_before_separate_label_reader(self):
        calls = []
        real_events = LocalData.events
        real_builder = supervised.build_pre_match_features
        def read_events(loader, mid):
            calls.append(("events", id(loader), mid))
            return real_events(loader, mid)
        def build(*args, **kwargs):
            calls.append(("builder", None, args[0].match_id))
            return real_builder(*args, **kwargs)
        with patch.object(LocalData, "events", read_events), patch.object(supervised, "build_pre_match_features", build):
            supervised.build_dataset(self.root)
        builders = [i for i, call in enumerate(calls) if call[0] == "builder"]
        label_loader = next(call[1] for call in calls[max(builders) + 1:] if call[0] == "events")
        self.assertTrue(builders)
        self.assertTrue(all(i > max(builders) for i, call in enumerate(calls) if call[0] == "events" and call[1] == label_loader))
        history_loaders = {call[1] for call in calls[:min(builders)] if call[0] == "events"}
        self.assertNotIn(label_loader, history_loaders)

    def test_pure_builder_only_receives_frozen_historical_evidence(self):
        row = self.example(supervised.build_dataset(self.root)).features
        rebuilt = supervised.build_pre_match_features(row.fixture, row.home_history, row.away_history)
        self.assertEqual(row, rebuilt)
        self.assertEqual(row.values, (1.0, 1.0))
        self.assertTrue(all(r.match_id not in (8, 9) for r in row.home_history + row.away_history))
        self.assertFalse(hasattr(row.fixture, "home_score"))

    def test_labels_count_all_shot_outcomes_and_regulation_penalties_only(self):
        for outcome in ("Blocked", "Goal", "Saved", "Off T", "Wayward", "Post", "Saved Off Target"):
            self.add_home_shot(8, outcome=outcome)
        self.add_home_shot(8, period=2, shot_type="Penalty")
        self.add_home_shot(8, period=3)
        self.add_home_shot(8, period=5, shot_type="Penalty")
        label = supervised.extract_observed_label(LocalData(self.root), self.fixture())
        self.assertEqual(label.home_shots, 9)
        self.assertEqual(label.match_id, 8)

    def test_feature_and_label_provenance_are_separate(self):
        example = self.example(supervised.build_dataset(self.root))
        sources = {p for r in example.features.home_history + example.features.away_history for p, _ in r.sources}
        self.assertNotIn("events/8.json", sources)
        self.assertNotIn("lineups/8.json", sources)
        self.assertNotIn("events/9.json", sources)
        self.assertEqual({p for p, _ in example.label.sources}, {"events/8.json", "lineups/8.json"})
        self.assertEqual(len(example.features.fingerprint), 64)

    def test_missing_selected_history_is_not_replaced_with_older_match(self):
        (self.root / "events/7.json").unlink()
        dataset = supervised.build_dataset(self.root)
        self.assertFalse(any(e.features.fixture.match_id == 8 for e in dataset.examples))
        reasons = next(e.reasons for e in dataset.excluded if e.match_id == 8)
        self.assertTrue(any("7" in reason and "sem reposição" in reason for reason in reasons))
        self.assertEqual(len(dataset.examples) + len(dataset.excluded), 9)

    def test_missing_target_label_is_excluded_and_never_filled(self):
        (self.root / "events/9.json").unlink()
        dataset = supervised.build_dataset(self.root)
        self.assertEqual([e.features.fixture.match_id for e in dataset.examples], [6, 7, 8])
        exclusion = next(e for e in dataset.excluded if e.match_id == 9)
        self.assertIn("label indisponível", " ".join(exclusion.reasons))

    def test_insufficient_teams_have_explicit_exclusions(self):
        dataset = supervised.build_dataset(self.root)
        for mid in (1, 2, 3, 4, 5):
            reasons = next(e.reasons for e in dataset.excluded if e.match_id == mid)
            self.assertTrue(any("home:" in r for r in reasons))
            self.assertTrue(any("away:" in r for r in reasons))

    def test_duplicate_event_ids_or_indices_are_rejected(self):
        original = self.events(8)
        for field in ("id", "index"):
            with self.subTest(field=field):
                events = deepcopy(original)
                events[1][field] = events[0][field]
                self.write("events/8.json", events)
                with self.assertRaises(DataError):
                    supervised.extract_observed_label(LocalData(self.root), self.fixture())
        self.write("events/8.json", original)

    def test_duplicate_ids_across_matches_are_rejected(self):
        events = self.events(9)
        events[0]["id"] = self.events(1)[0]["id"]
        self.write("events/9.json", events)
        with self.assertRaisesRegex(DataError, "entre partidas"):
            supervised.build_dataset(self.root)

    def test_shot_id_name_disagreement_and_explicit_cancel_are_rejected(self):
        original = self.events(8)
        for changes in ({"type": {"id": 99, "name": "Shot"}},
                        {"type": {"id": 16, "name": "Pass"}}, {"cancelled": True}):
            with self.subTest(changes=changes):
                events = deepcopy(original)
                shot = next(e for e in events if e["type"]["name"] == "Shot")
                shot.update(changes)
                if shot["type"]["name"] == "Pass":
                    shot["pass"] = {"end_location": [110, 40]}
                self.write("events/8.json", events)
                with self.assertRaises(DataError):
                    supervised.extract_observed_label(LocalData(self.root), self.fixture())

    def test_duplicate_calendar_match_is_rejected(self):
        self.write("matches/2/27.json", self.matches + [self.matches[0]])
        with self.assertRaises(DataError):
            supervised.build_dataset(self.root)

    def test_feature_contract_rejects_target_future_same_day_and_wrong_team(self):
        row = self.example(supervised.build_dataset(self.root)).features
        first = row.home_history[0]
        for change in ({"match_id": 8}, {"match_date": "2020-01-08"},
                       {"match_date": "2020-01-10"}, {"team_id": 2}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                history = (replace(first, **change),) + row.home_history[1:]
                supervised.build_pre_match_features(row.fixture, history, row.away_history)

    def test_feature_contract_rejects_missing_duplicate_unordered_and_nonfinite(self):
        row = self.example(supervised.build_dataset(self.root)).features
        for history in (row.home_history[:4], (row.home_history[0],) * 5, tuple(reversed(row.home_history))):
            with self.subTest(history=history), self.assertRaises(ValueError):
                replace(row, home_history=history)
        for values in ((math.nan, 1.0), (math.inf, 1.0), (-1.0, 1.0), (True, 1.0), (2.0, 1.0)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                replace(row, values=values)

    def test_prediction_and_label_contracts_reject_invalid_values(self):
        row = self.example(supervised.build_dataset(self.root)).features
        sources = tuple(sorted({source for h in row.home_history + row.away_history for source in h.sources}))
        prediction = supervised.QuantitativePrediction("synthetic-test-only", 8, "2020-01-08", 1.0, row.fingerprint, sources)
        for value in (math.nan, math.inf, -0.1, True, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                replace(prediction, prediction=value)
        with self.assertRaises(ValueError):
            replace(prediction, sufficient=False)
        for value in (-1, 1.5, True):
            with self.subTest(label=value), self.assertRaises(ValueError):
                supervised.ObservedLabel(8, value, (("events/8.json", "a" * 64),))
        with self.assertRaises(ValueError):
            supervised.Example(row, supervised.ObservedLabel(9, 1, (("events/9.json", "a" * 64),)))

    def test_valid_observed_zero_shots_is_not_missing_data(self):
        events = [e for e in self.events(8) if not (e["type"]["name"] == "Shot" and e["team"]["id"] == 1)]
        self.write("events/8.json", events)
        label = supervised.extract_observed_label(LocalData(self.root), self.fixture())
        self.assertEqual(label.home_shots, 0)
        self.assertEqual(self.example(supervised.build_dataset(self.root)).label.home_shots, 0)

    def test_missing_lineup_preserves_collective_counts_and_quality_gap(self):
        (self.root / "lineups/7.json").unlink()
        row = self.example(supervised.build_dataset(self.root)).features
        self.assertEqual(row.values, (1.0, 1.0))
        evidence = next(h for h in row.home_history if h.match_id == 7)
        self.assertEqual(dict(evidence.quality)["missing_lineup_files"], 1)
        self.assertNotIn("lineups/7.json", dict(evidence.sources))

    def test_observed_and_historical_sources_are_immutable_and_match_bound(self):
        example = self.example(supervised.build_dataset(self.root))
        label = example.label
        historical = example.features.home_history[0]
        for sources in (list(label.sources), (), (("events/999.json", "a" * 64),),
                        (("../events/8.json", "a" * 64),), (("events/8.json", "not-a-sha"),),
                        (label.sources[0], label.sources[0]), (("/events/8.json", "a" * 64),)):
            with self.subTest(label_sources=sources), self.assertRaises(ValueError):
                replace(label, sources=sources)
        for sources in (list(historical.sources), (("events/8.json", "a" * 64),),
                        ((f"events/{historical.match_id}.json", "g" * 64),)):
            with self.subTest(historical_sources=sources), self.assertRaises(ValueError):
                replace(historical, sources=sources)

    def test_prediction_rejects_target_sources_mutable_sources_and_wrong_contract(self):
        row = self.example(supervised.build_dataset(self.root)).features
        sources = tuple(sorted({source for h in row.home_history + row.away_history for source in h.sources}))
        prediction = supervised.QuantitativePrediction("synthetic-test-only", 8, "2020-01-08", 1.0, row.fingerprint, sources)
        for changes in ({"feature_sources": list(sources)},
                        {"feature_sources": (("events/8.json", "a" * 64),)},
                        {"feature_sources": (("lineups/8.json", "a" * 64),)},
                        {"feature_fingerprint": "z" * 64},
                        {"limitations": ["mutable"]}, {"task_version": "unknown"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(prediction, **changes)
