# YIP2｜Yuanli Investment Portal 2.0 Experience Architecture Design

Status: **DESIGN_ACCEPTED_PENDING_WRITTEN_SPEC_HUMAN_REVIEW**  
Design acceptance: `ACCEPT_YIP2_PORTAL_2_0_EXPERIENCE_ARCHITECTURE_DESIGN`  
Upstream repository baseline: `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
Scope: Notion Human Projection architecture only.  
Out of scope: GitHub Canon mutation, ontology/schema/registry authority, portfolio sizing, trading/live execution, ME2–ME5 authorization, public publishing.

---

## 0｜Purpose

YIP2 upgrades the existing Notion page **「原力投研」** from a strong entrepreneur-facing investment-judgment lesson into **原力投研 Portal 2.0**: a Human Projection that faithfully translates the accepted Yuanli Investment Canon into an entrepreneur-readable, behavior-changing journey.

The design must preserve the existing Portal principle:

> **后台极严，前台极轻。**

GitHub remains Canon / authority source. Notion remains Human Projection / learning experience.

The Portal does not attempt to reproduce repository complexity. It translates accepted semantics into a journey that changes how an entrepreneur approaches a real investment opportunity.

---

## 1｜M0 — One Belief

The single controlling belief is:

# **先问你准备赚什么钱，再问你准备买什么资产。**

Everything in the Portal must serve this belief.

Supporting narrative roles:

- Explanation bridge: 投资不是预测未来，而是在不确定中建立一个可验证、可承受、可复利的判断系统。
- Final return: 不是每次都对，而是活得足够久，抓住少数真正改变财富曲线的大机会。

No secondary story may compete with the One Belief.

---

## 2｜M1 — Audience

### Primary audience

**聪明但混合 Thesis 的企业家投资者。**

They often combine long-term trend, short-term catalyst, valuation, liquidity and narrative into one undifferentiated “I am bullish” opinion, and may silently migrate a failed R thesis into a C thesis after losses.

### Secondary audience

**财富治理型高净值企业家。**

They ultimately care about how multiple assets, managers and strategies fit into a survivable whole-capital system, but Portal 2.0 must not lead with asset allocation.

### Non-primary audience

Users seeking simple asset recommendations may be an entry trigger, but the Portal must not optimize around recommendation delivery.

---

## 3｜M1.1 — Required Behavior Shift

Portal 2.0 is successful only if it moves users through three identity shifts:

# **Asset Picker → Thesis Architect → Reality Learner**

The intended behavior changes are:

1. **Asset center → Return mechanism first**  
   Before asking what to buy, ask: “这一次，我准备赚什么钱？”

2. **Mixed opinion → Separate theses**  
   One Target may host multiple C/R/X theses; one EngineThesis has one primary engine.

3. **Story defense → No Silent Thesis Migration**  
   A failed thesis is settled. A new engine logic requires a new thesis identity.

4. **Research confidence → Capital-expression separation**  
   `Research pass ≠ Capital pass`.

5. **Price-result bias → Reality Settlement**  
   Review mechanism, evidence, falsifier, price path and reality path rather than equating P/L with truth.

The four questions users should internalize after ten minutes are:

1. 世界发生了什么？
2. 这次我到底准备赚什么钱？
3. 我现在拥有的是一个资产，还是一个具体 Thesis？
4. 什么发生以后，我必须承认这个 Thesis 已经死了？

---

## 4｜M2 — One Story, One Grammar

### One Story

> **你以为自己在选择资产，实际上你真正需要学会的，是识别你准备赚什么钱。**

Narrative arc:

`Asset question → Return mechanism → Thesis identity → Capital expression → Reality settlement → Survival / right-tail compounding`

### Human Grammar

The human-facing entry grammar remains:

# **势 · 信 · 极｜真 · 价 · 生**

- 势：世界与产业真实发生了什么？
- 信：市场正在相信什么？
- 极：哪里存在不对称与右尾？
- 真：什么证据真实成立？
- 价：价格已经预付了什么未来？
- 生：如果错了，是否仍保有下一次机会？

Hard guard:

# `Human Grammar ≠ Machine Ontology`

### Return Engine Grammar

Portal 2.0 introduces the accepted Genesis Engine Set:

- `ENG-C｜Compounding`
- `ENG-R｜Reflexive Repricing`
- `ENG-X｜Convexity`

Hard guards:

- `Asset ≠ Engine`
- `Cash ≠ Engine`; Cash is liquidity reserve / BOOK-CASH.
- C/R/X are an open-world Genesis Engine Set, not a proven exhaustive ontology.

### Object Grammar

# `ResearchTarget → EngineThesis → PositionPassport → BookState@PIT`

Human translation:

- Target：我在研究谁？
- Thesis：我为什么认为这一次能赚钱？
- Passport：我准备用什么方式表达？
- Book：这笔资本属于哪一种逻辑？

Hard guards:

- `Target ≠ Thesis ≠ Position ≠ Book`
- `Research pass ≠ Capital pass`
- `No Silent Thesis Migration`

### Final Return

# `Survive → Capture → Compound`

---

## 5｜M3 — Double-Layer Portal Architecture

Portal 2.0 uses two experience layers.

### Layer 1｜Frontstage Journey

Purpose: create the first cognitive shift within roughly five minutes.

It is not a directory and does not expose backend taxonomy.

### Layer 2｜Investment OS

Six Gold Doors provide optional depth after the user understands the core story.

1. **01｜为什么聪明人也会持续犯错？**  
   `YIP0｜Investment Philosophy`

2. **02｜看一个机会之前，先看这六件事**  
   `Human Grammar｜势·信·极｜真·价·生`

3. **03｜你到底准备赚哪一种钱？**  
   `Return Engines｜C / R / X`

4. **04｜从“我看好”到一个真正的 Thesis**  
   `Target → Thesis → Passport → Book`

5. **05｜让现实结算，而不是让记忆改写历史**  
   `PIT → Evidence → Falsifier → Replay → Benchmark → Settlement → Revision`

6. **06｜同一套方法，看五种完全不同的资产**  
   `Case Lab`

A separate **Case Registry｜案例实验室** is created as the scalable index behind Gold Door 06.

---

## 6｜M3.1 — Page-Level Construction Blueprint

### Existing page identity

The current Notion page **「原力投研」** must be upgraded in place. Its existing URL / Domain Registry identity should be preserved. A duplicate competing Portal page must not be created.

### Frontstage blocks

The Portal frontstage is constrained to one continuous journey:

1. **Hero** — `你准备赚什么钱？`
2. **Mirror** — 用户可能一直在用“资产名”代替 Thesis。
3. **Question Upgrade** — three different return-source questions.
4. **Main Peak** — C / R / X.
5. **NVIDIA Reveal** — same Target, different theses.
6. **Object Architecture** — Target → Thesis → Passport → Book.
7. **Red Card** — No Silent Thesis Migration.
8. **Reality Settlement** — Thesis → Evidence → Falsifier → Reality / Price Path → Settlement → Revision.
9. **Final Return** — Survive → Capture → Compound.
10. **Choose Your Door** — six question-led Gold Doors.

The frontstage may be visually divided into 8–10 Notion sections, but semantically it remains one journey rather than a collection of independent modules.

### Gold Door 01｜Philosophy

Human title: **为什么聪明人也会持续犯错？**

Core structure:

`实在 → 可错 → 反身 → 演化 → 凸性 → 生存`

Human Canon compression:

- 顺大势，不预测世界；
- 乘共识，不服从共识；
- 押极值，不押上生存；
- 守证据，不迷信模型；
- 问价格，不崇拜伟大；
- 等现实，不捍卫观点。

### Gold Door 02｜Human Grammar

Human title: **看一个机会之前，先看这六件事**

Core: `势 · 信 · 极｜真 · 价 · 生`

Must explicitly preserve `Human Grammar ≠ Machine Ontology`.

### Gold Door 03｜Return Engines

Human title: **你到底准备赚哪一种钱？**

- C: `Value Creation → ROIC → Reinvestment → FCF → Intrinsic Value`
- R: `Reality ↔ Expectations ↔ Narrative ↔ Liquidity ↔ Price`
- X: `Small Known Loss + Large Open Upside`

Boundary section must include Asset ≠ Engine, Cash ≠ Engine, and non-automatic classification warnings.

### Gold Door 04｜Thesis Architecture

Human title: **从“我看好”到一个真正的 Thesis**

Core: `ResearchTarget → EngineThesis → PositionPassport → BookState@PIT`

Must include:

- same target may host multiple theses;
- one thesis has one primary engine;
- Research pass ≠ Capital pass;
- No Silent Thesis Migration.

### Gold Door 05｜Reality Learning Loop

Human title: **让现实结算，而不是让记忆改写历史**

Core loop:

`PIT → Evidence → Falsifier → Replay → Benchmark → Settlement → Revision`

Two human artifacts are introduced:

- **Thesis Card**
- **Settlement Card**

### Gold Door 06｜Case Lab

Human title: **同一套方法，看五种完全不同的资产**

Genesis five:

- NVIDIA
- Gold
- UST30Y
- Copper
- USDJPY

Each case must answer:

1. Target 是什么？
2. 哪些 Engine Thesis 合理？
3. 最大混淆风险是什么？
4. 什么现实能证伪？

No case is a recommendation or live signal.

---

## 7｜M4 — Choreographed Journey

The journey follows the Imagineering rhythm:

# **埋 → 引 → 峰 → 转 → 结 → 终**

Approximate emotional intensity:

- Hero: 4/10
- Mirror: 6/10
- Question Upgrade: 7/10
- C/R/X main peak: 10/10
- NVIDIA Reveal: 8/10
- Object Architecture: 7/10
- No Silent Thesis Migration: 9/10
- Reality Settlement: 7/10
- Survive/Capture/Compound: 6/10
- Gold Doors: 4/10

### Main-peak discipline

The only maximum peak is:

# **C / R / X**

`Target ≠ Thesis ≠ Position ≠ Book` is the second cognitive peak but must remain visually subordinate.

`Survive → Capture → Compound` is the closing resonance, not a competing peak.

### CTA vocabulary

Only four CTA families should be used:

- **带一个真实投资机会进来**
- **进入这一扇 Gold Door**
- **写一张 Thesis Card**
- **做一次 Settlement**

The experience should not fragment into many unrelated calls to action.

### Sensory / visual principle

Notion should use structure and pacing rather than simulate a high-freedom web UI.

Suggested single-page motifs:

- C: time / tree / river / compounding
- R: feedback loop / ripple / mirror
- X: curve / open tail / asymmetry
- Reality: horizon / scale / settlement line
- Survival: shield / reserve / space

Each page should use one primary motif, not multiple competing metaphors.

---

## 8｜M5 — Keep the Promise & Governance

### Authority chain

# `Reality / Evidence → GitHub Canon → Human Acceptance → Notion Human Projection → Entrepreneur Experience`

Experience feedback may create editorial revisions or upstream candidates, but cannot directly mutate Canon.

The system is:

> **双向学习，单向法权。**

### Existing Portal governance is reused

YIP2 must conform to the existing Notion governance rather than invent a new lifecycle:

`candidate → canon_ready / projection_draft → human_review → review_ready → published → current | stale | deprecated | blocked`

No YIP2-specific alternative lifecycle is introduced.

### Domain Registry provenance

Implementation must populate or correctly use existing provenance fields after checking the live schema:

- Canon URI
- Canon Revision
- Source Authority
- Projection State

No new enum or database schema is invented unless separately designed and approved.

### Three Drift Gates

#### A｜Semantic Drift Gate

If accepted upstream semantics change, assess whether the Portal remains equivalent. If not, current projection becomes `stale` before reprojection.

#### B｜Pedagogy Drift Gate

If Canon is unchanged but users misunderstand the experience, editorial wording / structure may change without a Canon proposal, provided semantics remain unchanged.

#### C｜Authority Drift Gate

If Portal wording implies buy/sell, portfolio sizing, live trading, fixed ticker→engine identity, or research→capital authorization, the projection is `blocked`, not merely stale.

### Case Lab hard boundaries

1. `Case ≠ Recommendation`
2. `Target ≠ Current Thesis`
3. `Historical Replay ≠ Live Signal`
4. `No Case without Falsifier`

Every case must preserve PIT / as-of context and non-recommendation boundaries.

### Keep-the-Promise artifacts

#### Thesis Card

Human-facing fields should preserve the semantics of:

- Target
- Primary Engine
- Mechanism
- Evidence
- Falsifier
- Expression Intent
- Survival Boundary
- As-of

#### Settlement Card

Must preserve:

- original thesis;
- what was known then;
- what happened later;
- evidence outcome;
- falsifier outcome;
- reality / price path;
- settlement;
- learning / revision.

These are Human Projection artifacts, not portfolio or trading authority.

### Golden Loop

`Real Opportunity → Human Grammar → Engine Thesis → Thesis Card → Reality → Settlement Card → Learning → Next Thesis`

Portal success is therefore measured by reusable judgment objects and behavior change, not reading completion or praise.

---

## 9｜Human Review Contract

Before advancing the Portal from `human_review` to `review_ready`, require **10/10 PASS**:

1. User can repeat the One Belief within 30 seconds.
2. User can distinguish C / R / X.
3. User understands `Asset ≠ Engine`.
4. User understands `Target ≠ Thesis ≠ Position ≠ Book`.
5. User recognizes Silent Thesis Migration.
6. User can independently draft a Thesis Card.
7. User can repeat `Survive → Capture → Compound`.
8. No Portal language converts research authority into capital / trading authority.
9. Canon-derived core concepts have provenance.
10. Case Lab entries satisfy PIT + Falsifier + non-recommendation boundary.

Design review does not substitute for real-user validation.

---

## 10｜Opening Day / Reality Gate

Portal 2.0 build completion does **not** imply publication or Reality acceptance.

Required lifecycle:

`Design Accepted → Written Spec Accepted → Implementation Plan → Notion Projection Build → Internal Verification → Human Review → Opening Day / Live Trial → Reality Evidence → Projection Acceptance → separate Publish authorization if desired`

The broader Yuanli Portal remains PRIVATE / NOT PUBLISHED unless separately authorized.

The critical real-world signal is not “users like it” but whether, on the next real investment opportunity, users independently ask:

> **这次我到底准备赚什么钱？**

---

## 11｜Projection Watch Contract

Future accepted GitHub changes that touch philosophy, human grammar, return-engine semantics, object semantics, settlement semantics, or user-facing authority must trigger a projection-impact review with one of three results:

- `NO_PROJECTION_IMPACT`
- `EDITORIAL_REFRESH`
- `SEMANTIC_REPROJECTION_REQUIRED`

If semantic reprojection is required, the Portal must become stale before revision and re-enter Human Review.

ME2–ME5 may be shown only as roadmap visibility where appropriate. This design creates **no authorization** for ME2, ME3, ME4 or ME5.

---

## 12｜Explicit Non-Goals / Restraint List

Portal 2.0 must not become:

- an investment encyclopedia;
- a recommendation center;
- a live-market dashboard;
- a C/R/X scoring leaderboard;
- a place where one ticker is permanently bound to one engine;
- a place where research approval becomes buy / sizing authority;
- a public publishing action;
- a second Canon or SSOT;
- a surface for unaccepted ME2–ME5 theory;
- a mirror of GitHub schemas, JSON, registries or engineering internals.

The frontstage should remain question-led, entrepreneur-readable and behavior-first.

---

## 13｜Acceptance Boundary

Acceptance of this written design means only:

- the Portal 2.0 experience architecture is approved for implementation planning;
- the existing 「原力投研」 Notion identity is the intended upgrade target;
- the 1 Journey Portal + 6 Gold Doors + 1 Case Registry structure is frozen;
- the C/R/X main-peak discipline and Human Projection authority boundaries are frozen.

It does **not** authorize:

- direct Notion modification before an implementation plan is approved;
- Canon or schema changes;
- trading / portfolio actions;
- ME2–ME5;
- public publishing.

Required next Human Gate after written-spec review:

`ACCEPT_YIP2_PORTAL_2_0_WRITTEN_DESIGN_SPEC`
