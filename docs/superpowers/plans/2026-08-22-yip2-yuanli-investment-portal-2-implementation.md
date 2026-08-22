# YIP2｜Yuanli Investment Portal 2.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing Notion「原力投研」page into Portal 2.0 with one frontstage journey, six Gold Doors, one Case Registry, two reusable learning artifacts, provenance alignment, and human-review gates—without changing GitHub Canon, creating trading authority, authorizing ME2–ME5, or publishing the Portal.

**Architecture:** Preserve the existing Notion domain identity and URL, then rebuild the page as a Human Projection journey whose single peak is C/R/X. Create six human-facing depth pages plus one scalable Case Registry index beneath the existing Portal identity. Reuse current Notion governance (`Portal Authority Constitution v1.0`, `Projection Lifecycle v1.0`, `Naming Standard v1.0`) and update Domain Registry provenance only after live schema inspection. Treat all Notion content as projection-only; GitHub accepted Canon remains upstream authority.

**Tech Stack:** Notion API/MCP page + database operations, GitHub accepted Canon and design artifacts, Notion-flavored Markdown, existing Yuanli Portal governance and Domain Registry.

**Spec:** `docs/superpowers/specs/2026-08-22-yip2-yuanli-investment-portal-2-design.md`

## Global Constraints

- One Belief: **先问你准备赚什么钱，再问你准备买什么资产。**
- Primary audience: 聪明但混合 Thesis 的企业家投资者；Secondary audience: 财富治理型高净值企业家。
- Core identity shift: `Asset Picker → Thesis Architect → Reality Learner`.
- Human Grammar: `势 · 信 · 极｜真 · 价 · 生`; it must never be presented as machine ontology.
- Return engines: `ENG-C / ENG-R / ENG-X`; `Asset ≠ Engine`; `Cash ≠ Engine`; C/R/X remain an open-world Genesis Engine Set.
- Object grammar: `ResearchTarget → EngineThesis → PositionPassport → BookState@PIT`.
- Hard guards: `Target ≠ Thesis ≠ Position ≠ Book`, `Research pass ≠ Capital pass`, `No Silent Thesis Migration`.
- Final return: `Survive → Capture → Compound`.
- Notion remains Human Projection only. No Canon, schema, registry authority, portfolio sizing, trading/live execution, or public-publish authority is created.
- Existing Notion projection lifecycle must be reused; do not invent a YIP2-specific state machine.
- ME2–ME5 are not authorized. Roadmap visibility, if shown, must explicitly say `Roadmap visibility ≠ Stage authorization`.
- Existing「原力投研」Notion identity/URL must be preserved; do not create a competing replacement Portal page.
- No Case Lab item may be treated as a current recommendation or live signal; every case requires PIT/as-of context and a Falsifier.
- Portal build completion does not authorize publishing. The broader Portal remains PRIVATE / NOT PUBLISHED unless separately authorized.

---

## File / Resource Map

This implementation modifies Notion resources rather than repository runtime code. GitHub receives only execution receipts / governance records if the existing process requires them; the Portal content itself lives in Notion.

### Existing Notion resources to inspect and preserve

- `原力投研` page — existing Portal identity and current frontstage content.
- `Domain Registry` — row `YW-INVEST`.
- `Portal Authority Constitution v1.0` — authority rules.
- `Projection Lifecycle v1.0` — state machine.
- `Naming Standard v1.0` — stable-key rules.
- `Change Log` — execution record.

### Notion resources to create under the existing 原力投研 identity

- `01｜为什么聪明人也会持续犯错？`
- `02｜看一个机会之前，先看这六件事`
- `03｜你到底准备赚哪一种钱？`
- `04｜从“我看好”到一个真正的 Thesis`
- `05｜让现实结算，而不是让记忆改写历史`
- `06｜同一套方法，看五种完全不同的资产`
- `Case Registry｜案例实验室`
- Five Genesis case pages: `NVIDIA`, `Gold`, `UST30Y`, `Copper`, `USDJPY`.
- Two reusable Human Projection artifacts/templates: `Thesis Card`, `Settlement Card`.

### Optional GitHub execution records

If the existing yuanli-invest governance pattern requires execution receipts, create them only after Notion implementation is verified; do not add them pre-emptively.

---

### Task 1: Inspect Live Notion Schemas and Freeze Exact Resource IDs

**Resources:**
- Read: existing `原力投研` page
- Read: Domain Registry database + data source schema
- Read: Portal Authority Constitution v1.0
- Read: Projection Lifecycle v1.0
- Read: Naming Standard v1.0
- Read: Change Log

