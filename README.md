# 原力投研 · Yuanli Invest

原力投研是 **Research Capability Canon｜研究能力正典仓**。它的长期使命是：

> **Compile investment knowledge into machine-callable research intelligence.**
> 把投资理论、学术论文与经验研究中的有效机制，编译为可调用、可验证、可复用、可审计的研究能力。

仓库的中心对象是 `ResearchCapability`；股票、行业和资产是这些能力在 Wind AI、Codex 或 Reference Quant Runtime 中的 runtime targets，而不是 GitHub 的中心对象。

## Canon 编译链

```text
Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill
```

横向通过 `CanonicalDataField ↔ ProviderAdapter` 实现 provider independence：**算法属于原力，数据字段映射属于 Provider。**

## Runtime 法权

- `yuanli-invest`：Research Capability Canon
- Wind AI：Market Reality Runtime
- Codex：Research Engineering Runtime
- `moonstachain/quant-workspace`：Reference Quant Runtime；当前 A9 operational canon
- Evidence Vault：Audit / Replay Evidence Layer
- `yuanli-invest-rsi`：Capability Challenger Lane（仍受 FROZEN 治理）

## 当前状态

机器可读单一状态投影见：[`docs/architecture/CANON-STATUS.json`](docs/architecture/CANON-STATUS.json)。README 只做人类导航，不再作为状态真源。

- R0 Research Capability Canon Reframe：`accepted_merged`
- R1 Capability Object Model & Registry Bootstrap：`accepted_merged`
- R2 PNX-S Gold Capability Pack：`accepted_merged`
- R2.1 Canon Status Reconciliation：`human_accepted_pending_merge`
- R3A Gold Vertical Slice：`not_started`；仅在 R2.1 合并后进入
- Current A9 operational canon：`moonstachain/quant-workspace`
- Evidence / Outcome admission：未授权；Evidence Reviewer 边界保持不变
- Production deployment / live execution：`not_authorized`

R2 已编译第一批 12 个 Gold Research Capabilities 与 99 个 Registry Objects；`Gold = strategically selected + specified`，不等于 `canon`、`benchmark_passed` 或交易法权。

R2.1 已通过 Human Review，决策为 `ACCEPT_R2_1_CANON_STATUS_RECONCILIATION`，并已获得 merge PR #20 的显式授权。合并仍以 post-acceptance exact-head `repository-gates` PASS 为机器前置条件。

下一主线不是扩充第二批 Gold，而是先做 **R3A Gold Vertical Slice**：

1. `P | Technology Cost Curve`
2. `N | Narrative Velocity`
3. `Xa | Conditional Tail Activation`
4. `V | Price-Implied Expectations`（当前 R2 primitive 名称为 `Reverse DCF Expectations`，R3A 检验 Capability 是否应绑定稳定研究问题而非单一算法）

随后进入 Wind AI ↔ Codex ↔ Reference Quant Runtime 的运行闭环与 R4A Benchmark Closure。

## 数据边界

GitHub **不是 Data Warehouse**。原始网页、PDF、研报、Excel、大体量行情与 licensed vendor payload 应保留在合法 Runtime / Evidence 环境；GitHub 保存方法论、对象合同、Registry、reference code、task/skill contract、benchmark protocol、公开来源 locator、必要 hash 与审核回执。

Provider-specific 字段名不得成为 Factor / Algorithm 的本体；应通过 `ProviderAdapter` 映射到 provider-neutral `CanonicalDataField`。

## 研究与交易边界

本仓不直接提供或授权：

- 买卖信号；
- 仓位或推荐权重；
- 目标价；
- 收益承诺；
- broker / live execution；
- 单一 scalar PNX / Force score。

`canon` 只代表研究能力达到当前接纳标准，不代表可交易。

## 旧支线治理

- M1.2 的语义法权已被 R2 Constitution 吸收；旧 PR #16 已关闭为 superseded，其剩余价值重构为 **Runtime State Contract**：资产级 Xs/Xa/Xp/V/IssuerDurability 与组合级 S 的运行态合同。
- Q1 从数据基础设施主阻塞轨收口为 **Wind Provider Qualification**；旧 PR #12 已关闭为 absorbed/superseded。后续只验证 CanonicalDataField ↔ Wind 映射、PIT 语义、授权与运行兼容性，不再阻塞 Capability Canon 建设。

## 法权

见 [GOVERNANCE.md](GOVERNANCE.md)。
