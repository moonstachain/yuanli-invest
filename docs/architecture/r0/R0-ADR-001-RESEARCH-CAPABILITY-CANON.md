---
title: ADR-001 Research Capability Canon
status: candidate
version: 0.1.0
---

# R0 ADR-001｜Research Capability Canon

## Context

`yuanli-invest` 已形成 PNX-S 理论、point-in-time、Evidence、Schema、Replay/Eval 与 Human Gate 基础，但若继续把“数据获取、数据仓、实时量化运行”作为 GitHub 的中心使命，会与 Wind AI 等专业市场运行环境重复建设，并制造 vendor lock-in。

## Decision

候选决策：

> **`yuanli-invest` 的长期中心资产是 ResearchCapability，而不是 MarketData 或 Stock object。**

ResearchCapability 将高质量理论和论文编译为：

```text
Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill
```

并通过 provider-neutral Canonical Data Field 由 Wind AI、Codex、quant-workspace 或未来 runtime 执行。

## Authority map

- GitHub：Research Capability Canon / version / provenance / contract / benchmark
- Wind AI：Market Reality Runtime
- Codex：Research Engineering Runtime
- quant-workspace：Reference Quant Runtime
- Evidence Vault：Audit / Replay Evidence Layer

## Consequences

### Positive

- 降低 vendor dependency；
- 理论、因子、算法和评测可跨模型/数据商复用；
- GitHub 资产能够持续复利；
- Wind AI 与 Codex 可以通过 Task/Skill Contract 直接调用；
- 研究能力可以被 benchmark、ablation 与版本治理。

### Trade-offs

- 必须维护 Canonical Field 与 Provider Adapter；
- 因子/算法不能只写公式，需补足理论、边界、评测和测试；
- Capability Registry 会增加初期治理成本；
- GitHub 不再追求成为完整数据执行平台。

## Rejected alternative

`GitHub-centric full-stack market data + research + execution platform`：拒绝作为长期中心架构。原因不是技术不可行，而是它把可替换的数据/运行环境放在了不可替换知识资产之前。

## Non-decisions

本 ADR 不关闭 Q1/A6/M1.2，不切换 operational canon，不注册 production contract，不授权交易。

## Acceptance token

`ACCEPT_R0_RESEARCH_CAPABILITY_CANON_REFRAME`
