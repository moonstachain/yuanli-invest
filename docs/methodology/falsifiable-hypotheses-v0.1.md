---
title: PNX-S Falsifiable Hypotheses
version: 0.1.0
status: candidate_methodology
portfolio: A9
production_effect: none
---

# PNX-S｜可证伪假说 v0.1

## 0. 目的

PNX-S 只有在能被未来数据证明“没有增量”时，才有资格继续称为研究框架。

本文件冻结首批可证伪假说，防止方法论退化成事后解释器。

---

## H1｜Paradigm Incrementality

### 假说

当 P 结构证据更强时，未来进入长期财富右尾的 base rate 应高于可比基准。

概念表达：

`P(FutureTopTail | P_strong) > P(FutureTopTail | matched_baseline)`

### 失败条件

在足够样本、point-in-time 控制和 matched baseline 下，P 强弱对未来右尾没有稳定区分力，或只能由事后信息重构。

---

## H2｜Narrative Momentum Incrementality

### 假说

`ΔN / Δ²N` 与 narrative state 应对中短期资金流、价格动量、拥挤/反转窗口提供超越静态 attention level 的增量信息。

### 关键子假说

- `accelerate` 的未来传播/资金扩散概率应高于 `discover`；
- `consensus + decelerating` 的 narrative alpha 应低于 `accelerate`；
- `reverse_narrative=strong` 应提高衰减/反转概率。

### 失败条件

静态热度与随机基准已解释全部效果，动态状态没有 held-out 增量。

---

## H3｜Structural Right Tail

### 假说

高 Xs 实体更可能进入未来财富创造 Top 1%–5% 或 matched-universe 的极端右尾。

### 评估

- top-tail precision；
- top-tail recall；
- wealth-tail recall；
- false positive / false negative；
- matched control wealth creation。

### 失败条件

Xs ontology 只能描述已经成功的赢家，无法在 T0 信息约束下区分未来赢家与相似失败者。

---

## H4｜Tail Activation

### 假说

加入 Xa 领先状态后：

`P(Tail | State) `

应相对无条件 base rate 获得稳定、样本外、可校准的概率增量。

### 评估

- Brier score；
- log loss；
- calibration curve；
- precision-recall；
- false alarm rate；
- lead time；
- regime stability。

### 失败条件

仅在训练样本/单一 regime 有效；概率严重失准；false alarm 高到无法使用；或特征依赖未来数据。

---

## H5｜Payoff Convexity

### 假说

在相同 underlying thesis 下，合理识别的 Xp 应改善 realized payoff asymmetry，而不是仅增加理论最大收益。

### 评估

- realized expected payoff；
- right-tail capture；
- left-tail damage；
- premium / carry cost；
- path dependency；
- expiry miss rate。

### 失败条件

考虑价格、IV、theta、流动性与成本后，所谓“凸性机会”长期不优于简单线性表达。

---

## H6｜Valuation as Strike

### 假说

在 P/Xs 相近的资产中，V 对未来 realized payoff 应有增量解释力；极端预付的 optionality 应降低后续投资赔率。

### 评估

- reverse-DCF expectation gap；
- matched P/X cohorts；
- subsequent fundamental delivery vs embedded expectations；
- future return distribution，不只均值。

### 失败条件

V 状态不比简单 valuation baseline 更有解释力，或只能事后合理化价格。

---

## H7｜Survival & Growth

### 假说

在同样 PNX 信号下，加入 S 约束的 paper/shadow portfolio 应：

- 降低 ruin / ES / liquidity breach；
- 改善长期几何财富；
- 同时不过度牺牲关键右尾捕获。

### 候选比较

- unconstrained belief sizing；
- risk-budget baseline；
- full Kelly（研究基准，不是默认策略）；
- fractional Kelly；
- constrained growth-optimal；
- robust/shrinkage variant。

### 失败条件

S 只降低波动，却显著破坏长期几何财富或右尾捕获；或复杂 S 与简单 risk budget 无显著差异。

---

## H8｜PNX Joint Incrementality

### 假说

联合 P/N/X 的研究系统，对未来右尾识别或研究校准的增量应高于单一模块。

必须做 ablation：

- baseline；
- P only；
- N only；
- X only；
- P+N；
- P+X；
- N+X；
- PNX；
- PNX+V；
- PNX+V+S。

### 失败条件

简单模型表现相当或更好，则应保留简单模型，不因理论美感保留复杂性。

---

## 9. 核心组合 KPI 候选

### WTCR｜Wealth Tail Capture Rate

概念定义：

`portfolio captured wealth from future extreme winners / total extreme-winner wealth in eligible universe`

WTCR 的目的不是鼓励集中追涨，而是衡量系统是否真正暴露在长期财富右尾，而非只优化平均命中率。

### 其他指标

- geometric CAGR；
- ruin breach rate；
- expected shortfall；
- max drawdown；
- time-to-recovery；
- tail precision / recall；
- calibration；
- human correction rate；
- evidence fidelity。

---

## 10. 预注册纪律

任何历史 Replay / Future Settlement 必须先冻结：

- T0 / as_of；
- eligible sources；
- excluded sources；
- feature versions；
- hypotheses；
- primary metrics；
- falsifiers；
- outcome window；
- benchmark / matched-control rule。

禁止根据 Outcome 回改 T0 规则或挑选最漂亮的指标。

---

## 11. 科学结论规则

- 单次成功案例不证明方法有效；
- 30 个 seed asset 不足以证明长期资产定价定律；
- 先验证研究纪律和 calibration，再讨论收益增量；
- Future Settlement 是最难作弊、也最慢的证据；
- 如果 PNX-S 没有稳定 incremental predictive power，允许把它降级为解释/研究组织框架。
