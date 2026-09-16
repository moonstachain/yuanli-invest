# YCI0-RP1-G0｜First Live Evidence Receipt

**Status:** `LIVE_FIRST_PARTY_EVIDENCE / PIT_NORMALIZED / RAW_SOURCE_ARCHIVE_PENDING`  
**Program:** `YCI0-RP1｜First Live Reality Admission`  
**Gate:** `G0｜One Live Evidence × One PIT Admission × One Human State Change`  
**Question:** `YCI0-RP0-CQ-001`  
**Authority:** `RESEARCH_ONLY`  

## 1. Frozen evidence object

- Entity: Microsoft Corp. (`MSFT`)
- Fiscal period: FY2026 Q4
- Quarter end: `2026-06-30`
- First-party release date / `known_as_of`: `2026-07-29`
- Metric ID: `MSFT_CASH_PAID_PP&E_FY26Q4`
- Metric name: Cash paid for property and equipment
- Value: **USD 35.802 billion**
- Source: Microsoft Investor Relations, FY26 Q4 Earnings Release
- Canonical locator: `https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast`

Microsoft's FY26 Q4 cash-flow table reports additions to property and equipment of $35.802B for the quarter. The earnings-call transcript separately states cash paid for PP&E was $35.8B and total capital expenditures were $41B including finance leases.

## 2. Interpretation boundary

This object is **total company PP&E cash spend**, not an AI-only capex series. It is admitted as a hyperscaler infrastructure-demand proxy and may not be restated as “Microsoft AI capex = $35.802B.”

`FIRST_PARTY_DISCLOSURE != AI_ONLY_METRIC != INVESTMENT_CONCLUSION`

## 3. PIT / provenance status

- Source role: `FIRST_PARTY_INVESTOR_RELATIONS`
- Authority tier: `company_primary_disclosure`
- Observation date: `2026-06-30`
- Release date: `2026-07-29`
- Vintage date: `2026-07-29`
- Known as of: `2026-07-29`
- Current retrieval: `2026-09-17`
- Normalized payload SHA-256: `65b534702cfd4585362f7dce71748c4c7b6e698393121307a8267442cef97547`
- Raw provider bytes archived: **NO**
- Immutable normalized receipt: **YES — this Git commit/file**

Because the original HTML/PDF bytes have not yet been archived into the Evidence Vault, the evidence may enter the Reality ledger as a normalized first-party PIT observation, but the Claim Receipt must remain **LIMITED** rather than `PASS` until raw-source byte archival is completed.

## 4. Wind runtime status

The authorized remote computer / Wind MCP CLI was unavailable during this gate. No Wind result is fabricated.

`WIND_PROVIDER_EQUIVALENCE = NOT_RUN`

When the Wind runtime returns, it should retrieve the same fiscal-period metric or an explicitly mapped equivalent and compare value, period, unit, provider timestamp, and lineage. Wind remains an Evidence provider, not the truth authority.

## 5. Required machine behavior

This evidence is allowed to:

- create/update a first-party source identity;
- create an immutable normalized source snapshot reference;
- create a PIT observation;
- create a `LIMITED` Claim Receipt;
- bind the flagship Capital Question to real evidence;
- replace the prior DEMO-only binding state.

It is **not** sufficient by itself to:

- advance the question beyond `02 EVIDENCE`;
- assert AI-Infra Reality is accelerating;
- create a Research Projection;
- enter Shadow;
- grant Capital or Execution Authority.

## 6. Next evidence

To move from a single observation to `Level / Δ / Δ²`, the same metric definition needs at least two additional PIT-qualified historical observations under the same measurement regime. A separate management metric (`total capex including finance leases`) must remain a distinct series rather than being mixed with cash PP&E.