**Interfaces:**
- Consumes: accepted YIP2 design spec.
- Produces: exact Notion page IDs, data source URL, exact property names/options for `YW-INVEST`, existing child-page inventory, and current content snapshot used by later tasks.

- [ ] **Step 1: Fetch the existing 原力投研 page and record identity**

Verify:

```text
Title = 原力投研
Domain Key = YW-INVEST
Existing page identity is preserved
Existing URL is the upgrade target
```

- [ ] **Step 2: Fetch the parent Domain Registry database/data source schema**

Record exact property names and allowed select/status values for at least:

```text
Domain Key
Projection State
Canon URI
Canon Revision
Source Authority
Last Reviewed
Visibility
Featured
Root Question
Promise
Hero Statement
```

Do not write any values yet.

- [ ] **Step 3: Fetch existing Portal governance pages**

Confirm exact current rules:

```text
Portal is Projection, never Canon
candidate → canon_ready / projection_draft → human_review → review_ready → published → current | stale | deprecated | blocked
Upstream semantic drift → stale
Authority drift → blocked
Stable keys remain backstage even if human titles change
```

- [ ] **Step 4: Inventory child pages/databases under 原力投研**

Expected result: no existing YIP0/ME0/ME1 Gold Door subtree that would conflict with the new structure. If any child page exists, stop and classify it as `reuse`, `relocate`, or `preserve`; never delete implicitly.

- [ ] **Step 5: Capture current frontstage content for migration**

Extract these legacy assets for reuse:

```text
面对一个永远不确定的世界，你凭什么下注？
Investment Thesis / Falsifier Memo
Outcome Receipt
什么会让我承认错
错了以后损失是否可承受
财富最终购买时间、风险承受力、重新开始的能力与选择权
```

- [ ] **Step 6: Gate**

Expected: exact IDs/schemas known, no ambiguity about resource ownership or lifecycle. If schema does not support intended provenance values, do not invent new options; stop for a schema-design decision.

---

### Task 2: Build the Six Gold Door Pages and Case Registry Skeleton

**Resources:**
- Create under existing `原力投研` page: six Gold Doors + Case Registry.

**Interfaces:**
- Consumes: exact parent page ID from Task 1.
- Produces: stable child-page URLs/IDs used by Portal navigation and later content tasks.

- [ ] **Step 1: Create Gold Door 01 shell**

Title exactly:

```text
01｜为什么聪明人也会持续犯错？
```

Initial body:

```markdown
> Human Projection｜YIP0 Investment Philosophy

这里回答一个问题：为什么再聪明的人，也不可能通过更多信息彻底消灭投资中的不确定性？
```

- [ ] **Step 2: Create Gold Door 02 shell**

Title:

```text
02｜看一个机会之前，先看这六件事
```

Initial body includes the explicit guard:

```markdown
> Human Grammar｜势 · 信 · 极｜真 · 价 · 生

**Human Grammar ≠ Machine Ontology**
```

- [ ] **Step 3: Create Gold Door 03 shell**

Title:

```text
03｜你到底准备赚哪一种钱？
```

Initial body:

```markdown
> Return Engines｜C / R / X

**Asset ≠ Engine**
**Cash ≠ Engine**
```

- [ ] **Step 4: Create Gold Door 04 shell**

Title:

```text
04｜从“我看好”到一个真正的 Thesis
```

Initial body:

```markdown
> Thesis Architecture

`ResearchTarget → EngineThesis → PositionPassport → BookState@PIT`

**Target ≠ Thesis ≠ Position ≠ Book**
**Research pass ≠ Capital pass**
```

- [ ] **Step 5: Create Gold Door 05 shell**

Title:

```text
05｜让现实结算，而不是让记忆改写历史
```

Initial body:

```markdown
> Reality Learning Loop

`PIT → Evidence → Falsifier → Replay → Benchmark → Settlement → Revision`
```

- [ ] **Step 6: Create Gold Door 06 shell**

Title:

```text
06｜同一套方法，看五种完全不同的资产
```

Initial body includes:

```markdown
> Case Lab

案例用于展示研究方法、Thesis 分解与 Reality Settlement，不构成当前投资建议或实时交易信号。
```

- [ ] **Step 7: Create Case Registry shell**

Title:

```text
Case Registry｜案例实验室
```

Body:

```markdown
这里保存 Point-in-Time 的方法论案例。每个案例必须回答：Target 是什么、哪些 Engine Thesis 合理、最大混淆风险是什么、什么现实能证伪。

**Case ≠ Recommendation**
**Historical Replay ≠ Live Signal**
**No Case without Falsifier**
```

