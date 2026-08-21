# XC0-A｜Political-Economy Constraint × Cross-Asset Transmission Architecture & Profile Freeze

Status: `design_candidate_for_human_review`

Base: `main@f26fee209e0f5582d3c650b803a6c277da00d180`

Design branch: `xc0-a/political-economy-cross-asset-transmission-design-v0.1`

## 1. Purpose

XC0-A freezes the architecture for a bounded practitioner-derived research track that converts political-economy constraints and cross-asset trading intuition into machine-auditable ResearchCapability profiles without creating a new Yuanli investment ontology.

The mother question is:

> **When political, fiscal, monetary, geopolitical or institutional constraints change at the margin, through which financial transmission mechanisms do those changes propagate into rates, FX, credit, commodities and equities, and where does observable repricing still lag the changed state?**

XC0-A is an architecture and profile freeze only. It does not validate a theory, implement an algorithm, create a new Registry object, run a benchmark, qualify Shadow, promote a capability, or authorize capital action.

## 2. Upstream authority and isolation boundary

XC0-A inherits the accepted Yuanli Investment Research OS and may not redefine it.

Binding upstream contracts:

- `docs/os-vnext/CONSTITUTION.md`
- `docs/architecture/r2_3b0/R2-3B0-CAPABILITY-CONTRACT-ARCHITECTURE-FREEZE-v0.1.md`
- `docs/architecture/qxm1/QXM1-FINANCIAL-MECHANICS-CAPABILITY-CANDIDATE-PACK-v0.1.md`
- `docs/architecture/qxm2/QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`

Current inherited invariants:

1. `one_core_three_worlds_three_gates_one_loop` remains unchanged.
2. `P = P.capital + P.asset`; no fourth human world may be created.
3. `R` remains a typed machine decomposition/context for `P.capital`.
4. `X := (Xs, Xa, Xp)` remains indivisible.
5. `Claim Authority <= Evidence Authority`.
6. `Asset form is not pricing model`.
7. canonical output is typed `ResearchState`, never a scalar macro/Force score.
8. Research OS does not emit target price, recommended weight, position size, buy/sell or live execution.
9. PIT evidence, evidence cutoff, falsifier, benchmark, settlement and receipt requirements remain mandatory.

### 2.1 Hard isolation from QXM1/QXM2

QXM1 already owns the accepted Financial Mechanics candidate pack. QXM2 already hardens exactly six QXM1 objects with primary theory and empirical evidence.

Therefore XC0-A MUST NOT:

- create a second `Financial Mechanics` ontology;
- rename, split, merge or replace any QXM1 candidate;
- add a seventh QXM2 candidate;
- mutate `CAP-R-01` or `CAP-V-01` mother semantics;
- write into QXM2 source/evidence/theory/hypothesis/benchmark artifacts;
- claim that practitioner macro intuition upgrades QXM2 evidence authority;
- modify `registry/theories/`, `registry/hypotheses/`, `registry/benchmarks/`, `registry/capabilities/` or `canon/` during XC0-A.

XC0-A is additive only as a **profile architecture/staging track** over existing capability identities.

## 3. Architecture decision

XC0-A does not create a new top-level capability family. It compiles six bounded profiles that attach to already-frozen ResearchCapability identities.

| XC0 profile | Parent capability | Stable question |
|---|---|---|
| `XC-P1-POLITICAL-ECONOMY-CONSTRAINT-MAP` | `CAP-R-01` | Which political, fiscal, institutional and balance-sheet constraints currently bind the feasible policy set? |
| `XC-P2-POLICY-REACTION-FUNCTION-SHIFT` | `CAP-R-01` | Has the policy reaction function changed under the current constraint set, and what observable evidence supports that shift? |
| `XC-P3-CROSS-ASSET-TRANSMISSION-GRAPH` | `CAP-R-01` | Through which state-dependent financial channels should an identified shock propagate across asset classes? |
| `XC-P4-EXPECTATION-SURPRISE-GAP` | `CAP-V-01` | What was priced before the event, what new information arrived, and what residual expectation gap remains unresolved? |
| `XC-P5-DOMINANT-PRICING-NARRATIVE` | `CAP-N-01` + bounded `CAP-N-02` dependency | Which future assumption currently has the highest marginal pricing power, and is that assumption diffusing, saturating or fracturing? |
| `XC-P6-CROSS-ASSET-CONFIRMATION-DIVERGENCE` | `CAP-R-02` | Do rates, FX, credit, commodities, equities and volatility confirm the same state transition, or does the divergence require an alternative explanation? |

