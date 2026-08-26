#!/usr/bin/env python3
"""Fail-closed validation for YQS0 Supabase Sovereign Research Kernel architecture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YQS0 = ROOT / "docs" / "architecture" / "yqs0"

EXPECTED_SCHEMAS = {
    "core",
    "evidence",
    "pit",
    "quant",
    "runtime",
    "replay",
    "governance",
    "projection",
}
EXPECTED_OBJECTS = {
    "core.research_targets",
    "core.engine_theses",
    "core.position_passports",
    "core.book_states",
    "evidence.sources",
    "evidence.source_snapshots",
    "evidence.claims",
    "evidence.evidence_links",
    "pit.observations",
    "pit.feature_records",
    "pit.data_lineage",
    "quant.factor_definitions",
    "quant.factor_states",
    "runtime.run_receipts",
    "replay.replay_cases",
    "replay.settlements",
    "governance.authority_events",
    "projection.change_queue",
}
EXPECTED_ROLES = {
    "principal",
    "researcher",
    "quant_worker",
    "reviewer",
    "viewer",
    "system",
}
EXPECTED_PIT_CLOCKS = {
    "recorded_at",
    "known_as_of",
    "knowledge_cutoff",
    "replay_cutoff",
}


def load_json(name: str) -> dict:
    with (YQS0 / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_inventory() -> None:
    inventory = load_json("YQS0-OBJECT-INVENTORY-v0.1.json")
    schemas = set(inventory["application_schemas"])
    require(inventory["schema_count"] == 8, "YQS0 must freeze exactly eight schemas")
    require(schemas == EXPECTED_SCHEMAS, f"schema set mismatch: {schemas ^ EXPECTED_SCHEMAS}")
    require("public" not in schemas, "public cannot be a YQS0 application-domain schema")

    objects = inventory["objects"]
    names = [item["object"] for item in objects]
    require(inventory["object_count"] == 18, "YQS0 must freeze exactly eighteen core objects")
    require(len(names) == 18, "object inventory length must be eighteen")
    require(len(names) == len(set(names)), "duplicate YQS0 object identity")
    require(set(names) == EXPECTED_OBJECTS, f"object set mismatch: {set(names) ^ EXPECTED_OBJECTS}")
    require({item["schema"] for item in objects} == EXPECTED_SCHEMAS, "every schema must contain at least one frozen object")
    require(all(item.get("canon_authority") is False for item in objects), "Supabase object cannot claim Canon authority")

    invariants = inventory["global_invariants"]
    for field in (
        "public_schema_is_application_domain",
        "me1_object_semantics_redefined",
        "live_execution_authorized",
        "portfolio_weight_authorized",
        "position_sizing_authorized",
        "operational_canon_switch_authorized",
        "me2_me5_authorized",
    ):
        require(invariants.get(field) is False, f"inventory authority regression: {field}")
    require(invariants.get("all_objects_canon_authority_false") is True, "Canon authority invariant missing")


def validate_pit_law() -> None:
    pit = load_json("YQS0-PIT-LAW-v0.1.json")
    require(set(pit["required_clocks"]) == EXPECTED_PIT_CLOCKS, "PIT required clocks mismatch")
    require(pit["eligibility_rule"] == "known_as_of <= knowledge_cutoff <= replay_cutoff", "PIT eligibility law changed")
    laws = pit["laws"]
    require(len(laws) == 10, "YQS0 PIT law must contain ten fail-closed laws")
    require(all(item.get("fail_closed") is True for item in laws), "all PIT laws must fail closed")
    require(pit.get("replay_direct_table_access_authorized") is False, "direct replay table access cannot be authorized")
    require(pit.get("future_leakage_authorized") is False, "future leakage cannot be authorized")

    law_text = " ".join(item["rule"] for item in laws).lower()
    require("recorded_at cannot substitute for known_as_of" in law_text, "recorded_at/known_as_of distinction missing")
    require("latest-value overwrite is prohibited" in law_text, "revision overwrite prohibition missing")
    require("historical reconstruction" in law_text, "historical reconstruction rule missing")


def validate_rls() -> None:
    rls = load_json("YQS0-RLS-AUTHORITY-MATRIX-v0.1.json")
    require(set(rls["roles"]) == EXPECTED_ROLES, "RLS role set mismatch")
    principles = rls["principles"]
    require(principles.get("default_deny") is True, "RLS must default deny")
    require(principles.get("least_privilege") is True, "RLS must be least privilege")
    for field in (
        "service_role_frontend_exposure",
        "database_role_can_create_github_acceptance_receipt",
        "database_role_can_merge_github",
        "research_pass_implies_capital_pass",
        "live_execution_authorized",
    ):
        require(principles.get(field) is False, f"RLS authority regression: {field}")

    hard_denies = {item["role"]: set(item["deny"]) for item in rls["hard_denies"]}
    for role in ("quant_worker", "system"):
        require("human_approval" in hard_denies.get(role, set()), f"{role} must hard-deny human approval")
        require("live_execution" in hard_denies.get(role, set()), f"{role} must hard-deny live execution")
    require(not rls["matrix"]["governance"]["quant_worker"], "quant_worker cannot write/read governance authority ledger by default")


def validate_worker_contract() -> None:
    worker = load_json("YQS0-QUANT-WORKER-CONTRACT-v0.1.json")
    require(worker["control_plane"] == "Supabase", "Supabase must remain control plane")
    require(worker["compute_plane"] == "external_quant_worker", "heavy compute must remain external")
    require(worker.get("heavy_compute_in_edge_functions") is False, "Edge Functions cannot become quant HPC")
    require(worker.get("live_execution_authorized") is False, "worker contract cannot authorize live execution")
    declaration = worker["authority_declaration"]
    require(declaration and all(value is False for value in declaration.values()), "worker authority declaration must deny Canon/capital/execution authority")
    require(worker["write_boundary"].get("github_canon_write") is False, "worker cannot write GitHub Canon")
    require(worker["write_boundary"].get("governance_human_event_write") is False, "worker cannot write human governance events")
    conditions = set(worker["fail_closed_conditions"])
    require("missing knowledge_cutoff for replay" in conditions, "replay cutoff failure condition missing")
    require("attempted live execution or broker action" in conditions, "live execution failure condition missing")


def validate_stage_state() -> None:
    state = load_json("YQS0-STATE.json")
    require(state["stage"] == "YQS0_SUPABASE_SOVEREIGN_RESEARCH_KERNEL_ARCHITECTURE", "wrong YQS0 stage identity")
    require(state["human_gate"] == "ACCEPT_YQS0_SUPABASE_SOVEREIGN_RESEARCH_KERNEL_ARCHITECTURE", "wrong human gate token")
    require(state["merge_authority"] == "not_implied_by_acceptance", "acceptance cannot imply merge")
    auth = state["implementation_authority"]
    require(auth and all(value is False for value in auth.values()), "YQS0 candidate must not grant implementation/successor authority")
    frozen = state["frozen_candidate_decisions"]
    require(frozen["application_schema_count"] == 8, "state schema count mismatch")
    require(frozen["core_object_count"] == 18, "state object count mismatch")
    require(frozen["reuse_yuanli_health_project"] is False, "investment runtime cannot reuse health project")
    require(frozen["pit_safe_access_required"] is True, "PIT-safe access must be required")


def validate_architecture_text() -> None:
    text = (YQS0 / "YQS0-SUPABASE-SOVEREIGN-RESEARCH-KERNEL-ARCHITECTURE-v0.1.md").read_text(encoding="utf-8")
    required_phrases = [
        "GitHub        = WHAT IS LEGAL",
        "Supabase      = WHAT IS CURRENT",
        "Quant Runtime = WHAT IS COMPUTED",
        "Human Gate    = WHAT IS AUTHORIZED",
        "Supabase has operational state authority; GitHub retains normative Canon authority.",
        "No live execution.",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"architecture phrase missing: {phrase}")


def main() -> None:
    validate_inventory()
    validate_pit_law()
    validate_rls()
    validate_worker_contract()
    validate_stage_state()
    validate_architecture_text()
    print("YQS0 Supabase Sovereign Research Kernel validation: PASS")


if __name__ == "__main__":
    main()
