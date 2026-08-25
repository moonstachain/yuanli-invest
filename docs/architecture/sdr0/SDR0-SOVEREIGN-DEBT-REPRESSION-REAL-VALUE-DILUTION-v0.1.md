# SDR0｜Sovereign Debt Repression & Real-Value Dilution v0.1

Status: `candidate_ready_for_human_review`

## 0. Authority notice

SDR0 is a **specialized profile candidate under `CAP-R-01 | Regime Causal Decomposition`**. It does not create a new top-level world, return engine, investment ontology, or trading authority.

Upstream authority:

- YIP0 philosophy: Reality over Belief; all investment knowledge is provisional; Survival First.
- R2.3-B0: Universal 11-block `ResearchCapability` contract.
- QXM1 architecture: sovereign/credit/debt mechanics remain implementation profiles of `CAP-R-01` unless a later Human Gate proves that the mother question is genuinely different.
- `Claim Authority <= Evidence Authority`.
- Point-in-Time evidence, explicit falsifiers, failure receipts and outcome-leakage prohibition are mandatory.
- No scalar master score, target price, recommended weight, buy/sell/hold, position size or live execution.

## 1. Stable question

> **When sovereign debt-service and refinancing pressure rises, are fiscal, monetary, regulatory and balance-sheet policies shifting from market-clearing adjustment toward mechanisms that suppress the real cost of government funding or transfer duration/inflation risk to creditors; and is that shift economically material enough to change the cross-asset regime?**

The stable question is deliberately narrower than “Will the sovereign default?” and stricter than “Is debt high?”

## 2. Core ontology decision

SDR0 separates four concepts that are often collapsed into the phrase **soft default**:

1. **Fiscal constraint** — debt service, refinancing and issuance pressure are rising.
2. **Funding-market intervention** — authorities support market functioning or alter debt-management mechanics.
3. **Financial repression** — official policy persistently channels savings toward sovereign funding or suppresses government borrowing costs relative to a defensible market-clearing counterfactual.
4. **Real-value dilution** — creditors experience material loss of purchasing power through negative realized/ex-ante real returns, inflation surprise, or equivalent policy-induced dilution.

A liquidity backstop is not automatically financial repression. Financial repression is not automatically real-value dilution. Real-value dilution is not an explicit legal default.

SDR0 therefore prohibits the unqualified state label `soft_default` as a canonical output.

## 3. Causal mechanism

The candidate mechanism is a typed graph rather than a single story:

```text
Debt stock / maturity / primary balance
        ↓
Debt-service pressure + refinancing wall
        ↓
Sovereign issuance burden
        ↓
Marginal buyer elasticity / term premium / auction stress
        ↓
Funding cost ↑
        ↓
Fiscal pressure ↑
        ↘
          Policy response
          ├─ fiscal adjustment / growth repair
          ├─ debt-management changes
          ├─ liquidity backstop
          ├─ central-bank duration absorption / yield cap
          ├─ regulatory or captive-demand support
          └─ inflation tolerance / monetary accommodation
        ↓
Real sovereign funding cost
        ↓
Creditor real return / currency credibility / cross-asset repricing
```

Potential reflexive loop:

```text
Yield ↑ → interest expense ↑ → deficit / issuance ↑ → term premium ↑ → yield ↑
```

Potential repression loop:

```text
Fiscal constraint ↑ → policy support of sovereign funding ↑
→ nominal yield held below market-clearing path and/or inflation ↑
→ real creditor return ↓ → real debt burden diluted
```

These are mechanism hypotheses. SDR0 must preserve competing explanations and identification status.

## 4. Non-negotiable distinctions

### 4.1 `QE != financial repression`

Asset purchases can be motivated by macro stabilization, market dysfunction, reserve management or explicit sovereign-funding support. The policy objective, maturity choice, persistence, counterfactual and fiscal interaction must be identified.

### 4.2 `Treasury buyback != monetization`

Debt-management operations can improve liquidity or smooth maturity structure without creating central-bank money or suppressing real funding costs.

### 4.3 `FIMA / repo backstop != monetization`

Collateralized dollar liquidity facilities can reduce forced Treasury sales without changing the sovereign's real debt burden.

### 4.4 `negative real yield != repression`

Negative real yields may arise from growth expectations, safe-asset demand or monetary policy aimed at the macro cycle. Repression requires evidence of sovereign-funding transfer or policy-induced suppression/captive demand.

### 4.5 `foreign selling != sovereign crisis`

Foreign-holder reduction can reflect FX hedging, home-yield normalization, reserve management or portfolio rebalancing. SDR0 treats foreign pressure as a transmission node, not a sufficient condition.

### 4.6 `Japan catalyst != U.S. cause`

Japan or another foreign holder may alter marginal demand for Treasuries, but U.S. fiscal dynamics must be separately established. Catalyst, cause and policy response remain distinct objects.

## 5. Typed state model

Canonical output: `SovereignDebtRepressionStateProfile` under the `CAP-R-01` `ResearchState` root.

Required state dimensions:

