# YMQ4-B3｜Dynamic Beta Reality Challenge — Reality Receipt v0.1

**Settlement:** `B3_DYNAMIC_BETA_MATERIALIZED_PASS`  
**Scientific observation:** `DYNAMIC_BETA_DOES_NOT_BEAT_B2`  
**Battle:** `YMQ4-B3`  
**Panel:** `gold_core_monthly_v0.1`  
**Completed:** `2026-09-08T12:28:12.774186+00:00`

## 1. What this receipt proves

The preregistered minimal dynamic-beta candidate was physically executed against the canonical B2 fixed-beta baseline using the same Gold PIT panel, the same transformations, the same OOS interval and the same frozen victory law.

The physical experiment completed successfully. The scientific hypothesis did **not** pass the full B3 incrementality gate. This is a valid negative scientific result, not an infrastructure failure.

No B4-B7 logic, Kalman/TVP/DCC/HMM model, window search, Narrative/Herding layer, portfolio sizing, broker connection or trading action was executed.

## 2. Execution identity

- GitHub Actions workflow: `YMQ4 B3 Dynamic Beta Reality Challenge`
- Canonical successful run: `34226196855`
- Canonical successful job: `102060889174`
- Branch head that authorized/fixed the run: `e1ba000fbd651e31b52af67cd4a78cb5cd6f7f63`
- Executed PR merge SHA: `6121b380326cd492e90223a7fba168d71417ec59`
- Reality Gate run id: `2b4ea1f8-b317-433a-a801-630268b56c39`
- Artifact id: `10055814378`
- Artifact ZIP SHA-256: `953c6945425819244547a683834a79f82a58dc759b6937bbd8df7332c2aa91da`
- Runtime interval: `2026-09-08T12:28:11.290092+00:00` → `2026-09-08T12:28:12.774186+00:00`

## 3. Pre-registered experiment

Candidate:

```text
family: rolling_ols
window_months: 60
intercept: true
features: usd_return, inflation_change, real_rate_change
current Gold target in coefficient estimation: false
window search: false
```

Every OOS month estimates coefficients from exactly the prior 60 transformed rows. The current month Gold return is excluded from coefficient estimation.

Frozen comparison law:

```text
RMSE_B3 < RMSE_B2
MAE_B3 <= MAE_B2
positive RMSE incrementality in >= 3/4 frozen OOS blocks
```

All three are required for `DYNAMIC_BETA_BEATS_B2`.

## 4. Physical input and dynamic states

```text
physical months: 584
physical panel rows: 2336
transformed rows: 583
OOS rows / Dynamic Beta states: 236
future leakage: 0
strictly prior rolling window: true
```

The 236 coefficient states are deterministically committed by:

```text
coefficient_state_sha256:
7e3d640b1477715c2f184a0786be3405b7abb31d8aedde34cf79299484ab4c6c
```

The individual coefficient states were computed in the runtime and summarized by count + deterministic SHA in the Reality Receipt; B3 did not create a new per-state persistence table.

## 5. Canonical B2 opponent

B3 read back exactly the canonical B2 Reality Gate:

```text
B2 reality gate:
8907b60a-445c-4396-8e51-29e6f36620fb

B2 physical status:
B2_BASELINE_MATERIALIZED_PASS

B2 RMSE: 3.7129313457620357
B2 MAE:  2.9202089520079597
```

No alternate B2 duplicate verification row was selected.

## 6. B3 OOS result

| Metric | Dynamic B3 | Canonical B2 | Gate |
|---|---:|---:|---|
| RMSE | `3.6599160404780755` | `3.7129313457620357` | PASS |
| MAE | `2.8549260308862356` | `2.9202089520079597` | PASS |
| Sign accuracy | `61.4407%` | not a B3 victory condition | observation only |

Overall RMSE improvement versus B2:

```text
1 - 3.6599160404780755 / 3.7129313457620357
≈ +1.4277%
```

Overall MAE improvement versus B2:

```text
1 - 2.8549260308862356 / 2.9202089520079597
≈ +2.2369%
```

The overall RMSE and MAE gates therefore passed.

## 7. Frozen block test

