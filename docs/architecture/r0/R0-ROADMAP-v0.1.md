# R0 Follow-on Roadmap v0.1

R0 只冻结战略目标与母架构。Human Accepted 后，后续按独立 PR 推进。

## R1｜Capability Object Model & Registry Bootstrap

目标：建立正式 ID rules、Registry directories、JSON Schema 与 validator。

最小交付：

- Theory / Hypothesis / Factor / Algorithm / Benchmark / Skill schemas
- Canonical Field / Provider Adapter schemas
- ResearchCapability production-candidate schema
- registry index + lifecycle rules
- no silent promotion; maturity state machine

## R2｜PNX-S Gold Capability Pack

目标：不是先覆盖500个能力，而是做 12 个高价值 Gold Capability。

候选：

1. P｜Technology Cost Curve
2. P｜Adoption Acceleration
3. N｜Narrative Velocity
4. N｜Narrative Saturation
5. Xs｜Market Share Acceleration
6. Xs｜Bottleneck Scarcity
7. Xa｜Conditional Tail Activation
8. Xa｜Extreme Regime Shift
9. Xp｜Payoff Convexity Geometry
10. V｜Reverse DCF Expectations
11. S｜Expected Shortfall / Ruin Constraint
12. S｜Robust Fractional Kelly

每个必须完成 Theory → Hypothesis → Factor/Algorithm → Benchmark → Skill。

## R3｜Wind AI + Codex Skill Interface

目标：让同一个 Capability 能被两个 Runtime 调用。

每个 Gold Capability 至少交付：

- `wind-ai-task-spec.md`
- `codex-task-spec.md`
- input/output schema
- provider mapping requirements
- deterministic failure behavior
- result receipt format

## R4｜Reference Quant Runtime & Benchmark Harness

目标：在 `quant-workspace` 或等价 reference runtime 中形成最小可复现 implementation。

要求：

- simpler baseline
- point-in-time
- walk-forward / OOS
- calibration where applicable
- multiple-testing control where applicable
- benchmark receipt

## R5｜Capability Ratchet

目标：将 `yuanli-invest-rsi` 从笼统方法优化器升级为 Capability challenger。

比较对象：

```text
Capability champion
vs
Capability challenger
```

只有 benchmark / held-out / future settlement 显示可解释增量时，才允许提出 Canon Delta。

## R0 non-blocking rule

Q1 Wind provider qualification、A6 Evidence Vault、M1.2 Contract Split 可以并行存在，但不得阻塞 R1/R2 的 Theory/Capability Canon 建设；反之 R0 也不自动改变这些既有 PR 的治理状态。
