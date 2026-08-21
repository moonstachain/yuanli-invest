import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_rios_0_1_c_capability_registry.py"
STATE = ROOT / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-STATE.json"

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

    @unittest.expectedFailure
    def test_full_pack_validates_after_task2(self):
        module = load_validator_module()
        result = module.validate_rios_0_1_c(ROOT)
        self.assertEqual(result["genesis_count"], 10)


if __name__ == "__main__":
    unittest.main()
