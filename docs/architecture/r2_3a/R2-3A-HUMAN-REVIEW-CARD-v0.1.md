# R2.3-A Human Review Card v0.1

Status: `candidate_started`

Stage: **R2.3-A | Yuanli Investment OS Architecture Freeze + Cross-Asset Semantic Hardening**

Upstream dependency: PR #22 / R2.3 is accepted and squash-merged at `418f06200cde16173743454d506ee946bbc572fc`.

## Review purpose

Confirm architecture and semantic universality only. This review does **not** accept benchmark results, Evidence/Outcome admission, runtime implementation, trading action, target price, recommended weight, position sizing, A9 switch or RSI promotion.

## Frozen decisions to review

### D1 | Preserve base OS identity and freeze human front-end

Base machine identity remains:

> **一核 · 三界 · 三门 · 一环**
>
> `one_core_three_worlds_three_gates_one_loop`

Human front-end is compressed to:

> **势 · 信 · 极｜真 · 价 · 生**

Machine extensions must remain backstage.

### D2 | Freeze P as capital + asset reality

Human `P | 势` asks:

> **现实世界正在往哪里运动？**

- `P.capital`: growth, inflation, liquidity, risk appetite, term premium/duration supply, funding stress, policy reaction function.
- `P.asset`: technology/adoption, supply-demand/inventory/cost curve, cash flow/balance sheet, fiscal/monetary/regulatory/institutional reality as relevant.

`R | Regime Causal Decomposition` is a separately typed machine decomposition/context for `P.capital`.

**Reject if R is introduced as a fourth human world or if a hostile regime is allowed to erase valid bottom-up truth.**

### D3 | Universalize Xs

Canonical X remains:

> `X := (Xs, Xa, Xp)`

`Xs` mother concept becomes **Structural Asymmetry Source**.

Asset-specific implementations include:

- equity -> Value Control Point
- commodity -> Scarcity / Supply Elasticity
- sovereign rates -> Duration / Convexity / Term Premium
- credit -> Default / Spread / Recovery / Refinancing
- FX -> Policy Divergence / Carry / Flow
- gold/monetary asset -> Monetary Scarcity / Reserve Demand
- derivatives -> Volatility Mispricing / Convexity

Reject if Value Control Point is treated as universal cross-asset ontology.

### D4 | Freeze two-stage router A0/A1

`A0 | asset_form`:

`equity / sovereign_rates / credit / commodity / FX / monetary_asset / crypto / derivative`

`A1 | pricing_archetype`:

`growth / compounder / cyclical / duration / scarcity / event_optionality`

Invariant:

> **Asset form is not pricing model.**

A target may require multiple pricing archetypes.

### D5 | Generalize L0-L4 across asset classes

- L0 cross-asset regime
- L1 asset-class regime
- L2 theme / macro-theme regime
- L3 value pool / market structure
- L4 asset / instrument

Invariant:

> **Lower-level truth does not imply higher-level authorization.**

Research validity and capital permission remain distinct.

### D6 | Keep N as expectation regime, not sentiment

N remains:

`story -> diffusion -> expectation translation -> crowding -> regime break`

N authority may be `binding / auxiliary / irrelevant` according to pricing archetype.

A break triggers bounded V/Xa/Xp re-underwriting; it is not an automatic sell instruction.

### D7 | Keep E/V/S as gates

- E | 真: `Claim Authority <= Evidence Authority`
- V | 价: `Price-Implied Expectations`; no target-price ontology
- S | 生: portfolio survival; `Issuer Durability != Portfolio Survival`

### D8 | Preserve Research OS / Portfolio OS governance split without splitting X

The split allocates authority only. It does not redefine X or remove Xp from `X := (Xs, Xa, Xp)`.

Research OS cannot emit recommended portfolio weights or live actions merely because it studies Xp/S.

### D9 | Freeze candidate capability identities

P0:

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

These are candidate identities only; no Gold promotion is implied.

### D10 | Cross-Asset Stress Check

The architecture must route five deliberately different fixtures through the same human grammar without collapsing their physics:

- NVIDIA
- UST30Y
- Copper
- Gold
- USDJPY

The fixture tests semantic/routing coverage only. It does not claim current market attractiveness or historical alpha.

Machine fixture:

`docs/architecture/r2_3a/R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json`

## Mandatory rejection conditions

Reject if any of the following appears:

- a fourth human world is created for R;
- `P.capital` and `P.asset` are collapsed into one scalar;
- Value Control Point is universalized beyond its equity implementation role;
- A becomes sector taxonomy instead of pricing-engine routing;
- N becomes universally binding;
- V becomes target-price ontology;
- S becomes issuer quality or a stop-loss rule;
- P/N/X/E/V/S/R are recombined into a scalar Force score;
- Research/Portfolio split changes `X := (Xs, Xa, Xp)`;
- lower-level research is allowed to bypass higher-level authorization;
- Research OS can output recommended portfolio weights or live actions;
- cross-asset stress validation is replaced by prose assertion only.

## Machine qualification requirement

Before this Human Gate becomes active, exact-head CI must pass:

- deterministic `CANON-STATUS` projection check;
- R2.3 upstream merge-receipt validation;
- R2.3-A architecture validator;
- cross-asset stress validator;
- existing repository/governance validators.

## Proposed Human Gate token

`ACCEPT_R2_3A_YUANLI_INVESTMENT_OS_ARCHITECTURE_FREEZE`

Human Acceptance does not imply merge.
