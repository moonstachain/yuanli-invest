from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
ME1 = ROOT / "docs" / "architecture" / "me1"


class ME1AcceptanceTests(unittest.TestCase):
    def test_human_acceptance_receipt_matches_state(self):
        receipt = json.loads((ME1 / "ME1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json").read_text(encoding="utf-8"))
        state = json.loads((ME1 / "ME1-STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["decision"], "ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME")
        self.assertEqual(receipt["reviewed_head_sha"], "dc2c41b4499871336aafc62100a126ce8cab1475")
        self.assertEqual(receipt["reviewed_ci"]["run_number"], 353)
        self.assertEqual(receipt["formal_review"], "13/13 PASS")
        self.assertEqual(state["human_acceptance"], receipt["decision"])
        self.assertEqual(state["status"], "human_accepted_ready_for_merge_authorization")
        self.assertEqual(state["next_gate"], "ME1_MERGE_AUTHORIZATION")
        self.assertEqual(state["post_acceptance_qualification"]["validated_head_sha"], "bec2adcd58dbdfbfa9ee5ec3be062737ccafe795")
        self.assertEqual(state["post_acceptance_qualification"]["run_number"], 357)
        self.assertEqual(state["post_acceptance_qualification"]["contracts"], "success")
        self.assertEqual(state["post_acceptance_qualification"]["governance"], "success")

    def test_acceptance_does_not_grant_merge_or_successor_authority(self):
        receipt = json.loads((ME1 / "ME1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json").read_text(encoding="utf-8"))
        state = json.loads((ME1 / "ME1-STATE.json").read_text(encoding="utf-8"))
        self.assertFalse(receipt["boundaries_preserved"]["merge_authorized"])
        self.assertEqual(receipt["merge_authority"], "not_implied_by_acceptance")
        self.assertEqual(receipt["required_merge_token"], "AUTHORIZE_ME1_MERGE")
        self.assertFalse(state["merge_authorized"])
        self.assertFalse(state["next_me_stage_authorized"])
        self.assertEqual(state["migration"]["M3_authority_cutover"], "not_authorized")
        for key, value in state["implementation_authorities"].items():
            self.assertFalse(value, key)

    def test_acceptance_preserves_core_semantics(self):
        receipt = json.loads((ME1 / "ME1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json").read_text(encoding="utf-8"))
        accepted = receipt["accepted_decisions"]
        self.assertEqual(accepted["canonical_chain"], "ResearchTarget v2 -> EngineThesis[0..N] -> PositionPassport[0..N] -> BookState@PIT")
        self.assertTrue(accepted["research_target_v1_preserved"])
        self.assertTrue(accepted["research_target_v2_is_semantic_successor"])
        self.assertTrue(accepted["book_membership_is_passport_specific"])
        self.assertTrue(accepted["primary_engine_immutable_within_thesis_identity"])
        self.assertTrue(accepted["no_silent_thesis_migration"])
        self.assertFalse(accepted["settlement_rewrites_history"])
        self.assertFalse(accepted["legacy_rsv_future_write_authority"])
        self.assertTrue(accepted["legacy_write_back_prohibited"])
        self.assertTrue(accepted["legacy_rsv_auto_thesis_creation_prohibited"])
        self.assertFalse(accepted["engine_namespace_closed_world"])
        self.assertTrue(accepted["engine_resolution_fail_closed"])


if __name__ == "__main__":
    unittest.main()
