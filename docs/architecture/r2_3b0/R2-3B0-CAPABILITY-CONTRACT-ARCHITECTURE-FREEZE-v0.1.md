# R2.3-B0 | Capability Contract Architecture Freeze v0.1

Status: `candidate_started`

## 1. Purpose

R2.3-B0 does not implement alpha models. It freezes the contract architecture that every machine-callable `ResearchCapability` must obey before implementation, benchmark, shadow qualification, or Canon promotion.

The contract must preserve the accepted OS:

- `one_core_three_worlds_three_gates_one_loop`
- Human navigation: **势 · 信 · 极｜真 · 价 · 生**
- `P = P.capital + P.asset`
- `R` is typed machine decomposition/context for `P.capital`, not a fourth human world.
- `X := (Xs, Xa, Xp)` is indivisible.
- `Xs = Structural Asymmetry Source`; Value Control Point is an equity-specialized implementation.
- `Asset form is not pricing model`.
- `Claim Authority <= Evidence Authority`.
- `Lower-level truth does not imply higher-level authorization`.
- Research OS produces typed research state, not target price, recommended weight, buy/sell, or live execution.

## 2. The durable unit

A `ResearchCapability` is a versioned, testable, falsifiable research question plus its evidence, input, inference, output, benchmark, settlement, runtime and governance contracts.

A Capability is **not**:

- a prompt;
- a vendor field list;
- a report template;
- a single factor without theory/falsifier;
- a scalar P/N/X/Force score;
- a target-price model;
- a trading action.

## 3. Universal Capability Contract

Every Capability contract MUST contain the following eleven blocks.

### C1 | Identity & Stable Question

Required:

- `capability_id`
- `name`
- `contract_version`
- `stable_question`
- `semantic_parent`
- `maturity_state`
- `owner_scope`

The stable question is the durable identity. Algorithm families may change without silently changing the question.

### C2 | Scope & Routing

Required:

- eligible `asset_forms`
- eligible `pricing_archetypes`
- authority level(s) in `L0-L4`
- binding / auxiliary / irrelevant module semantics where applicable
- `router_dependencies`

A0 and A1 are separate: `A0 = asset_form`, `A1 = pricing_archetype`.

### C3 | Theory & Causal Mechanism

Required:

- `theory_ids`
- `hypothesis_ids`
- `causal_mechanism`
- `assumptions`
- `competing_mechanisms`
- `claim_boundary`

Theory references may include practitioner hypotheses, but source class and evidence authority must remain explicit.

### C4 | Evidence Contract

Required:

- `evidence_policy`
- `minimum_evidence_authority`
- `claim_types`
- `source_requirements`
- `as_of_required = true`
- `point_in_time_required = true`
- `evidence_cutoff_required = true`
- `falsifier_required = true`

Law: **Claim Authority <= Evidence Authority**.

A current-event claim, causal mechanism, narrative interpretation and asset-attribution claim must remain separately typed.

### C5 | Input Contract

Required:

- `canonical_input_fields`
- economic definitions rather than vendor-native ontology
- units / frequency / publication lag / revision semantics
- missingness policy
- allowed transformations
- provider mappings kept outside the economic definition

No vendor-specific field may become the Capability identity.

### C6 | Inference Contract

Required:

- `algorithm_families`
- `identification_assumptions`
- `state_transition_logic`
- `uncertainty_representation`
- `simpler_baselines`
- `known_failure_modes`

Causal labels require causal identification support. Correlation, feature importance, price lead or Granger lead do not self-promote to causal effect.

### C7 | Output Contract

The canonical output is a typed `ResearchState`, never one scalar master score.

Required:

- `state_type`
- typed state dimensions
- direction / magnitude band / persistence band where relevant
- uncertainty / confidence semantics
- `evidence_refs`
- `as_of`
- stale / insufficient-evidence semantics
- downstream dependencies

Prohibited canonical outputs:

- target price;
- upside percentage as research truth;
- recommended portfolio weight;
- position size;
- buy / sell / hold;
- live order / execution instruction;
- weighted P/N/X/E/V/S/R composite score.

### C8 | Falsification & Failure Contract

Required:

- `falsification_rules`
- `revision_triggers`
- `known_failure_regimes`
- `degrade_behavior`
- `fail_closed_states`

Allowed fail-closed states include `insufficient_evidence`, `research_only`, `stale`, and `unsupported`.

A Capability must become less authoritative when its evidence, timing or regime validity degrades.

### C9 | Benchmark & Qualification Contract

Required before promotion beyond specification:

- simple baseline(s)
- point-in-time split policy
- walk-forward / OOS policy when applicable
- regime holdout
- false-alarm accounting
- calibration requirement for probabilistic outputs
- multiple-testing policy
- complexity penalty
- failure receipts

Complexity that does not add information over a simpler baseline must be removed or demoted.

### C10 | Settlement & Learning Contract

Required:

- `settlement_horizon`
- `settlement_observables`
- `settlement_rule`
- `replay_policy`
- `revision_rule`
- outcome leakage prohibition

The system must preserve what was knowable at the original `as_of` time. Future outcomes cannot be backfilled into historical evidence.

### C11 | Runtime, Receipt & Governance Contract

Every invocation MUST carry an `InvocationEnvelope`:

- `canon_revision`
- `canon_hash`
- `capability_id`
- `capability_contract_version`
- `research_target`
- `A0_asset_form`
- `A1_pricing_archetype`
- `as_of`
- `evidence_cutoff`
- `provider/runtime`

Every result MUST carry a `ResearchReceipt` that preserves the invocation envelope, called algorithm family, evidence references, output state version and failure/degrade state.

Governance boundaries:

- Capability contract acceptance is not Capability promotion.
- Capability promotion is not Evidence/Outcome admission.
- Research PASS is not Capital PASS.
- Research OS does not authorize target price, recommended weight, buy/sell or live execution.
- A9 operational Canon switch remains separately governed.

## 4. P0 Contract Profiles

R2.3-B0 freezes profiles for three P0 identities only; it does not implement them.

### CAP-R-01 | Regime Causal Decomposition

Stable question:

> What causal capital regime currently governs discount rates, risk appetite, funding conditions and cross-asset capital allocation?

Minimum typed state:

- growth
- inflation
- liquidity
- risk_appetite
- term_premium
- funding_stress
- policy_reaction_function

Each material state must support direction, magnitude band, persistence band, evidence refs, competing mechanisms and confidence semantics.

Hard boundaries:

- R is not a fourth human world.
- No single yield level defines the regime.
- Liquidity and risk appetite are distinct.
- No scalar macro score.
- Regime state may constrain downstream authority without erasing valid bottom-up research truth.

### CAP-V-01 | Price-Implied Expectations

Stable question:

> What future state or operating assumptions are already embedded in current price?

The mother contract must route to asset-specific model families, including:

- equity: reverse DCF / implied operating assumptions;
- sovereign rates: implied policy path / inflation / term premium;
- credit: implied default / spread / recovery;
- commodity: futures curve / scarcity / marginal cost;
- FX: forward / rate differential / carry;
- monetary asset: real-rate / monetary-risk / reserve-demand interpretation;
- derivative: IV / skew / term structure / implied distribution.

Hard boundaries:

- Great asset is not great investment.
- Target price is not canonical output.
- Identification ambiguity must be surfaced, not hidden.
- Model family is routed by asset form + pricing archetype, not by one universal valuation formula.

### CAP-XS-01 | Structural Asymmetry Source Mapper

Stable question:

> Why can value, scarcity, duration, carry, volatility or risk become disproportionately concentrated in this research target?

Required implementation-family routing:

- equity -> value_control_point
- commodity -> scarcity_supply_elasticity
- sovereign_rates -> duration_convexity_term_premium
- credit -> default_spread_recovery_refinancing
- FX -> policy_divergence_carry_flow
- monetary_asset -> monetary_scarcity_reserve_demand
- derivative -> volatility_mispricing_convexity
- crypto -> network_scarcity_liquidity_reflexivity

Hard boundaries:

- Value Control Point is equity-specialized, not universal Xs ontology.
- Xs identifies asymmetry source; it does not manufacture a calibrated probability.
- Xs does not substitute for Xa activation, Xp payoff geometry, V price gate or S survival gate.

## 5. N-02 reserved contract requirement

R2.3-A reserved a bounded re-underwrite latency rule for `CAP-N-02`.

R2.3-B0 freezes the semantics, not a universal clock value:

- a detected expectation-regime break MUST trigger typed V/Xa/Xp re-underwriting;
- the SLA must be explicit and capability/asset/time-sensitivity specific;
- an expired SLA without completed re-underwrite MUST degrade downstream state to `research_only` or `stale`;
- R2.3-B0 does not invent one arbitrary number of days for all assets.

## 6. Lifecycle

```text
architecture_frozen
  -> contract_specified
  -> reference_implemented
  -> replay_qualified
  -> benchmark_qualified
  -> shadow_qualified
  -> canon_candidate
  -> human_gate
  -> canon
```

No step is implied by the prior one.

## 7. B0 acceptance criteria

R2.3-B0 can pass Human Review only if:

1. one universal contract architecture governs all future Capability implementations;
2. P0 profiles preserve accepted R2.3-A semantics;
3. provider independence, point-in-time evidence, falsification, benchmark and settlement are first-class;
4. InvocationEnvelope + ResearchReceipt make every result version-reproducible;
5. no scalar score, target price, recommended weight, trading action or live execution authority is introduced;
6. N-02 stale/research-only degradation semantics are frozen without arbitrary universal latency;
7. CI validates the architecture deterministically.

Human Gate token:

`ACCEPT_R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE`
