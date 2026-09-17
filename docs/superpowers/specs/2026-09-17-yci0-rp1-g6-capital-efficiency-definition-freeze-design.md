# YCI0-RP1-G6｜Capital Efficiency Definition Freeze — Design

**Date:** 2026-09-17  
**Status:** DESIGN / HUMAN REVIEW REQUIRED  
**Program:** `YCI0｜Yuanli Capital Intelligence Spine`  
**Flagship:** `YCI0-RP1｜AI Infra First Live Reality Admission`  
**Question:** `YCI0-RP0-CQ-001`  
**Authority:** `RESEARCH_ONLY`

## 1. Purpose

Freeze the sixth and final load-bearing AI-Infra Reality dimension before any Capital Efficiency data is selected or admitted.

This design answers one narrow question:

> Are incremental dollars of capital committed across the AI-Infrastructure value chain still converting into incremental operating economics and cash with stable or improving marginal productivity, or is capital efficiency itself becoming the next binding constraint?

This is **not** a company-quality score, valuation model, portfolio rank, or trade signal.

## 2. Why G6 Exists

The first five Reality dimensions answer whether AI infrastructure is expanding, where physical bottlenecks sit, and what the financing regime looks like. They do not answer whether each additional unit of capital is still economically productive.

Therefore:

`CAPEX GROWTH != CAPITAL EFFICIENCY`

`REVENUE GROWTH != CAPITAL PRODUCTIVITY`

`HIGH STATIC ROIC != HIGH INCREMENTAL ROIC`

G6 exists to detect a regime in which Reality may still expand while the marginal economics of that expansion deteriorate.

## 3. Approved Design Choice

Three candidate definitions were considered:

1. Static ROIC basket.
2. Revenue/Capex productivity.
3. Marginal Capital Productivity Stack.

The approved design is **3 — Marginal Capital Productivity Stack**.

## 4. Canonical Economic Construct

`Capital Efficiency` means:

> The ability of newly committed capital to produce incremental after-tax operating profit and cash conversion without requiring a structurally worsening capital burden or external financing dependence.

The construct has three orthogonal components:

1. **Marginal Return** — is incremental invested capital producing incremental operating profit?
2. **Cash Conversion** — are operating economics converting into cash rather than being absorbed by working capital or accounting capitalization?
3. **Capital Burden** — is continued growth requiring progressively more capital intensity or external financing support?

No single generic accounting ratio may substitute for all three components.

## 5. Component 1 — Marginal Return

Canonical formula:

`Incremental ROIC_t = (TTM NOPAT_t - TTM NOPAT_{t-4}) / (Operating Invested Capital_t - Operating Invested Capital_{t-4})`

Where:

- `TTM NOPAT = TTM Operating Income × (1 - TTM effective tax rate)`;
- `TTM effective tax rate = TTM Income Tax Expense / TTM Pretax Income`; if TTM pretax income <= 0 or the implied rate falls outside 0%–50%, NOPAT-based G6 metrics fail closed to `UNKNOWN`;
- `Operating Invested Capital = Total Assets - Cash & Cash Equivalents - Current Marketable Securities - Non-Interest-Bearing Current Liabilities`;
- `Non-Interest-Bearing Current Liabilities = Total Current Liabilities - Short-Term Borrowings - Current Maturities of Long-Term Debt - Current Finance-Lease Liabilities`, to the extent those interest-bearing items are separately disclosed;
- `t-4` is the same fiscal quarter one year earlier; G6 does not use quarter-over-quarter incremental ROIC;
- acquisition-driven or major accounting-regime discontinuities must be explicitly flagged.

Validity rules:

- the YoY increase in Operating Invested Capital must be positive and economically meaningful;
- zero/negative or near-zero YoY invested-capital change => `UNKNOWN`; capital release may be retained as context but is not interpreted through the Incremental ROIC ratio;
- negative NOPAT does not automatically invalidate the observation, but interpretation must remain explicit;
- quarter-to-quarter point estimates are not allowed to masquerade as TTM incremental economics.

Static ROIC may be stored as context, but it is not the G6 canonical marginal-return metric.

## 6. Component 2 — Cash Conversion

Canonical formula:

`Cash Conversion = TTM Operating Cash Flow / TTM NOPAT`

Purpose:

Detect cases where accounting operating profit appears healthy while working capital, capitalization, inventory, receivables, or other balance-sheet absorption weakens cash realization. `CFO / NOPAT` is explicitly treated as a pragmatic cash-conversion proxy, not a pure unlevered operating-cash-flow identity; leverage/interest effects remain a documented boundary.

Validity rules:

- NOPAT <= 0 or near zero => metric is `UNKNOWN` for cross-period state compilation;
- one-off tax, restructuring, acquisition, or working-capital effects must be retained in lineage and may lower confidence;
- Free Cash Flow is not the primary cash-conversion denominator because Capex is separately measured in Capital Burden and double-counting must be avoided.

