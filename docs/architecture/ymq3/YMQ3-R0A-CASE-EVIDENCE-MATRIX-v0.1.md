# YMQ3-R0A｜Case Evidence Matrix v0.1

**As of:** 2026-09-13  
**Machine source:** `config/ymq3/r0a_case_evidence_status.v0.1.json`  
**Authority:** Evidence Admission projection only

| Case | Market | Macro vintage | Official anchor | Narrative corpus | Rights | PIT provenance | Current verdict |
|---|---|---|---|---|---|---|---|
| C1 Dot-com 1999–2002 | provider binding pending | PASS | PASS | **BLOCKED** | **BLOCKED** | partial | **BLOCKED** |
| C2 GFC 2008–2009 | provider binding pending | PASS | PASS | **BLOCKED** | **BLOCKED** | partial | **BLOCKED** |
| C3 China leverage 2014–2016 | provider binding pending | partial | PASS | **BLOCKED** | **BLOCKED** | partial | **BLOCKED** |
| C4 COVID 2020 | provider binding pending | PASS | PASS | path exists / not measured | PASS for admitted metadata path | path exists / not measured | **READY_WITH_LIMITATIONS** |
| C5 Inflation 2021–2022 | provider binding pending | PASS | PASS | path exists / not measured | PASS for admitted metadata path | path exists / not measured | **READY_WITH_LIMITATIONS** |
| C6 AI 2022–2026 | provider binding pending | partial | PASS | path exists / not measured | PASS for admitted metadata path | path exists / not measured | **READY_WITH_LIMITATIONS** |

## Blocked-case reasons

### C1｜Dot-com

SEC/official primary material is available, but it cannot establish broad public Narrative diffusion by itself. GDELT 1.0 is event context, Google Books Ngram is long-horizon context, and Wayback access does not itself grant text-processing rights. No contracted multi-publisher historical-news corpus has been bound to the runtime.

### C2｜GFC

Fed and SEC anchors are strong, but the hard-negative crisis weeks do not yet have a rights-bound multi-publisher Story corpus. A hard-negative cannot be admitted on ordinary-week coverage alone.

### C3｜China leverage

Dated CSRC/PBOC/NBS examples prove that contemporaneous official evidence can be reconstructed, but the 2014-07-01 through 2015-02-18 interval precedes GDELT 2.0 and has no admitted Chinese multi-publisher Narrative corpus. Macro-vintage reconstruction is sampled, not yet systematic.

## Limited-case reasons

C4–C6 have a plausible modern open-data route through GDELT 2.0 metadata plus official anchors. They are still not `READY`, because this run has not materialized the topic-specific weekly panel required to prove:

- >=95% timestamp authority;
- >=80% week presence;
- median >=10 eligible documents per covered week;
- >=70% multi-publisher weeks;
- zero PIT/rights violations.

`PATH_EXISTS != COVERAGE_PROVEN`.

## Program-level implication

There are currently:

- `READY = 0`
- `READY_WITH_LIMITATIONS = 3`
- `BLOCKED = 3`
- `INDETERMINATE = 0`

Therefore the only admissible program verdict is:

# `INSUFFICIENT_EVIDENCE_INDETERMINATE`

This matrix does not authorize YMQ3-R0 feature/model computation, Forward Shadow, Capital Admission or execution.
