#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/ymq4/gold_b2_fixed_beta.v0.1.json"
SPEC = ROOT / "docs/superpowers/specs/2026-09-08-ymq4-b2-fixed-beta-oos-design.md"
PLAN = ROOT / "docs/superpowers/plans/2026-09-08-ymq4-b2-fixed-beta-oos.md"
AUTH = ROOT / "docs/architecture/ymq4/YMQ4-B2-AUTHORIZATION-v0.1.md"
RECEIPT = ROOT / "docs/architecture/ymq4/YMQ4-B2-REALITY-RECEIPT-v0.1.md"
RUNNER = ROOT / "scripts/ymq4_b2_fixed_beta.py"
MIGRATION = ROOT / "supabase/migrations/20260908070000_ymq4_b2_fixed_beta.sql"
READBACK_FIX = ROOT / "supabase/migrations/20260908070500_ymq4_b2_read_panel_json_aggregate.sql"
TEST_UNIT = ROOT / "tests/test_ymq4_b2.py"
TEST_DB = ROOT / "tests/test_ymq4_b2_contract.py"
WORKFLOW = ROOT / ".github/workflows/ymq4-b2-fixed-beta.yml"
DP1A_WORKFLOW = ROOT / ".github/workflows/ymq4-dp1a-reality-proof.yml"
ONE_SHOT = ROOT / ".ymq4/authorizations/YMQ4-B2-FULL"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    required = [
        CONFIG, SPEC, PLAN, AUTH, RECEIPT, RUNNER, MIGRATION, READBACK_FIX,
        TEST_UNIT, TEST_DB, WORKFLOW, DP1A_WORKFLOW,
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    require(not missing, f"missing B2 artifacts: {missing}")
    require(not ONE_SHOT.exists(), "consumed B2 one-shot authorization marker must not remain")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    require(config["battle"] == "YMQ4-B2", "battle mismatch")
    require(config["status"] == "reality_proof_pass", "B2 settlement status drift")
    require(config["panel_id"] == "gold_core_monthly_v0.1", "panel mismatch")
    integrity = config["input_integrity"]
    require(integrity["expected_months"] == 584, "expected months drift")
    require(integrity["expected_panel_rows"] == 2336, "expected panel rows drift")
    require(integrity["future_leakage_tolerance"] == 0, "leakage tolerance must be zero")
    require(integrity["expected_factors"] == ["gold_usd_oz", "usd", "inflation_yoy", "real_rate"], "factor contract drift")
    split = config["split"]
    require(split == {
        "train_start": "1978-02-28",
        "train_end": "2006-12-31",
        "train_rows": 347,
        "oos_start": "2007-01-31",
        "oos_end": "2026-08-31",
        "oos_rows": 236,
    }, "frozen split drift")
    require(config["model"]["family"] == "fixed_ols", "B2 must remain fixed OLS")
    require(config["model"]["coefficient_reestimation_in_oos"] is False, "OOS coefficient re-estimation forbidden")
    require(config["b3_incrementality_gate"]["minimum_positive_rmse_blocks"] == 3, "B3 block gate drift")
    settlement = config["settlement"]
    require(settlement["gate_status"] == "B2_BASELINE_MATERIALIZED_PASS", "gate settlement drift")
    require(settlement["economic_observation"] == "FIXED_BETA_BEATS_NULL", "economic observation drift")
    require(settlement["reality_gate_run_id"] == "8907b60a-445c-4396-8e51-29e6f36620fb", "canonical gate id drift")

    runner = RUNNER.read_text(encoding="utf-8")
    runner_lower = runner.lower()
    for token in (
        'BATTLE = "YMQ4-B2"',
        'PANEL_ID = "gold_core_monthly_v0.1"',
        "B2_BASELINE_MATERIALIZED_PASS",
        "FIXED_BETA_BEATS_NULL",
        "FIXED_BETA_DOES_NOT_BEAT_NULL",
        "coefficient_vectors_fitted",
        '"b3_b7_executed": False',
        '"trading_action": False',
        "np.linalg.lstsq",
    ):
        require(token in runner, f"runner missing frozen semantic: {token}")
    for forbidden in (
        "fit_rolling_beta", "fit_tvp_beta", "fit_kalman_beta", "fit_regime_switching",
        "rolling_beta(", "tvp_beta(", "kalman_filter(", "regime_switching(",
        "place_order(", "submit_order(", "broker.connect", "portfolio_size(",
    ):
        require(forbidden not in runner_lower, f"forbidden B3/trading runtime token: {forbidden}")

    migration = MIGRATION.read_text(encoding="utf-8").lower()
    for token in (
        "public.ymq4_b2_read_panel", "public.ymq4_b2_record_gate",
        "pit.decision_asof_values", "runtime.reality_gate_runs", "'ymq4-b2'",
        "from public, anon, authenticated", "to service_role",
    ):
        require(token in migration, f"migration missing contract: {token}")
    require("grant select on pit.decision_asof_values" not in migration, "direct PIT table grant forbidden")

    readback_fix = READBACK_FIX.read_text(encoding="utf-8").lower()
    for token in (
        "drop function if exists public.ymq4_b2_read_panel(text)",
        "create function public.ymq4_b2_read_panel",
        "returns jsonb",
        "jsonb_agg",
        "order by decision_date, factor_id",
        "from public, anon, authenticated",
        "to service_role",
    ):
        require(token in readback_fix, f"readback fix missing contract: {token}")
    require("grant select on pit.decision_asof_values" not in readback_fix, "readback fix direct PIT grant forbidden")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "YMQ4_SUPABASE_SECRET_KEY",
        "scripts/validate_ymq4_b2.py",
        "tests.test_ymq4_b2",
        "tests.test_ymq4_b2_contract",
        "B2_BASELINE_MATERIALIZED_PASS",
        "ymq4-b2-reality-receipt",
        "github.event_name == 'workflow_dispatch' && inputs.mode == 'full'",
    ):
        require(token in workflow, f"workflow missing contract: {token}")
    require("YMQ4-B2-FULL" not in workflow, "B2 durable workflow must not retain one-shot PR marker")

    dp1a_workflow = DP1A_WORKFLOW.read_text(encoding="utf-8")
    require("YMQ4-B2-FULL" not in dp1a_workflow, "temporary B2 marker path leaked into DP1-A workflow")
    require("b2-full-baseline" not in dp1a_workflow, "temporary B2 execution carrier leaked into DP1-A workflow")
    require("b2-preflight" not in dp1a_workflow, "temporary B2 preflight carrier leaked into DP1-A workflow")

    receipt = RECEIPT.read_text(encoding="utf-8")
    for token in (
        "B2_BASELINE_MATERIALIZED_PASS",
        "8907b60a-445c-4396-8e51-29e6f36620fb",
        "FIXED_BETA_BEATS_NULL",
        "2,336",
        "347",
        "236",
        "B3-B7",
    ):
        require(token in receipt, f"receipt missing settlement evidence: {token}")

    all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in required)
    for pattern in (
        r"sb_secret_[A-Za-z0-9_-]{12,}",
        r"service_role\s*[:=]\s*['\"][A-Za-z0-9._-]{12,}",
        r"api_key=[A-Za-z0-9]{20,}",
    ):
        require(re.search(pattern, all_text, flags=re.I) is None, f"possible secret literal: {pattern}")

    print("YMQ4-B2 validator: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"YMQ4-B2 validator: FAIL: {exc}")
        raise SystemExit(1)
