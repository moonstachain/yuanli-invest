# RCN0 Replay #1 B3 Partial Quant Control v0.1

Replay: `RCN-REPLAY-20260820-CN-INNOVATIVE-DRUG-MRNA`

Status: `partial_stress_test_not_b3_pass`

## 1. Purpose

Stress-test whether ordinal Narrative Distance retains explanatory signal after controlling for obvious confounds available from the T0 source. This is **not** the final B3 test because the source exposes full controls for only a selected 11-name table and does not provide beta, complete liquidity history, board/limit-regime encoding, or the full 29-name feature matrix.

## 2. Frozen sample

Only names with T0 source fields simultaneously available for same-day return, market capitalization, YTD return and 1M return were used.

- Near / vaccine-mRNA: 沃森生物, 智飞生物, 康泰生物
- Medium / innovative-drug: 泽璟制药, 神州细胞, 贝达药业, 百济神州, 恒瑞医药
- Farther / CXO: 泰格医药, 凯莱英, 药明康德

n = 11. This sample is selected by source-table availability, not by a pre-registered complete universe; therefore inference is descriptive only.

Ordinal coding: `near=0, medium=1, farther=2`.

## 3. Descriptive bucket returns

- Near mean same-day return: ~19.98%
- Medium mean: ~5.84%
- Farther mean: ~5.51%

The qualitative gradient is dominated by the near bucket.

## 4. OLS stress tests

Dependent variable: same-day return (%).

### Model A | Narrative Distance only

`return ~ D_N`

- D_N coefficient: ~-7.24 percentage points per ordinal step
- R²: ~0.466
- nominal p-value on D_N: ~0.021

### Model B | + log market cap

`return ~ D_N + log(market_cap)`

- D_N coefficient: ~-4.31pp
- R²: ~0.729
- nominal p-value on D_N: ~0.087

Interpretation: market-cap control materially absorbs part of the apparent narrative gradient. This directly confirms that size is a serious competing explanation.

### Model C | + YTD momentum

`return ~ D_N + log(market_cap) + YTD_return`

- D_N coefficient: ~-6.22pp
- R²: ~0.807
- nominal p-value on D_N: ~0.030

### Model D | + YTD + 1M momentum

`return ~ D_N + log(market_cap) + YTD_return + 1M_return`

- D_N coefficient: ~-5.98pp
- R²: ~0.904
- nominal p-value on D_N: ~0.014

## 5. What this does and does not mean

The sign of Narrative Distance remains directionally stable in this selected 11-name stress sample after adding available size and momentum controls. That is useful evidence that the narrative hypothesis is not instantly destroyed by these two confounds.

However **no statistical-pass claim is authorized** because:

1. n=11 is tiny;
2. sample membership is availability-selected;
3. 5 of 7 near-bucket names were near one-price limit-up sessions, so price-limit microstructure is not controlled;
4. beta is missing;
5. full turnover/liquidity history is missing;
6. only 3 of 7 near names enter this regression;
7. the complete 29-name universe is not recovered;
8. same-day cross-sectional association is not causal proof.

## 6. B3 verdict

`B3 = PARTIAL_STRESS_SURVIVED / FULL_TEST_BLOCKED`

The principal falsifier remains live:

> If the D_N relation disappears on the complete pre-registered universe after size, beta, momentum, liquidity and board/price-limit controls, H-RCN-01 fails and `narrative_led` must be downgraded.

## 7. Required full-test inputs

- complete 29-name universe;
- market cap at T0;
- beta estimated on a pre-specified lookback;
- prior 5D/20D/60D momentum;
- turnover/liquidity features;
- board and daily price-limit regime;
- one-price-limit dummy / intraday tradability;
- prior theme membership;
- abnormal return relative to healthcare/growth benchmark.

No Gold admission before these are completed.