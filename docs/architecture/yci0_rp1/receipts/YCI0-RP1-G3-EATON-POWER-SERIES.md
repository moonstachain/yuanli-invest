# YCI0-RP1-G3｜Eaton Electrical Americas Power/Grid Series

**Status:** `NORMALIZED_FIRST_PARTY / RAW_ARCHIVE_PENDING`  
**Authority:** `RESEARCH_ONLY`  
**Date:** 2026-09-17

## Metric

`Electrical Americas twelve-month rolling average order organic growth`

Candidate series ID:

`ETN_ELECTRICAL_AMERICAS_R12M_ORDER_ORGANIC_GROWTH_PCT`

Measurement regime:

`EATON_ELECTRICAL_AMERICAS_R12M_ORGANIC_ORDER_GROWTH`

## Frozen observations

| Quarter | Observation date | Released / known as of | Value |
|---|---|---|---:|
| 2025 Q3 | 2025-09-30 | 2025-11-04 | 7% |
| 2025 Q4 | 2025-12-31 | 2026-02-03 | 16% |
| 2026 Q1 | 2026-03-31 | 2026-05-05 | 42% |
| 2026 Q2 | 2026-06-30 | 2026-07-31 | 41% |

## First-party sources

- 2025 Q3: Eaton, `Eaton Reports Record Third Quarter 2025 Results, with Accelerating Orders and Continued Backlog Growth`.
- 2025 Q4: Eaton, `Eaton Reports Record Fourth Quarter 2025 Results, with Accelerating Orders and Continued Backlog Growth, and Issues Guidance on 2026 Outlook`.
- 2026 Q1: Eaton, `Eaton Reports Record First Quarter 2026 Results, with Accelerating Growth in Sales, Orders and Backlog...`.
- 2026 Q2: Eaton, `Eaton Reports Record Second Quarter 2026 Results, with Strong Organic Growth, Accelerating Orders and Backlog...`.

Each disclosure identifies the metric as the twelve-month rolling average of orders in Electrical Americas and reports the organic year-over-year growth rate.

## Proxy boundary

This is an **electrical infrastructure / power-management demand proxy**.

It is not an AI-only or data-center-only order series. Eaton serves multiple end markets. Q3/Q4/Q1 explicitly associated order momentum with data-center demand; Q2 also described data centers as a key growth driver while acknowledging broader end-market strength.

Therefore the metric may inform `power_grid`, but must not be relabeled as `AI data-center power orders`.

## Wind boundary

The tested Wind fundamental route returned `没找到数据` for the exact rolling-12-month organic order-growth metric.

Verdict: `NOT_AVAILABLE / FIRST_PARTY_ONLY`.

No zero, interpolation, or substitute metric is inferred.

## Current admission rule

Until raw Eaton source bytes are archived and SHA-readback verified, normalized claims remain `LIMITED`; the Reality State Compiler must keep this dimension `UNKNOWN`.

`NORMALIZED_VALUE != RAW_ARCHIVED_EVIDENCE`
