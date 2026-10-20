# RCN0 Shadow Benchmark Spec v0.1

Status: `candidate`

Issue: #26

First replay target: `2026-08-20-cn-innovative-drug-mrna`

## 1. Benchmark question

Can a composed Reality–Capital–Narrative state explain market/theme leadership more faithfully and with less post-hoc storytelling than simpler baselines?

The benchmark does not test whether RCN0 can predict prices perfectly. It tests whether the framework produces a disciplined, falsifiable and point-in-time attribution of the **dominant pricing driver**.

## 2. Required Shadow capability calls

RCN0 is a composer, not a replacement for canonical capabilities.

Each replay must generate independent Shadow outputs for:

1. `CAP-R-01 | Regime Causal Decomposition`
   - output role: `capital_state`
   - minimum question: Did growth/inflation/liquidity/risk appetite/funding/term-premium conditions materially shift enough to explain the move?

2. `CAP-P-01 | Reality State Transition`
   - output role: `reality_state`
   - minimum question: Did the relevant asset/industry reality materially change at T0, and at what layer?

3. `CAP-N-01 | Narrative / Expectation Regime`
   - output role: `narrative_state`
   - minimum question: What future assumption was newly translated into price, how did it diffuse, and where did crowding begin?

4. `CAP-V-01 | Price-Implied Expectations`
   - output role: `valuation_state`
   - minimum question: Was the move better explained as low-price repair, or did price already embed aggressive expectations before the catalyst?

Supporting Shadow:

- `CAP-R-02 | Internal vs External Rotation Detector`
- `CAP-E-01 | Evidence Authority Graph`

## 3. Pre-registered hypotheses for Replay #1

### H-RCN-01 — Narrative proximity gradient

At T0, after controlling for market cap, beta, prior momentum and exchange/limit-up microstructure, targets with lower pre-registered Narrative Distance to the mRNA-oncology story should show stronger same-day abnormal returns than more distant targets.

Failure condition: no incremental relation after controls.

### H-RCN-02 — Industrial-validation mismatch

The strongest same-day price leaders should not systematically coincide with the strongest contemporaneous industrial/earnings validation.

Failure condition: the same names are independently shown to possess the strongest direct economic exposure and validation.

### H-RCN-03 — Capital insufficiency

Broad Capital state should be insufficient to explain the cross-sectional healthcare move.

Failure condition: a broad risk-on/liquidity shock explains comparable or greater cross-sectional variation than RCN state.

### H-RCN-04 — High-valuation narrative repricing

The narrative-led label should remain admissible even when the theme is not in a depressed valuation state.

Failure condition: the move is fully explained by systematic low-valuation mean reversion.

## 4. Required universe freeze

Before quantitative replay, freeze a universe containing at minimum:

- vaccine/mRNA mapping chain;
- innovative-drug/BD/pipeline chain;
- CXO/service chain;
- broad healthcare benchmark;
- broad growth benchmark;
- broad market benchmark.

Universe membership must be determined from T0-available classifications/disclosures, not from ex-post returns.

## 5. Required features

### Reality features

- direct technology/platform comparability;
- pipeline/product presence;
- IP/economic-right ownership;
- clinical/regulatory stage where relevant;
- current order/revenue/profit/cash-flow evidence;
- contemporaneous earnings surprise.

### Capital features

- broad-index return state;
- turnover / incremental-flow proxies;
- risk appetite / beta regime;
- healthcare-sector flow versus market flow;
- funding/liquidity context if available.

### Narrative features

- event-story embedding frozen from T0 text;
- company/theme semantic similarity;
- concept co-occurrence / graph hops;
- media/discussion propagation if available;
- abnormal volume/limit-up diffusion only as downstream confirmation, not sole input.

### Valuation features

- PE/PB/PS where meaningful;
- historical percentile;
- loss-making/distorted-multiple flag;
- price-implied expectation proxy appropriate to the target.

### Controls

- market capitalization;
- beta;
- prior 5D/20D/60D momentum;
- liquidity/turnover;
- exchange board / daily price-limit regime;
- prior theme membership.

## 6. Minimum benchmark baselines

RCN0 must be compared with at least:

- `B0 Broad Beta`: broad-market/style returns only;
- `B1 Fundamental`: earnings/order/industrial-validation features only;
- `B2 Valuation Repair`: historical valuation percentile only;
- `B3 Size + Beta + Momentum`: standard cross-sectional controls;
- `B4 Narrative-only`: narrative proximity without Reality/Capital/V decomposition;
- `B5 RCN`: composed state and interaction terms without scalar collapse.

The goal is not to maximize one in-sample R². Evaluation must include explanatory stability, false positives, calibration of labels and out-of-sample transfer to later cases.

## 7. Quantitative tests

Candidate tests:

1. Cross-sectional abnormal return regression/ranking test using pre-registered `D_N` buckets.
2. Monotonicity test: near/medium/far Narrative Distance buckets.
3. Partial-information test: incremental contribution of Narrative after size/beta/momentum/valuation controls.
4. Industrial-distance interaction: highest short-run returns under `D_N near × D_R far` should be treated as a hypothesis, not assumed truth.
5. Mean-reversion/settlement test: compare short-horizon narrative payoff with later industrial settlement.

No result may be called causal solely from cross-sectional association.

## 8. Qualitative acceptance tests

A Human Reviewer should be able to distinguish from the output:

- what was known at T0;
- what was inferred;
- what was merely claimed by a source;
- what later evidence settled;
- why the label was not simply reverse-engineered from returns;
- which simpler explanation remained live.

## 9. Candidate metrics

- dominant-driver classification agreement across independent reviewers;
- evidence completeness rate;
- T0 leakage violations: target `0`;
- false narrative-led rate on known fundamental/capital-led controls;
- incremental explanatory value of Narrative Distance versus B3;
- monotonicity consistency across replay cases;
- revision latency after falsifier breach;
- unresolved-rate (must not be artificially forced toward zero).

## 10. Promotion ladder

`candidate`
-> `shadow_replay_ready`
-> `shadow_replay_passed`
-> `human_review_passed`
-> `gold_replay_accepted`
-> potential Capability promotion under separate authority.

A replay can become Gold without automatically promoting RCN0 to Canon. A Capability can be useful without every replay becoming Gold.

## 11. First-case acceptance gate

Replay #1 is not accepted as Gold until:

- official market data are independently verified;
- external mRNA catalyst is independently verified with primary sources;
- target universe is frozen independent of returns;
- control variables are obtained;
- CAP-R-01 / CAP-P-01 / CAP-N-01 / CAP-V-01 Shadow outputs are stored;
- baseline comparison is run;
- falsifiers are evaluated;
- Human Review explicitly accepts the case.
