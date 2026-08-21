# ME1 | Human Review Card v0.1

Status: `candidate_started`

This card is the future Human Gate for `ME1_STATE_OBJECT_MODEL_REFRAME`.

## D1 | Target / Thesis separation
ResearchTarget identity must not imply a unique investment thesis.

## D2 | One Target supports multiple Theses
A single ResearchTarget v2 may host independent C, R, X, or future governed-engine theses.

## D3 | Thesis / Passport separation
EngineThesis and PositionPassport remain distinct identities and lifecycles.

## D4 | Passport / capital authorization separation
PositionPassport is a capital-expression contract only; no position sizing or execution authority is implied.

## D5 | Book membership belongs to Passport, not ticker
ResearchTarget never belongs directly to a Book; Book membership is PositionPassport-specific and PIT-scoped.

## D6 | Primary Engine immutability
Within one qualified EngineThesis identity, `primary_engine` cannot be revised in place.

## D7 | No Silent Thesis Migration
An engine change requires a new Thesis identity and a future governed migration/graduation event.

## D8 | PIT / revision / settlement correctness
Revision preserves thesis identity; settlement evaluates history without rewriting it; PIT distinguishes knowledge vintage from recording time.

## D9 | Legacy RSV historical authority preserved
Historical ResearchStateVector identity and meaning remain immutable ledger facts.

## D10 | Legacy future write authority removed
Legacy RSV and ResearchTarget v1 receive no future canonical write authority.

## D11 | Compatibility adapter one-way and non-polluting
Legacy compatibility is read-only; RSV cannot auto-create EngineThesis and no legacy write-back into new Canon is allowed.

## D12 | No Portfolio / Trading / ME2–ME5 authority introduced
ME1 must not acquire portfolio sizing, buy/sell/hold, trading, execution, Registry promotion, Constitution mutation, or successor-stage authority.

## D13 | ResearchTarget v2 semantic successor non-regression
ResearchTarget v1.0.0 remains immutable; ResearchTarget v2.0.0 is an explicit semantic successor with new canonical write semantics rather than an in-place redefinition.

## Required Human Decision

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

Acceptance does not imply merge.
