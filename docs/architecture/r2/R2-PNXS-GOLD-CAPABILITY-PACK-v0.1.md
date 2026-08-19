# R2｜PNX-S Gold Capability Pack v0.1

## 0. Purpose

R2 is the first governed compilation of Yuanli's investment-research methodology into machine-callable Research Capability objects. It does **not** attempt to cover hundreds of signals. It compiles the 12 R0 Gold seeds into a small, inspectable, falsifiable pack.

The invariant chain for every capability is:

```text
Theory → Hypothesis → Factor or Algorithm → Benchmark → Skill
```

R2 freezes the specification layer. Reference implementations and benchmark execution belong to R4; Wind AI / Codex runtime-specific interfaces belong to R3.

## 1. The 12 Gold Capabilities

| Domain | Capability ID | Name | R2 maturity |
|---|---|---|---|
| P | `CAP-P-001-TECHNOLOGY-COST-CURVE` | Technology Cost Curve | specified |
| P | `CAP-P-002-ADOPTION-ACCELERATION` | Adoption Acceleration | specified |
| N | `CAP-N-001-NARRATIVE-VELOCITY` | Narrative Velocity | specified |
| N | `CAP-N-002-NARRATIVE-SATURATION` | Narrative Saturation | specified |
| XS | `CAP-XS-001-MARKET-SHARE-ACCELERATION` | Market Share Acceleration | specified |
| XS | `CAP-XS-002-BOTTLENECK-SCARCITY` | Bottleneck Scarcity | specified |
| XA | `CAP-XA-001-CONDITIONAL-TAIL-ACTIVATION` | Conditional Tail Activation | specified |
| XA | `CAP-XA-002-EXTREME-REGIME-SHIFT` | Extreme Regime Shift | specified |
| XP | `CAP-XP-001-PAYOFF-CONVEXITY-GEOMETRY` | Payoff Convexity Geometry | specified |
| V | `CAP-V-001-REVERSE-DCF-EXPECTATIONS` | Reverse DCF Expectations | specified |
| S | `CAP-S-001-RUIN-AND-EXPECTED-SHORTFALL` | Ruin and Expected Shortfall Constraint | specified |
| S | `CAP-S-002-ROBUST-FRACTIONAL-KELLY` | Robust Fractional Kelly | specified |

**Gold != canon.** `Gold` means strategically selected for deep hardening. In R2 every capability stops at `specified`; none is `implemented`, `benchmark_passed`, `shadow_qualified` or `canon`.

## 2. Pack topology

R2 adds versioned pack files into the R1 Registry address spaces:

```text
registry/theories/       19 TheoryObject
registry/hypotheses/     12 HypothesisObject
registry/factors/         6 FactorObject
registry/algorithms/      6 AlgorithmObject
registry/benchmarks/      7 BenchmarkObject
registry/skills/         12 SkillContract
registry/data-fields/    25 CanonicalDataField
registry/providers/       0 ProviderAdapter
registry/capabilities/   12 ResearchCapability
---------------------------------------------
Total                     99 objects
```

Pack files use `objects[]` only as a physical packaging convenience. Each child object is independently validated against its R1 single-object schema, and identity remains the immutable semantic ID.

## 3. PNX-S semantic laws

### P｜Reality / Direction

P asks whether technology, cost, adoption and deployment evidence indicate a structural migration. Perez is used only as an explanatory stage scaffold. R2 does not predict a Kondratieff turning-point year.

### N｜Belief / Timing

Shiller and epidemic-dynamics ancestors support a diffusion framework, not a literal disease identity and not a one-way theorem that narratives cause price. R2 therefore measures attention level, velocity, acceleration, saturation and counter-narrative pressure separately.

### X｜Distribution / Payoff

Canonical decomposition:

```text
X := (Xs, Xa, Xp)
```

- `Xs` = structural right-tail value capture;
- `Xa` = state-conditioned activation of extreme outcomes;
- `Xp` = payoff geometry under current price/instrument.

No arithmetic sum is allowed. No scalar X or PNX score is allowed.

### V｜Strike / Price Layer

V asks what expectations are already embedded in price. Reverse DCF returns implied assumptions and sensitivity, **not a target price**.

### S｜Portfolio Survival Outer Ring

S is portfolio/investor survival, not issuer durability. Ruin/ES and robust Kelly are deterministic research computations. They may expose admissible research ranges and constraint effects but may not emit recommended position sizes or portfolio weights.

## 4. Scientific boundaries

R2 separates theory lineage from empirical admission:

- Shiller (2017) is backed by an uploaded original NBER working paper and is marked `primary_source_verified`.
- Other academic ancestors are conservatively recorded as `survey_only` until a primary-source receipt is separately installed in the repository.
- Xu 2026 causal/extreme-event materials are recorded as `practitioner_claim`. Their useful problem framing—leading extreme factors, direction/strength/lag, conditional extreme probabilities—is retained, but self-reported accuracy, returns and causal identification are not treated as verified evidence.
- Bessembinder-style wealth concentration supports right-tail concentration, not ex-ante winner certainty.
- EVT models tails; it does not explain long-run corporate superstars.
- Kelly is a growth-optimal reference under assumptions; full Kelly is not a default production policy.

## 5. Benchmark law

All 12 hypotheses are `preregistered`. The seven benchmark objects are protocol definitions only; **no benchmark is claimed passed in R2**.

Required disciplines include:

- point-in-time reconstruction;
- walk-forward / OOS splits;
- held-out regimes where feasible;
- multiple-testing control;
- calibration for probabilistic outputs;
- false-alarm accounting for rare events;
- complexity penalty and simpler baselines.

For Xa, raw accuracy is prohibited as the primary rare-event metric. Calibration, precision-recall tradeoffs, false alarms and lead time are first-class.

## 6. Runtime and provider boundary

`registry/providers/` remains empty in R2. Canonical fields are provider-neutral. R2 skills are `generic_agent` contracts only.

- Q1 may continue provider qualification and mapping work.
- R3 owns Wind AI + Codex runtime-specific Skill Interface.
- R4 owns deterministic reference implementations and benchmark harnesses.

R2 therefore does not claim that any of the 12 capabilities can already run in Wind AI, Codex or quant-workspace.

## 7. Governance boundary

R2 does not alter Q1, A6 or M1.2 state. It does not authorize Evidence/Outcome admission, A9 operational-canon switching, RSI promotion, target prices, buy/sell signals, position sizing, recommended weights, broker actions or live execution.

## 8. Exit gate

R2 may advance from `candidate_started` to `candidate_ready_for_human_review` only after exact-head `repository-gates` PASS including `validate_r2_gold_pack.py`.

Human acceptance may authorize only:

> `R3｜Wind AI + Codex Skill Interface`

It still does not authorize production trading or portfolio actions.
