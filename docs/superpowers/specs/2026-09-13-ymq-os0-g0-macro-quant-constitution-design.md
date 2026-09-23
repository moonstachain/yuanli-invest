# YMQ-OS0-G0｜Macro Quant Constitution × Object Model × Physical Plane Freeze — Design

Date: 2026-09-13  
Status: `DESIGN_CANDIDATE / WRITTEN_SPEC_REVIEW_REQUIRED`  
Scope: `YMQ-OS0-G0 only`  
Architecture approval basis: explicit Human instruction `同意，深度执行：YMQ3-R0 ... / YMQ-OS0-G0 ...`  
Design base: protected `main` at `ee497283d0b402e16f43e91abc759355ebe35e5e`

---

## 0｜Mission

`YMQ-OS0-G0` freezes the constitutional and physical boundary of the Yuanli Macro Quant Intelligence OS.

It does **not** create a new investment philosophy, does **not** replace YIOS0, does **not** promote any research result to Capital Authority, and does **not** authorize portfolio sizing, VeighNa, broker connectivity, paper orders, live orders or real capital movement.

Its mission is narrower and more concrete:

> **Turn macro-quant research into a governed Point-in-Time research operating system in which external Reality is timestamped, every computed state is reproducible, every model run is defeasible, every result is benchmarked, and every settlement can be traced back to immutable evidence without allowing research authority to leak into capital or execution authority.**

Canonical research loop for this subsystem:

`External Reality → Evidence Snapshot → PIT Observation → PIT Feature → PIT State → Transmission → Capability Run → Research Settlement → LearningDelta`

YMQ-OS is a subsystem of YIOS0 L2–L8. It is not a parallel Investment OS.

---

## 1｜Authority position and inheritance

### 1.1 Parent authorities

The following existing authority remains binding:

1. `YIP0` — Investment Philosophy Authority.
2. `YIOS0` — system architecture/current-definition authority.
3. `ME0 / ME1` — accepted research ontology/state-object authority.
4. Existing accepted `YMQ4-DP1-A / DP1-B / B2` receipts — physical evidence that portions of the PIT/evidence plane can work in Reality.
5. `YMQ4-B3` remains `DRAFT / OPEN / NOT MERGED` with the scientific observation `DYNAMIC_BETA_DOES_NOT_BEAT_B2`; YMQ-OS0 may reference that result but must not rewrite, rescue, promote or conceal it.
6. `YEX0` and exact accepted `YVN1` stages remain the action-side authority boundary.

### 1.2 Binding laws

YMQ-OS0 inherits and makes operational the following laws:

- `Reality > Belief`
- `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition`
- `ClaimAuthority <= EvidenceAuthority`
- `ResearchPass != CapitalPass`
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
- `UNKNOWN = DENY`
- `Receipt = Ledger; Status = Projection`
- `Past Evidence Is Immutable; Learning May Revise Only Future State`

### 1.3 Namespace reconciliation

The repository already contains a substantial `YMQ4` Gold PIT / beta research lineage. YMQ-OS0 therefore freezes this rule:

> **Existing YMQ4 IDs are historical program IDs and MUST NOT be silently renumbered to match the new five-engine architecture.**

The five stable engine roles use the prefix `MQE`:

- `MQE1` Macro Reality Engine
- `MQE2` Industrial Reality Engine
- `MQE3` Narrative × Herding Engine
- `MQE4` Dynamic Transmission Engine
- `MQE5` Price × Payoff Engine

`YMQ3-R0` is the first formal Reality Audit for `MQE3`.

Existing `YMQ4` work is treated as inherited seed evidence for portions of `MQE4`, subject to its exact accepted authority and scientific settlement. No alias may imply that `YMQ4 == MQE4 Canon`.

---

## 2｜What YMQ-OS is — and is not

### 2.1 It is

A governed research subsystem that can:

