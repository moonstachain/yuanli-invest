#!/usr/bin/env python3
"""Fail-closed validation for R0 Research Capability Canon candidate.

R0 is architecture-only. It must preserve the current README mission until Human
Review and must not register candidate schemas into production contract paths.
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
README = ROOT / "README.md"

REQUIRED_FILES = [
    R0 / "R0-RESEARCH-CAPABILITY-CANON-REFRAME-v0.1.md",
    R0 / "R0-ADR-001-RESEARCH-CAPABILITY-CANON.md",
    R0 / "research-capability-object-model-v0.1.md",
    R0 / "registry-topology-v0.1.md",
    R0 / "runtime-authority-map-v0.1.md",
    R0 / "R0-ROADMAP-v0.1.md",
    R0 / "R0-HUMAN-REVIEW-CARD-v0.1.md",
    STATE,
    CONTRACTS / "research-capability.schema.json",
    CONTRACTS / "canonical-data-field.schema.json",
]

README_BLOB_SHA = "a3a03093e1b1255dc261ea2fa3d863c8c0e135e2"
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


def main() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED_FILES if not p.exists()]
    assert not missing, f"missing R0 files: {missing}"

    assert git_blob_sha(README) == README_BLOB_SHA, "README mission changed before R0 Human Review"

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

    state = load_json(STATE)
    assert state["stage"] == "R0_RESEARCH_CAPABILITY_CANON_REFRAME"
    assert state["status"] == "candidate_started"
    assert state["center_object_candidate"] == "ResearchCapability"
    assert state["provider_independence"] == "canonical_data_field_required"
    assert state["production_schema_change"] == "none"
    assert state["readme_mission_change"] == "not_authorized_before_human_acceptance"
    assert state["accepted_follow_on_if_approved"] == "R1_CAPABILITY_OBJECT_MODEL_AND_REGISTRY_BOOTSTRAP"

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
