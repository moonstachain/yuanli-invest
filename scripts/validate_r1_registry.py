#!/usr/bin/env python3
"""Fail-closed validation for R1 Research Capability registry bootstrap."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "docs" / "architecture" / "r1"
SCHEMAS = ROOT / "packages" / "contracts" / "schemas"
REGISTRY = ROOT / "registry"
STATE = R1 / "R1-STATE.json"
REGISTRY_INDEX = REGISTRY / "registry-index.json"
README = ROOT / "README.md"
R0_SEED = ROOT / "docs" / "architecture" / "r0" / "R0-GOLD-CAPABILITY-SEED-12-v0.1.json"

SCHEMA_FILES = [
    "theory-object.schema.json",
    "hypothesis-object.schema.json",
    "factor-object.schema.json",
    "algorithm-object.schema.json",
    "benchmark-object.schema.json",
    "skill-contract.schema.json",
    "canonical-data-field.schema.json",
    "provider-adapter.schema.json",
    "research-capability.schema.json",
]

REGISTRIES = {
    "theories": "TheoryObject",
    "hypotheses": "HypothesisObject",
    "factors": "FactorObject",
    "algorithms": "AlgorithmObject",
    "benchmarks": "BenchmarkObject",
    "skills": "SkillContract",
    "data-fields": "CanonicalDataField",
    "providers": "ProviderAdapter",
    "capabilities": "ResearchCapability",
}

PROHIBITED_PROPERTY_NAMES = {
    "target_price",
    "position_size",
    "recommended_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "broker_action",
    "live_execution",
    "pnx_score",
    "force_score",
}

LEGACY_BLOBS = {
    ROOT / "packages/contracts/schemas/convexity-profile.schema.json": "6c150e03ae3163517153bdd9683cbd083a675198",
    ROOT / "packages/contracts/schemas/force-triangle-snapshot.schema.json": "0e3be577a7daee5038e04401f760a75136be76ef",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def property_names(obj):
    if isinstance(obj, dict):
        props = obj.get("properties")
        if isinstance(props, dict):
            yield from props.keys()
        for value in obj.values():
            yield from property_names(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from property_names(item)


def main() -> None:
    required_docs = [
        R1 / "R1-CAPABILITY-OBJECT-MODEL-REGISTRY-BOOTSTRAP-v0.1.md",
        R1 / "R1-ID-RULES-v0.1.md",
        R1 / "R1-LIFECYCLE-RULES-v0.1.md",
        R1 / "R1-HUMAN-REVIEW-CARD-v0.1.md",
        STATE,
        REGISTRY / "README.md",
        REGISTRY_INDEX,
    ]
    missing = [str(p.relative_to(ROOT)) for p in required_docs if not p.exists()]
    assert not missing, f"missing R1 bootstrap files: {missing}"

    # R1 must not mutate legacy PNX v1.0 contracts in place.
    for path, expected in LEGACY_BLOBS.items():
        assert git_blob_sha(path) == expected, f"legacy contract drift: {path}"

    schemas = {}
    all_property_names = set()
    for name in SCHEMA_FILES:
        path = SCHEMAS / name
        assert path.exists(), f"missing R1 production-candidate schema: {name}"
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        assert schema["$id"].startswith("urn:yuanli-invest:"), name
        schemas[name] = schema
        all_property_names.update(property_names(schema))

    accidental = PROHIBITED_PROPERTY_NAMES & all_property_names
    assert not accidental, f"prohibited investment-action/scalar properties: {sorted(accidental)}"

    # Core semantic laws.
    cap = schemas["research-capability.schema.json"]["properties"]
    assert cap["provider_independent"] == {"const": True}
    assert cap["scalar_pnx_score_prohibited"] == {"const": True}
    assert cap["investment_action_fields_prohibited"] == {"const": True}
    assert set(cap["domain"]["enum"]) == {"P", "N", "XS", "XA", "XP", "V", "S", "E", "CROSS"}

    field = schemas["canonical-data-field.schema.json"]["properties"]
    assert field["provider_neutral"] == {"const": True}
    assert "provider_mappings" not in field, "provider mapping leaked into canonical field semantics"

    provider = schemas["provider-adapter.schema.json"]["properties"]
    assert provider["canonical_semantics_may_not_be_redefined"] == {"const": True}

    hyp = schemas["hypothesis-object.schema.json"]["properties"]
    assert hyp["point_in_time_requirement"] == {"const": True}

    bench = schemas["benchmark-object.schema.json"]["properties"]
    assert bench["lookahead_prohibited"] == {"const": True}

    # Registry topology and counts must be self-consistent.
    idx = load_json(REGISTRY_INDEX)
    entries = idx["registries"]
    assert len(entries) == 9
    observed = {item["name"]: item["object_type"] for item in entries}
    assert observed == REGISTRIES
    assert idx["entry_count_total"] == sum(item["entry_count"] for item in entries)
    assert idx["silent_promotion_prohibited"] is True
    assert idx["r0_gold_seed_pack_promoted"] is False

    for name, object_type in REGISTRIES.items():
        subindex = REGISTRY / name / "_index.json"
        assert subindex.exists(), f"missing registry subindex: {name}"
        item = load_json(subindex)
        assert item["registry"] == name
        assert item["object_type"] == object_type
        assert item["entry_count"] >= 0

    state = load_json(STATE)
    assert state["stage"] == "R1_CAPABILITY_OBJECT_MODEL_AND_REGISTRY_BOOTSTRAP"
    assert state["base_commit"] == "cbe943f7251e44703e8a2e4c8a68fce2be1d2ea7"
    assert state["center_object"] == "ResearchCapability"
    assert state["registry_count"] == 9
    assert state["production_candidate_schema_count"] == 9
    assert state["provider_independence"] == "canonical_data_field_plus_provider_adapter"
    assert state["silent_promotion"] == "prohibited"
    assert state["canon_promotion"] == "human_gate_required"
    assert state["a9_operational_canon_switch"] == "not_authorized"
    assert state["live_execution"] == "unavailable_by_design"
    assert state["accepted_follow_on_if_approved"] == "R2_PNXS_GOLD_CAPABILITY_PACK"

    if state["status"] == "candidate_started":
        assert idx["entry_count_total"] == 0, "R1 bootstrap must begin empty"
        assert state["bootstrap_entries"] == 0

    # R0 12 seeds remain candidate input for R2, not R1 canon entries.
    seed = load_json(R0_SEED)
    assert seed["status"] == "candidate_seed_not_canon"
    assert len(seed["capabilities"]) == 12

    readme = README.read_text(encoding="utf-8")
    for marker in (
        "Research Capability Canon",
        "Compile investment knowledge into machine-callable research intelligence.",
        "Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill",
        "Wind AI：Market Reality Runtime",
        "Codex：Research Engineering Runtime",
        "Current A9 operational canon：`moonstachain/quant-workspace`",
        "GitHub **不是 Data Warehouse**",
        "不代表可交易",
    ):
        assert marker in readme, f"README missing R0/R1 mission marker: {marker}"

    print("R1 Capability Object Model & Registry Bootstrap validation: PASS")


if __name__ == "__main__":
    main()
