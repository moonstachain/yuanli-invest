# YMQ-GOLD2｜Machine Qualification Receipt v0.1

**Program:** `YMQ-GOLD2｜Gold Monetary Regime × Property Drift × Timing Compiler`  
**PR:** `#99`  
**State:** `MACHINE_QUALIFIED / AWAITING_HUMAN_GATE`  
**Qualification branch head:** `07927ea6790b6e9b28df4b504e4a46cf001bf6e2`  
**Base:** `main @ 2e5cefe98f0b2fff03720e28cd93e942b88b35f3`

## 1. What was physically proven

### G0｜Semantic convergence — PASS

The accepted `YIOS-G1 / YIOS-GOLD-001` T0 state was compiled into `GoldUnifiedState@PIT` without authority escalation.

At `2024-01-31` the compiler preserved:

- candidate monetary regime: `EARLY_MONETARY_REGIME_REPRICING`;
- real rate, USD, inflation and demand evidence already admitted by YIOS;
- `R` and `S` as research candidates only;
- explicit UNKNOWN for fiscal/sovereign state, crowding, multi-lens valuation and future policy path;
- `capital_authorized=false`;
- `sizing_authorized=false`;
- `execution_authorized=false`;
- `broker_action=false`.

### G1｜Property Drift — PHYSICAL PASS / RESEARCH ONLY

The read-only Reality Run reused the governed `gold_core_monthly_v0.1` panel:

- 584 months;
- 2,336 PIT rows;
- future leakage = 0;
- rolling diagnostic window = 60 prior months;
- YMQ4-B3 history preserved exactly as `DYNAMIC_BETA_DOES_NOT_BEAT_B2`.

Observed B2 fixed coefficients:

- alpha = `0.388403239784779`;
- beta USD = `-0.43784352934335996`;
- beta inflation = `1.5097162035675193`;
- beta real rate = `-0.08225103153920177`.

Property-drift diagnostics by canonical B2 OOS block:

| Block | Median coefficient distance vs B2 | Dominant-factor match | Fixed-beta residual bias | Research state |
|---|---:|---:|---:|---|
| GFC 2007–2009 | 2.6479 | 0.3333 | 0.2526 | `DRIFT_CONFIRMED_RESEARCH_ONLY` |
| Post-GFC 2010–2019 | 3.3073 | 0.3333 | 0.0287 | `DRIFT_CANDIDATE` |
| Covid/Rates 2020–2022 | 5.2080 | 0.1667 | 0.0046 | `DRIFT_CANDIDATE` |
| Current 2023–2026-08 | 1.6714 | 0.5909 | 0.4111 | `DRIFT_CANDIDATE` |

Scientific scope remains:

`descriptive_property_drift_not_alpha`

This does **not** overturn the B3 no-go and does not establish tradable alpha.

### G2｜Expectation × Reality — CONTRACT PASS / EVIDENCE INCOMPLETE

The compiler exists and is fail-closed. The four-factor PIT core panel does not contain all required expectation-side evidence such as expected policy path, positioning and narrative/crowding.

Therefore historical core Replay correctly emits:

`INDETERMINATE`

rather than backfilling future information.

### G3｜Valuation × Driver — CONTRACT PASS / EVIDENCE INCOMPLETE

Three frozen lenses exist:

1. `MACRO_FAIR_VALUE_LENS`;
2. `MONETARY_REGIME_PREMIUM_LENS`;
3. `REFLEXIVITY_POSITIONING_LENS`.

The core PIT panel cannot independently populate all three. Historical core Replay therefore emits:

`UNIDENTIFIABLE`

No target price is generated.

### G4｜Eight-regime blind replay core — PHYSICAL PASS

Eight frozen historical windows materialized under PIT discipline.

Core Gold cumulative log returns observed from the governed panel:

