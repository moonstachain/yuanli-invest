# ME1 | State Object Model Reframe — Design Spec

Status: `design_accepted_for_implementation_planning`
Date: 2026-08-22
Upstream authority: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`

Approved design decisions:
- `APPROVE_ME1_A_OBJECT_IDENTITY_AUTHORITY_MODEL`
- `APPROVE_ME1_B_LIFECYCLE_VERSIONING_SETTLEMENT_ADAPTER_CONTRACT`
- `APPROVE_ME1_C_SCHEMA_CARDINALITY_VALIDATION_MIGRATION_GATE`
- `APPROVE_ME1_RESEARCH_TARGET_V2_SEMANTIC_SUCCESSOR`
- `ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN`

## 0. Purpose

ME1 compiles the ME0 ontology into a machine-governed state model that replaces the implicit legacy assumption:

`one target -> one ResearchStateVector -> one investment interpretation`

with:

`ResearchTarget v2 -> EngineThesis[0..N] -> PositionPassport[0..N] -> BookState@PIT`

The mother distinction is:

`Target != Thesis != Capital Expression != Book Membership`

ME1 grants no portfolio sizing, trading, execution, Registry promotion, Constitution mutation, ME2–ME5 authority, or live runtime authority.

## 1. First-principles problem

The historical `ResearchStateVector` binds `target_id` to one object containing `P / Xs / N / V / Xa / Xp / S`. That object remains historical evidence and compatibility surface, but it cannot remain the canonical future write model after ME0 because ME0 freezes:

- `target_identity_does_not_determine_thesis_identity = true`
- `book_membership_is_thesis_position_specific = true`
- `return_engine_not_engine_thesis = true`
- `engine_thesis_not_position_expression = true`

ME1 is therefore an ontology-to-object-model migration, not an additive RSV field change.

## 2. Compatibility Projection strategy

Historical RSV schemas, objects, and receipts remain immutable ledger facts. RSV becomes:

`legacy_authoritative_history / non_authoritative_future`

Rules:
1. Historical RSV identity and meaning are preserved.
2. RSV receives zero future canonical write authority.
3. RSV cannot automatically create `EngineThesis`.
4. New Canon may emit read-only legacy projections for old Replay/UI consumers.
5. Legacy projections cannot write back into the new Canon.
6. Compatibility is a `Legacy Read Compatibility Plane`, not dual authority.

## 3. ResearchTarget v1 -> v2 semantic successor

Repository reality discovered during implementation planning: `packages/contracts/schemas/vnext/research-target.schema.json` already exists as `urn:yuanli-invest:schema:vnext-research-target:1.0.0` with historical semantics around `target_type`, `target_id`, `display_name`, `parent_target_ids`, and `tags`.

ME1 MUST NOT redefine this v1 identity in place.

Therefore ME1 freezes:

- `ResearchTarget v1.0.0` = historical / compatibility authority, immutable in identity and meaning.
- `ResearchTarget v2.0.0` = ME1 canonical future write model.
- v2 file path: `packages/contracts/schemas/vnext/research-target-v2.schema.json`.
- v2 `$id`: `urn:yuanli-invest:schema:vnext-research-target:2.0.0`.
- migration is explicit semantic succession, not in-place mutation.

Human naming may continue to say `ResearchTarget`; machine contracts MUST distinguish v1 and v2.

## 4. Authority layers in ME1

- `ResearchTarget v2`: target identity only.
- `EngineThesis`: governed return-mechanism thesis.
- `PositionPassport`: capital-expression contract only; not capital authorization.
- `BookState`: point-in-time book membership state; not sizing/execution authority.
- `LegacyRSVProjection`: historical-to-new compatibility object; no thesis authority.
- `LegacyRSVReadModel`: new-to-legacy projection; read-only, non-authoritative.

## 5. ResearchTarget v2

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

`target_type` is open-world. Known values may include equity, rate, credit, commodity, FX, crypto, index, fund, theme, industry and macro reference, but known values MUST NOT be encoded as proof of exhaustive ontology. Unknown/new types require an explicit typed extension rather than silent coercion.

Forbidden target-level semantics:
- return engine
- unique thesis
- buy/sell/hold
- target price
- position size
- book membership

Invariant: `ResearchTarget != Investment Thesis`.

Cardinality: `ResearchTarget : EngineThesis = 1 : 0..N`.

## 6. EngineThesis

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
- lifecycle/version/PIT fields
- optional `settlement_ref`

One target may simultaneously host independent C, R, X, or future registered-engine theses.

### 6.1 Engine resolution: open-world but fail-closed

ME0 freezes C/R/X as Genesis Engine Set, not exhaustive ontology.

Rules:
- `ENG-C`, `ENG-R`, `ENG-X` resolve as known Genesis engines.
- unknown engine identifiers MUST NOT be silently accepted.
- a future engine resolves only with an explicit governed engine authority reference.
- ME1 itself does not create or promote future engines.

### 6.2 Immutable identity core

After a Thesis reaches `qualified`, these fields are immutable inside that identity:
- `engine_thesis_id`
- `target_id`
- `primary_engine`
- `thesis_origin`
- `opened_at`

Changing `primary_engine` requires a new Thesis identity. Revision is not migration.

### 6.3 Lifecycle

Conceptual lifecycle:

`draft -> researching -> qualified -> active -> challenged -> {active | invalidated | closed}`

`settled` is an evaluation terminal state. Once settled, no further research revision is permitted.

Hard rules:
- `qualified/active/challenged` requires at least one explicit falsifier.
- `active` requires at least one evidence reference.
- `invalidated` requires `invalidation_reason` and `triggered_falsifier_refs`.
- `settled` requires `settlement_ref`.
- `settled` forbids additional revision.
- hard deletion is prohibited.

### 6.4 Versioning

Required revision metadata:
- `revision`
- `supersedes_revision`
- `revision_reason`
- `as_of`
- `valid_from`
- `valid_to`

A major causal-mechanism replacement inside one Thesis identity is `migration_suspected` and requires Human Review even when `primary_engine` is unchanged.

## 7. Point-in-Time and knowledge-vintage semantics

Required semantics where applicable:
- `recorded_at`: wall-clock time when system recorded the object/reference.
- `known_as_of`: latest time at which referenced information was actually knowable.
- `knowledge_cutoff`: explicit evidence cutoff for the replay/research snapshot.
- `as_of`: represented state time.
- `valid_from / valid_to`: validity interval.

Hard PIT rule for replay evidence:

`known_as_of <= knowledge_cutoff <= replay_cutoff`

`recorded_at` MUST NOT substitute for `known_as_of`.

## 8. PositionPassport

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

Every ME1 Passport retains:
- `portfolio_weight_authority = false`
- `trade_execution_authority = false`

Cardinality: `EngineThesis : PositionPassport = 1 : 0..N`.

Lifecycle:

`draft -> eligible -> active -> {reduce_only | closed}`

`reduce_only -> closed`

Additional end states: `cancelled`, `expired`.

If Thesis becomes invalidated while Passport is active, ME1 emits a fail-closed `capital_expression_conflict`; it does not execute a trade.

## 9. BookState

Book membership belongs to PositionPassport, never directly to ticker or ResearchTarget.

Initial books:
- `BOOK-C`
- `BOOK-R`
- `BOOK-X`
- `BOOK-CASH`

`BOOK-CASH` is a liquidity-reserve role and MUST NOT invent `ENG-CASH`.

BookState is point-in-time and append-first.

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

## 10. Minimal PositionBookMembershipEvent

ME1 may define assignment/removal interface only:
- `event_id`
- `position_passport_id`
- `from_book`
- `to_book`
- `effective_at`
- `reason`
- `authority_ref`

ME1 does not implement `AssetGraduationEvent`; engine graduation remains deferred to ME4.

## 11. Settlement

Settlement applies to EngineThesis, not ResearchTarget.

Minimum semantics:
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

## 12. Research primitive and capability references

P/N/E/V/S and current/future Capability outputs are shared research primitives/services. EngineThesis references them; it does not own or copy them into target identity. ME1 MUST NOT recreate a new universal state vector inside EngineThesis.

## 13. Portfolio namespace

ME1 freezes `portfolio_namespace` as a state-identity dimension without creating Portfolio OS authority. Possible future namespaces include research shadow, paper replay, model portfolio or other governed contexts. ME1 defines no live weights, rebalance, or execution behavior.

## 14. Legacy compatibility contracts

### 14.1 Legacy RSV -> New compatibility plane

`Historical ResearchStateVector -> LegacyRSVProjectionAdapter -> LegacyRSVProjection`

Projection includes:
- `legacy_projection_id`
- `source_rsv_id`
- `target_ref`
- primitive-state refs to P/Xs/N/V/Xa/Xp/S
- legacy force projection
- migration confidence / warnings
- `engine_assignment.status = unresolved` by default

Historical RSV cannot automatically create active or draft EngineThesis.

### 14.2 New -> Legacy read model

Required flags:
- `projection_only = true`
- `machine_authority = false`
- `write_back_prohibited = true`

Authority direction:

`New Canon -> Legacy Read Model`

never `New Canon <-> Legacy RSV`.

### 14.3 ResearchTarget v1 -> v2 compatibility

Existing `ResearchTarget v1.0.0` remains historical/compatibility authority. ME1 may create explicit v1->v2 adapter logic, but it MUST NOT mutate v1 objects or infer Thesis/Book semantics from v1.

The valid identity migration is:

`ResearchTarget v1 -> explicit semantic-successor mapping -> ResearchTarget v2`

No v1 field obtains new Thesis or capital authority.

## 15. Engine Assignment Gate

Gate states:
- `unresolved`
- `candidate_C`
- `candidate_R`
- `candidate_X`
- `candidate_other`
- `human_review_required`
- `resolved`

A candidate assignment is not itself a Thesis.

Valid chain:

`Historical RSV -> Legacy Projection -> Engine Assignment Gate -> governed research decision -> EngineThesis:draft`

## 16. Schema architecture

ME1 implementation creates independent schemas:
1. `research-target-v2.schema.json`
2. `engine-thesis.schema.json`
3. `position-passport.schema.json`
4. `book-state.schema.json`
5. `legacy-rsv-projection.schema.json`
6. `legacy-rsv-read-model.schema.json`

Optional minimal interface schema may be added for `position-book-membership-event` if required by relational tests.

Historical schemas remain unchanged in identity/meaning:
- `research-target.schema.json` v1.0.0
- `research-state-vector.schema.json`

JSON Schema validates local structure. A dedicated ME1 relational validator validates cross-object invariants.

## 17. Cardinality constitution

- `ResearchTarget v2 : EngineThesis = 1 : 0..N`
- `EngineThesis : PositionPassport = 1 : 0..N`
- `PositionPassport : PrimaryBook = 1 : 0..1` per `portfolio_namespace + as_of`
- `ResearchTarget : Book = indirect N:N` through Passport membership

A target never belongs directly to a Book.

## 18. Relational validation contract

ME1 validator is fail-closed across eight rule families.

### V0 Historical identity non-regression
- existing ResearchTarget v1 `$id` and field semantics remain unchanged.
- existing RSV `$id` and field semantics remain unchanged.
- v1/v2 semantic successor mapping is explicit.

### V1 Identity Integrity
Validate unique object IDs and immutable identity core.

### V2 Reference Integrity
Validate:
- Thesis target -> valid ResearchTarget v2
- Passport thesis -> valid EngineThesis
- Book membership -> valid Passport
- Settlement -> valid EngineThesis

### V3 Engine Consistency
Validate:
- `Passport.target_id == Thesis.target_id`
- `Passport.primary_engine == Thesis.primary_engine`
- `BOOK-C` only ENG-C Passports
- `BOOK-R` only ENG-R Passports
- `BOOK-X` only ENG-X Passports
- `BOOK-CASH` governed non-engine exception
- future engine requires explicit governed authority reference

### V4 Lifecycle Consistency
Reject unless separately governed later:
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
- `known_as_of <= knowledge_cutoff <= replay_cutoff`
- `recorded_at` is not substituted for `known_as_of`
- no future information contamination

### V7 Authority Integrity
Fail if any ME1-owned field grants:
- portfolio weight authority
- position sizing authority
- buy/sell/hold authority
- trade execution authority
- live execution authority
- ME2–ME5 authority

## 19. Genesis hard-negative set

Implementation MUST reject at least:
1. same Thesis identity changes ENG-R -> ENG-C
2. Passport engine differs from Thesis engine
3. BOOK-C contains ENG-R Passport
4. Legacy RSV automatically creates active EngineThesis
5. Legacy read model has write-back enabled
6. settled Thesis receives a new revision
7. invalidated Thesis creates a new active Passport
8. one active Passport occupies BOOK-C and BOOK-R in same namespace/as-of
9. BookState lacks `as_of`
10. replay uses evidence beyond `knowledge_cutoff`
11. an ME1 object grants trading authority
12. Cash is assigned invented `ENG-CASH`
13. unknown future engine is used without governed engine authority
14. `recorded_at` is treated as historical `known_as_of`
15. ResearchTarget v1 schema is redefined in place
16. v1 ResearchTarget automatically acquires Thesis or Book authority

## 20. Migration strategy

### M1 Schema Parallel
Introduce new schemas and validators. Preserve legacy RSV and ResearchTarget v1 consumers. No bulk migration.

### M2 Shadow Projection
Use 3–5 historical Gold Cases, preferably NVDA, Gold, UST30Y, Copper, USDJPY, to construct:

`ResearchTarget v2 + LegacyRSVProjection`

EngineThesis creation remains explicit/governed.

### M3 Authority Cutover
Deferred until Replay demonstrates:
- historical truth preserved
- multi-thesis capability added
- no authority regression

ME1 may become M2 candidate-ready; it does not perform full M3 cutover without later authority.

## 21. Human Review dimensions

Final ME1 Human Review requires 13/13 PASS:
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
- D11 compatibility adapter one-way and non-polluting
- D12 no Portfolio / Trading / ME2–ME5 authority introduced
- D13 ResearchTarget v1 preserved and v2 introduced as explicit semantic successor

## 22. ME1 machine constitution

1. Canonical identity belongs to objects, not one universal state vector.
2. Target-to-Thesis is one-to-many by design.
3. ResearchTarget v1 is immutable historical/compatibility authority; v2 is the ME1 future write successor.
4. Primary Engine is immutable within one Thesis identity.
5. Engine namespace is open-world but fail-closed at resolution time.
6. Revision is not Migration.
7. Settlement evaluates history; it never rewrites history.
8. Book membership belongs to PositionPassport, never directly to ticker or ResearchTarget.
9. BookState is Point-in-Time, not mutable timeless truth.
10. PIT evidence distinguishes `recorded_at`, `known_as_of`, and `knowledge_cutoff`.
11. Legacy RSV preserves historical authority but has zero future canonical write authority.
12. Legacy RSV cannot automatically create EngineThesis.
13. Legacy compatibility is read-only and non-authoritative.
14. PositionPassport is a capital-expression contract, not capital authorization.
15. No ME1 schema grants portfolio sizing, trading, execution, or ME2–ME5 authority.

## 23. Scope exclusions

ME1 does not implement:
- C-specific economic value / ROIC / reinvestment refinement (ME2)
- X semantic split / Xa-Xp redesign (ME2)
- R engine L/ERN/N state machine or Market Clock (ME3)
- AssetGraduationEvent runtime (ME4)
- Meta Allocator (ME4)
- three-engine Gold Replay / benchmark / ablation (ME5)
- live portfolio sizing or execution
- automatic target price or buy/sell/hold recommendations
- Constitution mutation
- historical receipt rewrite
- in-place mutation of ResearchTarget v1 or RSV

## 24. Self-review result

- Placeholder scan: PASS.
- Internal consistency: PASS after ResearchTarget v1/v2 semantic-successor correction.
- Scope check: PASS; one implementation plan can cover ME1 candidate without ME2–ME5.
- Ambiguity check: PASS; target and engine namespaces are open-world/fail-closed, legacy writes are prohibited, settled Thesis is non-revisionable, PIT timing fields are distinct, v1/v2 authority is explicit.

## 25. Design acceptance and next gate

Design accepted by:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN`

Accepted ResearchTarget correction:

`APPROVE_ME1_RESEARCH_TARGET_V2_SEMANTIC_SUCCESSOR`

This Design acceptance authorizes implementation planning only. It does not imply implementation acceptance, merge authorization, Registry promotion, Portfolio/Trading authority, or ME2 authorization.
