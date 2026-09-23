# YIOS-TG1｜Trade Guidance Product Constitution v0.1

Date: 2026-09-22  
Status: `IMPLEMENTATION_CANDIDATE / HUMAN AUTHORIZED TO EXECUTE / SHADOW_ONLY`

## 1. Mission

YIOS-TG1 turns governed investment research into a daily decision product without collapsing research, capital and execution authority.

North-star user question:

> 今天究竟发生了什么、我现在应该做什么、什么事实出现我必须改变？

## 2. Application Boundary

YIOS-TG1 is an application binding over YIOS0 / YMQ / GOLD2 / YEX0 / YVN1-A0.

It does not create a second Investment Canon.

It does not authorize:
- recommended portfolio size
- broker action
- VeighNa runtime
- live execution
- real capital movement
- automatic research-to-execution

## 3. User Journey

```text
Today
→ Gold Cockpit
→ Trade Decision
→ Reality Audit
→ Shadow Book
→ Settlement & Learning
```

The front-stage action language is:

`WAIT / PROBE / HOLD / REDUCE / HEDGE`

## 4. Core Product Object

`TradeDecisionCandidate` is the bounded bridge between Research Settlement and Capital Admission.

Minimum fields:

- target / instrument scope
- horizon
- action_state
- thesis
- dominant_regime
- trigger_conditions
- defeat_conditions
- price_condition
- payoff_condition
- survival_condition
- known_as_of
- evidence_refs
- unknowns
- contract_version
- code_sha
- authority = SHADOW_ONLY by default

## 5. Program Spine

```text
Reality
→ Evidence / PIT
→ Research State
→ Reality Audit
→ TradeDecisionCandidate
→ Capital Admission
→ Shadow PositionPassport
→ Shadow Settlement
→ LearningDelta
→ Next-Task Pre-Action Recall
→ Decision Delta
```

## 6. Data Minimum

P0 live evidence:
- Gold Spot
- USD
- Actual Real Rate
- 10Y nominal / breakeven diagnostic bridge
- Central Bank Gold Demand
- one governed Stress Proxy

P1:
- ETF flow
- CFTC positioning
- broader USD
- fiscal burden
- COFER

P2:
- narrative diffusion
- alternative flow / microstructure

## 7. Product PIT Contract

Each material observation must preserve:

- observation_at
- released_at
- retrieved_at
- available_at
- vintage_id
- value / unit
- frequency
- source
- measurement_regime
- pit_grade

Missing temporal authority must degrade the claim; it must not be reconstructed silently.

## 8. Cross-Repository Authority

### moonstachain/yuanli-invest
Owns:
- Investment domain semantics
- TradeDecisionCandidate contract
- YIOS-TG1 program law
- CURRENT pointer
- research/capital/execution boundaries

### moonstachain/yuanli-invest-runtime
Owns:
- provider adapters
- Evidence/PIT/runtime implementation
- Reality Sink
- state compilation
- shadow settlement runtime
- learning runtime

### yuanli-life/yuanli-os
Owns:
- identity / Personal Node
- authority projection
- Web/PWA
- MCP / product gateway
- task continuity
- Gold Decision Cockpit UX

### Supabase
Runtime Reality Plane, not Canon.

### Notion
Human Projection / Project Cockpit, not Canon.

### ShareSpec
Cross-repository binding and reusable protocol slots only; no copied Investment Canon.

## 9. Gates

G0 Product Constitution × Architecture Freeze  
G1 Live Reality Plane × Supabase Sink × Freshness Contract  
G2 Invest Domain Gateway  
G3 Gold Decision Cockpit  
G4 Trade Decision Compiler  
G5 Shadow Runtime  
G6 Learning Recall  
G7 Internal Alpha  
G8 Seed Alpha

Broker Paper and Live Capital belong to later programs, not TG1.

## 10. Acceptance Law

TG1 becomes a usable Internal Alpha only when one real chain completes:

```text
Real provider evidence
→ governed PIT
→ product state
→ TradeDecisionCandidate
→ Human audit
→ Shadow admission or denial
→ Outcome
→ Settlement
→ LearningDelta
→ later independent task Pre-Action Recall
→ observable Decision Delta
```

A generated page, model output, or dashboard alone is not product completion.
