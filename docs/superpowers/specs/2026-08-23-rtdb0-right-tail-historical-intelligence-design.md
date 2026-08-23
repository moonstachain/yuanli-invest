# RTDB0｜Right-Tail Historical Intelligence Database — Master Design Spec

**Status:** design_candidate_for_human_review  
**Date:** 2026-08-23  
**Repository:** `moonstachain/yuanli-invest`  
**Base:** `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
**Branch:** `rtdb0-master-design`  
**Human design acceptance:** `ACCEPT_RTDB0_MASTER_DESIGN_ONE_SHOT_EXECUTION`

## 0. Purpose

RTDB0 establishes the **Yuanli Right-Tail Historical Intelligence Database** as a governed historical research infrastructure for studying how major right-tail outcomes were generated, whether their mechanisms were observable at the time, whether Yuanli capabilities could discriminate them from matched hard negatives, and how later reality should revise future research capability.

RTDB0 is not a list of historical winners, not a ten-bagger database, not a stock recommender, and not a new factor model. It is a historical testbench for the accepted Yuanli research chain:

```text
P → Xs → N → V → Xa → Xp → S
```

and for the accepted learning loop:

```text
Theory → Hypothesis → Capability → Runtime → Replay → Benchmark
→ Failure → Future Settlement → Capability Revision
```

The architectural north star is:

> **History is not a museum. It is a training ground.**

RTDB0 exists only if historical research improves future discrimination under uncertainty.

---

## 1. Authority architecture

### 1.1 Three-system authority model

RTDB0 freezes the following authority boundaries:

```text
GitHub Canon / Contracts
        ↓
Supabase Operational Memory
        ↓
