from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "benchmarks" / "yios-g1-gold-genesis-canonical-reality-loop-v1.json"
VALIDATOR = ROOT / "scripts" / "validate_yios_g1_gold_genesis_benchmark_registry.py"

EXPECTED_LINEAGE = [
    {"stage": "YIOS0", "commit_sha": "61412df120faca8b30d87572175e3be8ed021213"},
    {"stage": "A0", "commit_sha": "fa5dc9bf73b200e5ee91debf6e95e6097fbbc17a"},
    {"stage": "G1", "commit_sha": "6ca14e6edd2d9a48a3f3e1847aff87d77e180634"},
    {"stage": "G3", "commit_sha": "558275fe3fb4dcd13e4809c466b336a9119f02fe"},
    {"stage": "G4", "commit_sha": "b931a65a9a8532cca5d03992575e999015897361"},
]


def load_validator():
    if not VALIDATOR.exists():
        raise AssertionError(f"missing validator: {VALIDATOR}")
    spec = importlib.util.spec_from_file_location(
        "validate_yios_g1_gold_genesis_benchmark_registry", VALIDATOR
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class TestGoldGenesisBenchmarkRegistry(unittest.TestCase):
    def test_registry_object_freezes_exact_semantics_and_lineage(self):
        self.assertTrue(REGISTRY.exists(), f"missing registry object: {REGISTRY}")
        obj = json.loads(REGISTRY.read_text(encoding="utf-8"))

        self.assertEqual(obj["benchmark_id"], "GOLD_GENESIS_CANONICAL_REALITY_LOOP_v1")
        self.assertEqual(obj["object_type"], "GoldenRealityLoopBenchmarkRegistryObject")
        self.assertEqual(obj["registry_state"], "REGISTERED_PENDING_REALITY_ACTIVATION")
        self.assertEqual(obj["activation_target"], "ACTIVE")
        self.assertEqual(obj["canon_lineage"], EXPECTED_LINEAGE)

        frozen = obj["frozen_settlement"]
        self.assertEqual(frozen["scientific_primary"], "INDETERMINATE")
        self.assertEqual(frozen["capital_settlement"], "DENY")
        self.assertEqual(frozen["runtime_settlement"], "FAIL_CLOSED_VALID")
        self.assertEqual(frozen["learning"], "DENIAL_IS_VALID_EXECUTION_OUTCOME")

        self.assertEqual(obj["benchmark_meaning"], "SYSTEM_REALITY_LOOP_CORRECTNESS_NOT_GOLD_PRICE_PREDICTION")
        self.assertFalse(obj["activation"]["self_activation_authorized"])
        self.assertEqual(
            obj["activation"]["required_reality_gates"],
            [
                "EXACT_HEAD_CI_SUCCESS",
                "PROTECTED_MAIN_MERGE",
                "FRESH_MAIN_READBACK",
                "POST_MERGE_CI_SUCCESS",
            ],
        )
        self.assertTrue(all(value is False for value in obj["non_authorizations"].values()))

    def test_validator_exists_and_accepts_registry_contract(self):
        self.assertTrue(VALIDATOR.exists(), f"missing validator: {VALIDATOR}")
        validator = load_validator()
        validator.validate_gold_genesis_benchmark_registry()


if __name__ == "__main__":
    unittest.main()
