# YG100-BRAIN1｜Gold 100Y Knowledge Organ Reality Proof — Design

**Date:** 2026-09-02  
**Status:** DESIGN CANDIDATE / HUMAN REVIEW REQUIRED  
**Scope:** Gold 100Y topic only  
**Program:** 原力投研 × 原力 OS × 原力大脑 C2

---

## 1. Purpose

将 `YG100｜黄金100年货币凸性专题` 从 Notion 长文 / 人类页面，升级为原力大脑中的第一个单资产「知识器官」Genesis Case。

目标不是建设第二个知识库，而是证明一条受法权约束、可验证、可回放、可召回、可投影、可结算的专题知识链：

```text
Evidence
→ GoldCase Objects
→ Gold Synthesis
→ Human Projection
→ Brain Recall
→ Use Attestation
→ Reality Settlement
→ Learning / Revision
```

最高约束：

- Canon first, Projection second
- Human Projection != Machine Authority
- Asset != Engine
- Target != Thesis != Position != Book
- Research pass != Capital pass
- ClaimAuthority <= EvidenceAuthority
- Open Case != Settled Case
- Notion edit != Canon mutation

---

## 2. Authority Model

### 2.1 Domain authority

`yuanli-invest` 负责本项目的投资方法论、GoldCase domain contract、Replay schema、case objects 与 human projection source artifacts。

`OB LLM Wiki / Yuanli Brain` 继续承担联邦知识 Canon / evidence graph / authority-aware query surface；本项目不得在 `yuanli-invest` 内创建第二个 OB Canon。

`Notion` 在本项目中仅定义为 Human Projection / Navigation / Learning Surface。Notion Database 不得成为第二个 GoldCase truth store。

`OS-MAX` 若后续承接真实 Decision / Action / Outcome，只记录行动与结果，不负责改写 Gold knowledge canon。

### 2.2 Authority flow

```text
Primary / admitted evidence
        ↓
GoldCase object candidate
        ↓
validation / review / settlement
        ↓
Gold domain committed state
        ↓
Brain knowledge admission / recall surface
        ↓
Notion projection
```

任何下游投影与上游 Canon 冲突时必须 fail closed，并刷新 stale projection。

---

## 3. GoldCase Object Contract

每个历史节点不是一篇文章，而是稳定身份对象：

```text
GoldCase
├── case_id
├── title
├── period_start / period_end
├── world_regime
├── case_type
├── lifecycle_state
├── reality_state
├── belief_state
├── price_state
├── convexity_state
├── primary_engine
├── book_roles
├── action_state
├── primary_drivers
├── cross_asset_signals
├── known_as_of
├── replay_cutoff
├── evidence_refs
├── counter_evidence
├── falsifiers
├── hard_negative
├── settlement_status
├── outcome_summary
├── entrepreneur_lesson
├── authority_state
└── projection_hash
```

### 3.1 Required semantics

- `primary_engine`: only one primary engine per thesis context, using `ENG-C / ENG-R / ENG-X` semantics.
- `book_roles`: belongs to capital task, not asset label; Gold defaults may often include R, conditional S/X, but case-by-case only.
- `action_state`: `守 | 攻 | 持 | 收 | 等 | N/A`，是该 Case 在当时信息集下的研究动作语义，不是实时交易指令。
- `known_as_of` / `replay_cutoff`: 防止 hindsight leakage。
- `counter_evidence` / `falsifiers`: mandatory for every materially investable case.
- `settlement_status`: `OPEN | CLOSED_SUPPORTED | CLOSED_PARTIAL | CLOSED_FALSIFIED | INDETERMINATE`.
- `projection_hash`: 绑定 human projection 与 source object 版本，支持 drift audit。

---

## 4. Frozen Genesis Case Set

V1 冻结 12 个 GoldCase IDs：