Notion Human Sensemaking
```

- **GitHub** is Semantic and Governance Authority: contracts, schemas, taxonomy, validators, migrations, replay protocols, projection manifests, acceptance rules, and immutable governance artifacts.
- **Supabase** is Operational Data Authority: admitted structured research state, historical evidence bundles, PIT snapshots, replay state, settlements, receipts, and read-optimized projections. Supabase is not Canon Authority.
- **Notion** is Human Projection Authority: what people should see, compare, learn, and navigate. Notion does not define machine truth.

Constitutional rule:

> **Authority is one-way; learning may flow back only through explicit Proposal → Review → Accepted Change.**

### 1.2 Non-parallel-plane rule

RTDB0 does not create a sixth architecture plane. It spans existing research architecture:

- Research State semantics;
- Capability invocation and replay semantics;
- Truth / settlement semantics.

RTDB0 extends existing Canon objects and reuses their meanings rather than forking them.

### 1.3 Core object separation

RTDB0 preserves:

- `ResearchTarget != RightTailCase != RightTailEpisode`
- `Episode != Thesis`
- `Target != Thesis != Position != Book`
- `Generator Definition != Generator Activation`
- `EvidenceClaim != Source`
- `OutcomeObservation != Settlement`
- `Projection != Research != History != Canon`
- `Receipt = Ledger; Status = Projection`
- `Research PASS != Capital PASS`
- `Claim Authority <= Evidence Authority`

No RTDB artifact may silently override these boundaries.

---

## 2. Historical object model

### 2.1 Epistemic atomic unit

The primary epistemic atom is:

```text
RightTailEpisode × PITSnapshot
```

not a company, ticker, or retrospective case narrative.

A company may have multiple distinct right-tail episodes. Example:

```text
NVIDIA
├── CUDA 2006
├── Deep Learning 2012
└── Generative AI Infrastructure 2022
```

This prevents silent historical thesis migration.

### 2.2 Shared Canon objects

RTDB0 reuses accepted Yuanli object meanings where applicable:

- `ResearchTarget`
- `EvidenceClaim`
- `ResearchState`
- `ResearchCapability`
- `ResearchReceipt`
- `FutureSettlement`
- `FailureRegime`
- `CapabilityRevision`

The implementation may use RTDB-specific persistence tables, but semantic identity must remain compatible with the accepted objects.

### 2.3 RTDB-specific domain objects

RTDB0 adds these primary historical research objects:

1. **RightTailCase** — stable case identity across one or more episodes.
2. **RightTailEpisode** — bounded historical mechanism episode with its own time window and return-engine interpretation.
3. **RightTailGenerator** — reusable cross-case generator definition projected from GitHub Canon.
4. **GeneratorActivation** — episode × generator × time activation state; never a static checkbox.
5. **PITSnapshot** — frozen historical knowledge boundary.
6. **CaseMilestone** — seed / evidence / ignition / expansion / maturity / break marker; separate from arbitrary PIT snapshots.
7. **MatchedCasePair** — positive / hard-negative / boundary pairing designed for ex-ante discrimination.
8. **ReplayExperiment** — experiment protocol, hypothesis, baseline, PIT inputs, and success criteria.
9. **ReplayRun** — one concrete capability execution bound to revisions and receipts.
10. **BenchmarkResult** — incremental-value comparison against simpler baselines.
11. **OutcomeObservation** — realized facts; not thesis validation.
12. **LearningReceipt** — explicit bridge from historical experiment to `CapabilityRevision`, `FailureRegime`, new hypothesis, or `descriptive_only`.

### 2.4 Object laws

RTDB0 freezes these laws:

1. Target is not Case.
2. Case is not Episode.
3. Episode is not Thesis.
4. PIT Snapshot is a knowledge boundary, not a market screenshot.
5. Generator activation is time-varying and evidence-backed.
6. Outcome is observation, not validation.
7. Hard Negative is a first-class experimental relationship.
8. Experiment design and runtime execution are separate.
9. Frozen PIT may only be superseded, never silently edited.
10. Replays are append-only facts.
11. Settlement never mutates original PIT state.
12. Historical lessons that do not change capability must be explicitly marked `descriptive_only` rather than inflated into new theory.

---

## 3. Right-Tail Generator model

### 3.1 RTG role

`RightTailGenerator` is a reusable mechanism object, not a score and not an asset label.

The initial **candidate** generator registry may include the following families. Candidate presence in RTDB0 does not grant Canon status; only the later implementation/governance acceptance process may promote a definition:

- Structural Expansion
- Value Concentration / Bottleneck Control
- Increasing Returns
- Network Effect / Preferential Attachment
- Scale Economy
- Scarcity / Brand Scarcity
- Ecosystem Lock-in
- Operating Leverage
- Optionality Generation
- Scientific Breakthrough
- Supply Inelasticity
- Reflexive Financing
- Tail Activation
- Convex Payoff

### 3.2 Generator page contract

Every generator definition must include:

- mechanism definition;
- necessary / enabling conditions;
- observable evidence contract;
- falsifier / invalidator contract;
- boundary conditions;
- Gold episodes;
- hard negatives / false positives;
- relation to P / Xs / N / V / Xa / Xp / S;
- relation to C / R / X without collapsing to a scalar score.

### 3.3 No right-tail scalar

RTDB0 must not create a universal `right_tail_score`, `PNX_score`, or equivalent hidden composite that converts the accepted causal structure into one number.

---

## 4. Point-in-Time constitution

### 4.1 PIT definition

A `PITSnapshot` is:

> A frozen representation of the research world that was legally knowable under an explicit evidence cutoff and publication-lag policy.

Required fields include:

- `as_of`
- `evidence_cutoff`
- `publication_lag_policy`
- `data_revision_policy`
- `information_set_version`
- `snapshot_stage`
- `freeze_state`
- immutable identity / revision metadata

### 4.2 Evidence time semantics

Evidence must distinguish at least:

- `effective_at`
- `published_at`
- `first_available_at`
- `retrieved_at`

Replay admissibility rule:

```text
Evidence.first_available_at <= PITSnapshot.evidence_cutoff
```

Future evidence crossing the cutoff must fail closed.

### 4.3 Four-layer PIT integrity

RTDB0 freezes:

```text
PIT Integrity = Data Safety + Projection Safety + Page Safety + Navigation Safety
```

- **Data Safety:** post-cutoff evidence cannot enter PIT evidence bundles.
- **Projection Safety:** `notion_pit_blind_projection_v1` contains no future outcome or settlement fields.
- **Page Safety:** PIT Blind pages never contain future settlement content.
- **Navigation Safety:** PIT-facing views hide final outcome, settlement verdict, future generator activations, and final Gold role.

### 4.4 Known / Inferred / Unknown separation

PIT human and machine projections must preserve:

```text
Known != Inferred != Unknown
```

A current-day narrative may not be backfilled into a frozen PIT snapshot.

---

## 5. Experimental truth architecture

### 5.1 Gold × Hard Negative

A mature Gold episode is not discrimination-grade until matched against at least one qualified hard negative, boundary case, or control.

Pair design must record:

- pair decision date;
- matching dimensions;
- ex-ante surface similarity;
- candidate discriminators;
- confounders;
- primary discriminator hypothesis;
- human review receipt.

A pair may not be created merely because one object is now known to have failed.

### 5.2 Replay contract

`ReplayExperiment` defines:

- capability and version;
- Canon revision/hash;
- PIT snapshot(s);
- positive and contrast episode(s);
- research hypothesis;
- baseline model(s);
- primary / secondary metrics;
- leakage policy;
- success criteria.

`ReplayRun` records one execution and must bind:

- code commit;
- capability version;
- Canon revision;
- PIT snapshot IDs;
- evidence cutoff;
- runtime provider;
- result state IDs;
- receipt ID;
- degrade / failure state.

### 5.3 Benchmark and ablation

Complex capabilities must be compared against simpler baselines. A capability that does not provide stable incremental information should be demoted rather than defended by narrative complexity.

Replay infrastructure must support:

- baseline comparison;
- matched-pair discrimination;
- false-positive / false-negative analysis;
- ablation of specific generator signals;
- complexity penalty where appropriate;
- leakage audit.

### 5.4 Settlement

Settlement answers claim and mechanism questions, not merely asset return.

Allowed verdict families include:

- `SUPPORTED`
- `CONTRADICTED`
- `UNRESOLVED`
- `RIGHT_OUTCOME_WRONG_MECHANISM`
- `WRONG_OUTCOME_RIGHT_MECHANISM`

Every accepted settlement must end in one of:

- `REVISION_REQUIRED`
- `NO_REVISION_REQUIRED`
- `DESCRIPTIVE_ONLY`

---

## 6. Supabase physical architecture

### 6.1 Project isolation

RTDB0 must not share the existing `yuanli-health` Supabase project.

Target project name:

```text
yuanli-invest-data
```

Creating the project requires a separate explicit cost confirmation at implementation time if the platform reports a non-zero or billable cost.

### 6.2 Schemas

The physical design uses:

```text
rt_core
rt_epistemic
rt_experiment
rt_ledger
rt_projection
rt_sync
private
```

- `rt_core`: cases, episodes, generator refs, activations, matched pairs.
- `rt_epistemic`: PIT snapshots, source identity, evidence versions/claims/links, outcome observations.
- `rt_experiment`: replay experiments/runs, benchmarks, failure links, settlements, learning links.
- `rt_ledger`: append-only ingestion/research/replay/settlement/projection/sync receipts.
- `rt_projection`: read-optimized API / Notion projection contracts.
- `rt_sync`: outbox, projection map, reconciliation and drift state.
- `private`: privileged helper functions, enforcement functions, worker-only plumbing.

### 6.3 Identity

Every domain object uses both:

- internal UUID primary key;
- stable human/machine `object_key`.

Example keys:

```text
RTCASE-NVDA
RTEP-NVDA-GENAI-2022
RTG-BOTTLENECK-CONTROL
PIT-NVDA-GENAI-20221130
RTPAIR-NVDA-CISCO-2022
RTRP-NVDA-CISCO-CAPXS01
RTSET-NVDA-GENAI-20221130
```

Object keys are never reused.

### 6.4 Structured columns vs JSONB

Fields that must be joined, filtered, constrained, benchmarked, or audited are relational columns. JSONB is reserved for extensible details such as diagnostics, uncertainty maps, mechanism detail, provider metadata, or scenario payloads.

### 6.5 Lifecycle classes

- Ledger / Receipt data: append-only.
- Frozen knowledge objects: new revision + supersede; never overwrite.
- Workflow / display state: mutable under governed status semantics.

### 6.6 RLS / roles

Initial logical roles:

- `rt_admin`
- `rt_ingest`
- `rt_reviewer`
- `rt_replay`
- `rt_projector`
- `rt_reader`

Replay roles must not be able to access future truth for the PIT being evaluated.

### 6.7 Search

Full-text and structured filtering are primary. pgvector may be added as a retrieval layer, but semantic similarity never becomes Evidence Authority or automatic Gold promotion.

---

## 7. Notion Think-Tank architecture

### 7.1 Positioning

Notion is the Human Sensemaking Layer, not a database admin UI.

Portal mother question:

> **世界如何生成少数极端赢家？**

Sub-question:

> 当未来还没有成为历史时，哪些结构变化已经能够被看见？

### 7.2 Global + specialized model

Existing `Knowledge Object Registry` remains the global directory. RTDB0 must not create a second global registry.

RTDB0 creates seven specialized Notion databases:

1. Right-Tail Case Registry
2. Right-Tail Episode Library
3. Right-Tail Generator Atlas
4. PIT Snapshot Library
5. Contrast Pair Lab
6. Replay Dossier
7. Reality Settlement & Learning

Not every specialized object is globally registered. Global Registry admission is derived from the implementation-time eligibility contract rather than from manual one-off promotion.

### 7.3 Page system

All RTDB pages share one **Research Passport** and six Gold research templates:

- T1 Gold Episode
- T2 Generator
- T3 PIT Blind
- T4 Contrast Pair
- T5 Replay Dossier
- T6 Reality Settlement

Case pages remain lightweight identity/index pages.

### 7.4 Human reading grammar

Deep pages share:

```text
Identity → Question → Mechanism → PIT → Contrast
→ Replay → Settlement → Transfer
```

History transfers questions and capability, not stock recommendations.

### 7.5 Portal doors

The Think Tank presents:

- Thirty-Year Right-Tail Map
- Generator Atlas
- Gold Case Library
- Contrast Lab
- PIT Replay Lab
- Reality Settlement
- From History to Now

### 7.6 Learning journeys

One knowledge graph supports three reading depths:

- Beginner: Map → Case → Generator → Contrast.
- Entrepreneur: Generator → Value Concentration → Case → business-transfer questions.
- Researcher: Generator → PIT → Pair → Replay → Benchmark → Settlement → Revision.

The same object is not copied three times.

---

## 8. Supabase → Notion Projection Contract

### 8.1 Projection, not bidirectional sync

RTDB0 V1 implements:

```text
GitHub → Supabase → Notion
```

Notion feedback may become future governance proposals but does not automatically mutate Supabase or GitHub.

Principle:

> **One-way Truth, Two-way Intelligence.**

### 8.2 Stable projection contracts

Supabase exposes versioned projection views:

- `notion_case_projection_v1`
- `notion_episode_projection_v1`
- `notion_generator_projection_v1`
- `notion_pit_blind_projection_v1`
- `notion_contrast_projection_v1`
- `notion_replay_projection_v1`
- `notion_settlement_projection_v1`

Breaking projection changes require a new contract version.

### 8.3 Field ownership

Each Notion property is declared as one of:

- `MACHINE`
- `HUMAN`
- `PROPOSAL`
- `DERIVED_NOTION`

V1 rule:

- Projector may patch MACHINE-owned properties.
- Human long-form page body is never overwritten after initial template installation.
- PROPOSAL fields do not mutate upstream truth automatically.

Payload hashes cover machine-owned state only.

### 8.4 Transactional outbox

Accepted source-state changes append `projection_outbox` records in the same transaction.

Outbox event families:

- `CREATE_OR_UPDATE`
- `RELATION_REFRESH`
- `DEPRECATE`
- `REBUILD`
- `VERIFY`

Notion availability never controls whether Supabase commits succeed.

### 8.5 Projector behavior

The projector is a compiler/delivery worker only. It may not interpret investment semantics.

Flow:

```text
Claim Outbox Job
→ Read Projection Contract
→ Compute Desired Payload
→ Lookup Projection Map
→ Create / Patch / No-op
→ Bind Relations
→ Verify
→ Append Sync Receipt
→ Complete Outbox Job
```

### 8.6 Two-pass relations

Projection is topologically ordered:

1. Case + Generator identity
2. Episode identity
3. PIT + Contrast identity
4. Replay identity
5. Settlement identity
6. Relation refresh
7. selected Global Registry projection

This prevents missing relation dependencies.

### 8.7 Reconciliation

Daily reconciliation compares:

- desired source revision/hash;
- applied revision/hash;
- page existence;
- machine-owned property state;
- relation integrity;
- projection contract version.

Reconciliation emits drift evidence and repair jobs; it does not blindly rewrite every page.

### 8.8 Error taxonomy

Sync failure states include:

- `RETRYABLE`
- `DEPENDENCY_WAIT`
- `BLOCKED_SCHEMA`
- `BLOCKED_AUTH`
- `BLOCKED_CONFLICT`
- `DEAD_LETTER`

Runtime schema drift fails closed.

### 8.9 Delete policy

Projector never hard-deletes Notion pages automatically. Upstream deprecation changes projection state and hides objects from normal views; archive/destructive deletion remains governed human action.

---

## 9. Genesis dataset

### 9.1 Initial Gold set

RTDB0 targets 12 Genesis **case families**, each with one initial canonical Gold episode selected during implementation:

1. Amazon
2. Apple
3. Microsoft Cloud
4. NVIDIA
5. Tencent
6. Moutai
7. Tesla
8. Bitcoin
9. Gold
10. Paulson Subprime
11. GLP-1
12. ASML

These are research starting points, not investment recommendations.

### 9.2 Matched hard negatives

Each initial Gold episode must receive at least one matched hard negative, boundary case, or control based on ex-ante similarity rather than ex-post failure knowledge.

Candidate pairs include, subject to research validation:

- Amazon ↔ Webvan
- Apple ↔ Nokia / BlackBerry
- NVIDIA ↔ Cisco 2000 where the research question is structural truth versus price prepayment
- Tencent ↔ Renren
- Bitcoin ↔ Luna / FTX only where the matched dimensions are explicitly justified

Pair identity is not accepted until matching dimensions and confounders are reviewed.

### 9.3 PIT density

Genesis aims for approximately 3–5 meaningful PIT snapshots per initial Gold episode plus the PIT snapshots required for matched contrasts, producing roughly 100 historical knowledge slices across the first qualified corpus.

Quality dominates quantity.

### 9.4 First E2E proof

The first production-grade end-to-end proof is:

```text
NVIDIA Generative AI Infrastructure 2022
```

The full chain must pass before bulk Genesis expansion:

```text
GitHub Contract
→ Supabase Case / Episode / Generator
→ PIT Snapshot
→ Evidence Boundary
→ Matched Contrast
→ Capability Replay
→ Benchmark
→ Settlement
→ Notion Gold Episode
→ PIT Blind
→ Contrast
→ Reality Settlement
```

If this chain cannot be reproduced and audited, bulk import is blocked.

---

## 10. Acceptance gates

RTDB0 replaces many micro-gates with six Gold Acceptance Gates.

### G1 — Semantic Integrity

- No conflict with accepted Yuanli object meanings.
- No new scalar PNX/right-tail score authority.
- Target / Case / Episode / Thesis boundaries remain explicit.

### G2 — PIT Integrity

- Post-cutoff evidence fails closed.
- Frozen PIT cannot be silently edited.
- Blind projection contains no future fields.
- PIT leakage violations = 0.

### G3 — Experimental Integrity

- Every Gold has qualified contrast coverage.
- Replay competes against simpler baselines.
- Important generator signals can be ablated.
- Failure and unresolved outcomes are preserved.

### G4 — Reproducibility

A replay is reproducible when the same Canon revision, capability version, code commit, PIT input IDs, evidence cutoff, and frozen fixtures produce:

- exact equality for object identity, evidence bundle hash, receipt lineage, categorical verdicts, and benchmark pass/fail state;
- fixture-defined numeric tolerances for model/provider outputs where exact floating-point equality is not guaranteed.

The tolerance value must live in the executable test fixture/contract; it may not be chosen after seeing the rerun result.

### G5 — Projection Integrity

- Notion can be rebuilt from Supabase projection contracts without semantic loss.
- Human page body survives repeated projector runs.
- Projection drift and schema drift are detectable.
- Object-key upsert is idempotent.

### G6 — Reality Learning

- Settlement never mutates PIT.
- Settlement resolves claims/mechanisms separately from raw return.
- Capability delta is explicit or marked `DESCRIPTIVE_ONLY`.

RTDB0 becomes `GENESIS_QUALIFIED` only when all six pass.

---

## 11. Failure modes / hard negatives

Implementation must fail closed against at least these classes:

1. A company ticker is used as the sole historical research object.
2. A giant retrospective case merges multiple incompatible theses.
3. Generator presence is stored as a static checkbox without time/evidence semantics.
4. Post-cutoff evidence enters a replay bundle.
5. Frozen PIT is updated in place.
6. Settlement modifies historical PIT state.
7. Outcome return automatically marks a thesis supported.
8. Gold promotion occurs without a matched hard negative / boundary case.
9. Hard negatives are selected solely because their eventual failure is known.
10. Capability replay is accepted without a simple baseline.
11. A right-tail or PNX scalar becomes hidden authority.
12. Notion edits mutate machine-owned source truth.
13. Projector overwrites human page body.
14. Projection hash includes human narrative and therefore triggers destructive rewrites.
15. A Notion schema drift is auto-adapted by the worker rather than blocked.
16. PIT blind projection exposes settlement or future outcome fields.
17. Sync failure rolls back accepted Supabase research state.
18. Notion deletion silently erases human research history.
19. Supabase schema is changed manually without GitHub migration authority.
20. RTDB is placed inside the health-data Supabase project.

---

## 12. Implementation decomposition

After written-spec Human Acceptance, implementation planning must decompose work into eight battles under one master execution plan:

1. **Battle 0 — Master Plan / Environment Qualification**
   - implementation plan;
   - repo head/CI qualification;
   - Supabase project cost/organization confirmation;
   - Notion target-page/schema verification.

2. **Battle 1 — GitHub RTDB Canon / Schema / Validators**
   - RTDB docs;
   - JSON schemas;
   - generator registry contracts;
   - PIT / hard-negative / receipt invariants;
   - RED tests first.

3. **Battle 2 — Supabase Project + Physical Schema**
   - independent project;
   - schema namespaces;
   - migrations;
   - roles/RLS;
   - append-only enforcement.

4. **Battle 3 — PIT / Ledger / Projection Infrastructure**
   - evidence availability constraints;
   - freeze/supersede logic;
   - replay-safe access;
   - projection views;
   - outbox / maps / receipts.

5. **Battle 4 — Notion Think-Tank Construction**
   - seven specialized databases;
   - one Research Passport;
   - six templates;
   - portal views and learning journeys;
   - no raw evidence warehouse replication.

6. **Battle 5 — Projector + Reconciliation**
   - idempotent create/update/no-op;
   - two-pass relations;
   - field ownership manifest;
   - drift detection;
   - PIT-safe projection.

7. **Battle 6 — NVIDIA Genesis E2E**
   - one complete Gold chain;
   - matched contrast;
   - PIT replay;
   - benchmark / ablation;
   - settlement;
   - Notion projection;
   - exact receipts.

8. **Battle 7 — 12+12 Genesis Expansion + Qualification**
   - remaining case families and initial Gold episodes;
   - matched hard negatives / boundary cases;
   - replay/settlement coverage;
   - six acceptance gates;
   - Human Review package.

Every executable battle follows:

```text
RED → GREEN → REVIEW → RECEIPT
```

Micro-approval gates are intentionally eliminated. Human approval is required only where governance or external side effects demand it, including Supabase project billing confirmation, destructive actions, and final Canon/merge decisions.

---

## 13. Scope freeze

### In scope

- RTDB Canon design and contracts;
- historical object model;
- right-tail generator registry contract;
- PIT evidence boundary and leakage protection;
- Gold / hard-negative experimental design;
- replay / benchmark / settlement linkage;
- independent Supabase research data plane;
- projection/outbox/reconciliation infrastructure;
- Notion RTDB Think Tank;
- Genesis 12+12 corpus;
- NVIDIA E2E proof;
- CI / validators / receipts / Human Review artifacts.

### Out of scope for RTDB0

- portfolio sizing or trading execution;
- automatic BUY / SELL recommendations;
- replacing accepted P/N/X/E/V/S semantics;
- replacing C/R/X return-engine ontology;
- a universal right-tail ranking score;
- bulk raw Wind market-data warehousing in Supabase;
- automatic Notion → Supabase truth mutation;
- public portal publication without a separate visibility decision;
- unrelated changes to YIP0 / ME0 / ME1 accepted authority;
- health-data storage or health-system integration.

---

## 14. Security and operational rules

1. Supabase secrets / Notion tokens never enter GitHub.
2. Projector is a transport/compiler role and may not mutate research truth.
3. Secret/backend credentials remain server-side.
4. Public/anonymous access is denied by default.
5. Human content is preserved during projection updates.
6. Destructive deletion requires explicit human authorization.
7. Backups / PITR are required for production once available on the selected plan.
8. High-value governance manifests and receipts may be projected to GitHub; raw evidence and market-data payloads should not be duplicated there.

---

## 15. RTDB0 constitutional rules

1. **GitHub defines; Supabase operates; Notion projects.**
2. **Authority is one-way; learning may return through governed proposals.**
3. **Case × PIT is the historical epistemic unit.**
4. **Gold × Hard Negative is the default discrimination experiment.**
5. **Claim Authority <= Evidence Authority.**
6. **Outcome != Thesis Validation.**
7. **Receipt = Ledger; Status = Projection.**
8. **PIT Integrity = Data + Projection + Page + Navigation.**
9. **Projector may move truth; it may never invent truth.**
10. **History transfers questions and capability, not recommendations.**
11. **Historical infrastructure exists to improve future capability, not celebrate past winners.**
12. **Gold quality dominates dataset quantity.**

---

## 16. Human Review Gate

Written-spec Human Review should evaluate the design as one integrated architecture rather than reopening micro-sections.

The review passes when all of the following are accepted:

1. Authority boundaries are coherent and non-overlapping.
2. Object model prevents ticker-centric retrospective storytelling.
3. PIT constraints are fail-closed and auditable.
4. Gold / hard-negative structure is scientifically meaningful.
5. Replay / benchmark / settlement form one learning loop.
6. Supabase physical separation and schema boundaries are appropriate.
7. Notion is a Human Sensemaking layer rather than a data mirror.
8. Projection design preserves machine/human/proposal write authority.
9. NVIDIA E2E is a sufficient Genesis proof before bulk expansion.
10. Six Gold Acceptance Gates are sufficient to qualify the system.
11. Scope excludes portfolio/trading and unrelated Canon mutation.
12. The design is focused enough for one master implementation plan with eight independently reviewable battles.

### Requested written-spec acceptance token

```text
ACCEPT_RTDB0_MASTER_WRITTEN_SPEC
```

This spec authorizes implementation planning only after written-spec Human Acceptance. It does not by itself authorize billable Supabase project creation, destructive Notion actions, protected-branch merge, or final RTDB Canon promotion.
