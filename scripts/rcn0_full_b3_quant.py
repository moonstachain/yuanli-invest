#!/usr/bin/env python3
"""RCN0-S2 deterministic Full B3 Shadow Benchmark runner.

Research-only utility. It does not emit trading recommendations.
Expected input: CSV satisfying the data contract in
benchmarks/rcn0/RCN0-S2-FULL-B3-QUANT-CLOSURE-SPEC-v0.1.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

DN_MAP = {"near": 0, "medium": 1, "farther": 2}


def fit_ols(df: pd.DataFrame, y: str, xcols: list[str]) -> dict:
    work = df[[y] + xcols].dropna().copy()
    X = sm.add_constant(work[xcols], has_constant="add")
    model = sm.OLS(work[y], X).fit(cov_type="HC1")
    return {
        "n": int(model.nobs),
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "params": {k: float(v) for k, v in model.params.items()},
        "stderr_hc1": {k: float(v) for k, v in model.bse.items()},
        "pvalues_hc1": {k: float(v) for k, v in model.pvalues.items()},
    }


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["D_N_ord"] = out["D_N_bucket"].map(DN_MAP)
    if out["D_N_ord"].isna().any():
        bad = out.loc[out["D_N_ord"].isna(), "D_N_bucket"].unique().tolist()
        raise ValueError(f"Unknown D_N bucket(s): {bad}")
    out["log_market_cap"] = np.log(out["market_cap_t0"].astype(float))
    if "abnormal_return_t0" not in out or out["abnormal_return_t0"].isna().all():
        out["abnormal_return_t0"] = out["return_t0"] - out["benchmark_return_t0"]
    return out


def run(df: pd.DataFrame) -> dict:
    required = [
        "company", "chain", "D_N_bucket", "return_t0", "benchmark_return_t0",
        "market_cap_t0", "beta", "momentum_5d", "momentum_20d",
        "momentum_60d", "liquidity_proxy", "price_limit_pct",
        "one_price_limit_dummy", "prior_theme_member"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    d = prepare(df)

    # Parsimonious primary B3 model to reduce overfit at n=29.
    b3 = ["log_market_cap", "beta", "momentum_20d", "liquidity_proxy",
          "price_limit_pct", "prior_theme_member"]
    result = {
        "universe_n": int(len(d)),
        "bucket_counts": d["D_N_bucket"].value_counts().to_dict(),
        "bucket_mean_abnormal_return": d.groupby("D_N_bucket")["abnormal_return_t0"].mean().to_dict(),
        "models": {
            "M1_B3_controls": fit_ols(d, "abnormal_return_t0", b3),
            "M2_narrative_only": fit_ols(d, "abnormal_return_t0", ["D_N_ord"]),
            "M3_incremental_narrative": fit_ols(d, "abnormal_return_t0", b3 + ["D_N_ord"]),
        },
        "sensitivities": {},
    }

    sensitivities = {
        "exclude_one_price_limit": d[d["one_price_limit_dummy"] == 0],
        "exclude_smallest_cap_tercile": d[d["market_cap_t0"] > d["market_cap_t0"].quantile(1/3)],
    }
    for name, sub in sensitivities.items():
        result["sensitivities"][name] = fit_ols(sub, "abnormal_return_t0", b3 + ["D_N_ord"])

    # Jackknife D_N coefficient stability.
    coefs = []
    for idx in d.index:
        sub = d.drop(index=idx)
        try:
            r = fit_ols(sub, "abnormal_return_t0", b3 + ["D_N_ord"])
            coefs.append(r["params"].get("D_N_ord"))
        except Exception:
            continue
    result["jackknife_D_N"] = {
        "n_success": len(coefs),
        "min": float(np.nanmin(coefs)) if coefs else None,
        "max": float(np.nanmax(coefs)) if coefs else None,
        "median": float(np.nanmedian(coefs)) if coefs else None,
    }
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--out", type=Path, default=Path("rcn0_b3_result.json"))
    args = p.parse_args()
    df = pd.read_csv(args.csv)
    result = run(df)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "out": str(args.out), "universe_n": result["universe_n"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