## 7. Component 3 — Capital Burden

Canonical primary formula:

`Capital Intensity = TTM Capex / TTM Revenue`

Secondary guardrail:

`External Financing Dependence = net external financing required to sustain the operating/investment program`, when a PIT-defensible construction exists.

Capital Intensity is an inverse-efficiency metric: a higher raw value indicates a heavier capital burden, all else equal.

External Financing Dependence is a guardrail, not a mandatory first-proof metric. Absence of a valid guardrail must not be silently replaced with a convenient proxy.

## 8. Metric Directionality Contract

The existing Reality Compiler classifies numerical movement without knowing whether higher values are economically favorable. G6 requires explicit machine-readable directionality.

Closed set:

- `HIGHER_IS_MORE_EFFICIENT`
- `LOWER_IS_MORE_EFFICIENT`

Frozen directions:

- Incremental ROIC: `HIGHER_IS_MORE_EFFICIENT`
- Cash Conversion: `HIGHER_IS_MORE_EFFICIENT`
- Capital Intensity: `LOWER_IS_MORE_EFFICIENT`
- External Financing Dependence: `LOWER_IS_MORE_EFFICIENT`

Compilation must preserve raw Level / Δ / Δ² while using direction-normalized movement for the G6 aggregate state.

Frozen normalization rule:

- `HIGHER_IS_MORE_EFFICIENT` => `oriented_value = raw_value`;
- `LOWER_IS_MORE_EFFICIENT` => `oriented_value = -raw_value`.

Only `oriented_value` is used to derive the efficiency-oriented state. Raw Level / Δ / Δ² remain auditable and must never be sign-rewritten in evidence storage.

No global assumption such as `positive delta = better` is permitted.

## 9. Entity and Cohort Identity

One grammar must cover heterogeneous AI-Infra economics without pretending those businesses are physically identical.

Frozen cohorts:

- `HYPERSCALER`
- `COMPUTE`
- `NETWORKING`
- `POWER_ELECTRICAL`

Initial entity candidates should preferentially reuse already admitted RP1 representatives before expanding scope:

- Hyperscaler: Microsoft
- Compute: NVIDIA
- Networking: Arista Networks
- Power/Electrical: Eaton

Adding other entities is allowed only after the same accounting definition and PIT rules are satisfied.

## 10. Metric Identity Rule

Current `state_compiler.py` groups series by `metric_id`, not by `(metric_id, entity_id)`.

Therefore G6 metric identity must include cohort + entity + component, for example:

`AIINFRA.CAPITAL_EFFICIENCY.HYPERSCALER.MSFT.INCREMENTAL_ROIC`

`AIINFRA.CAPITAL_EFFICIENCY.COMPUTE.NVDA.CASH_CONVERSION`

`AIINFRA.CAPITAL_EFFICIENCY.NETWORKING.ANET.CAPITAL_INTENSITY`

This prevents cross-entity time-series contamination without silently changing existing RP0 identity semantics.

## 11. Time Aggregation and Measurement Regime

Canonical measurement regime:

- quarterly observations;
- every observation represents a TTM economic measure known at that filing/release date;
- at least four consecutive PIT-qualified **derived G6 observations** are required for first production admission;
- because Incremental ROIC uses `t` versus `t-4`, producing four consecutive quarterly G6 observations requires at least eight consecutive quarters of raw filing history;
- Reality Compiler may use the latest three valid derived observations for Level / Δ / Δ², consistent with current RP0 behavior;
- raw calculations must retain every source quarter required to reconstruct each TTM value and its prior-year comparison.

A change in fiscal calendar, accounting presentation, segment definition, or invested-capital construction must be treated as a measurement-regime event, not silently bridged.

## 12. Accounting Regime

For first proof, use company-level GAAP filing data unless a segment-level denominator and numerator can both be reconstructed under a stable, first-party accounting regime.

Rules:

- do not mix company-level NOPAT with segment-level capital;
- do not mix non-GAAP profit with GAAP invested capital unless a separately frozen reconciliation exists;
- do not backfill current segment definitions into historical periods without a first-party restatement;
- tax normalization must be deterministic and documented;
- stock compensation treatment must remain consistent within each entity series.

The objective is comparability through time within an entity first, not false cross-company accounting uniformity.

## 13. Source and PIT Authority

Preferred evidence order:

1. company 10-Q / 10-K / earnings filing and filed exhibits;
2. company investor-relations tables where raw bytes can be archived;
3. structured provider only when semantic identity is proven;
4. authored synthesis may remain context but cannot become PASS evidence by itself.

Every admitted observation must retain:

`source → raw snapshot → normalized components → calculation receipt → known_as_of → content hash → evidence receipt`

