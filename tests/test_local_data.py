"""Integração opt-in com JSONs reais locais; não baixa nem modifica dados."""
from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from managerai.data_inventory import inventory
from managerai.data_loader import LocalData
from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest


ROOT = Path(__file__).resolve().parents[1] / "open-data" / "data"


@unittest.skipUnless(os.environ.get("MANAGERAI_RUN_LOCAL_TESTS") == "1", "Integração local opcional: defina MANAGERAI_RUN_LOCAL_TESTS=1")
class LocalDataIntegrationTests(unittest.TestCase):
    def test_inventory_and_historical_report(self):
        self.assertTrue((ROOT / "competitions.json").is_file(), "Dataset local não encontrado.")
        inv = inventory(LocalData(ROOT))
        recorte = next(s for s in inv["seasons"] if (s["competition_id"], s["season_id"]) == (2, 27))
        self.assertEqual(recorte["matches"], 380)
        self.assertEqual(len(recorte["teams"]), 20)
        self.assertEqual(recorte["coverage"], {"events": 380, "lineups": 380, "three-sixty": 0})
        request = AnalysisRequest(2, 27, 36, 1, target_match_id=3754314)
        first = analyze(ROOT, request)
        # Frozen V1 artifact: all values, source hashes, rules and schema must match.
        reference = ROOT.parents[1] / "outputs/mvp_demo_city_arsenal/report.json"
        self.assertEqual(first.to_json(), reference.read_text(encoding="utf-8"))
        self.assertEqual(first.to_json(), analyze(ROOT, request).to_json())
        self.assertGreaterEqual(len(first.key_findings), 2)
        self.assertGreaterEqual(len(first.tactical_hypotheses), 2)
        for profile in (first.team_profile, first.opponent_profile):
            self.assertEqual(len(profile.match_ids), 10)
            self.assertNotIn(3754314, profile.match_ids)
            self.assertLess(profile.period_end, "2016-05-08")
            # Independent direct sum of raw shots checks attribution/aggregation.
            match_xg = []
            for mid in profile.match_ids:
                ev = json.loads((ROOT / "events" / f"{mid}.json").read_text())
                match_xg.append(sum(e["shot"]["statsbomb_xg"] for e in ev if e["type"]["name"] == "Shot" and e["team"]["id"] == profile.team_id and e["period"] in (1, 2)))
            self.assertAlmostEqual(profile.metrics["xg_for"].value, sum(match_xg)/len(match_xg))
        first_day = analyze(ROOT, AnalysisRequest(2, 27, 36, 1, cutoff_date="2015-08-08"))
        self.assertEqual(first_day.team_profile.match_ids, [])
        self.assertEqual(first_day.tactical_hypotheses, [])


if __name__ == "__main__":
    unittest.main()
