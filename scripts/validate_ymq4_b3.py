#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/ymq4/gold_b3_dynamic_beta.v0.1.json"
SPEC = ROOT / "docs/superpowers/specs/2026-09-08-ymq4-b3-dynamic-beta-challenge-design.md"
PLAN = ROOT / "docs/superpowers/plans/2026-09-08-ymq4-b3-dynamic-beta-challenge.md"
RUNNER = ROOT / "scripts/ymq4_b3_dynamic_beta.py"
MIGRATION = ROOT / "supabase/migrations/20260908123000_ymq4_b3_dynamic_beta.sql"
TEST_UNIT = ROOT / "tests/test_ymq4_b3.py"
TEST_DB = ROOT / "tests/test_ymq4_b3_contract.py"
WORKFLOW = ROOT / ".github/workflows/ymq4-b3-dynamic-beta.yml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    required = [CONFIG, SPEC, PLAN, RUNNER, MIGRATION, TEST_UNIT, TEST_DB, WORKFLOW]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    require(not missing, f"missing B3 artifacts: {missing}")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    require(config["battle"] == "YMQ4-B3", "battle drift")
    require(config["status"] in {"authorized_pre_result_freeze", "reality_proof_pass"}, "status drift")
    require(config["panel_id"] == "gold_core_monthly_v0.1", "panel drift")
    require(config["input_integrity"]["expected_months"] == 584, "month count drift")
    require(config["input_integrity"]["expected_panel_rows"] == 2336, "panel row drift")
    require(config["input_integrity"]["future_leakage_tolerance"] == 0, "leakage tolerance drift")
    require(config["transformations_source"] == "YMQ4-B2", "B2 transformation reuse required")
    require(config["model"]["family"] == "rolling_ols", "model-family drift")
    require(config["model"]["window_months"] == 60, "rolling window drift")
    require(config["model"]["current_target_in_estimation"] is False, "current target must be excluded")
    require(config["model"]["window_search"] is False, "window search forbidden")
    require(config["oos"] == {"start": "2007-01-31", "end": "2026-08-31", "rows": 236}, "OOS drift")
    b2 = config["canonical_b2"]
    require(b2["reality_gate_run_id"] == "8907b60a-445c-4396-8e51-29e6f36620fb", "canonical B2 gate drift")
    require(abs(float(b2["rmse"]) - 3.7129313457620357) < 1e-12, "B2 RMSE drift")
    require(abs(float(b2["mae"]) - 2.9202089520079597) < 1e-12, "B2 MAE drift")
    require(config["victory_gate"] == {"rmse_lt_b2": True, "mae_lte_b2": True, "minimum_positive_rmse_blocks": 3}, "victory gate drift")

    runner = RUNNER.read_text(encoding="utf-8")
    lower = runner.lower()
    for token in (
        'BATTLE = "YMQ4-B3"',
        "WINDOW_MONTHS = 60",
        "CANONICAL_B2_GATE_ID",
        "B3_DYNAMIC_BETA_MATERIALIZED_PASS",
        "DYNAMIC_BETA_BEATS_B2",
        "DYNAMIC_BETA_DOES_NOT_BEAT_B2",
        '"b4_b7_executed": False',
        '"trading_action": False',
        "rolling_dynamic_predictions",
        "coefficient_state_sha",
    ):
        require(token in runner, f"runner missing frozen semantic: {token}")
    for forbidden in (
        "fit_kalman", "fit_tvp", "fit_dcc", "fit_hmm", "fit_regime_switch",
        "place_order(", "submit_order(", "broker.connect", "portfolio_size(",
    ):
        require(forbidden not in lower, f"forbidden B3/runtime token: {forbidden}")

    migration = MIGRATION.read_text(encoding="utf-8").lower()
    for token in (
        "public.ymq4_b3_read_b2_canonical",
        "public.ymq4_b3_record_gate",
        "8907b60a-445c-4396-8e51-29e6f36620fb",
        "b3_dynamic_beta_materialized_pass",
        "dynamic_beta_beats_b2",
        "dynamic_beta_does_not_beat_b2",
        "from public, anon, authenticated",
        "to service_role",
    ):
        require(token in migration, f"migration missing contract: {token}")
    require("grant select on runtime.reality_gate_runs" not in migration, "direct runtime table grant forbidden")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "YMQ4_SUPABASE_SECRET_KEY",
        "scripts/validate_ymq4_b3.py",
        "tests.test_ymq4_b3",
        "tests.test_ymq4_b3_contract",
        "B3_DYNAMIC_BETA_MATERIALIZED_PASS",
        "ymq4-b3-reality-receipt",
        "AUTHORIZED_YMQ4_B3_FULL_ONCE",
    ):
        require(token in workflow, f"workflow missing contract: {token}")

    all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in required)
    for pattern in (
        r"sb_secret_[A-Za-z0-9_-]{12,}",
        r"service_role\s*[:=]\s*['\"][A-Za-z0-9._-]{12,}",
        r"api_key=[A-Za-z0-9]{20,}",
    ):
        require(re.search(pattern, all_text, flags=re.I) is None, f"possible secret literal: {pattern}")

    if config["status"] == "reality_proof_pass":
        settlement = config.get("settlement", {})
        require(settlement.get("physical_status") == "B3_DYNAMIC_BETA_MATERIALIZED_PASS", "final physical settlement missing")
        require(settlement.get("scientific_observation") in {"DYNAMIC_BETA_BEATS_B2", "DYNAMIC_BETA_DOES_NOT_BEAT_B2"}, "final scientific settlement missing")
        receipt = ROOT / settlement.get("receipt", "")
        require(receipt.exists(), "canonical B3 receipt missing")

    print("YMQ4-B3 validator: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"YMQ4-B3 validator: FAIL: {exc}")
        raise SystemExit(1)
