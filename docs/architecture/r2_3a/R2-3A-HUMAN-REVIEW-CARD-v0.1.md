# R2.3-A Human Review Card v0.1

Status: `human_accepted_ready_for_merge`

Stage: **R2.3-A | Yuanli Investment OS Architecture Freeze + Cross-Asset Semantic Hardening**

Upstream dependency: PR #22 / R2.3 is accepted and squash-merged at `418f06200cde16173743454d506ee946bbc572fc`.

Human decision: `ACCEPT_R2_3A_YUANLI_INVESTMENT_OS_ARCHITECTURE_FREEZE`

Reviewed exact head: `2bc27932f9580de9b41ed7a8ed0721bcafafd788`

Reviewed exact-head CI: repository-gates Run #124 (`32363617225`) = **SUCCESS**.

Acceptance receipt: `docs/architecture/r2_3a/R2-3A-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`.

Human Acceptance does **not** imply merge. Separate merge authorization remains required.

## Review purpose

Confirm architecture and semantic universality only. This review does **not** accept benchmark results, Evidence/Outcome admission, runtime implementation, trading action, target price, recommended weight, position sizing, A9 switch or RSI promotion.

## Accepted decisions

### D1 | Preserve base OS identity and freeze human front-end

Base machine identity remains:

> **一核 · 三界 · 三门 · 一环**
>
> `one_core_three_worlds_three_gates_one_loop`

Human front-end is compressed to:

> **势 · 信 · 极｜真 · 价 · 生**

Machine extensions remain backstage.

### D2 | Freeze P as capital + asset reality

Human `P | 势` asks:

> **现实世界正在往哪里运动？**

- `P.capital`: growth, inflation, liquidity, risk appetite, term premium/duration supply, funding stress, policy reaction function.
- `P.asset`: technology/adoption, supply-demand/inventory/cost curve, cash flow/balance sheet, fiscal/monetary/regulatory/institutional reality as relevant.

`R | Regime Causal Decomposition` is a separately typed machine decomposition/context for `P.capital`.

**R is not a fourth human world, and hostile regime state does not erase valid bottom-up research truth.**

### D3 | Universalize Xs

Canonical X remains:

> `X := (Xs, Xa, Xp)`

`Xs` mother concept is **Structural Asymmetry Source**.

Asset-specific implementations include:

- equity -> Value Control Point
- commodity -> Scarcity / Supply Elasticity
- sovereign rates -> Duration / Convexity / Term Premium
- credit -> Default / Spread / Recovery / Refinancing
- FX -> Policy Divergence / Carry / Flow
- gold/monetary asset -> Monetary Scarcity / Reserve Demand
- derivatives -> Volatility Mispricing / Convexity

Value Control Point is not universal cross-asset ontology.

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

The architecture routes five deliberately different fixtures through the same human grammar without collapsing their physics:

- NVIDIA
- UST30Y
- Copper
- Gold
- USDJPY

The fixture tests semantic/routing coverage only. It does not claim current market attractiveness or historical alpha.

Machine fixture:

`docs/architecture/r2_3a/R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json`

## Acceptance boundaries

Acceptance preserves all of the following:

- no fourth human world for R;
- no scalar PNX/Force/macro score;
- no universalization of Value Control Point beyond equity implementation;
- no universal N binding;
- no target-price ontology for V;
- no issuer-quality/stop-loss substitution for S;
- no X semantic split;
- no Research OS recommended weights or live actions;
- no Gold promotion, benchmark acceptance, Evidence/Outcome admission, A9 switch, RSI promotion or live execution.

## Post-acceptance qualification

The acceptance record/state/Canon/validator head must pass a fresh exact-head repository-gates run before merge authorization can be exercised.

Current machine state sets the next governance gate to `R2_3A_MERGE`, but merge remains blocked until the external post-acceptance exact-head CI fact is SUCCESS and the owner separately authorizes merge.
