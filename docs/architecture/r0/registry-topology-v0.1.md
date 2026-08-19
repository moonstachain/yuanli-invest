# Registry Topology v0.1

## Purpose

将研究知识拆成可独立版本、可引用、可组合的 Registry，而不是把全部内容塞进一篇方法论文档或一个 notebook。

## Core registries

### 1. Theory Registry

路径候选：`registry/theories/`

职责：保存理论出处、机制、证据级别、适用边界、PNX-S 映射。

### 2. Hypothesis Registry

路径候选：`registry/hypotheses/`

职责：把理论转换成 preregisterable、point-in-time、可证伪命题。

### 3. Factor Registry

路径候选：`registry/factors/`

职责：保存因子经济含义、公式/算法、输入字段、时点规则、预期方向、失败 regime、实现与 benchmark。

### 4. Algorithm Registry

路径候选：`registry/algorithms/`

职责：保存计算/统计模型的假设、baseline、实现、测试与不适用条件。

### 5. Benchmark Registry

路径候选：`registry/benchmarks/`

职责：保存评测协议，而不是保存单次回测结论；包括 point-in-time、OOS、ablation、calibration、multiple testing 和复杂度惩罚。

### 6. Skill / Task Registry

路径候选：`registry/skills/`

职责：把 Capability 暴露给 Wind AI、Codex、Reference Quant Runtime 和其他 Agent。

## Horizontal registries

### Canonical Field Registry

路径候选：`registry/data-fields/`

定义 provider-neutral 的经济字段语义、时点/修订语义与单位。

### Provider Adapter Registry

路径候选：`registry/providers/`

保存 Canonical Field 与 Wind/Exchange/Filing/其他 licensed provider 之间的映射合同。

## Capability index

路径候选：`registry/capabilities/`

每个 Capability 只引用 Registry ID，不复制理论、因子和算法正文。

示例：

```yaml
capability_id: CAP-N-003-NARRATIVE-VELOCITY
domain: N
theory_ids:
  - THEORY-SHILLER-2017-NARRATIVE-ECONOMICS
hypothesis_ids:
  - HYP-N-003-MARGINAL-NARRATIVE-ACCELERATION
factor_ids:
  - FACTOR-N-ATTENTION-VELOCITY
  - FACTOR-N-SOURCE-BREADTH
algorithm_ids:
  - ALG-N-HAWKES-INTENSITY
benchmark_ids:
  - BENCH-N-TURNING-POINT-V1
skill_ids:
  - SKILL-WIND-NARRATIVE-VELOCITY-V1
  - SKILL-CODEX-NARRATIVE-VELOCITY-V1
```

## Governance

R0 只冻结 Registry topology；R1 才允许建立正式 bootstrap registry 和 ID rules。

Registry entry 的状态不等于投资结论，也不得直接承载 target price、buy/sell、recommended weight 或 position size。
