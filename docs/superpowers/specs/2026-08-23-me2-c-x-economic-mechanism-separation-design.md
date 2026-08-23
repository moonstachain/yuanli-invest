# ME2 | C–X Economic Mechanism Separation — Design Spec

Status: `design_accepted_for_written_spec_review`
Date: 2026-08-23
Upstream authority: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`, `ME1_STATE_OBJECT_MODEL_REFRAME`
Program mode: strict sequential `ME2 -> ME3 -> ME4 -> ME5`
Implementation authority: none
Merge authority: none
ME3–ME5 authority: none

Approved design decisions:
- `ACCEPT_ME2_SEMANTIC_MACHINE_SEPARATION_SCOPE`
- `ACCEPT_ME2_D1_CANONICAL_SEMANTIC_ARCHITECTURE`
- `ACCEPT_ME2_D2_MACHINE_CONTRACT_SCHEMA_ARCHITECTURE`
- `ACCEPT_ME2_D3_SUCCESSOR_VALIDATOR_MIGRATION_GATE`

---

## 0. Purpose

ME2 resolves a category error that historical X/convexity work intentionally left open:

> A company or asset can possess structural right-tail economics without the investor position itself being a convex payoff expression.

ME2 therefore separates two planes:

`Underlying Economic Physics != Portfolio Payoff Physics`

It compiles that distinction into successor machine contracts, one-way legacy compatibility, fail-closed relational validation, CI, and Human Review.

ME2 does **not** implement alpha runtime, historical performance claims, portfolio allocation, trading, execution, ME3 Market Clock, ME4 Graduation/Meta Allocation, or ME5 replay/benchmark/ablation authority.

---

## 1. First-principles semantic laws

ME2 freezes the following canonical invariants:

1. `ECONOMIC_RIGHT_TAIL != CONVEX_PAYOFF`
2. `REAL_OPTIONALITY != FINANCIAL_OPTION_PAYOFF`
3. `UNDERLYING_OPTIONALITY_DOES_NOT_PROPAGATE_ENGINE_IDENTITY`
4. `INSTRUMENT_TYPE != RETURN_ENGINE`
5. `STRUCTURE_BELONGS_TO_ITS_CAUSAL_MECHANISM`
6. `POSITIVE_SKEW != ENG-X`
7. `CONVEX_PAYOFF != POSITIVE_EXPECTED_VALUE`
8. `HUMAN_X != MACHINE_ENG_X`

These remain subordinate to the upstream laws:

- `Target != Thesis != Position != Book`
- `Research Pass != Capital Pass`
- `No Silent Thesis Migration`
- `Claim Authority <= Evidence Authority`

### 1.1 Asset right tail is not an engine identity

A target may have network effects, scale economies, bottleneck control, market expansion, real optionality, scarcity, duration, recovery asymmetry or other non-linear economic consequences. These facts belong to the causal economic mechanism that creates them. They do not automatically create `ENG-X` identity.

### 1.2 Real optionality is underlying economics

Expansion, delay, abandon, switch, adjacent-market and platform-extension options alter the future state space of an underlying business or asset. They may support a C thesis, act as R repricing catalysts, or serve as scenario inputs to an X thesis. They are not financial option payoff geometry.

### 1.3 Instrument is not engine

Common stock, options, futures, ETFs or structured instruments do not determine primary engine identity. The engine is determined by the dominant expected source of P&L under an `EngineThesis`.

---

## 2. Canonical semantic architecture

ME2 uses the following conceptual stack:

```text
L0 ResearchTarget
    What is being researched?
        ↓
L1 Underlying Economic Physics
    What causal/economic structures exist in the target?
        ↓
L2 Return Engine
    What is the primary source of expected investor return?
        ↓
L3 EngineThesis
    Why does this mechanism apply to this target and horizon?
        ↓
L4 Position Expression
    Through what instrument/structure is the thesis expressed?
        ↓
L5 Realized Portfolio Payoff
    How do world states become investor P&L?