1. `YG100-C01`｜1929–1933｜大萧条：黄金作为货币约束
2. `YG100-C02`｜1933–1934｜Gold Reserve Act：Policy T0
3. `YG100-C03`｜1944–1968｜Bretton Woods：重要性 ≠ 投资凸性
4. `YG100-C04`｜1968–1971｜Two-tier market → Nixon window：Genesis T0
5. `YG100-C05`｜1971–1974｜现代黄金第一轮 Monetary R+X
6. `YG100-C06`｜1974–1976｜Hard Negative：真对 ≠ 价对
7. `YG100-C07`｜1976–1980｜第二轮货币失序：攻 → 收
8. `YG100-C08`｜1980–1982｜Volcker：ΔX Flip
9. `YG100-C09`｜1999–2003｜Central Bank Gold Agreement：Policy R T0
10. `YG100-C10`｜2008–2011｜GFC + QE：Monetary R + Tail X
11. `YG100-C11`｜2011–2015｜ETF 清算：拥挤解除与熊市
12. `YG100-C12`｜2022–2026｜Reserve Architecture Repricing：OPEN CASE

V1 不扩增 Case 数量。新增 Case 必须通过后续显式 admission。

---

## 5. C0｜Gold Case Canon & Projection Contract

C0 只冻结法权，不写满 12 个 Case 内容。

Deliverables：

- `gold-case.schema.json` 或等价 machine-readable contract
- `gold-case-registry.yaml/json`
- authority / projection rules
- PIT / evidence / settlement policy
- Notion projection contract
- mutation / conflict / stale behavior

### 5.1 Notion mutation rule

```text
Notion edit
→ event / detected change
→ re-fetch
→ diff
→ authority check
→ proposal
→ canonical review / admission
→ canonical update
→ projection rebuild
→ receipt
```

禁止：

```text
Notion edit → direct canonical mutation
```

---

## 6. K1｜12 Gold Case Canon Bootstrap

每个 Case 最低必须具备：

```text
Identity
+ Point-in-Time boundary
+ Mechanism
+ Evidence
+ Counter-evidence
+ Falsifier
+ Engine semantics
+ Book role
+ Action state
+ Settlement state
```

### 6.1 Hard Negative protection

至少以下对象必须进入独立 Hard Negative 视图 / query class：

- `YG100-C06` 1974–1976
- `YG100-C08` 1980–1982
- `YG100-C11` 2011–2015

目的：阻止系统把 YG100 退化为「黄金长期看多材料库」。

### 6.2 Open Case protection

`YG100-C12` 在 Reality Settlement 前必须保持 `OPEN`。

任何 projection 不得使用“已证明 / 已结算 / 历史定论”语言覆盖其 OPEN 状态。

---

## 7. N1｜Notion Projection Bootstrap

Notion 的正式角色：

```text
Human Projection
+ Navigation
+ Learning Experience
```

不是：

```text
Knowledge Canon
Decision Canon
Outcome Authority
```

### 7.1 Page IA

```text
Hero
→ 30秒结论
→ 真 / 价 / 凸
→ Gold Case Library Projection
→ 100Y Timeline
→ By Action
→ Hard Negative
→ Open Case
→ Cross-Asset Clock
→ Entrepreneur Whole Capital
→ Runtime / Query Guide
```

### 7.2 Hero rule

《黄金100年财富决策地图》属于 generated projection artifact。

Hero 必须由 GoldCase / synthesis 生成或人工核对后绑定 `projection_hash`；Hero 不得反向成为 evidence source。

---

## 8. Q1｜Gold Brain Recall Proof

目标：证明网页版 GPT / Yuanli Brain 能在不依赖直接页面 ID 的情况下稳定召回正确 GoldCase，并尊重 authority / freshness / conflict。

V1 Benchmark：40 cases

- 20 Golden Queries
- 10 Hard Negatives
- 5 Authority Leakage
- 5 Stale / Conflict

### 8.1 Golden examples

