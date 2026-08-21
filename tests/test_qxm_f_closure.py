import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"
G1_LEDGER = ROOT / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-ADMISSION-LEDGER-v0.1.json"
G1_ACCEPTANCE = ROOT / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
G1_ADMISSION_RECEIPT = ROOT / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-ADMISSION-RECEIPT-v0.1.json"
G1_THEORY_PACK = ROOT / "registry" / "theories" / "qxm-f-financial-mechanics-v0.1.json"
G1_HYPOTHESIS_PACK = ROOT / "registry" / "hypotheses" / "qxm-f-financial-mechanics-v0.1.json"
THEORY_INDEX = ROOT / "registry" / "theories" / "_index.json"
HYPOTHESIS_INDEX = ROOT / "registry" / "hypotheses" / "_index.json"
BENCHMARK_INDEX = ROOT / "registry" / "benchmarks" / "_index.json"
REGISTRY_INDEX = ROOT / "registry" / "registry-index.json"
QXM2_EVIDENCE = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json"
QXM2_STATE = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-STATE.json"
QXM2_COUNT_RECONCILIATION = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-EVIDENCE-COUNT-RECONCILIATION-v0.1.json"

EXPECTED_G1_THEORY_IDS = {
    "THEORY-LEVTHIAGARAJAN-1993-FUNDAMENTAL-INFORMATION",
    "THEORY-NISSIMPENMAN-2001-RATIO-HIERARCHY",
    "THEORY-DECHOW-1994-ACCRUAL-MATCHING",
    "THEORY-SLOAN-1996-ACCRUAL-CASH-PERSISTENCE",
    "THEORY-BERNANKEGERTLER-1989-NET-WORTH-AGENCY-COST",
    "THEORY-KIYOTAKIMOORE-1997-COLLATERAL-CREDIT-CYCLES",
    "THEORY-SHARPE-1964-CAPITAL-ASSET-PRICES",
    "THEORY-CAMPBELLSHILLER-1988-PRESENT-VALUE-DECOMPOSITION",
    "THEORY-KYLE-1985-MARKET-DEPTH",
    "THEORY-BRUNNERMEIERPEDERSEN-2009-MARKET-FUNDING-LIQUIDITY",
    "THEORY-BRINSONHOODBEEBOWER-1986-PORTFOLIO-ATTRIBUTION",
    "THEORY-CAMPBELL-1991-RETURN-NEWS-DECOMPOSITION",
}

