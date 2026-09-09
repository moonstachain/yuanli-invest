# YGR0-S0｜Gold Genesis Case Canon Constitution — Design

Date: 2026-09-09  
Status: `DESIGN_CANDIDATE / HUMAN_REVIEW_REQUIRED`  
Scope: `YGR0 only`  
Repository: `moonstachain/yuanli-invest`

## 0. Purpose

YGR0 turns the completed Gold research battles into the first canonical Genesis Case for Yuanli Investment Research OS.

Its job is not to prove a Gold model. Its job is to freeze an immutable, auditable answer to:

> What did Yuanli believe, what evidence was admissible at the time, what experiments were actually run, what Reality said, what failed, what remains unknown, and what authority was or was not earned?

YGR0 is the bridge from one successful research program to a reusable research operating discipline.

The canonical settlement target is:

`GOLD_GENESIS_CASE_SETTLED`

This must never be described as `GOLD_MODEL_VALIDATED`, `DYNAMIC_BETA_VALIDATED`, or any equivalent scientific or capital-authority escalation.

---

## 1. Authority position and temporal direction

YGR0 sits below YIP0 philosophy authority and below the existing Yuanli investment ontology. It may summarize and freeze historical case evidence; it may not redefine upstream philosophy, engines, thesis semantics, capital authority, or historical receipts.

The Genesis sequence is intentionally asymmetric:

```text
YIP0 + existing OS / ME laws
        ↓ constrain
YGR0 Gold Genesis Case
        ↓ supplies proven case evidence
YRP1 future research protocol
        ↓ once accepted, constrains future research battles
Future Gold / Copper / NVIDIA / BTC cases
```

YRP1 does **not** retroactively create or rewrite the Gold Genesis history. Gold is the first case evidence from which YRP1 may later be abstracted. Once YRP1 exists, Gold may serve as its first Golden Fixture, but the original YGR0 settlement remains an immutable historical ledger fact.

YGR0 may not mutate DP1-A, DP1-B, B2, or B3 historical receipts in place.

---

## 2. Inputs and immutable lineage

YGR0 consumes exactly four Gold battle lineages:

1. `YMQ4-DP1-A` — external runtime × source authority Reality Proof.
2. `YMQ4-DP1-B` — Gold 1978–2026 Historical PIT Backfill.
3. `YMQ4-B2` — Fixed Beta Baseline × OOS Incrementality Gate.
4. `YMQ4-B3` — Dynamic Beta Reality Challenge.

The current accepted main branch already contains DP1-A, DP1-B and B2. B3 is currently settled on Draft PR #72 and is not yet part of main. YGR0 implementation therefore has a hard prerequisite:

`B3_NEGATIVE_EVIDENCE_ON_MAIN == true`

No YGR0 Canon Settlement may pass while the B3 scientific no-go remains only on a side branch.

Historical lineage must retain, at minimum, the original battle ID, physical status, scientific observation where applicable, Reality Gate run ID, executed Git SHA, canonical receipt path, and any material artifact identity.

---

## 3. Three-state separation

YGR0 freezes the following invariant for the Gold case:

`PhysicalStatus != ScientificStatus != AuthorityStatus`

### 3.1 PhysicalStatus

Answers whether the experiment or data-plane operation actually ran as specified.

Allowed values for the Gold Genesis Case summary:

- `PASS`
- `FAIL_CLOSED`
- `NOT_RUN`

### 3.2 ScientificStatus

Answers what Reality said about the research claim.

Allowed values:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `NOT_SUPPORTED`
- `INDETERMINATE`
- `NOT_APPLICABLE`

For Gold v1, expected settlement includes:

- DP1-A: `NOT_APPLICABLE` scientific status; physical data-plane proof only.
- DP1-B: `NOT_APPLICABLE` scientific status; physical PIT-panel proof only.
- B2: `SUPPORTED` only for the narrow claim `FIXED_BETA_BEATS_NULL`, with the qualifier `MODEST`.
- B3: `NOT_SUPPORTED` for the preregistered claim that the single 60-month Rolling OLS candidate robustly beats B2 under all frozen gates.