- [ ] **Step 8: Re-fetch all seven pages**

Expected: correct parent, correct titles, no accidental duplicate pages, all boundary copy present.

---

### Task 3: Build Gold Door 01 — YIP0 Philosophy Human Projection

**Resources:**
- Modify: Gold Door 01.

**Interfaces:**
- Consumes: accepted YIP0 semantics already frozen in GitHub and YIP2 spec.
- Produces: entrepreneur-readable philosophy page; no new philosophy claims.

- [ ] **Step 1: Replace shell with full philosophy journey**

Required structure:

```markdown
## 为什么聪明人也会持续犯错？

投资最危险的幻觉，是以为只要信息足够多、模型足够强，就能把未来变成确定答案。

## 六个底层事实

### 实在
现实不会因为你的观点改变而消失。

### 可错
任何模型、叙事和判断都只是对现实的有限压缩。

### 反身
市场参与者的信念会改变价格，价格又会反过来改变行为与现实。

### 演化
竞争、制度、技术、资本和叙事会持续改变游戏本身。

### 凸性
真正改变长期财富曲线的，往往不是平均的小正确，而是少数右尾机会。

### 生存
没有任何一次判断，值得牺牲以后所有判断的资格。

## 六句 Human Canon

- 顺大势，不预测世界；
- 乘共识，不服从共识；
- 押极值，不押上生存；
- 守证据，不迷信模型；
- 问价格，不崇拜伟大；
- 等现实，不捍卫观点。

## 带走什么？

**你不需要确定未来。你需要知道自己为什么相信、什么会让你承认错，以及错了以后是否还能继续。**
```

- [ ] **Step 2: Migrate legacy opening question here**

Move/reuse the old line:

```text
面对一个永远不确定的世界，你凭什么下注？
```

as the page-opening question, not the Portal Hero.

- [ ] **Step 3: Verify semantic restraint**

Must not add portfolio sizing, live recommendations, ME2–ME5 claims, or claim that YIP0 alone selects trades.

- [ ] **Step 4: Re-fetch and review**

Expected: readable in human language, six principles intact, no engineering jargon in the main flow.

---

### Task 4: Build Gold Door 02 — Human Grammar

**Resources:**
- Modify: Gold Door 02.

**Interfaces:**
- Consumes: accepted Human Grammar.
- Produces: six-question opportunity-reading framework.

- [ ] **Step 1: Write the six-door content**

Required copy skeleton:

```markdown
## 看一个机会之前，先看这六件事

### 势｜世界与产业真实发生了什么？
不要从价格开始，先看现实变量、技术、制度、供需和产业结构发生了什么变化。

### 信｜市场正在相信什么？
判断当前共识、预期与叙事是什么，以及它们是否正在扩散、固化或破裂。

### 极｜哪里存在不对称与右尾？
寻找“错了损失有限、对了空间巨大”或者收益高度集中在少数状态的结构。

### 真｜什么证据真实成立？
区分原始事实、推断、叙事和愿望；ClaimAuthority 不能高于 EvidenceAuthority。

### 价｜价格已经预付了什么未来？
好资产不等于好价格。必须问：当前价格已经包含了多少成功？

### 生｜如果错了，我还能不能继续？
任何一次判断都必须服从长期选择权和生存约束。
```

- [ ] **Step 2: Add explicit guardrail section**

```markdown
> **Human Grammar ≠ Machine Ontology**
> 势·信·极｜真·价·生是帮助人看世界的研究语法，不是 C/R/X 的打分器，也不是自动交易模型。
```

- [ ] **Step 3: Add CTA**

Only CTA:

```text
带一个真实投资机会，用这六问重新看一次。
```

- [ ] **Step 4: Re-fetch and verify**

Expected: no scalar score, no claim that six factors mechanically output an engine or position.

---

### Task 5: Build Gold Door 03 — C / R / X Main Peak Page

**Resources:**
- Modify: Gold Door 03.

**Interfaces:**
- Consumes: ME0 accepted engine semantics.
- Produces: core human-facing return-engine explanation.

- [ ] **Step 1: Write C section**

Required semantics:

```markdown
## C｜Compounding
### 赚价值创造与复利的钱

`Value Creation → Value Capture → ROIC → Reinvestment → FCF → Intrinsic Value`

**关键问题：我今天为未来长期现金流付了多少钱？**

C 不是“好公司”的同义词，也不是“股票长期都会涨”。它要求价值创造、价值捕获、再投资与价格之间形成可持续关系。
```

