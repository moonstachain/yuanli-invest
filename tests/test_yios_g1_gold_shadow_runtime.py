from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validate_yios_g1_gold_shadow_runtime import validate_yios_g1_gold_shadow_runtime

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "config" / "yios_g1" / "gold_g4_shadow_runtime_settlement.v1.json"
RECEIPT = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G4-RUNTIME-SETTLEMENT-RECEIPT-v1.0.json"


class TestYIOSG1GoldShadowRuntime(unittest.TestCase):
    def test_validator_passes(self):
        validate_yios_g1_gold_shadow_runtime()

    def test_indeterminate_research_fails_closed_at_capital_boundary(self):
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        self.assertEqual(runtime["research_input"]["primary_settlement"], "INDETERMINATE")
        self.assertEqual(runtime["capital_admission"]["decision"], "DENY")
        self.assertEqual(runtime["capital_admission"]["max_notional"], 0)
        self.assertEqual(runtime["capital_admission"]["max_loss"], 0)

    def test_runtime_is_shadow_only_and_emits_no_order_or_fill(self):
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        self.assertEqual(runtime["execution_runtime"]["mode"], "SHADOW")
        self.assertEqual(runtime["execution_runtime"]["quantity_delta"], 0)
        self.assertEqual(runtime["execution_runtime"]["max_notional"], 0)
        event_types = [event["event_type"] for event in runtime["execution_runtime"]["events"]]
        for forbidden in ("OrderSubmitted", "OrderAccepted", "PartialFillReceived", "FillReceived"):
            self.assertNotIn(forbidden, event_types)
        self.assertIn("ExecutionFailureObserved", event_types)

    def test_four_way_reconciliation_is_complete_without_external_execution(self):
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        recon = runtime["execution_settlement"]["reconciliation"]
        self.assertEqual(set(recon), {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"})
        self.assertEqual(recon["capital_intent"]["status"], "MATCHED")
        self.assertEqual(recon["yuanli_execution"]["status"], "SIMULATED_MATCH")
        self.assertEqual(recon["execution_engine_oms"]["status"], "NOT_APPLICABLE")
        self.assertEqual(recon["broker_custodian"]["status"], "NOT_APPLICABLE")
        self.assertEqual(runtime["execution_settlement"]["status"], "FAIL_CLOSED")

    def test_authority_firewall_remains_zero(self):
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        authority = runtime["authority"]
        for key in (
            "portfolio_weight_authority",
            "position_sizing_authority",
            "capital_movement_authority",
            "trade_execution_authority",
            "live_execution_authority",
            "broker_authority",
            "veighna_invocation_authority",
            "automatic_research_to_execution_authority",
        ):
            self.assertFalse(authority[key], key)

    def test_settlement_receipt_records_denial_as_learning_not_trade_signal(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["runtime_outcome"], "FAIL_CLOSED_VALID")
        self.assertEqual(receipt["learning_outcome"], "DENIAL_IS_VALID_EXECUTION_OUTCOME")
        self.assertFalse(receipt["authority_changes"]["capital_authority_granted"])
        self.assertFalse(receipt["authority_changes"]["execution_authority_granted"])
        self.assertFalse(receipt["authority_changes"]["real_capital_authority_granted"])


if __name__ == "__main__":
    unittest.main()
