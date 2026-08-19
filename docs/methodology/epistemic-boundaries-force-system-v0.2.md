---
title: PNX-S Epistemic Boundaries
version: 0.2.0
status: candidate_methodology
portfolio: A9
production_effect: none
---

# PNX-S｜认识论边界 v0.2

## 0. 目的

本文件继承 `epistemic-boundaries-force-triangle-v0.1.md`，并针对 M1.1 新增的 Xs/Xa/Xp、V 与 S 语义做进一步收口。

核心原则：

> **任何无法区分事实、推断、假说、价格与生存约束的框架，最终都会退化成不可证伪的故事。**

---

## 1. P 的边界

P 可以：

- 用技术/成本/资本/基础设施/制度/生产率证据组织长期结构；
- 使用 Dosi/Perez 等框架描述阶段；
- 构造历史类比与反事实；
- 输出 state / confidence / falsifier。

P 不可以：

- 用固定 50–60 年长波预测具体拐点日期；
- 用历史相似性当因果证明；
- 因某资产价格上涨反证某范式必然正确；
- 因叙事崩盘自动宣布范式结束。

---

## 2. N 的边界

N 可以：

- 研究传播、共识、拥挤、反向叙事与反身性；
- 使用 source/cohort diffusion、velocity、acceleration 等代理指标；
- 研究叙事状态对未来传播/价格路径的增量。

N 不可以：

- 把词频当因果；
- 把传播力当真实性；
- 把当前热度当 TAM 或最终渗透率；
- 忽略价格→叙事的反向因果；
- 把 narrative state 直接翻译成买卖指令。

---

## 3. Xs 的边界

Xs 研究结构性财富右尾。

允许：

- winner-take-most；
- network effects；
- increasing returns；
- bottleneck / lock-in；
- platform optionality；
- value capture。

禁止：

- 仅因大 TAM 就判定强右尾；
- 仅因公司今天是龙头就假设长期 lock-in；
- 仅根据事后超级赢家归纳“赢家特征”；
- 将 Bessembinder 的财富集中结论误读为事前可轻易识别赢家。

---

## 4. Xa 的边界

Xa 研究尾部结果的条件概率变化，不宣称“精确预测黑天鹅”。

必须区分：

- `predictive`；
- `causal_candidate`；
- `identified`；
- `unknown`。

禁止：

- 用 feature importance 直接写因果；
- 用 Granger lead 直接写结构因果；
- 尾部样本极少时用普通 accuracy 宣称高胜率；
- 忽略 multiple testing / data snooping / regime drift；
- 在 point-in-time 不完整时填补未来数据。

---

## 5. Xp 的边界

Xp 研究 payoff geometry，不等于“买期权”。

必须考虑：

- price paid；
- premium / IV / skew；
- theta；
- expiry；
- liquidity；
- path dependency；
- transaction cost。

禁止：

- “最多亏权利金，所以天然优质”；
- 只比较理论最大收益，不比较长期 EV；
- 把 asset optionality 与 instrument convexity 混为一谈。

---

## 6. V 的边界

V 是 price context / strike，不是第四顶点。

允许：

- reverse DCF；
- implied growth / margin / market share；
- valuation distribution；
- expectation gap；
- scenario valuation。

禁止：

- 单 PE/PB 指标自动裁决范式；
- “好公司任何价格都值得”；
- 因高估值自动把 P/X 降为弱；
- 事后根据涨跌倒推事前价格一定合理。

---

## 7. Issuer Durability 与 S 的边界

### Issuer Durability

研究对象层：公司是否能活到 thesis 被验证。

### S｜Portfolio Survival

投资者组合层：整个资本系统是否能持续复利。

禁止继续用同一个 `survival` 字段同时表达两者。

M1.1 只冻结语义；现有 v1.0 Contract 保持不变，等待 M1.2 candidate schema migration。

---

## 8. Kelly 的边界

Kelly 提供 growth-optimal 理论基因，不是无条件生产公式。

必须显式考虑：

- 参数估计误差；
- model uncertainty；
- non-stationarity；
- tail risk；
- liquidity；
- leverage；
- crisis correlation。

禁止：

- 将模型估计胜率直接映射成 full Kelly；
- 用 Kelly 结果绕过组合风险约束；
- 用单一历史样本证明长期概率参数已知。

---

## 9. Evidence 层级

所有 material claim 必须标记：

- `fact`
- `estimate`
- `inference`
- `hypothesis`

### Fact

来源直接支持，不超出 locator 内容。

### Estimate

由公开、版本化公式或来源估算，必须记录公式和输入。

### Inference

由多个事实推出，必须公开推导链和反例。

### Hypothesis

等待未来验证，不得包装成已知事实。

---

## 10. 历史 Replay 边界

历史案例只能用于：

- 暴露机制；
- 构造反事实；
- 训练研究纪律；
- 预注册模型比较。

不得：

- 用已知结局挑选当时不可知指标；
- 只收集赢家；
- 忽略退市、失败、泡沫、幸存者偏差；
- 因三轮历史类比相似就宣称统计定律。

---

## 11. 模型复杂性边界

PNX-S 不因结构复杂而天然优于简单模型。

必须执行 ablation：

- baseline；
- P；
- N；
- X；
- pairwise；
- PNX；
- PNX+V；
- PNX+V+S。

若简单模型 held-out 表现相当或更好，应保留简单模型。

---

## 12. 输出边界

M1.1 可以输出：

- theory candidate；
- state / evidence / falsifier；
- research priority hypothesis；
- future contract proposal；
- replay/eval plan。

M1.1 不可以输出：

- 自动 buy/sell；
- 个性化 position size；
- target price；
- broker execution；
- Evidence/Outcome 自动晋级；
- RSI FROZEN 自动修改；
- A9 canon 自动切换。

---

## 13. 最终纪律

> **框架可以帮助提出更好的问题，但不能获得免于被数据推翻的特权。**

PNX-S 的最高治理原则不是“维护理论完整”，而是：

> **维护 point-in-time、Evidence、Falsifier、Replay 和 Future Settlement 的完整。**