- [ ] **Step 2: Write R section**

Required semantics:

```markdown
## R｜Reflexive Repricing
### 赚信念、资金、价格与现实相互作用形成的重定价

`Reality ↔ Expectations ↔ Narrative ↔ Liquidity ↔ Positioning ↔ Price`

**关键问题：什么正在改变市场相信，并推动价格与现实继续相互强化或最终破裂？**

R 不是“所有上涨”、不是“有故事”、也不是宏观 Regime 本身。
```

- [ ] **Step 3: Write X section**

Required semantics:

```markdown
## X｜Convexity
### 赚有限损失、开放上行的钱

`Small Known Loss + Large Open Upside`

**关键问题：这份非线性上行，现在卖多少钱？**

X 不等于期权、不等于高成长、不等于“这家公司空间很大”。核心是被刻意设计或识别出来的不对称 payoff geometry。
```

- [ ] **Step 4: Add boundary card**

Must include exactly these ideas:

```text
Asset ≠ Engine
Cash ≠ Engine
Great Company ≠ C automatically
Narrative ≠ R automatically
High Growth ≠ X automatically
C/R/X = Genesis Engine Set, open-world
```

- [ ] **Step 5: Verify single-peak presentation**

This page may be visually strongest in Portal 2.0. Do not let another page use stronger top-level visual hierarchy.

- [ ] **Step 6: Re-fetch and verify**

Expected: engine boundaries preserved; no weighted C/R/X score; no recommendation language.

---

### Task 6: Build Gold Door 04 — Thesis Architecture

**Resources:**
- Modify: Gold Door 04.

**Interfaces:**
- Consumes: ME1 accepted object model.
- Produces: human-facing object architecture and behavior guards.

- [ ] **Step 1: Write the four-object explanation**

```markdown
## 从“我看好”到一个真正的 Thesis

### ResearchTarget｜我在研究谁？
它回答身份，不回答为什么赚钱。

### EngineThesis｜我为什么认为这一次能赚钱？
一个 Target 可以同时存在多个 Thesis；每个 Thesis 只有一个 Primary Engine。

### PositionPassport｜我准备用什么方式表达？
它负责把研究判断翻译成资本表达约束，但不自动授予交易权限。

### BookState@PIT｜这笔资本属于哪一种逻辑？
Book 记录 Point-in-Time 的资本逻辑与表达，不把 ticker 永久绑定到某一个 Engine。
```

- [ ] **Step 2: Add NVIDIA bridge example**

```text
NVIDIA × C Thesis = 长期价值创造 / ROIC / Reinvestment / FCF
NVIDIA × R Thesis = AI Capex / EPS Revision / Narrative / Flow / Repricing
NVIDIA × X Thesis = Event Window / Defined Loss / Open Upside
```

Explicitly say: these are methodological examples, not current recommendations.

- [ ] **Step 3: Add No Silent Thesis Migration section**

Required example:

```markdown
买入时：“AI 正在发生反身性重定价。”
下跌后：“没关系，我长期看好 AI。”

**这不是同一个 Thesis。**

R Thesis 失败就结算 R。若后来形成 C Thesis，应创建新的 Thesis；不能改写旧历史。
```

- [ ] **Step 4: Add hard-guard card**

```text
Target ≠ Thesis ≠ Position ≠ Book
Research pass ≠ Capital pass
No Silent Thesis Migration
```

- [ ] **Step 5: Re-fetch and verify**

Expected: no schema dump, no JSON, no lifecycle engineering details unless placed in a collapsed backstage note; frontstage remains human-readable.

---

### Task 7: Build Gold Door 05 + Thesis Card + Settlement Card

**Resources:**
- Modify: Gold Door 05.
- Create: Thesis Card page/template.
- Create: Settlement Card page/template.

**Interfaces:**
- Consumes: accepted settlement/PIT semantics.
- Produces: two reusable human artifacts and a complete learning loop.

- [ ] **Step 1: Write Reality Learning Loop**

```markdown
## 让现实结算，而不是让记忆改写历史

`PIT → Evidence → Falsifier → Replay → Benchmark → Settlement → Revision`

复盘不是重新解释过去，而是保存过去的判断，再让现实结算。
```

- [ ] **Step 2: Create Thesis Card**

Title:

```text
Thesis Card｜一次判断卡
```

Body:

