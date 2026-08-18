# Q0｜90-Day Implementation Plan v1

Status: `architecture_freeze_candidate`

Goal at Day 90: a reproducible, read-only, 30-asset China/US AI Force Radar with point-in-time evidence, deterministic features, multi-agent candidate research, historical replay/evals and a paper/shadow portfolio. No live trading.

## Days 0-7｜Q0 Architecture Freeze

Deliver:

- Human review architecture package;
- freeze repo boundaries;
- accept logical data model;
- accept candidate schemas;
- accept agent/tool contracts;
- accept 30-asset seed universe as fixture;
- accept eval/CI/Human Gate rules.

Exit: `HG-Q0 = ACCEPT`.

## Days 8-21｜Q1 Universe & Data Contract Qualification

Work in `quant-workspace` + candidate contract PRs.

Tasks:

1. revalidate all 30 listings and vendor identifiers;
2. map Wind codes / US vendor codes / corporate-action history;
3. verify historical market data coverage;
4. verify point-in-time fundamental publication dates;
5. verify historical consensus snapshots where available;
6. freeze AI value-chain mappings with evidence;
7. add 5-10 control/counterexample assets for eval, without expanding the product radar yet;
8. define data quality states and missingness report.

Exit criteria:

- 30/30 identifier valid;
- market data completeness measured;
- fundamental/estimate coverage matrix published;
- no ambiguous current-symbol backfill in historical periods;
- Wind licensing/storage boundary documented.

## Days 22-35｜Q2 Data Plane + Deterministic Feature Store

Build in `quant-workspace`:

- DuckDB migrations;
- incremental ingestion;
- source snapshot manifests;
- feature registry;
- fundamental gates features;
- survival features;
- right/left-tail quant features;
- macro snapshot adapter from `yiru-macro-cockpit`;
- point-in-time query API/MCP server.

Initial feature families:

- price/liquidity/volatility;
- revisions/growth/margins/FCF;
- debt/cash/refinancing/dilution;
- CAPEX/inventory/receivables;
- EVT/VaR/ES subset;
- industry capacity/price where data exists;
- narrative event counts/source diversity.

Exit: deterministic rerun on same manifest yields byte/row-equivalent outputs within defined tolerances.

## Days 36-49｜Q3 Evidence + Narrative Graph

Build:

- source/claim/locator index;
- Wind Alice -> discovery-only adapter;
- raw capture worker into local/NAS Evidence Vault;
- SHA/locator receipts;
- narrative node registry;
- cohort/event schema;
- `ΔN`, `Δ²N`, crowding and reverse-narrative feature prototypes.

Continue A6 historical Evidence Vault work in parallel, without letting Q3 silently promote it.

Exit:

- at least 5 current narratives tracked across multiple cohorts;
- point-in-time evidence query works;
- machine summary cannot bypass SourceRecord/Evidence boundary.

## Days 50-63｜Q4 Force Agent Runtime

Implement OpenAI Agents SDK runtime:

- `ForceCIOAgent`;
- six specialists;
- strict output schemas;
- MCP/function tool adapters;
- tracing;
- input/tool/output guardrails;
- approval interruptions for W1/G1;
- runtime profiles configurable by environment.

Test on 5 assets first, then 30.

Exit:

- 30 assets can complete candidate run or fail closed;
- no unsupported governance writes;
- no live trading fields;
- trace/run artifact saved for every run.

## Days 64-72｜Q5 Force Radar MVP

Build three surfaces:

1. Force Radar overview;
2. Asset Research Page;
3. Change Queue.

Daily batch computes deterministic data first, then agent reasoning.

User-facing output prioritizes change:

- P state transition;
- N acceleration/reversal;
- X structural change;
- Fundamental/Survival gate change;
- Research Priority delta.

Exit: RAY can review all high-value changes in <=20 minutes/day in shadow use.

## Days 73-82｜Q6 Replay / Eval Expansion

Expand historical cases:

`3 Gold seed -> minimum 30 replay cases`.

Required composition:

- known winners;
- failed leaders;
- bubbles;
- durable survivors;
- incumbent disruption;
- false-positive-like setups;
- false-negative-like setups;
- China and US examples.

Run architecture ablations:

- single agent;
- specialists;
- +Red Team;
- +Evidence Judge.

Exit:

- zero lookahead leakage on accepted cases;
- multi-agent benefit measured rather than assumed;
- held-out subset established.

## Days 83-90｜Q7 Shadow Portfolio & Go/No-Go Review

Create research-only shadow portfolios/benchmarks:

- high research priority basket;
- `golden_extreme` candidates;
- `latent_dragon` candidates;
- matched AI control basket;
- broad market benchmark.

Measure without optimizing to the first 90 days:

- research precision/false positives;
- thesis survival;
- drawdown;
- fundamental confirmation;
- rank stability;
- human correction rate;
- system cost/latency.

Day-90 Human Review decides:

- continue 30 assets;
- expand to 100;
- redesign N/X engine;
- pause agent complexity;
- authorize a separate production hardening phase.

No automatic move to 300 assets and no live execution.

# Workstream Ownership

| Workstream | Primary repo/system | Authority |
|---|---|---|
| methodology/contracts/canon | yuanli-invest | candidate until Human Gate |
| market/fundamental/features/backtest | quant-workspace | current operational quant plane |
| macro regime | yiru-macro-cockpit | provider only |
| raw evidence | local/NAS Evidence Vault | physical source truth |
| Wind retrieval | Wind licensed environment | source/data provider |
| agent orchestration | yuanli-invest runtime package (future implementation) | candidate research only |
| self-evolution | yuanli-invest-rsi | isolated challenger, FROZEN protected |

# Day-90 Definition of Done

A successful 90 days does **not** mean the model makes money. It means:

- data is reproducible and point-in-time;
- P/N/X judgments are evidence-grounded and machine-readable;
- historical replay is hard to game;
- agents add measured value over simpler baselines;
- human review can identify and correct errors;
- shadow outcomes can begin accumulating honestly;
- governance remains intact.
