# Yuanli Research Capability Registries

R1 建立九个 Registry 地址空间；R2 首次把 12 个 PNX-S Gold seeds 编译成机器可验证的 `specified` Capability。Registry 是研究能力正典候选层，不是市场数据仓库，也不是交易结果目录。

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

R2 采用 **pack file**：每个 Registry 可包含一个版本化 JSON pack，其 `objects[]` 中每一项仍按 R1 单对象 JSON Schema 独立验证。对象身份由不可变 ID 决定，不由文件名决定。

规则：

- 所有 ID 遵循 `docs/architecture/r1/R1-ID-RULES-v0.1.md`；
- 生命周期遵循 `R1-LIFECYCLE-RULES-v0.1.md`；
- R2 的 12 个 Gold Capability 全部停在 `specified`，**Gold != canon**；
- hypotheses 为 `preregistered`，benchmark 只冻结协议，不代表已经通过；
- Provider Registry 在 R2 仍为空，Wind/provider 映射留给 Q1/R3；
- `r0_gold_seed_pack_promoted=false` 表示没有被静默晋升为 `canon`；R2 只执行 `compiled_to_specified=true`；
- Registry 不承载 target price、buy/sell、recommended weight、position size、broker action 或 live execution；
- Provider-specific 字段只进入 `providers/`，不得污染 `data-fields/` 的 canonical semantics；
- P/N/X 不得压缩成标量总分；`X := (Xs, Xa, Xp)` 为结构分解，不做算术加总。
