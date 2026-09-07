# YMQ4-G1｜NVIDIA Genesis Pair Design v0.1

Status: `HUMAN_ACCEPTED_DESIGN / SPEC_CANDIDATE`

Human acceptance token:

`ACCEPT_YMQ4_G1_NVIDIA_GENESIS_PAIR_DESIGN`

Date: 2026-09-07

Branch: `feat/ymq4-g1-nvidia-genesis-pair-20260907`

---

## 1. Mission

`YMQ4-G1` is the first real vertical-slice battle for **Dynamic Repricing Intelligence**.

It does **not** attempt to prove a general macro-quant system, produce alpha, or authorize capital action.

Its purpose is narrower and harder:

> Under strict point-in-time constraints, can the same frozen research protocol identify the dominant repricing driver of the same asset across two different regimes, expose uncertainty and competing explanations, and emit a reproducible ResearchCapability result with an immutable receipt?

Target: **NVIDIA / NVDA**.

Core research chain:

`Shock → Dynamic Beta → Driver Contribution → Property Drift → Repricing → Falsifier`

Stable question:

> **At this point in time, what force is most plausibly dominating NVIDIA's repricing, through what transmission path, with what uncertainty, and what evidence would falsify that explanation?**

---

## 2. Constitutional Invariants

This battle inherits the `yuanli-invest` ResearchCapability law and may not silently override it.

1. `Claim Authority <= Evidence Authority`.
2. Research output is a typed state, never a scalar master score.
3. Provider/vendor fields are adapters, never Capability identity.
4. Point-in-time semantics, publication lag, revisions and evidence cutoff are mandatory.
5. Missing evidence, stale data, under-identification and model disagreement must degrade state explicitly.
6. Correlation, feature importance, Granger precedence or dynamic beta cannot self-promote to causal proof.
7. `Research PASS != Capital PASS`.
8. No target price, portfolio weight, position size, buy/sell/hold, or live execution field is permitted.
9. `ResearchStateSnapshot` is a product/runtime projection of a CapabilityResult, not the Canon ontology center.
10. GitHub remains Canon; Supabase remains runtime/evidence/state plane; Python/DuckDB remains quant compute plane.

---

## 3. Genesis Pair Design

### 3.1 Genesis T0

`2022-08-26T16:00:00-04:00` (New York)

Reason for selection:

- NVIDIA had already disclosed a material Q2 FY23 revenue shortfall versus prior guidance, with Gaming weakness and continued Data Center growth.
- The Federal Reserve's Jackson Hole communication on 2022-08-26 reinforced a restrictive policy path and willingness to tolerate slower growth to restore price stability.
- The date therefore creates a genuine competing-mechanism environment rather than a single-story case.

Primary competing explanations at T0:

- discount-rate / real-rate shock;
- liquidity / broad risk-off shock;
- NVIDIA-specific earnings deterioration;
- broad-tech common-factor repricing;
- narrative effects, if evidence supports them.

### 3.2 Held-out Transfer T1

`2023-05-25T16:00:00-04:00` (New York)

T1 is a **held-out transfer point** and is forbidden for model, factor, window or threshold tuning.

Reason for selection:

- NVIDIA's 2023-05-24 earnings release materially changed the earnings and AI-related information set, including a large forward revenue guide and explicit accelerated-computing / generative-AI framing.
- T1 creates a same-asset challenge for potential driver rotation from rate/liquidity dominance toward earnings / AI-reality / narrative dominance.

### 3.3 Genesis-Pair Law

The G1 method is frozen using information and design decisions available before evaluating T1.

No post-T1 tuning is allowed for:

- factor selection;
- transformation family;
- rolling windows;
- beta estimator family;
- drift distance family;
- drift thresholds;
- common-factor controls;
- output semantics.

Any change after seeing T1 must create a new version and invalidate the previous transfer test.

---

## 4. Scope: Five Input Packs Only

G1 intentionally limits scope to five input packs.

### 4.1 Rates

Minimum candidate observables:

- U.S. 2Y nominal yield;
- U.S. 10Y nominal yield;
- U.S. 10Y real yield or defensible real-rate proxy.

Purpose:

- discount-rate pressure;
- policy-path repricing;
- duration sensitivity.

### 4.2 Liquidity

Minimum candidate observables:

- Federal Reserve balance-sheet state / change;
- USD or broad financial-conditions proxy;
- optional funding-stress proxy if PIT-quality is available.

Purpose:

- liquidity tightening / easing;
- external funding pressure;
- broad risk appetite versus actual liquidity distinction.

### 4.3 Earnings

Minimum candidate observables:

