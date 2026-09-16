# YMQ-GOLD2｜Gold Monetary Regime × Property Drift × Timing Compiler — Design

Status: `HUMAN_APPROVED / IMPLEMENTATION_AUTHORIZED`

## 0. Mission

Build the first governed macro-quant Genesis Benchmark that converges the existing Gold research assets instead of creating a fourth parallel Gold system.

The system question is:

> Can Yuanli compile monetary-regime reality, price/belief, property drift, expectation-vs-reality, valuation-vs-driver, survival and future settlement into one Point-in-Time, defeatable, replayable, live-shadow research object without laundering a failed model into a better-looking backtest?

The target is `GOLD` as a `monetary_asset`, not generic commodities.

## 1. Existing authority that MUST be reused

YMQ-GOLD2 is downstream of, and may not rewrite:

- `docs/os-vnext/*` — canonical human grammar and authority boundaries;
- `YMQ4-DP1-B` — `gold_core_monthly_v0.1`, 1978–2026 historical PIT/as-of panel;
- `YMQ4-B2` — fixed-beta OOS baseline;
- `YMQ4-B3` — scientific no-go for the preregistered 60-month rolling OLS dynamic-beta candidate;
- `YIOS-G1` — Gold Genesis Case, PIT firewall, research settlement, shadow-only execution boundary;
- `YG100` — human projection / historical monetary-convexity atlas in Notion.

Hard invariant:

`NEW_RESEARCH_MAY_LEARN_FROM_B3_NO_GO; IT MAY_NOT RETUNE B3 INTO SUCCESS.`

## 2. One Gold object, three existing languages

YMQ-GOLD2 creates one translation layer, not a new source of truth.

```text
YG100 Human Gold Grammar
Monetary Reality / Reflexivity / Convexity / 守攻持收
                ↓
YMQ Research Grammar
Reality / Narrative / Transmission / Price × Payoff / S-C-R-X
                ↓
YIOS Governed State
RealityState / MonetaryState / DemandState / NarrativeState /
RegimeState / UnknownState / FalsifierState / AuthorityState
```

The unified object is `GoldUnifiedState@PIT`.

## 3. G0｜Semantic Convergence

`GoldUnifiedState@PIT` MUST carry:

- `as_of`, `known_as_of_max`, `source_panel`;
- `monetary_regime_state`;
- `real_rate_state`;
- `usd_state`;
- `inflation_state`;
- `fiscal_sovereign_state`;
- `official_demand_state`;
- `private_demand_state`;
- `narrative_state` and `crowding_state`;
- `price_state` and `implied_expectation_state`;
- `property_drift_state`;
- `expectation_reality_state`;
- `valuation_state` and `driver_state`;
- `engine_state` for `C/R/X/S` with no scalar total score;
- `lifecycle_state` limited to `守/攻/持/收/等/未知`;
- `falsifiers`, `unknowns`, `authority_state`.

No field may authorize portfolio sizing, buy/sell, broker execution or Capital admission.

## 4. G1｜Property Drift Detection — not B3 rescue

The first machine hypothesis is not “dynamic beta beats fixed beta”. That candidate already failed its preregistered multi-regime gate in YMQ4-B3.

YMQ-GOLD2 instead asks:

> Is the *explanatory property* of Gold changing across regimes, and can that change be detected without claiming tradable alpha?

Required comparisons:

- fixed B2 exposures / residual behavior;
- rolling descriptive sensitivities using only prior data;
- regime-conditioned residual persistence;
- factor-contribution concentration;
- explicit `UNKNOWN` when evidence is insufficient.

Allowed labels:

- `STABLE_PROPERTY`
- `DRIFT_CANDIDATE`
- `DRIFT_CONFIRMED_RESEARCH_ONLY`
- `INSUFFICIENT_EVIDENCE`

Forbidden claim:

`PROPERTY_DRIFT == DYNAMIC_BETA_ALPHA`.

## 5. G2｜Expectation × Reality

For Gold, “Reality” is not industrial spot consumption. It is monetary and balance-sheet reality.

Reality candidates:

- real yields;
- USD;
- realized policy;
- realized inflation;
- fiscal / sovereign credibility observations;
- official reserve demand;
- ETF/private flows where PIT authority exists.

Expectation candidates:

- expected policy path;
- inflation expectations;
- futures/options positioning where available;
- consensus/narrative/crowding;
- price-implied monetary stress.

Output labels:

- `REALITY_LED`
- `EXPECTATION_LED`
- `CONFIRMED`
- `DIVERGENT`
- `INDETERMINATE`

