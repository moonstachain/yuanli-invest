import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import ymq_gold2_learning_live as learning
from scripts import invest

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "fixtures/ymq_gold2/demo-prior.json"
CURRENT = ROOT / "fixtures/ymq_gold2/demo-current.json"


class InvestCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "scripts.invest", *map(str, args)],
            cwd=ROOT, capture_output=True, text=True,
        )

    def test_offline_compare_reports_real_calculations(self):
        result = self.run_cli("compare", PRIOR, CURRENT, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        candidate = json.loads(result.stdout)
        self.assertAlmostEqual(candidate["delta"]["gold_price_pct"], 1.5)
        self.assertAlmostEqual(candidate["delta"]["real_rate_bps"], 12)
        self.assertEqual(candidate["settlement"]["directional_claim_score"], "NOT_SCORABLE")
        self.assertFalse(candidate["accepted_learning"])

    def test_empty_status_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "absent"
            result = self.run_cli("status", "--runtime-dir", root, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "NO_RECEIPT")
            self.assertFalse(root.exists())

    def test_status_only_displays_learning_for_current_receipt(self):
        prior = invest.read_object(PRIOR)
        current = invest.read_object(CURRENT)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            learning.write_receipt(prior, root)
            learning.write_receipt(current, root)
            learning.process_current_receipt(current, root)
            self.assertIn("learning", invest.read_status(root))
            learning.write_receipt({"status": "PROVIDER_FAIL_CLOSED", "as_of": "2026-09-18"}, root)
            result = invest.read_status(root)
            self.assertEqual(result["status"], "PROVIDER_FAIL_CLOSED")
            self.assertNotIn("learning", result)

    def test_corrupt_optional_learning_does_not_hide_current_observation(self):
        current = invest.read_object(CURRENT)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            learning.write_receipt(current, root)
            (root / "learning").mkdir()
            matching_source = {"current_sha256": learning.receipt_sha256(current)}
            for damaged in ("{", '{"source_receipts": null}', json.dumps({"source_receipts": matching_source, "delta": None})):
                with self.subTest(damaged=damaged):
                    (root / "learning/latest-learning.json").write_text(damaged)
                    result = self.run_cli("status", "--runtime-dir", root, "--json")
                    self.assertEqual(result.returncode, 0)
                    status = json.loads(result.stdout)
                    self.assertEqual(status["receipt"], current)
                    self.assertIn("learning_error", status)

    def test_invalid_input_is_an_actionable_error(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{")
            result = self.run_cli("compare", bad, CURRENT, "--json")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "ERROR")
            self.assertNotIn("Traceback", result.stderr)

    def test_future_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            bad = invest.read_object(CURRENT)
            bad["known_as_of_max"] = "2026-09-18"
            path = Path(td) / "future.json"
            path.write_text(json.dumps(bad))
            result = self.run_cli("compare", PRIOR, path, "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("future-dated", json.loads(result.stdout)["error"])


if __name__ == "__main__":
    unittest.main()
