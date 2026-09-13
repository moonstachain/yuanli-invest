# YKS0｜K-Shaped Society × Reality Distribution Regime

This directory is the governed **YKS0-R0 Research Estate** for the five-country 1990–2026 desktop evidence program.

## Authority at a glance

```text
authority_state = RESEARCH_CANDIDATE
reality_state = DESKTOP_EVIDENCE_HARDENED
scientific_state = STRONG_PRIOR / FORMAL_PIT_VALIDATION_REQUIRED
runtime_state = NOT_STARTED
capital_state = NOT_AUTHORIZED
execution_state = NOT_AUTHORIZED
```

This estate is **not** a trading signal, a production data warehouse, a completed historical PIT replay, or a scientific settlement of YKS0. G2 owns vintage-safe historical Reality reconstruction; G3 owns preregistered blind replay.

## Start here

### Human synthesis

- [Five-Country 1990–2026 Research Synthesis](reports/YKS0-R0-FIVE-COUNTRY-1990-2026-RESEARCH.md)
- [Three Divergences × Asset-Transmission Map](reports/YKS0-R0-DIVERGENCE-ASSET-MAP.md)
- [Desktop Research Settlement](settlements/YKS0-R0-DESKTOP-SETTLEMENT.md)

### Country dossiers

- [United States](countries/US.md)
- [Germany](countries/DE.md)
- [Japan](countries/JP.md)
- [South Korea](countries/KR.md)
- [China](countries/CN.md)

### Machine-readable research objects

- [Source Registry](evidence/source-registry.json) — exact source locators, authority grades, PIT readiness and source-fact summaries.
- [Evidence Claims](evidence/evidence-claims.json) — Source Fact / Research Inference / Scientific Status kept as separate fields.
- [45-Cell K Evidence Matrix](dimensions/k-dimension-evidence-matrix.json) — US/DE/JP/KR/CN × K01–K09, with UNKNOWN preserved.
- [H1–H8 Hypothesis Registry](hypotheses/hypothesis-registry.json) — null hypotheses, falsifiers, baselines, contradictory evidence and replay status.
- [50 Replay Case Candidates](replay/case-candidate-registry.json) — exact G0 event windows/questions; exact T0 and visible cutoffs remain unbound for G2.
- [PIT Readiness Matrix](replay/pit-readiness-matrix.json) — what is native, reconstructable, current-only, back-tested/restated or unknown.
- [Research Estate Manifest](manifests/research-estate-manifest.json) — stable machine discovery root for future UIG/Context Gateway use.

## Evidence law

Read [Evidence Authority × PIT Readiness Policy](evidence/source-authority-policy.md) before using any source. The controlling disciplines are:

`Reality > Belief`  
`ClaimAuthority <= EvidenceAuthority`  
`UNKNOWN = DENY`

A later-retrieved artifact does not become historical T0 evidence. Current authoritative statistics can support desktop research while remaining unqualified for historical replay.

## Research object hierarchy

```text
Source Fact
  -> Research Inference
  -> Scientific Status

Current/Retrospective Evidence
  -> PIT Readiness Audit
  -> G2 Historical Vintage Reconstruction
  -> G3 Blind Replay
  -> Scientific Settlement
```

Do not collapse these levels.

## Three target divergences

- `D-A INDEX–MEDIAN`: cap-weight/large-cohort outcomes versus median/equal-weight/broader-market outcomes. Conditional on the Price Gate.
- `D-B GDP–HOUSEHOLD`: aggregate output/productivity versus median wage/income/consumption/employment quality.
- `D-C PROFIT–EMPLOYMENT`: profit/output/value-capture concentration versus employment diffusion.

Current desktop prior: `D-C > D-B > D-A` in expected structural explanatory power. This is a candidate prior, not a settled ranking.

## Asset boundary

The only admitted research chain is:

`KRegime -> Value Capture -> Earnings/Cash-flow Distribution -> Ownership -> Price/Valuation/Discount Rate/Liquidity -> Relative Return Candidate`

No file in R0 may create target prices, allocation weights, position sizing, broker actions, paper orders, live orders, or execution authority.

## Key gaps intentionally left visible

The weakest R0 areas are K07 Region and K08 Opportunity across most countries; K06 wealth outside the US; direct K04 employment-diffusion evidence in China/Japan; historical firm-level PIT data; index constituent/delisting/corporate-action reconstruction; and China historical release/revision provenance. These gaps are inputs to G2 Evidence Sufficiency, not defects to hide with proxies.

## Validation

Repository validation entry point:

```bash
python scripts/validate_yks0_r0_research_estate.py
python -m unittest tests.test_yks0_r0_research_estate -v
```

The validator fails closed on missing estate paths, wrong country/dimension sets, scalar-K resurrection, broken evidence references, PIT laundering, premature replay qualification, forbidden investment/action keys, authority escalation, or a desktop settlement that exceeds R0's scientific ceiling.
