import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "generated" / "bootstrap-exact-sha.json"


class BootstrapReceiptTests(unittest.TestCase):
    def test_exact_source_recomputes(self):
        subprocess.run([sys.executable, "scripts/verify_bootstrap_receipt.py"], cwd=ROOT, check=True)

    def test_transition_stops_before_activation(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["canon_transition"]["state"], "pending_registry_activation")
        self.assertEqual(receipt["canon_transition"]["current_operational_canon"], "moonstachain/quant-workspace")
        self.assertEqual(receipt["surfaces"]["research_admission"], "blocked_unassigned_evidence_reviewer")
        self.assertEqual(receipt["counts"]["approved_research_objects"], 0)


if __name__ == "__main__":
    unittest.main()
