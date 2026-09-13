from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "config" / "ymq3" / "r0a_evidence_gate.v0.1.json"

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


def main() -> None:
    require(GATE.exists(), f"missing gate config: {GATE}")
    validate_gate()
    print("YMQ3-R0A evidence gate: PASS")


if __name__ == "__main__":
    main()
