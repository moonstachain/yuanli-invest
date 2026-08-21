# ME1 | State Object Model Reframe — Design Spec

Status: `design_candidate_for_human_review`
Date: 2026-08-22
Upstream authority: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`
Approved design sections:
- `APPROVE_ME1_A_OBJECT_IDENTITY_AUTHORITY_MODEL`
- `APPROVE_ME1_B_LIFECYCLE_VERSIONING_SETTLEMENT_ADAPTER_CONTRACT`
- `APPROVE_ME1_C_SCHEMA_CARDINALITY_VALIDATION_MIGRATION_GATE`

## 0. Purpose

ME1 compiles the ME0 ontology into a machine-governed state model that replaces the implicit legacy assumption:

`one target -> one ResearchStateVector -> one investment interpretation`

with:

`ResearchTarget -> EngineThesis[0..N] -> PositionPassport[0..N] -> BookState@PIT`

The mother distinction is:

`Target != Thesis != Capital Expression != Book Membership`

ME1 does not grant portfolio sizing, trading, execution, Registry promotion, Constitution mutation, ME2–ME5 authority, or live runtime authority.

## 1. First-principles problem

The historical `ResearchStateVector` binds `target_id` to a single object containing `P / Xs / N / V / Xa / Xp / S`. That structure is retained as historical evidence and compatibility surface, but it cannot remain the canonical write model after ME0 because ME0 freezes:

- `target_identity_does_not_determine_thesis_identity = true`
- `book_membership_is_thesis_position_specific = true`
- `return_engine_not_engine_thesis = true`
- `engine_thesis_not_position_expression = true`

Therefore ME1 is an ontology-to-object-model migration, not an additive RSV field change.

## 2. Chosen migration strategy: Compatibility Projection

ME1 adopts `Compatibility Projection`.

Historical RSV schemas, historical objects, and historical receipts remain immutable ledger facts. RSV becomes:

`legacy_authoritative_history / non_authoritative_future`

Rules:

1. Historical RSV identity and meaning are preserved.
2. RSV receives no new future canonical write authority.
3. RSV cannot automatically create `EngineThesis`.
4. New Canon may emit a read-only legacy projection for old Replay/UI consumers.
5. Legacy projection cannot write back into the new Canon.
6. Compatibility is a `Legacy Read Compatibility Plane`, not a dual-authority model.

## 3. Authority layers in ME1

ME1 instantiates ME0 L3/L4 object identities without acquiring Portfolio OS authority.

- `ResearchTarget`: target identity only.
- `EngineThesis`: governed return-mechanism thesis.
- `PositionPassport`: capital-expression contract only; not capital authorization.
- `BookState`: point-in-time book membership state; not sizing/execution authority.
- `LegacyRSVProjection`: historical-to-new compatibility object; no thesis authority.
- `LegacyRSVReadModel`: new-to-legacy projection; read-only, non-authoritative.

## 4. ResearchTarget

Stable question: `What is being researched?`

Minimum identity:

- `target_id`
- `schema_version`
- `target_type`
- `canonical_name`
- `asset_form`
- `primary_market`
- `currency`
- `identifiers`
- `active_status`
- `created_at`
- `valid_from`
- `valid_to`

Forbidden target-level semantics:

- return engine
- unique thesis
- buy/sell/hold
- target price
- position size
- book membership

Invariant: `ResearchTarget != Investment Thesis`.

Cardinality: `ResearchTarget : EngineThesis = 1 : 0..N`.

## 5. EngineThesis

Stable question: `For this target, what mechanism is expected to produce investor payoff?`

Canonical form:

`EngineThesis = Target + PrimaryEngine + Horizon + CausalMechanism + Evidence + Falsifier + PriceSemantics`

Minimum fields:

- `engine_thesis_id`
- `schema_version`
- `target_id`
- `identity_core.primary_engine`
- `identity_core.thesis_origin`
- `identity_core.opened_at`
- `research_contract.source_of_return`
- `research_contract.time_horizon`
- `research_contract.thesis_statement`
- `research_contract.causal_mechanism`
- `research_contract.price_semantics`
- `evidence.supporting_refs[]`
- `evidence.counter_refs[]`
- `evidence.capability_output_refs[]`
- `evidence.primitive_state_refs[]`
- `falsification.falsifier_refs[]`
- `falsification.challenge_conditions[]`
- lifecycle/version fields
- optional `settlement_ref`

One target may simultaneously own independent C, R, X, or future registered-engine theses.

### 5.1 Immutable identity core

After a Thesis reaches `qualified`, the following are immutable inside that thesis identity:

- `engine_thesis_id`
- `target_id`
- `primary_engine`
- `thesis_origin`
- `opened_at`

Changing `primary_engine` is not a revision; it requires a new Thesis identity and, if applicable later, a governed graduation/migration event.

### 5.2 Lifecycle

Allowed conceptual lifecycle:

`draft -> researching -> qualified -> active -> challenged -> {active | invalidated | closed}`

Additional terminal/evaluation state: `settled`.

Semantics:

- `qualified`: research threshold passed; no capital authority implied.
- `active`: thesis remains valid for research and may be referenced by a Passport.
- `challenged`: material counter-evidence exists; resolution pending.
- `invalidated`: falsifier or causal failure has been triggered.
- `closed`: intentionally ended without necessarily being falsified.
- `settled`: evaluated against later reality/outcomes.

Hard rules:

- `qualified/active/challenged` requires at least one explicit falsifier.
- `active` requires at least one evidence reference.
- `invalidated` requires invalidation reason and triggered falsifier refs.
- `settled` requires `settlement_ref`.
- no hard deletion.

### 5.3 Versioning

Revision is allowed only when thesis identity is preserved.

Required revision metadata:

- `revision`
- `supersedes_revision`
- `revision_reason`
- `as_of`
- `valid_from`
- `valid_to`

`Revision != Thesis Migration`.

A major causal-mechanism rewrite without engine change is a semantic-risk event and must trigger human review rather than silently pass as a normal revision.

## 6. PositionPassport

Stable question: `If this Thesis is capital-expressed, under what governed contract is it entered, held, reduced, exited, and settled?`

Minimum fields:

- `position_passport_id`
- `schema_version`
- `engine_thesis_id`
- redundant but validated `target_id`
- redundant but validated `primary_engine`
- expression type / instrument ref / direction semantics
- entry/add/hold/trim/exit conditions
- risk budget class / max-loss semantics / path-risk notes
- falsifier refs / settlement basis
- `graduation_allowed`
- `silent_migration_prohibited = true`
- `governed_event_required = true`
- lifecycle timestamps/state

Authority invariant:

`PositionPassport is a capital-expression contract, not capital authorization.`

Therefore every ME1 Passport must retain:

- `portfolio_weight_authority = false`
- `trade_execution_authority = false`

Cardinality: `EngineThesis : PositionPassport = 1 : 0..N`.

Lifecycle:

`draft -> eligible -> active -> reduce_only -> closed`

Additional end states: `cancelled`, `expired`.

Thesis and Passport lifecycle are intentionally decoupled. An active Thesis may have zero active Passport. If a Thesis becomes invalidated while a Passport is active, ME1 emits a fail-closed capital-expression conflict state but does not execute a trade.

## 7. BookState

Book membership belongs to PositionPassport, never directly to asset ticker or ResearchTarget.

Initial book identities:

- `BOOK-C`
- `BOOK-R`
- `BOOK-X`
- `BOOK-CASH`

`BOOK-CASH` is a liquidity-reserve role and must not require or invent `ENG-CASH`.

BookState is point-in-time and append-first, not timeless mutable truth.

Identity scope:

`portfolio_namespace + book_id + as_of`

Minimum fields:

- `book_state_id`
- `schema_version`
- `book_id`
- `portfolio_namespace`
- `as_of`
- `memberships[]`
- `survival_constraint_refs[]`
- `source_snapshot_refs[]`
- `snapshot.append_only = true`
- `snapshot.point_in_time = true`

In one `portfolio_namespace + as_of`, one active PositionPassport may have at most one primary Book.

The same ResearchTarget may indirectly appear in multiple Books through different Theses and Passports.

## 8. Minimal Book membership event

ME1 may define a minimal `PositionBookMembershipEvent` interface for assignment/removal only:

- `event_id`
- `position_passport_id`
- `from_book`
- `to_book`
- `effective_at`
- `reason`
- `authority_ref`

ME1 does not implement `AssetGraduationEvent`; R->C or other engine graduation remains deferred to ME4.

## 9. Settlement

Settlement applies to `EngineThesis`, not directly to ResearchTarget.

A target may host simultaneous Theses with different settlement outcomes.

Minimum settlement semantics:

- `settlement_id`
- `engine_thesis_id`
- evaluation window
- realized outcome
- thesis result: `supported | partially_supported | falsified | indeterminate`
- source-of-return realization
- falsifier outcome
- price path summary
- reality path summary
- benchmark refs
- replay refs
- `settled_at`

Law: `Settlement evaluates history; it never rewrites history.`

Settlement cannot mutate earlier Thesis revisions.

## 10. Research primitive and capability references

P/N/E/V/S and current/future Capability outputs are shared research primitives/services. They are referenced by EngineThesis; they are not owned by Thesis identity and must not be copied into ResearchTarget identity.

This preserves reusability across targets and engines and prevents rebuilding a new universal state vector inside EngineThesis.

## 11. Portfolio namespace

ME1 freezes `portfolio_namespace` as a state-identity dimension without creating Portfolio OS authority.

Example future namespaces may include research shadow, paper replay, model portfolio, or other governed contexts. ME1 does not define live portfolio weights or rebalance/execution behavior.

## 12. Legacy compatibility contracts

### 12.1 Legacy -> New

`Historical ResearchStateVector -> LegacyRSVProjectionAdapter -> LegacyRSVProjection`

Projection output includes:

- `legacy_projection_id`
- `source_rsv_id`
- `target_ref`
- primitive-state refs to historical P/Xs/N/V/Xa/Xp/S
- legacy force projection
- migration confidence / warnings
- `engine_assignment.status = unresolved` by default

Historical RSV cannot automatically create any active or draft EngineThesis.

A new Thesis requires a governed Engine Assignment Gate and explicit research decision.

### 12.2 New -> Legacy

New Canon may emit `LegacyRSVReadModel` for compatibility.

Required authority flags:

- `projection_only = true`
- `machine_authority = false`
- `write_back_prohibited = true`

The adapter is authority-single-direction:

`New Canon -> Legacy Read Model`

never `New Canon <-> Legacy RSV`.

## 13. Engine Assignment Gate

Legacy-to-new engine assignment is not inference-by-default.

Gate states:

- `unresolved`
- `candidate_C`
- `candidate_R`
- `candidate_X`
- `candidate_other`
- `human_review_required`
- `resolved`

Even a candidate assignment is not itself an EngineThesis. The valid migration chain is:

`Historical RSV -> Legacy Projection -> Engine Assignment Gate -> governed research decision -> EngineThesis:draft`

## 14. Schema architecture

ME1 implementation should create independent schemas for:

1. `research-target`
2. `engine-thesis`
3. `position-passport`
4. `book-state`
5. `legacy-rsv-projection`
6. `legacy-rsv-read-model`

The existing `research-state-vector.schema.json` remains unchanged in identity/meaning.

JSON Schema validates local object structure. A dedicated ME1 relational validator validates cross-object invariants.

## 15. Cardinality constitution

- `ResearchTarget : EngineThesis = 1 : 0..N`
- `EngineThesis : PositionPassport = 1 : 0..N`
- `PositionPassport : PrimaryBook = 1 : 0..1` per `portfolio_namespace + as_of`
- `ResearchTarget : Book = indirect N:N` through Passport membership

A target never belongs directly to a Book.

## 16. Relational validation contract

The ME1 validator must be fail-closed across seven rule families.

### V1 Identity Integrity

Validate unique object IDs and immutable identity core.

### V2 Reference Integrity

Validate:

- Thesis target -> valid ResearchTarget
- Passport thesis -> valid EngineThesis
- Book membership -> valid Passport
- Settlement -> valid EngineThesis

### V3 Engine Consistency

Validate:

- `Passport.target_id == Thesis.target_id`
- `Passport.primary_engine == Thesis.primary_engine`
- `BOOK-C` accepts only ENG-C Passports
- `BOOK-R` accepts only ENG-R Passports
- `BOOK-X` accepts only ENG-X Passports
- `BOOK-CASH` is a governed non-engine exception

### V4 Lifecycle Consistency

Reject, unless a separately governed reactivation mechanism exists later:

- archived Target -> new Thesis
- invalidated Thesis -> new active Passport
- settled Thesis -> new revision

### V5 No Silent Thesis Migration

Hard failure:

`same engine_thesis_id + changed primary_engine`

Human-review semantic gate:

major causal-mechanism replacement inside same identity.

### V6 Point-in-Time Integrity

Validate at minimum:

- `valid_from <= as_of`
- referenced knowledge cutoff does not exceed replay cutoff
- no future information contamination in Point-in-Time Replay

### V7 Authority Integrity

All ME1 objects must fail if any ME1-owned field grants:

- portfolio weight authority
- position sizing authority
- buy/sell/hold authority
- trade execution authority
- live execution authority
- ME2–ME5 authority

## 17. Genesis hard-negative set

The implementation must include negative tests that reject at least:

1. same Thesis identity changes ENG-R -> ENG-C
2. Passport engine differs from Thesis engine
3. BOOK-C contains ENG-R Passport
4. Legacy RSV automatically creates active EngineThesis
5. Legacy read model has write-back enabled
6. settled Thesis receives a new revision
7. invalidated Thesis creates a new active Passport
8. one active Passport occupies BOOK-C and BOOK-R in same namespace/as-of
9. BookState lacks `as_of`
10. Replay uses evidence beyond `knowledge_cutoff`
11. an ME1 object grants trading authority
12. Cash is assigned an invented `ENG-CASH`

## 18. Migration strategy

ME1 uses a staged migration.

### M1 Schema Parallel

Introduce new schemas and validators. Preserve legacy RSV consumers. No bulk data migration.

### M2 Shadow Projection

Use 3–5 historical Gold Cases, preferably the existing cross-asset set such as NVDA, Gold, UST30Y, Copper, USDJPY, to construct:

`ResearchTarget + LegacyRSVProjection`

EngineThesis creation remains explicit/governed rather than inferred.

### M3 Authority Cutover

Deferred until Replay demonstrates:

- historical truth preserved
- multi-thesis capability added
- no authority regression

ME1 may become M2 candidate-ready but does not itself perform full M3 authority cutover unless separately accepted later.

## 19. Human Review dimensions

ME1 final Human Review must reach 12/12 PASS:

- D1 Target / Thesis separation
- D2 one Target supports multiple Theses
- D3 Thesis / Passport separation
- D4 Passport / capital authorization separation
- D5 Book membership belongs to Passport, not ticker
- D6 Primary Engine immutability
- D7 No Silent Thesis Migration
- D8 PIT / revision / settlement correctness
- D9 legacy RSV historical authority preserved
- D10 legacy future write authority removed
- D11 compatibility adapter is one-way and non-polluting
- D12 no Portfolio / Trading / ME2–ME5 authority introduced

## 20. ME1 machine constitution

1. Canonical identity belongs to objects, not to one universal state vector.
2. Target-to-Thesis is one-to-many by design.
3. Primary Engine is immutable within one Thesis identity.
4. Revision is not Migration.
5. Settlement evaluates history; it never rewrites history.
6. Book membership belongs to PositionPassport, never directly to ticker or ResearchTarget.
7. BookState is Point-in-Time, not mutable timeless truth.
8. Legacy RSV preserves historical authority but has zero future canonical write authority.
9. Legacy RSV cannot automatically create EngineThesis.
10. Legacy compatibility is read-only and non-authoritative.
11. PositionPassport is a capital-expression contract, not capital authorization.
12. No ME1 schema grants portfolio sizing, trading, execution, or ME2–ME5 authority.

## 21. Scope exclusions

ME1 does not implement:

- C-specific economic value / ROIC / reinvestment schema refinement (ME2)
- X semantic split / Xa-Xp redesign (ME2)
- R engine L/ERN/N state machine or Market Clock (ME3)
- AssetGraduationEvent runtime (ME4)
- Meta Allocator (ME4)
- three-engine Gold Replay / benchmark / ablation (ME5)
- live portfolio sizing or execution
- automatic target price or buy/sell/hold recommendations
- Constitution mutation
- historical receipt rewrite

## 22. Design acceptance and next gate

This document is a design candidate only. It creates no production schema/runtime authority.

Required written design acceptance token before implementation planning:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN`

After that acceptance, the only valid next workflow is to create a separate implementation plan via the Superpowers `writing-plans` process. Acceptance of the design does not imply implementation acceptance, merge authorization, or ME2 authorization.
