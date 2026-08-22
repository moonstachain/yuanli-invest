import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QXMF = ROOT / "docs" / "architecture" / "qxm-f" / "g1"
ACCEPT = QXMF / "QXM-F-G1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
THEORY_PACK = ROOT / "registry" / "theories" / "qxm-f-financial-mechanics-v0.1.json"
HYP_PACK = ROOT / "registry" / "hypotheses" / "qxm-f-financial-mechanics-v0.1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class QXMFG1ApplyTests(unittest.TestCase):
    def test_acceptance_receipt_freezes_exact_dispositions(self):
        receipt = load(ACCEPT)
        self.assertEqual(receipt["decision"], "ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION")
        dispositions = receipt["accepted_dispositions"]
        self.assertEqual(len(dispositions), 30)
        self.assertEqual(sum(v == "ADMIT_WITH_BOUNDARY" for v in dispositions.values()), 23)
        self.assertEqual(dispositions["HYP-V-202-OOS-DISCOUNT-RATE"], "KEEP_SHADOW")
        self.assertEqual(sum(v == "FORMALIZE" for v in dispositions.values()), 6)
        self.assertFalse(receipt["boundaries_preserved"]["merge_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["hypothesis_preregistration_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["benchmark_execution_authorized"])

    def test_registry_delta_equals_human_accepted_dispositions(self):
        receipt = load(ACCEPT)
        dispositions = receipt["accepted_dispositions"]
        expected_theories = {k for k, v in dispositions.items() if k.startswith("THEORY-") and v in {"ADMIT", "ADMIT_WITH_BOUNDARY"}}
        expected_hypotheses = {k for k, v in dispositions.items() if k.startswith("HYP-") and v in {"ADMIT", "ADMIT_WITH_BOUNDARY"}}
        self.assertTrue(THEORY_PACK.exists(), "RED: accepted G1 theory Registry pack not materialized")
        self.assertTrue(HYP_PACK.exists(), "RED: accepted G1 hypothesis Registry pack not materialized")
        theories = load(THEORY_PACK)
        hypotheses = load(HYP_PACK)
        self.assertEqual({o["theory_id"] for o in theories["objects"]}, expected_theories)
        self.assertEqual({o["hypothesis_id"] for o in hypotheses["objects"]}, expected_hypotheses)
        self.assertEqual(theories["entry_count"], 12)
        self.assertEqual(hypotheses["entry_count"], 11)
        self.assertTrue(all(o["status"] == "proposed" for o in hypotheses["objects"]))
        self.assertNotIn("HYP-V-202-OOS-DISCOUNT-RATE", {o["hypothesis_id"] for o in hypotheses["objects"]})

    def test_registry_indices_close_exact_delta(self):
        theory_index = load(ROOT / "registry" / "theories" / "_index.json")
        hyp_index = load(ROOT / "registry" / "hypotheses" / "_index.json")
        global_index = load(ROOT / "registry" / "registry-index.json")
        self.assertIn("qxm-f-financial-mechanics-v0.1.json", theory_index["pack_files"])
        self.assertIn("qxm-f-financial-mechanics-v0.1.json", hyp_index["pack_files"])
        self.assertEqual(theory_index["entry_count"], 31)
        self.assertEqual(hyp_index["entry_count"], 23)
        self.assertEqual(global_index["entry_count_total"], 122)


if __name__ == "__main__":
    unittest.main()