- acquire external macro/market/industry/narrative facts;
- preserve revision/vintage/availability semantics;
- compile point-in-time state;
- execute deterministic or model-based research capabilities;
- compare candidates against frozen baselines;
- run replay, ablation, hard negatives and leakage checks;
- persist physical/scientific/authority settlement separately;
- expose low-authority Human/AI projections;
- produce a Research Settlement Packet consumable by a separately governed Capital Admission layer.

### 2.2 It is not

YMQ-OS0 does not authorize:

- automatic macro forecasting claims;
- one global macro score;
- one model choosing asset weights;
- auto-tuning against future outcomes;
- hidden use of revised historical data in PIT replay;
- trading signals as Capital Authority;
- portfolio sizing;
- execution;
- broker credentials;
- live/paper orders;
- silent Canon promotion from a good backtest.

---

## 3｜Four physical planes

YMQ-OS0 freezes four primary planes. Providers are replaceable; authority roles are not.

### P1｜Law & Control Plane — GitHub

Primary role: **law, contracts, code lineage, review, CI, versioning, admission**.

Authoritative repository for this subsystem: `moonstachain/yuanli-invest`.

Expected content after implementation:

- constitutions and architecture receipts;
- object schemas and contracts;
- source-authority registry definitions;
- capability contracts;
- preregistrations;
- baselines and kill gates;
- validators/tests;
- workflow definitions;
- scientific and Human acceptance receipts.

GitHub is **not** the raw time-series database.

`quant-workspace` may later host compute-oriented implementation adapters, but it receives no independent law authority from YMQ-OS0.

### P2｜Evidence & Runtime Truth Plane — Postgres/Supabase + Object Storage/NAS

Primary role: **immutable source snapshots, PIT observations, derived runtime state, run receipts and readback truth**.

Existing accepted YMQ4 groundwork already materializes schemas including `evidence`, `pit`, and `runtime`; YMQ-OS0 extends rather than forks that lineage.

Storage split:

- Object Storage / NAS: raw source payloads, licensed files, immutable snapshots, hashes.
- Postgres/Supabase: source metadata, PIT observations, features/state indexes, run/settlement receipts.

No Human-facing dashboard or HF repository becomes the authoritative PIT truth merely because it is easier to inspect.

### P3｜Experiment Compute Plane — Hugging Face Jobs / replaceable container runner

Primary role: **ephemeral reproducible compute**.

Allowed workloads:

- panel materialization from authorized evidence;
- feature generation;
- historical replay;
- candidate model fitting;
- baseline/ablation/hard-negative evaluation;
- artifact hashing;
- deterministic result production.

Hugging Face is a provider, not authority.

Design-time WebGPT readback on 2026-09-13 observed authenticated HF identity `Hay2045` with OAuth scopes `jobs`, `openid`, `profile`, `read-mcp`, `read-repos`, and no write-repos scope. This is a transient Reality observation, **not** a permanent architecture assumption. Any future Dataset/Model/Space write path requires a separately verified writable credential and must fail closed if absent.

HF Datasets/Models may host versioned **research projections/artifacts** after authorization, but the canonical evidence lineage remains anchored by GitHub law + Evidence Plane provenance/hash.

### P4｜Experience & Projection Plane — Web / HF Space / ChatGPT / Notion

Primary role: **human and AI inspection**.

Allowed:

- market-state cockpit;
- provenance drill-down;
- replay comparison;
- state-transition visualization;
- Human review/approval requests;
- ChatGPT reasoning over authorized Context.

Forbidden:

- direct mutation of Canon;
- silent overwrite of PIT truth;
- direct Capital or Execution authority;
- presentation of stale projections as current without `known_as_of`.

### Non-plane｜Execution

VeighNa/broker execution remains outside YMQ-OS. A future accepted Research Settlement may be consumed by Capital Admission, but:

`YMQ Research Settlement →/≠ Execution Authorization`.

---

## 4｜Nine canonical research objects

YMQ-OS0 freezes nine object classes. They are semantic contracts, not necessarily nine database tables.

### O1｜`SourceSnapshot`

Immutable evidence payload identity.

