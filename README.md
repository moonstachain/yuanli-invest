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

- R0 Research Capability Canon Reframe：`human_accepted_merged`
- R1 Capability Object Model & Registry Bootstrap：`candidate_started`
- Current A9 operational canon：`moonstachain/quant-workspace`
- Evidence / Outcome admission：未授权；Evidence Reviewer 边界保持不变
- Production deployment / live execution：`not_authorized`

R1 正在建立 Theory / Hypothesis / Factor / Algorithm / Benchmark / Skill / Canonical Field / Provider Adapter / Capability 九个 Registry 的对象合同、ID 规则与生命周期。R0 的 12 个 Gold Capability seeds 不会在 R1 中静默晋升；它们留给 R2 独立编译与验证。

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

## 法权

见 [GOVERNANCE.md](GOVERNANCE.md)。
