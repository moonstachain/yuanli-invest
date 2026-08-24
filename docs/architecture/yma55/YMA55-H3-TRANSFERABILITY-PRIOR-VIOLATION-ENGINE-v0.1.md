# YMA55-H3｜Transferability × Prior Violation Engine — Design Spec

**Status:** `design_candidate_for_human_review`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Base:** `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
**Dependencies:** YMA55-H1 + YMA55-H2 written specifications  
**Capital / trading authority:** none

## 0. Purpose

YMA55-H3 hardens the step that most historical frameworks leave implicit:

> Even if a historical mechanism was real, can it validly transfer into the current institutional world — and is current reality behaving as that prior says it should?

H3 therefore introduces two separate but linked objects:

1. `TransferabilityAssessment`
2. `PriorViolationRecord`

The first limits how much authority a historical episode may lend to the present. The second detects when current observations violate the pre-committed expectations carried by that prior.

The objective is to prevent two common errors:

- **analogy overreach** — a valid old mechanism is imported into a structurally different world;
- **prior loyalty** — the model keeps defending a historical prior after current reality has materially broken it.

---

## 1. TransferabilityAssessment

Canonical question:

> What must remain structurally similar for this historical mechanism to be transportable into the current case?

Required fields:

- `assessment_id`
- `historical_episode_ref`
- `current_case_ref`
- `mechanism_ref`
- `as_of`
- `dimensions`
- `blocking_mismatches`
- `unknowns`
- `overall_transferability`
- `evidence_refs`
- `version`

### 1.1 Five mandatory dimensions

Every assessment must evaluate:

#### A. Monetary Regime

Questions include:

- fixed vs floating FX;
- gold / commodity anchor vs fiat;
- QE / balance-sheet tools available or absent;
- capital controls / monetary sovereignty differences.

#### B. Fiscal Capacity

Questions include:

- debt structure and maturity;
- domestic vs external funding base;
- reserve-currency privilege;
- tax / spending flexibility;
- fiscal-monetary interaction.

#### C. Market Structure

Questions include:

- market depth and liquidity;
- leverage architecture;
- derivative-market importance;
- passive / systematic flow share;
- dealer / collateral plumbing.

#### D. Global Order

Questions include:

- trade regime;
- capital mobility;
- geopolitical bloc structure;
- reserve / settlement architecture;
- sanctions / external-balance constraints.

#### E. Policy Toolkit

Questions include:

- tools available to central bank / treasury / regulators;
- institutional constraints on use;
- historical precedents and credibility;
- lender / market-maker-of-last-resort capacity.

### 1.2 Dimension states

Each dimension must resolve to one of:

- `MATCHED`
- `PARTIAL`
- `MISMATCHED`
- `UNKNOWN`

No scalar score is required.

Each dimension must also identify:

- `mechanism_relevance`
- `evidence_refs`
- `why_it_matters`
- `blocking_if_mismatched`

### 1.3 Overall transferability

Allowed outcomes:

- `HIGH_TRANSFERABILITY`
- `PARTIAL_TRANSFERABILITY`
- `WEAK_TRANSFERABILITY`
- `NON_TRANSFERABLE`
- `UNRESOLVED`

Fail-closed decision rules:

- any `blocking_if_mismatched=true` dimension that is `MISMATCHED` → `NON_TRANSFERABLE`;
- no blocking mismatch but material partial differences → at most `PARTIAL_TRANSFERABILITY`;
- multiple `UNKNOWN` dimensions that affect the core mechanism → `UNRESOLVED` or `WEAK_TRANSFERABILITY`, never `HIGH_TRANSFERABILITY`;
- `HIGH_TRANSFERABILITY` requires no material mismatch and sufficient evidence on all mechanism-critical dimensions.

Historical similarity in asset returns, charts or narrative language cannot override a blocking structural mismatch.

---

## 2. Prior authority after transferability

Historical priors are not deleted when transferability is weak. Their authority is bounded.

Canonical mapping:

```text
HIGH_TRANSFERABILITY
→ historical prior may materially inform current research judgment

