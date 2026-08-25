# YMA55-H4.1｜Primary Evidence Hydration & Blind Replay Qualification v0.1

**Status:** `implementation_authorized_candidate`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yma55-h1-h3-causal-prior-hardening`  
**Prerequisite:** `ACCEPT_YMA55_H4_REFERENCE_IMPLEMENTATION_REPLAY_CANDIDATE`  
**Capital / trading authority:** none

## 0｜Purpose

H4 proved that H1/H2/H3 can be represented as an executable reference runtime and that settlement can be physically isolated from T0 research state. H4.1 tests a harder proposition:

> Can the same mechanism competition be resolved using only evidence that was actually public at the historical cutoff, without outcome leakage, retrospective narrative or case-role labels?

H4.1 therefore adds two independent gates:

1. **Primary Evidence Hydration** — replace placeholder evidence refs with timestamped, provenance-bound historical evidence.
2. **Blind Replay Qualification** — resolve Primary / Alternative / Null from a sanitized T0 packet before the sealed settlement and intended case role are revealed.

H4.1 is a research qualification layer. It does not admit Historical Gold, mutate Canon, authorize Portfolio or create trading signals.

---

## 1｜Authority Freeze

H4.1 MAY:

- create evidence-source and evidence-signal records;
- reject evidence that was not public by the T0 cutoff;
- construct sanitized blind packets;
- run deterministic hypothesis discrimination;
- preserve `UNRESOLVED`;
- produce replay-qualification proposals after reveal;
- identify candidates that deserve later Gold / Hard-Negative review.

H4.1 MUST NOT:

- mutate H4's original 12 replay fixtures to hide provenance mistakes;
- relabel a candidate as Historical Gold merely because the blind resolver agrees with settlement;
- use E3/E4 retrospective material in the blind resolver;
- expose case type, settlement, intended answer or outcome-bearing identifiers to the resolver;
- convert replay qualification into Portfolio, sizing, buy/sell/hold, trading or execution authority;
- authorize merge.

Invariant:

`Replay Qualification != Historical Gold Admission != Capital Admission`

---

## 2｜Evidence Tier Contract

### E0｜Contemporaneous Primary

A document, release, dataset or statement produced by the actor / institution that directly generated the relevant policy, balance-sheet, market or economic fact, and public no later than `evidence_cutoff`.

Examples: FOMC statement, Treasury announcement, EIA monthly report, FDIC banking data, official price/yield series.

### E1｜Contemporaneous Independent

A contemporaneous source from an independent producer that is public by cutoff and can corroborate or contradict the same mechanism without inheriting the E0 producer's institutional narrative.

### E2｜PIT-Derived

A derived signal computed only from observations available by the cutoff. E2 can summarize E0/E1 but cannot rescue missing E0 evidence.

### E3｜Later Authoritative Reconstruction

Later official histories, transcripts released after the cutoff, retrospective statistical revisions, later central-bank studies or official reconstructions. E3 is useful for settlement audit but is **inadmissible to the blind T0 resolver**.

### E4｜Retrospective Narrative

Later journalism, books, research essays, memoirs or narrative reconstructions. E4 may help human interpretation after reveal but is **inadmissible to the blind T0 resolver**.

The resolver admission set is strictly:

`ResolverEvidence = E0 ∪ E1 ∪ admissible(E2)`

and never E3/E4.

---

## 3｜Publication-Lag & PIT Admission

Every evidence record must bind:

- `source_id`
- `title`
- `publisher`
- `canonical_url`
- `document_date`
- `published_at`
- `retrieved_at`
- `evidence_tier`
- `producer_class`
- `public_at_t0`
- `admissible_at_cutoff`
- `provenance_note`
- `claims`
- `signals`

Fail closed rules:

1. `published_at > evidence_cutoff` ⇒ inadmissible.
2. `public_at_t0 = false` ⇒ inadmissible even if the underlying meeting/event occurred before cutoff.
3. Unknown publication time ⇒ cannot count as required E0/E1 coverage until resolved.
4. A later-released transcript of an earlier meeting is E3, not E0.
5. A revised data vintage cannot silently replace the vintage available at T0.

This contract treats publication lag as part of historical truth, not metadata decoration.

---

## 4｜Hydration Minimum

Each of the 12 H4 candidates must have, at minimum:

- at least one admissible E0 source supporting or contradicting a decisive mechanism observable;
- at least one admissible E1 source from an independent producer class, OR a documented `E1_UNAVAILABLE` state with explicit reason;
- explicit evidence for at least one discriminator between Primary and Alternative;
- explicit evidence status for Null where observable;
- no unresolved placeholder `needs_primary_hydration` refs inside the H4.1 evidence packet.

Qualification states:

- `EVIDENCE_HYDRATED`
- `PARTIAL_HYDRATION`
- `INSUFFICIENT_EVIDENCE`
- `PIT_LEAKAGE_REJECTED`

Only `EVIDENCE_HYDRATED` can proceed to a normal blind discrimination result. Partial/insufficient cases must remain unresolved or explicitly degraded.

---

## 5｜Evidence Independence

Evidence independence is about producer and causal information, not merely URL count.

Two records are not independent merely because they are hosted on different pages if they reproduce the same originating release.

The evidence packet therefore records `producer_class` and `originating_source_id`. H4.1 rejects fake independence where E1 is only a republication of E0.

---

## 6｜Blind Packet Firewall

The blind resolver MUST NOT receive:

- `case_type`
- `settlement`
- `outcome_class`
- intended Gold / Near-Miss / Wrong-Mechanism / Wrong-Strike role
- file path containing role labels
- the original `episode_id` if it embeds role information such as `GOLD`, `NEAR`, `WM`, `WS`
- post-cutoff evidence
- E3/E4 evidence

Instead each case receives an opaque `blind_case_id` such as `H41-B01`.

Two physically separate artifacts are required:

1. `blind_manifest.json` — resolver-visible opaque cases only.
2. `sealed_mapping.json` — maps opaque IDs to original episode IDs and case roles; it is used only after blind resolution is frozen.

Invariant:

`BlindInput ∩ SealedOutcomeFields = ∅`

---

## 7｜Blindness Grades

H4.1 explicitly distinguishes algorithmic blindness from human procedural blindness.

- `A_INDEPENDENT_BLIND` — evidence authoring and resolution performed by a resolver with no access to intended role / settlement.
- `B_PIPELINE_BLIND` — runtime packet is mechanically outcome-blind, but the surrounding research process may have prior knowledge of the historical episode or intended role.
- `C_NOT_BLIND` — resolver input contains outcome/role leakage or post-cutoff evidence.

This implementation session can at most claim `B_PIPELINE_BLIND`, because the candidate roles and historical settlements are already known in the working context. H4.1 MUST NOT misrepresent B-grade qualification as an independent blind replication.

A future fresh resolver can rerun the frozen blind pack for A-grade replication without changing evidence records.

---

## 8｜Deterministic Discrimination Contract

For each admitted signal, the resolver compares the observed state against each hypothesis's frozen:

- required conditions;
- predicted observables;
- expected sequence where observable at T0;
- falsifiers;
- breaker.

The reference resolver emits, per hypothesis:

- `support_count`
- `contradiction_count`
- `unknown_count`
- `falsifier_triggered`
- `breaker_triggered`
- `coverage_ratio`

It then emits one of:

- `PRIMARY_LEADS`
- `ALTERNATIVE_LEADS`
- `NULL_LEADS`
- `TIE_UNRESOLVED`
- `INSUFFICIENT_EVIDENCE`

Fail-closed settlement rules:

1. A triggered breaker cannot be offset by raw support count.
2. A resolver cannot select a winner if decisive observables lack admissible evidence.
3. Tie / weak margin remains `UNRESOLVED`.
4. Price direction alone cannot validate the mechanism.
5. Wrong-mechanism lucky direction is not epistemic success.

The reference resolver is deliberately transparent and qualitative. It is not an alpha score.

---

## 9｜Reveal & Qualification

Only after the blind resolution object is serialized and hash-bound may the sealed mapping and H4 settlement be revealed.

Post-reveal comparison may produce a **proposal**:

- `REPLAY_QUALIFIED_POSITIVE_CANDIDATE`
- `REPLAY_QUALIFIED_HARD_NEGATIVE_CANDIDATE`
- `MECHANISM_AMBIGUOUS_CANDIDATE`
- `EXPRESSION_ERROR_CANDIDATE`
- `INSUFFICIENT_EVIDENCE`
- `BLINDNESS_COMPROMISED`

None of these states is Historical Gold admission.

Historical Gold / Hard-Negative admission remains a later Human Gate requiring evidence review and, where required, A-grade independent blind replication.

---

## 10｜12-Case Scope

H4.1 remains deliberately narrow:

`Duration × Credit × Scarcity × {GOLD-role, Near Miss, Wrong Mechanism, Wrong Strike} = 12`

No additional replay episodes may be added merely to improve apparent hit rate.

The research question is not “how many historical examples can we collect?” but:

> Does H1/H2/H3 reduce causal overfitting and retrospective freedom on a balanced contrast set?

---

## 11｜CI / Fail-Closed Invariants

The dedicated H4.1 validator must reject:

- post-cutoff evidence entering resolver input;
- E3/E4 entering resolver input;
- missing E0 evidence claimed as fully hydrated;
- fake E1 independence;
- role-bearing IDs or `case_type` in blind packets;
- settlement leakage;
- blind result generated after reveal rather than before reveal freeze;
- Gold admission flags;
- Portfolio/sizing/trading/execution fields;
- forced primary wins under insufficient evidence.

The validator must be an explicit `repository-gates` step.

---

## 12｜Stop Condition

H4.1 stops after:

1. evidence contract machine tests pass;
2. 12 evidence packets are hydrated or explicitly degraded;
3. blind packets pass anti-leak validation;
4. resolver outputs are frozen;
5. reveal/qualification report is generated;
6. dedicated H4.1 CI gate and full repository tests are green;
7. a Human Review Card is produced.

At that point the system waits for Human Acceptance.

No merge, Historical Gold admission or capital authority is implied.
