---
title: Force Triangle Gold Replay Set
version: 0.1.0
status: pre_registered_reconstruction
portfolio: A9
---

# 原力投研黄金三角｜三轮 Gold Replay Set v0.1

## 1. 目的

这组回放不用于证明“黄金三角一定有效”，而用于检验：在**结果尚未知**的点时信息约束下，P/N/X 能否稳定地区分：

1. 范式正确 vs 具体资产正确；
2. 叙事加速 vs 价值已经兑现；
3. 右尾潜力 vs 左尾脆弱；
4. 成功案例 vs 失败/幸存者偏差。

首批三轮：

- PC 互联网：1995 Netscape IPO；
- 移动互联网：2008 App Store；
- AI：2023 ChatGPT 扩散后的早期算力基础设施。

## 2. 状态边界

当前状态：`pre_registered_reconstruction`。

原因：历史材料已经存在，但独立 Evidence Reviewer 仍未具名，且历史时点的 Evidence 集尚未逐条冻结。因此本轮只冻结**T0、允许信息、禁止信息、P/N/X 问题、Outcome 窗口和失败判据**；任何 P/N/X 初始分类都只是待重建假说，不是 `approved` 研究结论。

## 3. Gold Replay 六条硬纪律

1. **T0 先冻结**：先写 T0，再取证；
2. **point-in-time**：只允许 T0 当日或之前公开可得信息；
3. **禁未来泄漏**：未来赢家、崩盘、财报、指数成分、估值峰值不得反向进入 T0；
4. **P/N/X 分开裁决**：不得因为后续收益高反向提高 P、N 或 X；
5. **双 Outcome**：市场 20/60/120/250 日 + 至少两个后续财报期；
6. **失败也入 Gold**：失败案例与成功案例同等重要；若只能解释赢家，则框架失败。

## 4. Replay 输入协议

每个案例在真正生成 Canon Replay 前必须冻结：

```text
T0
├── evidence_cutoff
├── admissible_sources
├── prohibited_future_information
├── ParadigmSnapshot hypothesis
├── StageSnapshot hypothesis
├── ConvexityProfile hypothesis
├── Fundamental Gate hypothesis
├── Survival Gate hypothesis
├── ForceTriangle classification hypothesis
├── falsifiers
└── outcome windows
```

真正落入 `canon/replays/` 时，应通过 `Replay.force_triangle_mode = pnx_pre_registered` 或 `pnx_reconstructed_partial` 连接具体 P/N/X snapshot ID。

## 5. Outcome 不等于单一收益率

Outcome 至少分三面：

- **market**：20/60/120/250 日相对与绝对表现、最大回撤；
- **fundamental**：后续两期财报的收入、利润、单位经济、订单/采用；
- **structural**：范式扩散、平台控制、价值捕获、左尾生存是否按 T0 假说演化。

一个对象可以出现：

- 范式判断正确，但资产失败；
- 叙事判断正确，但价格先于基本面透支；
- 右尾结构正确，但左尾融资/稀释导致验证失败；
- 短期价格错误，但长期结构假说仍未被证伪。

## 6. 三个预注册案例

| Case | T0 | 主要问题 | 预注册重点 |
|---|---|---|---|
| PC-1995 | 1995-08-09 | 互联网范式是否成立，但 Netscape 是否具有可持续价值捕获？ | 强制区分 P 与 X |
| Mobile-2008 | 2008-07-10 | App Store 是否把移动互联网从设备创新推向平台生态？ | 检验 P/N/X 同向时的可识别性 |
| AI-2023 | 2023-02-01 | ChatGPT 叙事加速时，算力基础设施是否同时具有范式与极值结构？ | 检验早期 N 加速与 X 的独立性 |

详细协议见同目录三个 case 文件。

## 7. 晋级条件

从 `pre_registered_reconstruction` 升到 Canon Gold Replay 至少需要：

- historical Narrative / Evidence / SourceRecord 可定位；
- Evidence cutoff 逐条通过 point-in-time 检查；
- P/N/X snapshot 用新 Schema 验证；
- Replay `lookahead_check = passed`；
- 至少一个明确失败案例；
- Outcome 接受仍需独立 Evidence Reviewer / Human Gate；
- 禁止因 Replay 表现好自动修改方法论或 RSI FROZEN。
