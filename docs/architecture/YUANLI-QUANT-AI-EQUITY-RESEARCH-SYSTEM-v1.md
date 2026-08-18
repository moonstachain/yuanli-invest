---
title: Yuanli Quant AI Equity Research System | Architecture & Implementation Spec
version: 1.0.0-q0-candidate
status: architecture_freeze_candidate
portfolio: A9
owner: RAY
base_commit: f37f1127d49981d6ece81b6000d494d87a1214f1
human_gate: required_before_implementation
---

# Yuanli Quant AI Equity Research System v1.0

## 0. Q0 Decision

本文件冻结“原力量化投研｜AI 标的物（中美为主）”的工程母架构候选。系统目的不是生产买卖指令，而是持续发现、验证、跟踪 **范式级右尾资产候选**。

核心研究链：

`World / Industry -> Evidence -> Quant Features -> P/N/X State -> Fundamental Gate -> Survival Gate -> Force Classification -> Research Priority -> Replay / Eval -> Human Review`

黄金三角继续沿用已冻结方法论：

- `P = Paradigm Potential / 范式势能`：世界往哪里迁移？
- `N = Narrative Momentum / 叙事动能`：钱与社会认知什么时候开始相信、拥挤、衰减？
- `X = Extreme Convexity / 极值凸性`：判断正确时能捕获多少右尾；判断错误时能否活下来？

**禁止把 P/N/X 变成任意 0-100 黑箱总分再相乘。** 量化层提供 evidence/features/state-transition，不制造伪精确。

## 1. Authority / Repository Boundary

Q0 不改变现有 A9 法权：

- `moonstachain/yuanli-invest`：未来 A9 业务 Canon / Evidence / Snapshot / Replay / Decision contract；当前仍未被授权切换为 operational canon。
- `moonstachain/quant-workspace`：当前 A9 operational canon；负责 DuckDB、行情/财务特征、确定性因子、回测与 paper portfolio 计算。
- `moonstachain/yuanli-invest-rsi`：隔离 Challenger / self-evolution sandbox；只产研究判断与 paper portfolio，不接实盘，不修改 FROZEN，除非另过 Human Gate。
- `moonstachain/yiru-macro-cockpit`：宏观 regime / liquidity / cross-asset sensor，只向 A9 提供 versioned snapshot，不夺取 A9 研究法权。
- Local/NAS Evidence Vault：原始网页、PDF、公告、Wind 导出、Parquet、DuckDB raw snapshot 的物理真源。
- Wind / Wind Alice：专业数据与检索来源；Alice 是 Machine Evidence Analyst，不是最终 Evidence Reviewer。
- OpenAI Agents SDK：研究编排运行时，不是 Canon Authority。

因此目标拓扑为：

```text
Wind / SEC / IR / News / Macro / Market
                 |
                 v
        Local/NAS Evidence Vault
                 |
        SourceRecord / Evidence
                 |
       +---------+----------+
       |                    |
quant-workspace        yuanli-invest
Features/Backtest      Canon/Snapshot/Replay
       |                    |
       +---------+----------+
                 |
          Force Agent Runtime
                 |
       P / N / X Candidate State
                 |
       Fundamental / Survival Gate
                 |
          Force Classification
                 |
          Human Review / PR
                 |
       Outcome / Replay / Evals
                 |
         yuanli-invest-rsi
        Challenger proposals only
```

## 2. Six Non-Negotiable Architecture Principles

1. **Point-in-time first**：任何训练、回放、判断都必须记录 `as_of`、`published_at`、`captured_at`、`lookahead_check`。
2. **Evidence before opinion**：Agent 不能直接写 Force 结论；必须先生成可定位 claim/evidence/counterevidence。
3. **State, not magic score**：P/N/X 使用结构化 state + confidence + reasons + falsifiers；允许 `unknown`。
4. **Deterministic quant, probabilistic reasoning**：可计算内容由 Python/DuckDB 完成；LLM 负责语义归因、证据组织、冲突识别与假设生成。
5. **Normal path machine, exception path human**：读取、计算、候选研究可自动；Evidence admission、Canon promotion、Outcome acceptance、RSI ratchet、任何 external action 保留 Human Gate。
6. **No live execution**：Q0-Q7 只允许 research / paper portfolio / shadow benchmark；不产生交易指令、仓位、目标价或个性化投资建议。

## 3. System Planes

### 3.1 Data Plane

数据分五类：

