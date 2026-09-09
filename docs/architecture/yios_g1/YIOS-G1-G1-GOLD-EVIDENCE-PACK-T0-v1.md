# YIOS-G1-G1｜Gold Evidence Pack @ T0 — v1

**Case:** `YIOS-GOLD-001`  
**Historical T0:** `2024-01-31T23:59:59-05:00`  
**Evidence law:** `known_as_of <= T0`  
**Authority:** `RESEARCH_EVIDENCE_ONLY`  

> This pack reconstructs what was admissible at T0. It must not import later YMQ4-B2/B3 outcomes, later Gold price paths, or later narratives into the T0 state.

## 1. Machine PIT evidence

The governed Supabase PIT panel `gold_core_monthly_v0.1` materializes the following T0-aligned values:

| Factor | T0 value | PIT status | Source series | Snapshot |
|---|---:|---|---|---|
| Gold USD/oz | `2034.0` | `PIT_MARKET_RECONSTRUCTED` | `worldbank_pinksheet_gold` | `71d24a7e-33d2-4775-9b43-f9d521881e21` |
| USD broad index | `120.4331` | `PIT_MARKET_RECONSTRUCTED` | `DTWEXBGS` | `202f0c3c-25f0-4849-9140-d6249817f1a3` |
| Inflation YoY | `3.29776915615907` | `PIT_STRICT_ASOF_DERIVED` | `CPIAUCSL` | `6150296d-bb92-4e90-9451-4e0812692680` |
| 10Y real rate | `1.73` | `PIT_MARKET_RECONSTRUCTED` | `DFII10` | `ec23477e-04bf-4255-aefd-4d8493acf125` |

All four panel rows have `known_as_of = 2024-01-31` and measurement regime `2006_plus_modern`.

Snapshot SHA256 identities retained in the evidence ledger:

- Gold: `9fdcfa8a2aed9a1bb545a10c1a5ce036c6a0acd4766f450424ca800b4b5a0225`
- USD: `154c824238046f2ae5de399848655a51e3825693e4cb052255a82d87618351e5`
- CPI bundle: `3f840dd14dc43aadac9e7516b4c5aadc46846852467b5933c4a3b592fc6a949a`
- Real rate: `66238ed05e0192356bcc33aec69942826e1c1fe93d0276e353169a1c7341e1ca`

These source snapshots were physically retrieved later as part of historical PIT reconstruction; their later retrieval timestamp does not grant later information to T0. The controlling time field for the historical state is the frozen `known_as_of` / vintage logic.

## 2. Monetary-policy evidence admissible at T0

### Federal Reserve — A_PRIMARY

Federal Reserve FOMC statement, 31 January 2024:

https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm

Admitted facts:

- target range remained `5.25%–5.50%`;
- inflation had eased but remained elevated;
- the Committee did not expect rate cuts to be appropriate until it gained greater confidence inflation was moving sustainably toward 2%.

### BLS CPI — A_PRIMARY

BLS CPI release, 11 January 2024:

https://www.bls.gov/news.release/archives/cpi_01112024.htm

Admitted fact: December 2023 headline CPI was `+3.4% y/y`.

### BEA PCE — A_PRIMARY

BEA Personal Income and Outlays, 26 January 2024:

https://www.bea.gov/news/2024/personal-income-and-outlays-december-2023

Admitted facts: December 2023 PCE price index was `+2.6% y/y`; core PCE was `+2.9% y/y`.

## 3. Gold-demand evidence admissible at T0

### World Gold Council FY2023 — B_MARKET_PRIMARY / industry primary compilation

Published 31 January 2024:

https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2023

Central-bank section:

https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2023/central-banks

Admitted T0 facts:

- full-year 2023 central-bank net purchases: `1,037.4t`;
- central-bank purchases exceeded 1,000t for the second successive year;
- PBoC reported additions of `225t` in 2023;
- global Gold ETFs lost `244.4t` in 2023;
- total bar-and-coin investment was `1,189.5t`.

This is deliberately a mixed demand picture: official demand was exceptionally strong while global ETF demand remained negative.

## 4. Decisive H1 evidence gap

The frozen H1 law is not merely “central banks bought a lot.” It requires an exact threshold:

`P75(rolling_12m_official_net_purchases, 2010-01-01..2019-12-31) using only data known at T0`.

The governed runtime does not currently materialize a coherent exact T0-vintage rolling-12m official-demand series covering the entire 2010–2019 threshold window.

World Gold Council historical demand tables are subject to revisions across publications. Therefore, constructing the P75 by stitching later-vintage annual/quarterly tables into the T0 record would violate the Two-Clock and PIT laws.

Settlement consequence:

`H1_OFFICIAL_DEMAND_STRUCTURAL = INDETERMINATE`

This is `UNKNOWN = DENY`, not a negative claim that official demand was weak.

## 5. T0 state interpretation boundary

Evidence allows the following research-state candidate at T0:

- Gold remained resilient despite restrictive Fed policy and a positive real-rate environment;
- official-sector demand was historically salient;
- private demand was not uniformly bullish;
- a `Monetary Scarcity / S-R / Early Monetary-Regime Repricing` state was plausible enough to test.

Evidence does **not** allow, at T0:

- knowledge of later Gold returns;
- knowledge of B2/B3 scientific results;
- a settled claim that monetary-regime repricing was already proven;
- Capital Admission, position sizing, or execution action.

## 6. Evidence-pack integrity result

`PIT_INTEGRITY = PASS`

`FUTURE_LEAKAGE_COUNT = 0`

`H1_DECISIVE_THRESHOLD = UNAVAILABLE / FAIL_CLOSED`

The absence of a decisive threshold is retained as a first-class unknown rather than repaired with mixed-vintage hindsight.
