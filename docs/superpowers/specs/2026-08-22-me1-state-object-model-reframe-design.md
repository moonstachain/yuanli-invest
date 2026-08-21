# ME1 | State Object Model Reframe — Design Spec

Status: `design_accepted_for_implementation_planning`
Date: 2026-08-22
Upstream authority: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`
Approved design sections:
- `APPROVE_ME1_A_OBJECT_IDENTITY_AUTHORITY_MODEL`
- `APPROVE_ME1_B_LIFECYCLE_VERSIONING_SETTLEMENT_ADAPTER_CONTRACT`
- `APPROVE_ME1_C_SCHEMA_CARDINALITY_VALIDATION_MIGRATION_GATE`
- `APPROVE_ME1_RESEARCH_TARGET_V2_SEMANTIC_SUCCESSOR`
- `ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN`

## 0. Purpose

ME1 compiles ME0 into a machine-governed state model:

`ResearchTarget v2 -> EngineThesis[0..N] -> PositionPassport[0..N] -> BookState@PIT`

The mother distinction is:

`Target != Thesis != Capital Expression != Book Membership`

ME1 grants no portfolio sizing, trading, execution, Registry promotion, Constitution mutation, ME2–ME5 authority, or live runtime authority.

## 1. Compatibility Projection

Historical identities are immutable. Existing `ResearchStateVector v1` and `ResearchTarget v1` retain historical/compatibility authority but have zero future canonical write authority.

Rules:
1. no in-place semantic rewrite;
2. no automatic RSV -> EngineThesis inference;
3. new Canon may emit read-only legacy projections;
4. legacy projection cannot write back into new Canon;
5. compatibility is a Legacy Read Compatibility Plane, not a dual-authority model.

## 2. ResearchTarget v1 -> v2 semantic successor

Existing machine identity:

`urn:yuanli-invest:schema:vnext-research-target:1.0.0`

remains immutable with its accepted historical semantics.

ME1 introduces:

`urn:yuanli-invest:schema:vnext-research-target:2.0.0`

as an explicit semantic successor and future canonical write model. Human-facing concept name remains `ResearchTarget`; machine identity is version-separated.

ResearchTarget v2 answers only `What is being researched?` and cannot carry unique-thesis, return-engine, buy/sell/hold, target-price, position-size, or book-membership semantics.

Known target types are open-world; new types require explicit typed extension rather than silent coercion.

## 3. EngineThesis

`EngineThesis = Target + PrimaryEngine + Horizon + CausalMechanism + Evidence + Falsifier + PriceSemantics`.

One target may host independent C, R, X, or future governed-engine theses.

Engine namespace is open-world but fail-closed:
- ENG-C / ENG-R / ENG-X resolve as Genesis Engines;
- unknown engine IDs fail unless accompanied by explicit governed authority reference;
- ME1 cannot create or promote future engines.

After `qualified`, the thesis identity core is immutable: `engine_thesis_id`, `target_id`, `primary_engine`, `thesis_origin`, `opened_at`.

Lifecycle: `draft -> researching -> qualified -> active -> challenged -> {active | invalidated | closed}`, with `settled` as non-revisionable evaluation terminal state.

`Revision != Thesis Migration`.

## 4. PIT semantics

ME1 distinguishes:
- `recorded_at`: when the system recorded the object;
- `known_as_of`: when information was actually knowable;
- `knowledge_cutoff`: evidence cutoff for a replay/research snapshot;
- `as_of`: represented state time;
- `valid_from / valid_to`: validity interval.

PIT invariant for replay evidence:

`known_as_of <= knowledge_cutoff <= replay_cutoff`.

`recorded_at` must never substitute for `known_as_of`.

## 5. PositionPassport

PositionPassport is a capital-expression contract, not capital authorization.

It references exactly one EngineThesis and redundantly carries `target_id` and `primary_engine`; relational validation requires both to match the referenced Thesis.

It includes entry/add/hold/trim/exit conditions, risk semantics, falsifier refs, settlement basis, and the hard invariants:

`silent_migration_prohibited = true`

`governed_event_required = true`

All portfolio-weight/trade-execution authorities remain false.

## 6. BookState

Book membership belongs to PositionPassport, never directly to ticker or ResearchTarget.

Initial Book namespace: `BOOK-C`, `BOOK-R`, `BOOK-X`, `BOOK-CASH`.

`BOOK-CASH` is a non-engine liquidity reserve and must never create `ENG-CASH`.

BookState is Point-in-Time and append-first. Identity scope is `portfolio_namespace + book_id + as_of`.

One active PositionPassport may occupy at most one primary Book per namespace/as-of. The same ResearchTarget may appear indirectly in multiple Books through distinct Theses and Passports.

## 7. Compatibility contracts

Legacy -> New:

`Historical RSV -> LegacyRSVProjectionAdapter -> LegacyRSVProjection`

Engine assignment defaults to `unresolved`. A governed Engine Assignment Gate is required before any EngineThesis:draft may be created.

New -> Legacy:

`New Canon -> LegacyRSVReadModel`

with `projection_only=true`, `machine_authority=false`, `write_back_prohibited=true`.

## 8. Schema architecture

ME1 implementation creates:
1. `research-target-v2.schema.json`
2. `engine-thesis.schema.json`
3. `position-passport.schema.json`
4. `book-state.schema.json`
5. `legacy-rsv-projection.schema.json`
6. `legacy-rsv-read-model.schema.json`

Existing `research-target.schema.json` v1 and `research-state-vector.schema.json` remain unchanged in identity and meaning.

Local JSON Schema validates object shape. A dedicated relational validator enforces cross-object invariants.

## 9. Cardinality

- `ResearchTarget v2 : EngineThesis = 1 : 0..N`
- `EngineThesis : PositionPassport = 1 : 0..N`
- `PositionPassport : PrimaryBook = 1 : 0..1` per `portfolio_namespace + as_of`
- `ResearchTarget : Book = indirect N:N`

## 10. Relational validation

V0 Historical non-regression.
V1 Identity integrity.
V2 Reference integrity.
V3 Engine consistency.
V4 Lifecycle consistency.
V5 No Silent Thesis Migration.
V6 Point-in-Time integrity.
V7 Authority integrity.

Hard failures include engine mutation inside same Thesis ID, Passport/Thesis mismatch, wrong-engine Book membership, legacy write-back, automatic RSV->Thesis creation, settled revision, invalidated Thesis creating active Passport, duplicate primary Book membership, future-knowledge contamination, trading authority, ENG-CASH, unknown engine without authority, and ResearchTarget v1 redefinition.

## 11. Migration strategy

M1 Schema Parallel: new schemas/validators alongside legacy objects; no bulk migration.

M2 Shadow Projection: use cross-asset historical cases (NVDA, Gold, UST30Y, Copper, USDJPY) to prove structural compatibility and multi-thesis cardinality. EngineThesis creation remains explicit/governed.

M3 Authority Cutover: not authorized in ME1 candidate implementation; requires later replay evidence and separate Human acceptance.

## 12. Human Review dimensions

D1 Target / Thesis separation.
D2 One Target supports multiple Theses.
D3 Thesis / Passport separation.
D4 Passport / capital authorization separation.
D5 Book membership belongs to Passport, not ticker.
D6 Primary Engine immutability.
D7 No Silent Thesis Migration.
D8 PIT / revision / settlement correctness.
D9 Legacy RSV historical authority preserved.
D10 Legacy future write authority removed.
D11 Compatibility adapter is one-way and non-polluting.
D12 No Portfolio / Trading / ME2–ME5 authority introduced.
D13 ResearchTarget v1 remains immutable and v2 is an explicit semantic successor.

Final Human Review requires 13/13 PASS.

## 13. Machine constitution

1. Canonical identity belongs to objects, not one universal state vector.
2. Target-to-Thesis is one-to-many by design.
3. Primary Engine is immutable within one Thesis identity.
4. Engine namespace is open-world but fail-closed at resolution time.
5. Revision is not Migration.
6. Settlement evaluates history; it never rewrites history.
7. Book membership belongs to PositionPassport.
8. BookState is Point-in-Time.
9. PIT distinguishes recorded time from historical knowledge availability.
10. Legacy RSV preserves historical authority but has zero future canonical write authority.
11. Legacy RSV cannot automatically create EngineThesis.
12. Legacy compatibility is read-only and non-authoritative.
13. PositionPassport is a capital-expression contract, not capital authorization.
14. ResearchTarget v1 is immutable; v2 is its semantic successor.
15. No ME1 schema grants portfolio sizing, trading, execution, or ME2–ME5 authority.

## 14. Scope exclusions

ME1 does not implement C-specific economic refinement, X semantic split, R Market Clock state machine, AssetGraduationEvent runtime, Meta Allocator, ME5 Gold Replay benchmark/ablation, live portfolio sizing/execution, target-price automation, Constitution mutation, historical receipt rewrite, or M3 authority cutover.

## 15. Design acceptance

Accepted design token:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN`

Implementation planning and execution remain separately governed. Design acceptance does not imply implementation acceptance, merge authorization, or ME2 authorization.