- `fiscal_constraint`
- `debt_service_pressure`
- `refinancing_state`
- `issuance_burden`
- `marginal_demand_state`
- `term_premium_market_stress`
- `foreign_holder_pressure`
- `liquidity_backstop_state`
- `central_bank_duration_absorption`
- `captive_demand_intensity`
- `real_rate_suppression`
- `inflation_tolerance_state`
- `monetary_fiscal_boundary`
- `real_value_dilution`
- `currency_credibility_state`
- `transmission_lag`

Each dimension is typed by direction, magnitude band, persistence band, evidence authority and identification status. No weighted composite score is allowed.

## 6. Regime-stage vocabulary

A categorical stage may be emitted only as a summary of the typed dimensions:

- `market_financing_normal`
- `fiscal_constraint_rising`
- `funding_market_stress`
- `liquidity_backstop_active`
- `repression_candidate`
- `repression_active`
- `real_value_dilution_active`
- `policy_normalization_or_exit`
- `indeterminate`

### Hard AND gate for `real_value_dilution_active`

The label requires all of the following:

1. fiscal/debt-service pressure is elevated and persistent;
2. policy evidence supports systematic suppression/captive demand or equivalent transfer mechanism rather than mere market-function support;
3. creditor real returns are materially negative or purchasing-power dilution is observed over the declared horizon;
4. at least one major competing explanation has been tested and bounded;
5. evidence authority meets the declared threshold.

`2-of-4` voting rules are prohibited.

## 7. Evidence hierarchy

### Tier A｜Primary policy and official data

- central-bank decisions, balance sheets, operation terms and minutes;
- sovereign debt-management statements, auction data, maturity profiles and buyback rules;
- fiscal authority / budget office debt, deficit and interest-cost data;
- regulatory rules that create captive demand;
- official cross-border holdings and reserve data;
- official inflation, inflation-expectation and real-yield series.

### Tier B｜Primary theory and peer-reviewed / central-bank research

- fiscal dominance / monetary-fiscal interaction;
- financial repression and debt liquidation;
- debt-service and refinancing transmission;
- term premium, safe-asset demand and market-function mechanisms.

### Tier C｜High-quality secondary interpretation

May seed competing hypotheses and event locators, but cannot prove the live state.

## 8. Initial theory lineage seeds

SDR0 records these as source seeds only; it does not silently admit them as Canon `TheoryObject`s.

- Sargent & Wallace (1981), *Some Unpleasant Monetarist Arithmetic* — fiscal/monetary interaction and the limits of monetary control under fiscal pressure.
- Reinhart, Kirkegaard & Sbrancia (2011), IMF *Financial Repression Redux* / related debt-liquidation work — directed domestic savings, below-market government funding and negative real rates as debt-liquidation mechanisms.
- Federal Reserve historical record on the 1942–1951 Treasury–Fed peg — explicit low-rate government-financing regime and subsequent exit through the Treasury–Fed Accord.
- Bank of Japan official YCC record, 2016–2024 — direct calibration of yield-target operations, balance-sheet absorption and policy exit.
- Federal Reserve FIMA Repo Facility — hard negative / boundary case for dollar-liquidity support that can reduce forced Treasury sales without constituting sovereign debt monetization.
- BIS debt-service-ratio methodology — methodological seed for distinguishing debt stock from debt-service burden; sovereign implementation requires sovereign-specific definitions rather than direct reuse of private-sector DSR levels.

## 9. Canonical inputs

Provider-independent canonical inputs include:

```text
public_debt
marketable_debt
primary_balance
fiscal_balance
net_interest_expense
interest_to_revenue
interest_to_gdp
weighted_average_maturity
maturity_wall
gross_issuance
net_issuance
auction_tail
bid_to_cover
primary_dealer_takedown
foreign_official_holdings
foreign_private_holdings
home_foreign_yield_spread
fx_hedging_cost
term_premium
nominal_yield_curve
real_yield_curve
breakeven_inflation
realized_inflation
inflation_expectations
central_bank_government_bond_holdings
central_bank_purchase_flow
purchase_maturity_mix
yield_target_or_cap
repo_and_liquidity_facilities
debt_buyback_flow
regulatory_sovereign_demand_rules
bank_sovereign_holdings
pension_insurance_sovereign_holdings
currency_index
reserve_currency_share
```

Provider mappings to Wind, FRED, Treasury, CBO, BOJ, BIS or other runtimes are separate from the economic definitions.

## 10. Inference families

Allowed candidate algorithm families:

- sovereign debt-service decomposition;
- refinancing-wall / maturity waterfall;
- issuance-demand balance decomposition;
- term-premium and auction-stress decomposition;
- foreign-holder / hedge-adjusted repatriation pressure;
- policy-event study;
- balance-sheet transmission graph;
- real-rate suppression decomposition;
- negative-real-return liquidation accounting;
- state-space / regime-switching candidate;
- local-projection candidate for identified policy shocks;
- narrative/event evidence graph only when separated from causal proof.

Prohibited shortcuts:

- high debt/GDP → repression;
- QE → monetization;
- foreign selling → crisis;
- gold up → soft default;
- correlation/Granger lead/feature importance → causal proof.

## 11. Falsifiers

