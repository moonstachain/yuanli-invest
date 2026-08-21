# RP0 Stage-1｜Capability Incremental Truth Contract v0.1

## 0. Status and Authority

This document is a **design-only specification** for `RP0｜Yuanli Reality Proof Program` Stage 1.

Human design acceptance token already supplied:

`ACCEPT_RP0_STAGE1_CAPABILITY_INCREMENTAL_TRUTH_CONTRACT_DESIGN`

This acceptance authorizes only the written design specification. It does **not** authorize implementation, Benchmark execution, Registry admission, Canon promotion, Capability maturity promotion, production runtime, portfolio action, or trading.

---

## 1. Strategic Purpose

RP0 exists to move Yuanli Investment Research from **Research Capability Canon Formation** into **Reality Proof**.

Stage 1 asks one question:

> Under strict point-in-time, replayable, and ablatable conditions, does a ResearchCapability produce independent, repeatable, attributable research information beyond a simpler, cheaper, mature baseline?

RP0 is not another ontology, Registry, Replay engine, Benchmark engine, or Agent framework. It is the **reality-settlement layer above existing capabilities and B2 runtime infrastructure**.

Core law:

> **A Mother Capability survives only if it earns independent incremental research value.**

Elegance, popularity, explanatory usefulness, expert pedigree, and narrative coherence do not constitute Reality Proof.

---

## 2. Relationship to Existing Architecture

### 2.1 B2 owns execution infrastructure

R2.3-B2 remains the owner of:

- deterministic Research Runtime;
- PIT invocation and evidence-cutoff semantics;
- immutable replay fixtures;
- five-asset Shadow harness;
- Benchmark execution primitives;
- Ablation primitives;
- typed `ResearchState` / `ResearchReceipt` outputs.

RP0 must reuse these rather than create a second Replay or Benchmark stack.

### 2.2 RP0 owns reality doctrine

RP0 Stage 1 owns:

- `RealityTrial` contract;
- baseline doctrine;
- incremental-truth evaluation doctrine;
- complexity accounting;
- failure learning;
- cross-capability settlement;
- Stage-1 disposition;
- admission to RP0 Stage 2 testing.

### 2.3 Non-authority boundary

A Stage-1 result may authorize only further RP0 testing.

It never implies:

- Registry admission;
- Canon promotion;
- Capability lifecycle promotion;
- production runtime;
- portfolio action;
- trading or live execution.

`Research PASS != Capital PASS` remains binding.

---

## 3. RP0 Five-Case Reality Set v0.1

Stage 1 inherits the five cross-asset targets already used by B2 so that RP0 measures incremental research value rather than fixture-construction skill.

### RP0-RC-01｜NVIDIA — AI Infrastructure Reality

Mother question:

> Do AI capex, adoption, bottleneck, structural value capture, narrative, and price-implied expectations still support the AI infrastructure thesis at T0?

Primary capability families: `P`, `Xs`, `V`, `N`, `E`.

Primary test: distinguish genuine structural reality from expectations already embedded in price.

### RP0-RC-02｜UST30Y — Long-Duration Regime

Mother question:

> Which mechanisms dominate long-duration US Treasury repricing at T0: growth, inflation, liquidity, term premium, policy reaction, fiscal/financial mechanics, or competing combinations?

Primary capability families: `R`, `V`, Financial Mechanics, `E`.

Primary test: whether decomposed macro/financial mechanics outperform a simpler inflation + policy-expectation framework.

### RP0-RC-03｜Copper — Real Economy × Scarcity

Mother question:

> Is copper repricing driven by cyclical demand, durable structural supply bottlenecks, or narrative amplification?

Primary capability families: `P`, `Xs`, `N`, `V`, `E`.

Primary test: whether scarcity is durable and causally relevant rather than a post-price narrative.

### RP0-RC-04｜Gold — Monetary Asset Reality

Mother question:

> Which mechanisms dominate gold repricing at T0: real rates, reserve demand, monetary risk, liquidity, scarcity, or narrative?

Primary capability families: `R`, `Xs`, `V`, `N`, `E`.

Primary test: separate long-horizon monetary narrative from the contemporaneous pricing driver.

### RP0-RC-05｜USDJPY — Policy Divergence × Flow × Reflexivity

Mother question:

> Is USDJPY at T0 primarily explained by policy divergence, carry, flow, risk appetite, liquidity, or narrative reflexivity?

Primary capability families: `R`, `Xs`, `V`, `N`, `E`.

Primary test: cross-asset generalization beyond equities.

### Case law

Every Reality Case must freeze exactly one research question, one T0, one evidence cutoff, one baseline set, one preregistered research-state expectation, one falsifier, and one settlement rule.

Forbidden:

- changing the question after settlement data are visible;
- selecting capabilities after outcomes are known;
- allowing settlement data into T0 inputs;
- using narrative completeness as a substitute for benchmark improvement;
- equating realized return with research correctness;
- promoting a Capability from one successful Case.

---

## 4. RealityTrial Contract

The atomic unit of Stage 1 is:

`RealityTrial := Capability × RealityCase × T0 × FrozenEvidence × BaselineSet × SettlementRule`

Every trial must contain at least:

1. `trial_id` — immutable unique identity;
2. `reality_case_id`;
3. `capability_id`;
4. `capability_version`;
5. `t0`;
6. `evidence_cutoff`;
7. `input_snapshot_hash`;
8. `baseline_spec_ids`;
9. `research_state_spec`;
10. `falsifier`;
11. `settlement_rule`;
12. `evaluation_contract`.

After T0, trial semantics are immutable. Outcome and settlement evidence may be appended, but historical T0 inputs, baselines, capability version, falsifier, and evaluation contract may not be rewritten.

---

## 5. Baseline Doctrine

A Capability cannot prove itself against a weak straw-man baseline.

### B0｜Naive Baseline

Examples:

- historical mean;
- persistence / unchanged-state assumption;
- recent direction;
- simple momentum.

Purpose: verify the Capability beats trivial information.

### B1｜Practitioner Baseline

Represents a competent analyst using a small mature variable set.

Illustrative examples:

- NVIDIA: revenue / EPS revision + capex trend + valuation multiple;
- Gold: real yield + USD + reserve-demand proxy;
- UST30Y: inflation + policy expectation + term-premium proxy.

Rule:

> Beating B0 but not the best valid B1 does not establish incremental Capability value.

### B2｜Component / Cheap-Proxy Baseline

Tests whether the Capability's theoretical structure adds value beyond a cheaper approximation.

Examples:

- narrative diffusion/velocity/saturation vs simple mention growth;
- structural bottleneck mechanism vs scarcity indicator only;
- ordered `L → E → N` transitions vs unordered `L + E + N` variables.

If the cheap proxy is equivalent within the preregistered tolerance, the complex Capability should be simplified rather than rewarded for complexity.

---

## 6. Evaluation Contract

Stage 1 evaluates a **Research Reality Profile**, not a trading return score.

### M1｜State Accuracy

Did the Capability's stated research condition settle correctly?

Examples include earnings revision direction, bottleneck persistence, narrative saturation, expectation stress, or regime transition.

### M2｜Uncertainty Calibration

When output is `underidentified`, `mixed`, `insufficient_evidence`, or high uncertainty, do future outcomes exhibit correspondingly greater uncertainty?

Core principle:

> A good system must know when it does not know.

### M3｜Incremental Information

Compare the Capability with the **best valid preregistered baseline**, not only B0.

Allowed qualitative settlement states:

- `positive_increment`;
- `neutral_increment`;
- `negative_increment`;
- `insufficient_evidence`.

No scalar `RP0 score`, `Capability score`, `Force score`, or `PNX score` is permitted.

### M4｜Decision Relevance

Did the Capability materially alter a research-decision state such as:

- thesis strengthened;
- thesis weakened;
- thesis unresolved;
- additional evidence required;
- valuation tension increased;
- structural invalidator activated;
- uncertainty increased?

Forbidden outputs include target price, buy/sell/hold, recommended weight, target weight, position size, broker action, and live execution.

### M5｜Complexity Cost

Every trial must account for the cost of complexity, including at least:

- data dependency;
- provider dependency;
- runtime cost;
- human-review burden;
- interpretability burden;
- failure surface;
- maintenance burden.

The relevant question is not whether a Capability is more sophisticated, but whether its information gain earns its complexity cost.

---

## 7. Ablation Contract

Every important Mother Capability must survive three ablation classes where applicable.

### A1｜Remove

`Full stack` vs `Full stack − Capability X`.

If removal does not materially reduce preregistered research quality, independent Mother status is challenged.

### A2｜Replace

`Capability X` vs `Simple Proxy X'`.

If the proxy is effectively equivalent, preferred disposition is `SIMPLIFY`.

### A3｜Mechanism Break

Preserve similar inputs while breaking the claimed theoretical structure.

Examples:

- ordered transition vs unordered variables;
- causal/mechanism chain vs undifferentiated feature bundle.

If mechanism structure provides no incremental value, that structure cannot be defended merely by theoretical elegance.

---

## 8. Mother Capability Survival Law

### MC-01｜Independent Incremental Value Law

A Mother Capability does not survive because it is elegant, intuitive, famous, or explanatory. It survives only by earning independent incremental research value.

Evidence for survival may include one or more of:

1. independent information increment;
2. independent uncertainty/calibration increment;
3. independent decision-state increment;
4. inability to be replaced by a materially simpler proxy;
5. cross-case or cross-asset generalization.

