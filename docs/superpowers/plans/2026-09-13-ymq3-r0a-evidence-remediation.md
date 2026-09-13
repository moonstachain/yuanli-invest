# YMQ3-R0A｜Evidence Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Before any Story/Herding feature or model is computed, decide whether each of the six YMQ3-R0 historical cases has lawful, timestamp-valid, provenance-complete and reproducible Point-in-Time evidence.

**Architecture:** R0A is an Evidence Admission subsystem, not a model. It freezes evidence law, audits sources and rights, performs minimal physical source probes, measures weekly corpus coverage, and emits case-level plus program-level verdicts. Allowed program outcomes are `FULL6_READY`, `OPEN4_READY`, `INSUFFICIENT_EVIDENCE_INDETERMINATE`, and `PHYSICAL_FAIL`.

**Tech Stack:** Python 3.12; JSON/JSON Schema; existing YMQ-OS0 contracts; stdlib `unittest/hashlib/json/datetime/pathlib`; GitHub Actions for deterministic validation; authorized browser/API probes for source evidence.

**Spec:** `docs/superpowers/specs/2026-09-13-ymq3-r0-narrative-herding-pit-reality-audit-design.md`

## Global Constraints

- Frozen cases remain: `C1_DOTCOM 1999-01-01..2002-12-31`, `C2_GFC 2008-01-01..2009-12-31`, `C3_CHINA_LEVERAGE 2014-07-01..2016-02-29`, `C4_COVID 2020-01-01..2020-12-31`, `C5_INFLATION 2021-01-01..2022-10-31`, `C6_AI 2022-11-01..2026-08-31`.
- R0A computes no predictive feature, classifier or trading signal.
- `Narrative != Herding`; attention/event proxies are not automatically Narrative evidence.
- `T4_RETROSPECTIVE` material is annotation-only.
- `publication_available_at <= canonical_week_end` is mandatory for eventual Story inputs.
- Current revised macro series may not substitute for historical vintages.
- `UNKNOWN = DENY` for timestamp, provenance and rights.
- Public readability does not imply rights to process, store or redistribute full text.
- Rights are four separate axes: `processing_authority`, `raw_storage_authority`, `derived_feature_storage_authority`, `redistribution_authority`.
- No third-party article bodies enter Git; Git stores contracts, registries, hashes, locators and receipts only.
- CI tests are network-free; physical probes create separate receipts.
- Primary multimodal R0 eligibility requires >=4 `READY` cases, including >=2 narrative-heavy cases and >=1 acute-shock hard negative.
- Case exclusion is frozen before feature computation; no case is silently dropped after reveal.
- R0A creates no Capital or Execution Authority.

## Frozen readiness thresholds

A case is `READY` for primary multimodal R0 only when all mandatory evidence domains pass and the Narrative corpus satisfies all of:

- `pit_violation_count == 0`
- `unknown_processing_rights_count == 0`
- `unauthorized_raw_storage_count == 0`
- `timestamp_authority_rate >= 0.95`
- `scored_week_presence_rate >= 0.80`
- `median_eligible_documents_per_covered_week >= 10`
- `multi_publisher_week_rate >= 0.70`, with >=2 distinct `publisher_group_id` values
- narrative-heavy cases include at least one contemporaneous media/news/broadcast family; official releases/filings alone cannot prove broad Narrative diffusion.

Case verdicts are exactly `READY`, `READY_WITH_LIMITATIONS`, `BLOCKED`, `INDETERMINATE`. `READY_WITH_LIMITATIONS` may support infrastructure/annotation/behavior work but does not count toward the primary Story × Herding gate.

## Planned file map

```text
config/ymq3/
  r0a_evidence_gate.v0.1.json
  r0a_source_registry.v0.1.json
  r0a_case_evidence_status.v0.1.json

docs/architecture/ymq3/
  YMQ3-R0A-SOURCE-AUTHORITY-AUDIT-v0.1.md
  YMQ3-R0A-CASE-EVIDENCE-MATRIX-v0.1.md
  YMQ3-R0A-BLIND-ANNOTATION-PROTOCOL-v0.1.md
  YMQ3-R0A-EVIDENCE-SUFFICIENCY-DECISION-MEMO-v0.1.md
  YMQ3-R0A-HUMAN-REVIEW-CARD-v0.1.md

scripts/
  ymq3_r0a_evidence.py
  ymq3_r0a_source_probe.py
  validate_ymq3_r0a.py

tests/
  test_ymq3_r0a_evidence_gate.py
  test_ymq3_r0a_source_registry.py
  test_ymq3_r0a_case_verdicts.py
```

