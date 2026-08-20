# RCN0-S2 Full B3 Quant Closure Spec v0.1

Status: `active / data_blocked`

Issue: #34

Replay: `RCN-REPLAY-20260820-CN-INNOVATIVE-DRUG-MRNA`

## 1. Stable question

> After controlling for standard size, beta, momentum, liquidity and A-share microstructure effects, does pre-registered ordinal Narrative Distance retain incremental explanatory information for the 2026-08-20 healthcare cross-section?

This is an explanatory Shadow Benchmark, not a trading model and not causal proof.

## 2. Analysis universe

Exactly the 29 A-share targets declared by the T0 source:

- 7 vaccine/mRNA mapping-chain targets;
- 17 innovative-drug BD/pipeline targets;
- 5 CXO/service targets.

No target may be added, removed or re-bucketed because of its realized return.

Current extraction state: 24/29 names recovered unambiguously; five innovative-drug names unresolved. Full regression is blocked until all 29 are recovered from T0 source/classification evidence.

## 3. Frozen D_N state

Narrative Distance remains ordinal:

- `near`: vaccine/mRNA mapping chain;
- `medium`: innovative-drug BD/pipeline chain;
- `farther`: CXO/service chain.

No continuous semantic score is authorized for Replay #1.

## 4. Required data contract

One row per target with fields:

`ticker, company, chain, D_N_bucket, return_t0, benchmark_return_t0, abnormal_return_t0, market_cap_t0, beta, beta_lookback, momentum_5d, momentum_20d, momentum_60d, turnover_t0, turnover_20d, liquidity_proxy, board, price_limit_pct, one_price_limit_dummy, tradability_dummy, prior_theme_member, source_locator, as_of`

Missingness must remain explicit. No silent interpolation for T0 controls.

## 5. Pre-specified models

### M0 | Broad/sector abnormal return

`AR_i = R_i - R_benchmark`

Benchmarks must be frozen before model comparison; at minimum healthcare and broad-growth contextual benchmarks.

### M1 | B3 controls only

`AR ~ log(MCap) + Beta + Mom5 + Mom20 + Mom60 + Liquidity + Board/Limit + PriorTheme`

### M2 | Narrative-only

`AR ~ D_N`

### M3 | Incremental Narrative

`AR ~ B3 controls + D_N`

### M4 | RCN interaction candidate

B3 controls + ordinal D_N + Reality/Capital/V state interactions only where those states are point-in-time typed and do not collapse into a scalar score.

## 6. Primary evaluation

RCN0-S2 must report:

- D_N coefficient/direction and uncertainty;
- change in out-of-sample-style or penalized explanatory metrics where feasible given small n;
- rank correlation / bucket monotonicity;
- residual diagnostics;
- robust / HC standard errors;
- coefficient stability under sensitivity tests;
- false-positive implications.

With n=29, p-values alone are not an acceptance criterion.

## 7. Mandatory sensitivity tests

1. exclude one-price-limit names;
2. exclude smallest-cap tercile;
3. use abnormal rather than raw return;
4. collapse momentum to one pre-specified measure to reduce overfit;
5. jackknife / leave-one-out coefficient stability;
6. near-vs-rest binary robustness;
7. winsorization sensitivity without deleting observations;
8. chain-level permutation/randomization diagnostic, explicitly labeled exploratory.

## 8. Acceptance law

`B3_full_pass` requires all of:

- complete frozen 29-name universe;
- no T0 leakage;
- D_N relation remains directionally stable after a parsimonious B3 control set;
- signal is not solely produced by one-price-limit names or smallest-cap tercile;
- Narrative adds interpretable incremental information over B3, not merely in-sample complexity;
- falsifier F1 is not triggered.

`B3_full_fail` if the complete controlled test removes the Narrative gradient or shows it is adequately explained by simpler factors.

`unresolved_due_to_data` if required T0 features cannot be admitted without fabrication or post-hoc substitution.

## 9. Consequences

- Pass: may advance Replay #1 toward `shadow_replay_passed`, still blocked by D_R and Evidence Gate.
- Fail: H-RCN-01 fails; downgrade `narrative_led` confidence and retain RCN only as bounded descriptive attribution unless later replays restore transferability.
- Unresolved: no promotion; preserve uncertainty.

## 10. Non-authorization

No target price, position sizing, buy/sell, live execution, Gold promotion or Canon promotion is authorized by this benchmark.