---
title: Force Triangle Gold Reconstruction
version: 0.1.0
status: candidate_reconstruction
portfolio: A9
pre_registration_commit: 392e4230493f7e860360defdbda82c0c61c48285
---

# A5｜Force Triangle Gold Reconstruction v0.1

## 0. 目标

A4 已经在不知道本轮重建结论之前冻结了三个案例的 T0、允许信息、禁止信息、待检验 P/N/X 假说与 falsifier。A5 的任务不是再写一篇历史故事，而是把三个案例推进到：

`Pre-registration → Source Freeze → Point-in-time Reconstruction → Provisional P/N/X → Human Review`

本轮仍**不接受 Outcome**，也不把任何 P/N/X 对象升级为 `approved`。Evidence Reviewer 仍未具名，因此本轮产物只到 `candidate_reconstruction` / `partial`。

## 1. A5 的法权边界

### 可以做

- 冻结每个案例允许使用的公开来源清单；
- 标记每个来源是否在 T0 前已经公开；
- 把同日但时间戳不充分的来源单列为 `same_day_timestamp_review`；
- 在不使用未来结果的前提下形成 P/N/X 暂定判断；
- 显式记录证据缺口、反证和为什么不能升级结论；
- 为下一轮 Human Review 给出可复核的 disagreement points。

### 不可以做

- 使用 T0 之后的价格、财报、赢家名单反推 T0；
- 把 2026 年研究报告中的后见之明事实当作 T0 Evidence；
- 因为历史最终结果“看起来正确”而修改 A4 的 T0；
- 把浏览器/手机/AI 范式正确自动升级成 Netscape/Apple/NVIDIA 资产正确；
- 接受任何历史 Outcome；
- 修改 RSI FROZEN、A9 operational canon 或生产规则。

## 2. Evidence Freeze 的定义

A5 的 `freeze` 只意味着：**来源集合和 T0 资格被锁定，不再根据后续结论挑选来源。**

它不等于 Evidence 已经正式 admitted。由于原文网页/PDF 必须进入本机或 NAS Evidence Vault 并产生稳定 SHA-256，而当前 GitHub 任务不能假装这些临时网页已经进入真实 Vault，因此来源状态分为：

- `eligible_pending_vault_capture`：时间上合格，但还需要真实 Evidence Vault 捕获与哈希；
- `same_day_timestamp_review`：发布日期与 T0 同日，但精确发布时间不足，需要人工裁决；
- `excluded_post_t0`：明确晚于 T0，禁止进入点时判断；
- `discovery_only`：用于找到原始资料，但本身是后见资料，不能支持 T0 判断。

只有 `eligible_pending_vault_capture` 经 Vault 捕获、locator 固化、Evidence Reviewer 审核以后，才能转换为正式 `SourceRecord / Evidence`。

## 3. 三个案例的暂定重建

> 下面是 **provisional reconstruction**，不是 Gold 判决。机器可读版本见 `reconstructions/force-triangle/*.json`。

### 3.1 PC Internet · Netscape IPO · 1995-08-09

**P：`installation / medium`。**

1995 年点时证据已经足以说明互联网/WWW 不是纯概念：浏览器成为可被普通 PC 用户使用的入口，资本市场开始把互联网当作新的软件与分发层。但 A5 目前没有冻结足够独立的、T0 前互联网用户/主机/骨干流量数据，因此不把“后来互联网改变世界”反向当成 P 的高置信证据。

**N：`accelerate / medium`。**

8 月 6 日的 contemporaneous 媒体已经把 Netscape 描述为 Web 浏览器主导者，同时讨论其极端热门 IPO、Microsoft 竞争与电子商务不确定性；8 月 9 日同日媒体把 IPO 本身描述为对 Internet 的资本市场投票。由于 8 月 9 日来源精确发布时间仍需审计，N 的结论保持中等置信。

**X：`fragile/watch`。**

右尾并非不存在：浏览器拥有入口、分发和跨平台潜力。但点时材料同时显示利润尚未形成、价值捕获路径未被证明、Microsoft 等大型软件商已经是可见竞争者。因此“互联网增长”与“Netscape 捕获互联网增长”不能等号。

**Force：`unknown / high research priority`。**

A4 预注册了 `paradigm_bubble` 候选，但 A5 不因最终历史结果而强行命中。当前证据更支持：**P/N 比 X 更容易在 T0 被识别，单一资产价值捕获仍不足以闭合。**

### 3.2 Mobile Internet · App Store · 2008-07-10

**P：`installation / high`。**

T0 前 Apple 已经卖出约 400 万部 iPhone（截至 2008 财年上半年），并且 iPhone 3G、3G 网络、GPS、iPhone 2.0、开发工具和已宣布的 App Store 分发机制开始形成一个互相强化的系统。这里已经不是单一硬件事件。

**N：`accelerate / high`。**

这个判断只使用 **T0 前** 的核心证据：3 月 SDK 发布后四天下载已超过 10 万次；6 月 Apple 已公开称有数百个第三方应用使用 iPhone SDK 构建，并已预告通过 App Store 进行分发。这已经表明故事从消费者硬件扩散到开发者、企业应用与全球运营商。7 月 10 日发布稿中的“500+ apps”和 iTunes 账户结算细节仅列为 `same_day_timestamp_review`，**不作为 `accelerate/high` 成立的必要证据**。

**X：`convex / survivable`。**

