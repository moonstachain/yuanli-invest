import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"
G1_LEDGER = ROOT / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-ADMISSION-LEDGER-v0.1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


from scripts.validate_qxm_f_closure import (
    LEGAL_STATES,
    assert_no_authority_escalation,
    assert_state,
    validate_qxm_f,
)


class QXMFClosureBootstrapTests(unittest.TestCase):
    def test_state_enum_is_closed(self):
        for state in LEGAL_STATES:
            assert_state(state)
        with self.assertRaises(AssertionError):
            assert_state("G1_MAGIC_AUTO_ADMISSION")

    def test_trading_and_silent_authority_escalation_fail_closed(self):
        assert_no_authority_escalation({
            "registry_admission_authorized": False,
            "benchmark_execution_authorized": False,
            "trading_action_authorized": False,
        })
        with self.assertRaises(AssertionError):
            assert_no_authority_escalation({"trading_action_authorized": True})
        with self.assertRaises(AssertionError):
            assert_no_authority_escalation({"capability_promotion_authorized": True})

    def test_full_bootstrap_validates(self):
        result = validate_qxm_f(ROOT)
        self.assertEqual(result["stage"], "QXM_F_FINANCIAL_MECHANICS_CAPABILITY_CLOSURE")


class QXMFG1AdmissionLedgerTests(unittest.TestCase):
    def test_g1_ledger_has_exact_30_source_objects_and_no_human_decisions_yet(self):
        self.assertTrue(G1_LEDGER.exists(), "G1 admission ledger must exist before Human Review")
        ledger = json.loads(G1_LEDGER.read_text(encoding="utf-8"))
        rows = ledger["objects"]
        self.assertEqual(len(rows), 30)
        self.assertEqual(sum(r["object_class"] == "TheoryObject" for r in rows), 12)
        self.assertEqual(sum(r["object_class"] == "HypothesisObject" for r in rows), 12)
        self.assertEqual(sum(r["object_class"] == "BenchmarkSeed" for r in rows), 6)
        for row in rows:
            self.assertIsNone(row["human_disposition"], row["source_shadow_id"])
            self.assertTrue(row["recommended_disposition"], row["source_shadow_id"])

    def test_g1_closed_disposition_enums_and_discount_rate_boundary(self):
        self.assertTrue(G1_LEDGER.exists(), "G1 admission ledger must exist before Human Review")
        rows = json.loads(G1_LEDGER.read_text(encoding="utf-8"))["objects"]
        theory_hyp_legal = {"ADMIT", "ADMIT_WITH_BOUNDARY", "KEEP_SHADOW", "REJECT"}
        seed_legal = {"FORMALIZE", "DEFER", "REJECT"}
        for row in rows:
            legal = seed_legal if row["object_class"] == "BenchmarkSeed" else theory_hyp_legal
            self.assertIn(row["recommended_disposition"], legal, row["source_shadow_id"])
            if row["candidate_id"] == "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE":
                self.assertFalse(row["predictive_or_timing_authority_requested"], row["source_shadow_id"])


if __name__ == "__main__":
    unittest.main()
