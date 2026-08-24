# YMA55-H4.3｜H3 Transferability & Prior-Violation Paired Challenge — Design Spec

**Status:** `execution_authorized_design_freeze_candidate`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yma55-h1-h3-causal-prior-hardening`  
**Parent:** YMA55-H4.2 Human Accepted  
**Dependencies:** H1/H2/H3 accepted specs + H4.1 blind replay + H4.2 same-case benchmark  
**Capital / trading / merge authority:** none

## 0. Purpose

H4.2 established that H3 cannot be measured inside a historical-only same-case mechanism replay. H4.3 therefore changes the experimental object from **case classification** to **prior transport**.

Canonical question:

> When a historically valid mechanism is transported from a source regime into a different target regime, can H3 (a) prevent structurally non-transferable priors from gaining current authority and (b) detect when an otherwise transferable prior is violated by target-world evidence?

The experiment is deliberately historical-to-historical. A historical target is treated as a pseudo-current world with a strict PIT cutoff. This isolates H3 from Market Clock, valuation, 2026 live data, portfolio construction and execution.

H4.3 does not test return forecasting. It tests **epistemic authority control**.

---

## 1. Experimental architecture

Each challenge pair has four clocks/locks:

```text
SOURCE SETTLEMENT LOCK
        ↓
SOURCE PRIOR ELIGIBILITY
        ↓
TARGET T0 STRUCTURAL EVIDENCE
        ↓
TRANSFERABILITY FREEZE
        ↓
TARGET FORWARD OBSERVATION STREAM
        ↓
PRIOR-VIOLATION FREEZE
        ↓
