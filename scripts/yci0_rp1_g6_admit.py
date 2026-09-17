#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.yci0_rp1.capital_efficiency_contract import (
    MANDATORY_COMPONENTS,
    REQUIRED_COHORTS,
    REPRESENTATIVES,
    load_capital_efficiency_contract,
)

CONTRACT_PATH = ROOT / "config/yci0_rp1/capital_efficiency_contract.v0.1.json"
CURRENT_SCOPE = "PARTIAL_REALITY_STATE_5_OF_6"
CANDIDATE_FULL_SCOPE = "FULL_REALITY_STATE_6_OF_6"


def _canonical_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dedupe_by_content_hash(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        content_hash = str(row.get("content_hash") or "")
        if not content_hash:
            raise ValueError("content_hash is required for idempotent admission")
        if content_hash in seen:
            continue
        seen.add(content_hash)
        out.append(row)
    return out


def _base_decision(status: str, blockers: list[str]) -> dict[str, Any]:
    return {
        "program": "YCI0-RP1",
        "gate": "G6_CAPITAL_EFFICIENCY_ADMISSION",
        "admission_status": status,
        "g6_state": "UNKNOWN",
        "current_scope": CURRENT_SCOPE,
        "candidate_scope": None,
        "qualified_metric_identities": 0,
        "required_metric_identities": 12,
        "blockers": blockers,
        "mutation_plan": [],
        "mutation_count": 0,
        "authority": "RESEARCH",
        "journey_stage": "02 EVIDENCE",
        "transition_suggestion": "HOLD",
        "physical_readback_required": False,
        "capital_authorized": False,
        "execution_authorized": False,
    }


def _raw_readback_blockers(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    rows = receipt.get("archives") or []
    expected = {(entity, kind) for entity in REPRESENTATIVES.values() for kind in ("companyfacts", "submissions")}
    actual = {(str(row.get("entity_id")), str(row.get("kind"))) for row in rows}
    if receipt.get("status") != "PASS" or receipt.get("archive_mode") != "PRIVATE_S3_SHA_READBACK":
        blockers.append("ARCHIVE_NOT_PRIVATE_S3_PASS")
    if actual != expected:
        blockers.append("RAW_ARCHIVE_COVERAGE_MISMATCH")
    for row in rows:
        if not row.get("sha256") or row.get("sha256") != row.get("storage_readback_sha256"):
            blockers.append(f"RAW_READBACK_MISMATCH:{row.get('entity_id')}:{row.get('kind')}")
    return blockers


def build_admission_decision(receipt: dict[str, Any]) -> dict[str, Any]:
    authority = receipt.get("authority") or {}
    if any(bool(v) for v in authority.values()):
        return _base_decision("BLOCKED_BY_AUTHORITY_LEAKAGE", ["ARCHIVE_RECEIPT_AUTHORITY_MUST_BE_ZERO"])

    readback_blockers = _raw_readback_blockers(receipt)
    if readback_blockers:
        return _base_decision("BLOCKED_BY_RAW_READBACK", sorted(set(readback_blockers)))

    entities = {str(row.get("entity_id")): row for row in receipt.get("entities") or []}
    expected_entities = set(REPRESENTATIVES.values())
    qualified_entities = set(str(x) for x in (receipt.get("qualified_entities") or []))

    contract = load_capital_efficiency_contract(CONTRACT_PATH)
    qualified_ids: list[str] = []
    coverage_blockers: list[str] = []
    candidates: list[dict[str, Any]] = []

    for cohort in REQUIRED_COHORTS:
        entity_id = REPRESENTATIVES[cohort]
        entity = entities.get(entity_id)
        if entity is None:
            coverage_blockers.append(f"MISSING_ENTITY:{entity_id}")
            continue
        if entity.get("qualification") != "QUALIFIED":
            for blocker in entity.get("blockers") or ["ENTITY_NOT_QUALIFIED"]:
                coverage_blockers.append(f"{entity_id}:{blocker}")
        derived = entity.get("derived") or {}
        for component in MANDATORY_COMPONENTS:
            metric_id = f"AIINFRA.CAPITAL_EFFICIENCY.{cohort}.{entity_id}.{component}"
            contract.metric_spec(metric_id)
            component_row = derived.get(component) or {}
            if entity.get("qualification") != "QUALIFIED" or component_row.get("qualified") is not True:
                coverage_blockers.append(f"UNQUALIFIED_METRIC:{metric_id}")
                continue
            latest_values = component_row.get("latest_four_values") or []
            latest_periods = component_row.get("latest_four_periods") or []
            latest_receipts = component_row.get("latest_four_receipts") or []
            if len(latest_values) != 4 or len(latest_periods) != 4 or len(latest_receipts) != 4:
                coverage_blockers.append(f"INCOMPLETE_DERIVED_LINEAGE:{metric_id}")
                continue
            qualified_ids.append(metric_id)
            core = {
                "metric_id": metric_id,
                "entity_id": entity_id,
                "cohort": cohort,
                "component": component,
                "periods": latest_periods,
                "values": latest_values,
                "calculation_receipts": latest_receipts,
                "authority": "RESEARCH",
            }
            candidates.append({**core, "content_hash": _canonical_hash(core)})

    if receipt.get("g6_coverage_status") != "FULL":
        coverage_blockers.append("RECEIPT_COVERAGE_NOT_FULL")
    if qualified_entities != expected_entities:
        coverage_blockers.append("QUALIFIED_ENTITY_SET_MISMATCH")

    if len(qualified_ids) != len(contract.metrics) or coverage_blockers:
        decision = _base_decision("BLOCKED_BY_COVERAGE", sorted(set(coverage_blockers)))
        decision["qualified_entities"] = sorted(qualified_entities)
        decision["qualified_metric_identities"] = len(qualified_ids)
        return decision

    mutation_plan = dedupe_by_content_hash(candidates)
    decision = _base_decision("READY_FOR_ADDITIVE_WRITE", [])
    decision.update({
        "g6_state": "PENDING_PHYSICAL_READBACK",
        "candidate_scope": CANDIDATE_FULL_SCOPE,
        "qualified_metric_identities": len(qualified_ids),
        "mutation_plan": mutation_plan,
        "mutation_count": len(mutation_plan),
        "physical_readback_required": True,
    })
    return decision


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a fail-closed YCI0-RP1 G6 admission decision.")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    decision = build_admission_decision(receipt)
    rendered = json.dumps(decision, ensure_ascii=False, sort_keys=True, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
