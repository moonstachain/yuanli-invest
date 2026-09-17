# YCI0-RP1-G6｜Capital Efficiency Evidence Admission Receipt

**Date:** 2026-09-17
**Gate:** `G6_CAPITAL_EFFICIENCY_ADMISSION`
**Latest evidence run:** `35210577631` (`YCI0 RP1 Capital Efficiency Evidence` run #7, SUCCESS)
**Artifact:** `10491722055 / yci0-rp1-g6-capital-efficiency-receipt`
**Head:** `6a64155980ee95205584fa45fe6daf070a1c30f3`
**Result:** `BLOCKED_BY_COVERAGE`
**Authority:** `RESEARCH_ONLY`
**Production mutation:** `0`

## Raw evidence proof

The latest cloud run physically archived **11 governed SEC raw objects** to private `ymq4-raw-evidence` with SHA-256 readback:

- 8 base objects: `companyfacts + submissions` for MSFT / NVDA / ANET / ETN;
- 3 governed NVDA filed-XBRL fallbacks: FY2026 10-K, FY2027 Q1 10-Q, FY2027 Q2 10-Q.

The filed-XBRL fallback is governed by `config/yci0_rp1/capital_efficiency_filing_bridges.v0.1.json`. It is `fallback_only`, `RESEARCH`, requires immutable raw archive/readback and exact semantic-equivalence proof, and grants zero downstream authority.

## Coverage result

| Cohort | Entity | Result | Mandatory identities | Current blocker |
|---|---|---|---:|---|
| HYPERSCALER | MSFT | QUALIFIED | 3/3 | none |
| COMPUTE | NVDA | QUALIFIED | 3/3 | none |
| NETWORKING | ANET | UNKNOWN | 0/3 | `NO_SINGLE_TAG_COVERS_LATEST_11:CAPEX` |
| POWER_ELECTRICAL | ETN | UNKNOWN | 0/3 | `NO_SINGLE_TAG_COVERS_LATEST_11:OPERATING_INCOME` |

Qualified metric identities: **`6 / 12`**. Required cohorts qualified: **`2 / 4`**. Therefore `capital_efficiency = UNKNOWN`.

## NVDA semantic bridge proof

NVDA moved from UNKNOWN to QUALIFIED without changing the accepted G6 economic definition.

1. CAPEX continuity was repaired by deterministic cumulative-flow reconstruction: FY Q4 can be reconstructed as FY less Q3 YTD when the same standard `PaymentsToAcquireProductiveAssets` concept is present in the filed accounting record. This removed the prior CompanyFacts aggregation gap.
2. FY2026 current marketable securities anchor uses filed-XBRL `MarketableSecuritiesAndEquitySecuritiesFVNI = 51.951B` at `2026-01-25`.
3. FY2027 Q1 disaggregation uses zero-dimension `DebtSecuritiesCurrent + EquitySecuritiesFvNi`; the same filing reports prior-period `39.065B + 12.886B = 51.951B`, exactly reconciling the FY2026 anchor before the current value is admitted.
4. FY2027 Q2 uses the same disaggregation and independently reconciles to the same `51.951B` prior-period anchor.
5. `LongTermDebtCurrent` and `DebtCurrent` are admitted as optional aliases only because their overlapping periods are value-equivalent; a mismatch still fails closed.

Filed-XBRL proof receipts:

- FY2026 anchor: `64ec8826685789f9c611ec9cf3ee5ac6128a7818d3189c2c9319726c949c1e2d`
- FY2027 Q1 disaggregation: `4076d8e86a060d95324440a47dcbd8f998581a4f12f29b0dae7394cc2be6da93`
- FY2027 Q2 disaggregation: `218b103e0b7e6cf0b9c3bc79155f339e5aec13283d11c9f25f092e9f4340c275`

Raw filed-XBRL SHA readbacks:

- FY2026 10-K: `af8398105d629d98defacca572c8e85fe0d8a5f551266b01df2d8be4fa03558f`
- FY2027 Q1 10-Q: `34b9c489ac8d4fad7f7896332a5e47af98586b834042470d70f265d37e911925`
- FY2027 Q2 10-Q: `fd37c5c3b08be610fa48f8e3e394ab8d2108a23bbc2dfa26ee0bf0d91493bdfd`

NVDA's latest four derived observations are consecutive and PASS for all three mandatory components.

## Admission decision

The latest receipt, replayed through the governed admission semantics, yields:

- `admission_status = BLOCKED_BY_COVERAGE`
- `g6_state = UNKNOWN`
- `current_scope = PARTIAL_REALITY_STATE_5_OF_6`
- `qualified_entities = [MSFT, NVDA]`
- `qualified_metric_identities = 6`
- `required_metric_identities = 12`
- `mutation_count = 0`
- `mutation_plan = []`
- `journey_stage = 02 EVIDENCE`
- `transition_suggestion = HOLD`
- `capital_authorized = false`
- `execution_authorized = false`

No G6 Supabase production rows were written, so the existing 5/6 production state card and runtime run remain authoritative.

## Remaining evidence bridge

Only two cohort-level evidence gaps remain:

- **ANET / NETWORKING:** quarterly PP&E and annual Productive Assets are not semantically identical. Do not use `FY ProductiveAssets - Q3 PP&E` unless first-party filing detail can exactly isolate the PP&E-only annual amount.
- **ETN / POWER_ELECTRICAL:** recent standard `OperatingIncomeLoss` continuity is absent. A company-specific operating-profit bridge requires accession-specific first-party semantic proof before admission.

## Hard negatives learned

`RAW ARCHIVE PASS != SEMANTIC COVERAGE PASS`.

`COMPANYFACTS GAP != ECONOMIC DISCLOSURE GAP`.

`TAG RENAME != DISAGGREGATION`; a disaggregation bridge is admissible only when the overlap period reconciles exactly.

`6/12 QUALIFIED != G6 QUALIFIED != FULL REALITY 6/6`.
