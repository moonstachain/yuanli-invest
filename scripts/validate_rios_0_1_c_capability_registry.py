#!/usr/bin/env python3
"""Validate RIOS-0.1-C convergence before Human Review.

Task 5 closes the pre-Human machine gate. It validates the exact ten Genesis
concepts, convergence classifications, governed dependencies, semantic-gap
readiness, provider neutrality, orchestration non-authority, and changed-path
scope. Registry/Canon/Runtime mutation remains forbidden.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
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

ALLOWED_CLASSIFICATIONS = {"reuse", "composite", "profile", "new_candidate", "reject"}
ALLOWED_CANDIDATE_READINESS = {
    "identity_candidate_only",
    "schema_dependencies_complete_candidate",
    "not_justified",
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
TASK4_NEW_CANDIDATE_FIELDS = {
    "semantic_gap_statement",
    "why_existing_mothers_are_insufficient",
    "required_dependency_types",
    "candidate_readiness",
}
REQUIRED_DEPENDENCY_KEYS = {
    "theory_ids",
    "hypothesis_ids",
    "factor_ids",
    "algorithm_ids",
    "benchmark_ids",
    "canonical_input_fields",
}
REGISTRY_DEPENDENCY_CONFIG = {
    "theory_ids": ("theories", "theory_id"),
    "hypothesis_ids": ("hypotheses", "hypothesis_id"),
    "factor_ids": ("factors", "factor_id"),
    "algorithm_ids": ("algorithms", "algorithm_id"),
    "benchmark_ids": ("benchmarks", "benchmark_id"),
    "canonical_input_fields": ("data-fields", "field_id"),
}

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
PROVIDER_NATIVE_KEYS = {
    "wind_field",
    "wind_code",
    "bloomberg_field",
    "bloomberg_ticker",
    "provider_native_identifier",
    "vendor_field",
    "vendor_code",
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
                assert value in (None, False, "none", "not_authorized"), (
                    f"prohibited output: {key}={value!r}"
                )
            assert_non_authority(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_non_authority(value)


def assert_provider_neutral(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert key not in PROVIDER_NATIVE_KEYS, f"provider-native semantic key prohibited: {key}"
            assert_provider_neutral(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_provider_neutral(value)


def assert_pre_human_scope(paths):
    offenders = [
        path
        for path in paths
        if path.startswith(PRE_HUMAN_PROHIBITED_PREFIXES) or path == CAPABILITY_SCHEMA_PATH
    ]
    assert not offenders, f"pre-Human authority paths changed: {offenders}"


def detect_changed_paths(root: Path):
    """Detect PR changed paths against the GitHub base ref; fail closed."""
    root = Path(root)
    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip() or "main"
    base = f"origin/{base_ref}"
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, (
        "unable to establish pre-Human changed-path scope",
        base,
        proc.stderr.strip(),
    )
    paths = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert paths, f"no changed paths detected against {base}; refusing ambiguous pre-Human scope"
    return paths


def _ids_from_pack(path: Path, id_key: str):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        obj[id_key]
        for obj in payload.get("objects", [])
        if isinstance(obj, dict) and id_key in obj
    ]


def load_active_registry_ids(root: Path, registry_name: str, id_key: str):
    root = Path(root)
    registry_dir = root / "registry" / registry_name
    index_path = registry_dir / "_index.json"
    assert index_path.exists(), f"registry index missing: {index_path}"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    active_ids = set()
    for pack_name in index.get("pack_files", []):
        pack_path = registry_dir / pack_name
        assert pack_path.exists(), f"governed {registry_name} pack missing: {pack_name}"
        active_ids.update(_ids_from_pack(pack_path, id_key))
    assert len(active_ids) == index["entry_count"], (
        registry_name,
        len(active_ids),
        index["entry_count"],
    )
    return active_ids


def load_available_capability_ids(root: Path):
    root = Path(root)
    registry_dir = root / "registry" / "capabilities"
    index = json.loads((registry_dir / "_index.json").read_text(encoding="utf-8"))

    physical_occurrences = []
    for path in sorted(registry_dir.glob("*.json")):
        if path.name == "_index.json":
            continue
        physical_occurrences.extend(_ids_from_pack(path, "capability_id"))

    counts = Counter(physical_occurrences)
    duplicate_physical_ids = {
        capability_id for capability_id, count in counts.items() if count > 1
    }

    active_ids = set()
    for pack_name in index.get("pack_files", []):
        pack_path = registry_dir / pack_name
        assert pack_path.exists(), f"governed capability pack missing: {pack_name}"
        active_ids.update(_ids_from_pack(pack_path, "capability_id"))
    assert len(active_ids) == index["entry_count"], (len(active_ids), index["entry_count"])

    return {
        "physical_ids": set(physical_occurrences),
        "active_ids": active_ids,
        "duplicate_physical_ids": duplicate_physical_ids,
        "active_pack_files": tuple(index.get("pack_files", [])),
    }


def validate_candidate_readiness(root: Path, row: dict):
    root = Path(root)
    assert row.get("classification") == "new_candidate", row.get("genesis_id")
    assert TASK4_NEW_CANDIDATE_FIELDS.issubset(row), row.get("genesis_id")
    assert isinstance(row["semantic_gap_statement"], str) and row["semantic_gap_statement"].strip()
    assert isinstance(row["why_existing_mothers_are_insufficient"], str) and row["why_existing_mothers_are_insufficient"].strip()
    readiness = row["candidate_readiness"]
    assert readiness in ALLOWED_CANDIDATE_READINESS, readiness

    deps = row["required_dependency_types"]
    assert isinstance(deps, dict), row.get("genesis_id")
    assert set(deps) == REQUIRED_DEPENDENCY_KEYS, (row.get("genesis_id"), set(deps))
    for dep_key, (registry_name, id_key) in REGISTRY_DEPENDENCY_CONFIG.items():
        active_ids = load_active_registry_ids(root, registry_name, id_key)
        for object_id in deps[dep_key]:
            assert object_id in active_ids, (
                row.get("genesis_id"),
                dep_key,
                f"dependency is not governed-active: {object_id}",
            )

    dependency_complete = bool(deps["theory_ids"])
    dependency_complete = dependency_complete and bool(deps["hypothesis_ids"])
    dependency_complete = dependency_complete and bool(deps["factor_ids"] or deps["algorithm_ids"])
    dependency_complete = dependency_complete and bool(deps["benchmark_ids"])
    dependency_complete = dependency_complete and bool(deps["canonical_input_fields"])

    preview = row.get("candidate_contract_preview", {})
    output_contract = preview.get("output_contract")
    contract_complete = bool(isinstance(output_contract, str) and output_contract.strip())
    contract_complete = contract_complete and preview.get("provider_independent") is True
    contract_complete = contract_complete and preview.get("scalar_pnx_score_prohibited") is True
    contract_complete = contract_complete and preview.get("investment_action_fields_prohibited") is True
    if preview:
        assert_provider_neutral(preview)
        assert_non_authority(preview)

    schema_dependencies_complete = dependency_complete and contract_complete
    registry_apply_ready = readiness == "schema_dependencies_complete_candidate" and schema_dependencies_complete

    if readiness == "schema_dependencies_complete_candidate":
        assert schema_dependencies_complete, (
            row.get("genesis_id"),
            "schema-ready claim requires governed Theory + Hypothesis + Factor/Algorithm + Benchmark + CanonicalDataField + provider-independent output contract/prohibitions",
        )
    else:
        assert not registry_apply_ready

    return {
        "candidate_readiness": readiness,
        "schema_dependencies_complete": schema_dependencies_complete,
        "registry_apply_ready": registry_apply_ready,
        "missing_dependency_types": [key for key in REQUIRED_DEPENDENCY_KEYS if not deps[key]],
    }


def validate_convergence_matrix(root: Path):
    root = Path(root)
    matrix_path = root / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json"
    assert matrix_path.exists(), f"convergence matrix missing: {matrix_path}"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    rows = matrix["rows"]
    assert matrix["genesis_count"] == 10
    assert len(rows) == 10
    ids = [row["genesis_id"] for row in rows]
    assert_exact_genesis_ids(ids)
    assert len(ids) == len(set(ids))
    actual = {row["genesis_id"]: row["classification"] for row in rows}
    assert actual == EXPECTED_CLASSIFICATIONS, actual

    inventory = load_available_capability_ids(root)
    assert not inventory["duplicate_physical_ids"], inventory["duplicate_physical_ids"]
    candidate_ids = []
    readiness_results = []
    for row in rows:
        assert REQUIRED_MATRIX_FIELDS.issubset(row), row["genesis_id"]
        assert_classification(row)
        assert_non_authority(row)
        assert_provider_neutral(row)
        assert row["benchmark_execution_authorized"] is False
        assert row["runtime_authorized"] is False
        assert row["trading_authorized"] is False
        for capability_id in row["canonical_capability_ids"]:
            assert capability_id in inventory["active_ids"], (
                row["genesis_id"],
                f"canonical dependency is not active governed authority: {capability_id}",
            )
        candidate_id = row["candidate_capability_id"]
        if row["classification"] == "new_candidate":
            assert candidate_id
            assert row["registry_mutation_required"] is True
            readiness_results.append(validate_candidate_readiness(root, row))
        else:
            assert candidate_id is None, (row["genesis_id"], candidate_id)
            assert row["registry_mutation_required"] is False
        if candidate_id:
            assert candidate_id not in inventory["physical_ids"], f"candidate ID collision: {candidate_id}"
            candidate_ids.append(candidate_id)
    assert len(candidate_ids) == len(set(candidate_ids))

    return {
        "genesis_count": 10,
        "new_candidate_count": len(candidate_ids),
        "active_capability_count": len(inventory["active_ids"]),
        "physical_capability_count": len(inventory["physical_ids"]),
        "schema_ready_candidate_count": sum(1 for result in readiness_results if result["registry_apply_ready"]),
    }


def validate_genesis_pack(root: Path):
    root = Path(root)
    rios = root / "docs" / "architecture" / "rios" / "0.1-c"
    matrix = json.loads((rios / "RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json").read_text(encoding="utf-8"))
    pack_path = rios / "RIOS-0.1-C-GENESIS-PACK-v0.1.json"
    assert pack_path.exists(), f"Genesis pack missing: {pack_path}"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))

    assert pack["pack_id"] == "RIOS-GENESIS-PACK-001"
    assert pack["status"] == "candidate_orchestration_pack"
    assert pack["genesis_count"] == 10
    assert_non_authority(pack)
    assert_provider_neutral(pack)
    for key in (
        "registry_admission_authorized",
        "benchmark_execution_authorized",
        "runtime_authorized",
        "trading_authorized",
    ):
        assert pack[key] is False, (key, pack[key])

    entries = pack["entries"]
    assert_exact_genesis_ids([entry["genesis_id"] for entry in entries])
    matrix_by_id = {row["genesis_id"]: row for row in matrix["rows"]}
    for entry in entries:
        row = matrix_by_id[entry["genesis_id"]]
        assert entry["classification"] == row["classification"]
        assert entry["canonical_capability_ids"] == row["canonical_capability_ids"]
        assert entry.get("candidate_capability_id") == row["candidate_capability_id"]
        routes = entry["agent_routes"]
        assert routes and set(routes).issubset(ALLOWED_AGENT_ROUTES)
        prereqs = entry["replay_prerequisites"]
        assert set(prereqs) == REQUIRED_REPLAY_PREREQUISITES
        assert all(value is True for value in prereqs.values())
        assert entry["replay_pass_claimed"] is False
        assert_non_authority(entry)
        assert_provider_neutral(entry)

    return {
        "pack_id": pack["pack_id"],
        "entry_count": len(entries),
        "agent_route_count": len({route for entry in entries for route in entry["agent_routes"]}),
        "replay_pass_claims": 0,
    }


def validate_rios_0_1_c(root: Path, changed_paths=None):
    root = Path(root)
    rios = root / "docs" / "architecture" / "rios" / "0.1-c"
    state_path = rios / "RIOS-0.1-C-STATE.json"
    assert state_path.exists(), state_path
    state = json.loads(state_path.read_text(encoding="utf-8"))

    assert state["stage"] == "RIOS_0_1_C_CAPABILITY_REGISTRY_MATERIALIZATION_GOVERNANCE_GATE"
    assert state["status"] == "candidate_ready_for_human_review", state["status"]
    assert state["next_gate"] == "RIOS_0_1_C_HUMAN_REVIEW", state["next_gate"]
    assert state["genesis_concept_count"] == 10
    for field in (
        "registry_mutation_authority",
        "benchmark_execution_authority",
        "runtime_authority",
        "trading_authority",
    ):
        assert state[field] == "none", (field, state[field])

    paths = list(changed_paths) if changed_paths is not None else detect_changed_paths(root)
    assert_pre_human_scope(paths)
    matrix_result = validate_convergence_matrix(root)
    pack_result = validate_genesis_pack(root)

    return {
        **matrix_result,
        **pack_result,
        "registry_mutations": 0,
        "changed_path_count": len(paths),
        "state_status": state["status"],
        "next_gate": state["next_gate"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-primitives", action="store_true")
    parser.add_argument("--matrix-only", action="store_true")
    parser.add_argument("--pack-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    if args.self_test_primitives:
        assert_exact_genesis_ids(EXPECTED_GENESIS_IDS)
        assert_classification({"classification": "profile"})
        assert_non_authority({"runtime_authorized": False, "trading_authorized": False})
        assert_provider_neutral({"canonical_input": "provider-independent"})
        assert_pre_human_scope(["docs/architecture/rios/0.1-c/example.json"])
        print("RIOS-0.1-C primitive bootstrap: PASS")
        return 0
    if args.matrix_only:
        print(json.dumps(validate_convergence_matrix(root), ensure_ascii=False, sort_keys=True))
        return 0
    if args.pack_only:
        print(json.dumps(validate_genesis_pack(root), ensure_ascii=False, sort_keys=True))
        return 0

    result = validate_rios_0_1_c(root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
