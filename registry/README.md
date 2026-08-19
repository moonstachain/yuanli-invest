# Yuanli Research Capability Registries

R1 建立九个空 Registry。它们是对象地址空间与治理边界，不是数据仓库，也不是单次研究结果目录。

```text
theories/      TheoryObject
hypotheses/    HypothesisObject
factors/       FactorObject
algorithms/    AlgorithmObject
benchmarks/    BenchmarkObject
skills/        SkillContract
data-fields/   CanonicalDataField
providers/     ProviderAdapter
capabilities/  ResearchCapability
```

规则：

- 所有 Registry ID 遵循 `docs/architecture/r1/R1-ID-RULES-v0.1.md`；
- 生命周期遵循 `R1-LIFECYCLE-RULES-v0.1.md`；
- R1 bootstrap entry count 全部为 0；
- R0 12 Gold seeds 由 R2 编译，不得在 R1 静默晋升；
- Registry 不承载 target price、buy/sell、recommended weight、position size 或 live execution；
- Provider-specific 字段只进入 `providers/`，不得污染 `data-fields/` 的 canonical semantics。
