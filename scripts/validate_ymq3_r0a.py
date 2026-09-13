from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any

from ymq3_r0a_evidence import case_evidence_verdict, program_evidence_verdict
from ymq3_r0a_source_probe import validate_probe_receipt

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "config" / "ymq3" / "r0a_evidence_gate.v0.1.json"
REGISTRY = ROOT / "config" / "ymq3" / "r0a_source_registry.v0.1.json"
STATUS = ROOT / "config" / "ymq3" / "r0a_case_evidence_status.v0.1.json"
PROBES = ROOT / "artifacts" / "ymq3" / "r0a" / "YMQ3-R0A-PROBE-20260913" / "source-probe-receipts.jsonl"
RECEIPT = ROOT / "artifacts" / "ymq3" / "r0a" / "YMQ3-R0A-PROBE-20260913" / "evidence-sufficiency-receipt.json"
DOCS = [
    ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-SOURCE-AUTHORITY-AUDIT-v0.1.md",
    ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-CASE-EVIDENCE-MATRIX-v0.1.md",
    ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-BLIND-ANNOTATION-PROTOCOL-v0.1.md",
    ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-EVIDENCE-SUFFICIENCY-DECISION-MEMO-v0.1.md",
    ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-HUMAN-REVIEW-CARD-v0.1.md",
]

