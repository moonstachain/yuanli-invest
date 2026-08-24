# YMA55-H2｜Competing Mechanism & Null Hypothesis Contract — Design Spec

**Status:** `design_candidate_for_human_review`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Base:** `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
**Dependency:** YMA55-H1 written specification  
**Capital / trading authority:** none

## 0. Purpose

YMA55-H2 attacks the largest epistemic risk in macro historical reasoning:

> A sufficiently flexible narrative can explain almost any realized market outcome after the fact.

H2 therefore requires every material YMA55 macro judgment to be expressed as a **MechanismHypothesisSet** containing:

1. exactly one declared `PrimaryMechanismHypothesis`;
2. at least one and at most three `AlternativeMechanismHypothesis` objects;
3. exactly one `NullHypothesis`;
4. ex-ante discriminating observations;
5. symmetric evidence search and explicit falsifiers;
6. PIT version freeze before outcome knowledge.

The purpose is not to force false certainty. The purpose is to make disagreement inspectable and to allow `UNRESOLVED` to remain a valid outcome.

---

## 1. Contract object

Canonical object:

`MechanismHypothesisSet`

Required top-level fields:

- `hypothesis_set_id`
- `as_of`
- `research_target_or_question`
- `world_state_ref`
- `constraint_ref`
- `primary`
- `alternatives`
- `null`
- `discrimination_matrix`
- `evidence_search_budget`
- `resolution_state`
- `version`
- `supersedes`

No field in this object grants capital authority.

---

## 2. Primary mechanism hypothesis

Exactly one primary is required at PIT freeze.

Required fields:

- `hypothesis_id`
- `mechanism_family`
- `causal_chain`
- `required_conditions`
- `predicted_observables`
- `expected_sequence`
- `expected_horizon`
- `falsifiers`
- `breaker`
- `supporting_evidence_refs`
- `contradicting_evidence_refs`
- `support_state`

`support_state` uses qualitative bands only:

- `strong`
- `moderate`
- `weak`
- `contradicted`
- `unknown`

H2 prohibits faux precision such as `78.3% probability` unless separately justified by a statistically valid model with an explicit sample and calibration contract.

---

## 3. Alternative mechanisms

Each material judgment must carry `1..3` alternatives.

Alternative hypotheses are not rhetorical objections. They must be **mechanistically capable of explaining the same observed market fact**.

Each alternative uses the same minimum fields as the primary:

- mechanism family;
- causal chain;
- predicted observables;
- expected sequence;
- falsifiers;
- evidence for and against.

Symmetry rule:

> An alternative cannot be rejected merely because it is less narratively attractive. It must lose through evidence or discriminatory observations.

If no plausible alternative can be found, the record must state `alternative_search_exhausted=false` rather than fabricating one.

---

## 4. Null hypothesis

Exactly one null is mandatory.

The null asks:

> Can the observed price move be explained without the proposed structural macro mechanism?

Canonical null families include, where applicable:

- simple momentum / trend continuation;
- positioning squeeze / deleveraging;
- mechanical flow / rebalancing;
- idiosyncratic asset news;
- generic risk-on / risk-off beta;
- measurement noise / data revision;
- random path within normal historical variation.

The null should be simpler than the structural mechanism and must define what observation would make the structural explanation necessary rather than decorative.

Null is not synonymous with `nothing matters`; it is a disciplined simpler competing explanation.

---

## 5. Causal-chain complexity discipline

H2 freezes a narrative-complexity budget.

A mechanism chain should normally contain no more than six causal nodes between initiating constraint and expected payoff mechanism. Longer chains are allowed only with an explicit `complexity_exception` describing:

- why the extra nodes are causally necessary;
- which nodes are independently observable;
- which edge is most likely to fail.

Every chain must designate:

- `critical_edge`
- `weakest_edge`
- `first_observable_confirmation`
- `first_observable_disconfirmation`

This reduces the ability to rescue a thesis by endlessly adding intermediate stories after the fact.

---

## 6. Mechanism Discrimination Matrix

Every hypothesis set must pre-commit to observations that help distinguish hypotheses.

Required dimensions:

- observable / sensor;
- primary expected sign/state;
- alternative expected sign/state;
- null expected sign/state;
- expected ordering / lead-lag where applicable;
- maximum admissible observation window;
- evidence source.

Example structure:

| Observable | Primary | Alternative | Null | Discriminating meaning |
|---|---|---|---|---|
| Long-end term premium | rises | flat/down | no stable view | distinguishes fiscal-duration stress |
| Real yield | mixed | falls materially | no stable view | supports opportunity-cost mechanism |
| Central-bank gold buying | persists | irrelevant | irrelevant | supports reserve-diversification channel |
| Positioning | not sufficient alone | not sufficient alone | extreme | supports squeeze/null |

The matrix must be frozen at T0. Outcome-aware edits create a new version and cannot overwrite the original.

---

## 7. Evidence symmetry contract

`evidence_search_budget` must declare a minimum search policy before resolution.

Default:

- one primary-source search lane for the primary;
- one independent counter-evidence lane for the primary;
- one evidence lane per alternative;
- one lane testing the null / simple benchmark.

The research process must actively seek evidence that would reduce support for the primary.

Invariant:

`FalsifierBeforeConviction = true`

and:

`ClaimAuthority <= EvidenceAuthority`

---

## 8. Resolution states

H2 freezes the following epistemic resolution states:

- `PRIMARY_BEST_SUPPORTED`
- `ALTERNATIVE_BEST_SUPPORTED`
- `NULL_BEST_SUPPORTED`
- `MULTIPLE_MECHANISMS_PLAUSIBLE`
- `PRIMARY_CONTRADICTED`
- `UNRESOLVED`

Resolution is **not** based only on price direction.

For example:

- price rises and primary mechanism is confirmed → may be `PRIMARY_BEST_SUPPORTED`;
- price rises but evidence supports the null squeeze → `NULL_BEST_SUPPORTED`;
- price rises while primary is contradicted and alternative is confirmed → `ALTERNATIVE_BEST_SUPPORTED`;
- price rises but no mechanism can be discriminated → `UNRESOLVED`.

---

## 9. Version and no-retrofit law

Once a hypothesis set is PIT-frozen:

- changing the primary mechanism requires a new version;
- adding an alternative after material outcome knowledge requires a new version marked `post_outcome_added=true`;
- deleting a failed falsifier is prohibited;
- reclassifying the same thesis from R to C/X without closure is prohibited under `NO_SILENT_THESIS_MIGRATION`.

Canonical lineage:

```text
MHS-v1 @ T0
  ↓ evidence update
