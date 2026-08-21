# RCN0｜Reality–Capital–Narrative Market Driver Canon v0.1

Status: `candidate`

Issue: #26

## 1. Mission

RCN0 is a market/industry state-attribution layer under the accepted Yuanli Investment Research Intelligence Constitution.

It answers one stable question:

> **What is currently doing the pricing: Reality, Capital, Narrative, or a coupled regime?**

RCN0 does not replace PNX, does not create a fourth human world, and does not authorize trades. It is a bounded composition of existing canonical semantics:

- `Reality := P.asset`
- `Capital := P.capital`, informed by `CAP-R-01 | Regime Causal Decomposition`
- `Narrative := N | Expectation Regime`

The intended primary scope is L0–L3: cross-asset, asset-class, theme/macro-theme, value-pool/market-structure. L4 single-name evidence may validate or falsify a higher-level state but must not be silently generalized upward.

## 2. First-principles model

Traditional equity pricing can be compressed into numerator and denominator:

- numerator: earnings / cash flow / industrial reality;
- denominator: discount rate / liquidity / risk appetite.

RCN0 makes a third pricing engine explicit:

- `R | Reality`: what is actually changing in the economy, industry, technology, supply-demand system or cash-flow path;
- `C | Capital`: what is changing in the price and availability of capital, discount rates, liquidity, funding and risk budget;
- `N | Narrative`: what future assumption the market is collectively adopting, diffusing, crowding or abandoning.

Conceptual identity:

`Price Change = Phi(Reality State, Capital State, Narrative State)`

This is not a linear factor model and must not be collapsed into a scalar RCN score.

## 3. Core invariants

1. **Narrative strength is not truth.**
2. **Attention and price appreciation do not establish Reality.**
3. **Capital regime and asset reality are separable states even when they interact.**
4. **Narrative is not raw sentiment.** N describes the future assumption the market is paying for and its diffusion/crowding/break dynamics.
5. **Narrative Mapping != Industrial Validation.**
6. **A lower-level truth does not imply higher-level authorization.**
7. **RCN attribution is state diagnosis, not a buy/sell/position-size instruction.**
8. **No scalar RCN/Force score is canonical.**

## 4. Narrative Mapping vs Industrial Validation

### 4.1 Narrative Mapping

Narrative Mapping is a belief-network transmission chain:

`external event -> punchy story -> semantic analogy -> theme/industry mapping -> capital attention -> price response`

It asks:

> **How close is this target, in market cognition, to the story currently spreading?**

### 4.2 Industrial Validation

Industrial Validation is a reality/causal chain:

`technical result -> technical comparability -> ownership/rights -> product/pipeline -> regulatory/clinical/operating milestones -> commercialization/order -> revenue -> profit -> cash flow`

It asks:

> **How many real-world gates remain before this event changes the target's economics?**

These chains may move at different speeds and in opposite directions.

## 5. Two distances

### 5.1 Narrative Distance `D_N`

`D_N(event, target)` is an ordinal/graph distance representing how many belief/semantic translation steps separate an event from a market target.

Possible observables:

- semantic similarity of event language to theme/company disclosures;
- concept-tag co-occurrence;
- media/social propagation path;
- cross-sectional return gradient by concept proximity;
- fund-flow gradient by concept proximity.

RCN0 does not require a universal numeric metric. The first implementation may use ordinal buckets and graph hops.

### 5.2 Industrial Distance `D_R`

`D_R(event, target)` is the number and materiality of real-world validation gates between the event and durable economics.

Candidate gates include:

- technical comparability;
- IP / economic-right ownership;
- product/pipeline presence;
- regulatory/clinical validation;
- production/scale validation;
- commercial contract/order;
- revenue recognition;
- profit/cash-flow settlement.

## 6. Narrative–Reality Gap `NRG`

`NRG` is a state, not a scalar score.

It describes whether expectation migration is running materially ahead of, in line with, or behind reality migration.

Canonical labels:

- `reality_leads_belief`
- `coupled_confirmation`
- `belief_leads_reality`
- `divergent_or_unclear`

Interpretation:

- `reality_leads_belief`: potential under-recognition / latent-dragon research state;
- `coupled_confirmation`: narrative and industrial settlement reinforce one another;
- `belief_leads_reality`: narrative mapping has outrun industrial validation;
- `divergent_or_unclear`: no authorized directional compression.

These are research labels, not trading instructions.

## 7. Dominant Market Driver Attribution

RCN0 classifies the current move using a multidimensional state vector rather than a score.

