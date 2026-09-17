# YCI0-RP1-G6｜Capital Efficiency Evidence Admission Receipt

**Date:** 2026-09-17
**Gate:** `G6_CAPITAL_EFFICIENCY_ADMISSION`
**Result:** `BLOCKED_BY_COVERAGE`
**Authority:** `RESEARCH_ONLY`
**Production mutation:** `0`

## Raw evidence proof

GitHub Actions `YCI0 RP1 Capital Efficiency Evidence` run `35200548325` completed `SUCCESS`. Eight SEC official raw objects were archived to private `ymq4-raw-evidence` and physically SHA-256 read back: `companyfacts + submissions` for MSFT, NVDA, ANET, and ETN. Artifact: `yci0-rp1-g6-capital-efficiency-receipt`, artifact id `10487991517`.

The archive receipt itself grants zero downstream authority. Its semantic boundary is explicit: current SEC aggregate XBRL reconstruction linked to original accessions is not a byte-for-byte historical snapshot of each filing at original acceptance time.

## Coverage result

| Cohort | Entity | Result | Mandatory metric identities | Primary blockers |
|---|---|---|---:|---|
| HYPERSCALER | MSFT | QUALIFIED | 3/3 | none |
| COMPUTE | NVDA | UNKNOWN | 0/3 | no single CAPEX tag covers latest 11 quarters; no single current-marketable-securities tag covers latest 11; current-debt disclosure regime break |
| NETWORKING | ANET | UNKNOWN | 0/3 | no single CAPEX tag covers latest 11 quarters |
| POWER_ELECTRICAL | ETN | UNKNOWN | 0/3 | no single operating-income tag covers latest 11 quarters; current finance-lease-liability disclosure regime break |

Qualified metric identities: `3 / 12`. Required cohorts qualified: `1 / 4`. Therefore `capital_efficiency = UNKNOWN`.

## Admission decision

The real Task-4 receipt was compiled through `scripts/yci0_rp1_g6_admit.py`. The deterministic decision is:

- `admission_status = BLOCKED_BY_COVERAGE`
- `g6_state = UNKNOWN`
- `current_scope = PARTIAL_REALITY_STATE_5_OF_6`
- `mutation_count = 0`
- `mutation_plan = []`
- `journey_stage = 02 EVIDENCE`
- `transition_suggestion = HOLD`
- `capital_authorized = false`
- `execution_authorized = false`

No Supabase G6 Source/Snapshot/Observation/Claim rows were written, so no production state card or runtime run changed. Existing 5/6 production state remains authoritative.

## Hard negative learned

`RAW ARCHIVE PASS != SEMANTIC COVERAGE PASS`.

A provider can expose current XBRL facts and the raw objects can pass immutable archive/readback while the accounting series still fails the frozen 11-quarter semantic-regime requirement. The correct result is `UNKNOWN`, not tag stitching, generic ROIC substitution, or a manufactured 6/6.