### 3.3 AuthorityStatus

Answers what the result is allowed to authorize.

Gold v1 may authorize only:

- historical research-case settlement;
- reuse as a Golden Fixture / reference case for future protocol design;
- learning admission.

It must not authorize:

- production model promotion;
- B4–B7 execution;
- portfolio sizing;
- broker connection;
- buy/sell/hold action;
- trading execution;
- a universal claim that dynamic beta is invalid;
- a universal claim that dynamic beta is valid.

---

## 4. Canonical objects

YGR0 implementation must create exactly four first-class objects.

### 4.1 `GoldGenesisCaseManifest`

Machine-readable source of truth. Proposed path:

`config/ygr0/gold_genesis_case.v1.json`

Minimum fields:

```text
schema_version
case_id
target_id
period
case_status
source_receipts[]
physical_status
scientific_status
authority_status
evidence_ledger
learning_delta
open_unknowns
non_authorizations
settlement
```

Required stable identities:

```text
case_id: YGR-GOLD-001
target_id: GOLD
```

Allowed case lifecycle values:

```text
DRAFT
LINEAGE_LOCKED
NEGATIVE_EVIDENCE_ADMITTED
CANON_CANDIDATE
HUMAN_ACCEPTED
GOLD_GENESIS_CASE_SETTLED
```

`GOLD_GENESIS_CASE_SETTLED` is legal only after the final Human + repository settlement gate.

`source_receipts[]` must contain the four battle lineages and may only point to canonical repository receipts / immutable Reality Gate identities.

### 4.2 `GoldGenesisCaseCanon`

Human-readable canonical case document. Proposed path:

`docs/architecture/ygr0/GOLD-GENESIS-CASE-CANON-v1.md`

This document is a human explanation of the machine manifest and original receipts. It may not invent new numeric evidence.

It must answer exactly these six questions:

1. What did we initially believe or attempt to test?
2. What evidence and PIT boundary were admissible?
3. What physical research infrastructure was actually built and proven?
4. What did the fixed-beta baseline establish?
5. What did the dynamic-beta challenge fail to establish?
6. What remains unknown and therefore still cannot be claimed?

### 4.3 `GoldGenesisCaseLearning`

Learning delta. Proposed path:

`docs/architecture/ygr0/GOLD-GENESIS-CASE-LEARNING-v1.md`

Every admitted learning entry must use:

```text
Before
Evidence
Settlement
After
Still Unknown
```

The learning document may update the current knowledge state but must not rewrite the original hypothesis or historical receipt.

Required Gold v1 learning:

```text
Before:
Dynamic beta was a plausible route to improve static macro transmission modeling.

Evidence:
60M Rolling OLS improved aggregate RMSE and MAE versus B2, but improved only 2/4 frozen OOS regimes.

Settlement:
The preregistered B3 candidate did not pass its full victory law.

After:
Dynamic transmission remains plausible as a research question, but simple rolling-beta robustness is unproven.

Still Unknown:
Whether failure came from estimator lag, omitted drivers, nonlinear transmission, time-scale/measurement mismatch, or dynamic-beta estimation noise.
```

### 4.4 `YGR0Validator`

Proposed path:

`scripts/validate_ygr0.py`

The validator is a fail-closed contract. It must reject any case state that violates the invariants below.

---

## 5. Positive and negative evidence law

YGR0 establishes the case-level law:

`POSITIVE_EVIDENCE_AUTHORITY == NEGATIVE_EVIDENCE_AUTHORITY`

A negative scientific result is not a lower-class artifact.

The Gold Canon must therefore freeze both:

