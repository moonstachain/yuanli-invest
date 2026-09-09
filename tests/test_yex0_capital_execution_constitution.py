from pathlib import Path
import copy
import json
import unittest

from scripts import validate_yex0_capital_execution_constitution as yex0

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages/contracts/schemas/vnext"
CONFIG = ROOT / "config/yex0/yex0_constitution.v0.1.json"
ACCEPTANCE = ROOT / "docs/architecture/yex0/YEX0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"


class YEX0SchemaTests(unittest.TestCase):
    def load_schema(self, name):
        return json.loads((VNEXT / name).read_text(encoding="utf-8"))

    def test_five_yex0_schemas_exist(self):
        for name in (
            "capital-admission.schema.json",
            "execution-intent.schema.json",
            "action-contract.schema.json",
            "execution-event.schema.json",
            "execution-settlement.schema.json",
        ):
            self.assertTrue((VNEXT / name).exists(), name)

    def test_position_passport_still_has_zero_execution_authority(self):
        schema = self.load_schema("position-passport.schema.json")
        authority = schema["properties"]["authority"]["properties"]
        self.assertEqual(authority["portfolio_weight_authority"]["const"], False)
        self.assertEqual(authority["position_sizing_authority"]["const"], False)
        self.assertEqual(authority["trade_execution_authority"]["const"], False)
        self.assertEqual(authority["live_execution_authority"]["const"], False)

    def test_capital_admission_cannot_execute(self):
        schema = self.load_schema("capital-admission.schema.json")
        auth = schema["properties"]["authority"]["properties"]
        self.assertEqual(auth["order_submission_authority"]["const"], False)
        self.assertEqual(auth["live_execution_authority"]["const"], False)
        self.assertEqual(auth["real_capital_movement_authority"]["const"], False)

    def test_execution_intent_cannot_self_authorize(self):
        schema = self.load_schema("execution-intent.schema.json")
        self.assertEqual(schema["properties"]["self_execution_authorized"]["const"], False)

    def test_action_contract_is_non_live(self):
        schema = self.load_schema("action-contract.schema.json")
        props = schema["properties"]
        self.assertEqual(set(props["execution_mode"]["enum"]), {"shadow", "broker_paper"})
        self.assertEqual(props["live_execution_authorized"]["const"], False)
        self.assertEqual(props["real_capital_movement_authorized"]["const"], False)

    def test_execution_event_is_append_only_and_hash_chained(self):
        schema = self.load_schema("execution-event.schema.json")
        props = schema["properties"]
        self.assertEqual(props["append_only"]["const"], True)
        self.assertIn("previous_event_hash", props)
        self.assertIn("event_hash", props)
        self.assertIn("idempotency_key", props)

    def test_execution_settlement_requires_four_way_reconciliation(self):
        schema = self.load_schema("execution-settlement.schema.json")
        reconciliation = schema["properties"]["reconciliation"]
        self.assertEqual(
            set(reconciliation["required"]),
            {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"},
        )
        self.assertIn("research_outcome_ref", schema["properties"])
        self.assertIn("execution_quality", schema["properties"])

    def test_constitution_freezes_unknown_as_deny_and_three_authorities(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["firewall"]["unknown_semantics"], "DENY")
        self.assertEqual(
            config["authority_separation"],
            ["ResearchAuthority", "CapitalAuthority", "ExecutionAuthority"],
        )


class YEX0RelationalTests(unittest.TestCase):
    def bundle(self):
        return yex0.load_fixture_bundle()

    def assert_rejected(self, fn, bundle):
        with self.assertRaises(ValueError):
            fn(bundle)

    def test_positive_fixture_bundle_is_valid(self):
        yex0.validate_bundle(self.bundle())

    def test_live_action_contract_is_rejected(self):
        b = self.bundle()
        b["action_contract"]["live_execution_authorized"] = True
        self.assert_rejected(yex0.validate_authority_integrity, b)

    def test_real_capital_movement_is_rejected(self):
        b = self.bundle()
        b["action_contract"]["real_capital_movement_authorized"] = True
        self.assert_rejected(yex0.validate_authority_integrity, b)

    def test_scope_expansion_is_rejected(self):
        b = self.bundle()
        b["action_contract"]["scope"]["max_notional"] = b["execution_intent"]["limits"]["max_notional"] + 1
        self.assert_rejected(yex0.validate_scope_integrity, b)

    def test_expired_contract_is_rejected(self):
        b = self.bundle()
        b["action_contract"]["expires_at"] = b["action_contract"]["issued_at"]
        self.assert_rejected(yex0.validate_time_integrity, b)

    def test_reference_mismatch_is_rejected(self):
        b = self.bundle()
        b["action_contract"]["execution_intent_id"] = "EI-MISMATCH"
        self.assert_rejected(yex0.validate_reference_integrity, b)

    def test_incomplete_four_way_reconciliation_is_rejected(self):
        b = self.bundle()
        del b["execution_settlement"]["reconciliation"]["broker_custodian"]
        self.assert_rejected(yex0.validate_reconciliation_integrity, b)

    def test_unexplained_external_order_is_rejected(self):
        b = self.bundle()
        b["execution_settlement"]["drift"]["unknown_external_orders"] = 1
        self.assert_rejected(yex0.validate_reconciliation_integrity, b)

    def test_event_hash_chain_break_is_rejected(self):
        b = self.bundle()
        b["execution_events"][1]["previous_event_hash"] = "sha256:" + "f" * 64
        self.assert_rejected(yex0.validate_ledger_integrity, b)

    def test_projection_cannot_be_declared_truth(self):
        b = self.bundle()
        b["execution_settlement"]["projection_is_truth"] = True
        self.assert_rejected(yex0.validate_ledger_integrity, b)


class YEX0HumanAcceptanceTests(unittest.TestCase):
    def test_acceptance_receipt_is_machine_checked(self):
        self.assertTrue(ACCEPTANCE.exists())
        yex0.validate_human_acceptance()

    def test_acceptance_does_not_imply_merge_or_yvn1(self):
        receipt = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        self.assertEqual(receipt["decision"], "ACCEPT_YEX0_CAPITAL_EXECUTION_CONSTITUTION")
        self.assertEqual(receipt["reviewed_head_sha"], "8767005c8a78f5426cfcadc3fb643a221132d96b")
        self.assertFalse(receipt["boundaries_preserved"]["merge_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["yvn1_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["broker_paper_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["live_execution_authorized"])
        self.assertEqual(receipt["required_merge_token"], "AUTHORIZE_YEX0_MERGE")


if __name__ == "__main__":
    unittest.main()