- `market`: OHLCV、corporate actions、liquidity、volatility、cross-asset；
- `fundamental`: 财报、估值、分析师一致预期、CAPEX、现金流、资产负债表；
- `industry`: shipment、capacity、price/cost curve、utilization、lead time、supply-chain bottleneck；
- `narrative`: 新闻、公告、开发者/企业 adoption、政策、搜索/媒体/资本市场传播；
- `macro`: liquidity、rates、USD、credit、regime、risk appetite。

Raw 数据留在本地/NAS；GitHub 只存 schema、manifest、snapshot metadata、hash、locator、accepted research object。

### 3.2 Feature Plane

`quant-workspace` 提供确定性特征：

- price/volume/liquidity；
- revisions / growth / margin / FCF；
- balance-sheet / refinancing / dilution；
- CAPEX / inventory / receivables；
- volatility / drawdown / EVT / VaR / ES；
- industry growth / price / capacity / utilization；
- narrative counts / source diversity / cross-cohort diffusion；
- macro regime joins。

所有 feature 必须具备：`feature_id, subject_id, as_of, source_snapshot_ids, formula_version, value, unit, quality_state`。

### 3.3 Evidence Plane

Evidence object 永远区分：

`Source -> Claim -> Locator -> Support/Counterevidence -> Eligibility -> Reviewer state`

Machine retrieval/capture 不等于 Evidence admission。

### 3.4 Reasoning Plane

采用 OpenAI Agents SDK 的 **Manager + Specialists-as-tools** 模式作为默认编排，而不是让六个 Agent 自由聊天。顶层 `Force CIO Agent` 负责拆解、调用 specialist、冲突合并和最终 candidate package；specialists 不相互改写结论。

默认 specialists：

1. `ParadigmAgent`
2. `NarrativeAgent`
3. `ConvexityAgent`
4. `FundamentalAgent`
5. `RedTeamAgent`
6. `EvidenceJudgeAgent`

所有 agent output 使用 strict structured output；模型名不得写死在 Canon，统一由 runtime profile 配置：`reasoning_model`, `fast_model`, `batch_model`。

### 3.5 Decision Plane

最终对象不是“研究报告”，而是 versioned `ForceRadarSnapshot`：

```text
Asset + AsOf
  -> ParadigmSnapshot
  -> StageSnapshot
  -> ConvexityProfile
  -> FundamentalGate
  -> SurvivalGate
  -> Evidence + CounterEvidence
  -> ForceTriangleSnapshot
  -> ResearchPriority
```

### 3.6 Learning Plane

学习链：

`Snapshot -> Frozen Forecast/Claim -> Future Outcome -> Replay -> Eval -> LearningCandidate -> Held-out Challenge -> Human Gate -> Canon delta`

Outcome 永不自动改 Canon。

## 4. P Engine | Paradigm Potential

P 只从六个结构面构建：

1. `technology_breakthrough`
2. `cost_curve`
3. `infrastructure`
4. `capital_formation`
5. `institutional_adaptation`
6. `productivity_diffusion`

每个结构面输出：`strong | mixed | weak | unknown` + evidence ids + counterevidence ids + falsifiers。

Paradigm stage 继续使用现有契约：

`emergence | installation | frenzy | turning_point | deployment | maturity | unknown`

禁止使用康波“年份预测”做确定性信号；Perez 仅作为解释框架。

## 5. N Engine | Narrative Momentum

N 不是 sentiment score。系统维护 `NarrativeNode` 和 `NarrativeEdge`：

- narrative examples: AI agents, inference, custom ASIC, HBM, AI networking, sovereign AI, AI power, physical AI, robotaxi, humanoid, China substitution；
- cohorts: researchers, developers, founders, enterprises, investors, media, government, consumers；
- event types: discover, adopt, invest, deploy, regulate, reject, reverse-narrative。

关键状态：

`discover | accelerate | consensus | decay | residual | unknown`

量化辅助指标：

- source-diversity；
- cohort-diversity；
- cross-cohort transition count；
- narrative velocity `ΔN`；
- narrative acceleration `Δ²N`；
- crowding proxy；
- reverse-narrative ratio；
- post-T0 leakage flag。

这些指标只辅助状态判定，不直接映射为 Force 总分。

## 6. X Engine | Extreme Convexity

### 6.1 Right-tail capture

沿用现有 ConvexityProfile ontology：

- `winner_take_most`
- `network_effects`
- `scale_economics`
- `bottleneck_control`
- `platform_optionality`
- `market_expansion`
- `value_capture`

### 6.2 Left-tail survival

- `balance_sheet_fragility`
- `refinancing_dependency`
- `dilution_risk`
- `concentration_risk`
- `regulatory_ruin`
- `technical_obsolescence`
- `valuation_cashflow_mismatch`

