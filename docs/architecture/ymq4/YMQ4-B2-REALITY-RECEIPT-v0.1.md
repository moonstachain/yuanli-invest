# YMQ4-B2｜Fixed Beta Baseline × OOS Incrementality Gate — Reality Receipt v0.1

## Settlement

**Battle:** `YMQ4-B2`

**Settlement:** `PASS`

**Physical status:** `B2_BASELINE_MATERIALIZED_PASS`

**Economic observation:** `FIXED_BETA_BEATS_NULL`

This receipt closes B2 only. It does **not** authorize B3-B7, Canon promotion, portfolio sizing, broker connection, or trading action.

---

## 1. Physical Reality Chain

`DP1-B PIT panel → service-role-only readback RPC → full 2,336-row integrity gate → frozen transformations → one fixed OLS vector → 2007-2026 OOS evaluation → intercept-only null comparison → runtime.reality_gate_runs → independent database readback`

The first physical attempt failed closed because PostgREST truncated the set-returning RPC at 1,000 rows while the frozen contract required 2,336 rows. The repair changed the readback RPC to return the complete ordered panel as one `JSONB` aggregate. Before the successful physical run, direct database verification returned exactly 2,336 rows with first decision date `1978-01-31` and last decision date `2026-08-31`.

No model thresholds, split dates, factors, null benchmark, or B3 victory conditions were relaxed after the first failure.

---

## 2. Canonical Execution Evidence

- GitHub Actions run: `34198365994`
- B2 full job: `101971238876`
- PR branch head that triggered the run: `f1cb974572a676698c934b4bce11aece5e3be072`
- Executed PR merge SHA checked out by Actions: `9a86a76e4b04b1b2c63b4a1c6ab31f7313a11aae`
- Canonical Reality Gate run id: `8907b60a-445c-4396-8e51-29e6f36620fb`
- Artifact id: `10044791323`
- Artifact name: `ymq4-b2-reality-receipt`
- Artifact digest: `sha256:f1c2332eeff30f4a72aec0ae3febd1a40753cc1526361f57e45f27a3a3012728`
- Artifact size: `1608` bytes

The workflow preflight, secret gate, physical materialization, PASS-receipt assertion and artifact upload all completed successfully.

### 2.1 Temporary carrier audit

The browser-accessible GitHub connector did not expose a direct `workflow_dispatch` mutation, so B2 used a temporary PR-trigger carrier guarded by a one-shot marker. After the canonical PASS run, two documentation/configuration commits were made before that marker was removed. Those commits retriggered the temporary carrier and produced two additional **idempotent** B2 Reality Gate rows:

| Role | Reality Gate id | Executed merge SHA | Fixed RMSE | Null RMSE |
|---|---|---|---:|---:|
| Canonical authorized run | `8907b60a-445c-4396-8e51-29e6f36620fb` | `9a86a76e4b04b1b2c63b4a1c6ab31f7313a11aae` | `3.71293134576204` | `3.77256576171896` |
| Duplicate verification rerun | `8dbf3a40-6cd6-4b17-91b0-4fccaa70a6b2` | `77819bd7373fecb4dde04d412a774f735db86e80` | `3.71293134576204` | `3.77256576171896` |
| Duplicate verification rerun | `75a9558f-665d-4da8-a1ec-10edbe629389` | `0311a829557e8c10af6e8a296ea3082f732b199c` | `3.71293134576204` | `3.77256576171896` |

The duplicate rows are retained as immutable audit evidence rather than deleted. They did not change the data, coefficient vector, metrics, model contract, or B3 gate. The canonical settlement remains the first successful authorized run above.

The one-shot marker was subsequently consumed and deleted, and the temporary B2 PR-trigger carrier was removed from the DP1-A workflow. Durable B2 behavior is restored to explicit `workflow_dispatch(mode=full)` only.

---

## 3. Frozen Input Integrity

| Field | Physical result |
|---|---:|
| Panel | `gold_core_monthly_v0.1` |
| Physical months | 584 |
| Physical factor rows | 2,336 |
| Factors per month | 4 |
| Future leakage | 0 |
| Transformed months | 583 |

The four factors remained exactly:

- `gold_usd_oz`
- `usd`
- `inflation_yoy`
- `real_rate`

---