---

### Task 1｜Freeze Evidence Admission law before corpus acquisition

**Files:** create `config/ymq3/r0a_evidence_gate.v0.1.json`, `tests/test_ymq3_r0a_evidence_gate.py`, `scripts/validate_ymq3_r0a.py`.

**Produces:** exact cases, evidence domains, source/timestamp/right classes, thresholds and program verdict law.

- [ ] Write RED tests for exact non-overlapping case windows.
- [ ] Require evidence domains: `MARKET`, `MACRO_VINTAGE`, `OFFICIAL_ANCHOR`, `NARRATIVE_CORPUS`, `LICENSE_RIGHTS`, `PIT_PROVENANCE`.
- [ ] Freeze source verdicts: `ADMIT`, `ANNOTATION_ONLY`, `UNKNOWN_DENY`, `REJECT`.
- [ ] Freeze timestamp classes: `TS1_SOURCE_NATIVE`, `TS2_ARCHIVE_VERIFIED`, `TS3_PROVIDER_INDEXED`, `TS4_INFERRED_RETROSPECTIVE`; TS4 cannot enter Story features.
- [ ] Require four rights axes with values `ALLOW|DENY|UNKNOWN`; UNKNOWN fails closed for the requested action.
- [ ] Encode the readiness thresholds above exactly.
- [ ] Run `python -m unittest tests.test_ymq3_r0a_evidence_gate -v` and observe RED.
- [ ] Implement minimal gate + validator and rerun to GREEN.
- [ ] Commit the gate before any physical source probe or bulk acquisition.

---

### Task 2｜Build Source Authority Registry: access is not rights

**Files:** create `config/ymq3/r0a_source_registry.v0.1.json`, `tests/test_ymq3_r0a_source_registry.py`, `docs/architecture/ymq3/YMQ3-R0A-SOURCE-AUTHORITY-AUDIT-v0.1.md`.

Each source record must include:

```text
source_id, publisher_group_id, source_family, source_class,
case_coverage, historical_start, historical_end, timestamp_authority,
access_mode, machine_access, primary_locator, terms_locator,
processing_authority, raw_storage_authority,
derived_feature_storage_authority, redistribution_authority,
attribution_required, registry_verdict, verified_at,
verification_evidence_refs, notes
```

- [ ] Write RED tests requiring all fields and rejecting the inference `publicly_readable -> raw_storage_allowed`.
- [ ] Seed candidate roles: `FRED_ALFRED`, `SEC_EDGAR`, `FED_OFFICIAL`, `WHO_OFFICIAL`, `OPENAI_PRIMARY`, `GDELT_2_GKG_MENTIONS`, `GDELT_1_EVENTS`, `GOOGLE_TRENDS`, `GOOGLE_BOOKS_NGRAM`, `INTERNET_ARCHIVE_WAYBACK`, `CSRC_OFFICIAL`, `PBOC_OFFICIAL`, `NBS_OFFICIAL`, `SSE_OFFICIAL`, `SZSE_OFFICIAL`, `CNINFO_DISCLOSURES`, plus unsatisfied capability classes `LICENSED_EN_NEWS_ARCHIVE` and `LICENSED_CN_FIN_NEWS_ARCHIVE`.
- [ ] Keep the two licensed archive capability classes `UNKNOWN_DENY` until a named provider and contract are physically audited.
- [ ] Treat GDELT 1.0 and Google Trends as event/attention/control context by default, not primary Narrative truth.
- [ ] Store no original third-party news bodies in Git.
- [ ] Run tests and commit.

---

### Task 3｜Create physical source-probe receipts without bulk downloading corpora

**Files:** create `scripts/ymq3_r0a_source_probe.py`; runtime output `artifacts/ymq3/r0a/<run_id>/source-probe-receipts.jsonl`.

**Interfaces:** `build_probe_receipt(source_record, observed) -> dict`; `validate_probe_receipt(receipt) -> None`.

Receipt fields must include `run_id`, `source_id`, `probe_locator`, `observed_at`, `provider_status`, `sample_historical_locator`, `sample_publication_timestamp`, `historical_range_observed`, `machine_access_observed`, `terms_locator_observed`, `rights_verdict_observed`, `content_or_metadata_hash`, `notes`.

