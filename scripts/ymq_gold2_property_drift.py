#!/usr/bin/env python3
"""YMQ-GOLD2 G1 read-only Gold Property Drift Reality Run.

The runner reuses the governed YMQ4-DP1-B panel and B2 transformations. It does
not write Supabase, does not retune YMQ4-B3, and does not claim trading alpha.
"""

from __future__ import annotations

import json
import math
import os
import statistics
from datetime import datetime, timezone
from typing import Any

from scripts import ymq4_b2_fixed_beta as b2
from scripts import ymq_gold2_compiler as gold2


BATTLE = "YMQ-GOLD2-G1"
WINDOW_MONTHS = 60
FEATURES = (
    ("usd_return", "beta_usd"),
    ("inflation_change", "beta_inflation"),
    ("real_rate_change", "beta_real_rate"),
)


def rolling_states(transformed: list[dict[str, Any]], start_index: int) -> list[dict[str, Any]]:
    if start_index < WINDOW_MONTHS:
        raise ValueError("insufficient prior history for frozen 60-month window")
    states: list[dict[str, Any]] = []
    for idx in range(start_index, len(transformed)):
        current = transformed[idx]
        estimation = transformed[idx - WINDOW_MONTHS : idx]
        if estimation[-1]["decision_date"] >= current["decision_date"]:
            raise ValueError("current month leaked into rolling estimation")
        coef = b2.fit_ols(estimation)
        states.append({
            "decision_date": current["decision_date"],
            "known_as_of": current["known_as_of"],
            "coefficients": coef,
            "row": current,
        })
    return states


def oos_start_index(transformed: list[dict[str, Any]]) -> int:
    target = b2.OOS_START.isoformat()
    for idx, row in enumerate(transformed):
        if row["decision_date"] == target:
            return idx
    raise ValueError("canonical B2 OOS start not found")


def coefficient_distance(dynamic: dict[str, float], fixed: dict[str, float]) -> float:
    keys = ("beta_usd", "beta_inflation", "beta_real_rate")
    num = math.sqrt(sum((dynamic[k] - fixed[k]) ** 2 for k in keys))
    den = math.sqrt(sum(fixed[k] ** 2 for k in keys))
    return num / max(den, 1e-12)


def dominant_factor(row: dict[str, Any], coefficients: dict[str, float]) -> str:
    contributions = {
        feature: abs(float(row[feature]) * float(coefficients[beta]))
        for feature, beta in FEATURES
    }
    return max(contributions, key=contributions.get)


def rmse(values: list[float]) -> float:
    if not values:
        raise ValueError("empty residual vector")
    return math.sqrt(sum(v * v for v in values) / len(values))


def block_summary(
    states: list[dict[str, Any]],
    fixed_coef: dict[str, float],
    start_date,
    end_date,
) -> dict[str, Any]:
    block = [s for s in states if start_date <= b2._as_date(s["decision_date"]) <= end_date]
    if not block:
        raise ValueError("empty diagnostic block")

    distances: list[float] = []
    dominant_matches = 0
    residuals: list[float] = []
    for state in block:
        row = state["row"]
        dyn = state["coefficients"]
        distances.append(coefficient_distance(dyn, fixed_coef))
        dominant_matches += dominant_factor(row, dyn) == dominant_factor(row, fixed_coef)
        fixed_prediction = b2.predict([row], fixed_coef)[0]
        residuals.append(float(row["gold_return"]) - fixed_prediction)

    median_distance = float(statistics.median(distances))
    match_share = dominant_matches / len(block)
    block_rmse = rmse(residuals)
    residual_bias = abs(sum(residuals) / len(residuals)) / max(block_rmse, 1e-12)

    diagnostics = {
        "coefficient_distance_ge_0_50": median_distance >= 0.50,
        "dominant_factor_match_le_0_50": match_share <= 0.50,
        "residual_bias_ratio_ge_0_25": residual_bias >= 0.25,
    }
    # All three diagnostics were measured. A false anomaly flag is evidence of
    # stability, not missing evidence; thresholds are applied by the classifier.
    evidence_count = len(diagnostics)
    label = gold2.classify_property_drift(
        coefficient_distance=median_distance,
        dominant_factor_match_share=match_share,
        residual_bias_ratio=residual_bias,
        independent_evidence_count=evidence_count,
    )
    return {
        "rows": len(block),
        "median_coefficient_distance_vs_b2": median_distance,
        "dominant_factor_match_share_vs_b2": match_share,
        "fixed_beta_residual_bias_ratio": residual_bias,
        "diagnostics": diagnostics,
        "independent_evidence_count": evidence_count,
        "property_drift_state": label,
    }


def run(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gold2.validate_constitution(gold2.load_constitution())
    b2.validate_panel(rows)
    transformed = b2.build_transformed_rows(rows)
    train, _ = b2.split_rows(transformed)
    fixed_coef = b2.fit_ols(train)
    states = rolling_states(transformed, oos_start_index(transformed))
    if len(states) != b2.EXPECTED_OOS_ROWS:
        raise ValueError("OOS state count drift")

    blocks = {
        name: block_summary(states, fixed_coef, start, end)
        for name, (start, end) in b2.BLOCKS.items()
    }
    drift_blocks = sum(
        v["property_drift_state"] in {"DRIFT_CANDIDATE", "DRIFT_CONFIRMED_RESEARCH_ONLY"}
        for v in blocks.values()
    )
    confirmed_blocks = sum(
        v["property_drift_state"] == "DRIFT_CONFIRMED_RESEARCH_ONLY"
        for v in blocks.values()
    )
    return {
        "battle": BATTLE,
        "status": "PROPERTY_DRIFT_DIAGNOSTICS_MATERIALIZED",
        "scientific_scope": "descriptive_property_drift_not_alpha",
        "panel_id": b2.PANEL_ID,
        "panel_rows": b2.EXPECTED_PANEL_ROWS,
        "months": b2.EXPECTED_MONTHS,
        "future_leakage": 0,
        "rolling_window_months": WINDOW_MONTHS,
        "b2_fixed_coefficients": fixed_coef,
        "b3_scientific_history": gold2.EXPECTED_B3_SETTLEMENT,
        "blocks": blocks,
        "drift_candidate_or_confirmed_blocks": drift_blocks,
        "confirmed_research_only_blocks": confirmed_blocks,
        "capital_authorized": False,
        "sizing_authorized": False,
        "execution_authorized": False,
        "broker_action": False,
    }


def main() -> int:
    started = datetime.now(timezone.utc)
    sb_url = b2.require_env("SUPABASE_URL")
    sb_key = b2.require_env("YMQ4_SUPABASE_SECRET_KEY")
    rows = b2.rpc(sb_url, sb_key, "ymq4_b2_read_panel", {"p_panel_id": b2.PANEL_ID})
    if not isinstance(rows, list):
        raise RuntimeError("Gold PIT panel RPC returned unexpected shape")
    receipt = run(rows)
    receipt["git_sha"] = os.getenv("GITHUB_SHA", "LOCAL")
    receipt["started_at"] = started.isoformat()
    receipt["completed_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({
            "battle": BATTLE,
            "status": "FAIL_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        raise SystemExit(1)
