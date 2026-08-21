# R2.3-B2 | P0 Reference Implementation & Replay Architecture

## Mission

将 ResearchCapability Contract 从 specification 转化为可验证 reference implementation。

目标不是预测市场，而是验证：

`Theory -> Contract -> Algorithm -> PIT Data -> Replay -> Settlement`

是否形成闭环。

## Runtime Layers

### Layer 1 | Canonical Data

- provider-independent economic fields
- point-in-time vintages
- revision lineage
- as-of timestamp

### Layer 2 | Capability Runtime

- CAP-R-01: Regime Causal Decomposition
- CAP-V-01: Price-Implied Expectations
- CAP-XS-01: Structural Asymmetry Source Mapper

### Layer 3 | ResearchState

所有输出必须生成：

- state
- evidence_refs
- uncertainty
- failure_state
- replay_receipt

## Shadow Assets

第一批验证对象：

1. NVIDIA
2. UST30Y
3. Copper
4. Gold
5. USDJPY

## Benchmark Doctrine

必须包含：

- simple baseline
- walk-forward replay
- regime holdout
- ablation
- failure receipts

复杂模型如果没有稳定增量信息，自动降级。

## Authority Boundary

B2 不授权：

- Capability promotion
- Trading action
- Portfolio sizing
- Live execution