Minimum fields:

- `source_id`
- `source_authority_tier`
- `source_class`
- `canonical_locator`
- `retrieved_at`
- `content_sha256`
- `storage_locator`
- `license_class`
- `runner_git_sha`

Invariant: a snapshot may be superseded but never silently mutated.

### O2｜`ObservationPIT`

A value/fact known to the system at a specific historical time.

Minimum fields:

- `observation_id`
- `series_or_fact_id`
- `observation_time`
- `release_time`
- `vintage_time`
- `known_as_of`
- `value`
- `unit`
- `source_snapshot_id`
- `measurement_regime`
- `pit_status`

Invariant: a replay at `T0` may read only observations with `known_as_of <= T0`.

### O3｜`FeaturePIT`

A reproducible transformation of one or more PIT observations.

Minimum fields:

- `feature_id`
- `feature_definition_version`
- `as_of`
- `input_observation_refs`
- `transform_git_sha`
- `value`
- `lookback_window`
- `normalization_rule`

Invariant: all inputs must be PIT-valid at the same `as_of` boundary.

### O4｜`StatePIT`

A structured estimate of the world at `T0`.

Examples:

- Macro Reality State
- Industrial Reality State
- Narrative State
- Herding State
- Asset Beta State
- Price/Payoff State

Minimum fields:

- `state_id`
- `state_type`
- `as_of`
- `feature_refs`
- `method_version`
- `state_payload`
- `uncertainty`
- `unknown_fields`

Invariant: uncertainty/unknown cannot be converted to a stronger state by UI projection.

### O5｜`TransmissionEdgePIT`

A time-bounded relationship hypothesis or estimate from a driver/state to another state/asset.

Minimum fields:

- `edge_id`
- `from_state_or_driver`
- `to_state_or_asset`
- `as_of`
- `method`
- `coefficient_or_effect`
- `confidence_or_uncertainty`
- `evidence_refs`
- `stability_window`

Invariant: `Beta_{i,t}` is stateful, not permanent law.

### O6｜`ResearchClaim`

A defeasible machine/human-readable claim.

Minimum fields:

- `claim_id`
- `claim_type`
- `as_of`
- `statement`
- `evidence_refs`
- `claim_authority`
- `falsifier`
- `expiry_or_review_rule`

Invariant: `ClaimAuthority <= EvidenceAuthority`.

### O7｜`CapabilityRun`

One reproducible invocation of a frozen research capability.

Minimum fields:

- `run_id`
- `battle_id`
- `capability_id`
- `capability_version`
- `git_sha`
- `dataset_or_panel_revision`
- `parameter_contract`
- `started_at`
- `completed_at`
- `artifact_hashes`
- `runner_identity`

Invariant: a result without an exact run identity cannot be used for scientific settlement.

### O8｜`ResearchSettlement`

Separates what physically ran, what science learned, and what authority exists.

Minimum fields:

- `settlement_id`
- `run_refs`
- `physical_status`
- `scientific_status`
- `authority_status`
- `baseline_result`
- `hard_negative_result`
- `ablation_result`
- `known_limitations`
- `next_authorized_stage`

Invariant: `PHYSICAL_PASS` may coexist with `SCIENTIFIC_NO_GO`.

### O9｜`LearningDelta`

A forward-only update proposal generated from settlement.

Minimum fields:

- `learning_id`
- `settlement_ref`
- `proposed_change`
- `affected_capability_or_contract`
- `evidence_basis`
- `requires_human_review`
- `status`

Invariant: LearningDelta may change future capability law only through GitHub review/admission. It cannot rewrite past evidence or settlement.

### Derived, non-canonical projections

`DecisionPacket`, `DashboardCard`, `Alert`, `StateSummary` and `PortfolioSuggestion` are projections built from the nine objects. They do not gain independent authority merely by existing.

---

## 5｜Point-in-Time temporal constitution

PIT semantics are a first-class law, not a data-cleaning detail.

### 5.1 Required timestamps