```

Binding distinction:

`L1 != L2 != L4`

### 2.1 No universal EconomicAsymmetryProfile

ME2 does not replace the old `ConvexityProfile` with a renamed universal `EconomicAsymmetryProfile`.

Underlying economics are represented through mechanism-specific references owned by appropriate ResearchCapabilities or other governed research objects. Example roles may include:

- `value_pool`
- `value_capture`
- `owner_economics`
- `reinvestment`
- `economic_optionality`
- `scarcity`
- `supply_elasticity`
- `duration`
- `issuer_durability`
- `repricing_structure`

ME2 owns the routing semantics, not silent promotion of new capabilities.

---

## 3. ENG-C | Economic Compounding

ME2 refines `ENG-C` as a return mechanism whose primary expected P&L is durable economic compounding:

```text
Value Pool
  -> Value Capture
  -> Owner Economics
  -> ROIC / Cash Conversion
  -> Reinvestment Runway
  -> Owner-Relevant Cash Flow
  -> Intrinsic Value Compounding
```

A C thesis may have enormous positive skew or 10x/100x realized outcomes. Large upside does not transform it into X if the primary source of return remains economic compounding through time.

Real optionality may be referenced in a C thesis where it expands future value pools or reinvestment opportunity sets, but it remains underlying economics.

---

## 4. ENG-X | Portfolio Convexity

ME2 narrows `ENG-X` to a portfolio-payoff mechanism:

> The primary expected P&L is dominated by conditional tail activation and non-linear payoff geometry, net of the price paid for convexity.

Conceptual structure:

`ENG-X = Tail Activation + Payoff Geometry + Price of Convexity`

This is structural composition, not arithmetic.

### 4.1 Tail Activation

`TailActivationSnapshot` answers:

> At this point in time, which tail is changing and under what horizon/evidence state?

It is a PIT snapshot, not a permanent target attribute.

### 4.2 Payoff Geometry

`PayoffGeometryContext` answers:

> How does this specific position map world states into investor payoff?

It belongs to `PositionPassport`, not `ResearchTarget`.

### 4.3 Convexity price semantics

X must account for premium, implied volatility, skew, term structure, theta/carry decay, breakeven, path dependency, liquidity and frictions. `Convex payoff != Positive EV` remains binding.

---

## 5. Human X versus machine ENG-X

The human grammar `势 · 信 · 极｜真 · 价 · 生` remains valid as a navigation projection. Human `X` may still ask where structural asymmetry, tail activation and payoff asymmetry exist.

Machine `ENG-X` is narrower.

Historical human tuple:

`X = (Xs, Xa, Xp)`

Successor machine interpretation:

```text
Human X
  Xs -> routed back to underlying causal/economic mechanisms
  Xa -> TailActivationSnapshot
  Xp -> PayoffGeometryContext

Machine ENG-X
  Tail Activation
  + Payoff Geometry
  + Price of Convexity
```

`Human X != Machine ENG-X` is explicit and non-negotiable.

---

## 6. Stable Core + Engine-Specific Sidecars

ME2 does not create `EngineThesis v2` and does not mutate the accepted `EngineThesis` or `PositionPassport` schema identities.

Architecture:

```text
EngineThesis (stable core)
    ├── CompoundingMechanismAttachment  [ENG-C]
    └── ConvexityMechanismAttachment   [ENG-X]

PositionPassport
    └── PayoffGeometryContext@PIT
