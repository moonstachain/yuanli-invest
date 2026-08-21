# YIP0 | Yuanli Investment Philosophy Canon — Design

## Status

- Stage: `YIP0_INVESTMENT_PHILOSOPHY_CANON`
- Design state: approved in conversation on 2026-08-21
- Repository role: architecture / philosophy authority candidate
- Base: `main@43911282d5ff80a2795d1b02afcf7ef40bc513a3`
- Merge authority: not implied

## Purpose

YIP0 gives the existing Yuanli Investment OS a philosophical substrate without changing the already accepted semantic architecture.

The repo already freezes:

- Objective: `Lifetime Right-Tail Capture under Survival Constraints`
- OS: `one_core_three_worlds_three_gates_one_loop`
- Three Worlds: `P Reality / N Belief / X Asymmetry`
- `X := (Xs, Xa, Xp)`
- Three Gates: `E Evidence / V Price / S Survival`
- human navigation: `势 · 信 · 极｜真 · 价 · 生`
- research dependency graph: `P -> Xs -> N -> V -> Xa -> Xp -> S`, with E horizontal

YIP0 does not replace any of those objects. It explains the philosophical laws underneath them and makes those laws machine-checkable.

## Core philosophical identity

Human name:

> **可错的反身演化实在论**

English identity:

> **Fallibilist Reflexive Evolutionary Realism**

Six compression words:

> **实在 · 可错 · 反身 · 演化 · 凸性 · 生存**

Mother proposition:

> Reality exists independently of any one investor, yet it changes through time. Human knowledge of it is always incomplete. In financial systems, belief can alter action, capital allocation, price and therefore later reality. Markets can remain non-equilibrium for long periods. Wealth outcomes are non-Gaussian and path-dependent. Therefore the investment objective is not permanent correctness, but reality-tested learning, asymmetric payoff capture and survival.

## Authority position

YIP0 is an upstream philosophy authority candidate, not a market-data authority, not a trading authority and not a replacement for capability contracts.

Authority relationship:

```text
Investment Philosophy Canon (YIP0)
        ↓ constrains
OS Constitution / semantic ontology
        ↓ constrains
ResearchCapability contracts
        ↓ implemented by
Runtime / Agent / Quant algorithms
        ↓ tested by
Replay / Benchmark / Failure / Settlement
```

YIP0 may constrain interpretation and admissibility. It may not create target prices, portfolio weights, buy/sell instructions, live execution permissions or evidence admission by itself.

## Twelve axioms

### `YL-PH-01 | Becoming before Being`

**World is process before state.**

Research must ask what reality is becoming, not only what it currently is.

Maps primarily to: `P`.

### `YL-PH-02 | Reality exceeds belief`

**Reality exists independently; belief is incomplete.**

`P != N`. Narrative strength cannot establish physical, institutional or economic truth.

Maps to: `P`, `N`, `E`.

### `YL-PH-03 | All investment knowledge is provisional`

**Every investment claim is a revisable hypothesis.**

No research object is infallible merely because it is canonical, historical Gold, model-generated or widely accepted.

Maps to: `E`, learning loop.

### `YL-PH-04 | Belief is an economic state variable`

**Belief is not noise.**

Shared expectations can alter spending, financing, positioning, valuation and institutional behavior.

Maps to: `N`.

### `YL-PH-05 | Belief can change reality`

**Financial systems are reflexive.**

Belief can change capital flows and prices; those can change financing conditions, incentives and later fundamentals.

Maps to: `P <-> N <-> V`.

### `YL-PH-06 | Price is both outcome and cause`

**Price participates in the system it measures.**

Price can affect financing capacity, collateral, incentives, attention and future actions.

Maps to: `N`, `V`, reflexive-loop analysis.

### `YL-PH-07 | Non-equilibrium can persist`

**Mispricing is not self-correcting on a fixed clock.**

A valuation gap alone does not imply an immediate mean-reversion trade. Research must identify the sustaining feedback loop and its breaker.

Maps to: `N`, `V`, `Xa`.

### `YL-PH-08 | Returns are non-Gaussian`

**Wealth is disproportionately shaped by tails.**

Average outcomes are insufficient descriptions of long-horizon investment reality.

Maps to: `X`.

### `YL-PH-09 | Payoff dominates raw hit-rate`

**Decision quality cannot be reduced to prediction accuracy.**

Research must distinguish probability, payoff geometry, path dependence and ruin exposure.

Maps to: `Xs`, `Xa`, `Xp`.

### `YL-PH-10 | Great future != great investment`