Examples of falsification / downgrade conditions:

1. debt-service burden stabilizes or falls through fiscal adjustment, growth or maturity management without repression;
2. auctions and marginal demand remain healthy despite higher issuance;
3. long real yields remain positive and market-clearing while central-bank support is absent or clearly temporary;
4. policy interventions are time-limited market-function operations and exit without persistent suppression;
5. regulatory demand is unchanged and there is no new captive-buyer mechanism;
6. inflation expectations remain anchored and realized creditor real returns are not persistently negative;
7. foreign-holder reductions are offset by domestic/private demand without term-premium stress;
8. a supposed fiscal-dominance episode is better explained by a standard cyclical monetary-policy shock.

## 12. Historical replay architecture

### Gold Replay A｜United States 1942–1951

Purpose: calibrate an explicit sovereign-funding interest-rate peg and its inflation / real-return consequences.

Mandatory PIT cuts:

- 1942 peg installation;
- 1946–1948 post-price-control inflation;
- 1950 Korean War pressure;
- 1951 Treasury–Fed Accord exit.

### Gold Replay B｜Japan 2016–2024 YCC

Purpose: calibrate yield suppression, central-bank duration absorption, policy flexibility and exit without presuming that every YCC year equals real-value dilution.

Mandatory PIT cuts:

- September 2016 YCC installation;
- December 2022 band widening;
- July/October 2023 flexibility changes;
- March 2024 framework exit.

### Hard negatives

- United States 2020 pandemic QE: large purchases and negative real yields do not by themselves prove fiscal dominance.
- United Kingdom 2022 LDI intervention: emergency gilt purchases for market functioning are not automatically sovereign repression.
- FIMA repo usage / availability: liquidity backstop can reduce forced Treasury sales without monetization.

### Point-in-Time Shadow｜United States × Japan 2026

Question: is the current system moving from `fiscal_constraint_rising` toward `repression_candidate`, or are market-clearing adjustment and liquidity plumbing still sufficient?

Shadow must preserve weekly/as-of snapshots and cannot backfill future policy outcomes.

## 13. Benchmark and qualification

SDR0 must beat simpler baselines on explanatory discipline, false-positive control and state-transition detection.

Baselines:

1. debt/GDP threshold only;
2. net-interest/GDP threshold only;
3. 10Y real yield only;
4. central-bank balance-sheet growth only;
5. foreign Treasury holdings change only;
6. narrative keyword count (`soft default`, `debasement`, `fiscal dominance`) only.

Qualification requires:

- lower false-positive rate on hard negatives;
- earlier or clearer detection of true repression transitions in Gold Replay;
- explicit decomposition of liquidity support vs repression vs real dilution;
- no benefit from lookahead leakage;
- complexity must add stable information beyond the baselines.

## 14. Settlement

Settlement horizons are mechanism-specific:

- market plumbing / auctions: days to quarters;
- fiscal and refinancing pressure: quarters to years;
- financial repression: quarters to multi-year;
- real-value dilution: annual to multi-year.

Settlement observables include realized debt-service burden, debt maturity/refinancing, auction outcomes, central-bank duration absorption, real yields, inflation, official holdings, regulatory-demand changes, currency response and subsequent policy normalization or escalation.

Outcome categories:

- `supported`
- `partially_supported`
- `falsified`
- `indeterminate`

A profitable gold or inflation trade does not prove SDR0 was correct. A bond rally does not automatically falsify the structural fiscal constraint. Mechanism claims settle separately.

## 15. Runtime and governance

SDR0 emits research state only.

It does not authorize:

- portfolio allocation;
- target price;
- duration trade;
- gold/commodity trade;
- currency trade;
- derivatives positioning;
- live execution;
- automatic Canon promotion.

Required runtime receipt fields inherit R2.3-B0 and add:

- `profile_id`
- `jurisdiction`
- `sovereign_curve`
- `fiscal_data_vintage`
- `policy_event_cutoff`
- `replay_or_shadow_mode`

## 16. Strategic interpretation

The most important conceptual upgrade is:

> **“Soft default” is not an event prediction. It is a potentially observable transition from market-clearing sovereign finance toward persistent policy-induced real creditor dilution.**

The research system therefore asks not “Will the U.S. default?” but:

```text
Which constraint is binding?
Which policy function is changing?
Who is absorbing duration?
Is the support temporary plumbing or persistent repression?
Are creditors actually losing real purchasing power?
What evidence would prove the story wrong?
```

## 17. Exit gate

SDR0 may move from `candidate_ready_for_human_review` to `accepted_design` only after Human Review confirms:

- profile remains under `CAP-R-01`;
- `soft_default` is not emitted as an unqualified canonical state;
- liquidity backstop, financial repression and real-value dilution remain distinct;
- the `real_value_dilution_active` AND gate is preserved;
- Gold Replay, hard negatives and 2026 PIT Shadow are mandatory before promotion;
- no trading authority or scalar score has entered the contract.

Reserved Human Gate:

`ACCEPT_SDR0_SOVEREIGN_DEBT_REPRESSION_REAL_VALUE_DILUTION_DESIGN`
