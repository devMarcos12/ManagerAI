"""Blocos sintéticos, associação temporal e política de ausência da V3."""
import unittest

from managerai.v3_sequences import sequence_summary


MATCH = {"match_id": 100, "match_date": "2016-01-01",
         "home_team": {"home_team_id": 1}, "away_team": {"away_team_id": 2}}


def event(index, typ="Pass", owner=1, tid=1, possession=1, period=1,
          start=(30, 40), end=(40, 40), **extra):
    data = {"id": str(index), "index": index, "period": period,
            "timestamp": f"00:00:{index:02d}.000", "possession": possession,
            "possession_team": {"id": owner}, "team": {"id": tid},
            "type": {"name": typ}, "location": list(start)}
    if typ in ("Pass", "Carry"):
        data[typ.lower()] = {"end_location": list(end)}
    data.update(extra)
    return data


class SequenceTests(unittest.TestCase):
    def summary(self, events):
        return sequence_summary(MATCH, events, 1)

    def test_entry_shot_evidence_and_denominator(self):
        es = [event(1), event(2, "Carry", end=(60, 40)),
              event(3, start=(60, 40), end=(85, 40)), event(4, "Shot", start=(100, 40))]
        result = self.summary(es)
        self.assertEqual((result["valid_blocks"], result["entry_blocks"], result["shot_blocks"]), (1, 1, 1))
        block = result["blocks"][0]
        self.assertEqual([e["event_id"] for e in block["entries"][0]["preceding_actions"]], ["1", "2"])
        self.assertEqual([e["event_id"] for e in block["shots"][0]["preceding_actions"]], ["1", "2", "3"])
        self.assertIn("causalidade", " ".join(result["limitations"]))
        self.assertEqual(result["entry_block_share"], 100)

    def test_returning_possession_is_not_joined(self):
        result = self.summary([event(1, possession=73), event(2, owner=2, tid=2, possession=74),
                               event(3, possession=73, start=(70, 40), end=(90, 40))])
        self.assertEqual(result["valid_blocks"], 2)
        self.assertEqual(result["blocks"][1]["entries"][0]["preceding_actions"], [])

    def test_period_change_breaks_block_and_accepts_clock_reset(self):
        result = self.summary([event(1), event(2, period=2, timestamp="00:00:00.000")])
        self.assertEqual(result["valid_blocks"], 2)

    def test_off_owner_actions_are_not_own_attack(self):
        result = self.summary([event(1, "Pressure", tid=2), event(2), event(3, "Shot", tid=2)])
        self.assertEqual(result["valid_blocks"], 1)
        self.assertEqual(result["shot_blocks"], 0)
        self.assertEqual(result["blocks"][0]["offensive_action_ids"], ["2"])

    def test_only_pressure_is_not_a_denominator(self):
        result = self.summary([event(1, "Pressure")])
        self.assertEqual(result["valid_blocks"], 0)
        self.assertIsNone(result["entry_block_share"])

    def test_missing_context_is_unavailable_not_zero(self):
        for field in ["possession", "possession_team", "timestamp"]:
            e = event(1)
            del e[field]
            result = self.summary([e])
            self.assertIsNone(result["valid_blocks"])
            self.assertIsNone(result["entry_blocks"])
            self.assertTrue(result["quality"])

    def test_bad_timestamp_or_period_invalidates_game(self):
        for second in [event(2, timestamp="bad"), event(2, timestamp="00:00:00.000"),
                       event(2, period=0), event(2, owner=99)]:
            self.assertIsNone(self.summary([event(1), second])["valid_blocks"])
        self.assertIsNone(self.summary([event(1, period=2), event(2, period=1)])["valid_blocks"])

    def test_bad_identity_is_unavailable_and_input_not_sorted_in_place(self):
        es = [event(2), event(1)]
        self.assertEqual(self.summary(es)["valid_blocks"], 1)
        self.assertEqual(es[0]["index"], 2)
        self.assertIsNone(self.summary([event(1), event(1)])["valid_blocks"])

    def test_lateral_box_entry_and_incomplete_pass_break_chain(self):
        incomplete = event(2)
        incomplete["pass"]["outcome"] = {"name": "Incomplete"}
        result = self.summary([event(1), incomplete, event(3, start=(110, 5), end=(110, 25))])
        entry = result["blocks"][0]["entries"][0]
        self.assertTrue(entry["box"])
        self.assertFalse(entry["final_third"])
        self.assertEqual(entry["preceding_actions"], [])

    def test_geometry_gap_and_empty_stream_are_unavailable(self):
        self.assertIsNone(self.summary([])["valid_blocks"])
        self.assertIsNone(self.summary([event(1, start=(121, 0))])["valid_blocks"])

    def test_malformed_objects_are_unavailable(self):
        for field in ["possession_team", "team", "type"]:
            self.assertIsNone(self.summary([event(1, **{field: [1, 2]})])["valid_blocks"])
        self.assertIsNone(self.summary([None])["valid_blocks"])

    def test_evidence_limited_to_three_prior_actions(self):
        result = self.summary([event(i) for i in range(1, 6)] + [event(6, "Shot")])
        self.assertEqual([e["event_id"] for e in result["blocks"][0]["shots"][0]["preceding_actions"]], ["3", "4", "5"])


if __name__ == "__main__":
    unittest.main()
