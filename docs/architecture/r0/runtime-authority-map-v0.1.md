# Runtime Authority Map v0.1

## 1. Principle

Capability 是 Canon；Runtime 可替换。

任何运行环境不得通过“拥有数据”自动取得研究方法法权，任何 GitHub 文档也不得因为“是 Canon”而伪装拥有实时市场事实。

## 2. Authority table

| Surface | Primary authority | Owns | Does not own |
|---|---|---|---|
| `yuanli-invest` | Research Capability Canon | theory, hypothesis, factor, algorithm, benchmark, skill, canonical field, provenance, version | live market truth, vendor raw data, broker action |
| Wind AI | Market Reality Runtime | licensed market/fundamental/news/research data access and interactive research execution | Yuanli Canon semantics, long-term capability version authority |
| Codex | Research Engineering Runtime | code generation, testing, packaging, refactor, implementation | market-data truth, Canon admission |
| `quant-workspace` | Reference Quant Runtime | deterministic reference implementation, benchmark harness, reproducible examples | unique theory authority, production trading authority |
| Evidence Vault | Audit / Replay Evidence Layer | immutable snapshots, hashes, locators, disputed/history replay evidence | daily runtime requirement for every interactive research task |
| `yuanli-invest-rsi` | Challenger / improvement lane | capability change proposals, benchmark deltas, ratchet candidates | unilateral Canon mutation |

## 3. Wind AI integration rule

Wind AI 调用 Capability 时，最小闭环应为：

```text
Capability ID + version
      ↓
Canonical input fields
      ↓
Wind provider mapping
      ↓
Wind runtime calculation / retrieval
      ↓
Capability output schema
      ↓
result + as_of + provider provenance
```

GitHub 不要求保存 Wind licensed raw payload；只需要在需要复现/审计时保存允许落库的 metadata / mapping / result receipt。

## 4. Codex integration rule

Codex 调用 Capability 时，最小闭环应为：

```text
Capability ID + version
      ↓
Algorithm contract
      ↓
Reference implementation / task spec
      ↓
unit/property/replay tests
      ↓
benchmark result
      ↓
proposed Capability revision
```

Codex 不得因为生成了代码就自动提升 Capability maturity。

## 5. Q1 reinterpretation

Q1 长期应被解释为 `Provider Integration Qualification`：

- 验证 Canonical Field 是否能映射到 Wind；
- 验证 publication/revision/PIT semantics；
- 验证 provider error/fallback 行为；
- 不要求 30/30 vendor ingestion 完成后才能继续 Theory/Factor/Algorithm Canon；
- 30-asset universe 仍可作为 integration fixture / operational MVP fixture。

## 6. A6 reinterpretation

A6 Evidence Vault 继续保留，但调整为 Audit / Replay lane：

- Gold case；
- historical point-in-time reconstruction；
- disputed evidence；
- benchmark dataset receipt；
- provenance / hash / locator。

不要求每次 Wind AI 临时研究都走完整 Evidence admission 流程。

## 7. Non-authority

无任何 Runtime 在 R0 获得：

- live trading；
- target price authority；
- automatic position sizing；
- Evidence admission override；
- Outcome acceptance override；
- Canon merge bypass。
