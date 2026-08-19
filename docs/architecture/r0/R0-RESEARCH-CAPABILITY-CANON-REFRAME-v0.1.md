---
title: Yuanli Research Capability Canon Reframe
version: 0.1.0
status: candidate_architecture
portfolio: A9
production_effect: none
---

# R0｜Yuanli Research Capability Canon Reframe v0.1

## 0. Decision in one sentence

`yuanli-invest` 的第一使命，不再定义为“在 GitHub 内复制一个完整行情/量化运行平台”，而定义为：

> **把高质量投资理论、论文与经验研究编译成 provider-independent、machine-callable、testable、versioned Research Capabilities，供 Wind AI、Codex 与未来研究 Agent 组合调用。**

英文 North Star：

> **Compile investment knowledge into machine-callable research intelligence.**

R0 是战略重构候选，不改变当前 operational canon，不修改 Q1/M1.2 的既有治理事实，不授权生产数据接入或交易执行。

---

## 1. 第一性原理

长期复利价值最高的不是某个 vendor 的原始数据副本，而是：

```text
Theory
  ↓
Mechanism
  ↓
Hypothesis
  ↓
Observable
  ↓
Factor
  ↓
Algorithm
  ↓
Evaluation
  ↓
Machine Capability
```

原因：

1. 原始行情/财务/新闻数据具有强时效、授权与 vendor 依赖；
2. Wind AI 等专业环境已经承担 Market Reality Runtime；
3. Codex 等工程环境能够承担代码实现、测试和重构；
4. 真正值得长期拥有的是“为什么这样研究、怎么算、何时有效、何时失效、如何验证”的知识与计算协议；
5. 这些协议必须能够脱离单一模型、单一数据商和单一运行环境持续复用。

因此冻结：

```text
GitHub != Data Warehouse
GitHub != Backtest Notebook
GitHub = Research Capability Canon
```

---

## 2. 三类核心运行角色

### 2.1 GitHub｜Research Capability Canon

回答：

> 该研究能力为什么存在、怎么算、需要什么输入、输出什么、如何验证、什么情况下失败？

主要沉淀：

- Theory / Paper lineage
- Mechanism
- Hypothesis
- Factor
- Algorithm
- Benchmark / Eval
- Canonical Data Field
- Provider Adapter Contract
- Skill / Task Spec
- Reference Implementation
- Test / Validator
- Provenance / version / failure regime

### 2.2 Wind AI｜Market Reality Runtime

回答：

> 真实市场当前或历史时点发生了什么？

负责专业数据、研报、行情、财务、行业、宏观、新闻与实际研究运行。R0 不要求 GitHub 复制 Wind 的数据仓。

### 2.3 Codex｜Research Engineering Runtime

回答：

> 如何把研究设计变成可靠、可测试、可维护的代码？

负责 Python/SQL、feature pipeline、model、backtest、package、tests、benchmark 与 refactor。

---

## 3. ResearchCapability 成为中心对象

R0 将长期中心对象从“Stock/Asset”提升为 `ResearchCapability`。

资产是 runtime target；能力才是可复用资产。

示例：

```text
CAP-P-001   Technology Cost Curve
CAP-N-003   Narrative Velocity
CAP-XS-002  Winner-Take-Most Structure
CAP-XA-004  Conditional Tail Activation
CAP-V-003   Reverse DCF Expectations
CAP-S-006   Robust Fractional Kelly
```

每个 Capability 必须能够映射到 PNX-S/E/V 之一或多个研究域，并明确：理论来源、机制、假说、输入字段、算法、评测、失败条件与运行合同。

---

## 4. PNX-S 的新地位

PNX-S 不再只是一套“选股模型”，而成为 Research Capability Ontology：

- `P`｜Reality / Direction
- `N`｜Belief / Timing
- `Xs`｜Structural Right Tail
- `Xa`｜Tail Activation
- `Xp`｜Payoff Convexity
- `V`｜Price / Strike
- `S`｜Portfolio Survival & Growth
- `E`｜Evidence / Epistemic Discipline

任何 Factor / Algorithm / Skill 都必须声明其 ontology mapping；但禁止因此生成单一 `PNX score`。

---

## 5. Canon 的主要资产链

### Layer 1｜Research Canon

```text
Theory → Paper → Mechanism → Hypothesis → Epistemic Boundary
```

### Layer 2｜Research Capability

```text
Factor → Algorithm → Model → Benchmark → Reference Code
```

### Layer 3｜Research Interface

```text
Canonical Field → Provider Adapter → Schema → Task Spec → Skill / MCP
```

最终链路：

```text
Knowledge
   ↓ compile
Computation
   ↓ expose
Agent-callable Capability
   ↓ run
Wind AI / Codex / other runtime
   ↓
Empirical result / failure
   ↓
Capability revision
```

---

## 6. Provider independence

算法与能力不得直接绑定 Wind 私有字段名作为核心语义。

统一通过 `CanonicalDataField`：

