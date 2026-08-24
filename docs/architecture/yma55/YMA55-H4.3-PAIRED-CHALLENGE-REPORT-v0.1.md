# YMA55-H4.3｜H3 Transferability & Prior-Violation Paired Challenge — Machine Settlement Report

**Status:** `machine_qualified_paired_transfer_challenge_candidate`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yma55-h1-h3-causal-prior-hardening`  
**Human acceptance:** pending  
**Capital / trading / merge authority:** none

## 1. Question settled

H4.3 tests one narrow epistemic question:

> When a historically valid mechanism is transported into a structurally different target world, can H3 first decide whether the prior has authority to transfer, and then detect whether an otherwise admissible prior is violated by forward target evidence?

This is not a return-forecasting experiment. It is a test of historical-prior authority control.

The experiment is historical-to-historical. Each target episode is treated as a pseudo-current world with a strict PIT cutoff, so H3 can be isolated from Market Clock, valuation, portfolio construction and live execution.

## 2. Experimental freeze

Six opaque paired challenges were pre-registered. The runner sees only `TP-01` through `TP-06`; actual source/target identities and challenge roles live in the sealed mapping.

The information order is frozen as:

```text
source mechanism settlement
→ source-prior eligibility
→ target T0 structural evidence
→ transferability freeze
→ target forward observation stream
→ prior-violation settlement
→ post-resolution unblinding
```

Structural comparison evidence in H4.3 is explicitly `CANDIDATE_DERIVED_FROM_H4_H41`. It is not Historical Gold evidence and does not claim independent primary-evidence authority.

## 3. Three variants

### T0｜Unconditional Transport

A historically eligible source prior is transported into every target without structural transferability gating and without forward prior-violation evaluation.

### T1｜Transferability Gate Only

Only `HIGH_TRANSFERABILITY` and `PARTIAL_TRANSFERABILITY` receive active research-prior authority. `WEAK_TRANSFERABILITY`, `NON_TRANSFERABLE` and `UNRESOLVED` are fail-closed.

T1 does not inspect forward target observations.

### T2｜Full H3

T2 uses the same transferability gate as T1. Only after an active prior has earned transfer authority does the runner consume the forward target observation stream and evaluate prior violations.

Therefore:

`HistoricalValidity != Transferability != CurrentValidity`.

## 4. Machine result matrix

The dedicated H4.3 validator on repository-gates run #507 produced:

| Metric | T0 Unconditional | T1 Transferability Gate | T2 Full H3 |
| --- | ---: | ---: | ---: |
| unsafe prior applications | 3 | 0 | 0 |
| correct structural blocks | 0 | 3 | 3 |
| eligible prior maintains | 1 | 1 | 1 |
| eligible prior violations detected | 0 | 0 | 2 |
| eligible prior violations missed | 2 | 2 | 0 |
| false breakers | 0 | 0 | 0 |
| weak-prior active authority leaks | 1 | 0 | 0 |
| source-prior laundering events | 0 | 0 | 0 |
| capital-authority events | 0 | 0 | 0 |

The full unit suite passed with 190 tests.

## 5. What T0 → T1 establishes

The transferability gate removed all three unsafe historical-prior applications in the constructed pair set:

`unsafe_prior_applications: 3 → 0`

while increasing correctly blocked structurally inadmissible priors:

`correct_structural_blocks: 0 → 3`.

It also closed the specific implementation gap where `WEAK_TRANSFERABILITY` could otherwise be treated like an active prior:

`weak_prior_active_authority_leaks: 1 → 0`.

Narrow settlement:

> H3 structural transferability gating is supported as an epistemic-authority control within this constructed challenge set.

This does not prove population accuracy or current-world forecasting superiority.

## 6. What T1 → T2 establishes

T1 correctly decides which priors may speak, but it cannot know when an admissible prior later stops matching reality.

The two pre-registered active-but-violated priors therefore remain missed under T1:

`eligible_prior_violations_missed = 2`.

After forward evidence is opened under T2:

`eligible_prior_violations_detected: 0 → 2`

and

`eligible_prior_violations_missed: 2 → 0`.

No compatible prior is falsely broken:

`false_breakers = 0`.

Narrow settlement:

> Prior-Violation logic adds information beyond structural transferability gating within the constructed paired challenge set.

## 7. The three machine disciplines are now behaviorally represented

### Discipline 1｜No evidence, permission to abstain

> **没有证据，可以不知道。**

This discipline was demonstrated upstream in H4.1 by the 1971 Gold evidence abstention and remains a required authority boundary.

Machine meaning:

`Evidence not sufficient → INSUFFICIENT_EVIDENCE / no forced resolution`.

### Discipline 2｜A preferred explanation must be allowed to lose

> **有喜欢的解释，也必须允许它输。**

H4.2 showed that the dominant measured increment came from explicit mechanism competition rather than more supporting evidence. Alternative / Null hypotheses can defeat Primary.

Machine meaning:

`Primary is a contestant, not an authority`.

### Discipline 3｜Historical truth does not grant current authority

> **历史上是对的，也不代表今天有资格说话。**

H4.3 now operationalizes two separate gates:

`historically valid prior → transferability gate → bounded authority`

and, only if authority is earned:

`bounded authority → forward evidence → prior violation / maintain / reopen`.

Machine meaning:

`HistoricalValidity != Transferability != CurrentValidity`.

## 8. What H4.3 does not establish

H4.3 does not establish:

- 2026 live-world validity;
- out-of-sample return forecasting superiority;
- population-level accuracy;
- exact superiority over the pre-H1/H2/H3 YMA55 implementation;
- independent primary-evidence qualification for the five structural transferability dimensions;
- Historical Gold admission;
- Canon promotion;
- Portfolio, sizing, signal, trading or live-execution authority.

The six pairs are a constructed diagnostic challenge set, not an IID sample.

## 9. Kernel closure settlement

Taken together, H1/H2/H3 now have distinct operational jobs:

- **H1 — Compress Reality:** stabilize the causal object language.
- **H2 — Compete Explanations:** prevent preferred-story monopoly.
- **H3 — Control Transfer:** prevent historical truth from automatically becoming current authority and revoke an admissible prior when reality violates it.
- **Evidence Gate — Earn the Right to Know:** preserve abstention.
- **Reality Settlement — Final Authority:** preserve wrong-mechanism and lucky-outcome distinctions.

The resulting epistemic kernel is:

```text
Evidence
→ Causal Compression
→ Competing Mechanisms
→ Transferability
→ Prior Violation
→ Reality Settlement
```

## 10. Strategic recommendation after Human Acceptance

If H4.3 receives 24/24 Human Review and explicit acceptance, YMA55 2.1 should stop theory expansion.

There should be no default `H4.4` theory battle.

The next program should be a clean second-stage line:

```text
Evidence Hardening
→ Shadow Runtime
→ Reality Settlement
```

The purpose changes from **inventing the epistemic kernel** to **feeding it higher-authority evidence, exposing it to a current-world shadow stream, and allowing reality to repeatedly settle it**.

Any future theory change should require a demonstrated failure mode from Evidence / Shadow / Reality, not a desire to make the framework more elegant.

## 11. Current authority boundary

H4.3 remains a machine-qualified candidate pending Human Review.

It grants no:

- Historical Gold admission;
- Constitution or Engine Registry mutation;
- Canon promotion;
- Portfolio authority;
- position sizing;
- trade signal authority;
- live execution;
- merge authority;
- Phase 2 execution authority.

Recommended Human Acceptance token, only after 24/24 review:

`ACCEPT_YMA55_H4_3_TRANSFERABILITY_PRIOR_VIOLATION_PAIRED_CHALLENGE`
