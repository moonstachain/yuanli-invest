# QXM1｜Financial Mechanics Capability Candidate Pack v0.1

Status: `candidate_started`

## 1. Purpose

QXM1 compiles the Qin Xiaoming financial-thinking material from `moonstachain/llm-wiki` into the universal 11-block `ResearchCapability` contract frozen by R2.3-B0.

QXM1 is **not** a course summary and does **not** promote practitioner teaching material into Canon theory authority. It extracts stable research questions, mechanism seeds, evidence requirements, input/output contracts, falsifiers, benchmarks and settlement rules.

Upstream authority:

- R2.3-B0: `accepted_merged`
- Universal contract: 11 mandatory blocks
- canonical output root: typed `ResearchState`
- `Claim Authority <= Evidence Authority`
- point-in-time evidence and outcome-leakage prohibition are mandatory
- no scalar PNX/Force score, target price, recommended weight, position size, buy/sell or live execution

## 2. Reverse-engineering judgment

The Qin material is most useful as a **Classical Financial Mechanics layer**, not as a new top-level Yuanli ontology.

Its durable contribution is a set of mechanism primitives:

1. economic choice under scarcity and opportunity cost;
2. credit/debt transmission across time and sector balance sheets;
3. deductive business-driver decomposition from revenue/cost/profit toward primitive operating drivers;
4. stock/flow separation and three-statement reconciliation;
5. price as future payoff translated through opportunity cost / discount-rate assumptions;
6. holding-period return and exit liquidity as ex-post investment outcome mechanics.

These primitives strengthen existing `P.capital / P.asset / V / S / FutureSettlement` semantics. They do not create a fourth world, a new master score or a parallel investment constitution.

## 3. Six compiled candidates

| Candidate | Contract role | Semantic placement | Core question |
|---|---|---|---|
| `CAP-P-003-FUNDAMENTAL-DRIVER-DECOMPOSITION` | new capability candidate | `P.asset` | Which primitive operating drivers actually generate revenue, margin, reinvestment and cash flow? |
| `CAP-P-004-THREE-STATEMENT-INTEGRITY-CASH-CONVERSION` | new capability candidate | `P.asset + E` | Do earnings, balance-sheet changes and cash flows reconcile into one coherent economic reality? |
| `CAP-R-01 / QXM1-PROFILE-R-CREDIT-BALANCE-SHEET-TRANSMISSION` | profile candidate | `P.capital / R` | How are credit, debt service and sector balance sheets transmitting into spending/funding/risk appetite? |
| `CAP-V-01 / QXM1-PROFILE-V-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE` | profile candidate | `V` with `P.capital` context | Which opportunity-cost / discount-rate assumptions reconcile current price with expected payoff state? |
| `CAP-S-004-STRESS-EXIT-LIQUIDITY` | new capability candidate | `S + Xp` | Can the exposure actually be exited in stress near defensible value and within required horizon? |
| `CAP-CROSS-001-RETURN-SOURCE-ATTRIBUTION` | settlement-layer candidate | `FutureSettlement / CROSS` | Why did the investment actually make or lose money, and which original claims were truly supported? |

## 4. Architecture decision: four new candidates, two profiles

QXM1 deliberately does **not** create six independent top-level Capability identities.

### 4.1 Credit transmission remains inside `CAP-R-01`

Credit and debt-cycle mechanics are an implementation profile of `Regime Causal Decomposition` because the mother question is still about the capital regime governing discount rates, funding, risk appetite and allocation.

Creating a new human `Credit World` or parallel macro ontology would violate R2.3-A/B0 architecture.

### 4.2 Opportunity cost remains inside `CAP-V-01`

The DCF “denominator” language is useful, but QXM1 rejects DCF as a universal cross-asset ontology.

`CAP-V-01 | Price-Implied Expectations` remains the mother capability. The QXM profile contributes a reusable opportunity-cost/discount-rate bridge and routes to asset-specific model families such as reverse DCF, implied policy path, spread decomposition, forward/carry, real-rate decomposition or implied-volatility surfaces.

Invariant:

> **Asset form is not pricing model.**

## 5. The two most important new P.asset capabilities

### 5.1 Fundamental Driver Decomposition

The core move is deductive rather than checklist-based:

```text
Eligible demand
  -> penetration / share
  -> volume
  -> price / mix
  -> revenue
  -> unit cost / gross margin
  -> opex
  -> operating profit
  -> working capital / reinvestment
  -> free cash flow
```

This is not a universal one-way causal law. It is a machine-auditable decomposition graph where arithmetic identities, observed facts and hypothesized causal edges must remain typed separately.

The intended use is to replace vague prompts such as “analyze company fundamentals” with a provider-independent driver tree that can later be mapped to Wind, filings, industry data or other runtimes.

### 5.2 Three-Statement Integrity & Cash Conversion

This candidate asks a different question from normal valuation:

> Does the company’s reported story leave coherent traces across earnings, balance sheet and cash flow?

It tracks:

