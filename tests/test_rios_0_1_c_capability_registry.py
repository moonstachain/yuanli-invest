import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_rios_0_1_c_capability_registry.py"
STATE = ROOT / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-STATE.json"
MATRIX = ROOT / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json"
PACK = ROOT / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-GENESIS-PACK-v0.1.json"

EXPECTED_GENESIS_IDS = [
    "RIOS-GEN-01-AI-INFRASTRUCTURE-REGIME-TRANSITION",
    "RIOS-GEN-02-ENERGY-BOTTLENECK-CAPTURE",
    "RIOS-GEN-03-NARRATIVE-DIFFUSION-ENGINE",
    "RIOS-GEN-04-NARRATIVE-BUBBLE-DETECTION",
    "RIOS-GEN-05-PLATFORM-WINNER-CAPTURE",
    "RIOS-GEN-06-CONVEXITY-EXPRESSION-ENGINE",
    "RIOS-GEN-07-EVIDENCE-AUTHORITY-ENGINE",
    "RIOS-GEN-08-NARRATIVE-PRICE-GAP",
    "RIOS-GEN-09-PORTFOLIO-SURVIVAL-ENGINE",
    "RIOS-GEN-10-MARKET-CLOCK-REGIME-TRANSITION",
]

EXPECTED_CLASSIFICATIONS = {
    "RIOS-GEN-01-AI-INFRASTRUCTURE-REGIME-TRANSITION": "profile",
    "RIOS-GEN-02-ENERGY-BOTTLENECK-CAPTURE": "profile",
    "RIOS-GEN-03-NARRATIVE-DIFFUSION-ENGINE": "composite",
    "RIOS-GEN-04-NARRATIVE-BUBBLE-DETECTION": "composite",
    "RIOS-GEN-05-PLATFORM-WINNER-CAPTURE": "composite",
    "RIOS-GEN-06-CONVEXITY-EXPRESSION-ENGINE": "composite",
    "RIOS-GEN-07-EVIDENCE-AUTHORITY-ENGINE": "new_candidate",
    "RIOS-GEN-08-NARRATIVE-PRICE-GAP": "composite",
    "RIOS-GEN-09-PORTFOLIO-SURVIVAL-ENGINE": "composite",
    "RIOS-GEN-10-MARKET-CLOCK-REGIME-TRANSITION": "new_candidate",
}

REQUIRED_MATRIX_FIELDS = {
    "genesis_id",
    "human_name",
    "classification",
    "canonical_capability_ids",
    "candidate_capability_id",
    "rationale",
    "semantic_overlap_notes",
    "authority_boundary",
    "registry_mutation_required",
    "benchmark_execution_authorized",
    "runtime_authorized",
    "trading_authorized",
}

ALLOWED_AGENT_ROUTES = {
    "P_AGENT",
    "N_AGENT",
    "X_AGENT",
    "E_AGENT",
    "V_AGENT",
    "S_AGENT",
    "CHIEF_RESEARCH_COUNCIL",
}

REQUIRED_REPLAY_PREREQUISITES = {
    "historical_case_required",
    "pit_evidence_required",
    "falsifier_required",
    "benchmark_spec_required_before_execution",
}


