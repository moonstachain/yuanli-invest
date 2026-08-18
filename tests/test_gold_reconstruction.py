import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "reconstructions" / "force-triangle"


class GoldReconstructionTests(unittest.TestCase):
    def load(self, name):
        return json.loads((RECON / name).read_text(encoding="utf-8"))

    def test_fail_closed_validator(self):
        subprocess.run(
            [sys.executable, "scripts/validate_gold_reconstruction.py"],
            cwd=ROOT,
            check=True,
        )

    def test_three_cases_and_candidate_classifications(self):
        pc = self.load("pc-internet-1995.v0.1.json")
        mobile = self.load("mobile-internet-2008.v0.1.json")
        ai = self.load("ai-2023.v0.1.json")
        self.assertEqual(pc["force"]["classification"], "unknown")
        self.assertEqual(mobile["force"]["classification"], "golden_extreme")
        self.assertEqual(ai["force"]["classification"], "unknown")
        for packet in (pc, mobile, ai):
            self.assertTrue(packet["outcome_locked"])
            self.assertEqual(packet["status"], "candidate_reconstruction")

    def test_ai_100m_user_claim_is_explicitly_post_t0(self):
        freeze = self.load("a5-evidence-freeze-v0.1.json")
        ai_case = next(case for case in freeze["cases"] if case["case_id"] == "FT-GR-AI-2023")
        source = next(source for source in ai_case["sources"] if source["source_id"] == "FTSRC-AI-004")
        self.assertEqual(source["eligibility"], "excluded_post_t0")
        self.assertGreater(source["published_at"], ai_case["t0"])
        ai = self.load("ai-2023.v0.1.json")
        self.assertNotIn("FTSRC-AI-004", ai["source_ids_used"])
        self.assertIn("FTSRC-AI-004", ai["source_ids_excluded_post_t0"])

    def test_a4_pre_registration_commit_is_immutable_anchor(self):
        freeze = self.load("a5-evidence-freeze-v0.1.json")
        self.assertEqual(
            freeze["pre_registration_commit"],
            "392e4230493f7e860360defdbda82c0c61c48285",
        )

    def test_no_outcome_or_trading_payloads(self):
        forbidden = {
            "outcome", "outcomes", "returns", "realized_return", "target_price",
            "position", "position_size", "trade_action", "future_financials",
        }
        for name in (
            "pc-internet-1995.v0.1.json",
            "mobile-internet-2008.v0.1.json",
            "ai-2023.v0.1.json",
        ):
            text = (RECON / name).read_text(encoding="utf-8")
            payload = json.loads(text)
            stack = [payload]
            keys = set()
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    keys.update(key.lower() for key in item)
                    stack.extend(item.values())
                elif isinstance(item, list):
                    stack.extend(item)
            self.assertTrue(forbidden.isdisjoint(keys), name)


if __name__ == "__main__":
    unittest.main()