No XC profile has independent Canon authority. Profile outputs inherit the authority ceiling of their parent capability and their evidence.

## 4. Governing causal chain

XC0-A freezes the following research chain:

```text
Political-Economy Constraint
  -> Shock / New Information
  -> Policy Reaction Function
  -> Transmission Hub + Secondary Channels
  -> Pre-Event Expectations
  -> Surprise
  -> First-Round Cross-Asset Repricing
  -> Residual Expectation Gap
  -> Narrative / Expectation Reweighting
  -> Cross-Asset Confirmation or Divergence
  -> Revision / Falsification / Settlement
```

This chain is not a universal one-way causal law. Every edge must remain conditional, typed and falsifiable.

## 5. Seven XC laws

### LAW-XC-01｜No Universal Transmission Hub

No single variable, including interest rates, is the permanent center of all cross-asset transmission.

Each event must identify a candidate `shock_family`, `transmission_hub`, secondary channels and alternative mechanisms.

### LAW-XC-02｜Constraint Before Intent

Research the feasible policy set before inferring the preferences or intentions of political or policy actors.

`constraint != preference != narrative`.

### LAW-XC-03｜Surprise Before Level

A high or low macro variable is not new information by itself. Operational news is the difference between realization and frozen pre-event expectation, subject to revision and measurement semantics.

### LAW-XC-04｜Transmission Before Asset Direction

A political, geopolitical or policy event may not jump directly to an asset-direction conclusion. The mechanism and expected cross-asset signature must be explicit first.

### LAW-XC-05｜Cross-Asset Confirmation Is Conditional

A market that leads in one regime is not permanently causal or leading in another regime.

### LAW-XC-06｜Narrative Is a State Variable, Not Truth Authority

The dominant story may explain what the market is paying for. Narrative strength does not establish causal truth or fundamental correctness.

### LAW-XC-07｜Practitioner Alpha Does Not Create Theory Authority

Practitioner conversations, forecasts, P&L or trading success may seed hypotheses and observables. They cannot self-promote to primary theory, causal proof, empirical validation, capability qualification or Canon.

## 6. Profile contracts

XC0-A freezes profile-specific state shapes only. A later implementation must still satisfy all eleven blocks of the universal ResearchCapability contract through its parent capability.

### 6.1 XC-P1｜Political-Economy Constraint Map

Minimum typed state:

```text
PoliticalEconomyConstraintState
├── jurisdiction
├── as_of
├── fiscal_space
├── debt_service_pressure
├── refinancing_pressure
├── expenditure_rigidity
├── revenue_capacity
├── monetary_independence_constraint
├── financial_stability_constraint
├── electoral_constraint
├── trade_external_constraint
├── geopolitical_constraint
├── market_absorption_constraint
├── binding_constraints[]
├── non_binding_constraints[]
├── competing_interpretations[]
├── evidence_refs[]
├── confidence_semantics
└── falsifiers[]
```

Hard boundary: no `empire_decline_score`, political destiny score or deterministic policy forecast.

### 6.2 XC-P2｜Policy Reaction Function Shift

Minimum typed state:

```text
ReactionFunctionState
├── policy_actor
├── target_variables[]
├── constraint_variables[]
├── prior_reaction_function
├── candidate_reaction_function
├── evidence_of_shift[]
├── communication_shift
├── implementation_shift
├── credibility_state
├── persistence_band
├── competing_reaction_functions[]
├── evidence_refs[]
└── falsifiers[]
```

