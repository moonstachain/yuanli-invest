from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "ymq3" / "r0a_evidence_gate.v0.1.json"

VALID_STORY_TIMESTAMP_CLASSES = {"TS1_SOURCE_NATIVE", "TS2_ARCHIVE_VERIFIED", "TS3_PROVIDER_INDEXED"}
MANDATORY_DOMAINS = ["MARKET", "MACRO_VINTAGE", "OFFICIAL_ANCHOR", "NARRATIVE_CORPUS", "LICENSE_RIGHTS", "PIT_PROVENANCE"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_gate() -> dict[str, Any]:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(dt.tzinfo is not None, f"timestamp must be timezone-aware: {value}")
    return dt


def validate_evidence_row(row: dict[str, Any], gate: dict[str, Any] | None = None, registry: dict[str, Any] | None = None) -> None:
    gate = load_gate() if gate is None else gate
    required = [
        "case_id", "document_id", "source_id", "publisher_group_id", "week_end",
        "publication_available_at", "timestamp_authority", "processing_authority",
        "raw_payload_stored", "raw_storage_authority", "eligible_for_story",
    ]
    for field in required:
        require(field in row, f"missing evidence field: {field}")
    require(row["case_id"] in {c["case_id"] for c in gate["cases"]}, "unknown case")
    require(bool(row["document_id"]), "document_id required")
    require(bool(row["publisher_group_id"]), "publisher_group_id required")
    require(row["processing_authority"] in gate["rights_values"], "invalid processing authority")
    require(row["raw_storage_authority"] in gate["rights_values"], "invalid raw storage authority")

    week_end = parse_time(row["week_end"])
    available = parse_time(row["publication_available_at"])
    require(available <= week_end, "future publication entered historical week")

    if row["eligible_for_story"]:
        require(row["timestamp_authority"] in VALID_STORY_TIMESTAMP_CLASSES, "retrospective/unknown timestamp cannot enter Story")
        require(row["processing_authority"] == "ALLOW", "Story processing right must be ALLOW")
    if row["raw_payload_stored"]:
        require(row["raw_storage_authority"] == "ALLOW", "raw payload stored without ALLOW authority")

    if registry is not None:
        source = {s["source_id"]: s for s in registry["sources"]}.get(row["source_id"])
        require(source is not None, "source missing from authority registry")
        require(source["processing_authority"] == row["processing_authority"], "row processing authority disagrees with registry")
        require(source["raw_storage_authority"] == row["raw_storage_authority"], "row raw-storage authority disagrees with registry")


def canonical_fridays(start_date: str, end_date: str) -> list[date]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    delta = (4 - start.weekday()) % 7
    current = start + timedelta(days=delta)
    out: list[date] = []
    while current <= end:
        out.append(current)
        current += timedelta(days=7)
    return out


def weekly_coverage(rows: list[dict[str, Any]], case: dict[str, Any]) -> dict[str, Any]:
    relevant = [r for r in rows if r.get("case_id") == case["case_id"]]
    for row in relevant:
        validate_evidence_row(row)

    weeks = canonical_fridays(case["start_date"], case["end_date"])
    by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for row in relevant:
        if not row["eligible_for_story"]:
            continue
        w = parse_time(row["week_end"]).date()
        if date.fromisoformat(case["start_date"]) <= w <= date.fromisoformat(case["end_date"]):
            by_week[w].append(row)

    covered = [w for w in weeks if by_week.get(w)]
    eligible_counts = [len(by_week[w]) for w in covered]
    multi = 0
    for w in covered:
        groups = {r["publisher_group_id"] for r in by_week[w]}
        if len(groups) >= 2:
            multi += 1
    total_rows = sum(eligible_counts)
    authoritative_rows = sum(1 for w in covered for r in by_week[w] if r["timestamp_authority"] in VALID_STORY_TIMESTAMP_CLASSES)
    return {
        "case_id": case["case_id"],
        "total_scored_weeks": len(weeks),
        "covered_weeks": len(covered),
        "scored_week_presence_rate": (len(covered) / len(weeks)) if weeks else 0.0,
        "eligible_documents": total_rows,
        "median_eligible_documents_per_covered_week": median(eligible_counts) if eligible_counts else 0,
        "multi_publisher_weeks": multi,
        "multi_publisher_week_rate": (multi / len(covered)) if covered else 0.0,
        "timestamp_authority_rate": (authoritative_rows / total_rows) if total_rows else 0.0,
        "publisher_group_count": len({r["publisher_group_id"] for w in covered for r in by_week[w]}),
    }


def case_evidence_verdict(stats: dict[str, Any], mandatory_domains: list[str] | None = None, gate: dict[str, Any] | None = None) -> str:
    gate = load_gate() if gate is None else gate
    mandatory_domains = MANDATORY_DOMAINS if mandatory_domains is None else mandatory_domains
    if stats.get("blocked_reasons"):
        return "BLOCKED"
    if any(stats.get(k, 0) > 0 for k in ["pit_violation_count", "unknown_processing_rights_count", "unauthorized_raw_storage_count"]):
        return "BLOCKED"
    domains = stats.get("domain_statuses", {})
    if any(domains.get(d) in {"FAIL", "BLOCKED"} for d in mandatory_domains):
        return "BLOCKED"
    if not stats.get("coverage_materialized", False):
        return "READY_WITH_LIMITATIONS" if any(domains.get(d) in {"PASS", "PARTIAL", "PATH_EXISTS_NOT_MEASURED"} for d in mandatory_domains) else "INDETERMINATE"
    if any(domains.get(d) != "PASS" for d in mandatory_domains):
        return "READY_WITH_LIMITATIONS"

    t = gate["readiness_thresholds"]
    checks = [
        stats.get("pit_violation_count", 0) == t["pit_violation_count"],
        stats.get("unknown_processing_rights_count", 0) == t["unknown_processing_rights_count"],
        stats.get("unauthorized_raw_storage_count", 0) == t["unauthorized_raw_storage_count"],
        stats.get("timestamp_authority_rate", 0.0) >= t["timestamp_authority_rate_min"],
        stats.get("scored_week_presence_rate", 0.0) >= t["scored_week_presence_rate_min"],
        stats.get("median_eligible_documents_per_covered_week", 0) >= t["median_eligible_documents_per_covered_week_min"],
        stats.get("multi_publisher_week_rate", 0.0) >= t["multi_publisher_week_rate_min"],
    ]
    role = stats.get("case_role")
    if role == "NARRATIVE_HEAVY" and t["narrative_heavy_requires_media_family"]:
        checks.append(stats.get("narrative_media_family_present", False) is True)
    return "READY" if all(checks) else "READY_WITH_LIMITATIONS"


def program_evidence_verdict(case_verdicts: dict[str, str], case_roles: dict[str, str], physical_fail: bool = False) -> str:
    if physical_fail:
        return "PHYSICAL_FAIL"
    ready = [c for c, verdict in case_verdicts.items() if verdict == "READY"]
    if len(case_verdicts) == 6 and len(ready) == 6:
        return "FULL6_READY"
    narrative_ready = sum(1 for c in ready if case_roles.get(c) == "NARRATIVE_HEAVY")
    shock_ready = sum(1 for c in ready if case_roles.get(c) == "ACUTE_SHOCK_HARD_NEGATIVE")
    if len(ready) >= 4 and narrative_ready >= 2 and shock_ready >= 1:
        return "OPEN4_READY"
    return "INSUFFICIENT_EVIDENCE_INDETERMINATE"
