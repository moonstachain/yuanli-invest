# YMQ4-B3｜Dynamic Beta Reality Challenge Design v0.1

Status: `AUTHORIZED / PRE-RESULT FREEZE`

## 1. Mission

Test the smallest credible form of the YMQ4 core hypothesis:

> Does a time-varying Gold beta estimated only from information prior to each OOS month add repeatable explanatory power beyond the already-positive B2 fixed-beta baseline?

B3 is an experiment, not a trading system. A correct negative result is a valid research outcome.

## 2. Complexity budget

B3-A uses exactly one dynamic candidate: **60-month rolling OLS** with intercept and the same three B2 features. No Kalman, TVP, DCC, HMM, regime switching, feature selection, window search, hyperparameter search, winsorization, narrative variables or post-result tuning is permitted in this battle.

The 60-month window is frozen before the physical run as a five-year compromise between estimation stability and regime responsiveness. It may not be changed after B3 metrics are observed.

If B3-A does not beat B2 under the frozen gate, B3 settles negative/unsupported. It does not automatically escalate to a more complex estimator.

## 3. Frozen data and transformations

Input panel: `gold_core_monthly_v0.1`.

Physical integrity remains:

- 584 month-end states, `1978-01-31 → 2026-08-31`;
- 2,336 factor rows;
- factors: `gold_usd_oz`, `usd`, `inflation_yoy`, `real_rate`;
- future leakage tolerance: `0`.

B3 must import/reuse B2 transformations unchanged:

- target: `100 * ln(gold_t / gold_t-1)`;
- USD: `100 * ln(usd_t / usd_t-1)`;
- inflation: `inflation_yoy_t - inflation_yoy_t-1`;
- real rate: `real_rate_t - real_rate_t-1`.

OOS dates remain exactly `2007-01-31 → 2026-08-31`, 236 rows.

## 4. Dynamic estimation semantics

For each OOS row at month `t`:

1. locate its index in the 583-row transformed history;
2. take exactly the preceding 60 transformed rows `[t-60, ..., t-1]`;
3. require the latest estimation row date `< t`;
4. fit one OLS vector with intercept using those 60 prior rows only;
5. apply that frozen-at-t coefficient vector to the contemporaneous B2 feature vector for month `t`;
6. record the prediction/attribution and coefficient state.

The current month's Gold return is never used to estimate the coefficient vector applied to that same month.

This remains a **coefficient-state generalization / repricing diagnostic**, not a claim that the contemporaneous macro changes are tradable before month-end.

## 5. Canonical B2 opponent

B3 must compare against the canonical B2 Reality Gate:

`8907b60a-445c-4396-8e51-29e6f36620fb`

Frozen B2 OOS metrics:

- RMSE: `3.7129313457620357`
- MAE: `2.9202089520079597`

Frozen B2 block RMSE:

- `gfc_2007_2009`: `4.735405232228532`
- `post_gfc_2010_2019`: `3.280590575419435`
- `covid_rates_2020_2022`: `3.1050742795420367`
- `current_2023_2026`: `4.284300249030305`

B3 must independently read back the canonical B2 gate and reject any mismatch rather than silently using one of the duplicate B2 audit rows.

## 6. Frozen victory law

Physical integrity status is separate from scientific outcome.

A physically valid run settles `B3_DYNAMIC_BETA_MATERIALIZED_PASS` if all data, window, chronology, baseline-readback and authority checks pass.

The scientific label is `DYNAMIC_BETA_BEATS_B2` only if **all** are true:

1. `RMSE_B3 < RMSE_B2`;
2. `MAE_B3 <= MAE_B2`;
3. B3 RMSE is lower than B2 in at least `3/4` frozen blocks.

Otherwise the scientific label is `DYNAMIC_BETA_DOES_NOT_BEAT_B2`.

A negative scientific label does not invalidate experiment integrity.

## 7. Audit object

The runtime will produce 236 dynamic coefficient states. To avoid prematurely introducing a production DynamicExposure schema, B3 persists only the Reality Receipt plus a deterministic SHA-256 over the ordered coefficient-state payload. The artifact contains non-secret aggregate metrics and the hash, not credentials.

A later B4/B5 battle may separately authorize persistent driver-contribution or property-drift state tables.

## 8. Authority boundary

B3 does not authorize:

- B4-B7 execution;
- Kalman/TVP/DCC/regime-switching rescue attempts;
- Narrative/Herding integration;
- Canon promotion;
- portfolio sizing;
- broker connectivity;
- trading action.

## 9. PASS / stop condition

B3 closes only after:

`clean main → frozen config/tests → Supabase service-role-only B3 gate RPC → preflight GREEN → one physical run → artifact → independent Supabase readback → one-shot authorization consumed → post-cleanup CI GREEN → canonical Reality Receipt`.

If the scientific outcome is negative, the YMQ4 dynamic-beta hypothesis is downgraded at this minimal-complexity gate unless a separately authorized research rationale justifies a new hypothesis test.