Candidate driver labels:

- `reality_led`
- `capital_led`
- `narrative_led`
- `triple_resonance`
- `mixed_rotation`
- `unresolved`

### 7.1 `reality_led`

Minimum pattern:

- material `P.asset` transition;
- price/sector leadership broadly consistent with industrial/earnings evidence;
- capital and narrative may amplify but are not required to explain the move.

### 7.2 `capital_led`

Minimum pattern:

- material change in rates/liquidity/risk appetite/funding;
- broad duration/beta/style response consistent with that capital shift;
- no equivalent contemporaneous asset-reality improvement required.

### 7.3 `narrative_led`

Candidate pattern:

- new external/internal story creates an expectation-regime shock;
- `P.capital` is insufficient to explain the magnitude/cross-section;
- industrial evidence is mixed, lagged or materially narrower than price diffusion;
- cross-sectional returns follow Narrative Distance more closely than Industrial Validation quality;
- valuation/repricing is not parsimoniously explained as simple low-valuation repair.

### 7.4 `triple_resonance`

Reality, Capital and Narrative point in the same direction with mutually reinforcing evidence.

This is a strong market-state label, not a portfolio instruction.

## 8. Standard state vector

A machine-callable RCN state SHOULD preserve at least:

```yaml
as_of: YYYY-MM-DDTHH:MM:SSZ
scope:
  level: L0|L1|L2|L3
  target: string
reality:
  state: improving|deteriorating|mixed|unchanged|unknown
  transition: accelerating|decelerating|stable|unknown
  evidence_refs: []
capital:
  state: supportive|restrictive|mixed|neutral|unknown
  transition: easing|tightening|stable|unknown
  evidence_refs: []
narrative:
  story: string
  phase: ignition|acceleration|crowding|deceleration|break|unknown
  delta: rising|falling|flat|unknown
  delta2: accelerating|decelerating|unknown
  counter_narrative: absent|emerging|material|dominant|unknown
  evidence_refs: []
mapping:
  narrative_distance: near|medium|far|unknown
  industrial_distance: near|medium|far|unknown
  nrg_state: reality_leads_belief|coupled_confirmation|belief_leads_reality|divergent_or_unclear
attribution:
  dominant_driver: reality_led|capital_led|narrative_led|triple_resonance|mixed_rotation|unresolved
  confidence: high|medium|low
valuation:
  price_implied_expectation_state: underwritten|partially_underwritten|overextended|unknown
falsifiers: []
revision_rule: string
non_authorization: research_only
```

## 9. Required capability bindings

RCN0 must not duplicate the canonical research capabilities. It composes them.

Required Shadow bindings:

- `CAP-R-01 | Regime Causal Decomposition` -> Capital state;
- `CAP-P-01 | Reality State Transition` -> Reality state;
- `CAP-N-01 | Narrative / Expectation Regime` -> Narrative state;
- `CAP-V-01 | Price-Implied Expectations` -> valuation/embedded-future sanity check.

Useful supporting bindings:

- `CAP-R-02 | Internal vs External Rotation Detector`;
- `CAP-E-01 | Evidence Authority Graph`;
- later `CAP-N-02 | Expectation Regime Break Detector`.

## 10. Gold Replay law

An RCN case may be called a **Gold Replay candidate** only if:

1. evidence is frozen point-in-time;
2. later outcomes are excluded from the initial state reconstruction;
3. Reality, Capital and Narrative evidence are separately sourced;
4. at least one simpler baseline is specified;
5. the dominant-driver label has explicit falsifiers;
6. subsequent industrial settlement is tracked separately from the initial narrative move;
7. Human Review accepts the replay.

Documentation alone does not promote a case to Gold.

## 11. Falsification tests

RCN0 should fail if any of the following becomes systematic:

- `narrative_led` labels merely restate large price moves;
- Narrative Distance is inferred from returns without independent semantic/network evidence;
- Industrial Distance ignores economic-right ownership or commercialization gates;
- Capital state is treated as a single liquidity number;
- Reality and Narrative are silently conflated;
- future outcomes leak into point-in-time reconstruction;
- RCN labels outperform only after tuning on the same cases used for evaluation.

## 12. Non-authorization boundary

RCN0 does not authorize:

- buy/sell;
- target price;
- portfolio weight;
- position size;
- broker/live execution;
- automatic Gold promotion;
- replacement of the accepted `一核 · 三界 · 三门 · 一环` Constitution.

RCN0 is a market-driver research capability candidate only.
