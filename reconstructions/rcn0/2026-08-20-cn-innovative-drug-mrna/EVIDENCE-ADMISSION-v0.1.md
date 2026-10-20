# RCN0 Evidence Admission v0.1

Replay: `RCN-REPLAY-20260820-CN-INNOVATIVE-DRUG-MRNA`

Status: `partial_admission`

Principle: `Claim Authority <= Evidence Authority`

This file distinguishes primary evidence, independent verification, source-synthesis claims and unresolved items. It does not allow a synthesis report to self-promote into primary evidence.

## 1. External catalyst | INTerpath-001

### Claim

Merck and Moderna announced positive topline Phase 3 INTerpath-001 results for intismeran autogene plus KEYTRUDA in completely resected stage IIB-IV melanoma; the trial met recurrence-free survival and distant metastasis-free survival endpoints and was described as the first positive Phase 3 readout for an mRNA-based cancer therapy / individualized neoantigen therapy.

### Evidence status

`ADMITTED_WITH_PRIMARY_LOCATOR_GAP`

Independent current verification:

- Reuters Breakingviews, 2026-08-19: Moderna market-value surge after promising personalized cancer-vaccine Phase 3 announcement; notes recurrence-free and metastasis outcomes and that detailed data had not yet been released.
- Multiple contemporaneous financial-news reproductions carry the same company-originated topline statement.

Primary-company background independently verified:

- Merck official release, 2026-06-01: five-year Phase 2b KEYNOTE-942 update; 49% reduction in recurrence/death risk and 59% reduction in distant metastasis/death; identifies INTerpath-001 as fully enrolled.
- Merck official release, 2026-01-20: same five-year Phase 2b program background and ongoing Phase 3 program.

Unresolved:

- the direct company-hosted 2026-08-19 Phase 3 press-release URL was not independently resolved in the current runtime. The claim therefore remains below full primary-admission authority even though the company-originated statement is independently corroborated.

### Boundary

The current topline did **not** disclose complete hazard ratios, p-values, subgroup data or full safety tables in the evidence retrieved here. Do not upgrade the claim to quantified Phase 3 efficacy beyond the disclosed endpoint success.

## 2. A-share / Hong Kong market closes

### Claims used in the replay

Source synthesis reports official 2026-08-20 closes including:

- CSI Vaccine & Biotechnology: +9.17%
- CS Innovative Drug (931152): +4.01%
- SW Healthcare: +3.73%
- Shanghai Composite: +0.24%
- CSI 300: +0.09%
- ChiNext: +0.64%
- STAR 50: -0.87%
- Hengrui: -6.00%
- WuXi AppTec: +2.38%
- vaccine/mRNA limit-up basket: seven names, all zero closing sell queue according to the source synthesis.

### Evidence status

`SOURCE_SYNTHESIS_VERIFIED_INTERNAL_CONSISTENCY / PRIMARY_ADMISSION_PENDING`

The supplied research report explicitly states that A-share/H-share close data were checked against official closing data and that stale index series were excluded. Internal consistency is strong and the same broad-market level is independently echoed in contemporaneous public market commentary.

However, the current runtime has not independently retrieved the official exchange/index-provider record for every value and order-book claim. Therefore these remain `pending_primary_admission` for Gold purposes.

## 3. Hengrui 2026H1 / 2Q26 financial evidence

### Claims used

Source synthesis reports:

- 1H26 revenue RMB 15.456bn, -1.94% YoY;
- 1H26 attributable profit RMB 4.465bn, +0.34%;
- 1H26 adjusted attributable profit RMB 3.730bn, -12.71%;
- 2Q26 revenue RMB 7.315bn, -14.50%;
- 2Q26 attributable profit RMB 2.183bn, -15.25%;
- 2Q26 adjusted attributable profit RMB 1.557bn, -35.39%.

### Evidence status

`SOURCE_SYNTHESIS_CLAIMING_OFFICIAL_FILING / PRIMARY_FILING_RETRIEVAL_PENDING`

The synthesis explicitly states these were checked against the official 2026-06-30 interim report disclosed 2026-08-20. The current runtime has not independently fetched the exchange filing, so Claim Authority remains bounded.

## 4. WuXi AppTec operating validation

### Claims used

Source synthesis reports:

- 1H attributable profit RMB 11.08bn;
- 2Q adjusted-profit growth ~92%;
- full-year revenue guidance raised to RMB 58.5-60.5bn;
- backlog RMB 66.43bn, +25.2% YoY.

### Evidence status

`SOURCE_SYNTHESIS / PRIMARY_FILING_PENDING`

These claims are used only to support the relative statement that CXO possessed stronger contemporaneous operating validation than the vaccine mapping chain. They are not promoted to primary evidence until the company filing or official release is independently admitted.

## 5. Valuation percentiles

### Claims used

Source synthesis reports:

- CS Innovative Drug PE-TTM ~51.90; 1Y and 3Y PE percentiles 100%;
- SW Healthcare PE-TTM ~49.08; 3Y percentile ~91.93%;
- CSI Vaccine & Biotechnology PB ~3.25; 1Y percentile 100%; PE distorted by loss-making constituents.

### Evidence status

`METHOD_AND_TIMESTAMP_REVIEW_PENDING`

These data weaken a simple low-valuation-repair hypothesis at the index level, but Gold admission requires the exact provider methodology, timestamp, historical-window definition and treatment of negative earnings.

## 6. Evidence authority matrix

| Evidence object | Current authority | Gold-ready? |
|---|---|---|
| Phase 3 catalyst existence and endpoint success | independent current verification + company-program primary background | partial |
| Exact Phase 3 efficacy magnitude | not available from admitted evidence | no |
| Broad A-share index closes | synthesis + partial independent corroboration | no |
| Seven limit-up/order-book claims | synthesis claiming official checks | no |
| Hengrui official financials | synthesis claiming official filing | no |
| WuXi operating/guidance figures | synthesis | no |
| Valuation percentiles | synthesis; methodology pending | no |

## 7. Evidence verdict

`EVIDENCE_GATE = PARTIAL / GOLD_BLOCKING`

The external catalyst is sufficiently verified to support a **Shadow** narrative-state analysis, but the replay cannot become Gold until official China-market, company-filing and valuation-methodology evidence is independently admitted.