Derived ratios inherit no more authority than their weakest required source component.

## 14. Fail-Closed Rules

G6 remains `UNKNOWN` when any mandatory component is not reconstructable under the frozen definition.

Mandatory first-proof components:

- Incremental ROIC
- Cash Conversion
- Capital Intensity

Fail closed on:

- denominator instability or near-zero denominator;
- mixed accounting regimes without explicit bridge;
- missing PIT release semantics;
- missing raw bytes / hash lineage;
- insufficient consecutive observations;
- source semantic ambiguity;
- entity-series collision;
- unregistered metric directionality.

## 15. Cohort and Dimension Aggregation

G6 must not create a 0-100 score.

Each entity/component series first compiles independently to:

`Level → Δ → Δ² → oriented component state`

Then:

1. entity state aggregates its mandatory component states;
2. cohort state aggregates qualified entity states;
3. `capital_efficiency` dimension aggregates qualified cohort states.

Aggregation laws:

- any mandatory component `UNKNOWN` => entity `UNKNOWN`;
- any required cohort with no qualified entity => dimension `UNKNOWN`;
- unanimous oriented states => that state / HIGH confidence;
- disagreement => `MIXED / MEDIUM`;
- no weighting by market cap, revenue, or subjective importance in first proof.

The first proof may use one qualified representative per frozen cohort. This is a coverage proof, not a claim that one company statistically represents the entire cohort.

## 16. State Semantics

For G6, the state refers to **economic efficiency**, after direction normalization:

- `ACCELERATING` — marginal capital productivity is improving at an improving rate;
- `STABLE` — material change is not established;
- `DECELERATING` — marginal capital productivity is deteriorating with negative acceleration;
- `MIXED` — qualified components/cohorts disagree;
- `UNKNOWN` — evidence or construct requirements are not satisfied.

A `DECELERATING` Capital Efficiency state does not imply AI-Infra demand collapse. It means expansion is becoming economically less productive under this construct.

## 17. Hard Negatives

The design must explicitly reject these substitutions:

- high static ROIC => Capital Efficiency PASS;
- revenue growth => capital productivity improvement;
- Capex growth => efficiency deterioration;
- FCF margin alone => cash conversion + capital burden;
- one quarter of ratio expansion => structural acceleration;
- provider field availability => semantic equivalence;
- a blended cross-company series => cohort Reality.

## 18. Machine Contract Changes Required After Human Review

Implementation is expected to add, at minimum:

1. a G6 Capital Efficiency metric contract/registry object;
2. directionality metadata and validator coverage;
3. entity-safe metric identity;
4. tests proving no cross-entity contamination;
5. tests proving inverse metrics orient correctly;
6. calculation receipts preserving numerator/denominator lineage;
7. production compiler support for entity → cohort → dimension aggregation;
8. fail-closed tests for accounting/PIT/denominator breaks.

## 19. No-Authority Boundary

G6 may only extend `RESEARCH` Reality Evidence.

It must not grant or imply:

- Narrative transition;
- Shadow authority;
- Capital authority;
- portfolio sizing;
- broker action;
- execution authority;
- real capital movement.

Even a future `FULL_REALITY_STATE_6_OF_6` only proves six qualified Reality dimensions. It does not by itself prove the investment thesis or authorize `02 EVIDENCE → 03 NARRATIVE`.

## 20. Acceptance Criteria for Definition Freeze

The definition freeze is accepted only if Human Review agrees that:

- the economic construct is marginal, not static;
- numerator and denominator semantics are explicit;
- TTM and PIT time rules are explicit;
- three mandatory components are orthogonal enough to avoid double-counting;
- directionality is machine-readable;
- entity/cohort identity prevents cross-series contamination;
- accounting regime is fail-closed;
- raw lineage requirements are sufficient for replay;
- no scoring/ranking/trading authority is introduced.

## 21. Post-Approval Implementation Sequence

After explicit Human Review of this spec:

1. write the implementation plan;
2. RED-test the frozen contract and directionality laws;
3. implement machine contract/validator changes;
4. prove entity-safe and direction-safe compiler behavior on synthetic fixtures;
5. select first-party sources for the four representative entities;
6. archive raw bytes and reconstruct PIT TTM observations;
7. admit PASS receipts only after physical readback;
8. compile G6;
9. compile the 6/6 Reality state card;
10. keep Human Workbench at `02 EVIDENCE / HOLD` until a separate explicit coverage-transition Human Gate.

## 22. Recovery Point

Current production state remains:

`PARTIAL_REALITY_STATE_5_OF_6 / OVERALL_REALITY_UNSETTLED / HOLD_AT_02_EVIDENCE`

Current G6 state remains:

`capital_efficiency = UNKNOWN`

No data admission or 6/6 mutation is authorized by this design document alone.