- B2 positive evidence: `FIXED_BETA_BEATS_NULL`, explicitly qualified as modest and non-tradable.
- B3 negative evidence: `DYNAMIC_BETA_DOES_NOT_BEAT_B2` for the single preregistered 60M Rolling OLS candidate.

The validator must fail if:

- B2 positive evidence exists but B3 negative evidence is omitted;
- B3 is summarized only as `PASS` without separating physical pass from scientific no-go;
- aggregate B3 metric improvement is described as overall scientific validation;
- the B3 2/4 regime failure is missing;
- a negative result exists only in prose but not in the machine manifest.

---

## 6. No Silent Rewrite

YGR0 extends `NO_SILENT_THESIS_MIGRATION` into a research-history invariant:

`NO_SILENT_HYPOTHESIS_REWRITE`

Forbidden transformations include:

```text
B3 hypothesis loses
→ rename the claim after seeing the result
→ describe the same run as success
```

```text
B3 loses 3/4 regime gate
→ silently drop the regime gate
→ retain only aggregate RMSE/MAE
```

```text
B3 candidate loses
→ generalize that all dynamic-beta methods fail
```

```text
B3 candidate loses
→ immediately substitute Kalman/TVP under the same battle identity
```

Any second hypothesis must receive a new governed identity, later intended as `YMQ4-B3R` or a child battle thereof.

---

## 7. Evidence ledger

The manifest must distinguish evidence class from interpretation.

Minimum ledger categories:

```text
PHYSICAL_EVIDENCE
SCIENTIFIC_POSITIVE_EVIDENCE
SCIENTIFIC_NEGATIVE_EVIDENCE
ENGINEERING_INCIDENT
LEARNING_INFERENCE
OPEN_UNKNOWN
```

Gold v1 must preserve engineering incidents that materially hardened the OS, including at least:

- PostgREST 1000-row truncation during B2, followed by fail-closed repair;
- direct-script import-path failure during the first B3 authorized physical attempt, followed by regression test and module-invocation repair.

These incidents are not scientific evidence about Gold, but they are evidence about the robustness of the Research OS.

---

## 8. Settlement state machine

YGR0 case state machine:

```text
DRAFT
  ↓
LINEAGE_LOCKED
  ↓
NEGATIVE_EVIDENCE_ADMITTED
  ↓
CANON_CANDIDATE
  ↓
HUMAN_ACCEPTED
  ↓
GOLD_GENESIS_CASE_SETTLED
```

### `LINEAGE_LOCKED`

All four battle receipts resolve to canonical immutable identities. B3 must already exist on main.

### `NEGATIVE_EVIDENCE_ADMITTED`

The B3 physical/scientific split and 2/4 failure are machine-readable in the manifest.

### `CANON_CANDIDATE`

Manifest, human Canon, Learning Delta and validator all exist; repository tests are green.

### `HUMAN_ACCEPTED`

Requires a separate explicit human acceptance token. Implementation completion does not imply this state.

### `GOLD_GENESIS_CASE_SETTLED`

May be entered only after Human Acceptance and clean repository integration.

---

## 9. Validator invariants

`validate_ygr0.py` must fail closed on at least the following:

1. fewer or more than the required DP1-A / DP1-B / B2 / B3 Genesis lineage entries;
2. B3 receipt not present on main at settlement time;
3. B3 physical status not represented separately from B3 scientific status;
4. B3 scientific status anything other than `NOT_SUPPORTED` for this candidate;
5. omission of the `2/4` positive-regime result and frozen `>=3/4` threshold;
6. B2 described as strong prediction, statistical significance, or tradability;
7. any `production`, `portfolio`, `broker`, or `trading` authority set true;
8. source receipt IDs / Reality Gate IDs inconsistent with canonical receipts;
9. original receipt mutation rather than reference/lineage;
10. missing `Still Unknown` section;
11. wording or machine fields that imply all dynamic-beta methods fail;
12. wording or machine fields that imply dynamic beta has been validated;
13. hidden replacement of a defeated hypothesis under the same battle identity;
14. missing negative-evidence entry;
15. case status set to `GOLD_GENESIS_CASE_SETTLED` before the required Human Acceptance token and repository integration gate.