- [ ] Write deterministic tests using fake observations; no live network in CI.
- [ ] Implement receipt builder/validator; HTTP 200 cannot imply rights.
- [ ] Physically probe each candidate source family with an authorized browser/API runner using only metadata/sample records.
- [ ] Distinguish `published_at`, `available_at`, `archive_capture_at`, `retrieved_at`; retrieval time never substitutes for publication time.
- [ ] If rights cannot be established, write `UNKNOWN` and keep action denied.

---

### Task 4｜C1 Dot-com remediation: prove or reject a lawful 1999–2002 Story corpus

- [ ] Use SEC EDGAR only for company/filer primary perspective; it cannot alone prove broad public Narrative diffusion.
- [ ] Use Fed/official policy material as anchors, not media breadth.
- [ ] Evaluate Wayback captures only when original page/document dating plus archive capture support the claimed PIT availability.
- [ ] Keep GDELT 1.0 and Google Books Ngram as context/annotation, not weekly Story breadth.
- [ ] If the public/open stack fails thresholds, audit at least one named licensed historical English multi-publisher archive with explicit computational-research rights.
- [ ] Measure C1 coverage with frozen thresholds.
- [ ] If no lawful multi-publisher path qualifies, freeze C1 as `BLOCKED` or `READY_WITH_LIMITATIONS`; never weaken the gate.

---

### Task 5｜C2 GFC remediation: preserve the hard negative

- [ ] Use Federal Reserve/official records to anchor Bear Stearns, Lehman, AIG, facilities and policy chronology.
- [ ] Use SEC filings for contemporaneous institution/company disclosure.
- [ ] Treat GDELT 1.0 as event/attention context, not the primary Story corpus.
- [ ] Audit a lawful multi-publisher historical news path for 2008–2009.
- [ ] Ensure crisis/common-shock weeks themselves have sufficient coverage; ordinary-week coverage cannot hide hard-negative gaps.
- [ ] Measure C2 and freeze verdict.

---

### Task 6｜C3 China remediation: solve pre-Feb-2015 text and macro vintages

- [ ] Audit dated CSRC, PBOC, NBS, SSE, SZSE and legally accessible disclosure archives.
- [ ] Reject current revised NBS/PBOC series as historical T0 evidence unless original release/vintage can be reconstructed from dated releases or archived contemporaneous documents.
- [ ] Record that GDELT 2.0 begins in February 2015 and therefore cannot alone cover the C3 window starting 2014-07-01.
- [ ] Audit a lawful Chinese financial/news archive covering at least 2014-07 through 2015-02 and preferably the entire case.
- [ ] Count mirrored URLs under the same editorial owner as one `publisher_group_id`.
- [ ] If pre-Feb-2015 Narrative breadth remains missing, C3 cannot be `READY` for the primary Story audit.

---

### Task 7｜Qualify C4–C6 modern evidence with the same gate

- [ ] `C4_COVID`: verify GDELT 2.0 contemporary media metadata/corpus plus WHO/Fed/government anchors.
- [ ] `C5_INFLATION`: use ALFRED or equivalent vintage-aware macro sources, dated BLS/Fed releases and admitted contemporary media evidence.
- [ ] `C6_AI`: use OpenAI/company primary releases, SEC filings, admitted media evidence and dated capex/earnings/industry evidence; transcript bodies retain their own license boundary.
- [ ] Apply exactly the same coverage thresholds as C1–C3.
- [ ] Freeze C4–C6 verdicts before Story/model feature computation.

---

### Task 8｜Build weekly coverage compiler + fail-closed verdict engine

**Files:** create `scripts/ymq3_r0a_evidence.py`, `tests/test_ymq3_r0a_case_verdicts.py`, `config/ymq3/r0a_case_evidence_status.v0.1.json`.

**Interfaces:**

```python
validate_evidence_row(row, gate, registry) -> None
weekly_coverage(rows, case) -> dict
case_evidence_verdict(stats, mandatory_domains) -> str
program_evidence_verdict(case_verdicts, case_roles) -> str
```

- [ ] RED-test future timestamps, TS4 Story rows, duplicate publisher aliases, unknown processing rights and unauthorized payload storage.
- [ ] Implement weekly stats: total/covered weeks, presence rate, eligible document count, median docs/week, multi-publisher rate, timestamp authority rate, PIT violations, rights violations, source/publisher counts.
- [ ] `READY` requires every mandatory domain plus every frozen Narrative threshold.
- [ ] Program verdict law is exactly:

```text
FULL6_READY
  iff all six cases == READY

OPEN4_READY
  iff >=4 cases == READY
  and READY set has >=2 narrative-heavy cases
  and READY set has >=1 acute-shock hard-negative case

INSUFFICIENT_EVIDENCE_INDETERMINATE
  iff the multimodal minimum is not met and no integrity failure applies

PHYSICAL_FAIL
  iff admitted evidence contains PIT/provenance/rights integrity violations
```

- [ ] Run all R0A unit tests and `python scripts/validate_ymq3_r0a.py`.

---

### Task 9｜Freeze Blind Annotation protocol before phase labels

**Files:** create `docs/architecture/ymq3/YMQ3-R0A-BLIND-ANNOTATION-PROTOCOL-v0.1.md`.

- [ ] Two independent annotator packets per case use admitted chronology/evidence only.
- [ ] Hide CSAD, dependency, Story scores, model outputs, held-out predictions, future returns outside the annotation boundary and the other annotator's labels.
- [ ] Freeze A/B labels independently, calculate agreement, then adjudicate disagreements in a new projection without overwriting originals.
- [ ] Permit `ANNOTATION_UNCERTAIN`; do not force D0–D4 for weak evidence.

---

### Task 10｜Generate Evidence Sufficiency settlement + next-stage gate

**Files:** create `YMQ3-R0A-CASE-EVIDENCE-MATRIX-v0.1.md`, `YMQ3-R0A-EVIDENCE-SUFFICIENCY-DECISION-MEMO-v0.1.md`, `YMQ3-R0A-HUMAN-REVIEW-CARD-v0.1.md`; runtime receipt `artifacts/ymq3/r0a/<run_id>/evidence-sufficiency-receipt.json`.

Receipt must include `run_id`, `code_sha`, `gate_version`, `registry_hash`, `source_probe_receipt_hash`, `weekly_coverage_hash`, `case_verdicts`, `program_verdict`, `blocked_reasons`, ready/limited/blocked/indeterminate case lists, PIT/rights violation counts, non-authorizations and `artifact_hash`.

- [ ] Generate the six-row Evidence Matrix mechanically.
- [ ] Generate program verdict via code, not prose discretion.
- [ ] Apply next-stage law:

```text
FULL6_READY -> full six-case YMQ3-R0 becomes eligible for execution
OPEN4_READY -> only evidence-qualified multimodal subset may enter R0; exclusions stay visible
INSUFFICIENT_EVIDENCE_INDETERMINATE -> stop before features/models; continue remediation only
PHYSICAL_FAIL -> invalidate run, repair integrity issue, rerun from admitted inputs
```

- [ ] Preserve explicit non-authorizations: no scientific PASS claim, no R1 Forward Shadow, no Capital Admission, no sizing, no VeighNa/broker path.
- [ ] Add `validate_ymq3_r0a.py` to protected `contracts` CI only after unit gates are GREEN.
- [ ] Run fresh exact-head PR `repository-gates`; record `contracts` and `governance` in the receipt.
- [ ] Fresh-read final branch, PR diff, machine receipt and CI before claiming R0A machine qualification.

## Pre-audit priors — not verdicts

| Case | Current prior | Main unresolved issue |
|---|---|---|
| C1 Dot-com | likely BLOCKED/LIMITED | lawful weekly multi-publisher 1999–2002 Story corpus |
| C2 GFC | CONDITIONAL | lawful historical news breadth around shock weeks |
| C3 China leverage | CONDITIONAL | 2014-07→2015-02 Chinese Story corpus + macro vintages |
| C4 COVID | likely READY | physical rights/coverage verification |
| C5 Inflation | likely READY | physical rights/coverage verification |
| C6 AI | likely READY | physical rights/coverage verification |

These are priors only. R0A exists so physical evidence can overturn them.

## Definition of Done

R0A is complete only when the gate was committed before coverage reveal; every used source has timestamp/provenance/four-axis rights; admitted source families have physical probe receipts; six case metrics and verdicts are machine-generated before Story/model computation; no third-party raw corpus leaked into Git; the blind annotation protocol is frozen; exact-head tests/protected CI pass; and the Human Review Card states what the verdict does and does not authorize.

Only `FULL6_READY` or `OPEN4_READY` can make YMQ3-R0 model/replay execution eligible. Only a later genuine R0 scientific PASS can make `YMQ3-R1｜Forward Shadow Narrative-Herding State Runtime` eligible for separate authorization.