```

This preserves the open-world engine ontology. Future ME3 may add an R-specific attachment without turning `EngineThesis` into a God Object.

---

## 7. New machine contracts

ME2 introduces five additive successor schemas under `packages/contracts/schemas/vnext/`.

### 7.1 CompoundingMechanismAttachment | `CMA-*`

Purpose: prove that an `ENG-C` thesis is primarily an economic-compounding thesis.

Required semantic families:

- attachment identity and schema version;
- `engine_thesis_id`, `target_id`, `primary_engine = ENG-C`;
- `primary_return_source = economic_compounding`;
- `economic_mechanism_refs[]`;
- optional `economic_optionality_refs[]`;
- `return_bridge`;
- `price_semantics_refs[]`;
- `dominance_test`;
- PIT/evidence/counter-evidence/falsifier fields;
- all capital/trading/runtime authorities false.

`return_bridge` must connect, at minimum, value creation/control to value capture, owner economics and reinvestment. A large TAM, narrative or technology lead without an owner-economics bridge is insufficient.

### 7.2 ConvexityMechanismAttachment | `XMA-*`

Purpose: prove that an `ENG-X` thesis is primarily a non-linear portfolio-payoff thesis.

Required semantic families:

- attachment identity and schema version;
- `engine_thesis_id`, `target_id`, `primary_engine = ENG-X`;
- `primary_return_source = nonlinear_payoff_geometry`;
- `tail_activation_refs[]`;
- `convexity_price_refs[]`;
- optional `underlying_state_refs[]` for context only;
- `state_to_payoff_hypothesis`;
- `dominance_test`;
- PIT/evidence/counter-evidence/falsifier fields;
- all capital/trading/runtime authorities false.

Network effects, TAM, moat, value capture, historical multibag performance or other target-level right-tail facts cannot be sufficient X identity fields.

### 7.3 TailActivationSnapshot | `TAS-*`

Purpose: represent PIT conditional tail state.

Required semantic families:

- identity, target, horizon;
- `as_of`, `known_as_of`, `knowledge_cutoff`;
- `tail_side = upside | downside | two_sided`;
- `activation_state = inactive | watch | activating | active | unknown`;
- state/evidence/counter-evidence refs;
- probability semantics;
- calibration semantics;
- staleness and authority.

A numeric estimated probability is prohibited unless the object also contains an explicit probability definition, horizon, base-rate reference and calibration reference.

### 7.4 PayoffGeometryContext | `PGC-*`

Purpose: represent the payoff map of one governed position expression.

Required semantic families:

- identity;
- `position_passport_id`, `engine_thesis_id`, `instrument_ref`;
- PIT validity fields;
- `geometry_family`, direction semantics;
- downside and upside geometry;
- expiry/path/leverage semantics;
- premium/IV/skew/term-structure/carry-decay/breakeven refs where applicable;
- liquidity/friction refs;
- `geometry_dependency = auxiliary | material | dominant`;
- authority fields false.

Geometry is described before it is judged. This allows linear, leveraged-linear, convex, concave, capped, binary and path-dependent structures to be represented without forcing all positions into a convexity label.

### 7.5 LegacyConvexityProjection | `LCP-*`

Purpose: one-way compatibility view of historical `ConvexityProfile v1`.

Required constants:

- `projection_only = true`
- `machine_authority = false`
- `write_back_prohibited = true`
- `engine_inference_prohibited = true`

Historical `right_tail` fields map only to a legacy underlying-structure view. Historical `left_tail` fields map only to a legacy issuer-durability view. Historical `convexity_state` / `left_tail_state` become non-authoritative legacy labels.

No projection field may auto-create or auto-assign a new EngineThesis.

---

## 8. Cardinality and relational law

ME2 freezes the following cardinalities:

- `EngineThesis(ENG-C) : CMA = 1 : 0..1`; `qualified/active` C theses require exactly one current CMA.
- `EngineThesis(ENG-X) : XMA = 1 : 0..1`; `qualified/active` X theses require exactly one current XMA.
- `XMA : TailActivationSnapshot = 1 : 1..N` historical snapshots; one authoritative current PIT snapshot per governed context.
- `PositionPassport : PayoffGeometryContext = 1 : 0..N` PIT versions.
- `eligible/active ENG-X PositionPassport` requires exactly one current PGC.
- C/R Passports may optionally carry PGC when instrument geometry is relevant.

All target/thesis/passport IDs must resolve through the accepted ME1 object graph.

---

## 9. Primary Return Source / Dominance Test

Both CMA and XMA must contain a machine-readable `dominance_test`:

- `linear_counterfactual`
- `geometry_dependency`
- `tail_state_dependency`
- `expected_pnl_driver`
- `rationale`

C-valid state:

- `expected_pnl_driver = economic_compounding`
- `geometry_dependency != dominant`

X-valid state:

- `expected_pnl_driver = nonlinear_payoff_geometry`
- `geometry_dependency = dominant`
- valid tail activation reference required

If a thesis changes from compounding-dominant to geometry-dominant, the primary engine may not be edited in place. The old thesis must close/settle and a new EngineThesis identity is required.

### 9.1 Static linear exposure rule

A static linear exposure cannot satisfy ENG-X merely because the underlying has large upside, positive skew or a strong right-tail narrative.

A common-stock position can only qualify for ENG-X if the governed Position-level structure actually creates dominant non-linear payoff geometry through explicit contingent/dynamic/financing rules. Instrument labels alone never qualify or disqualify an engine.

---

## 10. Historical successor map

### 10.1 CAP-XS-01

Historical identity remains immutable:

- historical contract authority: retained;
- historical meaning: retained;
- redefined in place: prohibited;
- future canonical output authority: removed for the ME2 successor world;
- future reference implementation authority as one universal Xs runtime: removed;
- successor policy: typed route split by actual causal mechanism.

Historical routes are interpreted as follows:

- equity value control/network/scale -> underlying economic mechanism;
- commodity scarcity/elasticity -> underlying economic mechanism;
- rates duration/term premium -> underlying pricing physics / repricing context;
- credit default/recovery/refinancing -> claim/issuer economics;
- FX policy divergence/carry/flow -> reality/repricing mechanism;
- monetary scarcity/reserve demand -> underlying economic structure;
- crypto network/scarcity/liquidity -> underlying and reflexive structure;
- derivative volatility/contract convexity -> possible X price/payoff-geometry route.

ME2 does not silently create new ResearchCapabilities for these routes. Capability admission remains governed by the existing ResearchCapability lifecycle and Registry.

### 10.2 Historical ConvexityProfile v1

The existing schema identity and blob remain immutable historical authority. It gains zero future canonical write authority.

### 10.3 StructuralRightTailProfile

This historical candidate never became canonical schema authority. ME2 marks it:

`superseded_before_canonical_schema_creation`

Future ME2 implementation must not create this schema.

### 10.4 TailActivationSnapshot

The historical candidate is promoted into an explicit ME2 successor contract, subject to ME2 implementation and Human Review.

### 10.5 PayoffConvexityContext

The historical candidate is superseded by the explicit semantic successor `PayoffGeometryContext`.

---

## 11. Superseded future implementation path

The old `R2.3-B2` implementation plan contains the assumption:

`X := (Xs, Xa, Xp) remains indivisible`

and proposes a universal `CAP-XS-01` reference runtime.

ME2 freezes that future path as:

- historical plan remains immutable;
- `CAP-XS-01 Routed Reference Implementation` under the old indivisible-X assumption is `superseded_before_execution_by_ME2`;
- `do_not_execute = true` for future canonical implementation under that plan;
- replacement = ME2 typed successor contracts plus later capability-specific governance.

This is a successor decision, not a rewrite of the historical plan.

---

## 12. Validator Constitution

Implementation will add:

`python scripts/validate_me2_c_x_separation.py`

The validator will follow the accepted ME1 pattern: local JSON Schema checks plus relational fail-closed checks.

Validation layers:

- `V0 Historical Non-Regression`
- `V1 Successor Identity Integrity`
- `V2 Reference Integrity`
- `V3 Engine Attachment Cardinality`
- `V4 C/X Mechanism Separation`
- `V5 Dominance Test Integrity`
- `V6 Tail Activation PIT & Calibration`
- `V7 Position / Payoff Geometry Integrity`
- `V8 Legacy One-Way Compatibility`
- `V9 Authority / Scope Integrity`
- `V10 Hard Negative Suite`

### 12.1 V0 Historical Non-Regression

At minimum verify:

- legacy `convexity-profile.schema.json` blob unchanged;
- historical CAP-XS-01 specification unchanged;
- historical Extreme Engine methodology document unchanged;
- ME0 successor policy unchanged;
- ME1 EngineThesis and PositionPassport schema identities unchanged.

### 12.2 V4 Semantic Firewall

Fail closed when any of the following is treated as sufficient ENG-X identity:

- TAM / market expansion;
- network effect / scale / moat / winner-take-most;
- value capture / reinvestment runway;
- positive skew / historical 10x or 20x outcome;
- `ConvexityProfile.convexity_state`;
- historical Xs strength;
- option instrument type;
- real optionality.

### 12.3 V6 Probability discipline

Numeric tail probabilities require explicit calibration, probability definition, horizon and base-rate reference. Otherwise only ordinal activation state is allowed.

### 12.4 V8 Legacy firewall

Legacy projection is read-only, non-authoritative, write-back prohibited and engine-inference prohibited.

### 12.5 V9 Authority firewall

All ME2 successor objects must keep these authorities false:

- portfolio weight;
- position sizing;
- trading/execution;
- live execution;
- alpha-runtime authority;
- capability promotion;
- new engine creation;
- ME3/ME4/ME5 authorization.

---

## 13. Hard Negative and Hard Positive test matrix

Hard negatives must include at least:

- HN-01: big TAM -> ENG-X : FAIL
- HN-02: strong network effects -> ENG-X : FAIL
- HN-03: historical 20x stock -> ENG-X : FAIL
- HN-04: legacy `ConvexityProfile=convex` -> ENG-X : FAIL
- HN-05: legacy `Xs=strong` -> ENG-X : FAIL
- HN-06: option instrument -> automatic ENG-X : FAIL
- HN-07: ENG-X without valid TailActivationSnapshot : FAIL
- HN-08: eligible/active X Passport without current PGC : FAIL
- HN-09: tail probability without calibration contract : FAIL
- HN-10: C thesis with dominant geometry dependency : FAIL / new thesis required
- HN-11: X thesis with auxiliary/material-only geometry dependency : FAIL
- HN-12: real optionality -> financial convexity : FAIL
- HN-13: historical CAP-XS auto-creates new mechanism authority : FAIL
- HN-14: legacy projection write-back : FAIL
- HN-15: C -> X primary-engine mutation in same thesis ID : FAIL
- HN-16: any new ME2 schema gains portfolio/trading/runtime authority : FAIL

Hard positives must include at least:

- HP-01: NVDA common stock + ENG-C + valid CMA : PASS
- HP-02: NVDA LEAPS + ENG-C + valid CMA + PGC(material) : PASS
- HP-03: long call + ENG-X + XMA + TailActivationSnapshot + PGC(dominant) : PASS
- HP-04: historical ConvexityProfile -> read-only LegacyConvexityProjection : PASS
- HP-05: same ResearchTarget simultaneously carries independent C and X theses : PASS

The test suite must prove that ME2 distinguishes X correctly rather than merely suppressing it.

---

## 14. Migration strategy

### M0 | Ledger Preservation

Freeze historical schema IDs, file/blob identities, CAP-XS contract, ME0/ME1 authority and old plan history.

### M1 | Schema Parallel

Add the five ME2 successor schemas alongside all legacy objects. No in-place rewrite and no bulk migration.

### M2 | Relational Shadow Qualification

Use deterministic fixtures to prove ontology correctness only:

- same Target can carry C and X theses;
- C and X attachments route correctly;
- Position geometry remains separate from target economics;
- legacy projection is one-way;
- hard negatives fail closed.

M2 is not alpha research and makes no historical return-performance claim.

### M3 | Contract Authority Cutover

Only after exact-head CI green, ME2 Human Acceptance, separate merge authorization, merge, and post-merge closure may the successor contracts obtain future canonical contract authority.

Even after M3:

- `live_runtime_authority = false`
- `alpha_claim_authority = false`
- `portfolio_authority = false`
- `ME3_authorized = false`

---

## 15. CI integration

ME2 uses the existing single repository-gates workflow. It does not create a second CI framework.

The contracts job gains:

`python scripts/validate_me2_c_x_separation.py`

Placement should preserve architecture order:

`YIP0 -> ME0 -> ME1 -> ME2 -> YIM0 -> full unittest discovery`

Existing governance checks, leak guard, manifest verification and full unittest discovery remain unchanged and mandatory.

---

## 16. Human Review Gate

Final ME2 Human Review requires 18/18 PASS:

1. Economic Right Tail != Convex Payoff.
2. Real Optionality != Financial Option Payoff.
3. Human X != Machine ENG-X.
4. Structure is routed by causal mechanism.
5. CAP-XS-01 historical identity is preserved.
6. Old universal CAP-XS future implementation path is explicitly superseded.
7. ConvexityProfile v1 is immutable.
8. CMA correctly governs qualified/active ENG-C theses.
9. XMA correctly governs qualified/active ENG-X theses.
10. Xa successor is PIT TailActivationSnapshot.
11. Xp successor belongs to Position-level PayoffGeometryContext.
12. Instrument != Engine.
13. Dominant geometry is required for ENG-X.
14. Legacy compatibility is one-way and non-polluting.
15. No Silent Thesis Migration remains enforced.
16. Hard Negative / Hard Positive suites pass.
17. No capability/engine/portfolio/runtime authority leakage occurs.
18. ME0/ME1 historical non-regression passes.

Required Human decision after implementation review:

`ACCEPT_ME2_C_X_ECONOMIC_MECHANISM_SEPARATION`

Human Acceptance does not imply merge.

Separate merge authorization remains required:

`AUTHORIZE_ME2_MERGE`

---

## 17. Post-merge closure and sequential program gate

ME2 is not complete merely because a PR merges.

Post-merge closure must verify on exact `main` head:

- repository-gates green;
- ME2 validator green;
- full unit tests green;
- Canon status/projection convergence;
- ME2 completion receipt.

Completion state must converge to:

- `latest_completed_architecture_stage = ME2_COMPLETE`
- `roadmap_next_unapproved_stage = ME3`
- `ME3_authorized = false`

Only a later explicit Human authorization may start ME3.

---

## 18. Planned implementation surface

Implementation planning may target the following files after written-spec approval:

```text
docs/architecture/me2/
  ME2-C-X-ECONOMIC-MECHANISM-SEPARATION-AUTHORITY-v0.1.md
  ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json
  ME2-HARD-NEGATIVE-MATRIX-v0.1.json
  ME2-STATE.json
  fixtures/...

