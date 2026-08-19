---
title: M1.1 PNX-S Theory Canon Human Review Card
version: 0.2.0
status: candidate_review_card
portfolio: A9
---

# M1.1｜PNX-S Theory Canon v0.2 Human Review

## Review purpose

本轮只审理论语义是否值得成为下一阶段 Contract Hardening 的母版，不审收益表现，不授权生产动作。

## 必审五题

### 1. P/N/X/S 的本体边界是否清楚？

目标口径：

- `P = Reality / Direction`
- `N = Belief / Timing`
- `X = Distribution / Payoff`
- `S = Portfolio Survival / Growth Constraint`

拒绝条件：S 仍与公司级 durability 混淆，或 P/N/X 退化成综合评分维度。

### 2. X 拆成 Xs / Xa / Xp 是否成立？

- `Xs = Structural Right Tail`
- `Xa = Tail Activation`
- `Xp = Payoff Convexity`

拒绝条件：三层无法产生独立可证伪问题，或只是换名不改变研究对象。

### 3. V 作为 Strike / Price Layer 是否比“第四角”更严谨？

拒绝条件：V 被重新包装成与 P/N/X 直接相乘的黑箱分数。

### 4. S 是否应从资产卡迁移到组合层？

接受条件：公司级 `Issuer Durability` 与投资者级 `Portfolio Survival` 被明确解耦。

### 5. 理论是否保留被数据推翻的能力？

必须存在 H1-H8、Ablation、point-in-time、held-out、Future Settlement 和简化模型优先原则。

## Explicit non-decisions

Human Review 即使接受 M1.1，也不代表：

- M1.2 Contract migration 自动通过；
- Q1 Force state 可开始生成；
- Evidence / Outcome 可自动 admission；
- PNX-S 已被证明具有预测增量；
- 可以输出仓位、目标价或交易指令；
- A9 operational canon 切换；
- RSI FROZEN 修改。

## Decision options

- `ACCEPT_M1_1_PNXS_THEORY_CANON`
- `ACCEPT_M1_1_WITH_CHANGES`
- `REJECT_M1_1_PNXS_THEORY_CANON`

## Accepted follow-on if approved

只允许进入：

`M1.2｜Extreme / Survival Semantic Contract Split`

并要求 v1.0 contract 保持兼容，不原地破坏历史 Replay。
