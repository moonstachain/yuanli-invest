import json
import unittest

from scripts.validate_ymq_os0_g1 import (
    validate_contract,
    validate_projection_manifest,
    validate_runtime_request,
)


class YMQOS0G1ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = {
            "contract_id": "YMQ-OS0-G1-SOVEREIGN-STACK-v0.1",
            "planes": {
                "law": {"provider": "GitHub", "authority": "CANON", "replaceable": False},
                "reality": {"provider": "Supabase", "authority": "REALITY_LEDGER", "replaceable": True},
                "experiment": {"provider": "HuggingFace", "authority": "COMPUTE_ONLY", "replaceable": True},
                "experience": {"provider": "Notion", "authority": "PROJECTION_ONLY", "replaceable": True},
                "runtime": {"provider": "YuanliGateway", "authority": "RESEARCH_ORCHESTRATION_ONLY", "replaceable": True},
            },
            "laws": {
                "unknown_is_deny": True,
                "research_not_capital": True,
                "research_not_execution": True,
                "claim_authority_lte_evidence_authority": True,
            },
            "cross_plane_identity": {
                "required": ["run_id", "git_sha", "as_of", "evidence_refs"],
                "immutable_receipt": True,
            },
            "explicitly_not_authorized": [
                "CAPITAL_AUTHORITY",
                "POSITION_SIZING",
                "BROKER_EXECUTION",
                "REAL_CAPITAL_MOVEMENT",
            ],
        }

    def test_contract_accepts_five_planes_and_authority_separation(self):
        self.assertEqual(validate_contract(self.contract), [])

    def test_contract_rejects_provider_as_authority(self):
        bad = json.loads(json.dumps(self.contract))
        bad["planes"]["experiment"]["authority"] = "CANON"
        self.assertIn("experiment_provider_cannot_hold_canon_authority", validate_contract(bad))

    def test_runtime_unknown_evidence_denies(self):
        payload = {"intent": "research", "evidence_status": "UNKNOWN", "requested_authority": "RESEARCH"}
        result = validate_runtime_request(payload)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "UNKNOWN_DENY")

    def test_runtime_denies_capital_and_execution_intents(self):
        for intent in ("position_sizing", "broker_order", "real_capital_move"):
            with self.subTest(intent=intent):
                result = validate_runtime_request(
                    {"intent": intent, "evidence_status": "PASS", "requested_authority": "CAPITAL"}
                )
                self.assertFalse(result["allowed"])
                self.assertEqual(result["reason"], "AUTHORITY_DENY")

    def test_runtime_denies_any_non_research_authority(self):
        for authority in ("CANON", "ADMIN", "CAPITAL", "EXECUTION", None):
            with self.subTest(authority=authority):
                result = validate_runtime_request(
                    {"intent": "research", "evidence_status": "PASS", "requested_authority": authority}
                )
                self.assertFalse(result["allowed"])
                self.assertEqual(result["reason"], "AUTHORITY_DENY")

    def test_projection_manifest_cannot_be_truth_or_grant_authority(self):
        manifest = {
            "system": "Notion",
            "role": "PROJECTION_ONLY",
            "canonical_truth": False,
            "can_grant_authority": False,
            "capital_authorized": False,
            "execution_authorized": False,
        }
        self.assertEqual(validate_projection_manifest(manifest), [])
        manifest["canonical_truth"] = True
        self.assertIn("projection_cannot_be_canonical_truth", validate_projection_manifest(manifest))

    def test_projection_manifest_denies_capital_and_execution_authority(self):
        for field in ("capital_authorized", "execution_authorized"):
            manifest = {
                "system": "Notion",
                "role": "PROJECTION_ONLY",
                "canonical_truth": False,
                "can_grant_authority": False,
                "capital_authorized": False,
                "execution_authorized": False,
            }
            manifest[field] = True
            with self.subTest(field=field):
                self.assertIn("projection_authority_leak", validate_projection_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
