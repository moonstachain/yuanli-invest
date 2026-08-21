# ME1 | State Object Model Authority Freeze v0.1

Status: `candidate_started`
Upstream: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`

## Mother distinction

`ResearchTarget != EngineThesis != PositionPassport != BookState`

ME1 compiles the ME0 ontology into a machine-checkable state-object candidate. It does not grant portfolio sizing, buy/sell/hold, trading, live execution, Registry promotion, Constitution mutation, or ME2–ME5 authority.

## Canonical object chain

`ResearchTarget v2 -> EngineThesis[0..N] -> PositionPassport[0..N] -> BookState@PIT`

### ResearchTarget v2
Target identity only. Existing ResearchTarget v1.0.0 remains immutable historical/compatibility authority. v2 is an explicit semantic successor, not an in-place rewrite.

### EngineThesis
Return-mechanism thesis authority only. One target may host multiple independent theses. Primary engine is immutable inside one qualified thesis identity.

### PositionPassport
Capital-expression contract only. It does not authorize capital allocation or execution.

### BookState
Point-in-time membership state. Membership belongs to PositionPassport, never directly to ticker or ResearchTarget.

## Historical compatibility

`ResearchTarget v1` and `ResearchStateVector v1` preserve historical authority. Neither has future canonical write authority after ME1 acceptance. Legacy RSV may project into a non-authoritative compatibility object, but it cannot automatically create EngineThesis and cannot write back into the new Canon.

## Core invariants

1. `Target != Thesis != Capital Expression != Book Membership`.
2. `ResearchTarget v2 : EngineThesis = 1 : 0..N`.
3. `EngineThesis : PositionPassport = 1 : 0..N`.
4. Primary engine is immutable within one thesis identity.
5. `Revision != Thesis Migration`.
6. Settlement evaluates history; it never rewrites history.
7. BookState is Point-in-Time and append-first.
8. `BOOK-CASH` is a liquidity reserve, never `ENG-CASH`.
9. Legacy compatibility is read-only and non-authoritative.
10. PIT research distinguishes `recorded_at`, `known_as_of`, `knowledge_cutoff`, and replay cutoff.
11. Engine namespace is open-world but resolution is fail-closed.
12. No ME1 object grants portfolio/trading/runtime authority.
13. Historical schema identities are immutable; successors are explicit.

## Migration boundary

ME1 may reach `M1 Schema Parallel` and `M2 Shadow Projection candidate-ready`. Full `M3 Authority Cutover` remains not authorized until separately accepted after Replay/qualification.

## Human gate

Future acceptance token:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

Acceptance does not imply merge.