```markdown
## 这一次，我到底在押什么？

- **Target｜我研究谁？**
- **Primary Engine｜C / R / X 哪一个？**
- **Mechanism｜收益为什么会发生？**
- **Evidence｜当前最关键的三条证据是什么？**
- **Falsifier｜什么事实出现，这个 Thesis 必须死亡？**
- **Expression Intent｜我准备如何表达，而不是“自动买入”？**
- **Survival Boundary｜如果错了，我还能不能继续下一局？**
- **As-of｜这张判断卡代表哪个时间点的已知世界？**

> Research pass ≠ Capital pass
```

- [ ] **Step 3: Create Settlement Card**

Title:

```text
Settlement Card｜现实结算卡
```

Body:

```markdown
## 后来现实到底发生了什么？

- 原 Thesis 是什么？
- 当时真正知道什么？
- 后来发生了什么？
- 哪些 Evidence 成立 / 失败？
- Falsifier 是否触发？
- Reality Path 如何变化？
- Price Path 如何变化？
- 这个 Thesis 应该如何 Settlement？
- 我真正学到了什么？
- 下一次要保留、删除或修正什么？

> Settlement evaluates history; it never rewrites history.
```

- [ ] **Step 4: Link both artifacts from Gold Door 05**

Use only these CTAs:

```text
写一张 Thesis Card
做一次 Settlement
```

- [ ] **Step 5: Migrate legacy Falsifier Memo and Outcome Receipt ideas**

Map old Portal concepts into these two artifacts; do not keep parallel competing templates unless explicitly needed.

- [ ] **Step 6: Re-fetch and verify**

Expected: cards preserve human semantics but do not authorize sizing, orders, or trading.

---

### Task 8: Build Gold Door 06 and Five Genesis Case Pages

**Resources:**
- Modify: Gold Door 06.
- Create under Case Registry: NVIDIA, Gold, UST30Y, Copper, USDJPY.

**Interfaces:**
- Consumes: YIM0 Case Lab design and accepted methodology examples.
- Produces: method-demo cases with explicit PIT/Falsifier/non-recommendation boundaries.

- [ ] **Step 1: Write Gold Door 06 intro**

```markdown
## 同一套方法，看五种完全不同的资产

这里不是“哪个资产最好”的榜单，而是看同一套方法如何穿过股票、黄金、长债、工业金属和外汇。

每个案例固定回答四个问题：
1. Target 是什么？
2. 哪些 Engine Thesis 合理？
3. 最大混淆风险是什么？
4. 什么现实能证伪？
```

- [ ] **Step 2: Create NVIDIA case page**

Required frontmatter-style content:

```markdown
> Methodology Case｜Not a recommendation
> As-of / evidence cutoff: explicitly recorded before publication of the case

## Target
NVIDIA

## Possible Engine Thesis Families
C / R / X may coexist as separate theses.

## Key Confusion Risk
把“伟大公司”“AI 大趋势”“短期共识重定价”混成一个 Thesis。

## Falsifier Requirement
每个具体 Thesis 必须独立写 Falsifier；没有 Falsifier 不进入 Gold Case。
```

Do not invent current market facts if no source packet is being used. Keep this page methodological unless a point-in-time evidence pack is separately supplied.

- [ ] **Step 3: Create Gold case page**

Required methodological framing:

```text
Target = Gold
Likely thesis families may differ by C/R/X-style mechanism, but do not declare a current thesis without point-in-time evidence.
Key confusion risk = monetary narrative / safe-haven story / flow / convexity conflation.
Falsifier required per thesis.
```

- [ ] **Step 4: Create UST30Y case page**

Required framing:

```text
Target = UST30Y
Key confusion risk = duration exposure, macro regime, reflexive repricing, convexity and carry being mixed without explicit thesis identity.
No current recommendation.
```

- [ ] **Step 5: Create Copper case page**

Required framing:

```text
Target = Copper
Key confusion risk = structural demand story, cyclical inventory, China/global growth, positioning and price reflexivity being collapsed into one narrative.
No current recommendation.
```

- [ ] **Step 6: Create USDJPY case page**

Required framing:

```text
Target = USDJPY
Key confusion risk = rate differential, policy expectations, carry, intervention risk and reflexive positioning being mixed into one thesis.
No current recommendation.
```

- [ ] **Step 7: Link all five cases from Gold Door 06 and Case Registry**

Expected: Case Registry scales independently from the teaching page.

- [ ] **Step 8: Re-fetch and verify all cases**

Every case must visibly include:

```text
Case ≠ Recommendation
PIT / as-of requirement
Falsifier requirement
Historical Replay ≠ Live Signal
```

If a live evidence pack is absent, the page must remain methodological rather than silently inventing current facts.

---