**Price is an admissibility boundary.**

A correct structural thesis can still produce a poor investment if expectations are already overpaid.

Maps to: `V`.

### `YL-PH-11 | Survival precedes optimization`

**The right to continue compounding dominates local optimality.**

Any framework that maximizes expected return while allowing unacceptable ruin risk violates the philosophy.

Maps to: `S`.

### `YL-PH-12 | Reality has final settlement authority`

**Models answer to future reality.**

Replay, benchmark, falsification, failure receipts and future settlement must be allowed to revise or demote prior knowledge.

Maps to: learning loop and all ResearchCapability contracts.

## Four mother laws

The twelve axioms compress into four non-negotiable mother laws:

1. `REALITY_OVER_BELIEF` — prevents narrative relativism.
2. `REFLEXIVITY` — prevents static-fundamental reductionism.
3. `TAIL_ASYMMETRY` — prevents mean-variance / hit-rate reductionism.
4. `SURVIVAL_FIRST` — prevents ruinous optimization.

## Intellectual lineage boundary

YIP0 uses an intellectual lineage as orientation, not as a claim that each axiom is a verbatim theorem of one thinker.

- Popper: fallibilism, falsification, provisional knowledge.
- Soros: fallibility, reflexivity, non-equilibrium implications in financial/social systems.
- Shiller: narrative diffusion and economic effects of popular stories.
- Schumpeter / Kuhn / Perez: structural change, creative destruction, paradigm transition and technology-economic diffusion.
- Knight / Taleb / EVT tradition: uncertainty, fat tails, convexity and ruin sensitivity.
- Yuanli synthesis: combines these into the accepted `P/N/X + E/V/S + learning loop` architecture.

Machine objects must label `source_lineage` separately from `canonical_axiom`; lineage is not authority laundering.

## Machine-readable contract

Create `YIP0-PHILOSOPHY-CONTRACT-v0.1.json` with:

- identity and stage
- mother proposition
- six-word compression
- 12 axioms with stable IDs
- four mother laws
- mapping to canonical OS nodes
- explicit forbidden interpretations
- lineage boundary
- governance boundaries

No scalar philosophy score is permitted.

## State and Human Gate

Create `YIP0-STATE.json` with candidate-state semantics independent of the repository-wide `next_gate` because QXM2 is already an active program track.

Allowed YIP0 states:

- `candidate_started`
- `candidate_ready_for_human_review`
- `human_accepted_pending_post_acceptance_ci`
- `human_accepted_ready_for_merge`
- `accepted_merged`

Human acceptance token:

`ACCEPT_YIP0_INVESTMENT_PHILOSOPHY_CANON`

Future merge authorization token:

`AUTHORIZE_YIP0_MERGE`

Acceptance does not imply merge.

## Validator

Add a fail-closed validator that checks:

- all 12 stable axiom IDs are present exactly once;
- no existing constitutional invariant is silently redefined;
- `P != N` and `X := (Xs, Xa, Xp)` are preserved;
- E remains horizontal;
- V remains Price-Implied Expectations / no target-price ontology;
- S remains portfolio survival / no automatic sizing;
- no scalar PNX / Force / philosophy score;
- no buy/sell, recommended weight, position size or live execution authority;
- state and Human Gate are internally consistent;
- active repository-wide gate is not overwritten by YIP0 candidate status.

Hook the validator into `repository-gates` under contracts.

## Human Review dimensions

Formal review card should score PASS/FAIL on:

1. philosophical coherence
2. compatibility with accepted OS
3. reality/belief separation
4. reflexivity boundary
5. non-equilibrium boundary
6. tail/convexity boundary
7. price boundary
8. survival boundary
9. evidence/falsification boundary
10. anti-authority-laundering lineage rule
11. no scalar-score regression
12. no trading-authority regression

## Explicit non-goals

YIP0 does not:

- add a fourth human world;
- change `P/N/X/E/V/S` IDs;
- change `X := (Xs, Xa, Xp)`;
- promote any ResearchCapability;
- admit Evidence or Outcome objects;
- execute benchmarks;
- change A9 operational canon;
- modify the QXM2 gate chain;
- produce market recommendations, target prices, portfolio weights, position sizes, buy/sell instructions or live execution.

## Success criteria

YIP0 is ready for Human Review when:

- philosophy document exists;
- machine contract exists;
- candidate state exists;
- Human Review card exists;
- validator passes;
- all pre-existing repository gates continue to pass;
- exact-head CI is green;
- PR remains Draft until Human Review.
