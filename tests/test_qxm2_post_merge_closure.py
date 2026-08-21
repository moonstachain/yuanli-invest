import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QXM2 = ROOT / "docs" / "architecture" / "qxm2"


class QXM2PostMergeClosureTests(unittest.TestCase):
    def test_semantic_merge_must_be_closed_with_receipt_and_projection(self):
        receipt_path = QXM2 / "QXM2-MERGE-RECEIPT-v0.1.json"
        self.assertTrue(receipt_path.exists(), "semantic merge requires QXM2 merge receipt")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        state = json.loads((QXM2 / "QXM2-STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "accepted_merged")
        self.assertEqual(state["merge_authority"], "AUTHORIZE_QXM2_MERGE")
        self.assertEqual(state["merge_commit"], "e1b7a65736c6f93089d7e635e5c72624345941fc")
        self.assertEqual(state["merge_receipt"], "docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json")
        self.assertEqual(state["next_gate"], "QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION")
        self.assertEqual(state["qxm_f_next_gate"], "QXM_F_G1_SELECTIVE_ADMISSION")
        self.assertEqual(receipt["merge_authority"], "AUTHORIZE_QXM2_MERGE")
        self.assertEqual(receipt["semantic_merge_commit"], "e1b7a65736c6f93089d7e635e5c72624345941fc")
        self.assertEqual(receipt["qxm_f_next_gate"], "QXM_F_G1_SELECTIVE_ADMISSION")
        self.assertFalse(receipt["registry_admission_authorized"])
        self.assertFalse(receipt["hypothesis_preregistration_authorized"])
        self.assertFalse(receipt["formal_benchmark_creation_authorized"])
        self.assertFalse(receipt["benchmark_execution_authorized"])
        self.assertFalse(receipt["capability_promotion_authorized"])
        self.assertFalse(receipt["production_runtime_authorized"])
        self.assertFalse(receipt["trading_action_authorized"])


if __name__ == "__main__":
    unittest.main()