POST-RESOLUTION UNBLINDING / SETTLEMENT
```

The target forward observation stream must never be visible when transferability is frozen.

The experiment reuses already hydrated H4.1 target evidence wherever possible. H4.3 may derive structural-comparison candidate evidence from the frozen H4/H4.1 episode records, but such derived structural evidence remains `candidate_derived`, not Historical Gold evidence.

Invariant:

`HistoricalValidity != Transferability != PriorViolation != CapitalAuthority`

---

## 2. Source-prior eligibility

Only a source mechanism that passed H4.1 mechanism settlement may become an active source prior for this experiment.

Eligible source mechanisms:

- `D1982-P` — 1982 UST disinflation / duration primary;
- `CR2009-P` — 2009 policy-backstop / funding-stabilization credit primary;
- `CR2006-P` — 2006 credit-deterioration primary, mechanism right even though expression timing/strike failed.

Explicitly ineligible as active source priors in H4.3:

- 1971 Gold positive-pattern case because H4.1 preserved an evidence abstention;
- 2020 Gold scarcity primary because H4.1 settlement preserved a mechanism mismatch;
- any source mechanism whose historical mechanism settlement did not support that mechanism.

H4.3 must not launder an unqualified historical source into a transferable current prior.

---

## 3. Six pre-registered paired challenges

The six real pairs are chosen to separate three different H3 jobs: valid transfer, violated transfer, and blocked transfer.

| Pair | Source prior | Target world | Pre-registered challenge role | Required H3 behavior |
| --- | --- | --- | --- | --- |
| TP-01 | 2009 credit backstop | 2020 credit dislocation | transferable / compatible | allow bounded prior authority; no false violation |
| TP-02 | 1982 duration disinflation | 1994 tightening | transferable / violated | allow bounded authority, then detect violation and reopen competition |
| TP-03 | 1982 duration disinflation | 2020 zero-bound duration | structurally non-transferable | block active prior application before target outcome |
| TP-04 | 2006 systemic credit deterioration | 2015 energy credit stress | partially transferable / violated | allow bounded authority, then detect failed systemic confirmation |
| TP-05 | 2006 credit deterioration | 2020 pandemic credit | structurally non-transferable | block active prior application because policy toolkit / regime structure changes the mechanism authority |
| TP-06 | 2009 systemic credit backstop | 2015 sector credit stress | weak transferability | stress-reference only; no active prior application |

The pair labels and expected H3 settlements belong only in a sealed mapping / settlement artifact. Runtime packets use opaque IDs.

The six pairs are a constructed diagnostic challenge set, not an IID sample and not a population estimate.

---

## 4. Transferability resolver freeze

H4.3 operationalizes H3's five mandatory dimensions without a scalar score:

- monetary_regime
- fiscal_capacity
- market_structure
- global_order
- policy_toolkit

Allowed dimension states remain:

- `MATCHED`
- `PARTIAL`
- `MISMATCHED`
- `UNKNOWN`

Deterministic overall resolver for this experiment:

1. Any `blocking_if_mismatched=true` + `MISMATCHED` → `NON_TRANSFERABLE`.
2. Any mechanism-critical `UNKNOWN` → `UNRESOLVED` unless a stronger blocking mismatch already forces `NON_TRANSFERABLE`.
3. No blocker, but two or more material non-blocking `MISMATCHED` dimensions, or three or more material `PARTIAL` dimensions → `WEAK_TRANSFERABILITY`.
4. No blocker/critical unknown, but at least one material `PARTIAL` or non-blocking `MISMATCHED` dimension → `PARTIAL_TRANSFERABILITY`.
5. All mechanism-critical dimensions `MATCHED`, with no material mismatch → `HIGH_TRANSFERABILITY`.

This is a closed qualitative resolver. No weighted transferability score is allowed.

### Active-authority mapping

- `HIGH_TRANSFERABILITY` → active historical prior application allowed for research.
- `PARTIAL_TRANSFERABILITY` → bounded active application allowed with explicit reduced authority.
- `WEAK_TRANSFERABILITY` → analogy / stress reference only; **not** active prior application.
- `NON_TRANSFERABLE` → active prior application prohibited.
- `UNRESOLVED` → active prior application prohibited pending evidence.

H4.3 therefore hardens an implementation gap exposed by H4.2: `WEAK_TRANSFERABILITY` must not be treated like an active transferable prior.

---

## 5. Transported diagnostic contract

A source hypothesis is never silently rewritten.

Each pair creates a separate, versioned `TransportedDiagnosticContract` containing:

- `transport_id`
- `opaque_pair_id`
- `source_prior_ref`
- `source_mechanism_family`
- `target_case_ref_opaque`
- `as_of`
- `target_required_conditions`
- `target_expected_observables`
- `target_expected_sequence`
- `target_feasible_policy_set`
- `observation_window_end`
- `lineage_notes`
- `pit_frozen=true`
- `version`

The transported diagnostics may use target-native sensors only when the mapping is frozen before the forward observation stream. The original source hypothesis remains immutable.

Forbidden:

`source hypothesis mutation after seeing target evidence`

---

## 6. Target evidence firewall

Each blind pair packet contains two separate target evidence blocks:

### A. `structural_evidence_at_t0`

Visible to transferability resolver. Contains only evidence available at target T0 and the five-dimension comparison state.

### B. `forward_observation_stream`

Hidden until transferability has been frozen. Contains target observations used by the prior-violation engine.

Post-resolution settlement and source/target identities remain outside the blind runner packet.

H4.3 must verify that no target forward observation, target settlement or expected H3 answer appears inside the transferability-freeze payload.

---

## 7. Three H3 ablation variants

H4.3 compares three same-pair variants:

### T0｜Unconditional Transport Baseline

- historically eligible source prior is applied to every target;
- ignores transferability;
- does not run a prior-violation engine;
- cannot claim to reproduce old YMA55 exactly.

Purpose: expose analogy overreach / unsafe transport.

### T1｜Transferability Gate Only

- applies prior only for HIGH/PARTIAL;
- blocks WEAK/NON_TRANSFERABLE/UNRESOLVED;
- does not evaluate forward prior violations;
- therefore can still remain loyal to an eligible but target-violated prior.

Purpose: isolate structural gating value.

### T2｜Full H3

- applies the same transferability gate as T1;
- then evaluates target forward observations for sign, sequence, magnitude, persistence, policy-reaction and cross-asset-confirmation violations;
- can maintain, downgrade, reopen mechanism competition or retire the current prior application.

Purpose: isolate the additional value of prior-violation logic.

---

## 8. Settlement states and scoring

The experiment does not produce a single win rate or probability.

Per pair, settlement has two axes:

### Axis A｜Authority settlement

- `ACTIVE_PRIOR_ALLOWED`
- `ACTIVE_PRIOR_BLOCKED`
- `UNRESOLVED_NEEDS_EVIDENCE`

### Axis B｜If active, observation settlement

- `MAINTAIN_PRIOR`
- `DOWNGRADE_PRIOR`
- `REOPEN_MECHANISM_COMPETITION`
- `RETIRE_CURRENT_PRIOR_APPLICATION`
- `NOT_APPLICABLE`

Aggregate machine metrics:

- `unsafe_prior_applications`
- `correct_structural_blocks`
- `eligible_prior_maintains`
- `eligible_prior_violations_detected`
- `eligible_prior_violations_missed`
- `false_breakers`
- `weak_prior_active_authority_leaks`
- `source_prior_laundering_events`
- `capital_authority_events`

Counts are reported directly. No pseudo-precise probability is emitted.

---

## 9. Expected scientific interpretation

H4.3 may support only the following narrow claims if the machine results warrant them:

- H3 structural gating reduces unsafe historical-prior transport in the constructed paired challenge set.
- Prior-violation logic adds information beyond transferability gating when a structurally admissible prior is contradicted by target evidence.
- WEAK/NON_TRANSFERABLE/UNRESOLVED states can successfully preserve uncertainty or block authority.

H4.3 must **not** claim:

- out-of-sample return forecasting superiority;
- statistical population accuracy;
- 2026 current-world validity;
- exact superiority over pre-H1/H2/H3 YMA55;
- Historical Gold admission;
- Canon promotion;
- Portfolio/sizing/signal/trading authority.

---

## 10. Hard negatives / fail-closed cases

At minimum the test suite must reject or safely handle:

1. A blocking mismatch with overall transferability still HIGH/PARTIAL.
2. A critical UNKNOWN with active prior authority.
3. WEAK_TRANSFERABILITY allowed to run as an active prior.
4. Target forward evidence visible before transferability freeze.
5. Target settlement visible before violation freeze.
6. Source episode identity or role encoded in opaque runtime pair ID.
7. A target diagnostic contract created after observation-window evidence is known.
8. Source hypothesis mutated instead of creating a transported diagnostic contract.
9. A surprise-only event promoted to BREAKER.
10. A required sign/sequence/policy contradiction treated as harmless confirmation.
11. A non-transferable prior downgraded into a trade action.
12. An H4.1 evidence-abstention source laundered into an H4.3 active prior.
13. A historically wrong-mechanism source used as authoritative source prior.
14. Any capital, sizing, signal or execution field emitted by the challenge runner.
15. A scalar transferability score used to override dimension-level blockers.

---

## 11. TDD / CI gates

Implementation order:

1. Human acceptance receipt for H4.2.
2. H4.3 contract tests RED.
3. Transferability resolver + WEAK fail-closed behavior GREEN.
4. Transported diagnostic contract + evidence firewall RED/GREEN.
5. Six opaque paired fixtures + sealed mapping.
6. Same-pair T0/T1/T2 runner.
7. Dedicated H4.3 validator.
8. Full repository unit suite.
9. State/report/review card.
10. Final exact-head repository-gates verification.

No machine-qualified claim is valid until the exact final head passes governance + contracts + dedicated H4.3 validator + full unit suite.

---

## 12. Human Review Gate

H4.3 Human Acceptance requires **24/24 PASS** across four blocks:

- 6 experimental-integrity checks;
- 6 transferability-authority checks;
- 6 prior-violation / causal-attribution checks;
- 6 governance / non-overclaiming checks.

Acceptance token if and only if all checks pass:

`ACCEPT_YMA55_H4_3_TRANSFERABILITY_PRIOR_VIOLATION_PAIRED_CHALLENGE`

Acceptance does not authorize merge, Historical Gold, Canon, Portfolio, sizing, signals, trading, or any successor battle.

---

## 13. Stop condition

H4.3 stops at:

`machine_qualified_paired_transfer_challenge_candidate`

The PR remains Draft and unmerged. Human review is required before any successor battle.
