#!/usr/bin/env python3
"""YMQ4-B3 minimal rolling dynamic-beta Reality Challenge."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from scripts import ymq4_b2_fixed_beta as b2

BATTLE = "YMQ4-B3"
PANEL_ID = b2.PANEL_ID
WINDOW_MONTHS = 60
EXPECTED_OOS_ROWS = b2.EXPECTED_OOS_ROWS
CANONICAL_B2_GATE_ID = "8907b60a-445c-4396-8e51-29e6f36620fb"
B2_RMSE = 3.7129313457620357
B2_MAE = 2.9202089520079597
B2_BLOCK_RMSE = {
    "gfc_2007_2009": 4.735405232228532,
    "post_gfc_2010_2019": 3.280590575419435,
    "covid_rates_2020_2022": 3.1050742795420367,
    "current_2023_2026": 4.284300249030305,
}
MIN_POSITIVE_BLOCKS = 3


def rolling_dynamic_predictions(
    transformed: list[dict[str, Any]], *, start_index: int, window: int = WINDOW_MONTHS
) -> list[dict[str, Any]]:
    if window != WINDOW_MONTHS:
        raise ValueError(f"window drift: {window} != {WINDOW_MONTHS}")
    if start_index < window:
        raise ValueError("insufficient history for frozen rolling window")
    states: list[dict[str, Any]] = []
    for idx in range(start_index, len(transformed)):
        current = transformed[idx]
        estimation = transformed[idx - window : idx]
        if len(estimation) != window:
            raise ValueError("rolling estimation row-count drift")
        if estimation[-1]["decision_date"] >= current["decision_date"]:
            raise ValueError("current-month target leaked into coefficient estimation")
        coefficients = b2.fit_ols(estimation)
        prediction = b2.predict([current], coefficients)[0]
        states.append({
            "decision_date": current["decision_date"],
            "known_as_of": current["known_as_of"],
            "estimation_start": estimation[0]["decision_date"],
            "estimation_end": estimation[-1]["decision_date"],
            "estimation_rows": len(estimation),
            "coefficients": coefficients,
            "prediction": float(prediction),
            "actual": float(current["gold_return"]),
        })
    return states


def coefficient_state_sha(states: list[dict[str, Any]]) -> str:
    payload = [
        {
            "decision_date": state["decision_date"],
            "coefficients": state["coefficients"],
        }
        for state in states
    ]
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compare_to_b2(
    dynamic: dict[str, Any], b2_baseline: dict[str, Any], *, minimum_positive_blocks: int = MIN_POSITIVE_BLOCKS
) -> dict[str, Any]:
    improvements = {
        name: 1.0 - float(dynamic["blocks"][name]) / float(b2_baseline["blocks"][name])
        for name in b2_baseline["blocks"]
    }
    positive = sum(value > 0.0 for value in improvements.values())
    rmse_pass = float(dynamic["rmse"]) < float(b2_baseline["rmse"])
    mae_pass = float(dynamic["mae"]) <= float(b2_baseline["mae"])
    blocks_pass = positive >= minimum_positive_blocks
    return {
        "rmse_pass": rmse_pass,
        "mae_pass": mae_pass,
        "blocks_pass": blocks_pass,
        "positive_rmse_blocks": positive,
        "minimum_positive_rmse_blocks": minimum_positive_blocks,
        "block_rmse_improvement_vs_b2": improvements,
        "beats_b2": rmse_pass and mae_pass and blocks_pass,
    }


def _validate_canonical_b2(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError("canonical B2 RPC returned unexpected shape")
    if payload.get("run_id") != CANONICAL_B2_GATE_ID:
        raise RuntimeError("canonical B2 gate id mismatch")
    if payload.get("battle_id") != "YMQ4-B2":
        raise RuntimeError("canonical B2 battle mismatch")
    if payload.get("gate_status") != "B2_BASELINE_MATERIALIZED_PASS":
        raise RuntimeError("canonical B2 physical status mismatch")
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        raise RuntimeError("canonical B2 receipt missing")
    fixed = receipt.get("oos", {}).get("fixed_beta", {})
    if abs(float(fixed.get("rmse")) - B2_RMSE) > 1e-12:
        raise RuntimeError("canonical B2 RMSE drift")
    if abs(float(fixed.get("mae")) - B2_MAE) > 1e-12:
        raise RuntimeError("canonical B2 MAE drift")
    for name, expected in B2_BLOCK_RMSE.items():
        actual = float(receipt.get("oos_blocks", {}).get(name, {}).get("fixed", {}).get("rmse"))
        if abs(actual - expected) > 1e-12:
            raise RuntimeError(f"canonical B2 block drift: {name}")
    return receipt


def _oos_start_index(transformed: list[dict[str, Any]]) -> int:
    target = b2.OOS_START.isoformat()
    for idx, row in enumerate(transformed):
        if row["decision_date"] == target:
            return idx
    raise RuntimeError("B2 OOS start date absent from transformed history")


def main() -> int:
    started = datetime.now(timezone.utc)
    sb_url = b2.require_env("SUPABASE_URL")
    sb_key = b2.require_env("YMQ4_SUPABASE_SECRET_KEY")
    git_sha = os.getenv("GITHUB_SHA", "LOCAL")

    rows = b2.rpc(sb_url, sb_key, "ymq4_b2_read_panel", {"p_panel_id": PANEL_ID})
    if not isinstance(rows, list):
        raise RuntimeError("panel RPC returned unexpected shape")
    b2.validate_panel(rows)
    transformed = b2.build_transformed_rows(rows)
    start_index = _oos_start_index(transformed)
    states = rolling_dynamic_predictions(transformed, start_index=start_index, window=WINDOW_MONTHS)
    if len(states) != EXPECTED_OOS_ROWS:
        raise RuntimeError(f"B3 OOS state count mismatch: {len(states)} != {EXPECTED_OOS_ROWS}")
    if states[-1]["decision_date"] != b2.OOS_END.isoformat():
        raise RuntimeError("B3 OOS end date mismatch")

    canonical = b2.rpc(
        sb_url,
        sb_key,
        "ymq4_b3_read_b2_canonical",
        {"p_run_id": CANONICAL_B2_GATE_ID},
    )
    _validate_canonical_b2(canonical)

    actual = [state["actual"] for state in states]
    predicted = [state["prediction"] for state in states]
    oos_rows = [row for row in transformed if b2.OOS_START <= b2._as_date(row["decision_date"]) <= b2.OOS_END]
    if len(oos_rows) != EXPECTED_OOS_ROWS:
        raise RuntimeError("B3 OOS row alignment mismatch")
    overall = b2.metrics(actual, predicted)
    blocks = b2.block_metrics(oos_rows, actual, predicted)
    dynamic_summary = {
        "rmse": overall["rmse"],
        "mae": overall["mae"],
        "blocks": {name: blocks[name]["rmse"] for name in b2.BLOCKS},
    }
    b2_summary = {"rmse": B2_RMSE, "mae": B2_MAE, "blocks": B2_BLOCK_RMSE}
    comparison = compare_to_b2(dynamic_summary, b2_summary, minimum_positive_blocks=MIN_POSITIVE_BLOCKS)
    scientific = "DYNAMIC_BETA_BEATS_B2" if comparison["beats_b2"] else "DYNAMIC_BETA_DOES_NOT_BEAT_B2"

    receipt = {
        "battle": BATTLE,
        "status": "B3_DYNAMIC_BETA_MATERIALIZED_PASS",
        "scientific_observation": scientific,
        "git_sha": git_sha,
        "panel_id": PANEL_ID,
        "input": {
            "months": b2.EXPECTED_MONTHS,
            "panel_rows": b2.EXPECTED_PANEL_ROWS,
            "future_leakage": 0,
            "transformed_rows": len(transformed),
        },
        "model": {
            "family": "rolling_ols",
            "window_months": WINDOW_MONTHS,
            "coefficient_states": len(states),
            "coefficient_state_sha256": coefficient_state_sha(states),
            "strictly_prior_window": True,
        },
        "oos": {
            "start": b2.OOS_START.isoformat(),
            "end": b2.OOS_END.isoformat(),
            "rows": len(states),
            "dynamic": overall,
            "b2": {"rmse": B2_RMSE, "mae": B2_MAE},
            "comparison": comparison,
        },
        "oos_blocks": {
            name: {
                "rows": blocks[name]["rows"],
                "dynamic_rmse": blocks[name]["rmse"],
                "b2_rmse": B2_BLOCK_RMSE[name],
                "rmse_improvement_vs_b2": comparison["block_rmse_improvement_vs_b2"][name],
            }
            for name in b2.BLOCKS
        },
        "canonical_b2": {
            "reality_gate_run_id": CANONICAL_B2_GATE_ID,
            "physical_status": canonical["gate_status"],
        },
        "constraints": {
            "b4_b7_executed": False,
            "trading_action": False,
            "single_candidate_only": True,
        },
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    gate_id = b2.rpc(sb_url, sb_key, "ymq4_b3_record_gate", {
        "p_git_sha": git_sha,
        "p_started_at": receipt["started_at"],
        "p_completed_at": receipt["completed_at"],
        "p_gate_status": receipt["status"],
        "p_scientific_observation": scientific,
        "p_receipt": receipt,
    })
    receipt["reality_gate_run_id"] = gate_id
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"battle": BATTLE, "status": "FAIL_CLOSED", "error_type": type(exc).__name__, "error": str(exc)}, indent=2))
        raise SystemExit(1)
