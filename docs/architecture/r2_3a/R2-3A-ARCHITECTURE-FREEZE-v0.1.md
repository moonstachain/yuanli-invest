# R2.3-A | Yuanli Investment OS Architecture Freeze v0.1

Status: `candidate_started_cross_asset_hardening`

Base dependency: PR #22 / R2.3 is Human Accepted and squash-merged into `main` at `418f06200cde16173743454d506ee946bbc572fc`.

This document freezes architecture only. It does **not** authorize capability promotion, runtime implementation, benchmark acceptance, Evidence/Outcome admission, A9 switch, RSI promotion, buy/sell actions, target prices, recommended portfolio weights, position sizing, or live execution.

## 1. Strategic objective

The objective remains:

> **Lifetime Right-Tail Capture under Survival Constraints**

Human meaning:

> **抓住右尾 · 让赢家复利 · 永不出局**

The base OS identity remains:

> **一核 · 三界 · 三门 · 一环**
>
> `one_core_three_worlds_three_gates_one_loop`

R2.3-A.1 is a semantic hardening of that identity for cross-asset research. It does not add a fourth human world.

Human front-end mnemonic is frozen as:

> **势 · 信 · 极｜真 · 价 · 生**
>
> **顺大势 · 乘共识 · 押极值｜凭真据 · 买好价 · 永不死**

Machine complexity remains backstage.

## 2. P | 势 = Reality State Transition

Human umbrella question:

> **现实世界正在往哪里运动？**

P has two human-facing subspaces:

### P.capital | 资本势

Capital, discount-rate and financing reality:

- growth
- inflation
- liquidity
- risk appetite
- term premium / duration supply
- funding stress
- policy reaction function

Question:

> **钱、折现率和资本约束正在往哪里走？**

### P.asset | 资产势

Asset-/industry-specific physical reality. Depending on asset form this may include:

- technology / adoption / productivity / monetization
- supply / demand / inventory / cost curve / capacity
- earnings / cash flow / balance-sheet quality
- fiscal / monetary / regulatory / institutional regime
- international balance-of-payments and reserve structure

Question:

> **这个资产背后的真实世界正在怎样变化？**

### R relationship

`R | Regime Causal Decomposition` remains a separately typed machine capability/context for `P.capital` because capital-regime state has different observables, horizons and authorization effects from asset-specific structural reality.

**R is not a fourth human world and does not replace P.**

R constrains downstream signal transferability / execution authorization; it does not erase valid bottom-up research merely because the capital regime is hostile.

Hard prohibition: no universal rule such as `yield_up => equities_down` or `risk_off => every bottom-up thesis false`.

## 3. N | 信 = Expectation Regime

Human question:

> **市场正在为哪个未来付钱？**

N is not raw sentiment. It studies:

`story -> diffusion -> expectation translation -> crowding -> regime break`

N may be `binding`, `auxiliary`, or `irrelevant` to the dominant pricing mechanism according to asset/pricing routing.

Examples of expectation parameters differ by asset: revenue growth, margin duration, policy path, inflation path, supply deficit, reserve demand, carry persistence, event probability, or volatility state.

Narrative strength is not truth. A narrative break is a mandatory re-underwrite trigger for V/Xa/Xp, not an automatic sell instruction.

## 4. X | 极 = Structural Asymmetry

Canonical semantics remain indivisible:

> `X := (Xs, Xa, Xp)`

This is a structural tuple, never arithmetic addition or multiplication.

### Xs | Structural Asymmetry Source

Universal question:

> **为什么这里会产生不成比例的收益或风险？**

`Xs` is the mother concept. Asset-specific implementations include:

| Asset form / pricing context | Typical Xs implementation |
|---|---|
| equity | Value Control Point / network / scale / switching cost / bottleneck / distribution |
| commodity | scarcity / inventory criticality / supply elasticity / capacity lag |
| sovereign rates | duration / convexity / term-premium or policy-path asymmetry |
| credit | default / spread / recovery / refinancing asymmetry |
| FX | policy divergence / carry / balance-of-payments / positioning / flow |
| gold / monetary asset | monetary scarcity / real-rate sensitivity / reserve demand / credibility regime |
| derivatives | volatility mispricing / convexity / skew / path dependence |
| crypto | network / scarcity / liquidity reflexivity / protocol or custody control |

