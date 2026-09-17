# YCI0-RP1-G0.5｜Wind Provider Equivalence Receipt

**Status:** `NON_EQUIVALENT / ADJACENT_METRIC`  
**Date:** 2026-09-17  
**Authority:** `EVIDENCE_CONTEXT_ONLY`  
**Capital Authority:** `false`  
**Execution Authority:** `false`

## Question
Can Wind `get_stock_fundamentals` supply the same metric as Microsoft Investor Relations `Additions to property and equipment` / `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment` for FY26 Q1-Q4?

## First-party target series

`MSFT_CASH_PAID_PP&E_QUARTERLY_USD_BN`

Microsoft IR observations:

- FY26 Q1: 19.394 USD bn
- FY26 Q2: 29.876 USD bn
- FY26 Q3: 30.876 USD bn
- FY26 Q4: 35.802 USD bn

Boundary: **total-company cash paid/additions to PP&E, not AI-only capex**.

## Wind calls

Tool: `stock_data.get_stock_fundamentals`

The provider returned a field family named `资本性支出`, denominated in `亿元`, rather than the exact first-party cash-flow concept. Normalized results are recorded only to explain the equivalence verdict; raw provider bodies remain local and are represented by SHA-256.

| Query period | Wind field | Unit | Returned value | Raw-response SHA-256 |
|---|---|---:|---:|---|
| 2025-09-30 | `2025年9月30日资本性支出` | 亿元 | 474.72 | `7472f929921dc8aacf10d9e631fc7f0e65c8dd716b0b12421363186006087a7f` |
| 2025-12-31 | `2025年资本性支出` | 亿元 | 645.51 | `4a4fcad156fe72212cd672c9aed19ec6a915d863234ef956005c2eac1118c1d7` |
| 2026-03-31 | `2026年1季末资本性支出` | 亿元 | 193.94 | `24df157082e966d84776c514acaf7c04e32ad528749c58aad5ad35517912464b` |
| 2026-06-30 | `2026年2季末资本性支出` | 亿元 | 492.70 | `9a5374f8b8f6751053b06e8248825dc7e4e283d989879ec062451ccae35335af` |

## Verdict

`NON_EQUIVALENT / ADJACENT_METRIC`

Reasons:

1. Wind returned `资本性支出`, not the exact Microsoft cash-flow concept `PaymentsToAcquirePropertyPlantAndEquipment`.
2. Units and period labels differ from the first-party series.
3. Exact accounting-definition equivalence is not established by the provider response.
4. No currency conversion or inferred reconciliation is allowed to manufacture equivalence.

Therefore Wind is retained as an adjacent provider/context source for this case, but **must not replace, overwrite, or cross-promote the Microsoft first-party PIT series**.

## Law

`PROVIDER_AVAILABILITY != SEMANTIC_EQUIVALENCE`

`ADJACENT_METRIC != SAME_SERIES`

`WIND_EVIDENCE_ONLY != FIRST_PARTY_SOURCE_REPLACEMENT`