| Window | Gold log return | USD log return | Inflation Δ pp | Real-rate Δ pp | Property drift |
|---|---:|---:|---:|---:|---|
| R1 1978–1980 | +113.46% | -5.68% | +5.88 | +2.00 | pre-OOS / insufficient |
| R2 1981–1985 | -51.33% | +22.79% | -9.04 | +1.79 | pre-OOS / insufficient |
| R3 1999–2002 | +12.84% | +5.79% | +0.71 | -3.88 | pre-OOS / insufficient |
| R4 2007–2009 | +58.87% | -4.34% | -0.10 | -0.93 | `DRIFT_CONFIRMED_RESEARCH_ONLY` |
| R5 2011–2015 | -25.68% | +22.49% | -0.61 | -0.27 | `DRIFT_CANDIDATE` |
| R6 2018–2020 | +38.52% | +1.12% | -1.07 | -1.50 | insufficient |
| R7 2022–2024-01 | +12.78% | +4.37% | -3.58 | +2.77 | `DRIFT_CANDIDATE` |
| R8 2024-02–2026-08 | +77.41% | -1.41% | +0.01 | +0.71 | `DRIFT_CANDIDATE` |

The R4 B2-OOS boundary bug discovered during execution was corrected: the replay now applies the diagnostic to the actual overlap beginning `2007-01-31` rather than rejecting the whole 2007–2009 window.

Every replay still leaves missing evidence domains explicit:

- expected policy path;
- official demand series;
- private flow / positioning;
- narrative crowding;
- monetary-regime premium lens.

No historical outcome was used to fill those fields.

### G5｜RAY × Yiru × Machine — CONTRACT PASS / HUMAN EVIDENCE PENDING

The triangulation object exists.

- RAY slot = `PENDING_HUMAN_EVIDENCE`;
- Yiru slot = `PENDING_HUMAN_EVIDENCE`;
- anonymous Get-note speaker identity = `PENDING_HUMAN_ADJUDICATION`;
- Machine is prohibited from filling human slots.

### G6｜30-Day Live Shadow — CONTRACT FROZEN / NOT ACTIVATED

A provider-replaceable live-shadow contract exists with Wind as preferred evidence provider.

It explicitly keeps false:

- live scheduler authority;
- capital authority;
- sizing authority;
- execution authority;
- broker action;
- VeighNa authority;
- Canon promotion authority.

## 2. Machine evidence

### YMQ-GOLD2 Reality workflow

Run: `35112012750`  
Job: `104847861407`  
Conclusion: `SUCCESS`

Focused tests executed successfully:

- compiler: 15;
- property drift: 4;
- blind replay: 5;
- config authority: 2;
- YIOS convergence: 2.

Total GOLD2 focused tests: **28 PASS / 0 FAIL**.

Reality artifact:

- name: `ymq-gold2-reality-pack`;
- artifact id: `10452533208`;
- files: unified-state + property-drift + blind-replay;
- SHA-256: `e843bcf10b0ffcdcd7246ede49f18c6d97f085d598ee078c0cb7ad93a3f51e75`.

### Repository gates

Run: `35112012733`

- `governance` = SUCCESS;
- `contracts` = SUCCESS;
- full unittest discovery = SUCCESS;
- leak guard = SUCCESS.

## 3. Scientific non-claims

This receipt does **not** claim:

- Gold is bullish or bearish now;
- Property Drift predicts future returns;
- rolling beta beats B2;
- a target Gold price;
- a recommended Gold allocation;
- a buy/sell/timing instruction;
- RAY or Yiru judgment without explicit human evidence.

## 4. Authority state

```text
Research implementation     QUALIFIED
PIT core replay             QUALIFIED
Property Drift              RESEARCH-ONLY QUALIFIED
Expectation × Reality       CONTRACT QUALIFIED / DATA INCOMPLETE
Valuation × Driver          CONTRACT QUALIFIED / DATA INCOMPLETE
Human triangulation         AWAITING HUMAN EVIDENCE
Live shadow scheduler       DENY
Capital                     DENY
Sizing                      DENY
Execution                   DENY
Broker / VeighNa            DENY
Canon / merge               DENY
```

## 5. Human Gate

Machine execution stops here pending explicit Human decisions defined in the companion Human Review Card.