Where applicable, the system distinguishes:

- `event_time` — when the real-world event occurred;
- `observation_time` — economic/market period represented;
- `release_time` — when the source first published it;
- `vintage_time` — which revision/vintage is represented;
- `known_as_of` — earliest time the system was allowed to know the value;
- `retrieved_at` — when the system physically fetched the source;
- `ingested_at` — when the system wrote the object;
- `settled_at` — when a research settlement was frozen.

### 5.2 Replay law

For a replay boundary `T0`:

`ALLOW(object) iff object.known_as_of <= T0`

No later revision may be substituted for an earlier vintage unless the explicit research question is revision-aware and separately preregistered.

### 5.3 Market data

Market observations must preserve:

- venue/session timezone;
- close/fix timestamp;
- corporate-action adjustment policy where relevant;
- provider publication/availability semantics;
- missing-market-calendar semantics.

### 5.4 Text and narrative data

A document may enter a T0 replay only if its publication/availability time is proven. A modern retrospective article describing an old narrative is **historical evidence about the episode**, not valid PIT input for that episode.

### 5.5 Unknown rule

If release/vintage/availability semantics cannot be reconstructed to the required authority tier:

`PIT_STATUS = UNKNOWN` → deny use in PIT scientific claims.

---

## 6｜Five stable macro-quant engines

The engines are research capability families, not models.

### `MQE1｜Macro Reality Engine`

Question: what macro force is changing at the margin?

Domains:

- Growth
- Inflation
- Liquidity
- Credit
- Fiscal
- External/FX conditions

Primary representation:

`Level, Δ, Δ², Breadth, Surprise`.

### `MQE2｜Industrial Reality Engine`

Question: where is macro/technology change physically entering industry economics?

Domains:

- earnings
- orders
- inventory
- capex
- capacity
- margins/ROIC
- bottlenecks

### `MQE3｜Narrative × Herding Engine`

Question: is a story becoming shared belief, shared positioning and observable capital-behavior convergence — and can that be distinguished from a common shock?

Sensors may include:

- text/topic diffusion;
- narrative concentration/entropy;
- counter-narrative share;
- CSAD/CCK;
- DCC/rolling dependency;
- positioning/flow where PIT-valid.

`YMQ3-R0` is the Genesis Reality Audit for this engine.

### `MQE4｜Dynamic Transmission Engine`

Question: which driver is pricing which asset **now**, and is that relationship changing?

Methods may include:

- frozen beta baseline;
- rolling beta;
- state-space/TVP candidate;
- DCC;
- causal/transmission graph candidates.

Existing YMQ4 Gold work is inherited experimental evidence, including its B3 scientific NO-GO. No automatic production claim follows.

### `MQE5｜Price × Payoff Engine`

Question: what has already been priced, what is the current market confirmation, and what payoff asymmetry remains?

Domains:

- trend;
- breadth;
- realized/implied volatility;
- valuation;
- positioning/crowding;
- payoff/falsifier state.

MQE5 may inform a Research Settlement but cannot issue capital sizing authority.

---

## 7｜Capability execution contract

Every YMQ capability invocation must bind at least:

```text
battle_id
capability_id
capability_version
git_sha
source/panel revisions
T0 or live known_as_of
parameter_contract
baseline_id
hard_negative_set
ablation_set
falsifiers
runner identity
output artifact policy
```

A run is invalid if any of these are materially ambiguous after execution.

HF Jobs, GitHub Actions, local container or another future runner may execute the contract. Runner substitution is allowed only if deterministic input/output contracts remain satisfied.

---

## 8｜Repository and physical artifact target after approval

Implementation is expected to create a narrow YMQ-OS0 namespace without rewriting YIOS0 v1.0.

Expected artifacts:

```text
docs/architecture/ymq_os0/
├── YMQ-OS0-CONSTITUTION-v0.1.md
├── YMQ-OS0-OBJECT-MODEL-v0.1.md
├── YMQ-OS0-PHYSICAL-PLANE-FREEZE-v0.1.md
├── YMQ-OS0-HUMAN-REVIEW-CARD-v0.1.md
└── YMQ-OS0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md

config/ymq_os0/
└── ymq_os0_contract.v0.1.json

packages/contracts/schemas/ymq/
├── source_snapshot.schema.json
├── observation_pit.schema.json
├── feature_pit.schema.json
├── state_pit.schema.json
├── transmission_edge_pit.schema.json
├── research_claim.schema.json
├── capability_run.schema.json
├── research_settlement.schema.json
└── learning_delta.schema.json

scripts/
└── validate_ymq_os0_g0.py

tests/
└── test_ymq_os0_g0.py
```

No Supabase/HF runtime mutation is required merely to qualify the G0 constitution. Runtime migrations belong to subsequent separately planned tasks.

---

## 9｜Qualification gates

`YMQ-OS0-G0｜MACHINE_QUALIFIED` requires all of the following:

1. nine object schemas exist and validate;
2. object relationships preserve PIT lineage;
3. physical planes have exactly one primary authority role each;
4. HF/provider names are replaceable adapters, not embedded authority;
5. existing YMQ4 accepted/no-go states are referenced without rewriting their settlement;
6. no Capital/Execution authority appears in schema or docs;
7. validators fail if `ResearchPass == CapitalPass` semantics are introduced;
8. validators fail if a PIT object can reference evidence `known_as_of > as_of`;
9. validators fail if `ResearchSettlement` collapses physical/scientific/authority state into one `PASS`;
10. repository `contracts` and `governance` checks pass on the candidate head.

`HUMAN_ACCEPTED` is a separate gate after machine qualification.

---

## 10｜Failure conditions

G0 fails closed if any of the following occurs:

- YMQ-OS is described as a replacement for YIOS0;
- existing YMQ4 scientific NO-GO is hidden or upgraded;
- HF/Supabase/Notion/ChatGPT is granted Canon authority by provider identity alone;
- one database timestamp is used to stand in for release/vintage/known-as-of semantics;
- raw evidence can be mutated without creating a new snapshot/hash;
- a research output can directly create an execution action;
- a dashboard state can overwrite Evidence/PIT truth;
- unknown evidence is silently imputed into a high-authority claim;
- a positive backtest auto-promotes a capability;
- the architecture requires a specific cloud vendor to remain scientifically reproducible.

---

## 11｜Relationship to YMQ3-R0

`YMQ3-R0` is the first Genesis battle designed to prove whether this constitution is operationally useful.

Dependency law:

- YMQ3-R0 Written Spec may be designed in parallel.
- YMQ3-R0 implementation must bind to the G0 object/time/plane contracts.
- YMQ3-R0 may produce `ResearchSettlement`; it cannot produce Capital Admission.
- A valid YMQ3-R0 result may be `PHYSICAL_PASS / SCIENTIFIC_NO_GO`; that is a successful Reality audit, not a failed engineering project.

---

## 12｜Out of scope

Explicitly excluded from YMQ-OS0-G0:

- live data vendor procurement;
- production macro dashboard;
- n8n scheduling;
- HF Dataset/Model/Space creation;
- Supabase schema migration beyond existing inherited evidence;
- YMQ3-R0 code execution;
- Dynamic Beta rescue of YMQ4-B3;
- Market Clock state-machine implementation;
- portfolio construction;
- VeighNa;
- broker paper/live;
- any real capital action.

These require separate accepted design/plan/authority.

---

## 13｜Strategic closure

YMQ-OS0-G0 freezes one principle above all:

> **Macro Quant is not a machine that turns data into trades. It is a governed machine that turns time-valid Reality into defeasible state, exposes exactly where the state came from, lets competing explanations defeat each other, and only then produces a research settlement for a higher Capital Authority to judge.**

Human shorthand:

> **GitHub 管法；Evidence Plane 管事实；HF/容器做实验；Supabase 管运行时真相；Experience Plane 负责看懂；Reality 最终裁决。**
