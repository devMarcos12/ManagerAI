"""Participação verificada e frequência de formação inicial, sem ranking."""
import unittest

from managerai.data_loader import DataError
from managerai.v3_history import aggregate_history, historical_participation


MATCH = {"match_id": 10, "match_date": "2016-01-01", "home_team": {"home_team_id": 1}, "away_team": {"away_team_id": 2}}
ROSTER = [{"team_id": 1, "lineup": [{"player_id": 7, "player_name": "Zé"}, {"player_id": 8, "player_name": "Ana"}]},
          {"team_id": 2, "lineup": [{"player_id": 9, "player_name": "Rival"}]}]


def event(eid, typ="Pass", pid=7, tid=1, **extra):
    e = {"id": eid, "period": 1, "team": {"id": tid}, "player": {"id": pid},
         "type": {"name": typ}, "pass": {"end_location": [80, 40]},
         "carry": {"end_location": [80, 40]}, "shot": {"statsbomb_xg": .2}}
    e.update(extra)
    return e


class HistoricalTests(unittest.TestCase):
    def analyze(self, events, roster=ROSTER, match=MATCH):
        return historical_participation(match, events, roster, 1)

    def test_team_player_association_and_alphabetical_order(self):
        row = self.analyze([event("a"), event("b", pid=8), event("c", pid=9), event("d", pid=9, tid=2)])
        self.assertEqual([p["name"] for p in row["players"]], ["Ana", "Zé"])
        self.assertEqual(row["quality"]["unverified_player_actions_excluded"], 1)
        self.assertTrue(all(p["availability"] == "desconhecida" for p in row["players"]))

    def test_missing_roster_excludes_unverified_players(self):
        row = self.analyze([event("a"), event("b", "Shot")], None)
        self.assertEqual(row["players"], [])
        self.assertFalse(row["roster_verified"])
        self.assertEqual(row["quality"]["unverified_player_actions_excluded"], 2)

    def test_counts_and_xg_missing_is_not_partial_sum(self):
        es = [event("a"), event("b", "Carry"), event("c", "Pressure"),
              event("d", "Shot"), event("e", "Shot", shot={})]
        player = self.analyze(es)["players"][0]
        self.assertEqual((player["passes_completed"], player["carries"], player["shots"], player["pressures"]), (1, 1, 2, 1))
        self.assertEqual(player["total_actions"], 5)
        self.assertIsNone(player["xg"])
        self.assertEqual(player["event_ids"], ["a", "b", "c", "d", "e"])

    def test_distinct_match_denominator_and_zero_shots(self):
        a = self.analyze([event("a"), event("b")])
        b = self.analyze([event("c", "Shot")], match={**MATCH, "match_id": 11, "match_date": "2016-01-02"})
        aggregate = aggregate_history([b, a])
        player = aggregate["players"][0]
        self.assertEqual(aggregate["match_dates"], {"10": "2016-01-01", "11": "2016-01-02"})
        self.assertEqual(player["matches_with_actions"], 2)
        self.assertEqual(player["match_ids"], [10, 11])
        self.assertEqual(player["xg"], .2)
        self.assertEqual(a["players"][0]["xg"], 0)
        with self.assertRaises(DataError):
            aggregate_history([a, a])

    def test_initial_frequency_excludes_tactical_changes(self):
        es = [event("a", "Starting XI", tactics={"formation": 433}),
              event("b", "Tactical Shift", tactics={"formation": 442})]
        a = self.analyze(es)
        b = self.analyze([event("c", "Starting XI", tactics={"formation": 433})], match={**MATCH, "match_id": 11})
        result = aggregate_history([a, b])
        self.assertEqual(result["matches_with_initial_formation"], 2)
        self.assertEqual(result["initial_formations"], [{"formation": 433, "match_ids": [10, 11], "event_ids": ["a", "c"], "matches": 2, "share": 100}])
        self.assertEqual(result["formation_changes"][0]["formation"], 442)

    def test_ambiguous_initial_formation_excluded(self):
        result = aggregate_history([self.analyze([event("a", "Starting XI", tactics={"formation": 433}),
                                                  event("b", "Starting XI", tactics={"formation": 442})])])
        self.assertEqual(result["matches_with_initial_formation"], 0)
        self.assertEqual(result["initial_formations"], [])

    def test_empty_and_duplicate_roster_do_not_create_participants(self):
        self.assertEqual(aggregate_history([])["players"], [])
        duplicate = [{"team_id": 1, "lineup": [{"player_id": 7, "player_name": "A"}, {"player_id": 7, "player_name": "B"}]}]
        self.assertEqual(self.analyze([event("a")], duplicate)["players"], [])

    def test_excludes_extra_periods_and_invalid_movement_payload(self):
        row = self.analyze([event("a", period=3), event("b", **{"pass": None})])
        self.assertEqual(row["players"], [])
        self.assertEqual(row["quality"]["invalid_movement_payload"], 1)


if __name__ == "__main__":
    unittest.main()
