import json
import unittest
from pathlib import Path

from scripts.validate_qxm2_evidence_hardening import (
    assert_benchmark_seed_authority,
    assert_evidence_role,
    assert_expected_candidate_ids,
    assert_replication_status,
    assert_shadow_hypothesis_state,
)

ROOT = Path(__file__).resolve().parents[1]
QXM2 = ROOT / "docs" / "architecture" / "qxm2"
SOURCE_MATRIX = QXM2 / "QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json"
EVIDENCE_MATRIX = QXM2 / "QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json"

EXPECTED = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]


class QXM2PrimitiveTests(unittest.TestCase):
    def test_candidate_identity_is_exact(self):
        assert_expected_candidate_ids(EXPECTED)
        with self.assertRaises(AssertionError):
            assert_expected_candidate_ids(EXPECTED + ["QXM2-CAND-07"])

    def test_evidence_role_rejects_proof_language(self):
        for role in ("supports", "contradicts", "boundary", "competing_mechanism"):
            assert_evidence_role(role)
        with self.assertRaises(AssertionError):
            assert_evidence_role("proves")

    def test_replication_gap_must_be_explicit(self):
        assert_replication_status("not_found")
        with self.assertRaises(AssertionError):
            assert_replication_status("")

    def test_shadow_hypothesis_cannot_preregister(self):
        assert_shadow_hypothesis_state("proposed")
        with self.assertRaises(AssertionError):
            assert_shadow_hypothesis_state("preregistered")

    def test_benchmark_seed_has_no_execution_authority(self):
        assert_benchmark_seed_authority({
            "formal_benchmark_status": "not_created",
            "benchmark_execution_authorized": False,
            "benchmark_pass_claim_authorized": False,
        })


class QXM2RealityMechanicsEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads(SOURCE_MATRIX.read_text(encoding="utf-8"))["sources"]
        self.relations = json.loads(EVIDENCE_MATRIX.read_text(encoding="utf-8"))["relations"]

    def test_reality_mechanics_has_minimum_source_coverage(self):
        for candidate_id in EXPECTED[:2]:
            anchors = [s for s in self.sources if candidate_id in s["candidate_ids"] and s["authority_class"] != "normative_accounting_standard"]
            self.assertGreaterEqual(len(anchors), 2, candidate_id)

    def test_reality_mechanics_has_empirical_and_boundary_relations(self):
        for candidate_id in EXPECTED[:2]:
            rels = [r for r in self.relations if r["candidate_id"] == candidate_id]
            self.assertTrue(any(r["role"] == "supports" and r["identification_strength"] != "theoretical_only" for r in rels), candidate_id)
            self.assertTrue(any(r["role"] in {"boundary", "contradicts", "competing_mechanism"} for r in rels), candidate_id)
            for relation in rels:
                assert_evidence_role(relation["role"])
                assert_replication_status(relation["replication_status"])


if __name__ == "__main__":
    unittest.main()
