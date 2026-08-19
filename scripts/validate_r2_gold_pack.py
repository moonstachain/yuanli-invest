#!/usr/bin/env python3
"""Fail-closed validation for R2 PNX-S Gold Capability Pack."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "packages" / "contracts" / "schemas"
REGISTRY = ROOT / "registry"
R0_SEED = ROOT / "docs" / "architecture" / "r0" / "R0-GOLD-CAPABILITY-SEED-12-v0.1.json"
R1 = ROOT / "docs" / "architecture" / "r1"
R2 = ROOT / "docs" / "architecture" / "r2"
R2_STATE = R2 / "R2-STATE.json"
REGISTRY_INDEX = REGISTRY / "registry-index.json"

PACKS = {
    "theories": ("theory-object.schema.json", "TheoryObject", 19),
    "hypotheses": ("hypothesis-object.schema.json", "HypothesisObject", 12),
    "factors": ("factor-object.schema.json", "FactorObject", 6),
    "algorithms": ("algorithm-object.schema.json", "AlgorithmObject", 6),
    "benchmarks": ("benchmark-object.schema.json", "BenchmarkObject", 7),
    "skills": ("skill-contract.schema.json", "SkillContract", 12),
    "data-fields": ("canonical-data-field.schema.json", "CanonicalDataField", 25),
    "capabilities": ("research-capability.schema.json", "ResearchCapability", 12),
}

EXPECTED_CAPABILITIES = {
    "CAP-P-001-TECHNOLOGY-COST-CURVE",
    "CAP-P-002-ADOPTION-ACCELERATION",
    "CAP-N-001-NARRATIVE-VELOCITY",
    "CAP-N-002-NARRATIVE-SATURATION",
    "CAP-XS-001-MARKET-SHARE-ACCELERATION",
    "CAP-XS-002-BOTTLENECK-SCARCITY",
    "CAP-XA-001-CONDITIONAL-TAIL-ACTIVATION",
    "CAP-XA-002-EXTREME-REGIME-SHIFT",
    "CAP-XP-001-PAYOFF-CONVEXITY-GEOMETRY",
    "CAP-V-001-REVERSE-DCF-EXPECTATIONS",
    "CAP-S-001-RUIN-AND-EXPECTED-SHORTFALL",
    "CAP-S-002-ROBUST-FRACTIONAL-KELLY",
}

PROHIBITED_TOKENS = (
    '"target_price"',
    '"buy_signal"',
    '"sell_signal"',
    '"recommended_weight"',
    '"target_weight"',
    '"position_size"',
    '"broker_action"',
    '"live_execution"',
    '"pnx_score"',
    '"force_score"',
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_pack(name: str, schema_name: str, object_type: str, expected_count: int):
    pack_path = REGISTRY / name / "r2-pnxs-gold-v0.1.json"
    assert pack_path.exists(), f"missing R2 pack: {pack_path.relative_to(ROOT)}"
    pack = load_json(pack_path)
    assert pack["stage"] == "R2_PNXS_GOLD_CAPABILITY_PACK"
    assert pack["object_type"] == object_type
    assert pack["entry_count"] == expected_count == len(pack["objects"])
    schema = load_json(SCHEMAS / schema_name)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    id_key = {
        "TheoryObject": "theory_id",
        "HypothesisObject": "hypothesis_id",
        "FactorObject": "factor_id",
        "AlgorithmObject": "algorithm_id",
        "BenchmarkObject": "benchmark_id",
        "SkillContract": "skill_id",
        "CanonicalDataField": "field_id",
        "ResearchCapability": "capability_id",
    }[object_type]
    seen = set()
    for obj in pack["objects"]:
        errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
        assert not errors, f"{name}:{obj.get(id_key)} schema errors: {[e.message for e in errors[:5]]}"
        identity = obj[id_key]
        assert identity not in seen, f"duplicate {object_type} id: {identity}"
        seen.add(identity)
    return pack["objects"], seen


def main() -> None:
    required_docs = [
        R2 / "R2-PNXS-GOLD-CAPABILITY-PACK-v0.1.md",
        R2 / "R2-SOURCE-BOUNDARY-MAP-v0.1.md",
        R2 / "R2-HUMAN-REVIEW-CARD-v0.1.md",
        R2_STATE,
        R1 / "R1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json",
        R1 / "R1-MERGE-RECEIPT-v0.1.json",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required_docs if not p.exists()]
    assert not missing, f"missing R2/R1 reconciliation files: {missing}"

    objects = {}
    ids = {}
    for name, (schema_name, object_type, count) in PACKS.items():
        objects[name], ids[name] = validate_pack(name, schema_name, object_type, count)

    idx = load_json(REGISTRY_INDEX)
    expected_counts = {
        "theories": 19,
        "hypotheses": 12,
        "factors": 6,
        "algorithms": 6,
        "benchmarks": 7,
        "skills": 12,
        "data-fields": 25,
        "providers": 0,
        "capabilities": 12,
    }
    observed_counts = {item["name"]: item["entry_count"] for item in idx["registries"]}
    assert observed_counts == expected_counts, (observed_counts, expected_counts)
    assert idx["entry_count_total"] == 99 == sum(expected_counts.values())
    assert idx["silent_promotion_prohibited"] is True
    assert idx["r0_gold_seed_pack_promoted"] is False
    assert idx["r0_gold_seed_pack_compiled_to_specified"] is True
    assert idx["canon_entry_count"] == 0
    assert idx["provider_adapter_count"] == 0

    for name, expected in expected_counts.items():
        subindex = load_json(REGISTRY / name / "_index.json")
        assert subindex["entry_count"] == expected, f"subindex count drift: {name}"

    seed = load_json(R0_SEED)
    seed_ids = {item["capability_id"] for item in seed["capabilities"]}
    assert seed["status"] == "candidate_seed_not_canon"
    assert seed_ids == EXPECTED_CAPABILITIES == ids["capabilities"]

    by_cap = {obj["capability_id"]: obj for obj in objects["capabilities"]}
    for cap_id, cap in by_cap.items():
        assert cap["maturity_state"] == "specified", f"Gold must stop at specified: {cap_id}"
        assert cap["provider_independent"] is True
        assert cap["scalar_pnx_score_prohibited"] is True
        assert cap["investment_action_fields_prohibited"] is True
        assert cap["theory_ids"] and set(cap["theory_ids"]) <= ids["theories"]
        assert cap["hypothesis_ids"] and set(cap["hypothesis_ids"]) <= ids["hypotheses"]
        assert cap["benchmark_ids"] and set(cap["benchmark_ids"]) <= ids["benchmarks"]
        assert cap["canonical_input_fields"] and set(cap["canonical_input_fields"]) <= ids["data-fields"]
        assert cap["skill_ids"] and set(cap["skill_ids"]) <= ids["skills"]
        assert (cap["factor_ids"] or cap["algorithm_ids"]), f"missing factor/algorithm chain: {cap_id}"
        assert set(cap["factor_ids"]) <= ids["factors"]
        assert set(cap["algorithm_ids"]) <= ids["algorithms"]
        assert "target price" not in cap["output_contract"].lower(), cap_id

    for hyp in objects["hypotheses"]:
        assert hyp["status"] == "preregistered"
        assert hyp["point_in_time_requirement"] is True

    for factor in objects["factors"]:
        assert set(factor["hypothesis_ids"]) <= ids["hypotheses"]
        assert set(factor["canonical_input_fields"]) <= ids["data-fields"]
        assert set(factor["benchmark_ids"]) <= ids["benchmarks"]
        assert factor["point_in_time_required"] is True

    for alg in objects["algorithms"]:
        assert set(alg["benchmark_ids"]) <= ids["benchmarks"]
        assert alg["simpler_baselines"], alg["algorithm_id"]
        if alg["domain"] == "XA":
            assert alg["causal_claim_status"] == "predictive", "R2 Xa cannot overclaim causal identification"

    theory_by_id = {obj["theory_id"]: obj for obj in objects["theories"]}
    shiller = theory_by_id["THEORY-SHILLER-2017-NARRATIVE-ECONOMICS"]
    assert shiller["evidence_status"] == "primary_source_verified"
    xu = theory_by_id["THEORY-XU-2026-CAUSAL-EXTREME-SIGNALS"]
    assert xu["source_class"] == "practitioner_claim"
    assert xu["evidence_status"] == "practitioner_claim"
    practitioner_ids = {t["theory_id"] for t in objects["theories"] if t["evidence_status"] == "practitioner_claim"}
    assert practitioner_ids == {"THEORY-XU-2026-CAUSAL-EXTREME-SIGNALS"}
    for cap in objects["capabilities"]:
        if "THEORY-XU-2026-CAUSAL-EXTREME-SIGNALS" in cap["theory_ids"]:
            assert len(cap["theory_ids"]) >= 2, "practitioner claim cannot be sole theory basis"

    required_prohibited = {
        "target_price", "buy_signal", "sell_signal", "recommended_weight", "target_weight",
        "position_size", "broker_action", "live_execution", "scalar_pnx_score",
    }
    for skill in objects["skills"]:
        assert skill["runtime_class"] == "generic_agent", "R3 owns runtime-specific Wind/Codex interfaces"
        assert skill["skill_id"].startswith("SKILL-GENERIC-")
        assert skill["capability_id"] in EXPECTED_CAPABILITIES
        assert set(skill["data_requirements"]) <= ids["data-fields"]
        assert required_prohibited <= set(skill["prohibited_outputs"])

    for bench in objects["benchmarks"]:
        assert bench["lookahead_prohibited"] is True
        assert bench["calibration_requirement"].strip()
        assert bench["baseline"]
    xa_bench = next(b for b in objects["benchmarks"] if b["benchmark_id"] == "BENCH-XA-CONDITIONAL-TAIL-V1")
    assert not any(metric.lower() in {"accuracy", "raw_accuracy"} for metric in xa_bench["metric_set"])

    provider_idx = load_json(REGISTRY / "providers" / "_index.json")
    assert provider_idx["entry_count"] == 0

    r1_state = load_json(R1 / "R1-STATE.json")
    assert r1_state["status"] == "accepted_merged"
    assert r1_state["human_gate_decision"] == "ACCEPT_R1_CAPABILITY_REGISTRY_BOOTSTRAP"
    assert r1_state["reviewed_head_sha"] == "247dd734bd6eec8a927af1a65f8967130ee2701c"
    assert r1_state["merge_commit"] == "bfd1576e08dc836869b359773b09b3a169d09512"

    r2_state = load_json(R2_STATE)
    assert r2_state["stage"] == "R2_PNXS_GOLD_CAPABILITY_PACK"
    assert r2_state["base_commit"] == "bfd1576e08dc836869b359773b09b3a169d09512"
    assert r2_state["r1_decision"] == "ACCEPT_R1_CAPABILITY_REGISTRY_BOOTSTRAP"
    assert r2_state["capability_count"] == 12
    assert r2_state["registry_entry_count"] == 99
    assert r2_state["capability_maturity"] == "specified"
    assert r2_state["hypothesis_status"] == "preregistered"
    assert r2_state["benchmark_status"] == "protocol_only_not_passed"
    assert r2_state["provider_adapter_count"] == 0
    assert r2_state["canon_entry_count"] == 0
    assert r2_state["r3_authority"] == "not_authorized"
    assert r2_state["q1_state_change"] == "none"
    assert r2_state["a6_state_change"] == "none"
    assert r2_state["m1_2_state_change"] == "none"
    assert r2_state["a9_operational_canon_switch"] == "not_authorized"
    assert r2_state["evidence_admission"] == "not_authorized"
    assert r2_state["outcome_acceptance"] == "not_authorized"
    assert r2_state["rsi_frozen_change"] == "not_authorized"
    assert r2_state["live_execution"] == "unavailable_by_design"
    assert r2_state["accepted_follow_on_if_approved"] == "R3_WIND_AI_CODEX_SKILL_INTERFACE"

    docs_text = "\n".join((R2 / name).read_text(encoding="utf-8") for name in (
        "R2-PNXS-GOLD-CAPABILITY-PACK-v0.1.md", "R2-SOURCE-BOUNDARY-MAP-v0.1.md", "R2-HUMAN-REVIEW-CARD-v0.1.md"
    ))
    assert "X := (Xs, Xa, Xp)" in docs_text
    assert "Xs + Xa + Xp" not in docs_text
    assert "X_s + X_a + X_p" not in docs_text

    # No accidental action fields may appear as JSON property keys in the R2 pack.
    for name in PACKS:
        raw = (REGISTRY / name / "r2-pnxs-gold-v0.1.json").read_text(encoding="utf-8")
        for token in PROHIBITED_TOKENS:
            if name == "skills" and token in {
                '"target_price"', '"buy_signal"', '"sell_signal"', '"recommended_weight"', '"target_weight"',
                '"position_size"', '"broker_action"', '"live_execution"'
            }:
                # Skills must enumerate these values under prohibited_outputs; they are not output properties.
                continue
            assert token not in raw, f"prohibited action/scalar token in {name}: {token}"

    print("R2 PNX-S Gold Capability Pack validation: PASS")


if __name__ == "__main__":
    main()
