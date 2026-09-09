# HANDOFF｜YIOS0 当前会话交接

> 下次开新会话，第一句话：**先读 HANDOFF.md。**

更新时间：2026-09-09  
Repository：`moonstachain/yuanli-invest`  
Working branch：`yios0-canonical-definition-design`  
Protected main：`e2f06e039dccca45d178ab017654005cdb135666`  
YIOS0 design head before this handoff：`43679be1b5ee3f594ead1eba99a2116f6ae16e4f`

---

## 1｜当前任务

当前主任务是：

# `YIOS0｜Yuanli Investment OS Canonical Definition`

目标不是再造一套投资理论，而是把已经成立、已经被接受或已经运行到不同阶段的原力投研能力，编译成一个**稳定、可发现、可版本化、机器可解析、人类可理解的系统级定义**。

YIOS0 的母循环已经冻结为：

`Reality → Knowledge → Trial → Settlement → Capital → Execution → Reality → Learning`

YIOS0 的定位是：

- GitHub 上的 **System Architecture / Current Definition Authority**；
- 不替代 YIP0、ME0/ME1、YEX0、YVN1 等子 Canon 的领域法权；
- 不创造新的科学结论；
- 不授予 Capital Authority 或 Execution Authority；
- Notion 只作为 Human Projection，不是 Truth / Canon。

本会话刚刚完成的 Human Gate 是：

`ACCEPT_YIOS0_WRITTEN_SPEC`

这表示 Written Spec 已被接受，允许进入 **Writing Plan**；它**不等于实现授权、不等于合并授权**。

---

## 2｜已经完成的内容

### A. YIOS0 Architecture 已批准

已完成并接受 YIOS0 的系统级架构设计。核心结构包括：

- One System Definition；
- One Stable Current Pointer；
- One Dynamic Status Projection；
- One Machine Contract；
- One Notion Human Projection Contract；
- 12 层 Human Architecture；
- 8 个 Machine Service Boundaries；
- Knowledge Spine / Action Spine；
- Reality Bus / Intelligence Bus / Action Bus；
- Authority / Reality / Runtime 三轴状态模型。

### B. Written Spec 已完成并经过自我审查

Spec 文件：

`docs/superpowers/specs/2026-09-09-yios0-canonical-definition-design.md`

当前设计分支头：

`43679be1b5ee3f594ead1eba99a2116f6ae16e4f`

该 Spec 已特别修正过几个容易出错的语义：

1. YIOS0 是系统定义与发现层，不升级子系统法权；
2. `YIOS0-STATUS-MATRIX.md` 是动态 Projection，不是事实法权本身；
3. `yios0_current.json` 不能通过自声明的 `human_accepted_merged` 字段制造 Canon；
4. Notion 只能消费 GitHub Projection Contract，不能写回 Canon；
5. Architecture Version 与 Runtime / Program Status 必须分离。

### C. Protected main 已重新 Reality Readback

当前 protected `main`：

`e2f06e039dccca45d178ab017654005cdb135666`

required checks：

- `contracts`
- `governance`

当前设计分支相对 `main`：

- `ahead_by = 2`
- `behind_by = 0`

因此当前分支没有落后于主干，不需要先做 rebase 才能继续写 Implementation Plan。

### D. 关键上游法权已物理回读

当前 main 上已确认：

- `YIP0`：accepted + merged；
- `ME0`：accepted + merged；
- `ME1`：accepted + merged；
- `YEX0`：accepted + merged；
- `YVN1-A0`：accepted + merged；
- `YVN1-A1`：仍未授权；
- VeighNa / broker paper / live execution / real capital movement：仍未授权。

同时保留：

`ResearchAuthority != CapitalAuthority != ExecutionAuthority`

`ResearchPass != CapitalPass`

`ClaimAuthority <= EvidenceAuthority`

`UNKNOWN = DENY`

`Receipt = Ledger; Status = Projection`

### E. Gold / Dynamic Repricing 的当前状态已纳入 YIOS0 设计语义

YIOS0 的 Status Matrix 设计要求不能把路线图写成现实。

