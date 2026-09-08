# YMQ4-DP1-B｜Gold 1978–2026 Historical PIT Backfill Design

Status: `HUMAN_APPROVED / IMPLEMENTATION_AUTHORIZED`

## Mission

Materialize a reproducible monthly Gold core research panel from January 1978 through the latest complete month available in 2026, with explicit Point-in-Time semantics and no silent upgrade of reconstructed historical market data into strict-vintage evidence.

DP1-B ends at a data Reality Gate. It does **not** execute or tune B2–B7.

## Frozen law

`DATA REVEAL → MODEL FREEZE`

Once real historical values are exposed by this pipeline, B2–B7 model windows, transformations, baselines and win/loss criteria must not be changed merely because outcomes are visible.

## Core factors

The backfill materializes four monthly factors:

1. `gold_usd_oz`
2. `usd`
3. `inflation_yoy`
4. `real_rate`

The minimum complete-month coverage target is `>= 0.80` for each preregistered replay window. Future leakage tolerance is `0`.

## Measurement regimes

### 1978-01 through 2002-12

- Gold: World Bank Pink Sheet monthly Gold, USD/troy ounce; `PIT_MARKET_RECONSTRUCTED`.
- USD: Federal Reserve `DTWEXM` daily major-currencies dollar index, sampled as the last available observation on or before month-end; `PIT_MARKET_RECONSTRUCTED`.
- Inflation: CPI `CPIAUCSL`, reconstructed from a same-vintage ALFRED as-of view and therefore `PIT_STRICT_ASOF_DERIVED` when the as-of query succeeds.
- Real rate: last available `DTB3` 3-month Treasury bill market yield minus latest same-vintage CPI YoY known at decision date; `HISTORICAL_PROXY` / `PIT_DERIVED_PROXY`.

The historical proxy is not equivalent to 10Y TIPS real yield.

### 2003-01 through 2005-12

- Gold: World Bank Pink Sheet; `PIT_MARKET_RECONSTRUCTED`.
- USD: `DTWEXM`; `PIT_MARKET_RECONSTRUCTED`.
- Inflation: same-vintage CPI YoY as above.
- Real rate: `DFII10`, last available observation on or before month-end; `PIT_MARKET_RECONSTRUCTED`.

### 2006-01 through 2019-12

- Gold: World Bank Pink Sheet; `PIT_MARKET_RECONSTRUCTED`.
- USD: `DTWEXBGS`, last available observation on or before month-end; `PIT_MARKET_RECONSTRUCTED`.
- Inflation: same-vintage CPI YoY.
- Real rate: `DFII10`.

### 2020-01 onward

Same as 2006–2019. No historical series is upgraded to strict-vintage status merely because the source is official.

## Source authority

- World Bank Pink Sheet is an institutional monthly reconstruction source for Gold. The raw XLSX bytes are immutable evidence; the parsed Gold column is research-only market reconstruction.
- FRED/ALFRED distributes BLS CPI and Federal Reserve market series. Raw API responses are stored with SHA-256 and source snapshot metadata.
- `CPIAUCSL` uses ALFRED real-time/as-of semantics. Market series use their contemporaneously observable date as the logical known-as-of under `PIT_MARKET_RECONSTRUCTED`; retrieval date remains separately preserved by `evidence.source_snapshots.retrieved_at`.

## Decision calendar

One decision date per calendar month: calendar month-end. Market observations are selected as the latest non-missing observation on or before that decision date.

CPI is selected only when its release date is on or before the decision date. The YoY transformation must use values from the **same as-of vintage**, preventing index-base/revision mismatch across the two levels used in the ratio.

## Data plane

Raw provider payloads go to private bucket `ymq4-raw-evidence` with SHA-256 metadata.

Normalized source observations remain in `pit.observations`.

Derived monthly factor states are stored in a new fail-closed table:

`pit.decision_asof_values`

Key:

`panel_id × decision_date × factor_id`

Required fields include value, PIT status, known-as-of, measurement regime and JSON provenance.

## Runtime objects

DP1-B records a `runtime.reality_gate_runs` receipt containing:

- source snapshots and SHA-256 values;
- date coverage;
- per-factor completeness;
- replay-window completeness;
- future-leakage count;
- measurement-regime counts;
- Git SHA;
- final status.

## Replay windows

Coverage is explicitly reported for:

- `1978-01-01` to `1979-12-31`
- `2008-01-01` to `2009-12-31`
- `2020-01-01` to `2020-12-31`
- `2022-01-01` to `2022-12-31`
- `2023-01-01` to latest complete 2026 month

## Gate semantics

`DP1B_CORE_BACKFILL_PASS` requires:

- all required sources physically fetched or an explicitly permitted reconstructed substitute used;
- every raw payload stored privately and SHA-read back;
- no `known_as_of > decision_date` in the materialized panel;
- each replay window has at least 80% complete months for all four core factors;
- no secret/raw payload committed to Git;
- independent database readback matches receipt counts.

Anything else is `FAIL_CLOSED` or `PARTIAL_RESEARCH_ONLY`; no B2–B7 authorization follows automatically.

## Explicit non-authorizations

DP1-B does not authorize model tuning, B2–B7 execution, Canon promotion, portfolio sizing, broker integration or trading.
