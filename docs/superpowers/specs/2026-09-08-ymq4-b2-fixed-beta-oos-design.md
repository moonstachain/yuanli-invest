# YMQ4-B2｜Fixed Beta Baseline × OOS Incrementality Gate — Design

## 1. Mission

Build the first frozen, out-of-sample fixed-beta benchmark on the reality-backed Gold PIT panel created by YMQ4-DP1-B. B2 is a research-baseline battle, not a trading model and not a dynamic-beta implementation.

The core question is:

> If one estimates one set of Gold factor betas on an earlier historical period and freezes those coefficients, how well do they generalize to later regimes without re-estimation, hindsight tuning, or outcome-dependent model changes?

## 2. Authority boundary

B2 may read `pit.decision_asof_values` panel `gold_core_monthly_v0.1`, transform the four monthly PIT state variables into contemporaneous monthly changes, estimate one fixed OLS coefficient vector on a preregistered training window, evaluate that frozen coefficient vector on a preregistered OOS window, compare it with an intercept-only historical-mean baseline, and persist a non-secret Reality Receipt and gate result.

B2 may not estimate rolling, Kalman, TVP, regime-switching or other dynamic betas; tune windows after seeing OOS results; use future data inside training transforms; create portfolio weights, position sizes, trading signals or broker actions; or promote any economic interpretation to Canon.

## 3. Input data contract

Input panel: `pit.decision_asof_values(panel_id='gold_core_monthly_v0.1')`.

Expected physical shape: 584 month-end states from `1978-01-31 → 2026-08-31`, four factors per month (`gold_usd_oz`, `usd`, `inflation_yoy`, `real_rate`), 2,336 rows total, and zero future leakage. B2 fails closed if these conditions do not hold.

## 4. Frozen transformations

For month `t` and prior month `t-1`:

- `gold_return_t = 100 * ln(Gold_t / Gold_{t-1})`
- `usd_return_t = 100 * ln(USD_t / USD_{t-1})`
- `inflation_change_t = inflation_yoy_t - inflation_yoy_{t-1}`
- `real_rate_change_t = real_rate_t - real_rate_{t-1}`

All transformations are contemporaneous. Therefore B2 OOS is a **coefficient temporal-generalization test**, not a tradable one-month-ahead forecasting claim. No standardization is required; coefficients retain natural units.

## 5. Fixed model

`gold_return_t = alpha + beta_usd*usd_return_t + beta_inflation*inflation_change_t + beta_real_rate*real_rate_change_t + error_t`

Estimation: ordinary least squares with intercept using `numpy.linalg.lstsq`.

No regularization, variable selection, winsorization, clipping, interaction terms, lag search or post-reveal feature changes are allowed.

## 6. Frozen train/OOS split

Training transformed observations: `1978-02-28 → 2006-12-31`.

OOS transformed observations: `2007-01-31 → 2026-08-31`.

The 2006/2007 cut reserves GFC, COVID, the 2022 rate shock and 2023–2026 for untouched temporal generalization. Coefficients are estimated once and never re-estimated inside OOS.

Expected transformed counts are 347 training months and 236 OOS months.

## 7. Null benchmark and metrics

Intercept-only null: `prediction_null_t = mean(training gold_return)` for every OOS month.

For fixed-beta and null, report RMSE, MAE and sign accuracy. Also report OOS R² relative to null MSE (`1 - MSE_fixed/MSE_null`), RMSE improvement (`1 - RMSE_fixed/RMSE_null`) and MAE improvement (`1 - MAE_fixed/MAE_null`).

## 8. B2 settlement semantics

### Integrity settlement

`B2_BASELINE_MATERIALIZED_PASS` requires exact panel integrity, deterministic transformations, the frozen split, one coefficient vector only, finite coefficients and metrics, zero OOS leakage, and database/artifact readback agreement.

### Economic observation

`FIXED_BETA_BEATS_NULL` if fixed-beta OOS RMSE is lower than intercept-only OOS RMSE; otherwise `FIXED_BETA_DOES_NOT_BEAT_NULL`.

This observation does not decide B2 validity. A weak fixed-beta baseline remains a valid benchmark if measured honestly.

## 9. B3 incrementality gate frozen by B2

A future dynamic-beta candidate can claim OOS incrementality only if all are true:

1. same input panel and same transformed target/features;
2. no future leakage;
3. same OOS dates;
4. candidate OOS RMSE < B2 fixed-beta OOS RMSE;
5. candidate OOS MAE <= B2 fixed-beta OOS MAE;
6. positive RMSE improvement in at least 3 of 4 fixed OOS blocks: `2007-2009`, `2010-2019`, `2020-2022`, `2023-2026-08`.

No arbitrary percentage hurdle is added at B2. Statistical uncertainty may be preregistered in B3, but the directional multi-block gate cannot be relaxed after reveal.

## 10. Persistence

B2 writes one receipt to `runtime.reality_gate_runs` with `battle_id=YMQ4-B2`, executed Git SHA, source panel identity and DP1-B gate reference, train/OOS dates and row counts, coefficient vector, train metrics, OOS fixed-beta metrics, OOS null metrics, economic observation, block metrics, and `b3_b7_executed=false`.

A matching non-secret GitHub Actions artifact is uploaded.

## 11. Pass/Fail

`YMQ4-B2｜PASS` means the fixed-beta benchmark and OOS gate were physically materialized and independently read back. It does **not** mean the model predicts Gold well.

Fail closed on input integrity mismatch, non-finite transform/model values, train/OOS boundary violation, coefficient re-estimation, row-count mismatch, database receipt mismatch, or any B3-B7/trading logic entering B2.