Persistent failure to demonstrate any of these should trigger consideration of `Profile`, `Composite`, `Helper`, simplification, or rejection rather than repeated narrative defense.

---

## 9. Stage-1 Dispositions

Exactly six governed dispositions are allowed:

- `PROMOTE_FOR_STAGE2` — sufficient incremental value to enter RP0 Stage-2 testing;
- `KEEP_SHADOW` — promising but underpowered or not yet sufficiently generalized;
- `SIMPLIFY` — useful signal exists but the complex form does not earn its cost;
- `MERGE_INTO_COMPOSITE` — no stable independent value, but useful as a component;
- `REJECT_NO_INCREMENT` — no demonstrated incremental research value;
- `INSUFFICIENT_EVIDENCE` — evidence does not support a valid settlement.

`INSUFFICIENT_EVIDENCE` must not silently map to `KEEP_SHADOW` or PASS.

---

## 10. Negative Reality Registry

RP0 must preserve failures as first-class learning objects rather than hiding them from benchmark summaries.

Minimum failure taxonomy:

- `theory_failure`;
- `measurement_failure`;
- `provider_failure`;
- `pit_failure`;
- `implementation_failure`;
- `generalization_failure`;
- `calibration_failure`;
- `complexity_failure`;
- `no_incremental_value`;
- `underpowered_evidence`.

The strategic purpose is to make `known_failure_regimes` empirically useful so future agents can learn when **not** to invoke a Capability.

The name “Negative Reality Registry” in RP0 denotes a reality-proof learning ledger. It does **not** imply mutation of the canonical `registry/**` namespace unless separately designed and authorized later.

---

## 11. RP0-G1｜Incremental Truth Gate

Inputs:

- RealityTrial results;
- baseline results;
- ablation results;
- failure receipts;
- complexity profile;
- evidence-authority record.

Outputs:

- `CapabilityRealityProfile`;
- exactly one Stage-1 disposition.

A `CapabilityRealityProfile` is a structured vector of findings and failure regimes, not a scalar score.

Only `PROMOTE_FOR_STAGE2` grants:

`stage2_test_authorized = true`

All Stage-1 results retain:

- `registry_promotion_authorized = false`;
- `canon_promotion_authorized = false`;
- `production_runtime_authorized = false`;
- `portfolio_action_authorized = false`;
- `trading_authorized = false`.

---

## 12. Minimal RP0 Stage-1 Scope

RP0 v0.1 should remain deliberately small:

- exactly five Reality Cases;
- approximately 15–25 RealityTrials;
- initial focus on `R`, `P`, `N`, `Xs`, `V`, and `E`;
- `S` primarily remains a Stage-2 decision/survival constraint;
- `Xa` and `Xp` are deferred unless needed by a separately approved Stage-1 extension.

This is a minimum viable scientific test, not a claim of statistical universality.

---

## 13. Success and Failure Criteria

RP0 Stage 1 succeeds when it can credibly distinguish among:

- incremental value;
- no incremental value;
- excessive complexity;
- evidence insufficiency;
- component-only value;
- failure to generalize.

RP0 Stage 1 does **not** succeed by maximizing PASS rates.

Hard-negative outcomes are valid and desirable if the experiment is well specified.

Stage-1 should fail closed if any of the following occurs:

- a Capability beats only the naive baseline but not the practitioner baseline;
- removing the Capability produces no material deterioration;
- a cheap proxy is equivalent to the complex Capability;
- apparent value exists only in one asset and fails elsewhere without justified scope restriction;
- uncertainty outputs are poorly calibrated;
- hindsight, revised, or post-cutoff data leak into T0;
- replay cannot reproduce the result;
- complexity cost overwhelms information gain;
- failure cases are excluded after results are known.

---

## 14. Stage-1 → Stage-2 Boundary

RP0 adopts the two-stage mother architecture:

`Capability Incremental Truth → End-to-End Decision Value`

Stage 1 settles whether individual capabilities deserve to participate in Stage 2.

Stage 2 will separately define whether surviving capabilities, when composed in an end-to-end research workflow, improve human research decisions relative to a simple decision baseline.

Stage 2 is **not defined or authorized by this document**. It requires a separate design review before implementation planning.

---

## 15. Design Acceptance and Next Gate

Accepted design token:

`ACCEPT_RP0_STAGE1_CAPABILITY_INCREMENTAL_TRUTH_CONTRACT_DESIGN`

Current artifact state after this document is written:

`written_design_candidate_for_human_review`

Next gate:

`RP0_STAGE1_WRITTEN_SPEC_HUMAN_REVIEW`

No implementation plan or implementation work may begin until the written specification itself is reviewed and explicitly approved.