---

## 10. Settlement Gate

YGR0-S0 implementation is considered machine-complete only when all of the following are true:

```text
B3 negative evidence integrated to main
DP1-A canonical lineage resolves
DP1-B canonical lineage resolves
B2 canonical lineage resolves
B3 canonical lineage resolves
GoldGenesisCaseManifest validates
GoldGenesisCaseCanon exists
GoldGenesisCaseLearning exists
Negative evidence machine-readable
Open unknowns explicit
No authority escalation
Repository governance PASS
Repository contracts PASS
Full unit tests PASS
Draft PR remains unmerged until Human Gate
```

Machine-complete status before human acceptance:

`YGR0_CANON_CANDIDATE_READY_FOR_HUMAN_REVIEW`

Final status after explicit human acceptance and clean integration:

`GOLD_GENESIS_CASE_SETTLED`

---

## 11. Explicit non-goals

YGR0 does not:

- run a new Gold model;
- change B2 or B3 metrics, windows, factors, thresholds, or outcomes;
- run Kalman / TVP / DCC / HMM / regime switching;
- execute B4–B7;
- create a production `DynamicTransmissionState` claim;
- generalize one Gold result into a universal law of markets;
- grant capital or trading authority;
- define YRP1 in production;
- execute B3R diagnostics;
- modify YIP0, ME0, ME1, or historical receipts in place.

---

## 12. Handoff to YRP1

YGR0 produces a bounded set of `proven_disciplines` for later abstraction. Proposed Gold-qualified candidates:

```text
Authority
PIT
Baseline
PreRegistration
KillGate
Settlement
Physical-vs-Scientific status separation
Negative-evidence parity
No Silent Hypothesis Rewrite
Research Pass != Capital Pass
```

YRP1 must not simply copy these into universal law. It must mark them initially as `GOLD_QUALIFIED` and define a later cross-domain transfer gate before claiming universal qualification.

---

## 13. Handoff to YMQ4-B3R

YGR0 must preserve the B3 unresolved mechanism question without proposing a rescue model.

Required open question:

> Why did the 60M Rolling Dynamic Beta candidate improve versus B2 in 2010–2019 and 2023–2026, but underperform in GFC 2007–2009 and COVID/Rates 2020–2022?

The case must preserve at least these competing-explanation families as `OPEN_UNKNOWN`, not conclusions:

- estimator lag;
- omitted driver;
- nonlinear transmission;
- time-scale / measurement mismatch;
- dynamic-beta estimation noise.

No second-model eligibility is created by YGR0.

---

## 14. Implementation topology after design approval

Expected implementation artifacts:

```text
config/ygr0/gold_genesis_case.v1.json

docs/architecture/ygr0/
  GOLD-GENESIS-CASE-CANON-v1.md
  GOLD-GENESIS-CASE-LEARNING-v1.md
  YGR0-HUMAN-REVIEW-CARD-v0.1.md

scripts/validate_ygr0.py

tests/test_ygr0_contract.py
```

B3 integration to main is a prerequisite integration step, not a silent copy into YGR0.

The implementation plan must preserve existing repository branch protection and use Draft PR + fresh repository-gates before presenting YGR0 for Human Review.

---

## 15. Design decision

The central design decision is:

> Gold becomes Canon as a settled history of what Reality allowed us to know, including failure. It does not become Canon as a winning model.

Compressed rule:

`CASE_GENERATES_LEARNING; LEARNING_DOES_NOT_REWRITE_CASE.`

And the research-OS principle YGR0 is designed to prove is:

`A VALID RESEARCH SYSTEM MUST BE ABLE TO CANONIZE A NEGATIVE RESULT WITHOUT TRYING TO RESCUE IT.`