传统 EVT/VaR/ES 只属于 left-tail 的一个子集，不能替代 X。

## 7. Fundamental Gate / Survival Gate

Fundamental Gate 检查“叙事是否被现实兑现”：revenue, unit economics, gross margin, FCF, customer adoption, order/bookings, estimate revisions。

Survival Gate 回答：“如果判断错两三年，还能否活下来？”：cash, debt, maturity wall, financing dependency, dilution, inventory, regulation, concentration, replacement risk。

继续使用：`passed | partial | failed | unknown`。

## 8. Force Classification

沿用已冻结六分类：

- `golden_extreme`
- `latent_dragon`
- `paradigm_bubble`
- `meme_extreme`
- `ordinary_asset`
- `unknown`

Research Priority：`high | medium | low | unknown`。

分类器只消费 accepted/eligible evidence 和 deterministic features；若关键链不闭合，必须允许 `unknown`。

## 9. AI Value Chain Ontology

第一版统一中美标的的产业链语义，而不是按国家拆成两个孤立股票池：

```text
AI
├── Compute
│   ├── GPU
│   ├── Custom ASIC
│   └── CPU/Edge
├── Memory
│   ├── HBM
│   └── DRAM
├── Semiconductor
│   ├── Foundry
│   ├── Equipment
│   ├── EDA
│   └── Advanced Packaging
├── Datacenter
│   ├── Optical
│   ├── Networking
│   ├── Power
│   ├── Cooling
│   └── Storage
├── Cloud
├── Foundation Models
├── AI Software / Agent
├── Consumer AI
├── Autonomous Driving
├── Robotics / Physical AI
└── Sovereign / China substitution
```

每个资产必须映射到：`value_chain_nodes[]`, `narrative_nodes[]`, `bottlenecks[]`, `revenue_exposures[]`, `risks[]`。

## 10. OpenAI Runtime Contract

OpenAI runtime 采用：

- Responses API as model/tool substrate；
- Agents SDK as multi-step orchestration runtime；
- function tools / MCP for data access；
- strict structured outputs for machine contracts；
- tracing for run observability；
- Human-in-the-loop approvals for sensitive tools；
- Evals for replay/regression tests。

Tool policy：

- read-only market/evidence/feature retrieval: auto-allowed；
- local snapshot capture: allowed only inside designated vault worker；
- GitHub proposal writes: require explicit architecture/research workflow permission；
- Evidence admission / Canon promotion / Outcome acceptance / RSI FROZEN change: always Human Gate；
- live trading / broker execution: unavailable by design。

## 11. Product Surfaces

MVP 只做三张前台：

1. **Force Radar**：30 个 seed assets 的 P/N/X 状态和变化；
2. **Asset Research Page**：证据链、反证、P/N/X、Gate、falsifier、unknowns；
3. **Change Queue**：今日哪些资产/叙事/范式发生高价值 state transition，值得 RAY 审阅。

不做：实时交易终端、自动下单、社交荐股、收益承诺。

## 12. Q0 Freeze Decisions

Q0 若经 Human Review 接受，冻结以下工程决策：

- 不新建第五个“大一统 repo”；使用现有四仓分权；
- `yuanli-invest` 负责 business research contracts/canon；
- `quant-workspace` 负责 deterministic quant/data execution；
- `yiru-macro-cockpit` 只作为 macro snapshot provider；
- `yuanli-invest-rsi` 保持 isolated challenger；
- raw evidence 不入 Git；
- P/N/X 不变成任意 scalar multiplication；
- Manager + specialists-as-tools 为默认 agent pattern；
- MCP/function tools 为统一 data access boundary；
- 30-asset seed universe 先于 300-asset scaling；
- Replay/Eval 先于生产化；
- Q0 不改变 A9 operational-canon authority。

## 13. Q0 Exit / Next Gate

Q0 退出必须满足：

- main architecture spec Human Accepted；
- repo boundary accepted；
- DuckDB/data contract accepted；
- JSON schemas accepted；
- six-agent contracts accepted；
- MCP tool contract accepted；
- 30-asset seed universe accepted as research seed, not recommendation；
- replay/eval protocol accepted；
- CI/Human Gate accepted；
- 90-day implementation roadmap accepted。

下一阶段：`Q1 | China-US AI Universe & Data Contract Qualification`。

在 Q0 Human Review 前，不实施生产采集、不切换 operational canon、不修改 RSI FROZEN、不把 seed universe 解释为投资推荐。