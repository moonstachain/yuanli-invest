# YMA55-H1｜Five-Layer Decision Kernel Freeze — Design Spec

**Status:** `design_candidate_for_human_review`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Base:** `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
**Program role:** YMA55 causal historical-prior hardening  
**Capital / trading authority:** none

## 0. Purpose

YMA55-H1 freezes a **human five-layer decision kernel** while preserving a more expressive machine ontology underneath it.

The goal is not to simplify reality by deleting machine distinctions. The goal is to reduce human-facing cognitive load while preserving the accepted ME0 principle:

> Human compression may navigate machine state; it may not erase independent return mechanisms.

H1 therefore freezes two simultaneous representations:

```text
Human Decision Kernel
WORLD → CONSTRAINT → TRANSMISSION → MECHANISM → SETTLEMENT
```

and:

```text
Machine Causal Chain
HistoricalEpoch
→ MacroRealityState
→ StructuralConstraint
→ PolicyReactionFunction
→ FinancialTransmission
→ MacroReturnMechanism
→ EngineThesis(C/R/X)
→ AssetInstrumentExpression
→ PathPayoffSurvival
→ RealitySettlement
```

These two representations are compatible but **not identical**.

---

## 1. Authority boundary

H1 is downstream of accepted philosophy / methodology / engine authority.

```text
YIP0 Philosophy Authority
        ↓
OS / YIM0 Human Research Grammar & Projection
        ↓
ME0 Return Engine Ontology
        ↓
ME1 State Object Model
        ↓
