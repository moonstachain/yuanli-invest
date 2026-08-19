---
title: Extreme Engine
version: 0.1.0
status: candidate_methodology
portfolio: A9
production_effect: none
---

# X｜Extreme Engine v0.1

## 0. 目的

X 不再等同于“公司右尾 + 公司左尾 + 一点 EVT”的混合 Profile。v0.1 把极值问题拆成三个彼此不同、但需要联合研究的层次：

```text
Xs｜Structural Right Tail
        ↓
Xa｜Tail Activation
        ↓
Xp｜Payoff Convexity
```

目标不是“寻找必涨十倍股”，而是：

> **识别结构性右尾、监测极值条件是否正在变化、并研究当前价格/工具对应的收益几何。**

---

## 1. Xs｜Structural Right Tail

### 1.1 第一问题

> 如果一个范式真的扩散，为什么财富不是平均分给全行业，而可能集中到少数实体？

### 1.2 结构面

- `winner_take_most`
- `network_effects`
- `scale_economics / increasing_returns`
- `bottleneck_control`
- `switching_cost`
- `ecosystem_lock_in`
- `platform_optionality`
- `market_expansion`
- `reinvestment_runway`
- `value_capture`

### 1.3 关键边界

- 大 TAM 不等于强 Xs；
- 行业增长不等于公司价值捕获；
- 市占率高不等于永久 winner-take-most；
- 技术领先必须与经济捕获机制分开取证；
- Bessembinder 式右尾集中是 base-rate 事实，不是事前预测能力证明。

### 1.4 未来可检验命题

`P(Future wealth creator in top tail | Xs=strong)` 应显著高于 matched baseline；否则 Xs ontology 需要重构。

---

## 2. Xa｜Tail Activation

### 2.1 第一问题

> 在极值结果的无条件概率很低时，哪些当前状态会使其条件概率发生可重复、可校准的变化？

形式化问题：

`P(Tail_{t+h} | State_t)` 与 `P(Tail_{t+h})` 是否存在稳定增量？

### 2.2 两个时间尺度

#### Xa_long

研究 3–10 年财富右尾是否正在被激活。

候选领先状态：

- market-share reinforcement；
- incremental ROIC；
- reinvestment rate / runway；
- unit economics；
- ecosystem expansion；
- switching cost strengthening；
- bottleneck scarcity；
- value-capture widening；
- productivity evidence；
- dilution / capital intensity deterioration as counter-signal。

#### Xa_event

研究数日—数月的价格极值：

- crash / squeeze；
- volatility regime break；
- commodity spike；
- liquidity shock；
- extreme upside/downside return。

允许工具：

- POT / GPD / EVT；
- conditional quantile；
- regime-switching；
- rare-event classifier；
- leading-factor ensemble；
- point-in-time causal candidate graph。

### 2.3 因果状态必须显式

任何领先关系只允许标记：

- `predictive`：样本外具有增量预测力；
- `causal_candidate`：存在可辩护机制，但仍可能受共同原因/反向因果影响；
- `identified`：满足明确识别策略；
- `unknown`。

禁止：仅因 Granger lead、feature importance 或时间先后就写 `causal`。

### 2.4 尾部稀疏纪律

极端事件天然样本少，因此必须比均值预测更严格：

- point-in-time feature availability；
- walk-forward；
- regime holdout；
- multiple-testing control；
- probability calibration；
- precision-recall，而非 accuracy；
- false-alarm rate；
- independent replay / future settlement。

---

## 3. Xp｜Payoff Convexity

### 3.1 第一问题

> 当前价格、期限和表达工具，是否把同一个基本判断转换成有利的收益分布？

### 3.2 区分资产凸性与工具凸性

**Asset convexity**：业务/生态本身拥有开放右尾，例如新市场 optionality。

**Instrument convexity**：期权、权证等 payoff 非线性。

两者都不能单独证明正期望值。

### 3.3 研究面

- upside openness；
- maximum / practical downside；
- valuation embedded expectations；
- premium / implied volatility；
- skew；
- theta / time decay；
- liquidity / spread；
- path dependency；
- expiry mismatch；
- financing / leverage dependency。

### 3.4 核心纪律

`Convex payoff != Positive EV`。

概念上应研究：

`Expected Payoff - Price Paid - Frictions`

以及：

`Right Tail Capture / Left Tail Damage`

而不是只比较“最多亏多少”和“理论最多赚多少”。

---

## 4. 与 V、Issuer Durability、S 的边界

### V｜Valuation

V 负责检查市场已经为 X 的右尾收取多少价格。

### Issuer Durability

公司资产负债表、再融资、稀释、监管归零、技术替代等属于“研究对象能否维持 thesis 验证资格”。它不是 Portfolio Survival。

### S｜Portfolio Survival

仓位、相关性、杠杆、流动性、Expected Shortfall、Ruin Probability、Kelly 等属于投资者组合层。

因此：

```text
X != Issuer Durability != S
```

M1.1 先冻结这一语义；M1.2 再修改合同。

---

## 5. X 的三个典型错误

### 错误 A｜“行业很大，所以公司有极值”

缺失：value capture / competition / capital intensity。

### 错误 B｜“领先指标出现，所以黑天鹅可预测”

缺失：base rate、校准、false alarm、机制与样本外验证。

### 错误 C｜“买期权最多亏权利金，所以天然优质”

缺失：premium、IV、theta、expiry、liquidity 和长期负 carry。

---

## 6. 未来机器对象建议（不在 M1.1 实施）

后续 M1.2 可拆为：

- `StructuralRightTailProfile`
- `TailActivationSnapshot`
- `PayoffConvexityContext`

旧 `ConvexityProfile` 保留兼容，不原地破坏；新合同只能以 candidate vNext 方式进入。

---

## 7. X 的科学目标

X 不以短期命中率证明自己，而要回答三个独立问题：

1. Xs 是否提升未来 Top-Tail Wealth Creator 的识别率？
2. Xa 是否对 tail event / wealth-tail transition 提供稳定、可校准的条件概率增量？
3. Xp 是否在 matched thesis 下改善 realized payoff asymmetry，而不是仅提供漂亮叙述？

任一问题长期无法获得增量证据，对应子模块必须允许被降级或删除。