## 4. Frozen Train / OOS Split

| Window | Dates | Rows |
|---|---|---:|
| Train | `1978-02-28 → 2006-12-31` | 347 |
| OOS | `2007-01-31 → 2026-08-31` | 236 |

B2 uses contemporaneous monthly changes to test **coefficient temporal generalization**. It is not a tradable forecasting claim.

Exactly one coefficient vector was fitted per run; there was no OOS re-estimation, rolling beta, TVP/Kalman beta, regime switching, feature search or post-outcome tuning.

---

## 5. Materialized Fixed-Beta Vector

\[
r^{Gold}_t = \alpha + \beta_{USD}\Delta USD_t + \beta_{\pi}\Delta Inflation_t + \beta_R\Delta RealRate_t + \epsilon_t
\]

| Coefficient | Value |
|---|---:|
| Alpha | `0.3884032398` |
| Beta USD | `-0.4378435293` |
| Beta Inflation | `1.5097162036` |
| Beta Real Rate | `-0.0822510315` |

Training-period mean Gold return used by the frozen null benchmark: `0.3724577017`.

---

## 6. OOS Result vs Frozen Null

| Metric | Fixed Beta | Null |
|---|---:|---:|
| RMSE | `3.7129313458` | `3.7725657617` |
| MAE | `2.9202089520` | `2.9931488774` |
| Sign accuracy | `56.36%` | `53.81%` |

Relative results:

- OOS R² vs null: `0.0313649052`
- RMSE improvement vs null: `1.58073894%`
- MAE improvement vs null: `2.43689601%`

Therefore the preregistered economic label is:

`FIXED_BETA_BEATS_NULL`

This is a **modest** OOS improvement, not evidence of strong forecasting power, statistical significance, or tradability. B2's role is to establish a hard baseline that B3 must beat without changing the data or evaluation law.

---

## 7. Frozen OOS Block Readback

| Block | Rows | Fixed RMSE | Null RMSE | RMSE improvement |
|---|---:|---:|---:|---:|
| 2007-2009 GFC | 36 | `4.7354052322` | `4.8211367798` | `1.77824342%` |
| 2010-2019 | 120 | `3.2805905754` | `3.3251851182` | `1.34111459%` |
| 2020-2022 COVID / Rate Shock | 36 | `3.1050742795` | `3.2473943462` | `4.38259267%` |
| 2023-2026-08 | 44 | `4.2843002490` | `4.3053544047` | `0.48902259%` |

All four frozen B2 blocks beat the intercept-only null on RMSE, but the magnitude is small in several regimes. No block threshold was introduced after seeing these values.

---

## 8. B3 Incrementality Law Frozen Before B3

A future B3 candidate must use:

- the same panel;
- the same transformations;
- the same OOS dates;
- overall `RMSE_B3 < RMSE_B2`;
- overall `MAE_B3 <= MAE_B2`;
- positive RMSE incrementality versus B2 in at least `3/4` frozen OOS blocks.

These rules are recorded now so B3 cannot redefine victory after observing its own results.

---

## 9. Independent Database Readback

An independent Supabase query against `runtime.reality_gate_runs` reproduced the canonical run:

- battle: `YMQ4-B2`
- gate status: `B2_BASELINE_MATERIALIZED_PASS`
- executed SHA: `9a86a76e4b04b1b2c63b4a1c6ab31f7313a11aae`
- panel rows: `2336`
- months: `584`
- future leakage: `0`
- train rows: `347`
- OOS rows: `236`
- fixed RMSE: `3.71293134576204`
- null RMSE: `3.77256576171896`
- RMSE improvement: `0.0158073893799398`
- `b3_b7_executed = false`
- `trading_action = false`

A second independent readback reproduced the coefficient vector, relative OOS metrics, all four block improvements, and the frozen B3 incrementality gate. A repository-wide query also exposed all three B2 Reality Gate rows and confirmed identical benchmark metrics across the canonical run and duplicate verification reruns.

---

## 10. Authority Boundary

`YMQ4-B2 = CLOSED / REALITY PASS`

Still false / unauthorized:

- `B3-B7 executed`
- dynamic-beta production claim
- Canon promotion
- portfolio sizing
- broker connection
- trading action

B3 requires a separate explicit human authorization.