- stock vs flow;
- earnings vs operating cash conversion;
- working-capital absorption;
- capitalization intensity;
- external financing dependence;
- restatement/accounting-policy lineage.

Hard boundary:

> A reconciliation anomaly is **not** proof of fraud, manipulation or insolvency.

Misconduct attribution requires separate evidence authority.

## 6. Stress Exit Liquidity is not “can I click sell?”

QXM1 preserves a stronger liquidity definition:

> Liquidity is the ability to reduce or exit exposure within the required horizon **near economically defensible value**, not merely the existence of a quote or a theoretical buyer.

The candidate therefore separates:

- normal exit horizon;
- stress exit horizon;
- executable depth / price impact;
- fair-value haircut;
- settlement lag;
- margin/funding liquidity;
- transfer or redemption restrictions.

Research OS may diagnose this state. Portfolio OS still owns capital action.

## 7. HPR becomes learning, not another investment world

The raw holding-period identity remains useful:

```text
HPR = (exit price - entry price + cash distributions) / entry price
```

But QXM1 upgrades it into `Return Source Attribution` inside the Reality Learning Loop.

The intended settlement decomposition is:

```text
Realized total return
  = cash-flow / carry realization
  + fundamental revision
  + discount-rate / valuation revision
  + narrative / expectation repricing
  + FX
  + instrument geometry
  + benchmark/common component
  + unresolved residual
```

The decomposition must distinguish arithmetic attribution from causal attribution.

A profitable outcome does not prove the thesis was correct; a losing outcome does not automatically falsify every structural claim.

This is the mechanism that answers the Qin principle:

> If the system cannot explain why it made money, the outcome cannot become durable research intelligence.

## 8. Source authority and epistemic boundary

The source material in `llm-wiki/qin-xiao-ming/` is mainly raw course transcript plus internal synthesis. QXM1 classifies it as `practitioner_teaching_source` or `research_synthesis`.

Therefore it may seed:

- research questions;
- decomposition structures;
- mechanism hypotheses;
- candidate observables;
- failure questions.

It may **not** silently become:

- primary TheoryObject authority;
- independent empirical evidence;
- causal identification proof;
- live market fact;
- benchmark result;
- trading authority.

Primary-source academic research and independent empirical evidence remain a separate future battle before promotion.

See `QXM1-SOURCE-PROVENANCE-v0.1.json`.

## 9. 11-block contract compliance

Every candidate in `QXM1-CANDIDATE-CONTRACTS-v0.1.json` contains:

1. Identity & Stable Question
2. Scope & Routing
3. Theory & Causal Mechanism
4. Evidence Contract
5. Input Contract
6. Inference Contract
7. Typed ResearchState Output
8. Falsification & Failure Contract
9. Benchmark & Qualification Contract
10. Settlement & Learning Contract
11. Runtime, Receipt & Governance Contract

No candidate is implemented or benchmark-passed by this pack.

## 10. Candidate priority after QXM1

QXM1 freezes research candidates only. If a later Human Gate authorizes deepening, recommended order is:

### P0-A | Fundamental reality

1. `CAP-P-003-FUNDAMENTAL-DRIVER-DECOMPOSITION`
2. `CAP-P-004-THREE-STATEMENT-INTEGRITY-CASH-CONVERSION`

Reason: they close the current gap between structural thesis and actual company cash-generation mechanics.

### P0-B | Learning closure

3. `CAP-CROSS-001-RETURN-SOURCE-ATTRIBUTION`

Reason: it turns every Replay/FutureSettlement into capability learning rather than P&L storytelling.

### P1 | Capital mechanics profiles

4. `CAP-R-01` credit/balance-sheet profile
5. `CAP-V-01` opportunity-cost/discount-rate profile
6. `CAP-S-004-STRESS-EXIT-LIQUIDITY`

## 11. Explicit non-goals

QXM1 does not authorize:

- Registry admission of new Theory/Hypothesis/Factor/Algorithm objects;
- implementation of the six candidates;
- benchmark execution or benchmark PASS;
- Shadow qualification or Canon promotion;
- Wind/Codex production runtime;
- Evidence/Outcome admission;
- A9 operational-canon switch;
- RSI promotion;
- target price;
- recommended weight or position size;
- buy/sell/hold;
- broker or live execution.

## 12. Exit gate

QXM1 can move from `candidate_started` to `candidate_ready_for_human_review` only after exact-head CI validates:

- R2.3-B0 remains `accepted_merged`;
- six and only six QXM1 candidates exist;
- all eleven contract blocks and their required fields are present;
- the two profile candidates preserve `CAP-R-01` and `CAP-V-01` mother semantics;
- source provenance preserves practitioner/synthesis evidence limits;
- no scalar score or trading-authority regression exists;
- no candidate is represented as implemented, benchmark-passed, shadow-qualified or Canon.

Human Gate reserved for the next step:

`ACCEPT_QXM1_FINANCIAL_MECHANICS_CAPABILITY_CANDIDATE_PACK`
