# RCN0-S2 Wind Data Extraction Task v0.1

Status: `runtime_task_ready`

Issue: #34

Replay: `RCN-REPLAY-20260820-CN-INNOVATIVE-DRUG-MRNA`

## Objective

Use Wind as the Evidence/Data Runtime to build the complete T0 cross-sectional matrix required by `RCN0-S2 Full B3 Quant Closure`.

The task must preserve point-in-time discipline at `2026-08-20` and must not use post-T0 classification or price information to alter universe membership or Narrative Distance buckets.

## Universe law

Exactly 29 A-share targets declared by the T0 source:

- Near: 7 vaccine/mRNA names;
- Medium: 17 innovative-drug BD/pipeline names;
- Farther: 5 CXO/service names.

Current recoverable names: 24/29. Five Medium-bucket names remain unresolved from the source extraction and must be recovered from T0 source/classification evidence before running the final benchmark. Do not guess them.

## Required output file

`rcn0_s2_wind_t0_matrix_20260820.csv`

One row per stock. Required columns:

- `ticker`
- `company`
- `chain`
- `D_N_bucket`
- `return_t0`
- `benchmark_return_t0`
- `abnormal_return_t0`
- `market_cap_t0`
- `beta`
- `beta_lookback`
- `momentum_5d`
- `momentum_20d`
- `momentum_60d`
- `turnover_t0`
- `turnover_20d`
- `liquidity_proxy`
- `board`
- `price_limit_pct`
- `one_price_limit_dummy`
- `tradability_dummy`
- `prior_theme_member`
- `source_locator`
- `as_of`

## Point-in-time definitions

- `return_t0`: 2026-08-20 close-to-close return.
- `market_cap_t0`: total market capitalization at 2026-08-20 close.
- `beta`: estimated only with observations ending no later than 2026-08-19. Freeze the benchmark and lookback before extraction; recommended default is 120 trading days vs CSI 300, with actual lookback recorded.
- `momentum_5d/20d/60d`: cumulative return ending 2026-08-19, excluding T0.
- `turnover_t0`: turnover rate on 2026-08-20.
- `turnover_20d`: average turnover over the prior 20 trading days ending 2026-08-19.
- `liquidity_proxy`: pre-specified, preferably prior-20D median/mean trading amount or Amihud-style proxy; definition must be uniform across all 29 names.
- `one_price_limit_dummy`: 1 only when the T0 session was effectively one-price/near-one-price limit-up under the frozen rule; store rule in metadata.
- `tradability_dummy`: flag whether meaningful intraday trading occurred on T0.
- `prior_theme_member`: membership established from classifications available before T0, never inferred from T0 return.

## Benchmarks

Freeze before computation:

1. broad healthcare benchmark: SW Healthcare or another single, consistently available healthcare index;
2. broad growth benchmark: ChiNext or STAR 50 where appropriate;
3. broad market benchmark: CSI 300.

Primary abnormal-return benchmark for Full B3 must be selected once and documented before results are inspected.

## Quality gates

1. Exactly 29 unique A-share tickers.
2. Bucket counts exactly 7 / 17 / 5.
3. No as-of date later than 2026-08-20 for T0 values.
4. No beta/momentum window includes 2026-08-20 return.
5. Missing fields remain null with reason; do not interpolate silently.
6. Any suspended/newly listed/security-special-status observations must be explicitly flagged.
7. Every row must contain a Wind field/query locator or reproducible field definition.

## Required companion metadata

`rcn0_s2_wind_t0_matrix_20260820.meta.json`

Must store:

- Wind extraction timestamp;
- universe source/hash;
- beta benchmark/lookback;
- momentum formulas;
- liquidity formula;
- abnormal-return benchmark;
- price-limit and one-price-limit rule;
- missing-value policy;
- data-field identifiers / Wind query definitions;
- checksum of final CSV.

## Handoff

After extraction, run:

`python scripts/rcn0_full_b3_quant.py rcn0_s2_wind_t0_matrix_20260820.csv --out rcn0_b3_result.json`

Then store result and a Human Review readout under the replay directory.

## Non-authorization

This task is research-data extraction only. No target price, recommended position, buy/sell action or automatic execution is authorized.