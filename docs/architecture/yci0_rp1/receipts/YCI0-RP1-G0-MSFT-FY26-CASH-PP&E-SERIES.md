# YCI0-RP1-G0｜MSFT FY26 Cash-PP&E PIT Series Receipt

**Status:** `LIVE_FIRST_PARTY_SERIES / PIT_NORMALIZED / RAW_SOURCE_ARCHIVE_PENDING`  
**Series ID:** `MSFT_CASH_PAID_PP&E_QUARTERLY_USD_BN`  
**Measurement regime:** `CASH_PAID_PP&E_TOTAL_COMPANY`  
**Authority:** `RESEARCH_ONLY`

## Frozen observations

| Fiscal quarter | Quarter end | Release / known_as_of | Cash paid for PP&E | Source |
|---|---:|---:|---:|---|
| FY2026 Q1 | 2025-09-30 | 2025-10-29 | $19.394B | Microsoft Investor Relations Q1 cash flows |
| FY2026 Q2 | 2025-12-31 | 2026-01-28 | $29.876B | Microsoft Investor Relations Q2 cash flows |
| FY2026 Q3 | 2026-03-31 | 2026-04-29 | $30.876B | Microsoft Investor Relations Q3 cash flows |
| FY2026 Q4 | 2026-06-30 | 2026-07-29 | $35.802B | Microsoft Investor Relations Q4 earnings release |

Canonical sources:

- `https://www.microsoft.com/en-us/investor/earnings/fy-2026-q1/cash-flows`
- `https://www.microsoft.com/en-us/investor/earnings/fy-2026-q2/cash-flows`
- `https://www.microsoft.com/en-us/investor/earnings/fy-2026-q3/cash-flows`
- `https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast`

## Per-observation normalized hashes

- FY26 Q1: `f130df11ce37430fab6132720bbfd83b38fc4ff1f183df28ad7518542578fa62`
- FY26 Q2: `4443ebc3754af625ace69420faa42664c864871dc3f32c6f4feeee29ac54b847`
- FY26 Q3: `96655466cc3625654be3ef0d4d921e87e58446ce6d75d4507567ffc2c5ff321a`
- FY26 Q4: `65b534702cfd4585362f7dce71748c4c7b6e698393121307a8267442cef97547`

## Descriptive changes only

The raw numeric sequence is `19.394 → 29.876 → 30.876 → 35.802` USD billions.

Quarter-to-quarter level changes are approximately `+10.482`, `+1.000`, and `+4.926` USD billions. The latest second difference is therefore positive relative to the prior sequential change.

**This arithmetic must not be promoted to an AI-Infra Reality verdict yet.** Every observation in this first pass remains `LIMITED` because the original provider bytes are not archived in the Evidence Vault, and this metric is total-company PP&E rather than AI-only capex.

`NUMERIC_ACCELERATION != EVIDENCE_PASS != REALITY_ACCELERATING`

## Gate consequence

The correct machine state after this series is admitted is still:

- Journey Stage: `02 EVIDENCE`
- Human Evidence Status: `LIMITED`
- Machine Evidence Status: `UNKNOWN`
- Delta: `UNKNOWN`
- Delta2: `UNKNOWN`
- Transition Suggestion: `HOLD`

Next required actions: archive original source bytes; run Wind provider-equivalence; only then allow the existing Reality State Compiler to evaluate the same-regime series.