packages/contracts/schemas/vnext/
  compounding-mechanism-attachment.schema.json
  convexity-mechanism-attachment.schema.json
  tail-activation-snapshot.schema.json
  payoff-geometry-context.schema.json
  legacy-convexity-projection.schema.json

scripts/
  validate_me2_c_x_separation.py

tests/
  test_me2_c_x_separation.py

.github/workflows/ci.yml
```

Historical accepted files remain immutable unless a separate explicit successor/projection update is authorized; ME2 must not rewrite them in place.

---

## 19. Scope exclusions

ME2 explicitly does not:

- implement `ENG-R` Market Clock or reflexive runtime;
- run live or shadow alpha production;
- claim historical excess returns;
- perform portfolio sizing or allocation;
- implement Graduation or Meta Allocation;
- authorize trading or execution;
- promote new ResearchCapabilities from the typed successor routes;
- create new return engines;
- mutate historical receipts or accepted legacy schemas;
- authorize ME3, ME4 or ME5.

---

## 20. Design acceptance boundary

This written spec compiles the already-approved D1/D2/D3 architecture into one repository artifact.

Written-spec approval authorizes only the transition to implementation planning via the repository's normal engineering workflow. It does not authorize implementation, Human Acceptance, merge, post-merge completion, or ME3.