`Value Control Point Mapper` therefore remains an important **equity-specialized implementation**, not the universal ontology of Xs.

### Xa | Asymmetry Activation / Conditional Tail State

Question:

> **为什么是现在？哪一侧尾部正在变肥？**

Xa is a conditional tail state, not a fake precision probability-of-being-right score unless explicit calibration exists.

### Xp | Asymmetry Capture / Payoff Geometry

Question:

> **用什么工具才能真正吃到这个不对称？**

Underlying right-tail potential does not imply attractive instrument payoff. Premium/carry, liquidity, path dependency and left-tail damage matter.

## 5. 三门 | E / V / S

### E | 真 = Evidence Gate

Invariant:

> **Claim Authority <= Evidence Authority**

Every material claim must distinguish primary evidence, independent empirical evidence, synthesis, practitioner claim and hypothesis.

### V | 价 = Price Gate

Question:

> **这个未来已经被当前价格预付了多少？**

V is `Price-Implied Expectations`, not target-price ontology. Different asset forms use different algorithms: reverse DCF, implied policy path, futures curve, forward/carry, real-rate/monetary-premium decomposition, implied volatility/skew, and other replaceable implementations.

### S | 生 = Survival Gate

Question:

> **如果错了，组合还有没有下一局？**

`Issuer Durability != Portfolio Survival`.

S concerns concentration, stress correlation, liquidity, leverage, funding, gap risk and path dependency. It does not automatically emit position size.

## 6. L0-L4 | Cross-Asset Authority Ladder

The ladder is generalized beyond equity:

| Level | Research object | Core question | Output |
|---|---|---|---|
| L0 | Cross-Asset Regime | Where does capital prefer to go across equity/rates/credit/commodities/FX/monetary assets/cash? | cross-asset envelope |
| L1 | Asset-Class Regime | Which sub-regime inside the chosen asset class is active? | asset-class envelope |
| L2 | Theme / Macro-Theme Regime | Is a theme expanding, internally rotating, or externally de-risking? | theme envelope |
| L3 | Value Pool / Market Structure | Where is value, scarcity, duration, carry or control concentrated? | research universe |
| L4 | Asset / Instrument | What is the current asset/instrument state and payoff geometry? | decision candidate |

Invariant:

> **Lower-level truth does not imply higher-level authorization.**

This is an authorization rule, not a truth-destruction rule. Research validity and capital permission remain distinct.

## 7. A | Two-Stage Asset Router

A is routing infrastructure, not a score and not a sector taxonomy.

### A0 | asset_form

Canonical families:

- equity
- sovereign_rates
- credit
- commodity
- FX
- monetary_asset
- crypto
- derivative

### A1 | pricing_archetype

Canonical families:

- growth
- compounder
- cyclical
- duration
- scarcity
- event_optionality

Rule:

> **Asset form is not pricing model.**

Gold and copper may both trade in commodity markets but have different pricing archetypes. A single issuer can contain multiple archetypes by business line or payoff target.

A1 routes the binding pricing engine and the authority of N (`binding / auxiliary / irrelevant`).

## 8. Human navigation vs machine navigation

### Human front-end

Only six characters are required:

> **势 · 信 · 极｜真 · 价 · 生**

- P｜势：现实往哪里走？
- N｜信：市场正在为哪个未来付钱？
- X｜极：哪里存在结构性不对称？
- E｜真：证据够不够？
- V｜价：这个未来已经付了多少？
- S｜生：如果错了，还能继续吗？

### Seven-question drilldown

The accepted Seven Questions remain a deeper diagnostic projection:

1. 世界真的在变吗？ -> P
2. 不对称从哪里来？ -> Xs
3. 市场正在为哪个未来付钱？ -> N
4. 这个未来已经被价格预付多少？ -> V
5. 哪一侧尾部正在被激活？ -> Xa
6. 我的工具能否真正捕获右尾？ -> Xp
7. 如果我错了，还能继续复利吗？ -> S