- reported revenue;
- prior guidance;
- new guidance;
- Data Center revenue / growth;
- Gaming revenue / growth;
- gross-margin or margin guide where available;
- earnings-revision event pulse.

Purpose:

- company-reality impulse;
- earnings surprise;
- segment mix change.

### 4.4 Narrative

G1 narrative evidence is deliberately narrow.

Allowed first-version inputs:

- timestamped NVIDIA official releases;
- timestamped NVIDIA earnings-call / investor-relations language if available in auditable form;
- timestamped Federal Reserve policy language relevant to the discount-rate mechanism.

Disallowed in G1 unless separately admitted later:

- social-media sentiment;
- unlabeled news sentiment;
- retrospective media summaries;
- large NLP corpora without strict publication timestamps;
- any narrative field that cannot prove `known_as_of`.

Narrative is represented initially as a typed event / diffusion candidate, not a fake continuous sentiment truth.

### 4.5 Price

Minimum candidate observables:

- NVDA price / return;
- QQQ price / return;
- SPY price / return;
- realized volatility;
- relative strength;
- optional residual versus broad-tech factor.

Purpose:

- confirmation;
- broad-tech common-factor hard negative;
- residual decomposition.

---

## 5. Canonical Observation Contract

Every admitted runtime observation must map to the existing Supabase YMQ4 PIT schema and carry at minimum:

```text
economic_id
target_id
domain
observed_at
release_at
known_as_of
vintage_at
value_num | value_text
unit
frequency
transformation
source_id
provider
provider_series_id
authority_class
revision_status
provenance
```

Hard PIT rule:

```text
known_as_of <= invocation.evidence_cutoff
```

Historical replay must never substitute a later revised value for a value that was unavailable at T0.

For observations where a formal vintage does not exist, `vintage_at` may be null only if `revision_status = not_applicable` or an explicit provider policy explains the semantics.

---

## 6. Transformation Layer

Raw levels are not directly treated as shocks.

Allowed G1 transformation families:

- `level`;
- `delta`;
- `delta2`;
- rolling z-score;
- surprise versus prior expectation / guidance where auditable;
- event pulse;
- breadth where the underlying panel is explicit.

Each transformed field must preserve lineage back to the raw observation.

Examples:

```text
rate_shock_t = zscore(Δ real_yield_t)
```

```text
earnings_guidance_surprise = (new_guidance - prior_reference) / declared_scale
```

Narrative in G1 defaults to event-state semantics rather than an unvalidated continuous score.

---

## 7. Quant Model Stack

The modeling philosophy is:

`Simple → Robust → Dynamic → Challenge`

### B0｜Fixed Beta Baseline

A simple, interpretable baseline model is mandatory.

Conceptual form:

```text
r_NVDA,t = α + β' X_t + ε_t
```

Purpose:

- establish the static exposure baseline;
- create a model that the dynamic approach must eventually beat or add information over.

### B1｜Rolling Beta

Pre-registered windows:

- short window: **63 trading days**;
- long window: **252 trading days**.

Outputs:

- `beta_short`;
- `beta_long`;
- standard errors / uncertainty bands where feasible;
- missing-data and conditioning warnings.

### B2｜TVP / Kalman Dynamic Beta

Conceptual state equation:

```text
β_t = β_{t-1} + η_t
```

Observation equation:

```text
r_t = α_t + X_t'β_t + ε_t
```

Authority boundary:

- TVP/Kalman estimates dynamic exposure;
- it does not prove causal mechanism by itself.

### B3｜Challenge Layer

The first challenge layer is deliberately simple:

- compare NVDA with QQQ and SPY;
- separate broad-tech / broad-market common-factor movement before upgrading NVIDIA-specific explanation;
- surface residual / unexplained return explicitly.

No HMM, deep learning, regime neural net or black-box feature importance is allowed in G1.

---

## 8. Driver Contribution

The core explanatory runtime object is not beta alone.

For driver `k`:

```text
Contribution(i,k,t) = β_hat(i,k,t) × Shock(k,t)
```

Required output categories:

- Rates;
- Liquidity;
- Earnings;
- Narrative;
- Common Factor;
- Residual / Unexplained.

`Dominant Driver` is a model attribution label subject to uncertainty, not a causal fact.

A driver may only be called dominant when:

- contribution magnitude is meaningfully larger than competing modeled contributions;
- uncertainty is not prohibitive;
- the hard-negative layer does not fully explain the move;
- required evidence is available PIT.

Otherwise emit `mixed`, `unknown`, or `insufficient_evidence` semantics.

Residual must always be visible in the Dossier and may not be silently redistributed across named drivers.

---

