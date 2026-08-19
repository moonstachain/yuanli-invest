---
title: Valuation as Strike Price
version: 0.1.0
status: candidate_methodology
portfolio: A9
production_effect: none
---

# V｜Valuation as Strike Price v0.1

## 0. 定义

估值不是黄金三角的第四个顶点，也不是一个可以与 P/N/X 直接相乘的分数。

v0.1 将 V 定义为：

> **Price of Optionality / Strike Price：为了获得某个未来右尾分布，今天支付的价格。**

伟大资产不等于伟大投资。P、N、X 可以全部很强，但如果未来极大部分乐观结果已经被当前价格预付，投资的实际 convexity 仍可能很差。

---

## 1. V 在系统中的位置

```text
P｜世界可能多大
N｜共识处在什么阶段
Xs｜公司可能捕获多少
Xa｜极值概率如何变化
Xp｜payoff 几何
        ↓
V｜市场已经收了多少钱
        ↓
Investment Thesis Context
```

因此 V 不是“发现世界变化”的维度，而是把未来状态空间转换成当前投资赔率的价格层。

---

## 2. 估值需要回答的不是“贵不贵”

核心问题应是：

1. 当前价格隐含了怎样的收入增长？
2. 隐含了怎样的利润率、资本效率和市场份额？
3. 隐含了多长的高增长持续期？
4. 隐含了多少新业务 optionality？
5. 当前 narrative premium 是否已经把未来共识提前计价？
6. 若最乐观范式兑现但 value capture 低于预期，当前价格是否仍有安全边际？

所以推荐工具是：

- reverse DCF；
- implied growth / margin；
- historical valuation distribution；
- peer / value-chain relative context；
- scenario-based valuation；
- expectation gap；
- optionality decomposition。

---

## 3. V 与 Xp 的边界

### V

回答：

> 未来状态空间已经被市场定价到什么程度？

### Xp

回答：

> 在这个价格和表达工具下，收益函数是否有利地非线性？

二者相互作用，但不得合并为一个模糊的“赔率分数”。

例如：

- 伟大公司 + 极贵股票：Xs 强，V 可能差；
- 普通公司 + 深度错误定价：Xs 不强，但 V 可能有战术价值；
- 长期右尾资产 + 合理价格：可能形成战略 convexity；
- 长期期权 + 极高 IV：工具 payoff 凸，但 Xp 的实际 EV 仍可能很差。

---

## 4. V 与 N 的边界

N 高并不自动表示 V 贵；N 低也不自动表示 V 便宜。

需要独立研究：

- 共识传播是否已进入 saturation；
- 乐观预期是否进入价格；
- narrative premium 是否高于 fundamental realization；
- 价格变化是否本身在增强 narrative reflexivity。

因此：

`Narrative Crowding != Valuation Overpricing`

但二者同时出现时，需要显著提高 Red Team 强度。

---

## 5. 推荐状态语言

M1.1 只冻结理论语言，不实施 Schema。后续可候选化：

- `underpriced_optionality`
- `partially_priced`
- `fully_priced`
- `prepaid_extreme`
- `dislocated`
- `unknown`

任何状态必须绑定：

- valuation method revision；
- point-in-time inputs；
- scenario assumptions；
- evidence / counterevidence；
- sensitivity；
- falsifier。

---

## 6. 禁止事项

- 禁止用单一 PE/PB percentile 代替完整 expectation analysis；
- 禁止因为成长快就宣布“任何估值都合理”；
- 禁止因为估值高就自动否定 P/X；
- 禁止把事后涨跌反推事前估值一定正确/错误；
- 禁止在当前研究阶段输出目标价或自动交易结论。

---

## 7. 核心原则

> **Price is not a verdict on the paradigm; it is the entry condition for the payoff.**

价格不裁决范式真假，但价格决定投资者为了参与这个范式支付了什么。

所以原力投研的估值哲学不是寻找“最便宜”，而是：

> **避免为尚未兑现的右尾支付一个已经假设右尾必然兑现的价格。**