def load_validator_module():
    spec = importlib.util.spec_from_file_location("rios_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RIOS01CBootstrapTests(unittest.TestCase):
    def test_validator_entrypoint_runs_primitive_self_check(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--self-test-primitives"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_initial_state_exists(self):
        self.assertTrue(STATE.exists(), str(STATE))

    def test_task1_required_primitives_exist(self):
        module = load_validator_module()
        for name in (
            "assert_exact_genesis_ids",
            "assert_classification",
            "assert_non_authority",
            "assert_pre_human_scope",
            "validate_rios_0_1_c",
        ):
            self.assertTrue(hasattr(module, name), name)

    def test_exact_genesis_ids_fail_closed(self):
        module = load_validator_module()
        module.assert_exact_genesis_ids(EXPECTED_GENESIS_IDS)
        with self.assertRaises(AssertionError):
            module.assert_exact_genesis_ids(EXPECTED_GENESIS_IDS + ["RIOS-GEN-11-SILENT"])

    def test_classification_is_closed(self):
        module = load_validator_module()
        for value in ("reuse", "composite", "profile", "new_candidate", "reject"):
            module.assert_classification({"classification": value})
        with self.assertRaises(AssertionError):
            module.assert_classification({"classification": "mother_by_default"})

    def test_non_authority_rejects_escalation(self):
        module = load_validator_module()
        module.assert_non_authority({
            "registry_admission_authorized": False,
            "benchmark_execution_authorized": False,
            "runtime_authorized": False,
            "trading_authorized": False,
        })
        for bad in (
            {"runtime_authorized": True},
            {"target_price": 123},
            {"pnx_score": 0.9},
        ):
            with self.assertRaises(AssertionError):
                module.assert_non_authority(bad)

    def test_pre_human_scope_rejects_authority_paths(self):
        module = load_validator_module()
        module.assert_pre_human_scope([
            "docs/architecture/rios/0.1-c/example.json",
            "scripts/validate_rios_0_1_c_capability_registry.py",
        ])
        for path in (
            "registry/capabilities/new.json",
            "canon/new.md",
            "runtime/new.py",
            "packages/contracts/schemas/research-capability.schema.json",
        ):
            with self.assertRaises(AssertionError):
                module.assert_pre_human_scope([path])

    def test_task2_matrix_is_exactly_ten_unique_rows_with_frozen_classifications(self):
        self.assertTrue(MATRIX.exists(), str(MATRIX))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        rows = matrix["rows"]
        self.assertEqual(matrix["genesis_count"], 10)
        self.assertEqual(len(rows), 10)
        ids = [row["genesis_id"] for row in rows]
        self.assertEqual(ids, EXPECTED_GENESIS_IDS)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            {row["genesis_id"]: row["classification"] for row in rows},
            EXPECTED_CLASSIFICATIONS,
        )

    def test_task2_matrix_rows_have_required_fields_and_no_execution_authority(self):
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        module = load_validator_module()
        for row in matrix["rows"]:
            self.assertTrue(REQUIRED_MATRIX_FIELDS.issubset(row), row["genesis_id"])
            module.assert_classification(row)
            module.assert_non_authority(row)
            self.assertFalse(row["benchmark_execution_authorized"])
            self.assertFalse(row["runtime_authorized"])
            self.assertFalse(row["trading_authorized"])

    def test_task2_canonical_dependencies_are_active_and_candidate_ids_do_not_collide(self):
        module = load_validator_module()
        inventory = module.load_available_capability_ids(ROOT)
        self.assertFalse(inventory["duplicate_physical_ids"], inventory["duplicate_physical_ids"])
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        for row in matrix["rows"]:
            for capability_id in row["canonical_capability_ids"]:
                self.assertIn(capability_id, inventory["active_ids"], (row["genesis_id"], capability_id))
            candidate_id = row["candidate_capability_id"]
            if candidate_id:
                self.assertNotIn(candidate_id, inventory["physical_ids"], candidate_id)

    def test_task3_pack_exactly_covers_matrix_and_routes_only_allowed_agents(self):
        self.assertTrue(PACK.exists(), str(PACK))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual(pack["pack_id"], "RIOS-GENESIS-PACK-001")
        self.assertEqual(pack["status"], "candidate_orchestration_pack")
        entries = pack["entries"]
        self.assertEqual([entry["genesis_id"] for entry in entries], EXPECTED_GENESIS_IDS)
        matrix_deps = {row["genesis_id"]: row["canonical_capability_ids"] for row in matrix["rows"]}
        for entry in entries:
            self.assertEqual(entry["canonical_capability_ids"], matrix_deps[entry["genesis_id"]])
            self.assertTrue(entry["agent_routes"], entry["genesis_id"])
            self.assertTrue(set(entry["agent_routes"]).issubset(ALLOWED_AGENT_ROUTES), entry)

    def test_task3_pack_requires_replay_prerequisites_and_zero_authorities(self):
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        module = load_validator_module()
        module.assert_non_authority(pack)
        self.assertFalse(pack["registry_admission_authorized"])
        self.assertFalse(pack["benchmark_execution_authorized"])
        self.assertFalse(pack["runtime_authorized"])
        self.assertFalse(pack["trading_authorized"])
        for entry in pack["entries"]:
            prereqs = entry["replay_prerequisites"]
            self.assertEqual(set(prereqs), REQUIRED_REPLAY_PREREQUISITES)
            self.assertTrue(all(prereqs.values()), entry["genesis_id"])
            self.assertFalse(entry["replay_pass_claimed"])

    def test_task3_prohibited_outputs_and_provider_native_semantics_fail_closed(self):
        module = load_validator_module()
        for bad in (
            {"target_price": 100},
            {"buy_signal": True},
            {"sell_signal": True},
            {"recommended_weight": 0.2},
            {"target_weight": 0.2},
            {"position_size": 0.2},
            {"broker_action": "BUY"},
            {"live_execution": True},
            {"pnx_score": 0.9},
            {"force_score": 0.9},
        ):
            with self.assertRaises(AssertionError):
                module.assert_non_authority(bad)
        for bad in (
            {"wind_field": "S_DQ_CLOSE"},
            {"wind_code": "000001.SZ"},
            {"bloomberg_field": "PX_LAST"},
            {"provider_native_identifier": "vendor:key"},
        ):
            with self.assertRaises(AssertionError):
                module.assert_provider_neutral(bad)

    @unittest.expectedFailure
    def test_full_pack_validates_after_task4(self):
        module = load_validator_module()
        result = module.validate_rios_0_1_c(ROOT)
        self.assertEqual(result["genesis_count"], 10)


if __name__ == "__main__":
    unittest.main()
