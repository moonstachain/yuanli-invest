# YMA55-H4.1A｜Two-Clock Blind Replay Amendment v0.1

**Status:** `binding_amendment_before_fixture_hydration`  
**Date:** 2026-08-24  
**Parent:** `YMA55-H4.1｜Primary Evidence Hydration & Blind Replay Qualification`

## 0｜Why this amendment exists

A historical replay has two epistemically different clocks:

1. what was knowable when the hypothesis was formed; and
2. what became observable later while the hypothesis was still being tested.

Requiring all blind-resolver evidence to be public by the original T0 `evidence_cutoff` makes future predicted observables impossible to evaluate without silently smuggling future information into T0. That would defeat the purpose of replay.

Therefore H4.1 is amended to separate **T0 formation evidence** from a **forward PIT observation stream**.

---

## 1｜Clock A — T0 Hypothesis Freeze

`T0 = as_of / evidence_cutoff`

Only evidence public by T0 may:

- define World / Constraint / Transmission;
- support Primary / Alternative / Null formation;
- establish required conditions already observable at T0;
- determine initial transferability state.

T0 evidence admission remains:

`T0Evidence = E0 ∪ E1 ∪ admissible(E2), published_at <= evidence_cutoff`

No later observation may be written back into the T0 hypothesis packet.

---

## 2｜Clock B — Blind Resolver Cutoff

Every replay candidate must pre-register a second timestamp:

`resolver_cutoff > evidence_cutoff`

The blind resolver may observe evidence that became public after T0 but no later than `resolver_cutoff`, provided that:

- it is E0/E1/admissible E2;
- its `published_at` / `known_at` is preserved;
- it is placed in `observation_stream`, never in `t0_evidence`;
- it contains no settlement, case role, intended answer or retrospective E3/E4 narrative;
- the resolver cutoff is frozen before looking at the sealed settlement.

Thus:

`BlindResolverInput = FrozenT0 + T0Evidence + PITObservationStream(T0, ResolverCutoff]`

not:

`FrozenT0 + FutureSettlementKnowledge`.

---

## 3｜Observation Stream Contract

Every observation record must bind:

- `observation_id`
- `source_id`
- `observable`
- `state`
- `known_at`
- `evidence_tier`
- `derivation` (`direct` or `pit_derived`)
- `supports_or_contradicts` where pre-registered

Fail closed:

1. `known_at <= evidence_cutoff` ⇒ it belongs to T0 evidence, not the forward stream.
2. `known_at > resolver_cutoff` ⇒ resolver leakage; reject.
3. E3/E4 ⇒ reject from resolver even if published before resolver cutoff.
4. A later revision cannot overwrite the vintage first known during the replay window.
5. The observation stream is append-only in chronological order.

---

## 4｜Resolver Cutoff Selection

The cutoff must be chosen without reading the sealed outcome label.

Default reference rule for H4.1 Genesis cases:

- choose the earliest deterministic horizon boundary that is compatible with the frozen hypothesis set and permits at least one decisive observable to become measurable;
- cap the horizon at the shortest relevant upper bound among the competing hypotheses where practical;
- record the rule and timestamp in the sealed-free blind manifest before resolution.

The purpose is not to optimize hit rate. The purpose is to prevent arbitrary waiting until the preferred mechanism wins.

---

## 5｜Three Separate Objects

H4.1 now requires three physically distinct data layers:

### A. `t0_evidence`
Evidence available by original hypothesis cutoff.

### B. `observation_stream`
Later PIT observations available by the pre-registered resolver cutoff.

### C. `sealed_settlement`
Outcome / intended role / final historical adjudication, unavailable until blind result is hash-frozen.

Invariant:

`T0Evidence != ObservationStream != Settlement`

and:

`ObservationStream cannot mutate FrozenT0`.

---

## 6｜Blindness Grade Is Unchanged

This working session remains at most:

`B_PIPELINE_BLIND`

because the broader research context already knows the selected historical episodes and candidate roles.

The two-clock amendment improves outcome-data isolation but does not convert the current work into A-grade independent replication.

---

## 7｜Authority Freeze

The amendment creates no:

- Historical Gold admission;
- Canon promotion;
- Engine Registry authority;
- Portfolio / sizing authority;
- trading / execution authority;
- merge authority.

`Replay Qualification != Historical Gold Admission != Capital Admission` remains binding.