```text
canonical.revenue.ttm
canonical.capex.ttm
canonical.market_cap
canonical.news.count
canonical.search.attention
canonical.options.iv
```

再由 Provider Adapter 映射：

```text
Canonical Field
     ↓
Provider Adapter
 ├─ Wind
 ├─ Exchange / SEC / HKEX
 ├─ Company Filing
 └─ other licensed provider
```

原则：

> **算法属于原力，数据属于 Provider。**

---

## 7. 六类核心 Registry

R0 候选母库：

1. `Theory Registry`：理论/论文 → 机制
2. `Hypothesis Registry`：机制 → 可证伪命题
3. `Factor Registry`：观测变量 → 可计算因子
4. `Algorithm Registry`：因子/状态 → 计算与推断方法
5. `Benchmark Registry`：如何判断能力是否有价值
6. `Skill / Task Registry`：Wind AI / Codex / Agent 如何调用

另设横向基础注册表：

- `Canonical Field Registry`
- `Provider Adapter Registry`

---

## 8. Factor 的最低机构级合同

每个 Factor 至少包含：

```text
factor_id
theory_basis
economic_mechanism
formula_or_algorithm
required_inputs
point_in_time_requirements
frequency
eligible_universe
expected_direction
investment_horizon
neutralization
known_failure_regimes
academic_evidence
internal_replication_state
reference_implementation
evaluation_protocol
```

不得只提交一个公式或一个“因子分数”。

---

## 9. Algorithm 的最低合同

每个 Algorithm 至少说明：

- 解决什么研究问题；
- 数学/统计假设；
- 输入输出；
- 与哪条理论/假说关联；
- 何时不应使用；
- 原始或权威来源；
- Reference Implementation；
- Unit / property / replay test；
- benchmark 与 simpler baseline；
- 计算复杂度与 reproducibility。

候选算法族包括但不限于：

- Bayesian state-space / HMM / change-point
- embeddings / topic model / Hawkes / diffusion
- EVT / POT-GPD / quantile / rare-event classification
- DAG / SCM / Double ML / causal forest / synthetic control
- reverse DCF / scenario valuation
- Kelly / robust optimization / ES / drawdown constraints

“列入候选族”不等于算法有效；必须逐项进入 Capability 与 Benchmark 评测。

---

## 10. Benchmark-first

GitHub 不需要保存巨量市场数据，但必须保存“如何判断算法有没有价值”。

示例：

- P：state calibration / forward relevance / regime stability
- N：Brier / log loss / turning-point lead time / false alarm
- Xs：Top-tail precision / recall / WTCR
- Xa：PR-AUC / calibration / lead time / false alarm
- V：expectation-gap calibration / realized scenario error
- S：ruin / ES / MaxDD / geometric growth / tail-capture retention

任何复杂算法必须与 simpler baseline 做 ablation；复杂度本身不是价值。

---

## 11. 对现有路线的重新解释

### Q1

从“GitHub 数据基础设施关键路径”降级为：

> **Provider Integration Qualification**

Wind API/entitlement 是否在 GitHub CI 直接可用，不应阻塞 Theory/Factor/Algorithm/Capability Canon 的持续建设。

### A6 Evidence Vault

从日常研究必经主链调整为：

> **Audit / Replay Evidence Layer**

主要服务 Gold case、争议结果、point-in-time replay、benchmark 与 reproducibility。

### quant-workspace

长期目标调整为：

> **Reference Quant Runtime**

它是 Capability 的官方参考执行环境之一，不是 Capability 本体。

### M1.2 / M1.3

继续有效。M1.2 完成 PNX-S 机器语义拆分；M1.3 应进一步证明 Capability/Eval Contract，而不只证明一个选股总模型。

---

## 12. 治理边界

R0 不自动：

- 修改现有 README 的正式 Mission；
- 合并或关闭 Q1 / A6 / M1.2；
- 迁移 production schemas；
- 注册 candidate capability 到生产 Registry；
- 授权 Evidence/Outcome admission；
- 切换 A9 operational canon；
- 修改 RSI FROZEN；
- 授权 target price、position size、buy/sell 或 live trading。

只有 Human Accepted 后，才允许进入 R1：`Capability Object Model & Registry Bootstrap`。

---

## 13. R0 Exit Gate

Human Review 必须明确裁决：

1. 是否接受 `GitHub = Research Capability Canon`；
2. 是否接受 `ResearchCapability` 而非 Asset 成为长期中心对象；
3. 是否接受 Wind AI = Market Reality Runtime、Codex = Research Engineering Runtime；
4. 是否接受 provider-neutral Canonical Data Field；
5. 是否接受 Theory → Hypothesis → Factor → Algorithm → Benchmark → Skill 作为主价值链；
6. 是否接受 Q1 数据 vendor qualification 不再阻塞 Capability Canon 建设；
7. 是否接受 PNX-S 作为 Capability Ontology，而非单一综合分数模型。

建议 Human Gate：

`ACCEPT_R0_RESEARCH_CAPABILITY_CANON_REFRAME`
