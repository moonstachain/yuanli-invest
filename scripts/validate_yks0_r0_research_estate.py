#!/usr/bin/env python3
"""Fail-closed validator for YKS0-R0 Five-Country Research Estate."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ESTATE = Path("research/k-shaped-society")
COUNTRIES = {"US", "DE", "JP", "KR", "CN"}
DIMENSIONS = {f"K{i:02d}" for i in range(1, 10)}
PIT_STATES = {"PIT_NATIVE", "PIT_RECONSTRUCTABLE", "CURRENT_ONLY", "BACKTEST_OR_RESTATED", "UNKNOWN"}
CASE_STATES = {"CANDIDATE_DESKTOP", "PIT_AUDIT_REQUIRED", "PREREGISTRATION_READY", "REJECTED"}
FORBIDDEN_TERMS = {
    "recommended_weight", "target_weight", "position_size", "broker_action",
    "live_execution_authorized", "replay_pass", "scientific_pass",
    "k_score", "k-score", "scalar_k_score"
}
REQUIRED_PATHS = {
    "research/k-shaped-society/README.md",
    "research/k-shaped-society/reports/YKS0-R0-FIVE-COUNTRY-1990-2026-RESEARCH.md",
    "research/k-shaped-society/reports/YKS0-R0-DIVERGENCE-ASSET-MAP.md",
    "research/k-shaped-society/countries/US.md",
    "research/k-shaped-society/countries/DE.md",
    "research/k-shaped-society/countries/JP.md",
    "research/k-shaped-society/countries/KR.md",
    "research/k-shaped-society/countries/CN.md",
    "research/k-shaped-society/evidence/source-registry.json",
    "research/k-shaped-society/evidence/evidence-claims.json",
    "research/k-shaped-society/evidence/source-authority-policy.md",
    "research/k-shaped-society/dimensions/k-dimension-evidence-matrix.json",
    "research/k-shaped-society/hypotheses/hypothesis-registry.json",
    "research/k-shaped-society/replay/case-candidate-registry.json",
    "research/k-shaped-society/replay/pit-readiness-matrix.json",
    "research/k-shaped-society/settlements/YKS0-R0-DESKTOP-SETTLEMENT.md",
    "research/k-shaped-society/manifests/research-estate-manifest.json",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_estate(root: Path) -> dict[str, int | str]:
    missing = [path for path in sorted(REQUIRED_PATHS) if not (root / path).is_file()]
    require(not missing, f"missing_required_paths:{missing}")

    manifest = load_json(root / ESTATE / "manifests/research-estate-manifest.json")
    require(set(manifest.get("countries", [])) == COUNTRIES, "manifest_country_set_mismatch")
    require(set(manifest.get("dimensions", [])) == DIMENSIONS, "manifest_dimension_set_mismatch")
    for flag in ("production_runtime_authorized", "capital_authorized", "execution_authorized"):
        require(manifest.get(flag) is False, f"manifest_authority_escalation:{flag}")
    for locator in ("root", "source_registry", "pit_readiness", "desktop_settlement"):
        require(isinstance(manifest.get(locator), str) and (root / manifest[locator]).is_file(), f"bad_manifest_locator:{locator}")

    sources_doc = load_json(root / ESTATE / "evidence/source-registry.json")
    sources = sources_doc.get("sources", [])
    require(isinstance(sources, list) and sources, "empty_source_registry")
    source_ids = set()
    for source in sources:
        sid = source.get("source_id")
        require(isinstance(sid, str) and sid, "source_missing_id")
        require(sid not in source_ids, f"duplicate_source_id:{sid}")
        source_ids.add(sid)
        require(source.get("pit_status") in PIT_STATES, f"bad_source_pit_status:{sid}")
        require(source.get("local_grade") in {"A1","A2","A3","B1","B2","B3","C1","C2","D"}, f"bad_local_grade:{sid}")
        require(source.get("coarse_grade") in {"A","B","C","D"}, f"bad_coarse_grade:{sid}")
        require(bool(source.get("url")) and bool(source.get("logical_locator")), f"missing_source_locator:{sid}")
        require(bool(source.get("source_fact_summary")), f"missing_source_fact:{sid}")
        dims = set(source.get("k_dimensions", []))
        require(dims <= DIMENSIONS, f"bad_source_dimensions:{sid}")

    claims_doc = load_json(root / ESTATE / "evidence/evidence-claims.json")
    claims = claims_doc.get("claims", [])
    require(isinstance(claims, list) and claims, "empty_claim_registry")
    for claim in claims:
        cid = claim.get("claim_id", "UNKNOWN")
        refs = set(claim.get("source_ids", [])) | set(claim.get("counterevidence_ids", []))
        require(refs and refs <= source_ids, f"bad_claim_source_refs:{cid}:{sorted(refs-source_ids)}")
        require(bool(claim.get("source_fact")), f"missing_source_fact_layer:{cid}")
        require(bool(claim.get("research_inference")), f"missing_inference_layer:{cid}")
        require(bool(claim.get("scientific_status")), f"missing_scientific_status:{cid}")
        if claim.get("pit_qualified"):
            supporting = [s for s in sources if s["source_id"] in claim.get("source_ids", [])]
            require(supporting and all(s.get("pit_status") == "PIT_NATIVE" for s in supporting), f"pit_laundering:{cid}")

    matrix = load_json(root / ESTATE / "dimensions/k-dimension-evidence-matrix.json")
    cells = matrix.get("cells", [])
    require(set(matrix.get("countries", [])) == COUNTRIES, "matrix_country_set_mismatch")
    require(set(matrix.get("dimensions", [])) == DIMENSIONS, "matrix_dimension_set_mismatch")
    require(len(cells) == 45, f"matrix_cell_count:{len(cells)}")
    seen_cells = {(cell.get("country"), cell.get("dimension")) for cell in cells}
    require(seen_cells == {(c, d) for c in COUNTRIES for d in DIMENSIONS}, "matrix_not_complete_5x9")
    for cell in cells:
        require(set(cell.get("support_source_ids", [])) <= source_ids, "matrix_bad_support_ref")
        require(set(cell.get("counterevidence_ids", [])) <= source_ids, "matrix_bad_counter_ref")

    hypotheses = load_json(root / ESTATE / "hypotheses/hypothesis-registry.json").get("hypotheses", [])
    require({h.get("hypothesis_id") for h in hypotheses} == {f"H{i}" for i in range(1, 9)}, "hypothesis_set_mismatch")
    for hypothesis in hypotheses:
        require(bool(hypothesis.get("null_hypothesis")), f"missing_null:{hypothesis.get('hypothesis_id')}")
        require(bool(hypothesis.get("falsifier")), f"missing_falsifier:{hypothesis.get('hypothesis_id')}")
        require(hypothesis.get("formal_replay_status") != "REPLAY_PASS", "premature_replay_pass")

    cases = load_json(root / ESTATE / "replay/case-candidate-registry.json").get("cases", [])
    require(len(cases) == 50, f"case_count:{len(cases)}")
    require(all(case.get("status") in CASE_STATES for case in cases), "bad_case_status")
    require(all(case.get("pit_readiness") in PIT_STATES for case in cases), "bad_case_pit_state")
    by_country = {country: 0 for country in COUNTRIES}
    for case in cases:
        require(case.get("country") in COUNTRIES, f"bad_case_country:{case.get('case_id')}")
        by_country[case["country"]] += 1
    require(set(by_country.values()) == {10}, f"case_country_distribution:{by_country}")

    readiness = load_json(root / ESTATE / "replay/pit-readiness-matrix.json")
    require(set(readiness.get("countries", [])) == COUNTRIES, "pit_country_set_mismatch")
    require(all(item.get("pit_status") in PIT_STATES for item in readiness.get("entries", [])), "bad_pit_readiness_entry")

    json_paths = sorted((root / ESTATE).rglob("*.json"))
    forbidden_hits = []
    for path in json_paths:
        payload = load_json(path)
        for key in walk_keys(payload):
            if key.lower() in FORBIDDEN_TERMS:
                forbidden_hits.append(f"{path.relative_to(root)}:{key}")
    require(not forbidden_hits, f"forbidden_structured_keys:{forbidden_hits}")

    settlement = (root / ESTATE / "settlements/YKS0-R0-DESKTOP-SETTLEMENT.md").read_text(encoding="utf-8")
    upper = settlement.upper()
    require("FORMAL_PIT_VALIDATION_REQUIRED" in upper, "settlement_missing_formal_pit_gate")
    require("SCIENTIFIC PASS" not in upper and "UNCONDITIONAL PASS" not in upper, "desktop_to_science_escalation")

    return {
        "status": "VALID",
        "sources": len(sources),
        "claims": len(claims),
        "cells": len(cells),
        "hypotheses": len(hypotheses),
        "cases": len(cases),
    }


def main() -> int:
    try:
        result = validate_estate(ROOT)
    except Exception as exc:
        print(f"validation_error:{exc}", file=sys.stderr)
        return 1
    print(" ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
