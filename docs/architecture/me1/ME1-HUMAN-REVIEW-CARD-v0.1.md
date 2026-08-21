# ME1 | Human Review Card v0.1

Status: `human_accepted_pending_post_acceptance_ci`

Reviewed candidate:
- exact head: `dc2c41b4499871336aafc62100a126ce8cab1475`
- repository-gates Run #353 (`32510936828`)
- contracts: **SUCCESS**
- governance: **SUCCESS**
- ME1 validator: **SUCCESS**
- full unittest discovery: **SUCCESS**

Human decision:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

Formal review: **13/13 PASS**

## D1 | Target / Thesis separation — ACCEPTED
ResearchTarget identity does not imply a unique investment thesis.

## D2 | One Target supports multiple Theses — ACCEPTED
`RT2-NVDA` carries distinct `ET-NVDA-C-001` and `ET-NVDA-R-001` objects with independent mechanisms and falsifiers.

## D3 | Thesis / Passport separation — ACCEPTED
EngineThesis and PositionPassport remain distinct schemas, identities and lifecycles.

## D4 | Passport / capital authorization separation — ACCEPTED
PositionPassport is a capital-expression contract only; portfolio weight, sizing and execution authorities remain hard-false.

## D5 | Book membership belongs to Passport, not ticker — ACCEPTED
BOOK-C and BOOK-R contain distinct PositionPassports rather than direct NVDA target membership.

## D6 | Primary Engine immutability — ACCEPTED
Primary-engine changes within one Thesis identity are fail-closed.

## D7 | No Silent Thesis Migration — ACCEPTED
Engine change requires a new Thesis identity and a separately governed migration/graduation event.

## D8 | PIT / revision / settlement correctness — ACCEPTED
PIT distinguishes `recorded_at`, `known_as_of`, `knowledge_cutoff`, replay cutoff; settled Thesis cannot receive later revision.

## D9 | Legacy RSV historical authority preserved — ACCEPTED
Historical RSV schema identity remains immutable historical authority.

## D10 | Legacy future write authority removed — ACCEPTED
RSV and ResearchTarget v1 have zero future canonical write authority.

## D11 | Compatibility adapter one-way and non-polluting — ACCEPTED
Legacy projection cannot auto-create EngineThesis; legacy read model is projection-only, non-authoritative and write-back-prohibited.

## D12 | No Portfolio / Trading / ME2–ME5 authority introduced — ACCEPTED
Portfolio sizing, buy/sell/hold, trading, execution, Registry promotion, Constitution mutation, M3 cutover and ME2–ME5 remain unauthorized.

## D13 | ResearchTarget v2 semantic successor non-regression — ACCEPTED
ResearchTarget v1.0.0 remains immutable; ResearchTarget v2.0.0 is a distinct semantic successor.

## Next gate

`ME1_POST_ACCEPTANCE_CI`

Acceptance does not imply merge.

Required merge authorization, if later desired:

`AUTHORIZE_ME1_MERGE`
