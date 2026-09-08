#!/usr/bin/env python3
"""YMQ4-B2 frozen Gold fixed-beta baseline.

B2 is a contemporaneous coefficient temporal-generalization benchmark.
It is not a tradable forecast and MUST NOT execute B3-B7 or trading logic.
"""
from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from typing import Any, Iterable

import numpy as np

BATTLE = "YMQ4-B2"
PANEL_ID = "gold_core_monthly_v0.1"
FACTORS = ("gold_usd_oz", "usd", "inflation_yoy", "real_rate")
EXPECTED_MONTHS = 584
EXPECTED_PANEL_ROWS = 2336
TRAIN_START = date(1978, 2, 28)
TRAIN_END = date(2006, 12, 31)
OOS_START = date(2007, 1, 31)
OOS_END = date(2026, 8, 31)
EXPECTED_TRAIN_ROWS = 347
EXPECTED_OOS_ROWS = 236
BLOCKS = {
    "gfc_2007_2009": (date(2007, 1, 31), date(2009, 12, 31)),
    "post_gfc_2010_2019": (date(2010, 1, 31), date(2019, 12, 31)),
    "covid_rates_2020_2022": (date(2020, 1, 31), date(2022, 12, 31)),
    "current_2023_2026": (date(2023, 1, 31), date(2026, 8, 31)),
}


def _as_date(value: str | date) -> date:
    return value if isinstance(value, date) else date.fromisoformat(value)


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def validate_panel(rows: Iterable[dict[str, Any]]) -> None:
    material = list(rows)
    if len(material) != EXPECTED_PANEL_ROWS:
        raise ValueError(f"panel row count mismatch: {len(material)} != {EXPECTED_PANEL_ROWS}")
    keys: set[tuple[str, str]] = set()
    by_date: dict[str, set[str]] = {}
    for row in material:
        if row.get("panel_id") != PANEL_ID:
            raise ValueError("unexpected panel_id")
        d = row.get("decision_date")
        factor = row.get("factor_id")
        if not d or factor not in FACTORS:
            raise ValueError("invalid decision_date/factor_id")
        key = (str(d), str(factor))
        if key in keys:
            raise ValueError(f"duplicate factor/month: {key}")
        keys.add(key)
        by_date.setdefault(str(d), set()).add(str(factor))
        if not _finite(row.get("value_numeric")):
            raise ValueError(f"non-finite value: {key}")
        if factor in ("gold_usd_oz", "usd") and float(row["value_numeric"]) <= 0:
            raise ValueError(f"non-positive log-level input: {key}")
        known = row.get("known_as_of")
        if not known or _as_date(known) > _as_date(d):
            raise ValueError(f"future leakage: {key}")
    if len(by_date) != EXPECTED_MONTHS:
        raise ValueError(f"panel month count mismatch: {len(by_date)} != {EXPECTED_MONTHS}")
    for d, factors in by_date.items():
        if factors != set(FACTORS):
            raise ValueError(f"incomplete month {d}: {sorted(factors)}")
    ordered = sorted(_as_date(d) for d in by_date)
    if ordered[0] != date(1978, 1, 31) or ordered[-1] != OOS_END:
        raise ValueError("panel date boundary mismatch")