EXPECTED_CASES = [
    ("C1_DOTCOM", "1999-01-01", "2002-12-31", "NARRATIVE_HEAVY"),
    ("C2_GFC", "2008-01-01", "2009-12-31", "ACUTE_SHOCK_HARD_NEGATIVE"),
    ("C3_CHINA_LEVERAGE", "2014-07-01", "2016-02-29", "NARRATIVE_HEAVY"),
    ("C4_COVID", "2020-01-01", "2020-12-31", "ACUTE_SHOCK_HARD_NEGATIVE"),
    ("C5_INFLATION", "2021-01-01", "2022-10-31", "MIXED_REALITY_NARRATIVE"),
    ("C6_AI", "2022-11-01", "2026-08-31", "NARRATIVE_HEAVY"),
]
EXPECTED_DOMAINS = ["MARKET", "MACRO_VINTAGE", "OFFICIAL_ANCHOR", "NARRATIVE_CORPUS", "LICENSE_RIGHTS", "PIT_PROVENANCE"]
EXPECTED_SOURCE_VERDICTS = ["ADMIT", "ANNOTATION_ONLY", "UNKNOWN_DENY", "REJECT"]
EXPECTED_TIMESTAMPS = ["TS1_SOURCE_NATIVE", "TS2_ARCHIVE_VERIFIED", "TS3_PROVIDER_INDEXED", "TS4_INFERRED_RETROSPECTIVE"]
EXPECTED_RIGHTS_AXES = ["processing_authority", "raw_storage_authority", "derived_feature_storage_authority", "redistribution_authority"]
EXPECTED_RIGHT_VALUES = ["ALLOW", "DENY", "UNKNOWN"]
EXPECTED_CASE_VERDICTS = ["READY", "READY_WITH_LIMITATIONS", "BLOCKED", "INDETERMINATE"]
EXPECTED_PROGRAM_VERDICTS = ["FULL6_READY", "OPEN4_READY", "INSUFFICIENT_EVIDENCE_INDETERMINATE", "PHYSICAL_FAIL"]
EXPECTED_NON_AUTH = [
    "SCIENTIFIC_PASS",
    "YMQ3_R1_FORWARD_SHADOW",
    "CAPITAL_ADMISSION",
    "PORTFOLIO_WEIGHTING",
    "POSITION_SIZING",
    "VEIGHNA_OR_BROKER_EXECUTION",
    "REAL_CAPITAL_MOVEMENT",
]
EXPECTED_SOURCE_IDS = [
    "FRED_ALFRED", "SEC_EDGAR", "FED_OFFICIAL", "WHO_OFFICIAL", "OPENAI_PRIMARY",
    "GDELT_2_GKG_MENTIONS", "GDELT_1_EVENTS", "GOOGLE_TRENDS", "GOOGLE_BOOKS_NGRAM",
    "INTERNET_ARCHIVE_WAYBACK", "CSRC_OFFICIAL", "PBOC_OFFICIAL", "NBS_OFFICIAL",
    "SSE_OFFICIAL", "SZSE_OFFICIAL", "CNINFO_DISCLOSURES", "LICENSED_EN_NEWS_ARCHIVE",
    "LICENSED_CN_FIN_NEWS_ARCHIVE",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_gate(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(GATE) if cfg is None else cfg
    require(cfg["identity"]["program_id"] == "YMQ3-R0A", "program id drift")
    actual_cases = [(c["case_id"], c["start_date"], c["end_date"], c["role"]) for c in cfg["cases"]]
    require(actual_cases == EXPECTED_CASES, "case contract drift")
    for left, right in zip(cfg["cases"], cfg["cases"][1:]):
        require(date.fromisoformat(left["end_date"]) < date.fromisoformat(right["start_date"]), "case windows overlap")
    require(cfg["mandatory_evidence_domains"] == EXPECTED_DOMAINS, "evidence domain drift")
    require(cfg["source_registry_verdicts"] == EXPECTED_SOURCE_VERDICTS, "source verdict drift")
    require(cfg["timestamp_authority_classes"] == EXPECTED_TIMESTAMPS, "timestamp class drift")
    require(cfg["rights_axes"] == EXPECTED_RIGHTS_AXES, "rights axes drift")
    require(cfg["rights_values"] == EXPECTED_RIGHT_VALUES, "rights values drift")
    require(cfg["unknown_rights_semantics"] == "DENY", "UNKNOWN rights must deny")
    require(cfg["public_readability_implies_storage_rights"] is False, "public readability cannot imply storage rights")
    require(cfg["story_time_rule"] == "publication_available_at <= canonical_week_end", "Story PIT rule drift")
    require(cfg["retrospective_timestamp_class"] == "TS4_INFERRED_RETROSPECTIVE", "retrospective class drift")
    require(cfg["retrospective_allowed_as_story_feature"] is False, "retrospective Story input enabled")
    require(cfg["current_revised_macro_can_substitute_historical_vintage"] is False, "revised macro substitution enabled")
    t = cfg["readiness_thresholds"]
    require(t["pit_violation_count"] == 0, "PIT violations must be zero")
    require(t["unknown_processing_rights_count"] == 0, "unknown processing rights must be zero")
    require(t["unauthorized_raw_storage_count"] == 0, "unauthorized raw storage must be zero")
    require(t["timestamp_authority_rate_min"] == 0.95, "timestamp threshold drift")
    require(t["scored_week_presence_rate_min"] == 0.80, "week presence threshold drift")
    require(t["median_eligible_documents_per_covered_week_min"] == 10, "documents/week threshold drift")
    require(t["multi_publisher_week_rate_min"] == 0.70, "multi-publisher threshold drift")
    require(t["distinct_publisher_groups_per_multi_publisher_week_min"] == 2, "publisher group threshold drift")
    require(t["narrative_heavy_requires_media_family"] is True, "narrative-heavy media requirement disabled")
    require(cfg["case_verdicts"] == EXPECTED_CASE_VERDICTS, "case verdict drift")
    require(cfg["program_verdicts"] == EXPECTED_PROGRAM_VERDICTS, "program verdict drift")
    require(cfg["multimodal_minimum"] == {"ready_cases_min": 4, "narrative_heavy_ready_min": 2, "acute_shock_hard_negative_ready_min": 1}, "multimodal minimum drift")
    require(cfg["non_authorizations"] == EXPECTED_NON_AUTH, "non-authorization drift")


def validate_registry(registry: dict[str, Any]) -> None:
    sources = registry["sources"]
    require([s["source_id"] for s in sources] == EXPECTED_SOURCE_IDS, "source registry membership/order drift")
    by_id = {s["source_id"]: s for s in sources}
    for source in sources:
        for axis in EXPECTED_RIGHTS_AXES:
            require(source[axis] in EXPECTED_RIGHT_VALUES, f"invalid rights value: {source['source_id']} {axis}")
        require(source["registry_verdict"] in EXPECTED_SOURCE_VERDICTS, f"invalid source verdict: {source['source_id']}")
        require(source["timestamp_authority"] in EXPECTED_TIMESTAMPS, f"invalid timestamp class: {source['source_id']}")
    for sid in ["LICENSED_EN_NEWS_ARCHIVE", "LICENSED_CN_FIN_NEWS_ARCHIVE"]:
        source = by_id[sid]
        require(source["registry_verdict"] == "UNKNOWN_DENY", f"{sid} admitted without contract")
        require(source["processing_authority"] == "UNKNOWN", f"{sid} processing right fabricated")
        require(source["machine_access"] == "UNVERIFIED", f"{sid} machine access fabricated")
    require(by_id["GDELT_1_EVENTS"]["story_role"] != "PRIMARY_NARRATIVE_TRUTH", "GDELT1 silently promoted to Story truth")
    require(by_id["GOOGLE_TRENDS"]["story_role"] != "PRIMARY_NARRATIVE_TRUTH", "Google Trends silently promoted to Story truth")
    require(by_id["GDELT_2_GKG_MENTIONS"]["historical_start"] == "2015-02-19", "GDELT2 historical start drift")


def validate_probes() -> list[dict[str, Any]]:
    receipts = [json.loads(line) for line in PROBES.read_text(encoding="utf-8").splitlines() if line.strip()]
    require([r["source_id"] for r in receipts] == EXPECTED_SOURCE_IDS, "probe receipt membership/order drift")
    for receipt in receipts:
        validate_probe_receipt(receipt)
    return receipts


def validate_case_status(status: dict[str, Any]) -> None:
    gate = load_json(GATE)
    case_verdicts: dict[str, str] = {}
    for item in status["cases"]:
        actual = case_evidence_verdict(item, gate=gate)
        require(actual == item["case_verdict"], f"case verdict not mechanically reproducible: {item['case_id']} {actual} != {item['case_verdict']}")
        case_verdicts[item["case_id"]] = actual
    program = program_evidence_verdict(case_verdicts, status["case_roles"], physical_fail=status["physical_fail"])
    require(program == status["program_verdict"], f"program verdict not mechanically reproducible: {program}")
    require(program == "INSUFFICIENT_EVIDENCE_INDETERMINATE", "current run may not be upgraded without new admitted evidence")
    require(status["ready_cases"] == [], "current run must contain zero READY cases")
    require(status["limited_cases"] == ["C4_COVID", "C5_INFLATION", "C6_AI"], "limited case set drift")
    require(status["blocked_cases"] == ["C1_DOTCOM", "C2_GFC", "C3_CHINA_LEVERAGE"], "blocked case set drift")
    require(status["next_stage_authorized"] == "REMEDIATION_ONLY", "R0 model execution accidentally authorized")
    require("YMQ3_R0_REALITY_AUDIT" in status["explicitly_not_authorized"], "R0 audit must remain unauthorized")
    require("YMQ3_R1_FORWARD_SHADOW" in status["explicitly_not_authorized"], "R1 must remain unauthorized")


def validate_docs() -> None:
    for path in DOCS:
        require(path.exists(), f"missing Human projection: {path}")
        text = path.read_text(encoding="utf-8")
        require("YMQ3-R0A" in text, f"wrong doc identity: {path}")
    memo = DOCS[3].read_text(encoding="utf-8")
    require("INSUFFICIENT_EVIDENCE_INDETERMINATE" in memo, "decision memo hides machine verdict")
    require("Scientific model status:** `NOT_RUN`" in memo, "decision memo must state model not run")
    blind = DOCS[2].read_text(encoding="utf-8")
    require("BLIND_ANNOTATION_EXECUTION = NOT_AUTHORIZED" in blind, "blind annotation execution should be blocked")


def validate_final_receipt_if_present(status: dict[str, Any]) -> None:
    if not RECEIPT.exists():
        return
    receipt = load_json(RECEIPT)
    required = [
        "run_id", "code_sha", "gate_version", "registry_hash", "source_probe_receipt_hash",
        "weekly_coverage_hash", "case_verdicts", "program_verdict", "blocked_reasons",
        "ready_cases", "limited_cases", "blocked_cases", "indeterminate_cases",
        "pit_violation_count", "rights_violation_count", "non_authorizations", "artifact_hash",
    ]
    for field in required:
        require(field in receipt, f"receipt missing field: {field}")
    require(receipt["program_verdict"] == status["program_verdict"], "receipt program verdict drift")
    require(receipt["case_verdicts"] == {c["case_id"]: c["case_verdict"] for c in status["cases"]}, "receipt case verdict drift")
    require(receipt["ready_cases"] == status["ready_cases"], "receipt READY set drift")
    require(receipt["limited_cases"] == status["limited_cases"], "receipt limited set drift")
    require(receipt["blocked_cases"] == status["blocked_cases"], "receipt blocked set drift")
    require(receipt["indeterminate_cases"] == status["indeterminate_cases"], "receipt indeterminate set drift")
    require(receipt["pit_violation_count"] == 0, "receipt contains PIT integrity failure")
    require(receipt["rights_violation_count"] == 0, "receipt contains rights integrity failure")
    require(receipt["weekly_coverage_hash"] == "NOT_MATERIALIZED", "current run must not fabricate weekly coverage artifact")
    require("YMQ3_R0_REALITY_AUDIT" in receipt["non_authorizations"], "receipt accidentally authorizes R0")
    require("YMQ3_R1_FORWARD_SHADOW" in receipt["non_authorizations"], "receipt accidentally authorizes R1")
    require(isinstance(receipt["artifact_hash"], str) and receipt["artifact_hash"].startswith("sha256:") and len(receipt["artifact_hash"]) == 71, "invalid receipt artifact hash")


def main() -> None:
    for path in [GATE, REGISTRY, STATUS, PROBES]:
        require(path.exists(), f"missing R0A artifact: {path}")
    validate_gate()
    registry = load_json(REGISTRY)
    validate_registry(registry)
    validate_probes()
    status = load_json(STATUS)
    validate_case_status(status)
    validate_docs()
    validate_final_receipt_if_present(status)
    print("YMQ3-R0A evidence settlement: PASS")


if __name__ == "__main__":
    main()
