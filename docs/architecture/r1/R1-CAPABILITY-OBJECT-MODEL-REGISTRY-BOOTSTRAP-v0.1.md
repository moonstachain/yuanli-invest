# R1｜Capability Object Model & Registry Bootstrap v0.1

Status: `candidate_started`

Base: `main@cbe943f7251e44703e8a2e4c8a68fce2be1d2ea7`

## 1. Purpose

R0 已冻结：`yuanli-invest = Research Capability Canon`。R1 将该战略定义编译为可被 GitHub、Wind AI、Codex 与 reference runtime 稳定引用的对象合同与 Registry 骨架。

R1 不追求填满内容库；它只建立**长期不会轻易漂移的 ID、对象、生命周期和目录法权**。

## 2. Canonical compilation chain

```text
TheoryObject
  ↓
Mechanism
  ↓
HypothesisObject
  ↓
FactorObject / AlgorithmObject
  ↓
ResearchCapability
  ├─ BenchmarkObject
  └─ SkillContract
       ↓
Runtime Result / Receipt
```

横向：

```text
CanonicalDataField ↔ ProviderAdapter
EvidenceReference / ReferenceImplementation
```

## 3. R1 production-candidate object contracts

R1 在 `packages/contracts/schemas/` 新增：

- `theory-object.schema.json`
- `hypothesis-object.schema.json`
- `factor-object.schema.json`
- `algorithm-object.schema.json`
- `benchmark-object.schema.json`
- `skill-contract.schema.json`
- `canonical-data-field.schema.json`
- `provider-adapter.schema.json`
- `research-capability.schema.json`

这些对象是 **production-candidate contracts**，不是 A9 operational-canon switch，也不代表任何 Capability 已进入 `canon` maturity。

## 4. Registry topology

```text
registry/
├── theories/
├── hypotheses/
├── factors/
├── algorithms/
├── benchmarks/
├── skills/
├── data-fields/
├── providers/
└── capabilities/
```

R1 只建立 bootstrap index；所有 registry entry count 初始为 0。R0 的 12 个 Gold seed 继续只是 R2 输入，不在 R1 中静默晋升。

## 5. Provider independence

核心规则：**算法属于原力，数据映射属于 Provider Adapter。**

任何 Factor / Algorithm / Capability 的输入必须优先引用 `CanonicalDataField`。Wind、交易所、Filing 或其他 licensed provider 的字段名只能存在于 `ProviderAdapter` 中，不得成为算法本体。

## 6. Maturity & promotion

Capability maturity：

```text
concept → specified → implemented → replicated → benchmark_passed → shadow_qualified → canon → deprecated
```

禁止 silent promotion。任何跨 maturity 的晋升必须有可追溯 receipt；进入 `canon` 必须经过独立 Human Gate。`canon` 只表示研究能力接纳，不表示可交易、可给目标价或可自动执行。

## 7. Epistemic boundary

- practitioner claim 不得登记为 established theory；
- hypothesis 必须有 null / falsification rule；
- factor 必须有 point-in-time、publication lag、missingness 与 failure regime；
- algorithm 必须声明 assumptions、simpler baselines 与 failure modes；
- benchmark 必须显式处理 OOS / PIT / lookahead / multiple testing / calibration（适用时）；
- SkillContract 必须 fail closed，并声明 prohibited outputs；
- feature importance、Granger lead、相关性不得自动晋升为 causal effect。

## 8. Hard prohibitions

Registry 与对象合同不得直接承载：

- target price
- buy/sell signal
- recommended weight
- target weight
- position size
- broker/live execution
- scalar PNX/Force score

## 9. Relationship to other lanes

- Q1：继续存在；长期解释为 Provider Integration Qualification。
- A6：继续存在；长期解释为 Audit / Replay Evidence Lane。
- M1.2：继续独立，不被 R1 自动改写。
- `quant-workspace`：仍是当前 A9 operational canon / Reference Quant Runtime。
- `yuanli-invest-rsi`：仍 FROZEN，R1 不授权 challenger promotion。

## 10. R1 exit gate

R1 只有在以下条件同时成立后才可 Human Review：

1. 9 个 production-candidate schemas 均通过 JSON Schema 校验；
2. ID rules 与 lifecycle rules 冻结；
3. 9 个 registry bootstrap index 存在且 entry count = 0；
4. README 已对齐 R0 Human Accepted mission，但不宣称 A9 canon 已切换；
5. validator fail-closed；
6. repository-gates 全绿。

Human Accepted 后，只授权 `R2｜PNX-S Gold Capability Pack`，不自动晋升任何 capability 到 `canon`。