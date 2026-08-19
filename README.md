# 原力投研 · Yuanli Invest

原力投研正在升级为 **Yuanli Investment Research Intelligence Canon｜原力投研智能正典**。

候选 North Star：

> **Compile investment knowledge into reality-tested, machine-callable research intelligence.**

长期复利资产仍是 `ResearchCapability`。股票、行业、技术、宏观状态与投资工具是 research targets；Wind AI、Codex 与 `quant-workspace` 是 Runtime，而不是方法论本体。

## OS vNext：一核 · 三界 · 三门 · 一环

- 一核：Right-Tail Compounding；抓住右尾、让赢家复利、永不出局。
- 三界：P Reality / N Belief / X Asymmetry。
- `X := (Xs, Xa, Xp)` 只表示结构分解，不是求和或数值相乘。
- 三门：E Evidence / V Price / S Survival。
- 一环：Theory → Hypothesis → Capability → Runtime → Replay → Benchmark → Failure → Future Settlement → Capability Revision。

完整语义见 [`docs/os-vnext/`](docs/os-vnext/README.md)。

## Canon 编译链

vNext：`Research Question → Theory → Mechanism → Hypothesis → Observable → Factor / Algorithm → ResearchCapability → Benchmark`

R0/R1 compatibility chain：`Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill`

R2.2 新增 Observable 语义层，但不修改现有 R1/R2 对象历史；Gold successor migration 留到 R2.3，并必须显式 supersede，禁止静默 rename。

## Canonical Research State

候选机器状态：`ResearchStateVector`。

`P → Xs → N → V → Xa → Xp → S`，E 横贯所有节点。

这是 research dependency graph，不是现实世界的单向因果定律。Force classification 仅允许作为 projection。

## Runtime 法权

- `yuanli-invest`：Investment Research Intelligence Canon（R2.2 candidate）
- Wind AI：Market Reality / Evidence & Data Runtime
- Codex：Research Engineering Runtime
- `moonstachain/quant-workspace`：Reference Quant Runtime；仍是当前 A9 operational canon
- Evidence Vault：Audit / Historical Replay Evidence Layer
- `yuanli-invest-rsi`：Capability Challenger Lane；仍受 FROZEN 治理

## R0/R1 兼容法权标记

R2.2 是对既有 R0/R1 法权的上位语义升级，不抹除历史：

- Research Capability Canon
- Compile investment knowledge into machine-callable research intelligence.
- Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill
- Wind AI：Market Reality Runtime
- Codex：Research Engineering Runtime
- Current A9 operational canon：`moonstachain/quant-workspace`
- GitHub **不是 Data Warehouse**。
- Research `canon` 不代表可交易。

## Ledger 与状态

> **Receipt = Ledger; Status = Projection**

Human decision、CI、GitHub merge、Runtime execution、Future Settlement 等事实构成 ledger。`docs/architecture/CANON-STATUS.json` 是确定性 projection，不是事实源。

`python scripts/build_canon_status.py --check`

## 当前阶段

- R0：accepted_merged
- R1：accepted_merged
- R2：accepted_merged
- R2.1：accepted_merged
- R2.2：candidate_ready_for_human_review
- R3A：paused_not_started，等待 R2.2 / R2.3 Gate
- R4A：not_authorized

R2 的 12 个 Gold Capabilities 与 99 个 Registry Objects 保持历史身份；`Gold = specified != canon`。

## 研究与交易边界

本仓不直接提供或授权买卖信号、推荐仓位/权重、目标价、收益承诺、broker/live execution 或 scalar PNX/Force score。`canon` 代表研究能力法权，不代表交易法权。