PARTIAL_TRANSFERABILITY
→ prior is usable with explicit caveats and reduced authority

WEAK_TRANSFERABILITY
→ prior may serve as analogy / stress reference only

NON_TRANSFERABLE
→ prior cannot support current mechanism authority

UNRESOLVED
→ system must preserve uncertainty and seek missing evidence
```

Invariant:

`HistoricalValidity != CurrentTransferability`

A historically valid Gold Episode may be non-transferable today without losing its historical Gold status.

---

## 3. PriorViolationRecord

Canonical question:

> Given a transferable prior and a PIT-frozen mechanism expectation, what would current reality have to do to violate that prior?

Required fields:

- `violation_id`
- `prior_ref`
- `hypothesis_set_ref`
- `as_of`
- `expected_observables`
- `observed_evidence_refs`
- `violation_type`
- `severity`
- `status`
- `posterior_effect`
- `breaker_effect`
- `resolution_notes`
- `version`

---

## 4. Surprise vs violation

H3 freezes an important distinction.

### Surprise

A fact is surprising if it was not strongly expected but does not directly contradict the mechanism.

Examples:

- timing earlier/later than expected within admissible horizon;
- one secondary sensor moves before the primary sensor;
- magnitude differs but sign and causal order remain compatible.

### Prior violation

A fact is a prior violation if it contradicts a **pre-committed diagnostic expectation** necessary for the mechanism.

Examples:

- expected term premium rise is persistently absent while fiscal-stress mechanism requires it;
- policy reaction goes opposite to the feasible-set assumption;
- the supposed leading market repeatedly fails to confirm and the null mechanism explains the move better;
- key structural demand expected to persist reverses before the mechanism horizon.

Invariant:

`Surprise != PriorViolation`

Not every unexpected fact should kill the prior, but a required-condition violation must reduce authority.

---

## 5. Violation taxonomy

H3 freezes six Genesis violation types.

### V1｜Sign Violation

Observed direction is opposite to a required expected sign.

### V2｜Sequence Violation

Pre-committed causal / cross-asset order fails materially.

### V3｜Magnitude Violation

Observed effect remains below / above a threshold required for the mechanism to be economically meaningful.

### V4｜Persistence Violation

A state expected to persist mean-reverts or disappears before the mechanism can plausibly operate.

### V5｜Policy-Reaction Violation

Actual policy response falls outside the pre-committed feasible reaction set or directly contradicts the assumed reaction function.

### V6｜Cross-Asset Confirmation Violation

The asset or market expected to independently confirm the mechanism does not confirm within the declared observation window, or confirms the competing/null hypothesis instead.

Additional types require a versioned extension of this spec rather than ad-hoc labels.

---

## 6. Severity and response

Allowed severity:

- `WATCH`
- `MATERIAL`
- `BREAKER`

Allowed research-state responses:

- `MAINTAIN_PRIOR`
- `DOWNGRADE_PRIOR`
- `REOPEN_MECHANISM_COMPETITION`
- `RETIRE_CURRENT_PRIOR_APPLICATION`
- `UNRESOLVED_NEEDS_EVIDENCE`

A prior violation may alter research authority; it does **not** directly authorize a trade action.

Forbidden mapping:

`PriorViolation → Sell`

Required architecture:

```text
PriorViolation
→ Posterior research-state update
→ Market Clock / Current Evidence
→ V / Xa / Xp / S
→ Portfolio OS authority if separately authorized
```

---

## 7. Prior Violation Engine logic

### 7.1 Preconditions

The engine may evaluate a violation only if:

1. the historical prior has an explicit transferability state;
2. H2 hypothesis expectations were PIT-frozen;
3. expected observables have a declared observation window;
4. current evidence is sourced and timestamped.

If these are missing:

`status = NOT_EVALUABLE`

### 7.2 Evaluation order

```text
Transferability check
        ↓
Hypothesis / diagnostic expectation check
        ↓
