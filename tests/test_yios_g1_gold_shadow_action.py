from pathlib import Path
import json
import unittest

from scripts.validate_yios_g1_gold_shadow_action import validate_yios_g1_gold_shadow_action

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "config/yios_g1/gold_g3_shadow_action.v1.json"
PASSPORT = ROOT / "config/yios_g1/gold_g3_shadow_position_passport.v1.json"
LEARNING = ROOT / "docs/architecture/yios_g1/YIOS-G1-G3-LEARNING-RECEIPT-v1.0.json"


class TestYIOSG1GoldShadowAction(unittest.TestCase):
    def test_validator_passes(self):
        validate_yios_g1_gold_shadow_action()

    def test_unknown_deny_blocks_capital_and_orders(self):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        self.assertEqual(bundle["research_settlement"]["primary_settlement"], "INDETERMINATE")
        self.assertEqual(bundle["capital_admission"]["decision"], "deny")
        self.assertEqual(bundle["capital_admission"]["risk_budget"], {"max_notional": 0, "max_loss": 0})
        self.assertEqual(bundle["execution_intent"]["quantity_delta"], 0)
        self.assertEqual(bundle["action_contract"]["execution_mode"], "shadow")
        self.assertEqual(bundle["action_contract"]["scope"]["max_notional"], 0)
        event_types = [e["event_type"] for e in bundle["execution_events"]]
        self.assertNotIn("OrderSubmitted", event_types)
        self.assertNotIn("OrderAccepted", event_types)
        self.assertNotIn("PartialFillReceived", event_types)
        self.assertNotIn("FillReceived", event_types)
        self.assertIn("ExecutionFailureObserved", event_types)
        self.assertEqual(bundle["execution_settlement"]["status"], "FAIL_CLOSED")

    def test_shadow_passport_has_zero_authority(self):
        passport = json.loads(PASSPORT.read_text(encoding="utf-8"))
        self.assertEqual(passport["primary_engine"], "ENG-R")
        self.assertEqual(passport["lifecycle"]["status"], "cancelled")
        self.assertFalse(passport["authority"]["portfolio_weight_authority"])
        self.assertFalse(passport["authority"]["position_sizing_authority"])
        self.assertFalse(passport["authority"]["trade_execution_authority"])
        self.assertFalse(passport["authority"]["live_execution_authority"])

    def test_four_way_reconciliation_is_explicit(self):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        recon = bundle["execution_settlement"]["reconciliation"]
        self.assertEqual(set(recon), {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"})
        self.assertEqual(recon["capital_intent"]["status"], "MATCHED")
        self.assertEqual(recon["yuanli_execution"]["status"], "SIMULATED_MATCH")
        self.assertEqual(recon["execution_engine_oms"]["status"], "NOT_APPLICABLE")
        self.assertEqual(recon["broker_custodian"]["status"], "NOT_APPLICABLE")

    def test_learning_preserves_denial_as_valid_outcome(self):
        learning = json.loads(LEARNING.read_text(encoding="utf-8"))
        self.assertEqual(learning["learning_outcome"], "DENIAL_IS_VALID_EXECUTION_OUTCOME")
        self.assertFalse(learning["authority_changes"]["capital_authority_granted"])
        self.assertFalse(learning["authority_changes"]["execution_authority_granted"])
        self.assertFalse(learning["authority_changes"]["real_capital_authority_granted"])


if __name__ == "__main__":
    unittest.main()