No label is a trade instruction.

## 6. G3｜Valuation × Driver

Gold has no enterprise cash-flow anchor. YMQ-GOLD2 therefore freezes three lenses instead of a single target price:

1. `MACRO_FAIR_VALUE_LENS` — real rate / USD / inflation-liquidity relationship;
2. `MONETARY_REGIME_PREMIUM_LENS` — fiscal credibility, reserve architecture, official demand;
3. `REFLEXIVITY_POSITIONING_LENS` — flows, positioning, narrative/crowding when PIT admissible.

Valuation output is categorical:

- `UNDERPRICED`
- `FAIR`
- `OVERPRICED`
- `UNIDENTIFIABLE`

Each Driver carries direction, strength, persistence and evidence authority. No point target is allowed.

## 7. G4｜1978–2026 Blind Regime Replay

Input defaults to the already governed `gold_core_monthly_v0.1` panel. The replay must retain the B2 split and B3 no-go as benchmark history.

Frozen regime review windows:

1. 1978–1980 — inflation / monetary disorder peak;
2. 1980–1985 — Volcker credibility repair;
3. 1999–2002 — Gold reactivation;
4. 2007–2009 — GFC;
5. 2011–2015 — crowding unwind / stronger USD;
6. 2018–2020 — real-rate / QE reactivation;
7. 2022–2024 — traditional macro tension / official-demand rise;
8. 2024–2026 — fiscal / reserve-architecture repricing candidate.

For every window the harness must preserve T0 knowledge and produce:

`State@T0 → Frozen Research Label → Future Outcome → Settlement → LearningDelta`.

Hard negatives include:

- long-run monetary thesis true while price falls materially;
- price rises while the stated causal thesis is wrong;
- official demand strong while B0/B2 explanatory structure remains dominant;
- narrative strong while valuation is already crowded;
- regime shift claim without PIT evidence;
- post-event evidence entering T0.

## 8. G5｜RAY × Yiru × Machine triangulation

Human judgments are first-class evidence only when explicitly supplied by the humans. The system MUST NOT fabricate either judgment.

Each adjudication object contains independent frozen slots:

- `ray_regime_judgment`;
- `yiru_timing_judgment`;
- `machine_state_judgment`;
- `known_as_of` for each;
- later Reality settlement;
- attribution: information / method / luck / unknown.

Empty human slots remain `PENDING_HUMAN_EVIDENCE`.

## 9. G6｜30-Day Live Shadow

Only after historical qualification may the live runner compile live Gold evidence into research-only states.

Allowed live outputs:

- `WATCH`
- `BUILDING`
- `CONFIRMED_RESEARCH_ONLY`
- `CROWDED`
- `DETERIORATING`
- `REGIME_SHIFT_CANDIDATE`
- lifecycle projection `守/攻/持/收/等/未知`.

Every output must set:

- `capital_authorized=false`;
- `sizing_authorized=false`;
- `execution_authorized=false`;
- `broker_action=false`.

No live scheduling is authorized by the design alone.

## 10. Scientific scorecard

Primary evaluation is not CAGR.

Required diagnostics:

- PIT integrity;
- regime detection lag;
- false regime-shift rate;
- expectation-reality divergence resolution;
- property-drift precision / persistence;
- calibration where probabilistic outputs exist;
- B2/B3 benchmark preservation;
- drawdown / survival diagnostics for shadow research only;
- Decision Regret audit;
- explanation stability;
- explicit UNKNOWN rate.

## 11. Authority law

```text
Research Evidence
    ↓
Research State
    ↓
Research Settlement
    ↓
Human Review
```

This program does NOT authorize:

- capital admission;
- recommended weights;
- position sizing;
- broker connectivity;
- VeighNa invocation;
- paper/live orders;
- automatic learning promotion to Canon.

`RESEARCH_QUALIFIED != CAPITAL_AUTHORIZED != EXECUTION_AUTHORIZED`.

## 12. Human Gates

- `G0_ACCEPT_GOLD2_CONSTITUTION`
- `G1_ACCEPT_PROPERTY_DRIFT_BENCHMARK`
- `G4_ACCEPT_HISTORICAL_REPLAY_SETTLEMENT`
- `G5_SUPPLY_HUMAN_JUDGMENTS`
- `G6_AUTHORIZE_LIVE_SHADOW_SCHEDULER`
- final merge / Canon acceptance remains a separate Human Gate.

Implementation may fully build and machine-qualify the branch before G0–G4 acceptance, but it may not silently cross any authority gate.