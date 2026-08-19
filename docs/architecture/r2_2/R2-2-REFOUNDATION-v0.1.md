# R2.2 | Yuanli Investment Research Intelligence Canon Re-foundation v0.1

## Purpose

R2.2 performs a semantic re-foundation before R3A runtime implementation.

It does not erase R0-R2 history. It installs a higher semantic authority so future runtime code is compiled against the OS vNext ontology rather than against legacy asset-centric or score-centric assumptions.

## Decisions proposed

1. Upgrade repository identity from `Research Capability Canon` to **Investment Research Intelligence Canon** while retaining `ResearchCapability` as the durable compounding unit.
2. Freeze **一核 · 三界 · 三门 · 一环** as the top-level OS model.
3. Replace scalar/label-centric target state with candidate `ResearchStateVector`.
4. Make `E` horizontal through `EvidenceClaim`.
5. Freeze `P → Xs → N → V → Xa → Xp → S` as a research dependency graph, not a universal causal law.
6. Demote Force classifications to projections.
7. Freeze `Receipt = Ledger; Status = Projection`.
8. Replace transport-specific API semantics with transport-neutral invocation/result/receipt contracts.
9. Keep current 12 Gold objects immutable; perform any capability successor migration separately in R2.3.
10. Keep R3A paused until this semantic gate is Human Accepted and merged.

## Candidate vNext contracts

- ResearchTarget
- CanonicalObservation
- EvidenceClaim
- ResearchStateVector
- CapabilityInvocation
- CapabilityInputBundle
- CapabilityResult
- ExecutionReceipt
- FutureSettlement
- CapabilityRevision

All are candidate contracts under `packages/contracts/schemas/vnext/`; none are production registry admissions.

## Explicit non-changes

R2.2 does not:
- rename or mutate existing Gold IDs;
- create the V/S successor capability IDs;
- implement Wind provider adapters;
- implement R3A vertical slices;
- execute R4A benchmarks;
- admit Evidence or Outcome;
- switch the A9 operational canon;
- modify RSI FROZEN;
- authorize trading or live execution.

## Exit gate

After exact-head repository gates pass, perform a dedicated Human Review.

Decision token if accepted:

`ACCEPT_R2_2_RESEARCH_INTELLIGENCE_CANON_REFOUNDATION`

Acceptance authorizes only merge of the R2.2 semantic package and then R2.3 object/gold migration design. R3A remains downstream of the migration decision.
