#!/usr/bin/env python3
"""QXM2 evidence-hardening structural and governance validator primitives.

QXM2 is an Evidence Staging Plane. This module validates machine-checkable
contracts only; it does not judge scientific truth or authorize Registry
admission, benchmark execution, capability promotion, or trading.
"""

EXPECTED_CANDIDATES = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]

EVIDENCE_ROLES = {
    "supports",
    "contradicts",
    "boundary",
    "competing_mechanism",
}

REPLICATION_STATES = {
    "direct_replication_supported",
    "extension_supported",
    "mixed",
    "failed",
    "not_found",
    "not_applicable",
}


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
        [
            "formal_benchmark_status",
            "benchmark_execution_authorized",
            "benchmark_pass_claim_authorized",
        ],
        "benchmark_seed",
    )
    assert seed["formal_benchmark_status"] == "not_created"
    assert seed["benchmark_execution_authorized"] is False
    assert seed["benchmark_pass_claim_authorized"] is False


def assert_no_authority_regression(obj):
    """Fail closed on explicit authority escalation in QXM2 staging objects."""
    prohibited_true = {
        "registry_admission_authorized",
        "hypothesis_preregistration_authorized",
        "formal_benchmark_creation_authorized",
        "benchmark_execution_authorized",
        "benchmark_pass_claim_authorized",
        "capability_promotion_authorized",
        "target_price_authorized",
        "recommended_weight_authorized",
        "position_size_authorized",
        "trading_action_authorized",
        "live_execution",
    }
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in prohibited_true:
                assert value is False, f"QXM2 authority escalation: {key}={value!r}"
            assert_no_authority_regression(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_no_authority_regression(value)


if __name__ == "__main__":
    print("QXM2 validator primitives loaded; full pack validation is added incrementally by the implementation plan.")