EXPECTED_G1_HYPOTHESIS_IDS = {
    "HYP-P-201-DRIVER-INCREMENTAL-OOS",
    "HYP-P-202-DRIVER-REGIME-STABILITY",
    "HYP-P-203-CASH-CONVERSION-PERSISTENCE",
    "HYP-P-204-ACCRUAL-RELIABILITY",
    "HYP-P-205-CREDIT-SECTORAL-TRANSMISSION",
    "HYP-P-206-COLLATERAL-FEEDBACK",
    "HYP-V-201-EXPECTATION-DECOMPOSITION",
    "HYP-S-201-STRESS-LIQUIDITY-INCREMENTAL",
    "HYP-S-202-FUNDING-LIQUIDITY-SPIRAL",
    "HYP-CROSS-201-RETURN-IDENTITY-RECONSTRUCTION",
    "HYP-CROSS-202-THESIS-FIDELITY",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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

    def test_qxm2_stale_evidence_count_requires_explicit_reconciliation(self):
        evidence = load_json(QXM2_EVIDENCE)
        state = load_json(QXM2_STATE)
        actual = len(evidence["relations"])
        declared = evidence["relation_count"]
        if declared != actual:
            self.assertTrue(QXM2_COUNT_RECONCILIATION.exists(), "stale QXM2 relation_count requires immutable reconciliation receipt")
            receipt = load_json(QXM2_COUNT_RECONCILIATION)
            self.assertEqual(receipt["stale_declared_relation_count"], declared)
            self.assertEqual(receipt["actual_relation_array_count"], actual)
            self.assertEqual(receipt["corrected_authoritative_relation_count"], actual)
            self.assertEqual(state["evidence_compilation"]["relation_count"], actual)
            self.assertEqual(state["evidence_compilation"]["count_reconciliation_receipt"], "docs/architecture/qxm2/QXM2-EVIDENCE-COUNT-RECONCILIATION-v0.1.json")


class QXMFG1AdmissionLedgerTests(unittest.TestCase):
    def test_g1_ledger_has_exact_30_source_objects(self):
        self.assertTrue(G1_LEDGER.exists(), "G1 admission ledger must exist")
        ledger = load_json(G1_LEDGER)
        rows = ledger["objects"]
        self.assertEqual(len(rows), 30)
        self.assertEqual(sum(r["object_class"] == "TheoryObject" for r in rows), 12)
        self.assertEqual(sum(r["object_class"] == "HypothesisObject" for r in rows), 12)
        self.assertEqual(sum(r["object_class"] == "BenchmarkSeed" for r in rows), 6)
        for row in rows:
            self.assertTrue(row["recommended_disposition"], row["source_shadow_id"])

    def test_g1_closed_disposition_enums_and_discount_rate_boundary(self):
        rows = load_json(G1_LEDGER)["objects"]
        theory_hyp_legal = {"ADMIT", "ADMIT_WITH_BOUNDARY", "KEEP_SHADOW", "REJECT"}
        seed_legal = {"FORMALIZE", "DEFER", "REJECT"}
        for row in rows:
            legal = seed_legal if row["object_class"] == "BenchmarkSeed" else theory_hyp_legal
            self.assertIn(row["recommended_disposition"], legal, row["source_shadow_id"])
            if row["candidate_id"] == "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE":
                self.assertFalse(row["predictive_or_timing_authority_requested"], row["source_shadow_id"])

    def test_human_acceptance_freezes_recommended_dispositions_without_authority_escalation(self):
        self.assertTrue(G1_ACCEPTANCE.exists(), "Human Acceptance receipt must precede Registry writes")
        acceptance = load_json(G1_ACCEPTANCE)
        self.assertEqual(acceptance["decision"], "ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION")
        rows = load_json(G1_LEDGER)["objects"]
        for row in rows:
            self.assertEqual(row["human_disposition"], row["recommended_disposition"], row["source_shadow_id"])
        self.assertFalse(acceptance["boundaries_preserved"]["benchmark_execution_authorized"])
        self.assertFalse(acceptance["boundaries_preserved"]["capability_promotion_authorized"])
        self.assertFalse(acceptance["boundaries_preserved"]["trading_action_authorized"])

    def test_g1_registry_delta_equals_human_accepted_ledger(self):
        self.assertTrue(G1_THEORY_PACK.exists(), "accepted TheoryObjects must be materialized")
        self.assertTrue(G1_HYPOTHESIS_PACK.exists(), "accepted proposed HypothesisObjects must be materialized")
        theories = load_json(G1_THEORY_PACK)
        hypotheses = load_json(G1_HYPOTHESIS_PACK)
        theory_ids = {obj["theory_id"] for obj in theories["objects"]}
        hyp_ids = {obj["hypothesis_id"] for obj in hypotheses["objects"]}
        self.assertEqual(theory_ids, EXPECTED_G1_THEORY_IDS)
        self.assertEqual(hyp_ids, EXPECTED_G1_HYPOTHESIS_IDS)
        self.assertNotIn("HYP-V-202-OOS-DISCOUNT-RATE", hyp_ids)
        self.assertTrue(all(obj["status"] == "proposed" for obj in hypotheses["objects"]))

    def test_g1_registry_counts_are_deterministic_and_benchmark_registry_is_unchanged(self):
        theory_index = load_json(THEORY_INDEX)
        hypothesis_index = load_json(HYPOTHESIS_INDEX)
        benchmark_index = load_json(BENCHMARK_INDEX)
        registry_index = load_json(REGISTRY_INDEX)
        self.assertEqual(theory_index["entry_count"], 31)
        self.assertEqual(hypothesis_index["entry_count"], 23)
        self.assertEqual(benchmark_index["entry_count"], 7)
        self.assertEqual(registry_index["entry_count_total"], 122)
        self.assertEqual(
            registry_index["entry_count_total"],
            sum(item["entry_count"] for item in registry_index["registries"]),
        )

    def test_g1_admission_receipt_records_identity_only_admission_and_stops_before_merge(self):
        self.assertTrue(G1_ADMISSION_RECEIPT.exists(), "G1 admission receipt must record the accepted Registry delta")
        receipt = load_json(G1_ADMISSION_RECEIPT)
        self.assertEqual(receipt["theory_admitted_count"], 12)
        self.assertEqual(receipt["hypothesis_admitted_count"], 11)
        self.assertEqual(receipt["benchmark_formalized_count"], 0)
        self.assertEqual(receipt["kept_shadow_hypothesis_ids"], ["HYP-V-202-OOS-DISCOUNT-RATE"])
        self.assertEqual(receipt["required_merge_token"], "AUTHORIZE_QXM_F_G1_MERGE")
        self.assertFalse(receipt["boundaries_preserved"]["benchmark_execution_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["production_runtime_authorized"])
        self.assertFalse(receipt["boundaries_preserved"]["trading_action_authorized"])


if __name__ == "__main__":
    unittest.main()
