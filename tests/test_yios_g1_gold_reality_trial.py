from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validate_yios_g1_gold_reality_trial import validate_yios_g1_gold_reality_trial

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = ROOT / "config" / "yios_g1" / "gold_genesis_case_constitution.v1.json"
RESULT = ROOT / "config" / "yios_g1" / "gold_g1_reality_trial.v1.json"
T0_STATE = ROOT / "config" / "yios_g1" / "gold_state_t0.v1.json"


class TestYIOSG1GoldRealityTrial(unittest.TestCase):
    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_validator_passes(self):
        validate_yios_g1_gold_reality_trial()

    def test_constitution_remains_frozen(self):
        c = self.load_json(CONSTITUTION)
        self.assertEqual(c["two_clock_law"]["historical_t0"], "2024-01-31T23:59:59-05:00")
        self.assertEqual(c["primary_claim"]["claim_id"], "GOLD_EARLY_MONETARY_REGIME_REPRICING")
        self.assertFalse(c["primary_settlement_law"]["price_up_alone_can_pass"])

    def test_t0_state_has_no_future_leakage(self):
        s = self.load_json(T0_STATE)
        self.assertEqual(s["known_as_of"], "2024-01-31T23:59:59-05:00")
        self.assertEqual(s["future_leakage_count"], 0)
        self.assertNotIn("2025", json.dumps(s))
        self.assertNotIn("2026", json.dumps(s))

    def test_research_settlement_is_fail_closed_on_decisive_unknown(self):
        r = self.load_json(RESULT)
        self.assertEqual(r["hypothesis_results"]["H2_TRADITIONAL_MACRO_DECOUPLING"]["status"], "SUPPORTED")
        self.assertEqual(r["hypothesis_results"]["H3_PRICE_CONFIRMATION"]["status"], "SUPPORTED")
        self.assertEqual(r["hypothesis_results"]["H1_OFFICIAL_DEMAND_STRUCTURAL"]["status"], "INDETERMINATE")
        self.assertEqual(r["primary_research_settlement_candidate"], "INDETERMINATE")
        self.assertEqual(r["authority_state"], "RESEARCH_SETTLEMENT_CANDIDATE_ONLY")

    def test_no_capital_or_execution_authority(self):
        r = self.load_json(RESULT)
        for value in r["non_authorizations"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