E remains horizontal.

### Machine backstage

Machine state may use `R / A0 / A1 / L0-L4 / P.capital / P.asset / N / Xs / Xa / Xp / E / V / S` as typed state. Machine complexity must not replace the human mnemonic.

## 9. Research dependency and reflexivity

Reference orchestration:

`A0/A1 -> P.capital(R) + P.asset -> Xs -> V <-> N -> Xa -> Xp -> S`

with `E` horizontal and L0-L4 providing nested research/authorization context.

This is a research dependency graph, not a universal one-way causal law. Reflexive edges are allowed only when explicitly represented as hypotheses or evidence-backed mechanisms.

## 10. Research OS vs Portfolio OS

This is a governance authority separation, not an X ontology split.

Research OS owns typed research-state production and may study all X semantics.

Portfolio OS owns portfolio aggregation, expression, survival, rebalance and execution-adjacent authority.

Canonical X remains:

> `X := (Xs, Xa, Xp)`

Research OS cannot emit target prices, recommended portfolio weights, live sizing or execution merely because it studies Xp/S.

## 11. Candidate capability set

P0 implementation sequence:

1. `CAP-R-01 | Regime Causal Decomposition`
2. `CAP-V-01 | Price-Implied Expectations`
3. `CAP-XS-01 | Structural Asymmetry Source Mapper`

P1:

- `CAP-N-01 | Narrative / Expectation Regime`
- `CAP-N-02 | Expectation Regime Break Detector`
- `CAP-XA-01 | Conditional Tail State`
- `CAP-XP-01 | Payoff Geometry`
- `CAP-S-01 | Portfolio Survival Gate`

Supporting:

- `CAP-R-02 | Internal vs External Rotation Detector`
- `CAP-A-01 | Two-Stage Asset / Pricing Router`
- `CAP-P-01 | Reality State Transition`
- `CAP-E-01 | Evidence Authority Graph`

Priority is implementation order only, not conceptual rank, Gold status or capital authority.

## 12. Cross-Asset Stress Check

R2.3-A.1 requires a structural stress check across five deliberately different research targets:

- NVIDIA / equity-growth-control-point
- 30Y U.S. Treasury / sovereign-rates-duration
- Copper / commodity-cyclical-scarcity
- Gold / monetary-asset-scarcity
- USDJPY / FX-policy-divergence-carry

The stress check validates **semantic coverage and routing**, not investment conclusions or historical alpha. No current-market claim is implied by the fixture.

Machine fixture:

`docs/architecture/r2_3a/R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json`

## 13. Replay and benchmark law

Architecture acceptance is not capability validation. Each capability must later define point-in-time replay, simpler baselines, failure cases, false-alarm accounting, regime holdouts where relevant, future settlement and revision rules.

Complexity has no natural authority.

## 14. R2.3-B reserved requirements

`CAP-N-02` must define a bounded re-underwrite SLA. If an expectation-regime break fires and V/Xa/Xp reassessment is not completed within the typed SLA, downstream state degrades to `research_only / stale`.

R2.3-A does not invent a universal number of trading days before benchmark work.

## 15. Non-authorization boundary

This freeze does not authorize:

- Gold promotion;
- benchmark result acceptance;
- Evidence/Outcome admission;
- target prices;
- buy/sell actions;
- recommended portfolio weights or position sizes;
- live execution;
- A9 operational-canon switch;
- RSI promotion.

## 16. Exit gate

R2.3-A may reach Human Review only after:

1. PR #22 merge fact is closed by immutable receipt;
2. PR #23 is cleanly refreshed on accepted `main`;
3. R2.3-A.1 semantic hardening is present in Constitution / state / validators;
4. cross-asset stress fixture passes deterministic validation;
5. fresh exact-head contracts + governance CI passes.

Proposed Human Gate token:

`ACCEPT_R2_3A_YUANLI_INVESTMENT_OS_ARCHITECTURE_FREEZE`
