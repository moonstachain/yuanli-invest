# R2.3-B1｜P0 Capability Contract Specification v0.1

## 1. Purpose

B1 compiles the accepted R2.3-B0 universal 11-block `ResearchCapability` contract into three implementation-ready **specifications**, without implementing algorithms, admitting evidence/outcomes, promoting Capability maturity, or granting capital/execution authority.

P0 capabilities:

1. `CAP-R-01 | Regime Causal Decomposition`
2. `CAP-V-01 | Price-Implied Expectations`
3. `CAP-XS-01 | Structural Asymmetry Source Mapper`

The human front-end remains **势 · 信 · 极｜真 · 价 · 生**. B1 is backstage machine specification.

## 2. Constitutional invariants

- `Claim Authority <= Evidence Authority`.
- `P = P.capital + P.asset`; `R` is typed machine decomposition of `P.capital`, not a fourth human world.
- `Asset form is not pricing model`; all model selection uses `A0 | asset_form` + `A1 | pricing_archetype`.
- `X := (Xs, Xa, Xp)` remains indivisible; B1 specifies Xs only and may not silently absorb Xa/Xp/V/S.
- Canonical output is typed `ResearchState`, never a scalar Force/PNX/macro master score.
- Provider/vendor fields are adapters, never Capability identity.
- Point-in-time semantics, publication lag, revisions and evidence cutoff are mandatory.
- Target price, canonical upside %, recommended portfolio weight, position size, buy/sell/hold and live execution remain prohibited.
- `Research PASS != Capital PASS`.

## 3. Shared runtime law

Every invocation must bind:

`canon_revision + canon_hash + capability_id + contract_version + research_target + A0 + A1 + as_of + evidence_cutoff + provider_runtime`.

Every result must emit a `ResearchReceipt` containing the invocation envelope, algorithm family, evidence references, output state version, identification/uncertainty status and degrade state.

Failure is explicit. Missing evidence, stale data, under-identification, model disagreement or violated assumptions must degrade the state rather than be hidden by prose.

## 4. CAP-R-01｜Regime Causal Decomposition

Stable question:

> What causal capital regime currently governs discount rates, risk appetite, funding conditions and cross-asset capital allocation?

Semantic parent: `P.capital`.

### Minimum state

- growth
- inflation
- liquidity
- risk_appetite
- term_premium
- funding_stress
- policy_reaction_function

Each dimension must carry `direction`, `magnitude_band`, `persistence_band`, `evidence_refs`, `competing_mechanisms`, `uncertainty_semantics` and `as_of`.

### Core inference families

- causal state machine / rule graph
- dynamic factor / latent-state decomposition
- regime-switching / HMM as descriptive state detector
- change-point detection
- structural VAR / local-projection evidence where identification is defensible
- scenario-tree decomposition for policy reaction functions

No single family has constitutional privilege. Correlation, feature importance or Granger precedence cannot self-promote to causal effect.

### Key distinction

`liquidity != risk_appetite`, `nominal_yield != real_yield`, and a yield move must be decomposed into policy-path, inflation and term-premium channels before higher-authority causal claims are made.

### Settlement

Settle state calls against subsequent realized macro/market observables over typed 1m/3m/6m horizons, with PIT replay and regime holdouts. A capability succeeds by improving state discrimination and downstream research calibration versus simpler baselines, not by predicting one asset return.

## 5. CAP-V-01｜Price-Implied Expectations

Stable question:

> What future state or operating assumptions are already embedded in current price?

Semantic parent: `V`.

### Universal output

- model_family
- implied_parameters or identified parameter region
- scenario_mapping
- identification_status
- identification_caveats
- sensitivity_map
- evidence_refs
- as_of
- degrade_state

If the inverse problem is under-identified, output a **set/range/scenario family**, not fake point precision.

### Routed model families

- equity: reverse DCF / implied growth, margin, reinvestment and duration
- sovereign rates: implied policy path / inflation / term premium decomposition
- credit: implied default / spread / recovery / refinancing assumptions
- commodity: futures curve / convenience yield / scarcity / marginal-cost state
- FX: forward differential / carry / policy-path assumptions
- monetary asset: real-rate / monetary-risk / reserve-demand scenario mapping
- derivative: IV surface / skew / term structure / implied distribution
- crypto: network / scarcity / liquidity scenario mapping

No universal valuation formula is allowed across asset forms.

### Settlement

The unit of settlement is whether price-implied assumptions were correctly extracted and whether subsequent reality moved toward/away from those assumptions. Target-price accuracy is explicitly not the benchmark.

## 6. CAP-XS-01｜Structural Asymmetry Source Mapper

Stable question:

> Why can value, scarcity, duration, carry, volatility or risk become disproportionately concentrated in this research target?

Semantic parent: `Xs`.

### Routed implementations

- equity → value_control_point
- commodity → scarcity_supply_elasticity
- sovereign_rates → duration_convexity_term_premium
- credit → default_spread_recovery_refinancing
- FX → policy_divergence_carry_flow
- monetary_asset → monetary_scarcity_reserve_demand
- derivative → volatility_mispricing_convexity
- crypto → network_scarcity_liquidity_reflexivity

### Universal output

- implementation_family
- asymmetry_source
- mechanism_chain
- concentration_location
- structural_conditions
- durability_or_persistence
- substitutability_or_elasticity
- invalidators
- evidence_refs
- as_of
- degrade_state

Xs explains the **source** of non-linearity. It does not claim the tail is active now (Xa), that price is attractive (V), that the instrument captures the tail well (Xp), or that the portfolio can survive (S).

### Settlement

Settle whether the proposed structural source subsequently manifested in measurable concentration, scarcity, duration sensitivity, carry/flow persistence, reserve demand, volatility/convexity or other routed observables. Failure cases where the structure existed but no investable asymmetry emerged are mandatory.

## 7. Shared benchmark doctrine

Each P0 specification must beat or add stable information over a simpler baseline. Required comparison families include:

- single-variable heuristics
- simple quadrants / percentiles
- simple historical multiples / forward carry
- simple concentration / inventory / duration metrics

Walk-forward/PIT splits, OOS policy, regime holdout, false-alarm accounting, calibration where applicable, multiple-testing control and complexity penalties are mandatory. If complexity adds no incremental information, demote the complex method.

## 8. Implementation handoff after B1

B1 does not implement code. If Human Accepted and merged, the next implementation sequence is proposed as:

1. `B2-R | CAP-R-01 Reference Implementation + Replay`
2. `B2-V | CAP-V-01 Cross-Asset Reference Implementation + Replay`
3. `B2-XS | CAP-XS-01 Routed Reference Implementation + Replay`
4. joint five-asset shadow: NVIDIA / UST30Y / COPPER / GOLD / USDJPY
5. benchmark + ablation before any promotion

Each implementation must reuse the B0 contract and B1 spec without silently changing stable question identity.

## 9. Human Gate

B1 is a specification freeze only.

Human Gate token:

`ACCEPT_R2_3B1_P0_CAPABILITY_CONTRACT_SPECIFICATION`

Acceptance does not imply merge, implementation, promotion, evidence/outcome admission, A9 switch, portfolio authorization or live execution.
