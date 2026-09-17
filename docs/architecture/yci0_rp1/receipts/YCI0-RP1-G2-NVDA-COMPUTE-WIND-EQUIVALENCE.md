# YCI0-RP1-G2｜NVIDIA Compute Wind Provider Equivalence

**Status:** `NON_EQUIVALENT / ADJACENT_SEGMENT_CONTEXT`  
**Date:** 2026-09-17  
**Authority:** `EVIDENCE_CONTEXT_ONLY`  
**Capital Authority:** `false`  
**Execution Authority:** `false`

## Target first-party series

Metric: NVIDIA quarterly `Data Center revenue` disclosed by NVIDIA Newsroom.

Frozen observations:

- FY26 Q3, quarter ended 2025-10-26, released 2025-11-19: `51.2` USD bn
- FY26 Q4, quarter ended 2026-01-25, released 2026-02-25: `62.3` USD bn
- FY27 Q1, quarter ended 2026-04-26, released 2026-05-20: `75.2` USD bn
- FY27 Q2, quarter ended 2026-07-26, released 2026-08-26: `89.0` USD bn

Series candidate: `NVDA_DATA_CENTER_REVENUE_QUARTERLY_USD_BN`.

## Wind calls

Tool: `stock_data.get_stock_fundamentals`.

Wind returned the business-line concept `主营项目名称 = 数据中心产品` with `主营项目收入` in `亿元`, not a provider response that establishes semantic identity with NVIDIA's quarterly Newsroom `Data Center revenue` series.

| Requested report period | Wind field family | Returned value | Raw response SHA-256 |
|---|---|---:|---|
| 2025-10-26 | 数据中心产品 / 主营项目收入 | 796.06 亿元 | `2754def2a888998d7def4f2cce04567d5d42c7cdf309e421ea114dd9a1657823` |
| 2026-01-25 | 数据中心产品 / 主营项目收入 | 1151.86 亿元 | `f6e08f26c2c65b25a54b89ef509f51aed7f2f6140877c40d14c9a461d3f31165` |
| 2026-04-26 | 数据中心产品 / 主营项目收入 | 802.08 亿元 | `eef435aa7c96d8808a2036e0bed63f68fd41eb239d216c49388c7221ff606601` |
| 2026-07-26 | 数据中心产品 / 主营项目收入 | 802.08 亿元 | `bcebd23f265e02f1871117ad1fb7e93a0e0b1318599aeaa26c2f70a19f7352ed` |

## Verdict

`NON_EQUIVALENT / ADJACENT_SEGMENT_CONTEXT`

Reasons:

1. Wind's returned concept is a business-line `主营项目收入` field, not an explicitly identical quarterly NVIDIA Newsroom `Data Center revenue` accounting/disclosure object.
2. Period labels and units differ.
3. The repeated `802.08` values across different requested dates show that the provider response cannot be assumed to be the same point-in-time quarterly series without stronger lineage.
4. Currency conversion or period inference is prohibited as a means of manufacturing equivalence.

Therefore Wind may provide adjacent context, but it must not replace or overwrite the NVIDIA first-party PIT series.

## Law

`PROVIDER_AVAILABILITY != SEMANTIC_EQUIVALENCE`

`BUSINESS_SEGMENT_CONTEXT != SAME_SERIES`

`WIND_EVIDENCE_ONLY != FIRST_PARTY_SOURCE_REPLACEMENT`
