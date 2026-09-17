# YCI0-RP1-G5｜Financing Regime Reality PASS

**Status:** `PASS / RESEARCH_ONLY`
**Dimension:** `financing_regime`
**Compiler state:** `MIXED / MEDIUM`
**Scope after admission:** `PARTIAL_REALITY_STATE_5_OF_6`
**As of ceiling:** `2026-08-26T23:59:59Z`

## 1｜Frozen construction

Financing Regime uses three already-frozen RP0 metric families:

1. `AIINFRA.RATES.US10Y_NOMINAL` → FRED `DGS10`
2. `AIINFRA.RATES.US10Y_REAL` → FRED `DFII10`
3. `AIINFRA.FX.DXY_USD` → FRED `DTWEXBGS` broad USD proxy

Sampling policy: **last valid daily observation in each complete month, Apr-Jul 2026**. Partial August observations are excluded to keep all three metrics in the same monthly sampling regime.

The three metrics are compiled independently for Level / Δ / Δ² and aggregated only at the dimension-state layer. No cross-metric time-series concatenation is allowed.

## 2｜Raw evidence proof

### DGS10 nominal 10Y

GitHub Actions workflow `YCI0 RP1 Financing DGS10 Evidence`, run `35187024943`, completed successfully.

- source: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`
- raw bytes: `268727`
- SHA-256: `c4bd527f5b92c7e536808a0189a3e038a44c6850b2cd5124ac9016be5eecaaf6`
- private bucket: `ymq4-raw-evidence`
- storage readback SHA = source SHA
- downstream research/evidence-promotion/capital/execution authority: all `false`

### DFII10 real 10Y and DTWEXBGS USD proxy

These reuse the governed YMQ4-DP1B source snapshots:

- DFII10 snapshot `ec23477e-04bf-4255-aefd-4d8493acf125`
- DTWEXBGS snapshot `202f0c3c-25f0-4849-9140-d6249817f1a3`

`YMQ4-DP1-B-REALITY-RECEIPT-v0.1` proves immutable raw-object capture, provenance snapshots, PIT/as-of reconstruction, database readback, replay coverage, and zero future leakage for that data plane.

## 3｜PIT series and compiler output

| Metric | Apr | May | Jun | Jul | Latest Δ | Latest Δ² | State |
|---|---:|---:|---:|---:|---:|---:|---|
| DGS10 nominal 10Y | 4.40 | 4.45 | 4.44 | 4.75 | +0.31 | +0.32 | ACCELERATING |
| DFII10 real 10Y | 1.94 | 2.07 | 2.20 | 2.47 | +0.27 | +0.14 | ACCELERATING |
| Broad USD proxy | 118.6710 | 118.8783 | 120.9248 | 119.7034 | -1.2214 | -3.2679 | DECELERATING |

Existing `runtime.yci0_rp0.state_compiler` produced:

- `financing_regime.state = MIXED`
- `financing_regime.confidence = MEDIUM`
- `financing_regime.known_as_of = 2026-07-31T00:00:00Z`

This is a **mechanical multi-metric state**, not a discretionary macro label.

## 4｜Production persistence

- 12 YCI0 canonical PIT observations: physically written and read back
- 12 `PASS / RESEARCH_ONLY` claim receipts: physically written and read back
- Reality compiler run: `43e010ed-d8d9-4867-914f-339879c992b0`
- Reality state card: `ba6ab0a7-59dd-4799-abc7-1412a86c8d42`
- state hash: `db84f7a0ff505edffaeaee9b320d776d8f51fcf448fb586ff1bfdea0e7eee40b`
- total evidence refs: `28`

## 5｜Boundaries and anti-claims

- `DTWEXBGS` is a Federal Reserve broad trade-weighted USD proxy, **not literal ICE DXY**.
- DGS10 / DFII10 are Treasury market observations, **not direct corporate funding spreads**.
- `MIXED` does not mean neutral financing conditions; it means the frozen component states disagree under the existing compiler.
- Five qualified dimensions do not settle overall AI-Infra Reality.
- `capital_efficiency` remains `UNKNOWN`.
- No Narrative, Shadow, Capital, sizing, broker, or Execution authority is granted.

## 6｜Next gate

Freeze the Capital Efficiency economic/accounting construct before selecting data. Do not fill 6/6 using a convenient generic margin, ROIC, FCF margin, or capex/revenue ratio without a preregistered definition.
