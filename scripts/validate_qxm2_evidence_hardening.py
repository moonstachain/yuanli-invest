#!/usr/bin/env python3
"""Validate the QXM2 Evidence-First Shadow Admission staging pack.

Machine validation is intentionally limited to structural, referential, schema,
point-in-time, and governance properties. It does not judge scientific truth
and cannot authorize Registry admission, hypothesis preregistration, formal
benchmark creation/execution, capability promotion, or trading.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

EXPECTED_CANDIDATES = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]

EXPECTED_BENCHMARK_SEEDS = {
    "QXM2-BSEED-P003-DRIVER-OOS",
    "QXM2-BSEED-P004-CASH-CONVERSION",
    "QXM2-BSEED-R01-CREDIT-TRANSMISSION",
    "QXM2-BSEED-V01-EXPECTATION-DECOMPOSITION",
    "QXM2-BSEED-S004-STRESS-EXIT",
    "QXM2-BSEED-CROSS001-RETURN-ATTRIBUTION",
}

EXPECTED_ADMISSION_RECOMMENDATIONS = {
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION": "advance_with_boundary",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY": "advance_with_boundary",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION": "advance_with_boundary",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE": "interpretation_only",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY": "advance_with_boundary",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION": "advance_with_boundary",
}

EVIDENCE_ROLES = {"supports", "contradicts", "boundary", "competing_mechanism"}
REPLICATION_STATES = {
    "direct_replication_supported",
    "extension_supported",
    "mixed",
    "failed",
    "not_found",
    "not_applicable",
}

PROHIBITED_PREFIXES = (
    "registry/theories/",
    "registry/hypotheses/",
    "registry/benchmarks/",
    "registry/capabilities/",
    "canon/",
)

APPROVED_STATES = {
    "shadow_compilation_started": "QXM2_SOURCE_VERIFICATION",
    "source_verification_complete": "QXM2_MECHANISM_COMPILATION",
    "mechanism_compilation_complete": "QXM2_MACHINE_QUALIFICATION",
    "shadow_admission_ready_for_human_review": "QXM2_HUMAN_REVIEW",
    "human_accepted_ready_for_merge": "QXM2_MERGE",
    "accepted_merged": "QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION",
}

QXM1_MERGE_COMMIT = "81bf6d83da7463e31c58e2d35bcabc291b580546"
QXM2_ACCEPTANCE_TOKEN = "ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"
QXM2_REVIEWED_HEAD = "cecbdee29f888a6d9ee5041af5e1ad6d6965fb54"
QXM2_REVIEWED_RUN_NUMBER = 217
QXM2_REVIEWED_RUN_ID = 32461754235


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(obj, fields, context="object"):
    missing = [field for field in fields if field not in obj]
    assert not missing, f"{context} missing fields: {missing}"


def assert_expected_candidate_ids(ids):
    assert ids == EXPECTED_CANDIDATES, ids


def assert_evidence_role(role):
    assert role in EVIDENCE_ROLES, role


def assert_replication_status(status):
    assert status in REPLICATION_STATES, status


def assert_shadow_hypothesis_state(status):
    assert status == "proposed", status


def assert_benchmark_seed_authority(seed):
    require_fields(
        seed,
        ["formal_benchmark_status", "benchmark_execution_authorized", "benchmark_pass_claim_authorized"],
        "benchmark_seed",
    )
    assert seed["formal_benchmark_status"] == "not_created"
    assert seed["benchmark_execution_authorized"] is False
    assert seed["benchmark_pass_claim_authorized"] is False


def assert_no_prohibited_paths(paths):
    offenders = [path for path in paths if path.startswith(PROHIBITED_PREFIXES)]
    assert not offenders, f"QXM2 prohibited formal-authority paths changed: {offenders}"


def assert_no_authority_regression(obj):
    """Fail closed on explicit authority escalation in QXM2 staging objects."""
    prohibited_true = {
        "registry_admission",
        "registry_admission_authorized",
        "hypothesis_preregistration_authorized",
        "formal_benchmark_creation_authorized",
        "benchmark_execution_authorized",
        "benchmark_pass_claim_authorized",
        "benchmark_passed",
        "capability_promotion",
        "capability_promotion_authorized",
        "target_price_authorized",
        "recommended_weight_authorized",
        "position_size_authorized",
        "trading_action_authorized",
        "live_execution",
    }
    prohibited_nonfalse = {
        "target_price",
        "recommended_weight",
        "position_size",
        "buy_sell_instruction",
    }
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in prohibited_true:
                assert value is False, f"QXM2 authority escalation: {key}={value!r}"
            if key in prohibited_nonfalse:
                assert value in (None, False, "none", "not_authorized"), f"QXM2 action authority: {key}={value!r}"
            assert_no_authority_regression(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_no_authority_regression(value)


def assert_no_scalar_admission_score(obj):
    forbidden_keys = {
        "paper_count_score",
        "evidence_score",
        "admission_score",
        "scalar_evidence_score",
        "theory_score",
    }
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert key not in forbidden_keys, f"paper-count/scalar admission scoring prohibited: {key}"
            assert_no_scalar_admission_score(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_no_scalar_admission_score(value)


def assert_human_acceptance_receipt(receipt):
    require_fields(
        receipt,
        [
            "stage",
            "decision",
            "pr_number",
            "reviewed_head_sha",
            "reviewed_ci",
            "boundaries_preserved",
            "merge_authority",
        ],
        "QXM2 Human Acceptance receipt",
    )
    assert receipt["stage"] == "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"
    assert receipt["decision"] == QXM2_ACCEPTANCE_TOKEN
    assert receipt["pr_number"] == 38
    assert receipt["reviewed_head_sha"] == QXM2_REVIEWED_HEAD
    reviewed_ci = receipt["reviewed_ci"]
    assert reviewed_ci["run_number"] == QXM2_REVIEWED_RUN_NUMBER
    assert reviewed_ci["run_id"] == QXM2_REVIEWED_RUN_ID
    for key in ("conclusion", "contracts", "governance", "qxm2_evidence_hardening", "unit_tests"):
        assert reviewed_ci[key] == "success", (key, reviewed_ci[key])
    boundaries = receipt["boundaries_preserved"]
    for key in (
        "merge_authorized",
        "registry_admission_authorized",
        "hypothesis_preregistration_authorized",
        "formal_benchmark_creation_authorized",
        "benchmark_execution_authorized",
        "benchmark_pass_claim_authorized",
        "capability_promotion_authorized",
        "trading_action_authorized",
        "live_execution",
    ):
        assert boundaries[key] is False, (key, boundaries[key])
    assert receipt["merge_authority"] == "not_implied_by_acceptance"
    if "per_candidate_admission_recommendations" in receipt:
        assert receipt["per_candidate_admission_recommendations"] == EXPECTED_ADMISSION_RECOMMENDATIONS
    assert_no_authority_regression(receipt)


def _pull_request_changed_paths(root: Path):
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return []
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def validate_qxm2(root: Path):
    root = Path(root)
    qxm2 = root / "docs" / "architecture" / "qxm2"

    paths = {
        "state": qxm2 / "QXM2-STATE.json",
        "sources": qxm2 / "QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json",
        "evidence": qxm2 / "QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json",
        "crosswalk": qxm2 / "QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json",
        "theories": qxm2 / "QXM2-SHADOW-THEORY-OBJECTS-v0.1.json",
        "hypotheses": qxm2 / "QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json",
        "seeds": qxm2 / "QXM2-BENCHMARK-SEEDS-v0.1.json",
    }
    for label, path in paths.items():
        assert path.exists(), f"missing QXM2 {label}: {path}"

    state = load_json(paths["state"])
    sources_doc = load_json(paths["sources"])
    evidence_doc = load_json(paths["evidence"])
    crosswalk_doc = load_json(paths["crosswalk"])
    theories_doc = load_json(paths["theories"])
    hypotheses_doc = load_json(paths["hypotheses"])
    seeds_doc = load_json(paths["seeds"])

    acceptance_path = qxm2 / "QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
    acceptance_receipt = load_json(acceptance_path) if acceptance_path.exists() else None
    if acceptance_receipt is not None:
        assert_human_acceptance_receipt(acceptance_receipt)

    qxm1_state = load_json(root / "docs" / "architecture" / "qxm1" / "QXM1-STATE.json")
    assert qxm1_state["status"] == "accepted_merged"
    assert qxm1_state["merge_commit"] == QXM1_MERGE_COMMIT
    assert qxm1_state["next_gate"] == "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"

    assert state["stage"] == "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"
    assert state["candidate_count"] == 6
    assert state["status"] in APPROVED_STATES, state["status"]
    assert state["next_gate"] == APPROVED_STATES[state["status"]], (state["status"], state["next_gate"])
    assert state["upstream_dependency"]["resolved"] is True
    assert state["upstream_dependency"]["merge_commit"] == QXM1_MERGE_COMMIT
    assert state["admission_authority"] == "none"
    assert state["hypothesis_preregistration_authority"] == "none"
    assert state["formal_benchmark_creation_authority"] == "none"
    assert state["benchmark_execution_authority"] == "none"
    assert state["capability_promotion_authority"] == "none"

    if state["status"] in {"human_accepted_ready_for_merge", "accepted_merged"}:
        assert acceptance_receipt is not None, "accepted QXM2 state requires Human Acceptance receipt"
        human_gate = state["human_gate"]
        assert human_gate["token"] == QXM2_ACCEPTANCE_TOKEN
        assert human_gate["decision"] == QXM2_ACCEPTANCE_TOKEN
        assert human_gate["acceptance_receipt"] == "docs/architecture/qxm2/QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
        assert human_gate["reviewed_head_sha"] == QXM2_REVIEWED_HEAD
        assert human_gate["reviewed_ci_run"] == QXM2_REVIEWED_RUN_NUMBER
        assert state["post_acceptance_ci_required"] is True
        assert state["post_acceptance_ci_satisfied"] is True
        if state["status"] == "human_accepted_ready_for_merge":
            assert state["merge_authority"] == "not_implied_by_acceptance"

    sources = sources_doc["sources"]
    relations = evidence_doc["relations"]
    claims = crosswalk_doc["claims"]
    shadow_theories = theories_doc["shadow_theories"]
    shadow_hypotheses = hypotheses_doc["shadow_hypotheses"]
    benchmark_seeds = seeds_doc["benchmark_seeds"]

    candidate_ids = set()
    for source in sources:
        candidate_ids.update(source["candidate_ids"])
    candidate_ids.update(r["candidate_id"] for r in relations)
    candidate_ids.update(c["candidate_id"] for c in claims)
    candidate_ids.update(h["candidate_id"] for h in shadow_hypotheses)
    candidate_ids.update(s["candidate_id"] for s in benchmark_seeds)
    assert candidate_ids == set(EXPECTED_CANDIDATES), sorted(candidate_ids)

    relation_by_id = {r["relation_id"]: r for r in relations}
    assert len(relation_by_id) == len(relations), "duplicate EvidenceRelation ID"
    source_ids = {s["source_id"] for s in sources}

    relation_required = [
        "relation_id", "candidate_id", "claim_id", "mechanism_id", "source_id",
        "source_class", "original_or_secondary", "publication_year", "role",
        "identification_strength", "direction", "magnitude_relevance", "sample_domain",
        "geography", "asset_class", "period", "frequency", "replication_status",
        "external_validity", "known_failures", "pit_usable", "observable_mapping",
        "benchmark_relevance", "what_it_supports", "what_it_does_not_support",
    ]
    for relation in relations:
        require_fields(relation, relation_required, relation.get("relation_id", "EvidenceRelation"))
        assert relation["candidate_id"] in EXPECTED_CANDIDATES
        assert relation["source_id"] in source_ids, relation["relation_id"]
        assert_evidence_role(relation["role"])
        assert_replication_status(relation["replication_status"])
        assert isinstance(relation["pit_usable"], bool)
        assert relation["observable_mapping"], relation["relation_id"]
        assert str(relation["what_it_supports"]).strip()
        assert str(relation["what_it_does_not_support"]).strip()

    claim_ids = {c["claim_id"] for c in claims}
    assert len(claim_ids) == len(claims), "duplicate claim ID"
    hypothesis_ids = {
        obj["hypothesis_object"]["hypothesis_id"] for obj in shadow_hypotheses
    }
    seed_ids = {seed["benchmark_seed_id"] for seed in benchmark_seeds}
    for candidate_id in EXPECTED_CANDIDATES:
        anchors = [
            s for s in sources
            if candidate_id in s["candidate_ids"]
            and s["authority_class"] != "normative_accounting_standard"
        ]
        assert len(anchors) >= 2, f"{candidate_id}: <2 theory/seminal anchors"
        candidate_relations = [r for r in relations if r["candidate_id"] == candidate_id]
        assert any(r["role"] == "supports" and r["identification_strength"] != "theoretical_only" for r in candidate_relations), candidate_id
        assert any(r["role"] in {"boundary", "contradicts", "competing_mechanism"} for r in candidate_relations), candidate_id
        candidate_claims = [c for c in claims if c["candidate_id"] == candidate_id]
        assert 3 <= len(candidate_claims) <= 6, (candidate_id, len(candidate_claims))
        assert sum(candidate_id in obj["candidate_targets"] for obj in shadow_theories) >= 2, candidate_id
        assert sum(obj["candidate_id"] == candidate_id for obj in shadow_hypotheses) >= 2, candidate_id
        assert sum(seed["candidate_id"] == candidate_id for seed in benchmark_seeds) == 1, candidate_id

    for claim in claims:
        require_fields(
            claim,
            ["claim_id", "candidate_id", "statement", "mechanism_ids", "support_relation_ids", "boundary_relation_ids", "observable_set", "falsifier", "shadow_hypothesis_ids", "benchmark_seed_ids"],
            claim.get("claim_id", "claim"),
        )
        assert str(claim["statement"]).strip()
        assert claim["mechanism_ids"]
        assert claim["observable_set"]
        assert str(claim["falsifier"]).strip()
        assert claim["support_relation_ids"]
        assert claim["boundary_relation_ids"]
        for relation_id in claim["support_relation_ids"]:
            assert relation_id in relation_by_id, (claim["claim_id"], relation_id)
            assert relation_by_id[relation_id]["role"] == "supports"
        for relation_id in claim["boundary_relation_ids"]:
            assert relation_id in relation_by_id, (claim["claim_id"], relation_id)
            assert relation_by_id[relation_id]["role"] in {"boundary", "contradicts", "competing_mechanism"}
        for hypothesis_id in claim["shadow_hypothesis_ids"]:
            assert hypothesis_id in hypothesis_ids, (claim["claim_id"], hypothesis_id)
        for seed_id in claim["benchmark_seed_ids"]:
            assert seed_id in seed_ids, (claim["claim_id"], seed_id)

    theory_schema = load_json(root / "packages" / "contracts" / "schemas" / "theory-object.schema.json")
    hypothesis_schema = load_json(root / "packages" / "contracts" / "schemas" / "hypothesis-object.schema.json")
    theory_validator = Draft202012Validator(theory_schema)
    hypothesis_validator = Draft202012Validator(hypothesis_schema)

    for obj in shadow_theories:
        require_fields(obj, ["shadow_object_id", "admission_state", "admission_readiness", "candidate_targets", "theory_object", "verification", "admission_authority"], obj.get("shadow_object_id", "shadow_theory"))
        assert obj["admission_state"] == "shadow_only"
        assert obj["admission_authority"] == "none"
        theory_id = obj["theory_object"]["theory_id"]
        assert not theory_id.startswith("THEORY-QIN"), theory_id
        assert "IAS7" not in theory_id, theory_id
        theory_validator.validate(obj["theory_object"])

    for obj in shadow_hypotheses:
        require_fields(obj, ["shadow_object_id", "candidate_id", "admission_state", "hypothesis_object", "admission_authority"], obj.get("shadow_object_id", "shadow_hypothesis"))
        assert obj["admission_state"] == "shadow_only"
        assert obj["admission_authority"] == "none"
        hypothesis_validator.validate(obj["hypothesis_object"])
        assert_shadow_hypothesis_state(obj["hypothesis_object"]["status"])
        assert obj["hypothesis_object"]["point_in_time_requirement"] is True
        assert str(obj["hypothesis_object"]["null_hypothesis"]).strip()
        assert str(obj["hypothesis_object"]["falsification_rule"]).strip()

    assert seed_ids == EXPECTED_BENCHMARK_SEEDS, seed_ids
    seed_required = [
        "benchmark_seed_id", "candidate_id", "hypothesis_id", "target", "horizon",
        "candidate_model", "simpler_baselines", "pit_requirement", "oos_requirement",
        "regime_holdout", "primary_metrics", "failure_metrics", "known_leakage_risks",
        "multiple_testing_risk",
    ]
    for seed in benchmark_seeds:
        require_fields(seed, seed_required, seed.get("benchmark_seed_id", "benchmark_seed"))
        assert seed["hypothesis_id"] in hypothesis_ids
        assert seed["simpler_baselines"]
        assert seed["pit_requirement"]
        assert seed["oos_requirement"]
        assert seed["regime_holdout"]
        assert_benchmark_seed_authority(seed)

    docs_to_check = [state, sources_doc, evidence_doc, crosswalk_doc, theories_doc, hypotheses_doc, seeds_doc]
    if acceptance_receipt is not None:
        docs_to_check.append(acceptance_receipt)
    for doc in docs_to_check:
        assert_no_authority_regression(doc)
        assert_no_scalar_admission_score(doc)

    if state["status"] != "accepted_merged":
        changed_paths = _pull_request_changed_paths(root)
        if changed_paths:
            assert_no_prohibited_paths(changed_paths)

    return {
        "candidate_count": len(EXPECTED_CANDIDATES),
        "source_count": len(sources),
        "evidence_relation_count": len(relations),
        "claim_count": len(claims),
        "shadow_theory_count": len(shadow_theories),
        "shadow_hypothesis_count": len(shadow_hypotheses),
        "benchmark_seed_count": len(benchmark_seeds),
        "registry_admissions": 0,
        "status": state["status"],
    }


def main():
    root = Path(__file__).resolve().parents[1]
    result = validate_qxm2(root)
    print(
        "QXM2 evidence hardening validation passed: "
        f"{result['candidate_count']} candidates, {result['source_count']} sources, "
        f"{result['evidence_relation_count']} evidence relations, {result['claim_count']} claims, "
        f"{result['shadow_theory_count']} shadow theories, {result['shadow_hypothesis_count']} shadow hypotheses, "
        f"{result['benchmark_seed_count']} non-executable benchmark seeds; Registry admissions=0; "
        f"status={result['status']}."
    )


if __name__ == "__main__":
    main()
