# 原力投研 · Yuanli Invest

原力投研是 **Yuanli Investment Research Intelligence Canon｜原力投研智能正典**。

North Star：

> **Compile investment knowledge into reality-tested, machine-callable research intelligence.**

长期复利资产是 `ResearchCapability`。股票、行业、技术、宏观状态与投资工具是 research targets；Wind AI、Codex 与 `quant-workspace` 是 Runtime，而不是方法论本体。

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

## Canonical Research State

机器状态：`ResearchStateVector`。

`P → Xs → N → V → Xa → Xp → S`，E 横贯所有节点。这是 research dependency graph，不是现实世界的单向因果定律。Force classification 仅允许作为 projection。

## Runtime 法权

- `yuanli-invest`：Investment Research Intelligence Canon
- Wind AI：Market Reality / Evidence & Data Runtime
- Codex：Research Engineering Runtime
- `moonstachain/quant-workspace`：Reference Quant Runtime；仍是当前 A9 operational canon
- Evidence Vault：Audit / Historical Replay Evidence Layer
- `yuanli-invest-rsi`：Capability Challenger Lane；仍受 FROZEN 治理

## R0/R1 兼容法权标记

R2.2 / R2.3 / R2.3-A / R2.3-B0 是上位语义演进，不抹除历史 Human-Accepted 法权：

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
- R2.2：accepted_merged；merge commit `3bccf723c301f77364c198b9a7b1282c340f5534`
- R2.3：accepted_merged；merge commit `418f06200cde16173743454d506ee946bbc572fc`
- R2.3-A：accepted_merged；merge commit `ef3f470f7ef0ceb2b58f392d4a2bd5a5c4c691bd`
- R2.3-B0：accepted_merged；PR #24 squash merge commit `cb5ffd0f2e8e377d82c12d716e995c7b5b328e01`
- R3A：paused_not_started；Capability implementation/runtime remains separately governed
- R4A：not_authorized

R2.3-B0 已冻结 Universal ResearchCapability Contract 的 11 个必备区块，以及 `CAP-R-01 / CAP-V-01 / CAP-XS-01` 的 P0 contract profiles。它没有授权 Capability implementation、promotion、benchmark execution、Wind/Codex production runtime、Evidence/Outcome admission、A9 switch、RSI promotion 或交易执行。

当前下一研究战役：

> **QXM1｜Financial Mechanics Capability Candidate Pack**
>
> 将经典金融机械层——基本面 Driver Tree、三表完整性与现金转换、信用与资产负债表传导、机会成本/折现率桥、压力退出流动性、收益来源归因——第一次编译进 11-block ResearchCapability Contract，保持 candidate/specification 身份，不静默晋升 Canon。

## 研究与交易边界

本仓不直接提供或授权买卖信号、推荐仓位/权重、目标价、收益承诺、broker/live execution 或 scalar PNX/Force score。`canon` 代表研究能力法权，不代表交易法权。
