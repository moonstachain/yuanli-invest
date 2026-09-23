# YMQ-OS0｜Canonical Research Object Model v0.1

**Stage:** `YMQ-OS0-G0`  
**Status:** `IMPLEMENTATION_CANDIDATE / NOT_CANON`

## 1｜Why nine objects

The object model separates evidence, observation, transformation, state, transmission, claim, execution-of-research, settlement and learning so that no dashboard or model output can silently become Truth or action authority.

```text
SourceSnapshot
  ↓
ObservationPIT
  ↓
FeaturePIT
  ↓
StatePIT ↔ TransmissionEdgePIT
  ↓
ResearchClaim
  ↓
CapabilityRun
  ↓
ResearchSettlement
  ↓
LearningDelta
```

## 2｜O1 SourceSnapshot

Immutable evidence payload identity. Minimum semantics include source identity/authority/class, canonical locator, retrieval time, content SHA-256, storage locator, license class and runner Git SHA.

**Invariant:** supersession creates a new snapshot identity/hash; an old snapshot is never silently mutated.

## 3｜O2 ObservationPIT

A fact/value known at a historical boundary. It distinguishes observation, release, vintage and `known_as_of` time and binds to a SourceSnapshot.

**Invariant:** replay at `T0` may consume only `known_as_of <= T0`; `UNKNOWN` is denied for high-authority PIT claims.

## 4｜O3 FeaturePIT

A reproducible transformation of PIT-qualified observations. It binds feature-definition version, input observation references, transform Git SHA, lookback, normalization rule and as-of boundary.

**Invariant:** no future observation or future normalization statistic may enter a feature.

## 5｜O4 StatePIT

A structured estimate of the world at `T0`. State retains feature refs, method version, state payload, uncertainty and explicit unknown fields.

**Invariant:** a projection cannot strengthen unknown/uncertain state into stronger Reality.

## 6｜O5 TransmissionEdgePIT

A time-bounded relationship estimate or hypothesis from a state/driver to another state/asset. It retains method, effect/coefficient, uncertainty/evidence and stability window.

**Invariant:** time-varying transmission is state, not permanent law; `permanent_beta_claim=false` is explicit.

## 7｜O6 ResearchClaim

A defeasible claim with statement, evidence refs, evidence authority, claim authority, falsifier and expiry/review rule.

**Invariant:** `ClaimAuthority <= EvidenceAuthority`; every claim remains defeasible.

## 8｜O7 CapabilityRun

One reproducible invocation of a frozen research capability. It binds battle/capability/version, exact Git SHA, panel/source revision, parameter contract, runner identity, timing and artifact hashes.

**Invariant:** a result without an exact run identity cannot enter scientific settlement.

## 9｜O8 ResearchSettlement

The immutable research settlement separates:

- physical status — what actually ran;
- scientific status — what the experiment learned;
- authority status — what may legally happen next.

It also preserves baseline, hard-negative, ablation results, limitations and the next authorized stage.

**Invariant:** one catch-all `PASS` cannot replace the three axes. `PHYSICAL_PASS / SCIENTIFIC_NO_GO` is valid.

## 10｜O9 LearningDelta

A forward-only change proposal created from a ResearchSettlement. It names the affected future capability/contract, evidence basis, proposed change and Human-review requirement.

**Invariant:** LearningDelta cannot rewrite past Evidence or Settlement; any change to future law requires GitHub review/admission.

## 11｜Derived projections are not canonical objects

DecisionPacket, DashboardCard, Alert, StateSummary and PortfolioSuggestion may be generated from canonical objects, but their existence grants no additional evidence, Capital or Execution authority.

## 12｜Schema authority

The machine schemas live under `packages/contracts/schemas/ymq/`. This document explains them for Human review and cannot grant fields or authority absent from those schemas and the machine contract.
