---
title: Survival Constitution
version: 0.1.0
status: candidate_methodology
portfolio: A9
production_effect: none
---

# S｜Survival Constitution v0.1

## 0. 宪法第一条

> **Never Risk the Right to Compound.**
>
> 永远不要拿继续复利的资格去下注。

S 不是“风险厌恶”，也不是单纯降低波动。它研究的是：

> 在重复决策、参数未知、相关性会突变且尾部风险存在的现实世界里，如何让资本长期存活，并在存活约束下最大化几何财富增长。

---

## 1. 为什么 S 是外环而不是第四角

财富过程是乘法过程：

`W_T = W_0 × Π(1 + r_t)`

一旦资本进入不可逆的死亡状态，后续任何右尾机会都失去意义。

因此：

- P/N/X 决定哪里存在 edge / timing / payoff；
- S 决定是否有资格等待 edge 兑现。

`S = 0` 时，任何 P/N/X 优势都无法形成长期财富。

所以 S 是系统约束，不与 P/N/X 争夺第四顶点。

---

## 2. 理论基座

### Roy｜Safety First

第一问题：

> 如何降低财富或收益跌破不可承受阈值的概率？

概念表达：

`min P(W < W_critical)`

Roy 提供 S 的底线逻辑：先定义 dread event / ruin boundary。

### Kelly｜Growth Optimal

第一问题：

> 在存在可重复正 edge 时，下注多少可最大化长期对数财富/几何增长？

概念目标：

`maximize E[log W]`

Kelly 提供 S 的增长目标函数，而不是生产系统里可以不加折扣直接执行的万能仓位公式。

### Merton｜Dynamic Portfolio

把单一赌局扩展为多资产、跨时间的财富配置与动态决策。

### Knight / Model Uncertainty

现实中的胜率、赔率、相关性与分布参数不是已知常数。参数误差本身必须进入仓位折扣和 robustness 设计。

### Rare Disaster / Tail Risk

低概率巨大损失对长期复利具有非线性破坏，单看日常波动或相关性会低估生存风险。

---

## 3. S 与 Issuer Durability 必须分开

当前旧体系里，公司左尾和组合生存存在语义重叠。v0.1 正式定义：

### Issuer Durability

研究对象层：

- cash / debt；
- maturity wall；
- refinancing dependency；
- dilution；
- customer / supplier concentration；
- regulatory ruin；
- technical obsolescence；
- capital-cycle overbuild。

它回答：

> 公司/资产本身能否活到 thesis 被验证？

### Portfolio Survival

投资者层：

- position concentration；
- correlation / crisis correlation；
- leverage；
- liquidity；
- gap risk；
- Expected Shortfall；
- drawdown；
- ruin probability；
- cash buffer；
- fractional Kelly / constrained growth-optimal sizing。

它回答：

> 即使 thesis 错了，整个资本系统还能不能继续？

二者不得继续共用一个模糊的 `survival` 语义。

---

## 4. Ruin Boundary 必须先定义

“破产”不只等于净值归零。

现实的 ruin boundary 可以包括：

- 强平 / margin breach；
- 最大回撤超过既定阈值，导致策略无法继续；
- 流动性不足以覆盖固定现金需求；
- 赎回/负债义务无法履约；
- 杠杆 covenant breach；
- 单一风险因子导致不可逆资本损失；
- 组合规模跌到无法继续执行既定策略的阈值。

后续 `PortfolioSurvivalPolicy` 必须显式记录这些阈值，而不是等风险发生后临时解释。

---

## 5. 概念目标函数

未来确定性计算层可以研究：

`maximize expected log wealth`

subject to：

- `P(Ruin) < epsilon`
- `ExpectedShortfall_alpha < L`
- `Drawdown < D_max`
- `LiquidityBuffer > B`
- `GrossLeverage < L_max`
- crisis correlation stress passes

本文件不冻结具体数值阈值，不输出个性化仓位。

---

## 6. 为什么不能直接 Full Kelly

标准 Kelly 对 edge / probability / payoff 的估计质量高度敏感。

现实输入是：

`estimated_edge = true_edge + model_error`

因此 production research 不能把估计概率直接映射成 full Kelly。

必须显式考虑：

- model uncertainty；
- estimation error；
- fat tails；
- changing regime；
- liquidity；
- path dependency；
- correlation breakdown；
- parameter non-stationarity。

后续 paper/shadow 研究优先比较：

- fractional Kelly；
- constrained growth-optimal；
- risk-budget baseline；
- robust / shrinkage variants。

并通过 held-out / future settlement 决定是否有增量。

---

## 7. S 主要应由确定性系统计算

S 不应该成为一个“SurvivalAgent 给 85 分”的 LLM 模块。

建议职责：

### LLM 可做

- 提取风险情景；
- 识别未建模约束；
- 解释为什么某个 stress scenario 重要；
- 生成 counterfactual / red-team scenarios。

### Python / DuckDB / Optimizer 应做

- exposure aggregation；
- VaR / ES / EVT plugin；
- drawdown；
- liquidity ladder；
- leverage；
- correlation stress；
- ruin simulation；
- fractional Kelly / growth optimization；
- deterministic policy breach checks。

因此 S 的工程主权应主要位于 `quant-workspace`，而 Canon 合同与政策定义位于 `yuanli-invest`。

---

## 8. S 的评估标准

不能只看 Sharpe。

至少需要：

- `ruin_breach_rate`；
- `max_drawdown`；
- `expected_shortfall`；
- `liquidity_breach_rate`；
- `stress_survival_rate`；
- `geometric_cagr`；
- `right_tail_capture`；
- `capital_recovery_time`。

目标不是把波动降到最低，而是：

> **在不牺牲关键右尾暴露的前提下，显著降低永久退出概率。**

---

## 9. 三条禁止事项

1. 禁止把“低波动”直接等同于“安全”；
2. 禁止把 full Kelly 当作参数已知世界之外的默认生产仓位；
3. 禁止把公司资产负债表风险和组合破产风险继续混成同一个 Survival Gate。

---

## 10. M1.1 边界

本文件仅冻结 S 的理论地位和工程边界：

- 不修改现有 ForceRadar Schema；
- 不实现 Kelly / ruin calculator；
- 不输出仓位；
- 不授权 paper/live portfolio action；
- 不修改 RSI FROZEN。

后续 M1.2 才允许提出 `PortfolioSurvivalPolicy` / `PortfolioSurvivalSnapshot` Candidate Schema；实际算法留在 `quant-workspace` 的 paper/shadow 路径验证。