| Frozen OOS block | B2 RMSE | Dynamic RMSE | Improvement vs B2 | Result |
|---|---:|---:|---:|---|
| GFC 2007–2009 | `4.7354052322` | `4.8024892617` | `-1.4166%` | FAIL |
| Post-GFC 2010–2019 | `3.2805905754` | `3.2308631530` | `+1.5158%` | PASS |
| COVID / Rates 2020–2022 | `3.1050742795` | `3.2261811005` | `-3.9003%` | FAIL |
| Current 2023–2026-08 | `4.2843002490` | `3.9988692739` | `+6.6623%` | PASS |

Positive RMSE blocks:

```text
2 / 4
```

Frozen requirement:

```text
>= 3 / 4
```

Therefore:

```text
RMSE gate:   PASS
MAE gate:    PASS
Block gate:  FAIL
Overall B3 victory gate: FAIL
```

Final scientific observation:

`DYNAMIC_BETA_DOES_NOT_BEAT_B2`

## 8. Independent Supabase readback

After the GitHub Actions run completed, an independent Supabase SQL readback reproduced the persisted B3 Reality Gate:

```text
run_id: 2b4ea1f8-b317-433a-a801-630268b56c39
battle_id: YMQ4-B3
gate_status: B3_DYNAMIC_BETA_MATERIALIZED_PASS
scientific_observation: DYNAMIC_BETA_DOES_NOT_BEAT_B2
coefficient_states: 236
coefficient_state_sha256: 7e3d640b1477715c2f184a0786be3405b7abb31d8aedde34cf79299484ab4c6c
dynamic_rmse: 3.65991604047808
dynamic_mae: 2.85492603088624
positive_rmse_blocks: 2
rmse_pass: true
mae_pass: true
blocks_pass: false
beats_b2: false
b4_b7_executed: false
trading_action: false
```

A separate independent readback of the canonical B2 row reproduced:

```text
B2 gate_status: B2_BASELINE_MATERIALIZED_PASS
B2 RMSE: 3.71293134576204
B2 MAE: 2.92020895200796
```

The database contained exactly one `YMQ4-B3` Reality Gate row at settlement time.

## 9. Execution incident and repair

The first authorized physical attempt (`34225917846`) failed closed before model execution because the workflow launched the runner as:

```text
python scripts/ymq4_b3_dynamic_beta.py
```

while the runner imports B2 as `from scripts import ymq4_b2_fixed_beta`. Direct script execution therefore set Python's import path incorrectly and raised `ModuleNotFoundError: No module named 'scripts'`.

The root cause was frozen with a regression test, observed RED, and repaired by invoking the runtime as a module:

```text
python -m scripts.ymq4_b3_dynamic_beta
```

The subsequent preflight, unit/database contract tests and physical run passed. The failed attempt produced no B3 Reality Gate row and did not alter the scientific result.

## 10. One-shot authorization settlement

The one-shot marker:

`.ymq4/authorizations/YMQ4-B3-FULL`

was consumed and deleted immediately after the successful physical run and independent database readback, before writing this canonical settlement. Subsequent PR-triggered workflow executions therefore cannot re-run the physical challenge without a new explicit authorization.

## 11. Scientific interpretation boundary

B3 establishes only the following:

> A single preregistered 60-month Rolling OLS candidate improves aggregate RMSE and MAE versus the fixed-beta B2 baseline, but its improvement is not sufficiently regime-broad under the frozen `>=3/4` block rule.

It does **not** establish that all dynamic-beta approaches fail. It also does **not** authorize changing the rolling window, trying Kalman/TVP, adding Narrative/Herding, or moving to B4-B7 merely to rescue the hypothesis.

Any further dynamic-beta candidate requires a separate preregistered research battle and an explicit human authorization.

## 12. Final settlement

```text
Physical experiment: PASS
Scientific hypothesis gate: NOT SUPPORTED
Scientific observation: DYNAMIC_BETA_DOES_NOT_BEAT_B2
B4-B7 executed: false
Trading action: false
One-shot authorization: consumed
```

**Final state:** `YMQ4-B3｜REALITY PASS / SCIENTIFIC NO-GO FOR THIS CANDIDATE`
