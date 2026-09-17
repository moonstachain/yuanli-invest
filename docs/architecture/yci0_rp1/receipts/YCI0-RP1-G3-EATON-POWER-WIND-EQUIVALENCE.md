# YCI0-RP1-G3｜Eaton Power/Grid Wind Provider Equivalence

**Status:** `NOT_AVAILABLE / FIRST_PARTY_ONLY`  
**Date:** 2026-09-17  
**Authority:** `EVIDENCE_CONTEXT_ONLY`  
**Capital Authority:** `false`  
**Execution Authority:** `false`

## Target first-party series

Metric: Eaton Electrical Americas twelve-month rolling average order organic growth.

Frozen observations:

- 2025 Q3: `7%`, released 2025-11-04
- 2025 Q4: `16%`, released 2026-02-03
- 2026 Q1: `42%`, released 2026-05-05
- 2026 Q2: `41%`, released 2026-07-31

Candidate series: `ETN_ELECTRICAL_AMERICAS_R12M_ORDER_ORGANIC_GROWTH_PCT`.

This is a power/electrical-infrastructure demand proxy. It is not an AI-only or data-center-only order series. Q3/Q4/Q1 disclosures explicitly associated the acceleration with data-center momentum; Q2 described data centers as a key growth driver but broader end markets also contributed.

## Wind call

Tool: `stock_data.get_stock_fundamentals`.

Query requested all four report periods and the exact `Electrical Americas` rolling-12-month organic order growth metric.

Provider response: `没找到数据` with no returned tables.

Raw response SHA-256: `84647f0d3f936385703e22249966279ef47f51e29f7cdba50bff54e037a3cc73`.

## Verdict

`NOT_AVAILABLE / FIRST_PARTY_ONLY`

No Wind value is inferred or substituted. Absence from this provider route does not weaken the first-party Eaton disclosure; it only means provider equivalence cannot be established through the tested Wind fundamental endpoint.

## Law

`PROVIDER_ABSENCE != SOURCE_ABSENCE`

`NO_RESULT != ZERO`

`WIND_EVIDENCE_ONLY != REQUIRED_FOR_FIRST_PARTY_ADMISSION`
