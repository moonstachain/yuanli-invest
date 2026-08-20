#!/usr/bin/env python3
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
OUT = ARCH / "CANON-STATUS.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    r0 = load(ARCH / "r0" / "R0-STATE.json")
    r1 = load(ARCH / "r1" / "R1-STATE.json")
    r2 = load(ARCH / "r2" / "R2-STATE.json")
    r21 = load(ARCH / "r2_1" / "R2-1-STATE.json")
    r21r = load(ARCH / "r2_1" / "R2-1-MERGE-RECEIPT-v0.1.json")
    r22 = load(ARCH / "r2_2" / "R2-2-STATE.json")
    r22r = load(ARCH / "r2_2" / "R2-2-MERGE-RECEIPT-v0.1.json")
    r23 = load(ARCH / "r2_3" / "R2-3-STATE.json")
    r23r = load(ARCH / "r2_3" / "R2-3-MERGE-RECEIPT-v0.1.json")
    r23a = load(ARCH / "r2_3a" / "R2-3A-STATE.json")
    r23ar = load(ARCH / "r2_3a" / "R2-3A-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json")

    return {
        "schema_version": "0.9.0",
        "projection_semantics": "deterministic_non_authoritative_projection",
        "factual_authority": "immutable_receipts_and_external_git_runtime_facts",
        "mission": "Yuanli Investment Research Intelligence Canon",
        "north_star": "Compile investment knowledge into reality-tested, machine-callable research intelligence.",
        "objective": "Lifetime Right-Tail Capture under Survival Constraints",
        "center_object": "ResearchCapability",
        "canonical_state": "ResearchStateVector",
        "os_model": "one_core_three_worlds_three_gates_one_loop",
        "human_navigation": "势信极_真价生",
        "architecture_extensions": {
            "P": {"human_subspaces": ["P.capital", "P.asset"]},
            "R": "typed_machine_decomposition_and_context_for_P.capital_not_fourth_human_world",
            "authority_ladder": "L0-L4_cross_asset",
            "asset_router": "A0_asset_form_plus_A1_pricing_archetype",
            "Xs": "Structural_Asymmetry_Source_with_asset_specific_implementations",
            "research_portfolio_split": "governance_authority_split_not_X_semantic_split",
        },
        "operational_canon": {
            "repository": "moonstachain/quant-workspace",
            "authority": "A9",
            "switch_authorized": False,
        },
        "stages": {
            "R0": {"status": "accepted_merged", "merge_commit": r0["merge_commit_sha"]},
            "R1": {"status": r1["status"], "merge_commit": r1["merge_commit"]},
            "R2": {
                "status": r2["status"],
                "merge_commit": r2["merge_commit"],
                "historical_gold_capabilities": r2["capability_count"],
                "registry_objects": r2["registry_entry_count"],
                "canon_entries": r2["canon_entry_count"],
            },
            "R2_1": {
                "status": r21["status"],
                "merge_commit": r21["merge_commit"],
                "merge_receipt": "docs/architecture/r2_1/R2-1-MERGE-RECEIPT-v0.1.json",
            },
            "R2_2": {
                "status": r22["status"],
                "merge_commit": r22["merge_commit"],
                "merge_receipt": "docs/architecture/r2_2/R2-2-MERGE-RECEIPT-v0.1.json",
                "purpose": "Research Intelligence Canon Re-foundation",
            },
            "R2_3": {
                "status": r23["status"],
                "purpose": "Runtime Blocker Closure",
                "merge_commit": r23["merge_commit"],
                "merge_receipt": r23["merge_receipt"],
            },
            "R2_3A": {
                "status": r23a["status"],
                "purpose": r23a["purpose"],
                "human_gate": r23a["human_gate"]["token"],
                "human_gate_decision": r23a["human_gate"]["decision"],
                "human_acceptance_receipt": r23a["human_gate"]["acceptance_receipt"],
                "human_review_qualification": r23a["human_review_qualification"],
                "upstream_dependency_resolved": r23a["upstream_dependency"]["resolved"],
                "machine_qualification": r23a["machine_qualification"],
                "merge_authority": r23a["merge_authority"],
                "post_acceptance_ci_required": r23a["post_acceptance_ci_required"],
            },
            "R3A": {
                "status": "paused_not_started",
                "reason": "await_r2_3a_merge",
            },
            "R4A": {"status": "not_authorized", "purpose": "Benchmark Closure"},
        },
        "constitutional_invariants": {
            "x_semantics": "X := (Xs, Xa, Xp)",
            "xs_mother_concept": "Structural Asymmetry Source",
            "value_control_point_role": "equity_specialized_implementation",
            "r_is_fourth_human_world": False,
            "asset_form_is_not_pricing_model": True,
            "scalar_pnx_force_macro_score": "prohibited",
            "evidence_role": "horizontal_claim_control_plane",
            "claim_authority_cannot_exceed_evidence_authority": True,
            "lower_level_truth_does_not_imply_higher_level_authorization": True,
            "research_portfolio_split_changes_x_semantics": False,
            "ledger_law": "receipt_is_ledger_status_is_projection",
            "live_execution": "unavailable_by_design",
        },
        "r2_3_successor_candidates": {
            "effective_vnext_gold_count_after_acceptance": r23["effective_gold_count_after_acceptance"],
            "V": r23["successors"]["V"],
            "S": r23["successors"]["S"],
            "other_r2_gold_identities_mutated": r23["scope_guard"]["other_r2_gold_identities_mutated"],
        },
        "r2_3a_architecture": {
            "base_os_model": r23a["base_os_model"],
            "human_navigation": r23a["human_navigation"],
            "extensions": r23a["architecture_extensions"],
            "router": r23a["router"],
            "capability_priority": r23a["capability_priority"],
            "cross_asset_stress_check": r23a["cross_asset_stress_check"],
            "x_semantics_preserved_across_os_split": r23a["constitutional_invariants"]["research_portfolio_split_does_not_change_x_semantics"],
            "n02_latency_policy_required_in_r2_3b": r23a["r2_3b_contract_requirements"]["n02_reunderwrite_latency_policy_required"],
        },
        "r2_3a_acceptance_fact": {
            "pr": r23ar["pr_number"],
            "decision": r23ar["decision"],
            "reviewed_head": r23ar["reviewed_head_sha"],
            "reviewed_ci_run": r23ar["reviewed_ci"]["run_number"],
            "merge_authority": r23ar["merge_authority"],
        },
        "admission": {
            "evidence": "not_authorized",
            "outcome": "not_authorized",
            "rsi_promotion": "not_authorized",
        },
        "r2_1_merge_fact": {
            "pr": r21r["pr_number"],
            "merge_commit": r21r["merge_commit_sha"],
            "post_acceptance_ci_run": r21r["post_acceptance_ci"]["run_number"],
        },
        "r2_2_merge_fact": {
            "pr": r22r["pr_number"],
            "merge_commit": r22r["merge_commit_sha"],
            "post_acceptance_ci_run": r22r["post_acceptance_ci"]["run_number"],
        },
        "r2_3_merge_fact": {
            "pr": r23r["pr_number"],
            "merge_commit": r23r["merge_commit_sha"],
            "merge_method": r23r["merge_method"],
            "post_acceptance_ci_run": r23r["post_acceptance_ci"]["run_number"],
        },
        "pending_gate_chain": [r23a["next_gate"]],
        "next_gate": r23a["next_gate"],
    }


def render(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        actual = OUT.read_text(encoding="utf-8")
        if actual != expected:
            raise SystemExit("CANON-STATUS projection drift: run python scripts/build_canon_status.py")
        print("CANON-STATUS projection: PASS")
        return
    OUT.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
