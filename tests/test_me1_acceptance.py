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
        self.assertIn(state["status"], {"human_accepted_ready_for_merge_authorization", "human_accepted_merged_pending_post_merge_ci", "human_accepted_merged"})
        self.assertEqual(state["post_acceptance_qualification"]["validated_head_sha"], "bec2adcd58dbdfbfa9ee5ec3be062737ccafe795")
        self.assertEqual(state["post_acceptance_qualification"]["run_number"], 357)
        self.assertEqual(state["post_acceptance_qualification"]["contracts"], "success")
        self.assertEqual(state["post_acceptance_qualification"]["governance"], "success")

    def test_acceptance_does_not_grant_successor_authority(self):
        receipt = json.loads((ME1 / "ME1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json").read_text(encoding="utf-8"))
        state = json.loads((ME1 / "ME1-STATE.json").read_text(encoding="utf-8"))
        self.assertFalse(receipt["boundaries_preserved"]["merge_authorized"])
        self.assertEqual(receipt["merge_authority"], "not_implied_by_acceptance")
        self.assertEqual(receipt["required_merge_token"], "AUTHORIZE_ME1_MERGE")
        self.assertFalse(state["next_me_stage_authorized"])
        self.assertEqual(state["migration"]["M3_authority_cutover"], "not_authorized")
        for key, value in state["implementation_authorities"].items():
            self.assertFalse(value, key)

    def test_merge_receipt_matches_merged_state_when_present(self):
        path = ME1 / "ME1-MERGE-RECEIPT-v0.1.json"
        if not path.exists():
            self.skipTest("merge receipt not present before merge authorization")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        state = json.loads((ME1 / "ME1-STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["decision"], "AUTHORIZE_ME1_MERGE")
        self.assertEqual(receipt["pr_number"], 50)
        self.assertEqual(receipt["merge_method"], "squash")
        self.assertEqual(receipt["accepted_head_sha"], "c6385a6697cd85fc786f0266d257ca82b45818a1")
        self.assertEqual(receipt["pre_merge_ci"]["run_number"], 362)
        self.assertEqual(receipt["pre_merge_ci"]["conclusion"], "success")
        self.assertEqual(receipt["merge_commit"], "6f1e028831100f3e32575a8f6e5869e727d19271")
        self.assertEqual(state["merge_authority"], receipt["merge_authorization_token"])
        self.assertEqual(state["merge_commit"], receipt["merge_commit"])
        self.assertIn(state["status"], {"human_accepted_merged_pending_post_merge_ci", "human_accepted_merged"})
        self.assertTrue(state["post_merge_ci_required"])
        self.assertFalse(state["next_me_stage_authorized"])
        self.assertTrue(all(value is False for value in receipt["boundaries_preserved"].values()))

    def test_completion_receipt_matches_completed_state_when_present(self):
        path = ME1 / "ME1-COMPLETION-RECEIPT-v0.1.json"
        if not path.exists():
            self.skipTest("completion receipt not present before post-merge qualification")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        state = json.loads((ME1 / "ME1-STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["decision"], "ME1_COMPLETE")
        self.assertEqual(receipt["post_merge_qualification"]["validated_main_head_sha"], "46c985154238f3abd93c2d61e4892134f14ffc5a")
        self.assertEqual(receipt["post_merge_qualification"]["contracts"], "success")
        self.assertEqual(receipt["post_merge_qualification"]["governance"], "success")
        self.assertEqual(state["status"], "human_accepted_merged")
        self.assertTrue(state["post_merge_ci_satisfied"])
        self.assertEqual(state["next_gate"], "ME1_COMPLETE")
        self.assertFalse(state["next_me_stage_authorized"])
        self.assertTrue(all(value is False for value in receipt["boundaries_preserved"].values()))

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