Hard boundary: a speech, personnel appointment or isolated action does not by itself establish a durable reaction-function shift.

### 6.3 XC-P3｜Cross-Asset Transmission Graph

Minimum edge contract:

```text
TransmissionEdge
├── source_node
├── target_node
├── edge_type
├── expected_sign
├── expected_lag
├── regime_condition
├── asset_scope
├── evidence_authority
├── competing_edge
├── observable_mapping
└── falsifier
```

Minimum graph state:

```text
CrossAssetTransmissionState
├── shock_family
├── candidate_transmission_hub
├── primary_edges[]
├── secondary_edges[]
├── feedback_edges[]
├── expected_cross_asset_signature[]
├── competing_graphs[]
├── unresolved_identification[]
├── evidence_refs[]
└── degrade_state
```

Hard boundary: correlation, price lead, Granger lead or sequence alone does not establish structural causality.

### 6.4 XC-P4｜Expectation-Surprise Gap

Required decomposition:

```text
pre_event_expectation
  -> realized_information
  -> surprise_component
  -> first_round_repricing
  -> residual_expectation_gap
```

Minimum typed state:

```text
ExpectationGapState
├── event_id
├── as_of_pre_event
├── pre_event_consensus
├── market_implied_expectation
├── realized_information
├── surprise_component
├── first_round_repricing
├── residual_gap
├── disagreement_state
├── horizon
├── evidence_refs[]
├── confidence_semantics
└── falsifiers[]
```

Hard boundary: `residual_gap` is not target price or expected return.

### 6.5 XC-P5｜Dominant Pricing Narrative

Minimum typed state:

```text
DominantPricingNarrativeState
├── candidate_narratives[]
├── dominant_narrative
├── dominant_future_assumption
├── marginal_price_sensitivity_state
├── narrative_velocity
├── narrative_saturation
├── narrative_price_translation
├── competing_narratives[]
├── regime_break_signals[]
├── reunderwrite_required
├── evidence_refs[]
└── confidence_semantics
```

Hard boundary: profile state is expectation-regime analysis, not truth certification and not an automatic trading signal.

Any detected regime break must route into the existing bounded `CAP-N-02` re-underwrite semantics; XC0-A does not invent a parallel break detector.

### 6.6 XC-P6｜Cross-Asset Confirmation & Divergence

Minimum typed state:

```text
CrossAssetDivergenceState
├── rates_signal
├── fx_signal
├── credit_signal
├── commodity_signal
├── equity_signal
├── volatility_signal
├── agreement_state
├── leading_market_candidate
├── lagging_market_candidate
├── transmission_consistency
├── alternative_explanations[]
├── resolution_triggers[]
├── evidence_refs[]
└── confidence_semantics
```

Hard boundary: divergence is a research state requiring resolution, not automatic proof that one market is wrong.

## 7. XC staging input object｜ShockPacket

XC0-A introduces `ShockPacket` only as a staging/runtime research object. It is not a tenth Registry and has no independent admission authority.

```text
ShockPacket
├── shock_id
├── as_of
├── evidence_cutoff
├── jurisdiction
├── policy_actor
├── shock_family
│   ├── monetary
│   ├── fiscal
│   ├── trade
│   ├── regulatory
│   ├── geopolitical
│   ├── sovereign_credit
│   ├── financial_stability
│   └── supply
├── pre_event_expectation
├── realized_information
├── surprise_component
├── expected_persistence
├── binding_constraints[]
├── candidate_reaction_functions[]
├── candidate_transmission_hub
├── first_order_channels[]
├── second_order_channels[]
├── expected_cross_asset_signature[]
├── competing_mechanisms[]
├── disconfirming_signature[]
└── evidence_refs[]
```

A ShockPacket must preserve PIT semantics. Evidence or prices observed after the frozen cutoff may not be backfilled into its pre-event fields.