## 9. Property Drift

Property drift compares short-horizon and long-horizon exposure vectors.

Initial distance candidate:

```text
Drift_t = 1 - cosine(beta_short_t, beta_long_t)
```

The exact metric remains replaceable in later versions, but G1 freezes cosine distance for the Genesis Pair.

Thresholds are calibrated using only the pre-T0 historical distribution of the drift statistic:

- `< P50` → `stable`;
- `P50–P75` → `mixed`;
- `P75–P90` → `migrating`;
- `> P90` → `candidate_new_property`;
- insufficient evidence → `unknown`.

These labels are product-state semantics, not ontological claims that the asset has permanently changed species.

---

## 10. Pre-registered Hypotheses

### H-G1-A｜2022 Rate / Liquidity Dominance Candidate

At T0, the system should test whether NVIDIA short-horizon repricing is more strongly explained by rate/liquidity/broad-tech shocks than by an AI narrative explanation.

This is a hypothesis, not a pre-written conclusion.

A result where earnings dominates is admissible if the evidence supports it.

### H-G1-B｜2023 Driver Rotation Candidate

Using the frozen T0 method at held-out T1, the system should test whether earnings / AI-reality / narrative contribution rises materially and whether the dynamic exposure/property state changes relative to the T0 regime.

If no material rotation or drift appears, the hypothesis fails.

### H-G1-C｜No Universal Driver

No single driver is granted permanent explanatory privilege for NVIDIA across both points.

If the same fixed driver explains both points without meaningful incremental value from dynamic modeling, YMQ4's dynamic hypothesis is weakened.

---

## 11. Hard Negatives and Competing Explanations

Mandatory hard negatives:

1. **Broad Tech Common Factor** — NVIDIA only followed QQQ.
2. **Broad Market Risk-Off** — NVIDIA only followed SPY / market beta.
3. **Liquidity Panic** — apparent narrative convergence is actually system-wide liquidity stress.
4. **Narrative After Price** — the story appeared after price moved.
5. **Earnings Event Confound** — a company-specific earnings shock explains what looks like macro beta drift.
6. **Short-Window Spurious Beta** — apparent drift is unstable estimation noise.
7. **Vintage Leakage** — a later data revision contaminated T0.

Each CapabilityResult must emit at least one strongest competing explanation and one discriminating observation that could separate the leading explanation from the alternative.

---

## 12. Runtime Object Flow

The end-to-end G1 path is:

```text
GitHub Canon
  ↓
Supabase PIT Observation
  ↓
CapabilityInvocation
  ↓
Python / DuckDB Quant Compute
  ↓
CapabilityResult
  ↓
ResearchStateSnapshot
  ↓
ResearchReceipt
```

The existing Supabase `ymq4` schema is reused:

- `ymq4.provider_series_map`;
- `ymq4.observations`;
- `ymq4.replay_cases`;
- `ymq4.capability_invocations`;
- `ymq4.capability_results`;
- `ymq4.research_state_snapshots`;
- `ymq4.research_receipts`.

No additional Supabase table is required for G1 unless implementation proves a hard contract gap.

Any schema change discovered during implementation requires a new design amendment rather than silent expansion.

---

## 13. Quant-Workspace Implementation Boundary

`moonstachain/quant-workspace` remains the reference quant runtime, but G1 must not use the existing trading-strategy namespace as the semantic parent.

Recommended module boundary:

```text
src/ymq4/
├── contracts.py
├── transforms.py
├── fixed_beta.py
├── rolling_beta.py
├── tvp_kalman.py
├── contribution.py
├── property_drift.py
├── challenge.py
├── runtime.py
└── receipt.py

tests/ymq4/
```

Research-state generation and trading-signal generation remain separate concerns.

`src/strategy/` must not become the parent of YMQ4.

---

## 14. Product Output: Research Dossier

The first G1 Dossier must surface, at minimum:

```text
Target / As Of
What Changed?
Dominant Driver
Secondary Drivers
Common-Factor Explanation
Property State
Property Drift State
Reliability State
Residual / Unexplained
Strongest Alternative
Discriminating Observation
Strongest Falsifier
Evidence Cutoff
Model Version
Receipt ID
```

The Dossier may not display Buy/Sell, target price, recommended weight, expected return promise or live execution instruction.

---

## 15. G1 Victory Conditions

G1 is a **vertical-slice runtime proof**, not a Capability validation battle.

### G1 PASS requires all of the following

