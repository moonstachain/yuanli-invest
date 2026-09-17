# YCI0-RP1-G2｜NVIDIA Compute Reality Receipt

**Status:** `PASS_EVIDENCE / COMPUTE_ACCELERATING / PARTIAL_REALITY_ONLY`  
**Date:** 2026-09-17  
**Authority:** `RESEARCH_ONLY`

## First-party PIT series

Series: `NVDA_DATA_CENTER_REVENUE_QUARTERLY_USD_BN`  
Measurement regime: `NVIDIA_QUARTERLY_DATA_CENTER_REVENUE`

| Quarter | Quarter end | Known as of | Data Center revenue (USD bn) | Claim Receipt |
|---|---|---|---:|---|
| FY26 Q3 | 2025-10-26 | 2025-11-19 | 51.2 | `25d9f1f0-e74c-4ec7-82ec-025585e12366` |
| FY26 Q4 | 2026-01-25 | 2026-02-25 | 62.3 | `eb6ec500-3528-499e-9cb7-473e1f95b8f1` |
| FY27 Q1 | 2026-04-26 | 2026-05-20 | 75.2 | `8c1a92c2-defc-4e47-95be-02da47688804` |
| FY27 Q2 | 2026-07-26 | 2026-08-26 | 89.0 | `b9982a3f-59ab-4aa5-b75d-0a9af5da1110` |

All four claims are `PASS / COMPANY_PRIMARY_DISCLOSURE / RESEARCH_ONLY` and point to first-party NVIDIA Newsroom raw HTML archived in private `ymq4-raw-evidence`.

## Raw archive proof

GitHub Actions run: `35178170769`  
Artifact: `yci0-rp1-nvda-compute-receipt` (`10478553155`)

Raw SHA-256:

- FY26 Q3: `14d44bb7d4726ac7ac9c9b619005c972078249178a698f4fb4abcd06f325e5be`
- FY26 Q4: `2f66a120d113392370b010c3e1a6d47336f4daf1a1421fd1b9478bc145f39e6e`
- FY27 Q1: `8deb1c9faae10aef480136e257ab94367ce6e46e50d942195dc4987d2cec1716`
- FY27 Q2: `282f517583f249b35d4e497b64c8370439b42034e31fc0f31481753740e73c70`

Every object passed `raw_sha256 == storage_readback_sha256` and the archive workflow granted zero downstream authority.

## Wind equivalence

Wind `stock_data.get_stock_fundamentals` returned `数据中心产品 / 主营项目收入` in `亿元` with period/value behavior that does not establish identity with NVIDIA's quarterly Newsroom `Data Center revenue` series.

Verdict: `NON_EQUIVALENT / ADJACENT_SEGMENT_CONTEXT`.

## Reality Compiler

As of `2026-08-26T23:59:59Z`:

- `compute.level = 89.0` USD bn
- `compute.Δ = +13.8` USD bn
- `compute.Δ² = +0.9` USD bn
- `compute.state = ACCELERATING`
- `compute.confidence = HIGH`

Combined with the previously qualified Microsoft capex proxy:

- `hyperscaler_capex = ACCELERATING / HIGH`
- `compute = ACCELERATING / HIGH`
- `financing_regime = UNKNOWN`
- `networking = UNKNOWN`
- `power_grid = UNKNOWN`
- `capital_efficiency = UNKNOWN`

Production state card:

- `state_card_id = 65e4ab4f-0923-4fde-9518-9b7b2c4accff`
- `run_id = d82d5df6-5f03-46e3-a7ed-342853323153`
- `state_hash = a1a2b4f0b94ba766906be0a7e6af9950d9f292e05f9c5c144e76b81c4d6fa26e`
- `scope_status = PARTIAL_REALITY_STATE_2_OF_6`

## Anti-claim

Two qualified accelerating dimensions do **not** establish overall AI-Infra Reality acceleration.

Human Work therefore remains:

`02 EVIDENCE / READY / OPEN / Delta UNKNOWN / Delta2 UNKNOWN / HOLD`

No Narrative, Research Projection, Shadow, Capital, or Execution authority follows from this receipt.