- “黄金长期逻辑仍然成立，但为什么可能出现超过40%的中期回撤？” → `YG100-C06`
- “黄金最大的制度性逆风是什么？” → `YG100-C08`
- “现代黄金投资资产的 Genesis T0 是什么？” → `YG100-C04`
- “2008以后黄金主要赚的是什么钱？” → `YG100-C10` + ENG-R / ENG-X

### 8.2 Authority leakage tests

系统必须拒绝：

- 把 Notion card 文案升级成 primary evidence
- 把 Hero infographic 当作 canonical evidence
- 把 `OPEN` C12 说成已结算
- 从 Gold asset label 直接推导永久 Book identity

### 8.3 Acceptance

- deterministic expected-case mapping >= 95%
- Hard Negative leakage = 0
- Authority leakage = 0
- OPEN/CLOSED state confusion = 0
- no write / no promote / no decide / no act from read-only query path

---

## 9. P2｜Projection ↔ Brain Reconciliation Proof

使用一个非关键 Canary 字段验证双向变更语义，但不允许下游静默改 Canon。

Example：修改 `YG100-C12` 的 `projection_note` 或展示标签，而非 settlement / authority 字段。

验证链：

```text
Notion change
→ detected event
→ re-fetch
→ diff
→ authority classification
→ proposal
→ canonical decision
→ rebuild projection
→ receipt
→ natural-language recall
```

安全字段可自动生成 proposal；authority / settlement / evidence 字段必须 fail closed 并进入 Human Gate。

---

## 10. Reality Settlement Boundary

YG100-BRAIN1 只证明知识器官运行，不等于投资结果正确。

真实学习闭环：

```text
Source
→ Synthesis / Case
→ Decision Proposal
→ Action (if separately authorized)
→ Outcome
→ Knowledge Use Attestation
→ Learning Return
→ Decision Delta
```

以下不等价：

- Retrieved != Used
- Used != Correct
- Task done != Outcome
- Approved != Validated
- Projection visible != Canon mature

---

## 11. Acceptance Gates

| Gate | Pass condition |
|---|---|
| G0 Authority | 单一 GoldCase truth path；Notion 不成为第二真源 |
| G1 Object | 12 Case 全部 Stable ID + schema-valid |
| G2 Evidence | 关键 claim 可回到 evidence + PIT boundary |
| G3 Projection | Notion / Hero 有 hash / state 可追溯 |
| G4 Hard Negative | C06/C08/C11 独立可召回且不被牛市叙事覆盖 |
| G5 Open State | C12 在正式 settlement 前始终 OPEN |
| G6 Recall | 40-case benchmark 达标 |
| G7 No Silent Mutation | Notion edit 不得直接改变 canonical authority fields |
| G8 Reality | Use / Outcome / Learning / Decision Delta 彼此分离 |

最终状态只有在 G0–G8 全通过后才能标记：

`GOLD KNOWLEDGE ORGAN OPERATIONAL`

在此之前只能使用：

`DESIGN / BOOTSTRAPPED / PROJECTION READY / QUERY PROOF PARTIAL`

---

## 12. Explicit Non-Goals

V1 不做：

- 自动交易
- 组合仓位建议
- 实时金价交易引擎
- Notion 作为 Canon
- 自动 promotion 到跨域方法论 Canon
- 自动从 price outcome 反推理论正确
- 扩展到 BTC / Oil / Copper / UST

这些只在 YG100 完成 Reality Proof 后作为复制候选。

---

## 13. Implementation Sequence

```text
YG100-C0｜Canon & Projection Contract
        ↓
YG100-K1｜12 GoldCase Objects
        ↓
YG100-N1｜Notion Projection Bootstrap
        ↓
YG100-Q1｜Brain Recall Proof
        ↓
YG100-P2｜Projection Reconciliation Proof
        ↓
YG100-R1｜Reality Settlement (later, when evidence exists)
```

建议当前人闸：

`ACCEPT_YG100_BRAIN1_GOLD_KNOWLEDGE_ORGAN_DESIGN`

该接受仅授权进入实施计划，不授权 Canon promotion、Notion live mutation、外部行动或资本配置。