def _pivot(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for row in rows:
        d = str(row["decision_date"])
        bucket = by_date.setdefault(d, {"decision_date": d, "known_as_of": d})
        bucket[str(row["factor_id"])] = float(row["value_numeric"])
        known = row.get("known_as_of")
        if known and _as_date(known) > _as_date(bucket["known_as_of"]):
            bucket["known_as_of"] = str(known)
    return [by_date[d] for d in sorted(by_date)]


def build_transformed_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    levels = _pivot(rows)
    out: list[dict[str, Any]] = []
    for prev, cur in zip(levels, levels[1:]):
        for factor in FACTORS:
            if factor not in prev or factor not in cur:
                raise ValueError(f"missing factor required for transformation: {factor}")
        gold_prev, gold_cur = prev["gold_usd_oz"], cur["gold_usd_oz"]
        usd_prev, usd_cur = prev["usd"], cur["usd"]
        if min(gold_prev, gold_cur, usd_prev, usd_cur) <= 0:
            raise ValueError("log-return input must be positive")
        row = {
            "decision_date": cur["decision_date"],
            "known_as_of": cur.get("known_as_of", cur["decision_date"]),
            "gold_return": 100.0 * math.log(gold_cur / gold_prev),
            "usd_return": 100.0 * math.log(usd_cur / usd_prev),
            "inflation_change": cur["inflation_yoy"] - prev["inflation_yoy"],
            "real_rate_change": cur["real_rate"] - prev["real_rate"],
        }
        if any(not _finite(row[k]) for k in ("gold_return", "usd_return", "inflation_change", "real_rate_change")):
            raise ValueError("non-finite transformed row")
        if _as_date(row["known_as_of"]) > _as_date(row["decision_date"]):
            raise ValueError("transformed row future leakage")
        out.append(row)
    return out


def split_rows(rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    material = list(rows)
    train = [r for r in material if TRAIN_START <= _as_date(r["decision_date"]) <= TRAIN_END]
    oos = [r for r in material if OOS_START <= _as_date(r["decision_date"]) <= OOS_END]
    if len(train) != EXPECTED_TRAIN_ROWS:
        raise ValueError(f"train row count mismatch: {len(train)} != {EXPECTED_TRAIN_ROWS}")
    if len(oos) != EXPECTED_OOS_ROWS:
        raise ValueError(f"OOS row count mismatch: {len(oos)} != {EXPECTED_OOS_ROWS}")
    if train[-1]["decision_date"] != TRAIN_END.isoformat() or oos[0]["decision_date"] != OOS_START.isoformat():
        raise ValueError("train/OOS boundary mismatch")
    return train, oos


def _matrix(rows: Iterable[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    material = list(rows)
    x = np.asarray([[1.0, r["usd_return"], r["inflation_change"], r["real_rate_change"]] for r in material], dtype=float)
    y = np.asarray([r["gold_return"] for r in material], dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("non-finite model matrix")
    return x, y


def fit_ols(rows: Iterable[dict[str, Any]]) -> dict[str, float]:
    x, y = _matrix(rows)
    coef, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != 4:
        raise ValueError(f"OLS design matrix rank deficient: {rank}")
    if not np.isfinite(coef).all():
        raise ValueError("non-finite OLS coefficient")
    return {
        "alpha": float(coef[0]),
        "beta_usd": float(coef[1]),
        "beta_inflation": float(coef[2]),
        "beta_real_rate": float(coef[3]),
    }


def predict(rows: Iterable[dict[str, Any]], coefficients: dict[str, float]) -> list[float]:
    return [
        coefficients["alpha"]
        + coefficients["beta_usd"] * r["usd_return"]
        + coefficients["beta_inflation"] * r["inflation_change"]
        + coefficients["beta_real_rate"] * r["real_rate_change"]
        for r in rows
    ]


def metrics(actual: Iterable[float], predicted: Iterable[float]) -> dict[str, float]:
    a = [float(v) for v in actual]
    p = [float(v) for v in predicted]
    if len(a) != len(p) or not a:
        raise ValueError("metrics require equal non-empty vectors")
    errors = [x - y for x, y in zip(a, p)]
    mse = sum(e * e for e in errors) / len(errors)
    mae = sum(abs(e) for e in errors) / len(errors)
    def sign(v: float) -> int:
        return 1 if v > 0 else (-1 if v < 0 else 0)
    accuracy = sum(sign(x) == sign(y) for x, y in zip(a, p)) / len(a)
    return {"mse": mse, "rmse": math.sqrt(mse), "mae": mae, "sign_accuracy": accuracy}


def relative_metrics(fixed: dict[str, float], null: dict[str, float]) -> dict[str, float]:
    if null["mse"] <= 0 or null["rmse"] <= 0 or null["mae"] <= 0:
        raise ValueError("null metrics must be positive")
    return {
        "oos_r2_vs_null": 1.0 - fixed["mse"] / null["mse"],
        "rmse_improvement_vs_null": 1.0 - fixed["rmse"] / null["rmse"],
        "mae_improvement_vs_null": 1.0 - fixed["mae"] / null["mae"],
    }


def block_metrics(rows: list[dict[str, Any]], actual: list[float], predicted: list[float]) -> dict[str, dict[str, float]]:
    if len(rows) != len(actual) or len(rows) != len(predicted):
        raise ValueError("block metric vectors must align")
    result: dict[str, dict[str, float]] = {}
    for name, (start, end) in BLOCKS.items():
        idx = [i for i, row in enumerate(rows) if start <= _as_date(row["decision_date"]) <= end]
        if not idx:
            raise ValueError(f"empty OOS block: {name}")
        result[name] = metrics([actual[i] for i in idx], [predicted[i] for i in idx])
        result[name]["rows"] = len(idx)
    return result


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required env missing: {name}")
    return value


def request_json(url: str, *, headers: dict[str, str], payload: dict[str, Any]) -> Any:
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Supabase RPC HTTP {exc.code}") from None


def rpc(sb_url: str, secret_key: str, fn: str, payload: dict[str, Any]) -> Any:
    if not secret_key.startswith("sb_secret_"):
        raise RuntimeError("YMQ4_SUPABASE_SECRET_KEY must be modern sb_secret_ key")
    return request_json(
        sb_url.rstrip("/") + "/rest/v1/rpc/" + fn,
        headers={"apikey": secret_key, "Content-Type": "application/json"},
        payload=payload,
    )


def main() -> int:
    started = datetime.now(timezone.utc)
    sb_url = require_env("SUPABASE_URL")
    sb_key = require_env("YMQ4_SUPABASE_SECRET_KEY")
    git_sha = os.getenv("GITHUB_SHA", "LOCAL")

    rows = rpc(sb_url, sb_key, "ymq4_b2_read_panel", {"p_panel_id": PANEL_ID})
    if not isinstance(rows, list):
        raise RuntimeError("B2 panel RPC returned unexpected shape")
    validate_panel(rows)
    transformed = build_transformed_rows(rows)
    train, oos = split_rows(transformed)

    coefficients = fit_ols(train)
    train_actual = [r["gold_return"] for r in train]
    oos_actual = [r["gold_return"] for r in oos]
    train_prediction = predict(train, coefficients)
    oos_prediction = predict(oos, coefficients)
    null_mean = sum(train_actual) / len(train_actual)
    null_prediction = [null_mean] * len(oos)

    train_metrics = metrics(train_actual, train_prediction)
    oos_fixed = metrics(oos_actual, oos_prediction)
    oos_null = metrics(oos_actual, null_prediction)
    relative = relative_metrics(oos_fixed, oos_null)
    fixed_blocks = block_metrics(oos, oos_actual, oos_prediction)
    null_blocks = block_metrics(oos, oos_actual, null_prediction)
    block_improvement = {
        name: 1.0 - fixed_blocks[name]["rmse"] / null_blocks[name]["rmse"]
        for name in BLOCKS
    }
    economic_observation = "FIXED_BETA_BEATS_NULL" if oos_fixed["rmse"] < oos_null["rmse"] else "FIXED_BETA_DOES_NOT_BEAT_NULL"

    receipt = {
        "battle": BATTLE,
        "status": "B2_BASELINE_MATERIALIZED_PASS",
        "git_sha": git_sha,
        "panel_id": PANEL_ID,
        "input": {"months": EXPECTED_MONTHS, "panel_rows": EXPECTED_PANEL_ROWS, "future_leakage": 0},
        "transform": {"rows": len(transformed), "semantics": "contemporaneous_coefficient_temporal_generalization_not_forecast"},
        "train": {"start": TRAIN_START.isoformat(), "end": TRAIN_END.isoformat(), "rows": len(train), "metrics": train_metrics},
        "oos": {"start": OOS_START.isoformat(), "end": OOS_END.isoformat(), "rows": len(oos), "fixed_beta": oos_fixed, "null": oos_null, "relative": relative},
        "coefficients": coefficients,
        "null_training_mean_gold_return": null_mean,
        "economic_observation": economic_observation,
        "oos_blocks": {name: {"fixed": fixed_blocks[name], "null": null_blocks[name], "rmse_improvement_vs_null": block_improvement[name]} for name in BLOCKS},
        "b3_incrementality_gate": {
            "candidate_rmse_lt_b2": True,
            "candidate_mae_lte_b2": True,
            "minimum_positive_rmse_blocks": 3,
            "blocks": list(BLOCKS),
        },
        "constraints": {"coefficient_vectors_fitted": 1, "b3_b7_executed": False, "trading_action": False},
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    gate_id = rpc(sb_url, sb_key, "ymq4_b2_record_gate", {
        "p_git_sha": git_sha,
        "p_started_at": receipt["started_at"],
        "p_completed_at": receipt["completed_at"],
        "p_gate_status": receipt["status"],
        "p_receipt": receipt,
    })
    receipt["reality_gate_run_id"] = gate_id
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:
        message = str(exc)
        secret = os.getenv("YMQ4_SUPABASE_SECRET_KEY", "").strip()
        if secret:
            for variant in (secret, urllib.parse.quote(secret, safe=""), urllib.parse.quote_plus(secret)):
                message = message.replace(variant, "REDACTED")
        print(json.dumps({"battle": BATTLE, "status": "FAIL_CLOSED", "error_type": type(exc).__name__, "error": message}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