目前需继续保持区分：

- Gold DP1-A / DP1-B / B2：main 上存在 Reality evidence / baseline；
- YMQ4-B3：科学结论为 NO-GO for the preregistered candidate，但当前没有进入 main 的 YMQ4-B3 Canon receipt；
- YGR0：设计候选，不得伪装成 settled Canon；
- YRP1：架构已讨论/批准，但不能被 YIOS0 预授权为已实现 runtime。

---

## 3｜当前卡住的问题 / 尚未完成

当前不是技术阻塞，而是**流程 Gate 尚未走完**。

### 3.1 Writing Plan 尚未落盘

`ACCEPT_YIOS0_WRITTEN_SPEC` 已通过后，已经开始进入 `superpowers:writing-plans`，但在真正创建 Implementation Plan 文件之前，用户要求先写本 HANDOFF。

所以当前最直接的未完成项是：

> 把 Written Spec 编译成可逐任务执行的 Implementation Plan。

计划文件建议：

`docs/superpowers/plans/2026-09-09-yios0-canonical-definition.md`

### 3.2 YIOS0 实现尚未开始

以下文件都还没有创建：

```text
docs/architecture/yios0/
├── YIOS0-CANONICAL-ARCHITECTURE-v1.0.md
├── YIOS0-CURRENT.md
├── YIOS0-STATUS-MATRIX.md
├── YIOS0-CHANGELOG.md
├── YIOS0-HUMAN-REVIEW-CARD-v1.0.md
├── YIOS0-NOTION-PROJECTION-CONTRACT-v1.0.md
├── YIOS0-MACHINE-QUALIFICATION-RECEIPT-v1.0.md
└── YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json

config/yios0/
├── yios0_architecture.v1.json
└── yios0_current.json

scripts/
└── validate_yios0_canonical_definition.py

tests/
└── test_yios0_canonical_definition.py
```

### 3.3 Notion Projection 尚未执行

Notion 只能在 GitHub YIOS0 Candidate 完成、Human Acceptance、单独 Merge Authorization、protected-main readback 之后，再基于 Projection Contract 写入/更新。

不能现在提前把 Candidate 写成“当前 Canon”。

### 3.4 Merge 仍需独立授权

即使后续 YIOS0 machine qualification + Human Review PASS：

- Human Acceptance ≠ Merge；
- Merge 需要独立 token；
- 推荐 token：`AUTHORIZE_YIOS0_MERGE`。

在这个 token 之前，不要自动 merge protected main。

---

## 4｜下一步计划

下一个会话请严格按下面顺序继续：

### Step 1｜先读本文件和 Written Spec

首先读取：

- `HANDOFF.md`
- `docs/superpowers/specs/2026-09-09-yios0-canonical-definition-design.md`
- 当前 `main` head 和 branch head

并确认没有新的主干漂移。

### Step 2｜完成 Writing Plan

使用 `superpowers:writing-plans`，输出可直接执行的 YIOS0 Implementation Plan。

计划必须至少覆盖：

1. TDD RED：先写 YIOS0 contract tests；
2. machine architecture contract；
3. stable current pointer；
4. dynamic Status Matrix；
5. Canonical Architecture v1.0；
6. Changelog；
7. Notion Projection Contract；
8. fail-closed validator；
9. CI hook；
10. Machine Qualification Receipt；
11. Human Review Card；
12. Human Acceptance Receipt；
13. separate merge gate；
14. post-merge protected-main Reality readback；
15. only-after-merge Notion projection。

### Step 3｜Implementation Plan 完成后再进入执行

推荐继续采用：

`EXECUTE_YIOS0_PLAN_SUBAGENT_DRIVEN`

在用户明确授权前，不要把“计划已完成”误读为“允许实现”。

### Step 4｜实施时坚持 TDD + Fail Closed

实施阶段建议：

`RED → minimal machine contracts → validator → GREEN → architecture docs → status projection → full repo gates → machine receipt → Human Review`

不要先写大段漂亮 Canon 再补 validator。