### Task 9: Rebuild the Existing 原力投研 Frontstage Journey In Place

**Resources:**
- Modify: existing `原力投研` page only.
- Preserve: page identity and child pages created in Tasks 2–8.

**Interfaces:**
- Consumes: Gold Door URLs/IDs and preserved legacy content.
- Produces: one continuous 8–10-section frontstage journey.

- [ ] **Step 1: Preserve all child-page references before replacing content**

Fetch the current page immediately before write. If replace-content would delete child pages, include explicit `<page url="...">` references or use targeted content updates. Never set `allow_deleting_content=true` unless the user separately authorizes deletion.

- [ ] **Step 2: Replace Hero**

Required copy:

```markdown
# 先问你准备赚什么钱，再问你准备买什么资产。

大多数投资错误，并不是因为你不知道未来，而是从一开始就没有说清：**这一次收益究竟准备从哪里来。**

**带一个真实投资机会进来。**

`Survive → Capture → Compound`
```

Do not show YIP0/ME0/ME1/YIM0 in the Hero.

- [ ] **Step 3: Build Mirror section**

```markdown
## 你可能一直在用“资产名”代替判断

“我长期看好英伟达。”
“黄金长期肯定涨。”
“AI 是未来。”
“现在估值不贵。”

这些都可能是真的，但它们还没有回答：**你准备靠什么赚钱？**
```

- [ ] **Step 4: Build Question Upgrade section**

Present only the three questions leading to C/R/X, then CTA `看见 C / R / X`.

- [ ] **Step 5: Build the C/R/X main peak**

Use three columns or equivalent Notion structure. Keep explanations compressed; link to Gold Door 03 for depth. Required bottom guards:

```text
Asset ≠ Engine
Cash ≠ Engine
```

- [ ] **Step 6: Build NVIDIA Reveal**

Show one Target with C/R/X thesis examples; explicitly say methodological example, not current recommendation.

- [ ] **Step 7: Build Object Architecture section**

```text
Target｜我在研究谁？
Thesis｜我为什么认为这一次能赚钱？
Passport｜我准备用什么方式表达？
Book｜这笔资本属于哪一种逻辑？
```

Then:

```text
Target ≠ Thesis ≠ Position ≠ Book
```

- [ ] **Step 8: Build Red Card**

Title:

```text
亏了以后，禁止偷偷换故事。
```

Include the R→C migration example and `No Silent Thesis Migration`.

- [ ] **Step 9: Build Reality Settlement section**

```text
Thesis → Evidence → Falsifier → Reality / Price Path → Settlement → Revision
```

Migrate legacy Outcome Receipt semantics here and link to Settlement Card.

- [ ] **Step 10: Build Final Return section**

Required hierarchy:

```text
Survive
Capture
Compound
```

Closing copy:

```text
你不需要每次都对。你需要活得足够久，直到真正的大机会出现时，你看得懂，也还有资本。
```

- [ ] **Step 11: Build Choose Your Door section**

Show six question-led child-page links only; do not expose backend taxonomy as the primary title.

- [ ] **Step 12: Add top navigation affordances**

Only four navigation intents:

```text
开始一次判断
三种收益引擎
完整 Investment OS
案例实验室
```

Implement using Notion links/mentions without creating duplicate navigation pages.

- [ ] **Step 13: Re-fetch whole page**

Verify:

```text
One Belief visible in first screen
C/R/X is only maximum peak
No second competing hero
No GitHub engineering jargon dumped into frontstage
Child pages preserved
No recommendation language
```

---

### Task 10: Update Domain Registry Provenance Without Inventing Schema

**Resources:**
- Modify: existing `YW-INVEST` Domain Registry row only.

**Interfaces:**
- Consumes: live schema from Task 1 and exact accepted GitHub baseline/design references.
- Produces: traceable Portal provenance.

- [ ] **Step 1: Set Projection State to the correct pre-review state**

Use an existing allowed lifecycle value. Expected at build completion before Human Review:

```text
projection_draft
```

If current schema uses a different exact option spelling, use the existing option; do not create a new lifecycle.

- [ ] **Step 2: Populate Canon Revision**

Record the upstream accepted baseline used for this design:

```text
bd18ec6f92131ddb6948b07973a98d1fe69d5cbb
```

If the Portal implementation is intentionally rebased to a newer main before execution, stop and re-run projection-impact review before changing this value.

- [ ] **Step 3: Populate Canon URI**

Use a stable upstream GitHub Canon/navigation URI that resolves to the accepted methodology source; prefer the YIM0 human-projection/canon navigation entry rather than a transient PR URL.

