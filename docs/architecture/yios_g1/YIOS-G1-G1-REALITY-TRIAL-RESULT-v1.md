# YIOS-G1-G1｜Gold Reality Trial Result — Candidate v1

**Case:** `YIOS-GOLD-001`  
**Trial authority:** `AUTHORIZE_GOLD_G1_REALITY_TRIAL`  
**Historical T0:** `2024-01-31T23:59:59-05:00`  
**Reality Gate run:** `c9b6aada-f439-4ef3-830d-7d8df6b71625`  
**Current authority:** `RESEARCH_SETTLEMENT_CANDIDATE_ONLY`  

> This is a machine research-settlement candidate. It is not Human G2 acceptance, Capital Admission, sizing authority, or execution authority.

## 1. Executive Settlement

```text
PIT Integrity   PASS
H1 Official Demand Structural      INDETERMINATE
H2 Traditional Macro Decoupling    SUPPORTED
H3 Price Confirmation              SUPPORTED
H4 Narrative / Private Demand      EXPLORATORY ONLY

PRIMARY CLAIM
GOLD_EARLY_MONETARY_REGIME_REPRICING
= INDETERMINATE
```

The central result is deliberately asymmetric:

> Gold subsequently rose strongly and exhibited large positive residual performance versus the frozen traditional-macro baseline, but the preregistered primary claim still does **not** pass because its mandatory H1 threshold cannot be reconstructed with sufficient PIT/vintage authority.

That is the intended behavior of `UNKNOWN = DENY`.

## 2. PIT Integrity

`GoldState@T0` contains only evidence known at or before T0.

- Future leakage count: `0`
- YMQ4-B2/B3 later outcomes used as T0 evidence: `false`
- Post-T0 Gold path used to form the T0 state: `false`

Result: `PASS`.

## 3. H1｜Official Demand Structural

Frozen rule:

`P75(rolling_12m_official_net_purchases, 2010-2019) using only data known at T0`

Future Reality readback shows:

- 2024 central-bank and other institutional demand: `1,044.6t` in the WGC FY2024 publication;
- 2025 central-bank and other institutional demand: `863.3t` in the WGC FY2025 publication.

However, the exact coherent T0-vintage monthly/quarterly series needed to calculate the frozen 2010–2019 rolling-12m P75 threshold is not materialized in the governed runtime. WGC historical demand data are revision-prone across later publications.

The system therefore refuses to synthesize a mixed-vintage threshold after seeing the answer.

**H1 settlement: `INDETERMINATE`.**

This does not mean official demand was weak. It means the exact preregistered decisive test cannot be executed with adequate evidence authority.

## 4. H2｜Traditional Macro Decoupling

B0 is the frozen protocol-side four-factor traditional macro baseline:

`Gold ~ USD + InflationChange + RealRateChange`

The 24-month forward measurement begins **after** T0, from February 2024 through January 2026.

| Window | Cumulative B0 residual, log % | Frozen test |
|---|---:|---|
| T+3M | `13.159744628679` | positive |
| T+6M | `15.7785512393508` | positive |
| T+12M | `27.5074997964836` | positive |
| T+24M | `75.6115226190574` | positive |

Result:

- positive windows: `4/4`;
- T+12M `> 0`;
- T+24M `> 0`;
- no H2 defeat condition triggered.

**H2 settlement: `SUPPORTED`.**

Important limitation: this supports the preregistered residual-persistence claim. It is not evidence of a tradable forecasting model.

## 5. H3｜Price Confirmation

| Window | Cumulative Gold return, log % | Frozen test |
|---|---:|---|
| T+3M | `13.6293062427252` | positive |
| T+6M | `16.4630758978954` | positive |
| T+12M | `28.6944337265241` | positive |
| T+24M | `84.8771700005504` | positive |

Result:

- positive windows: `4/4`;
- T+12M `> 0`;
- T+24M `> 0`;
- no H3 defeat condition triggered.

**H3 settlement: `SUPPORTED`.**

But the Constitution explicitly states `price_up_alone_can_pass = false`.

## 6. B0 vs B1 sealed-forward readback

24 forward months, February 2024 through January 2026:

| Metric | B0 Traditional Macro | B1 Null |
|---|---:|---:|
| RMSE | `4.59739791982403` | `4.67959381509622` |
| MAE | `3.39853402948101` | `3.617070681837` |
| Sign accuracy | `91.67%` | `79.17%` |

B0 modestly beats B1 while Gold simultaneously accumulates a very large positive residual. The correct interpretation is not “the baseline predicted the rally”; rather, the baseline retained some incremental monthly explanatory value while leaving a large persistent residual unexplained.

## 7. Ablations

### ABL-1｜Remove official demand

Primary settlement becomes unidentifiable because H1 is mandatory.

### ABL-2｜Remove fiscal and narrative

H2 and H3 numerical settlements do not change. H4 remains non-decisive.

### ABL-3｜Downgrade authority to secondary evidence

Decisive primary settlement is denied.

### ABL-4｜B0-only reconstruction

H2 remains supported, but that cannot settle the full regime-repricing claim.

## 8. Hard Negatives

All eight frozen hard negatives were enforced:

- `PRICE_UP_ONLY` — rejected as sufficient proof;
- `OFFICIAL_DEMAND_ONLY` — rejected as sufficient proof;
- `NARRATIVE_ONLY` — rejected as sufficient proof;
- `POST_T0_LEAKAGE` — zero leakage;
- `B2_B3_RETROJECTION` — blocked from T0 state;
- `NEGATIVE_EVIDENCE_REWRITE` — no historical rewrite;
- `RESEARCH_TO_CAPITAL_AUTO_PROMOTION` — blocked;
- `RESEARCH_TO_EXECUTION_AUTO_PROMOTION` — blocked.

## 9. System-level learning

This run produces an important distinction:

```text
GOLD PRICE OUTCOME: STRONGLY POSITIVE
H2: SUPPORTED
H3: SUPPORTED
H1: INDETERMINATE
PRIMARY SCIENTIFIC SETTLEMENT CANDIDATE: INDETERMINATE
SYSTEM INTEGRITY: PASS
```

The OS succeeds when it can refuse to call a bullish thesis “proven” even after a huge rally, because one mandatory evidence gate remains unresolved.

`SYSTEM_PASS != GOLD_BULLISH_OUTCOME`

## 10. Authority Boundary

Still unauthorized:

- Capital Admission;
- PositionPassport;
- portfolio / position sizing;
- YVN1-A1 runtime;
- VeighNa installation or invocation;
- broker credentials / connection;
- Broker Paper;
- Live Execution;
- real capital movement;
- automatic research-to-execution.

## 11. Next Gate

The machine candidate stops here.

Required independent Human token:

`ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT`

Until that token is received, the primary result remains:

`RESEARCH_SETTLEMENT_CANDIDATE / INDETERMINATE / NOT CAPITAL AUTHORIZED`.