YMA55-H1 Historical-Prior Decision Kernel Projection + Domain Ontology
```

H1 does **not**:

- mutate YIP0 philosophical law;
- redefine historical P/N/E/V/S identities;
- close the ME0 engine registry;
- turn a human five-layer map into the unique machine ontology;
- grant Portfolio OS, position-sizing, trading or execution authority;
- authorize ME2–ME5 or any M3 cutover;
- make a historical analogy sufficient for a capital action.

H1 is allowed to define **YMA55 domain objects** required to represent historical-prior reasoning, provided those objects remain subordinate to existing authority boundaries.

---

## 2. Human five-layer kernel

### 2.1 WORLD｜世界

Stable question:

> What institutional world and current reality state are we actually in?

Human meaning:

`制度背景 × 现实状态`

Machine inputs:

- `HistoricalEpoch`
- `MacroRealityState`

WORLD is descriptive. It must not directly imply an asset, engine or position.

Forbidden shortcut:

`WORLD → Position`

### 2.2 CONSTRAINT｜约束

Stable question:

> What is becoming binding now?

A valid constraint must state:

1. the constrained actor/system;
2. the constrained resource / policy freedom / balance-sheet capacity;
3. observable evidence of bindingness;
4. evidence that would show the constraint is easing;
5. time horizon.

Examples include fiscal, inflation, funding, external-balance, energy, supply, institutional or geopolitical constraints.

A broad story such as `empire decline` is not itself a valid machine constraint until translated into an observable constraint such as fiscal capacity, external funding dependence or policy-set restriction.

### 2.3 TRANSMISSION｜传导

Stable question:

> Who must react, and through what financial channel does the constraint reach prices?

Machine inputs:

- `PolicyReactionFunction`
- `FinancialTransmission`

Canonical transmission surface may include:

- policy rate;
- real rate;
- yield curve;
- term premium;
- inflation breakeven;
- credit spread;
- funding conditions;
- FX / cross-currency basis;
- market risk capacity / risk premium.

The system must not collapse all transmission into one universal `interest-rate factor`.

### 2.4 MECHANISM｜机制

Stable question:

> What mechanism is capital being paid for?

Machine inputs:

- `MacroReturnMechanism`
- `EngineThesis`

Genesis macro return-mechanism families:

- `MRM-P | Productivity`
- `MRM-D | Duration`
- `MRM-CA | Carry`
- `MRM-CR | Credit`
- `MRM-SC | Scarcity`
- `MRM-RS | Relative Sovereignty`

These are **domain mechanism families**, not replacements for ME0 return-engine authority.

Each mechanism may translate into one or more separately versioned ME0 engine theses:

- `ENG-C | Compounding`
- `ENG-R | Reflexive Repricing`
- `ENG-X | Convexity`

Invariant:

`MacroReturnMechanism != ReturnEngine`

### 2.5 SETTLEMENT｜现实裁决

Stable question:

> What did reality eventually confirm, contradict or leave unresolved?

Machine inputs:

- `AssetInstrumentExpression`
- `PathPayoffSurvival`
- `RealitySettlement`

Settlement must distinguish at least:

- right mechanism / right outcome;
- right mechanism / wrong expression;
- wrong mechanism / lucky outcome;
- wrong mechanism / wrong outcome;
- unresolved.

Settlement is not a synonym for realized P&L. A profitable outcome under the wrong mechanism is explicitly not treated as epistemic success.

---

## 3. Frozen machine ontology

### 3.1 HistoricalEpoch

Role: institutional context only.

Required fields:

- `epoch_id`
- `start_date`
- `end_date`
- `monetary_regime`
- `fiscal_regime`
- `global_order`
- `market_structure`
- `policy_toolkit`
- `evidence_refs`

No timing or direct-position authority.

### 3.2 MacroRealityState

Role: dynamic state vector.

Canonical dimensions:

- `G | Growth`
- `I | Inflation`
- `L | Liquidity`
- `C | Credit`
- `F | Fiscal`
- `B | External Balance`

Each dimension must support:

- `level`
- `direction`
- `acceleration`
- `surprise`
- `persistence`
- `evidence_refs`

H1 deliberately freezes **change over level** as a first-class semantic requirement.

### 3.3 StructuralConstraint

Required fields:

- `constraint_id`
- `constraint_type`
- `bound_actor`
- `binding_resource_or_freedom`
- `binding_evidence`
- `easing_evidence`
- `horizon`
- `confidence_band`

### 3.4 PolicyReactionFunction

Required fields:

- `reaction_id`
- `constraint_id`
- `feasible_policy_set`
- `observed_reaction`
- `alternative_reactions`
- `political_or_institutional_limits`
- `evidence_refs`

### 3.5 FinancialTransmission

Required fields:

- `transmission_id`
- `reaction_id`
- `channels`
- `expected_sequence`
- `expected_signs`
- `lead_lag_expectations`
- `break_conditions`

### 3.6 MacroReturnMechanism

Required fields:

- `mechanism_id`
- `mechanism_family`
- `source_of_return`
- `required_conditions`
- `disconfirming_conditions`
- `typical_horizon_band`

### 3.7 EngineThesis

H1 reuses ME1/ME0 authority: target identity does not determine thesis identity.

YMA55 may reference an `EngineThesis`; it may not silently migrate an R thesis into C or X.

### 3.8 AssetInstrumentExpression

Required distinction:

`asset != instrument != thesis`

Expression records how a thesis would be represented for research purposes. Actual sizing and execution remain outside YMA55 authority.

### 3.9 PathPayoffSurvival

Must record:

- expected horizon;
- expected path risk;
- MAE / adverse path expectations where evidence permits;
- liquidity / funding constraints;
- survival breaker.

### 3.10 RealitySettlement

Must be append-only in historical semantics: later knowledge may add a settlement record but may not rewrite the original PIT thesis.

---

## 4. Human-to-machine projection map

| Human layer | Machine objects | Human question |
|---|---|---|
| WORLD | HistoricalEpoch + MacroRealityState | 世界是什么、正在怎样变化？ |
| CONSTRAINT | StructuralConstraint | 什么正在变成 Binding？ |
| TRANSMISSION | PolicyReactionFunction + FinancialTransmission | 谁被迫反应，怎样传入价格？ |
| MECHANISM | MacroReturnMechanism + EngineThesis | 资本为什么机制付钱？ |
| SETTLEMENT | Expression + Path/Payoff/Survival + RealitySettlement | 如何表达，最终现实如何裁决？ |

Projection law:

> A human layer may aggregate several machine objects, but no machine object may be silently deleted or semantically rewritten merely to make the human map simpler.

---

## 5. Core invariants

1. `HumanKernel != MachineOntology`
2. `HistoricalEpoch != MacroRealityState`
3. `WorldState != Constraint`
4. `Constraint != Transmission`
5. `Transmission != ReturnMechanism`
6. `MacroReturnMechanism != ReturnEngine`
7. `Target != Thesis != Position != Book`
8. `HistoricalAnalogy != CapitalAction`
9. `ResearchPass != CapitalPass`
10. `ClaimAuthority <= EvidenceAuthority`
11. `NoSilentThesisMigration = true`
12. `RealitySettlement = final epistemic authority`

---

## 6. Hard negatives

H1 must fail closed against at least these cases:

1. Human five-layer map is declared the complete machine ontology → FAIL.
2. `1970s-like` directly creates a Gold position recommendation → FAIL.
3. Epoch label is used as a timing signal → FAIL.
4. Constraint lacks explicit bound actor and binding evidence → FAIL.
5. Policy reaction is omitted and state maps directly to mechanism → FAIL unless documented as an empirically justified direct channel.
6. All transmission is reduced to one scalar policy-rate field → FAIL.
7. MRM-P/D/CA/CR/SC/RS are represented as replacements for ENG-C/R/X → FAIL.
8. One asset is assigned one permanent return engine → FAIL.
9. Realized profit is used to mark a wrong-mechanism thesis as epistemically correct → FAIL.
10. Historical PIT thesis is rewritten after outcome knowledge → FAIL.

---

## 7. Human Review Gate

H1 requires `10/10 PASS`:

1. Five-layer human model is materially easier to navigate than the ten-node chain.
2. All ten machine distinctions remain representable.
3. Constraint is the central causal bridge rather than a decorative label.
4. Dynamic state semantics preserve level / direction / acceleration / surprise / persistence.
5. Policy reaction and financial transmission remain separate.
6. MRM vs C/R/X authority is explicit.
7. Target / Thesis / Position / Book semantics remain intact.
8. No direct historical analogy → capital action path exists.
9. Wrong-mechanism lucky outcomes are explicitly detectable.
10. No portfolio/trading/execution authority is granted.

## 8. Acceptance token

Human acceptance token for this written specification:

`ACCEPT_YMA55_H1_FIVE_LAYER_DECISION_KERNEL_FREEZE`

Acceptance of H1 authorizes H2 specification review only. It does not imply merge, runtime deployment, portfolio authority or trading authority.
