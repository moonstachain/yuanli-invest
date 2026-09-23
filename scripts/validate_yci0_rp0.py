from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "yci0_rp0"

QUESTION_ID = "YCI0-RP0-CQ-001"
THEME = "AI_INFRA"
RESEARCH_AUTHORITY = "RESEARCH"
UNKNOWN = "UNKNOWN"

REQUIRED_METRIC_FAMILIES = {
    "US_10Y_NOMINAL_YIELD",
    "US_10Y_REAL_YIELD",
    "DXY_USD_PROXY",
    "HYPERSCALER_CAPEX",
    "HYPERSCALER_GUIDANCE",
    "NVDA_DATA_CENTER_REVENUE",
    "COMPUTE_SUPPLY_NORMALIZATION_PROXY",
    "NETWORKING_PROXY",
    "POWER_EQUIPMENT_PROXY",
    "POWER_AVAILABILITY_PROXY",
    "MARKET_PRICE",
    "VALUATION",
}
REQUIRED_METRIC_FIELDS = {
    "metric_id",
    "family",
    "source_type",
    "pit_policy",
    "required_timestamps",
    "admission_rule",
    "fallback",
}
REQUIRED_TIMESTAMPS = {
    "observed_at",
    "released_at",
    "known_as_of",
    "retrieved_at",
    "revised_at",
}
EXPECTED_CLOSED_SETS = {
    "authority": ["RESEARCH"],
    "evidence_status": ["PASS", "CURRENT_CONTEXT_ONLY", "BLOCKED", "UNKNOWN"],
    "reality_state": ["ACCELERATING", "STABLE", "DECELERATING", "MIXED", "UNKNOWN"],
    "narrative_stage": ["D0", "D1", "D2", "D3", "D4", "UNKNOWN"],
    "gate_status": ["OPEN", "PASS", "BLOCKED", "UNKNOWN", "NO_GO"],
}
EXPECTED_SYSTEM_ROLES = {
    "wind_structured_mcp": "SENSOR_EVIDENCE_ONLY",
    "wind_alice": "AUTHORED_KNOWLEDGE_CANDIDATE",
    "supabase": "REALITY_EVIDENCE_RUNTIME",
    "yuanli_brain": "CONTEXT_ROUTER",
    "ymq": "RESEARCH_COMPILER",
    "notion": "HUMAN_WORKBENCH",
}
REQUIRED_NON_AUTHORIZATIONS = {
    "CAPITAL_AUTHORITY",
    "EXECUTION_AUTHORITY",
    "SHADOW_AUTHORITY_EXPANSION",
    "BROKER_ACTION",
    "PORTFOLIO_SIZING_AUTOMATION",
    "REAL_CAPITAL_MOVEMENT",
}


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(
    question: dict[str, Any],
    reality_contract: dict[str, Any],
    metric_registry: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if question.get("question_id") != QUESTION_ID:
        errors.append("question:question_id_must_be_YCI0-RP0-CQ-001")
    if question.get("theme") != THEME:
        errors.append("question:theme_must_be_AI_INFRA")
    if question.get("authority") != RESEARCH_AUTHORITY:
        errors.append("question:authority_must_be_RESEARCH")
    if not _non_empty_text(question.get("prior_belief")):
        errors.append("question:prior_belief_required")
    if not _non_empty_text(question.get("defeat_condition")):
        errors.append("question:defeat_condition_required")
    if question.get("capital_authorized") is not False:
        errors.append("question:capital_authority_must_be_false")
    if question.get("execution_authorized") is not False:
        errors.append("question:execution_authority_must_be_false")

    if reality_contract.get("question_id") != QUESTION_ID:
        errors.append("reality_contract:question_id_mismatch")
    if reality_contract.get("closed_sets") != EXPECTED_CLOSED_SETS:
        errors.append("reality_contract:closed_sets_mismatch")
    if reality_contract.get("system_roles") != EXPECTED_SYSTEM_ROLES:
        errors.append("reality_contract:system_roles_mismatch")
    non_authorizations = reality_contract.get("explicitly_not_authorized", [])
    if not isinstance(non_authorizations, list) or not REQUIRED_NON_AUTHORIZATIONS.issubset(
        non_authorizations
    ):
        errors.append("reality_contract:explicit_non_authorizations_incomplete")
    required_laws = {
        "reality_over_belief",
        "claim_authority_lte_evidence_authority",
        "unknown_is_deny",
        "research_not_capital",
        "research_not_execution",
        "research_pass_not_capital_pass",
    }
    laws = reality_contract.get("laws", {})
    for law in sorted(required_laws):
        if laws.get(law) is not True:
            errors.append(f"reality_contract:law_required:{law}")

    if metric_registry.get("question_id") != QUESTION_ID:
        errors.append("metric_registry:question_id_mismatch")
    if metric_registry.get("authority") != RESEARCH_AUTHORITY:
        errors.append("metric_registry:authority_must_be_RESEARCH")
    metrics = metric_registry.get("metrics")
    if not isinstance(metrics, list):
        errors.append("metric_registry:metrics_must_be_list")
        metrics = []

    seen_ids: set[str] = set()
    families: set[str] = set()
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            errors.append(f"metric:index_{index}:definition_must_be_object")
            continue
        metric_id = metric.get("metric_id")
        label = metric_id if _non_empty_text(metric_id) else f"index_{index}"
        missing = REQUIRED_METRIC_FIELDS - set(metric)
        for field in sorted(missing):
            errors.append(f"metric:{label}:missing:{field}")
        if _non_empty_text(metric_id):
            if metric_id in seen_ids:
                errors.append(f"metric:{metric_id}:duplicate_metric_id")
            seen_ids.add(metric_id)
        family = metric.get("family")
        if _non_empty_text(family):
            families.add(family)
        if metric.get("fallback") != UNKNOWN:
            errors.append(f"metric:{label}:fallback_must_be_UNKNOWN")
        timestamps = metric.get("required_timestamps")
        if not isinstance(timestamps, list) or not REQUIRED_TIMESTAMPS.issubset(timestamps):
            errors.append(f"metric:{label}:required_timestamps_incomplete")
        for field in ("source_type", "pit_policy", "admission_rule"):
            if not _non_empty_text(metric.get(field)):
                errors.append(f"metric:{label}:{field}_required")

    for family in sorted(REQUIRED_METRIC_FAMILIES - families):
        errors.append(f"metric_registry:required_family_missing:{family}")

    return errors


def _load(name: str) -> dict[str, Any]:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


def main() -> int:
    errors = validate_contract(
        _load("ai_infra_question.v0.1.json"),
        _load("ai_infra_reality_contract.v0.1.json"),
        _load("wind_metric_registry.v0.1.json"),
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: YCI0-RP0 contracts and AI Infra metric registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