## 8. Source authority and practitioner material

The practitioner source set that motivated XC0 includes long-form investment conversations, monthly/weekly macro reviews and related synthesis material.

XC0-A freezes their authority as:

```text
source_class = practitioner_research_source | internal_research_synthesis
authorized_use = hypothesis_seed | mechanism_seed | observable_seed | failure_question
authorized_as_primary_theory = false
authorized_as_independent_empirical_evidence = false
authorized_as_causal_identification = false
authorized_as_benchmark_result = false
authorized_as_trading_authority = false
```

A profitable practitioner outcome does not prove the mechanism. A losing outcome does not automatically falsify every structural claim. Future settlement must preserve original receipts and attribution boundaries.

## 9. Evidence hardening handoff

A later `XC0-C` may use the QXM2 evidence-first pattern without modifying QXM2 artifacts:

```text
Practitioner Seed
  -> Primary / Seminal Theory
  -> Atomic Mechanism Claim
  -> Independent Empirical Evidence
  -> Boundary / Contradiction / Competing Evidence
  -> Observable Mapping
  -> Falsifiable Shadow Hypothesis
  -> Benchmark Seed
  -> Human Epistemic Review
```

`XC0-C` must use a separate XC staging root and may not imply QXM2 admission authority.

## 10. Replay and benchmark architecture reserved for later stages

XC0-A freezes evaluation families but does not execute them.

### 10.1 PIT replay families

Candidate Gold Replay families:

- reaction-function regime shift;
- international policy coordination / FX regime change;
- institutional-constraint crisis;
- credit/funding crisis;
- policy-path surprise;
- joint fiscal-monetary shock;
- inflation/tightening shock;
- geopolitical/supply shock.

Candidate China extensions may later cover RMB regime change, deleveraging/trade conflict, policy pivot and fiscal/property/FX interaction, subject to PIT evidence availability.

### 10.2 Hard negative families

Mandatory negative design families:

1. politically large event with no binding financial-constraint change;
2. one market moves first but cross-asset confirmation fails;
3. narrative changes but the event was already priced;
4. identical macro surprise has different sign under different regimes;
5. profitable asset move is driven by a mechanism different from the pre-registered thesis;
6. apparent cross-asset sequence disappears after publication-lag/PIT correction.

### 10.3 Benchmark families

Reserved benchmark questions:

- Shock Classification;
- Transmission Hub Identification;
- Cross-Asset Signature Fidelity;
- Expectation-Surprise Incremental Information;
- Regime-Dependent Sign / Lag Improvement;
- Cross-Asset Divergence Resolution.

Required simple baseline families must include at least:

```text
M0 = raw macro levels
M1 = rates-only
M2 = macro-surprise-only
M3 = simple financial-conditions / volatility baseline
M4 = narrative-only
M5 = XC without political constraint layer
M6 = XC without cross-asset confirmation
M7 = full XC
```

Complexity that fails to add stable PIT/OOS information over simpler baselines must be removed or demoted.

## 11. Runtime relationship to Market Clock and Yuanli OS

XC0 is not a replacement for the Market Clock or PNX-S.

The intended handoff is:

```text
P | long-horizon structural reality
  -> XC-P1/P2 | political-economy constraint + reaction function
  -> ShockPacket
  -> XC-P3 | transmission graph
  -> Market Clock | L/E/N runtime state
  -> XC-P4 | priced expectation / residual surprise gap
  -> XC-P5 | dominant expectation regime
  -> XC-P6 | cross-asset confirmation/divergence
  -> V / Xa / Xp re-underwrite when routed
  -> S remains Portfolio Survival authority
```

Human metaphor:

- PNX = strategic map;
- XC0 = financial transmission gearbox;
- Market Clock = runtime dashboard;
- V/Xa/Xp/S = pricing, tail, instrument and survival controls.

These are explanatory metaphors only; they do not create new ontology.

## 12. Planned XC0-A implementation artifacts after spec approval

