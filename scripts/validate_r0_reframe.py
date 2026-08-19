#!/usr/bin/env python3
"""Fail-closed validation for R0 Research Capability Canon.

The validator supports two governed states:
1. pre-merge Human Accepted R0: the legacy README mission must remain byte-identical;
2. post-merge R0: a merge receipt must exist before a separately governed follow-on
   (such as R1) may align README with the accepted Research Capability Canon mission.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
R0 = ROOT / "docs" / "architecture" / "r0"
CONTRACTS = R0 / "contracts"
STATE = R0 / "R0-STATE.json"
SEED = R0 / "R0-GOLD-CAPABILITY-SEED-12-v0.1.json"
RECEIPT = R0 / "R0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE_RECEIPT = R0 / "R0-MERGE-RECEIPT-v0.1.json"
README = ROOT / "README.md"

REQUIRED_FILES = [
    R0 / "R0-RESEARCH-CAPABILITY-CANON-REFRAME-v0.1.md",
    R0 / "R0-ADR-001-RESEARCH-CAPABILITY-CANON.md",
    R0 / "research-capability-object-model-v0.1.md",
    R0 / "registry-topology-v0.1.md",
    R0 / "runtime-authority-map-v0.1.md",
    R0 / "R0-ROADMAP-v0.1.md",
    R0 / "R0-HUMAN-REVIEW-CARD-v0.1.md",
    RECEIPT,
    SEED,
    STATE,
    CONTRACTS / "research-capability.schema.json",
    CONTRACTS / "canonical-data-field.schema.json",
]

README_BLOB_SHA = "a3a03093e1b1255dc261ea2fa3d863c8c0e135e2"
R0_ACCEPTED_HEAD = "f3ecf6af372e50194f5d511c62061c4c43362556"
R0_MERGE_COMMIT = "cbe943f7251e44703e8a2e4c8a68fce2be1d2ea7"
PROHIBITED_KEYS = {
    "target_price",
    "position_size",
    "recommended_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "pnx_score",
    "force_score",
}


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from walk_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_keys(item)


def validate_readme_after_merge() -> None:
    text = README.read_text(encoding="utf-8")
    required = (
        "Research Capability Canon",
        "Compile investment knowledge into machine-callable research intelligence.",
        "ResearchCapability",
        "Wind AI：Market Reality Runtime",
        "Codex：Research Engineering Runtime",
        "Current A9 operational canon：`moonstachain/quant-workspace`",
        "GitHub **不是 Data Warehouse**",
        "不代表可交易",
    )
    for marker in required:
        assert marker in text, f"post-R0 README missing governed mission/boundary marker: {marker}"


def main() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED_FILES if not p.exists()]
    assert not missing, f"missing R0 files: {missing}"

    schemas = []
    for path in (CONTRACTS / "research-capability.schema.json", CONTRACTS / "canonical-data-field.schema.json"):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        assert schema["$id"].startswith("urn:yuanli-invest:r0:"), path.name
        schemas.append(schema)

    keys = set()
    for schema in schemas:
        keys.update(walk_keys(schema))
    assert not (PROHIBITED_KEYS & keys), f"prohibited action/scalar keys: {sorted(PROHIBITED_KEYS & keys)}"

    capability = load_json(CONTRACTS / "research-capability.schema.json")
    props = capability["properties"]
    assert props["provider_independent"] == {"const": True}
    assert props["scalar_pnx_score_prohibited"] == {"const": True}
    assert props["investment_action_fields_prohibited"] == {"const": True}
    assert set(props["domain"]["enum"]) == {"P", "N", "XS", "XA", "XP", "V", "S", "E", "CROSS"}

    field = load_json(CONTRACTS / "canonical-data-field.schema.json")
    assert field["properties"]["provider_neutral"] == {"const": True}

    seed = load_json(SEED)
    assert seed["status"] == "candidate_seed_not_canon"
    seeded = seed["capabilities"]
    assert len(seeded) == 12, f"expected 12 Gold Capability seeds, got {len(seeded)}"
    ids = [item["capability_id"] for item in seeded]
    assert len(ids) == len(set(ids)), "duplicate capability seed id"
    assert {item["domain"] for item in seeded} == {"P", "N", "XS", "XA", "XP", "V", "S"}
    assert all(item["maturity_state"] == "concept" for item in seeded)

    receipt = load_json(RECEIPT)
    assert receipt["decision"] == "ACCEPT_R0_RESEARCH_CAPABILITY_CANON_REFRAME"
    assert receipt["reviewed_head_sha"] == "9f1c17990d66b327d080668753387be1f0eb80c3"
    assert receipt["pre_acceptance_ci"]["run_number"] == 46
    assert receipt["pre_acceptance_ci"]["conclusion"] == "success"
    assert receipt["merge_authority"] == "not_implied_by_acceptance"
    assert receipt["follow_on_authority"] == "R1_CAPABILITY_OBJECT_MODEL_AND_REGISTRY_BOOTSTRAP_AFTER_R0_MERGE"
    assert all(value is False for value in receipt["boundaries_preserved"].values())

    state = load_json(STATE)
    assert state["stage"] == "R0_RESEARCH_CAPABILITY_CANON_REFRAME"
    assert state["human_gate_decision"] == "ACCEPT_R0_RESEARCH_CAPABILITY_CANON_REFRAME"
    assert state["center_object_candidate"] == "ResearchCapability"
    assert state["provider_independence"] == "canonical_data_field_required"
    assert state["production_schema_change"] == "none"
    assert state["readme_mission_change"] == "authorized_after_r0_merge_via_separate_change"
    assert state["accepted_follow_on_if_approved"] == "R1_CAPABILITY_OBJECT_MODEL_AND_REGISTRY_BOOTSTRAP"

    if state["status"] == "human_accepted_ready_for_merge":
        # Before R0 merge, acceptance alone must not alter README or start R1.
        assert git_blob_sha(README) == README_BLOB_SHA, "README mission changed before governed post-R0 change"
        assert state["r1_authority"] == "authorized_after_r0_merge_not_started"
        assert state["next_gate"] == "R0_MERGE"
    elif state["status"] == "human_accepted_merged":
        assert MERGE_RECEIPT.exists(), "R0 merged state missing merge receipt"
        merge = load_json(MERGE_RECEIPT)
        assert merge["human_gate_decision"] == "ACCEPT_R0_RESEARCH_CAPABILITY_CANON_REFRAME"
        assert merge["pull_request"] == 17
        assert merge["accepted_head_sha"] == R0_ACCEPTED_HEAD
        assert merge["merge_commit_sha"] == R0_MERGE_COMMIT
        assert merge["post_merge_authority"]["readme_mission_alignment"] == "authorized_via_separate_governed_change"
        assert merge["post_merge_authority"]["r1_capability_registry_bootstrap"] == "authorized"
        assert state["accepted_head_sha"] == R0_ACCEPTED_HEAD
        assert state["merge_commit_sha"] == R0_MERGE_COMMIT
        assert state["r1_authority"] in {"authorized_not_started", "authorized_started_candidate"}
        assert state["next_gate"] == "R1_CAPABILITY_OBJECT_MODEL_AND_REGISTRY_BOOTSTRAP"
        validate_readme_after_merge()
    else:
        raise AssertionError(f"unsupported R0 state: {state['status']}")

    spec = (R0 / "R0-RESEARCH-CAPABILITY-CANON-REFRAME-v0.1.md").read_text(encoding="utf-8")
    for marker in (
        "GitHub != Data Warehouse",
        "GitHub = Research Capability Canon",
        "ResearchCapability",
        "Theory",
        "Hypothesis",
        "Factor",
        "Algorithm",
        "Benchmark",
        "Skill",
        "CanonicalDataField",
        "Wind AI｜Market Reality Runtime",
        "Codex｜Research Engineering Runtime",
    ):
        assert marker in spec, f"missing R0 invariant marker: {marker}"

    print("R0 Research Capability Canon reframe validation: PASS")


if __name__ == "__main__":
    main()
