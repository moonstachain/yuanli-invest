#!/usr/bin/env python3
"""Fail-closed validation for A5 Force Triangle Gold Reconstruction.

A5 is a point-in-time reconstruction layer, not Outcome acceptance. This validator
protects the A4 pre-registration boundary and rejects obvious hindsight leakage.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECON_DIR = ROOT / "reconstructions" / "force-triangle"
FREEZE = RECON_DIR / "a5-evidence-freeze-v0.1.json"

PRE_REGISTRATION_COMMIT = "392e4230493f7e860360defdbda82c0c61c48285"
EXPECTED_CASES = {
    "FT-GR-PC-1995": {
        "t0": "1995-08-09",
        "file": "pc-internet-1995.v0.1.json",
        "force": "unknown",
    },
    "FT-GR-MOBILE-2008": {
        "t0": "2008-07-10",
        "file": "mobile-internet-2008.v0.1.json",
        "force": "golden_extreme",
    },
    "FT-GR-AI-2023": {
        "t0": "2023-02-01",
        "file": "ai-2023.v0.1.json",
        "force": "unknown",
    },
}

ALLOWED_ELIGIBILITY = {
    "eligible_pending_vault_capture",
    "same_day_timestamp_review",
    "excluded_post_t0",
    "discovery_only",
}

PROHIBITED_KEYS = {
    "outcome",
    "outcomes",
    "realized_return",
    "realized_returns",
    "return_20d",
    "return_60d",
    "return_120d",
    "return_250d",
    "returns",
    "future_financials",
    "future_revenue",
    "future_profit",
    "target_price",
    "position",
    "position_size",
    "trade_action",
}


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_day(value: str) -> date:
    return date.fromisoformat(value[:10])


def walk_keys(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key
            yield from walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_keys(child, f"{path}[{index}]")


def source_index(freeze: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    result: dict[str, tuple[str, dict[str, Any]]] = {}
    for case in freeze["cases"]:
        case_id = case["case_id"]
        expected = EXPECTED_CASES.get(case_id)
        if not expected:
            raise ValueError(f"unexpected case in evidence freeze: {case_id}")
        if case["t0"] != expected["t0"]:
            raise ValueError(f"{case_id}: T0 drift {case['t0']} != {expected['t0']}")
        t0 = parse_day(case["t0"])
        for source in case["sources"]:
            source_id = source["source_id"]
            if source_id in result:
                raise ValueError(f"duplicate source_id: {source_id}")
            eligibility = source["eligibility"]
            if eligibility not in ALLOWED_ELIGIBILITY:
                raise ValueError(f"{source_id}: invalid eligibility {eligibility}")
            published = parse_day(source["published_at"])
            if eligibility == "eligible_pending_vault_capture" and published > t0:
                raise ValueError(f"{source_id}: post-T0 source marked eligible")
            if eligibility == "same_day_timestamp_review" and published != t0:
                raise ValueError(f"{source_id}: same-day review source not on T0")
            if eligibility == "excluded_post_t0" and published <= t0:
                raise ValueError(f"{source_id}: excluded_post_t0 is not post-T0")
            result[source_id] = (case_id, source)
    return result


def validate_packet(packet: dict[str, Any], expected: dict[str, str], sources: dict[str, tuple[str, dict[str, Any]]]) -> None:
    case_id = packet["case_id"]
    if packet.get("packet_type") != "ForceTriangleGoldReconstruction":
        raise ValueError(f"{case_id}: wrong packet_type")
    if packet.get("status") != "candidate_reconstruction":
        raise ValueError(f"{case_id}: status must remain candidate_reconstruction")
    if packet.get("t0") != expected["t0"]:
        raise ValueError(f"{case_id}: T0 drift")
    if packet.get("pre_registration_commit") != PRE_REGISTRATION_COMMIT:
        raise ValueError(f"{case_id}: pre-registration commit drift")
    if packet.get("outcome_locked") is not True:
        raise ValueError(f"{case_id}: Outcome must remain locked")
    if packet.get("force", {}).get("classification") != expected["force"]:
        raise ValueError(
            f"{case_id}: unexpected A5 candidate classification "
            f"{packet.get('force', {}).get('classification')!r}"
        )

    for object_path, key in walk_keys(packet):
        if key.lower() in PROHIBITED_KEYS:
            raise ValueError(f"{case_id}: prohibited hindsight/output key {object_path}.{key}")

    used = packet.get("source_ids_used", [])
    pending = packet.get("source_ids_pending_same_day_review", [])
    excluded = packet.get("source_ids_excluded_post_t0", [])
    discovery = packet.get("source_ids_discovery_only", [])
    all_refs = used + pending + excluded + discovery
    if len(all_refs) != len(set(all_refs)):
        raise ValueError(f"{case_id}: source referenced in multiple eligibility buckets")

    for source_id in used:
        if source_id not in sources:
            raise ValueError(f"{case_id}: missing source {source_id}")
        source_case, source = sources[source_id]
        if source_case != case_id:
            raise ValueError(f"{case_id}: cross-case source reference {source_id}")
        if source["eligibility"] != "eligible_pending_vault_capture":
            raise ValueError(f"{case_id}: used source {source_id} is not eligible")

    for source_id in pending:
        if source_id not in sources or sources[source_id][0] != case_id:
            raise ValueError(f"{case_id}: invalid pending source {source_id}")
        if sources[source_id][1]["eligibility"] != "same_day_timestamp_review":
            raise ValueError(f"{case_id}: pending source {source_id} not marked same-day review")

    for source_id in excluded:
        if source_id not in sources or sources[source_id][0] != case_id:
            raise ValueError(f"{case_id}: invalid excluded source {source_id}")
        if sources[source_id][1]["eligibility"] != "excluded_post_t0":
            raise ValueError(f"{case_id}: excluded source {source_id} not marked post-T0")

    for source_id in discovery:
        if source_id not in sources or sources[source_id][0] != case_id:
            raise ValueError(f"{case_id}: invalid discovery source {source_id}")
        if sources[source_id][1]["eligibility"] != "discovery_only":
            raise ValueError(f"{case_id}: discovery source {source_id} not discovery_only")

    # A5's most important anti-hindsight guard: the famous 100m-user claim is
    # post-T0 and may be listed only as excluded, never as evidence used.
    if case_id == "FT-GR-AI-2023":
        if "FTSRC-AI-004" in used or "FTSRC-AI-004" in pending:
            raise ValueError("AI case: post-T0 100m-user source leaked into reconstruction")
        if "FTSRC-AI-004" not in excluded:
            raise ValueError("AI case: explicit post-T0 100m-user exclusion missing")


def main() -> int:
    freeze = load(FREEZE)
    if freeze.get("pre_registration_commit") != PRE_REGISTRATION_COMMIT:
        raise ValueError("evidence freeze pre-registration commit drift")
    if freeze.get("outcome_locked") is not True:
        raise ValueError("evidence freeze must lock Outcome")
    if freeze.get("evidence_admission") != "blocked_unassigned_evidence_reviewer":
        raise ValueError("A5 may not imply Evidence admission")

    cases = {case["case_id"] for case in freeze["cases"]}
    if cases != set(EXPECTED_CASES):
        raise ValueError(f"evidence freeze cases mismatch: {sorted(cases)}")

    sources = source_index(freeze)
    packets: dict[str, dict[str, Any]] = {}
    for case_id, expected in EXPECTED_CASES.items():
        packet = load(RECON_DIR / expected["file"])
        if packet.get("case_id") != case_id:
            raise ValueError(f"{expected['file']}: wrong case_id")
        validate_packet(packet, expected, sources)
        packets[case_id] = packet

    print(
        "gold_reconstruction=valid "
        f"cases={len(packets)} sources={len(sources)} "
        "outcome_locked=true evidence_admission=blocked"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"gold_reconstruction_validation_error: {exc}", file=sys.stderr)
        raise SystemExit(1)