- [ ] **Step 4: Set Source Authority only if an allowed existing value matches**

Desired semantic meaning:

```text
GITHUB_CANON_PROJECTED
```

If no such allowed option exists, do not add one in this task. Leave the field unchanged and record a governance issue for separate schema design.

- [ ] **Step 5: Update Last Reviewed only if current schema supports it**

Use the actual review date at execution time, not the plan date.

- [ ] **Step 6: Do not change Visibility/Public state**

Portal remains PRIVATE / NOT PUBLISHED.

- [ ] **Step 7: Re-query the exact row**

Expected: provenance traceable, lifecycle valid, visibility unchanged.

---

### Task 11: Add Projection Watch / Drift Notes to Existing Governance Without Creating a Parallel Constitution

**Resources:**
- Prefer update: existing YIP2-related governance/design record or Change Log.
- Do not rewrite Portal Authority Constitution unless a separate authority-design change is approved.

**Interfaces:**
- Consumes: existing governance.
- Produces: operational reminder for future accepted Canon changes.

- [ ] **Step 1: Add a Change Log entry for YIP2 build**

Record:

```text
YIP2 Portal 2.0 projection build
Existing YW-INVEST identity preserved
Frontstage rebuilt around One Belief
6 Gold Doors + Case Registry created
GitHub Canon remains authority
Projection State moved to projection_draft
Public publishing not authorized
ME2–ME5 not authorized
```

- [ ] **Step 2: Record the Projection Watch decision contract**

Use existing governance notes or YIP2 implementation record to preserve these three outcomes:

```text
NO_PROJECTION_IMPACT
EDITORIAL_REFRESH
SEMANTIC_REPROJECTION_REQUIRED
```

and these three drift gates:

```text
Semantic Drift → stale if meaning diverges
Pedagogy Drift → editorial refresh if meaning unchanged
Authority Drift → blocked
```

- [ ] **Step 3: Verify no parallel state machine was introduced**

Search the new YIP2 Notion content for invented states such as `accepted_projection` or `projection_updated`; remove them if present.

---

### Task 12: Internal Verification — Content, Authority, and Link Integrity

**Resources:**
- Read all YIP2 Portal pages.
- Read YW-INVEST registry row.

**Interfaces:**
- Consumes: completed Notion build.
- Produces: internal verification result before Human Review.

- [ ] **Step 1: Verify structural inventory**

Expected:

```text
1 existing Journey Portal upgraded in place
6 Gold Doors
1 Case Registry
5 Genesis case pages
1 Thesis Card
1 Settlement Card
```

No competing second 原力投研 Portal page.

- [ ] **Step 2: Verify navigation**

All child links resolve; Gold Door 06 links to Case Registry and five cases; Gold Door 05 links to both cards; frontstage links to all six doors.

- [ ] **Step 3: Verify One Belief**

The first-screen controlling belief must be exactly:

```text
先问你准备赚什么钱，再问你准备买什么资产。
```

- [ ] **Step 4: Verify engine semantics**

Search all YIP2 pages and fail if any content implies:

```text
one ticker = one engine
C/R/X weighted score
Cash is an engine
narrative automatically means R
high growth automatically means X
great company automatically means C
```

- [ ] **Step 5: Verify object semantics**

Fail if any content implies:

```text
Target = Thesis
Thesis = Position
Research pass = Capital pass
failed R thesis may be silently relabeled C
```

- [ ] **Step 6: Verify authority boundaries**

Fail if any page contains unsupported directive language such as:

```text
应该买入
建议加仓
建议配置 X%
当前信号
交易指令
```

unless clearly quoted as an anti-example.

- [ ] **Step 7: Verify Case Lab boundaries**

Every case visibly includes non-recommendation, PIT/as-of requirement, and Falsifier requirement.

- [ ] **Step 8: Verify governance state**

Expected:

```text
Projection State = projection_draft (or exact existing equivalent)
Visibility remains PRIVATE
No publish authorization
Canon Revision / URI traceable if schema supports them
```

- [ ] **Step 9: Verify no ME2–ME5 authorization**

Any roadmap mention must explicitly remain unapproved / visible-only.

- [ ] **Step 10: Produce internal verdict**

Only valid verdicts:

```text
PASS_READY_FOR_HUMAN_REVIEW
FAIL_REPAIR_REQUIRED
```

Do not advance lifecycle on a failed verification.

---

### Task 13: Human Review Gate — 10/10

**Resources:**
- Portal frontstage + Gold Doors + cases + cards.