If this written design is Human Approved, XC0-A implementation should create only an architecture/staging pack such as:

```text
docs/architecture/xc0_a/
├── XC0-A-ARCHITECTURE-PROFILE-FREEZE-v0.1.md
├── XC0-A-PROFILE-CONTRACTS-v0.1.json
├── XC0-A-SHOCK-PACKET-SCHEMA-v0.1.json
├── XC0-A-TRANSMISSION-EDGE-SCHEMA-v0.1.json
├── XC0-A-ISOLATION-MATRIX-v0.1.json
├── XC0-A-HUMAN-REVIEW-CARD-v0.1.md
└── XC0-A-STATE.json

scripts/validate_xc0_a_architecture.py
tests/test_xc0_a_architecture.py
.github/workflows/ci.yml   # append only if required to register the validator
```

No Registry or Canon paths are planned for XC0-A.

## 13. Machine validation requirements for XC0-A implementation

The later validator must fail if any of the following occurs:

### Architecture integrity

- profile count is not exactly six;
- any profile creates an independent top-level capability identity;
- parent capability IDs differ from the frozen mapping;
- any profile introduces a fourth human world;
- any scalar macro/Political Economy/Force score is declared canonical.

### QXM isolation

- any QXM1/QXM2 candidate is renamed, replaced, split or merged;
- XC0 claims a seventh QXM2 candidate;
- `CAP-R-01` or `CAP-V-01` mother semantics are mutated;
- XC0 writes formal Registry/Canon admission objects;
- practitioner material is marked as primary theory or independent empirical evidence.

### Evidence / PIT

- ShockPacket lacks `as_of`, `evidence_cutoff`, pre-event expectation or falsifier-compatible disconfirming signature;
- post-event evidence is allowed to populate frozen pre-event fields;
- causal labels are inferred merely from correlation, price lead or Granger lead.

### Authority boundary

- target price, upside percentage, recommended weight, position size, buy/sell/hold or live execution authority appears;
- architecture acceptance is represented as capability qualification, benchmark PASS, Shadow qualification or Canon promotion.

## 14. XC0-A state machine

```text
design_candidate_for_human_review
  -> design_human_accepted
  -> implementation_started
  -> machine_validation_complete
  -> candidate_ready_for_human_review
  -> human_accepted_ready_for_merge
  -> accepted_merged
```

Each transition requires a separate receipt. No state implies the next.

## 15. Explicit non-goals

XC0-A does not authorize:

- external theory admission;
- new TheoryObject / HypothesisObject / BenchmarkObject / Capability Registry entries;
- live Wind data ingestion;
- production runtime;
- event prediction;
- deterministic political forecasting;
- price targets;
- recommended weights;
- position sizing;
- buy/sell/hold;
- broker integration or live execution;
- QXM1/QXM2 mutation;
- Market Clock Canon promotion;
- A9 operational-canon switch.

## 16. Design acceptance criteria

The written XC0-A design is acceptable only if Human Review confirms all of the following:

1. XC0 remains a profile/staging architecture, not a new ontology.
2. Exactly six profiles attach to existing capability identities.
3. QXM1 and QXM2 remain semantically and physically isolated.
4. `Constraint -> Shock -> Reaction Function -> Transmission -> Expectation Gap -> Repricing` is the governing research chain.
5. no universal interest-rate hub is assumed.
6. practitioner material remains hypothesis/mechanism seed authority only.
7. ShockPacket and TransmissionEdge preserve PIT, evidence and falsification requirements.
8. typed ResearchState replaces macro scores and directional trading outputs.
9. replay, hard-negative, benchmark and ablation families are reserved but not executed.
10. implementation remains bounded to `docs/architecture/xc0_a/`, validator/tests and minimal CI registration.

Design Human Gate token:

`ACCEPT_XC0_A_POLITICAL_ECONOMY_CROSS_ASSET_TRANSMISSION_DESIGN`

After this design gate is accepted, the next step is to write the implementation plan. Implementation must not begin before that approval.
