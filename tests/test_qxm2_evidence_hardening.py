import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

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
CROSSWALK = QXM2 / "QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json"
SHADOW_THEORIES = QXM2 / "QXM2-SHADOW-THEORY-OBJECTS-v0.1.json"
SHADOW_HYPOTHESES = QXM2 / "QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json"
THEORY_SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "theory-object.schema.json"
HYPOTHESIS_SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "hypothesis-object.schema.json"

EXPECTED = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]


def load_evidence():
    sources = json.loads(SOURCE_MATRIX.read_text(encoding="utf-8"))["sources"]
    relations = json.loads(EVIDENCE_MATRIX.read_text(encoding="utf-8"))["relations"]
    return sources, relations


def assert_minimum_evidence(testcase, candidate_id, sources, relations):
    anchors = [
        s for s in sources
        if candidate_id in s["candidate_ids"]
        and s["authority_class"] != "normative_accounting_standard"
    ]
    testcase.assertGreaterEqual(len(anchors), 2, candidate_id)
    rels = [r for r in relations if r["candidate_id"] == candidate_id]
    testcase.assertTrue(any(r["role"] == "supports" and r["identification_strength"] != "theoretical_only" for r in rels), candidate_id)
    testcase.assertTrue(any(r["role"] in {"boundary", "contradicts", "competing_mechanism"} for r in rels), candidate_id)
    for relation in rels:
        assert_evidence_role(relation["role"])
        assert_replication_status(relation["replication_status"])


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


class QXM2EvidenceCoverageTests(unittest.TestCase):
    def test_all_candidates_have_minimum_evidence(self):
        sources, relations = load_evidence()
        for candidate_id in EXPECTED:
            assert_minimum_evidence(self, candidate_id, sources, relations)


class QXM2ClaimMechanismCrosswalkTests(unittest.TestCase):
    def test_claim_crosswalk_is_referentially_complete(self):
        relations = json.loads(EVIDENCE_MATRIX.read_text(encoding="utf-8"))["relations"]
        relation_by_id = {r["relation_id"]: r for r in relations}
        claims = json.loads(CROSSWALK.read_text(encoding="utf-8"))["claims"]

        for candidate_id in EXPECTED:
            candidate_claims = [c for c in claims if c["candidate_id"] == candidate_id]
            self.assertGreaterEqual(len(candidate_claims), 3, candidate_id)
            self.assertLessEqual(len(candidate_claims), 6, candidate_id)

        for claim in claims:
            self.assertTrue(claim["statement"].strip(), claim["claim_id"])
            self.assertTrue(claim["mechanism_ids"], claim["claim_id"])
            self.assertTrue(claim["observable_set"], claim["claim_id"])
            self.assertTrue(claim["falsifier"].strip(), claim["claim_id"])
            self.assertTrue(claim["shadow_hypothesis_ids"], claim["claim_id"])
            self.assertTrue(claim["benchmark_seed_ids"], claim["claim_id"])
            self.assertTrue(claim["support_relation_ids"], claim["claim_id"])
            self.assertTrue(claim["boundary_relation_ids"], claim["claim_id"])
            for relation_id in claim["support_relation_ids"]:
                self.assertIn(relation_id, relation_by_id, claim["claim_id"])
                self.assertEqual(relation_by_id[relation_id]["role"], "supports", claim["claim_id"])
            for relation_id in claim["boundary_relation_ids"]:
                self.assertIn(relation_id, relation_by_id, claim["claim_id"])
                self.assertIn(relation_by_id[relation_id]["role"], {"boundary", "contradicts", "competing_mechanism"}, claim["claim_id"])


class QXM2ShadowObjectTests(unittest.TestCase):
    def test_shadow_theories_are_schema_compatible_and_non_authoritative(self):
        schema = json.loads(THEORY_SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        objects = json.loads(SHADOW_THEORIES.read_text(encoding="utf-8"))["shadow_theories"]
        for candidate_id in EXPECTED:
            self.assertGreaterEqual(sum(candidate_id in obj["candidate_targets"] for obj in objects), 2, candidate_id)
        for obj in objects:
            self.assertEqual(obj["admission_state"], "shadow_only")
            self.assertEqual(obj["admission_authority"], "none")
            self.assertFalse(obj["theory_object"]["theory_id"].startswith("THEORY-QIN"))
            validator.validate(obj["theory_object"])
        self.assertFalse(any("IAS7" in obj["theory_object"]["theory_id"] for obj in objects))

    def test_shadow_hypotheses_are_schema_compatible_and_proposed_only(self):
        schema = json.loads(HYPOTHESIS_SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        objects = json.loads(SHADOW_HYPOTHESES.read_text(encoding="utf-8"))["shadow_hypotheses"]
        for candidate_id in EXPECTED:
            candidate_objects = [obj for obj in objects if obj["candidate_id"] == candidate_id]
            self.assertGreaterEqual(len(candidate_objects), 2, candidate_id)
        for obj in objects:
            self.assertEqual(obj["admission_state"], "shadow_only")
            self.assertEqual(obj["admission_authority"], "none")
            validator.validate(obj["hypothesis_object"])
            assert_shadow_hypothesis_state(obj["hypothesis_object"]["status"])


if __name__ == "__main__":
    unittest.main()
