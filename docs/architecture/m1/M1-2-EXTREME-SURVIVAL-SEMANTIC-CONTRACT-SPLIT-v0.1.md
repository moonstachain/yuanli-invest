---
title: M1.2 Extreme / Survival Semantic Contract Split
version: 0.1.0
status: candidate_contract_design
portfolio: A9
base_commit: 04666a1d88183b80ad0186ac829453357d41e62a
---

# M1.2｜Extreme / Survival Semantic Contract Split v0.1

## 0. Decision

M1.2 implements the Human-accepted M1.1 ontology without modifying legacy v1.0 objects in place.

The split is:

```text
Asset Intelligence
P Paradigm
N Narrative
X Extreme
  ├─ Xs Structural Right Tail
  ├─ Xa Tail Activation
  └─ Xp Payoff Convexity
V Valuation Context
Issuer Durability
        ↓
Force Asset Snapshot

Portfolio Intelligence
Portfolio exposures + distributions + liquidity + stress
        ↓
S Portfolio Survival & Growth
```

## 1. Core semantic correction

Legacy `ConvexityProfile` mixes right-tail value capture and issuer-level left-tail fragility. Legacy `ForceTriangleSnapshot.survival_gate` is also issuer-level. M1.2 does not reinterpret those fields silently.

Instead:

- `StructuralRightTailProfile` owns Xs;
- `TailActivationSnapshot` owns Xa;
- `PayoffConvexityContext` owns Xp;
- `IssuerDurabilityGate` owns company/thesis survival;
- `ValuationContext` owns V;
- `ForceAssetSnapshot` assembles asset-level intelligence;
- `PortfolioSurvivalPolicy` and `PortfolioSurvivalSnapshot` own S.

## 2. Compatibility rule

Legacy v1.0 remains readable and replayable.

```text
ConvexityProfile.right_tail        -> candidate Xs source
ConvexityProfile.left_tail         -> candidate IssuerDurability source
ForceTriangleSnapshot.survival_gate-> legacy issuer-survival signal only
```

No legacy `survival_gate` may be re-labelled as Portfolio Survival.

Historical Replays keep their existing object references until an explicit migration Replay is created.

## 3. Candidate contract locations

M1.2 candidate schemas live under:

`docs/architecture/m1/contracts/`

They are NOT registered in `packages/contracts/schemas/` and therefore are not production Canon contracts yet.

## 4. Asset-level contract stack

### 4.1 Xs｜StructuralRightTailProfile

Question: if the paradigm succeeds, can value concentrate disproportionately in this subject?

Required surfaces:

- winner_take_most
- network_effects
- scale_economics
- bottleneck_control
- platform_optionality
- market_expansion
- value_capture

### 4.2 Xa｜TailActivationSnapshot

Question: is the conditional probability of a defined tail outcome changing?

Must expose:

- tail type and horizon;
- unconditional base rate where available;
- conditional probability estimate where available;
- probability delta;
- leading-factor references;
- causal status = `predictive | causal_candidate | identified | unknown`;
- calibration state;
- explicit unknowns.

`predictive != causal` is a hard invariant.

### 4.3 Xp｜PayoffConvexityContext

Question: given the asset thesis and current price context, what is the payoff geometry?

It describes asymmetry and embedded cost; it does not emit a trade, target price or position size.

### 4.4 IssuerDurabilityGate

Question: can the issuer/thesis survive long enough to be tested?

Covers balance sheet, refinancing, dilution, concentration, regulatory ruin and technical obsolescence.

This is NOT Portfolio Survival.

### 4.5 ValuationContext

V is `Strike / Price of Optionality`, not a fourth P/N/X vertex and not a scalar Force score.

### 4.6 ForceAssetSnapshot

Asset-level assembly only:

`P + N + Xs + Xa + Xp + V + IssuerDurability + Evidence`

It intentionally contains no Portfolio Survival object and no sizing output.

## 5. Portfolio-level S contracts

### 5.1 PortfolioSurvivalPolicy

Defines constraints, not recommendations:

- ruin boundary;
- drawdown / ES / leverage / liquidity limits;
- allowed sizing methodology classes;
- model-uncertainty policy;
- crisis-correlation / stress requirements.

### 5.2 PortfolioSurvivalSnapshot

Evaluates an already-specified paper/shadow portfolio against the policy.

It may report:

- `robust | acceptable | fragile | breached | unknown`;
- ruin-probability estimate if modelled;
- ES / drawdown / liquidity / leverage / stress states;
- model confidence and breaches.

It may NOT output proposed target weights, buy/sell actions or personalized allocation.

## 6. Governance boundary

M1.2 may:

- define candidate schemas;
- define deterministic validators;
- create compatibility fixtures;
- prepare M1.3 Replay/Eval migration work.

M1.2 may NOT:

- overwrite legacy v1.0 schemas;
- migrate historical Canon objects silently;
- generate new Q1 Force states;
- authorize production ingestion;
- switch A9 operational canon;
- modify RSI FROZEN;
- emit live trade, target price or position sizing.

## 7. Exit gate

M1.2 is ready for Human Review only when:

1. all candidate schemas validate;
2. Xs/Xa/Xp are separable by contract;
3. Issuer Durability and Portfolio Survival cannot be confused by field name or object type;
4. ForceAssetSnapshot contains no portfolio-survival or action fields;
5. legacy v1.0 remains unchanged;
6. CI passes;
7. compatibility mapping is documented.

Accepted follow-on would be:

`M1.3｜PNX-S Replay / Eval v2`