### Step 5｜Human Gate 与 Merge Gate 分离

Machine Qualified 后先停在：

`YIOS0_CANONICAL_DEFINITION_MACHINE_QUALIFIED / AWAITING_HUMAN_REVIEW`

Human Acceptance 推荐：

`ACCEPT_YIOS0_CANONICAL_DEFINITION`

之后仍需独立：

`AUTHORIZE_YIOS0_MERGE`

### Step 6｜Merge 后才做 Notion Projection

GitHub protected main 重新 readback 成功后，才允许：

`GitHub Canon → Projection Contract → Notion Human Projection`

Notion feedback 只能形成 review request / issue / battle / PR candidate，不能直接改变 Canon。

---

## 5｜踩过的坑 / 需要持续防守的 Hard Negatives

### Pitfall 1｜把“系统状态”写成一个 PASS

YIOS0 已冻结三轴：

- Authority State
- Reality State
- Runtime / Deployment State

禁止用一个 `PASS` 概括所有事情。

### Pitfall 2｜Projection 冒充 Truth

`YIOS0-STATUS-MATRIX.md`、Notion、Web、ChatGPT 都属于 Projection / Experience。

真正的事实法权来自 underlying receipts、main files、独立 runtime evidence。

### Pitfall 3｜Current Pointer 自我授权

`yios0_current.json` 不能靠内部字段声称自己已是 Canon。

Current 的成立必须来自：

`protected-main presence + valid Human Acceptance + merge/readback reality`。

### Pitfall 4｜Human Acceptance 偷渡 Merge

历史 YIP0 / ME0 / ME1 / YEX0 / YVN1 均已证明：

`ACCEPT_* != AUTHORIZE_*_MERGE`

YIOS0 必须继续保持这一纪律。

### Pitfall 5｜Notion 反向污染 Canon

Notion 是低法权 Human Projection。

禁止：

`Notion edit → silently changes GitHub Canon`。

### Pitfall 6｜把路线图写成已经实现

尤其注意：

- YRP1 future procedure；
- State Compiler；
- YVN1-A1 runtime；
- VeighNa adapter；
- broker paper/live execution。

只要没有独立 Reality evidence / authority receipt，就必须保持 NOT_IMPLEMENTED / NOT_AUTHORIZED / DESIGN_ONLY 等真实状态。

### Pitfall 7｜YIOS0 吞掉子 Canon 的法权

YIOS0 是 composition / discovery authority，不是“大一统超级 Canon”。

YIP0、ME0/ME1、YEX0、YVN1 的细节法权继续由其自身文件与 receipts 决定。

### Pitfall 8｜Architecture Version 与 Runtime Status 绑死

架构可以仍是 v1.0，而子系统 runtime 状态持续演化。

不要因为 Status Matrix 更新就自动 bump architecture major version。

### Pitfall 9｜CI 中做网络查询

YIOS0 validator 应基于 repository-local facts fail-closed。

Live GitHub / Notion / external runtime readback 应在 qualification / projection operation 里执行并记录 `known_as_of`，不要把 CI 变成不稳定网络依赖。

### Pitfall 10｜把 execution architecture 当成 execution authorization

YEX0 / YVN1-A0 已进入 main，但仍然：

- no YVN1-A1 runtime authority；
- no VeighNa invocation；
- no broker credential；
- no broker paper；
- no live order；
- no real capital movement。

YIOS0 只能准确描述这个边界，不能改变它。

---

## 6｜下一会话最小启动指令

第一句话直接说：

# `先读 HANDOFF.md。`

然后继续：

> 读取 YIOS0 Written Spec 和当前 GitHub main/branch Reality，完成 `YIOS0 Implementation Plan`。不要重新讨论已经接受的架构；不要开始实现，直到 Implementation Plan 完成并得到明确执行授权。

---

## 7｜当前状态一句话

# `YIOS0 Architecture ACCEPTED → Written Spec ACCEPTED → Implementation Plan PENDING → Implementation NOT STARTED → Merge NOT AUTHORIZED → Notion Projection NOT STARTED`