Current evidence intake
        ↓
Surprise classification
        ↓
Violation-type test
        ↓
Severity
        ↓
Posterior effect
        ↓
Reality Settlement later
```

### 7.3 Posterior effect

H3 does not require numeric Bayesian probabilities.

Allowed qualitative effects:

- `NO_CHANGE`
- `MODEST_DOWNGRADE`
- `MAJOR_DOWNGRADE`
- `PRIMARY_BREAK`
- `SHIFT_TO_ALTERNATIVE_REVIEW`
- `SHIFT_TO_NULL_REVIEW`

This preserves epistemic humility while making evidence updates explicit.

---

## 8. Prior Violation is a research trigger

A high-information event is often not a confirmation but a contradiction.

H3 therefore freezes:

> **Prior violation is a first-class research trigger.**

When current reality violates a strong, transferable prior, the system must open one of three investigations:

1. `MECHANISM_FAILURE` — the historical mechanism does not operate now;
2. `STRUCTURAL_REGIME_DIFFERENCE` — transferability was overstated;
3. `DOMINANT_COMPETING_MECHANISM` — an H2 alternative or null is stronger.

It must not automatically invent a fourth rescue story.

---

## 9. Worked example｜Fiscal stress and long yields

Illustrative only; not a current market conclusion.

Historical prior application:

```text
Fiscal capacity weakens
→ funding pressure / term premium rises
→ long yields rise
```

Transferability asks whether current monetary regime, fiscal funding base, market structure, global order and policy toolkit permit the old mechanism to operate comparably.

If transferability is `PARTIAL_TRANSFERABILITY`, the prior has bounded authority.

A possible prior violation would be:

```text
fiscal metrics continue to deteriorate
AND
term premium / long yields persistently decline
AND
independent funding-stress sensors fail to confirm
```

The engine should not immediately conclude `history is wrong`. It should trigger comparison among:

- growth / safe-haven alternative;
- central-bank reaction / financial repression alternative;
- null flow explanation;
- previously missed structural non-transferability.

---

## 10. Genesis hard negatives

H3 must fail closed against at least these cases:

1. Historical price chart looks similar, so transferability is marked high without institutional comparison → FAIL.
2. One blocking structural mismatch exists but overall transferability remains high → FAIL.
3. Several mechanism-critical dimensions are unknown but result is high transferability → FAIL.
4. Historical episode is downgraded from Gold solely because it is non-transferable today → FAIL.
5. Violation is evaluated without PIT-frozen expected observables → FAIL.
6. Every surprise is treated as a breaker → FAIL.
7. A required-condition contradiction is labeled harmless surprise to preserve the thesis → FAIL.
8. Prior violation directly generates a trade action → FAIL.
9. System invents a new mechanism after a violation without reopening H2 competition/versioning → FAIL.
10. Cross-asset non-confirmation is ignored after the declared observation window → FAIL.
11. Transferability is summarized as one opaque scalar without dimension evidence → FAIL.
12. System cannot return `NOT_EVALUABLE` or `UNRESOLVED` → FAIL.

---

## 11. Human Review Gate

H3 requires `10/10 PASS`:

1. Historical validity and current transferability are clearly separated.
2. Five structural transferability dimensions are mandatory.
3. Blocking mismatch rules fail closed.
4. Unknowns reduce authority rather than being silently imputed.
5. Surprise and prior violation are distinct.
6. Six violation types are explicit and testable in principle.
7. Expected observables must be PIT-frozen before violation evaluation.
8. Prior violation reopens research instead of directly trading.
9. H2 alternatives / null are integrated into violation resolution.
10. Reality Settlement remains the final authority.

## 12. Acceptance token

`ACCEPT_YMA55_H3_TRANSFERABILITY_PRIOR_VIOLATION_ENGINE`

Acceptance of H3 completes the written-spec package for YMA55-H1/H2/H3. It does not imply merge, runtime deployment, portfolio authority, trading authority, Canon promotion or historical-prior use in live capital decisions.