**Interfaces:**
- Consumes: `PASS_READY_FOR_HUMAN_REVIEW`.
- Produces: Human Review result; may advance `projection_draft → human_review → review_ready` only after explicit acceptance.

- [ ] **Step 1: Move Projection State to `human_review` using existing lifecycle**

Do this only immediately before Human Review begins.

- [ ] **Step 2: Evaluate 10 criteria**

Required 10/10:

```text
1. 30 秒内复述 One Belief
2. 区分 C / R / X
3. 理解 Asset ≠ Engine
4. 理解 Target ≠ Thesis ≠ Position ≠ Book
5. 能识别 Silent Thesis Migration
6. 能独立写 Thesis Card
7. 能复述 Survive → Capture → Compound
8. Portal 没有把 research authority 偷换成 capital/trading authority
9. Canon-derived 核心概念具有 provenance
10. Case Lab 满足 PIT + Falsifier + non-recommendation
```

- [ ] **Step 3: Record failures literally**

If any criterion fails, leave Portal in `human_review`, repair only the failed projection behavior, and re-run the relevant checks. Do not reinterpret failure as “close enough.”

- [ ] **Step 4: Human acceptance token**

Require a distinct explicit user acceptance before moving to `review_ready`. Suggested token:

```text
ACCEPT_YIP2_PORTAL_2_0_HUMAN_REVIEW
```

- [ ] **Step 5: Advance to `review_ready` only after 10/10 + explicit acceptance**

Do not publish.

---

### Task 14: Opening Day / Live Trial Preparation — No Publication

**Resources:**
- Reuse existing Yuanli Portal Opening Day principles and scorecard patterns.

**Interfaces:**
- Consumes: `review_ready` YIP2 projection.
- Produces: trial-ready but still private Portal.

- [ ] **Step 1: Define trial cohort target**

Use the already-defined audience priority:

```text
Primary: 企业家投资者 who mix theses
Secondary: wealth-governance entrepreneurs
```

Do not recruit or contact anyone automatically in this task.

- [ ] **Step 2: Define minimum behavioral evidence**

Observe whether participants independently:

```text
start from “这次赚什么钱” rather than “买什么”
separate C/R/X logic
separate Asset from Thesis
state a Falsifier
avoid silent thesis migration
complete a Thesis Card
reuse the framework on a second opportunity
```

- [ ] **Step 3: Keep no-teaching/no-rescue discipline**

Facilitator prompting cannot count as success.

- [ ] **Step 4: Freeze build/publication boundary**

State remains private. Trial readiness is not publish authorization.

- [ ] **Step 5: Stop at Reality Gate**

No claim of Portal 2.0 Reality acceptance until actual participant evidence exists.

---

## Self-Review

### Spec coverage

- M0 One Belief → Tasks 9, 12, 13.
- M1/M1.1 Audience + behavior shift → Tasks 9, 13, 14.
- M2 Human Grammar / C-R-X / object grammar → Tasks 4–6, 9.
- M3 double-layer architecture → Tasks 2–9.
- M3.1 page-level blueprint → Tasks 2–10.
- M4 choreographed journey / single peak / CTA discipline → Task 9 + Task 12 verification.
- M5 governance / provenance / drift / artifacts / reality gate → Tasks 7, 10–14.
- Case boundaries → Task 8 + Task 12.
- No public publishing → Global Constraints + Tasks 10, 13, 14.
- No ME2–ME5 authorization → Global Constraints + Task 12.

### Placeholder scan

No `TBD`, `TODO`, “implement later”, or undefined “appropriate handling” steps are permitted. Every task states concrete outputs, boundary checks, and expected states.

### Consistency check

- Existing Portal identity is preserved throughout.
- `projection_draft → human_review → review_ready` follows the existing lifecycle and does not invent new YIP2 states.
- C/R/X remains the single maximum peak; object architecture is subordinate; `Survive → Capture → Compound` is closing resonance.
- Thesis Card and Settlement Card remain Human Projection artifacts, not trading objects.
- Case pages remain methodological if no point-in-time evidence pack is available; the plan explicitly forbids filling those gaps with invented current facts.

---

## Execution Handoff

Plan implementation begins only after the user chooses an execution mode.

**Option 1 — Subagent-Driven (recommended):** use `superpowers:subagent-driven-development`; execute one task per fresh worker with review between tasks.

**Option 2 — Inline Execution:** use `superpowers:executing-plans`; execute task batches in this session with explicit checkpoints.

No Notion write action is authorized by this plan document alone; execution starts only after the user selects an execution mode.