1. **PIT Integrity** — zero known future-data leakage.
2. **Five-Pack Coverage** — Rates, Liquidity, Earnings, Narrative and Price each resolve to a typed state, or explicitly degrade to Unknown / Missing.
3. **Compute Reproducibility** — Fixed Beta, Rolling Beta and TVP/Kalman run deterministically for the same frozen inputs and version.
4. **Attribution Output** — Driver Contribution and Residual are emitted.
5. **Property Comparison** — short/long exposure vectors and drift state are emitted.
6. **Challenge Output** — at least one competing explanation and hard negative are surfaced.
7. **Runtime Round-Trip** — Invocation → Result → State Snapshot → Receipt is persisted.
8. **Receipt Reproduction** — the same receipt envelope can reproduce the same typed state under the same code/data version.
9. **Held-out Transfer** — T1 is evaluated without retuning the T0 method.
10. **No Capital Authority Leak** — no prohibited action field enters the result or product projection.

### G1 does not prove

- stable alpha;
- portfolio superiority;
- general causal validity;
- cross-asset transferability;
- TVP superiority over simple models;
- Shadow Runtime qualification;
- production readiness.

Those belong to later benchmark and transfer gates.

---

## 16. Failure and Kill Semantics

Permitted output states:

- `success`;
- `partial`;
- `unknown`;
- `fail_closed`.

Examples of `fail_closed`:

- PIT vintage cannot be established;
- source publication time is materially ambiguous;
- data alignment makes the model non-identifiable;
- insufficient pre-T0 history for the registered window;
- model output is numerically unstable and cannot be bounded.

If Dynamic Beta / TVP later fails to add stable information over Fixed Beta + Rolling Beta + common-factor baseline, the dynamic method must be demoted or removed rather than protected by narrative preference.

---

## 17. Source Authority for Genesis Events

The following source classes are preferred for G1 evidence:

1. NVIDIA Investor Relations / official news releases for company facts and timestamps.
2. Federal Reserve official publications / speeches for policy communication.
3. Primary or institutionally authoritative market/macro providers for rates, balance-sheet and price series.
4. Provider metadata or archived releases sufficient to establish `known_as_of` and vintage semantics.

Provider mappings are adapters and must remain separable from economic definitions.

---

## 18. Proposed Execution Sequence After Spec Approval

The implementation plan should decompose G1 into the following order:

1. freeze Genesis Pair replay-case records and evidence cutoff semantics;
2. freeze provider/economic-id map for the five packs;
3. build PIT ingestion/read adapters;
4. write transform tests first;
5. implement B0 Fixed Beta baseline;
6. implement B1 Rolling Beta;
7. implement B2 TVP/Kalman;
8. implement contribution and residual attribution;
9. implement property drift;
10. implement challenge/hard-negative output;
11. implement Supabase invocation/result/receipt round-trip;
12. run T0;
13. freeze T0 outputs and method version;
14. run held-out T1 with no retuning;
15. issue G1 Reality Receipt and classify PASS / PARTIAL / FAIL.

---

## 19. Explicit Non-Goals

G1 will not:

- ingest all U.S. equities;
- build a generic macro platform;
- build production-grade NLP;
- build a full portfolio optimizer;
- add autonomous trading;
- claim AI narrative causality from text frequency alone;
- tune for Sharpe ratio;
- promote YMQ4 to validated / operating / compounding CBM maturity;
- replace CAP-R-01, Market Clock, C/R/X, Price/Value Gate or Survival Gate.

---

## 20. Design Freeze Summary

`YMQ4-G1｜NVIDIA Genesis Pair` is frozen as:

```text
Target
  NVIDIA / NVDA

Genesis T0
  2022-08-26 16:00 ET

Held-out T1
  2023-05-25 16:00 ET

Input Packs
  Rates / Liquidity / Earnings / Narrative / Price

Model Stack
  Fixed Beta → Rolling Beta → TVP/Kalman

Core Outputs
  Driver Contribution
  Driver Rotation
  Property Drift
  Residual
  Competing Explanation
  Falsifier

Hard Negative
  Broad Tech / Broad Market Common Factor

Runtime
  GitHub Canon → Supabase PIT → Python/DuckDB Compute → Supabase Result/Receipt

Victory
  Same frozen protocol runs at both PIT points and emits reproducible typed ResearchCapability state + immutable receipt.

Non-Claim
  No alpha validation. No capital authority. No production promotion.
```

---

## 21. Human Gate

Design accepted by human principal with token:

`ACCEPT_YMQ4_G1_NVIDIA_GENESIS_PAIR_DESIGN`

This acceptance authorizes writing and reviewing this specification.

It does **not yet** authorize implementation-plan acceptance, code merge, runtime promotion, evidence/outcome Canon admission, portfolio action, or production Shadow Runtime.
