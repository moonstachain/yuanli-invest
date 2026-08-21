# ME1 | Human Review Card v0.1

Status: `candidate_ready_for_human_review`

Machine qualification basis:
- exact head: `66d9478438d11c19ef86a3a96316f5553f042976`
- repository-gates Run #352 (`32510838152`)
- contracts: **SUCCESS**
- governance: **SUCCESS**
- ME1 validator: **SUCCESS**
- full unittest discovery: **SUCCESS**

## D1 | Target / Thesis separation — REVIEW
ResearchTarget identity must not imply a unique investment thesis.

## D2 | One Target supports multiple Theses — REVIEW
`RT2-NVDA` carries distinct `ET-NVDA-C-001` and `ET-NVDA-R-001` objects with independent mechanisms and falsifiers.

## D3 | Thesis / Passport separation — REVIEW
EngineThesis and PositionPassport are distinct schemas, identities and lifecycles.

## D4 | Passport / capital authorization separation — REVIEW
PositionPassport is a capital-expression contract only; portfolio weight, sizing and execution authorities are hard-false.

## D5 | Book membership belongs to Passport, not ticker — REVIEW
BOOK-C and BOOK-R contain distinct PositionPassports rather than direct NVDA target membership.

## D6 | Primary Engine immutability — REVIEW
Validator rejects primary-engine changes within one Thesis revision history.

## D7 | No Silent Thesis Migration — REVIEW
Engine change under the same `engine_thesis_id` is fail-closed; migration requires a future governed event.

## D8 | PIT / revision / settlement correctness — REVIEW
PIT distinguishes `recorded_at`, `known_as_of`, `knowledge_cutoff`, replay cutoff; settled Thesis cannot receive later revision.

## D9 | Legacy RSV historical authority preserved — REVIEW
Historical RSV schema identity remains unchanged and explicitly retains historical authority.

## D10 | Legacy future write authority removed — REVIEW
RSV and ResearchTarget v1 have `future_write_authority=false` in the semantic successor map.

## D11 | Compatibility adapter one-way and non-polluting — REVIEW
Legacy projection cannot auto-create EngineThesis; read model is projection-only, non-authoritative and write-back-prohibited.

## D12 | No Portfolio / Trading / ME2–ME5 authority introduced — REVIEW
All implementation-authority fields remain false; M3 cutover and ME2–ME5 remain unauthorized.

## D13 | ResearchTarget v2 semantic successor non-regression — REVIEW
ResearchTarget v1.0.0 remains immutable; ResearchTarget v2.0.0 is a distinct machine identity and future canonical write candidate.

## Human Decision

Required token if D1–D13 are accepted:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

Acceptance does not imply merge.