右尾价值捕获链在 T0 前已经可见：硬件 + OS + 开发工具 + 已宣布的 App Store 集中分发 + 运营商渠道共同形成控制栈；同日发布稿中的 iTunes 账户结算细节仍待时间戳复核，不作为 X 成立的必要条件。Apple 同时拥有约 194 亿美元现金、现金等价物和短期投资，左尾生存能力显著强于早期单产品公司。反面是运营商依赖、强竞争和移动监管风险仍真实存在。

**Force：`golden_extreme / high research priority`（Candidate）。**

这里最值得 Human Review 的不是“Apple 后来涨了多少”，而是：**在 2008-07-10 当天，不借助未来 App Store 下载量和后续 iPhone 销量，平台控制点与生存能力是否已经足以支持 `golden_extreme`。**

### 3.3 AI · ChatGPT / NVIDIA · 2023-02-01

**P：`installation / medium-high`。**

T0 前 ChatGPT 已作为公开研究预览出现；Microsoft 在 2023-01-23 已宣布对 OpenAI 进行多年、数十亿美元投资，并明确扩大 AI supercomputing 与 Azure AI infrastructure；NVIDIA 2022-11-18 的 10-Q 已显示 Data Center 单季收入约 38.33 亿美元、同比增长 31%，H100 开始出货。这些都支持 AI 已从论文能力进入真实基础设施建设。

**N：`accelerate / partial`。**

A4 特意选 2023-02-01，是为了检验采用扩散是否已经点燃。但“约两个月破 1 亿用户”的著名数字在公开研究报道中主要于 2 月 2 日以后被广泛引用，因此 A5 明确禁止把它偷渡进 T0。基于 ChatGPT 发布、Microsoft 资本与产品跟进，可以判断跨载体扩散已经开始；但缺少冻结的 T0 用户序列，所以 N 保持 `partial`。

**X：`convex / watch`。**

NVIDIA 在 T0 前已经有真实 Data Center AI 收入、H100、AI software/accelerated-computing platform、云厂商合作和 131.4 亿美元现金及有价证券，说明右尾并非纯叙事。与此同时，2022 Q3 总收入同比下降、库存费用、China export restrictions 与产品周期风险都真实存在，不能用 2023 年后爆发的财报抹掉这些左尾。

**Force：`unknown / high research priority`。**

这是本轮最重要的反后见结论：A5 可以在 2023-02-01 点时识别 **P 强、X 值得重点研究**，但仍缺少“ChatGPT 采用 → hyperscaler capex → NVIDIA 价值捕获”的完整点时证据链。因此不把后来 NVIDIA 的爆发反向写成 T0 的 `golden_extreme` 已证实。

## 4. 三案例对照

| Case | P | N | X | Fundamental Gate | Survival Gate | A5 Force Candidate |
|---|---|---|---|---|---|---|
| PC / Netscape 1995 | installation · medium | accelerate · medium | fragile · watch | partial | partial | `unknown` |
| Mobile / Apple 2008 | installation · high | accelerate · high | convex · survivable | passed | passed | `golden_extreme` |
| AI / NVIDIA 2023 | installation · medium-high | accelerate · partial | convex · watch | passed | passed/partial | `unknown` |

这张表故意不追求“三个经典案例全部命中”。A5 的价值恰恰在于：**若证据不够，就保持 unknown。**

## 5. A5 的三个新增洞察

### 洞察 1｜黄金三角真正区分的是“范式可见性”和“价值捕获可见性”

Netscape 案例中，范式和叙事比资产价值捕获更早可见；Apple 案例中，平台控制点与资产负债表让 X 同步变得可见；NVIDIA 案例中，基础设施 X 已经出现，但 ChatGPT 到 NVIDIA 的传导链在 T0 仍没有后来那么清晰。

### 洞察 2｜`unknown` 不是失败，而是防后见之明的核心状态

如果一套历史模型在三个著名案例里都能完美给出后来的答案，第一嫌疑不是模型太强，而是历史信息泄漏。A5 因此把 `unknown` 保留为一等结果。

### 洞察 3｜下一步必须从“来源清单冻结”进入“Evidence Vault 真冻结”

当前最大的实证短板不是理论，而是历史网页/PDF 的稳定快照、SHA-256、locator 和独立 Reviewer。没有这一步，P/N/X 仍只能是可审查候选，而不是正式历史 Gold。

## 6. Human Review 只审五件事

1. 三个 T0 是否仍然合理，且有没有任何事实偷用了 T0 后信息；
2. PC 1995 的 `unknown` 是否比预注册的 `paradigm_bubble` 更诚实；
3. Mobile 2008 是否已经有足够点时证据把 X 判为 `convex`、Force 判为 `golden_extreme`；
4. AI 2023 是否应该因用户扩散证据未冻结而维持 `unknown`；
5. 哪些来源应该进入 Evidence Vault 成为下一轮正式 SourceRecord/Evidence。

## 7. A5 退出条件

A5 可以合并的最低条件：

- A4 pre-registration 未被篡改；
- 所有 source 都有 T0 eligibility；
- post-T0 source 在 validator 中 fail-closed；
- 三个 reconstruction 都没有 Outcome、收益率或未来财报字段；
- `unknown` 可被保留，不要求命中预注册候选；
- CI 全绿；
- Human Review 明确接受这是 `candidate_reconstruction`，不是 Gold Outcome。

A5 合并后，下一阶段应是 **A6｜Evidence Vault Freeze & Gold Adjudication**：真实抓取原文 → SHA/locator → SourceRecord/Evidence → Reviewer adjudication → 才把 reconstruction 编译成正式 Canon P/N/X Snapshot。