MHS-v2 @ T1
  ↓ settlement
RealitySettlement
```

The historical v1 remains immutable ledger evidence.

---

## 10. Gold-case worked example｜Gold under fiscal stress

This is a contract demonstration only, not a current investment conclusion.

### Primary

`Fiscal / Relative-Sovereignty Repricing`

Illustrative chain:

```text
Fiscal capacity deteriorates
→ funding / term-premium pressure rises
→ confidence in long-run monetary/fiscal discipline weakens
→ reserve / store-of-value demand shifts
→ gold reprices
```

### Alternative A

`Real-rate opportunity-cost mechanism`

```text
Growth / policy path weakens
→ real yields decline
→ opportunity cost of non-yielding gold falls
→ gold reprices
```

### Alternative B

`Geopolitical reserve diversification`

```text
Sanctions / reserve-asset risk rises
→ official reserve diversification increases
→ structural central-bank demand rises
→ gold reprices
```

### Null

`Positioning / momentum squeeze`

```text
trend + crowded short / CTA / flow mechanics
→ price acceleration
```

The test is not `which story sounds most macro`. The test is which mechanism best predicts the sequence of independently observable evidence.

---

## 11. Genesis hard negatives

H2 must fail closed against at least these cases:

1. Primary exists but no alternative exists → FAIL.
2. Primary + alternatives exist but no null exists → FAIL.
3. Null is a strawman that cannot plausibly explain the observed fact → FAIL.
4. Alternatives have no evidence search lane → FAIL.
5. Primary receives materially more evidence budget without justification → FAIL.
6. Primary has no falsifier → FAIL.
7. Discrimination matrix is created after outcome knowledge → FAIL.
8. Price direction alone selects the winning mechanism → FAIL.
9. Failed primary is renamed after the fact without versioning → FAIL.
10. A profitable wrong-mechanism thesis is scored as epistemic success → FAIL.
11. Hypothesis chain expands indefinitely after every contrary fact → FAIL unless a new version is created and complexity exception is explicit.
12. System cannot return `UNRESOLVED` → FAIL.

---

## 12. Human Review Gate

H2 requires `10/10 PASS`:

1. Exactly one primary is PIT-frozen.
2. At least one genuine alternative exists.
3. Exactly one meaningful null exists.
4. Primary / alternative / null are observationally discriminable in principle.
5. Evidence search is symmetric enough to challenge conviction.
6. Falsifiers and breaker are declared before resolution.
7. Complexity budget prevents endless narrative rescue.
8. Resolution can select alternative, null or unresolved.
9. Wrong-mechanism lucky outcomes are not rewarded.
10. No capital/trading authority is created.

## 13. Acceptance token

`ACCEPT_YMA55_H2_COMPETING_MECHANISM_NULL_HYPOTHESIS_CONTRACT`

Acceptance of H2 authorizes H3 specification review only. It does not imply merge, runtime deployment, portfolio authority or trading authority.
