#!/usr/bin/env python3
"""Validate RIOS-0.1-C convergence bootstrap and governance primitives.

Task 1 intentionally stops before Matrix / Genesis Pack materialization. The
full-pack validator therefore fails closed until later approved tasks create the
missing convergence artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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

ALLOWED_CLASSIFICATIONS = {"reuse", "composite", "profile", "new_candidate", "reject"}

PROHIBITED_TRUE_KEYS = {
    "registry_admission_authorized",
    "registry_apply_authorized",
    "benchmark_execution_authorized",
    "capability_promotion_authorized",
    "runtime_authorized",
    "trading_authorized",
    "live_execution",
}

PROHIBITED_VALUE_KEYS = {
    "target_price",
    "buy_signal",
    "sell_signal",
    "recommended_weight",
    "target_weight",
    "position_size",
    "broker_action",
    "pnx_score",
    "force_score",
}

PRE_HUMAN_PROHIBITED_PREFIXES = ("registry/", "canon/", "runtime/")
CAPABILITY_SCHEMA_PATH = "packages/contracts/schemas/research-capability.schema.json"


def assert_exact_genesis_ids(rows):
    assert list(rows) == EXPECTED_GENESIS_IDS, list(rows)


def assert_classification(row):
    classification = row.get("classification")
    assert classification in ALLOWED_CLASSIFICATIONS, classification


def assert_non_authority(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in PROHIBITED_TRUE_KEYS:
                assert value is False, f"authority escalation: {key}={value!r}"
            if key in PROHIBITED_VALUE_KEYS:
                assert value in (None, False, "none", "not_authorized"), f"prohibited output: {key}={value!r}"
            assert_non_authority(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_non_authority(value)


def assert_pre_human_scope(paths):
    offenders = [
        path
        for path in paths
        if path.startswith(PRE_HUMAN_PROHIBITED_PREFIXES) or path == CAPABILITY_SCHEMA_PATH
    ]
    assert not offenders, f"pre-Human authority paths changed: {offenders}"


def validate_rios_0_1_c(root: Path):
    root = Path(root)
    rios = root / "docs" / "architecture" / "rios" / "0.1-c"
    state_path = rios / "RIOS-0.1-C-STATE.json"
    matrix_path = rios / "RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json"
    pack_path = rios / "RIOS-0.1-C-GENESIS-PACK-v0.1.json"

    assert state_path.exists(), state_path
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["stage"] == "RIOS_0_1_C_CAPABILITY_REGISTRY_MATERIALIZATION_GOVERNANCE_GATE"
    assert state["status"] == "convergence_compilation_started"
    assert state["genesis_concept_count"] == 10
    for field in (
        "registry_mutation_authority",
        "benchmark_execution_authority",
        "runtime_authority",
        "trading_authority",
    ):
        assert state[field] == "none", (field, state[field])

    assert matrix_path.exists(), f"Task 2 convergence matrix missing: {matrix_path}"
    assert pack_path.exists(), f"Task 3 Genesis pack missing: {pack_path}"

    return {
        "genesis_count": 10,
        "new_candidate_count": 0,
        "registry_mutations": 0,
        "next_gate": state["next_gate"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-primitives", action="store_true")
    args = parser.parse_args()

    if args.self_test_primitives:
        assert_exact_genesis_ids(EXPECTED_GENESIS_IDS)
        assert_classification({"classification": "profile"})
        assert_non_authority({"runtime_authorized": False, "trading_authorized": False})
        assert_pre_human_scope(["docs/architecture/rios/0.1-c/example.json"])
        print("RIOS-0.1-C primitive bootstrap: PASS")
        return 0

    root = Path(__file__).resolve().parents[1]
    result = validate_rios_0_1_c(root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
