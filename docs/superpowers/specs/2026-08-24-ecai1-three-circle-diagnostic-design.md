# ECAI1｜Entrepreneur Capital Constitution & Strategy-Fit Engine
## Three-Circle Diagnostic Architecture Design v0.1

**Status**: `DESIGN_CANDIDATE_AWAITING_HUMAN_REVIEW`  
**Acceptance parent**: `ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_ARCHITECTURE`  
**Research parent**: `main@bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`  
**Scope**: Human-facing diagnostic, report contract, and fit semantics only.  
**Non-authority**: This design does **not** create portfolio, position sizing, trading, execution, manager-selection approval, security recommendation, or ME0/ME1 ontology authority.

---

# 0｜Purpose

ECAI1 converts a high-cognition entrepreneur's capital context, personal investment priors, research specialization, and asymmetry preference into a structured **Capital Constitution** and **Strategy-Fit** output.

The human-facing first-principles model is deliberately simple:

```text
Conviction × Specialization × Asymmetry
            ↓
Force Investment Domain
```

Chinese human grammar:

```text
信念 × 精专 × 凸性 = 原力投资域
```

This is not a numeric product. It is an intersection model.

The system-level objective inherited from Yuanli Investment OS is:

```text
Survive → Capture → Compound
```

and the hard interpretive rule is:

> **生存不是第四圈，而是整个三圈系统的地基。**

The diagnostic therefore answers four different questions in sequence:

1. **Context** — What constraints does this entrepreneur's real capital system impose?
2. **Three Circles** — Where are conviction, specialization, and asymmetry simultaneously strong?
3. **Engine Fit** — Which return engines (ENG-C / ENG-R / ENG-X) fit the person and capital context?
4. **Governance Output** — What should be owned, delegated, explored, avoided, or watched?

---

# 1｜Authority Boundaries

## 1.1 Human Grammar != Machine Ontology

The three circles are a human-facing diagnostic grammar. They do not redefine or replace accepted Yuanli Investment OS ontology.

Existing authority remains:

```text
YIP0 Philosophy
→ OS Human Grammar
→ ME0 Return Engines: ENG-C / ENG-R / ENG-X
→ ME1: ResearchTarget → EngineThesis → PositionPassport → BookState@PIT
→ Settlement / Revision
```

ECAI1 consumes these concepts; it does not mutate them.

## 1.2 Profile != Prescription

An entrepreneur profile may produce fit / non-fit judgments, but **fit is not a recommendation**.

```text
Profile != Prescription
Fit != Buy
Fit != Position Size
Fit != Manager Approval
```

## 1.3 Conviction != Evidence

Personal conviction is a user-state variable, not an evidence source.

```text
PersonalConviction != MarketBelief
PersonalConviction != EvidenceAuthority
```

ECAI1 must never upgrade a market or asset claim merely because the client strongly believes it.

## 1.4 Asymmetry != ENG-X

The human-facing circle `Asymmetry` means **opportunity asymmetry preference / recognition**.
It is broader than the accepted return engine `ENG-X｜Convexity`.

The diagnostic may map a client to ENG-X fit only after separate engine-fit checks.

---

# 2｜Product Experience

The complete experience follows:

```text
Mirror → Map → Constitution
照见自己 → 找到主场 → 建立法则
```

## Mirror
The entrepreneur sees how capital context and decision behavior actually operate.

## Map
The system identifies the user's **Force Investment Domain**: areas where conviction, specialization, and opportunity asymmetry overlap.

## Constitution
The system converts that map into capital-governance rules, engine-fit guidance, delegation boundaries, and review cadence.

---

# 3｜Gold Diagnostic Structure

The first production-grade questionnaire contains **36 questions**:

```text
6  Capital Context
8  Conviction
8  Specialization
8  Asymmetry
6  Scenario Consistency
----------------------
36 Total
```

Target completion time: **15–20 minutes**.

The questionnaire is designed for high-cognition entrepreneurs, not retail risk-profiling. It prefers real constraints and revealed behavior over self-labels such as “稳健型 / 进取型”.

---

# 4｜Section 0: Capital Context (6 questions)

Capital Context is a **constraint layer**, not part of the three-circle score.

## CC-01｜Enterprise capital demand
**未来 3 年，你的企业对新增资金的需求更接近哪种状态？**

- A. 极高：扩张、并购、研发或现金流压力可能持续需要大量资金
- B. 较高：每年仍需稳定追加资本
- C. 中等：基本可由经营现金流覆盖，但偶尔需要补充
- D. 较低：企业基本不需要新增个人资本
- E. 反向：企业预计持续产生可自由分配现金流

Semantic use: enterprise liquidity demand / entrepreneur-finance coupling.

## CC-02｜Freedom floor
**如果你从今天起不再获得主动收入，现有高流动性资产大约能覆盖家庭核心开支多久？**

- A. < 1 年
- B. 1–2 年
- C. 2–5 年
- D. 5–10 年
- E. > 10 年

Semantic use: personal survival floor.

## CC-03｜Primary wealth source
**你当前最大的财富来源是什么？**

- A. 未上市企业股权
- B. 上市公司 / 二级市场金融资产
- C. 房地产
- D. 稳定现金流业务
- E. 现金 / 固收 / 低波资产
- F. 其他

Semantic use: hidden beta / concentration context.

## CC-04｜30% drawdown consequence
**如果你的金融资产在 6 个月内下跌 30%，最接近真实情况的是：**

- A. 会直接影响家庭核心生活或企业经营
- B. 会影响未来 1–3 年的重要计划
- C. 不影响基本生活，但会明显影响心理和决策
- D. 基本不影响家庭或企业计划
- E. 可能反而形成可利用的再配置机会

Semantic use: capacity + behavioral interaction.

## CC-05｜Known large cash needs
**未来 3 年是否存在明确的大额资金需求？**

- A. 有，且金额可能占可投资资产 50% 以上
- B. 有，约占 20%–50%
- C. 有，约占 10%–20%
- D. 有，但占比 <10%
- E. 没有明确大额需求

Semantic use: liquidity floor / capital maturity matching.

## CC-06｜Research time budget
**现实中，你每周愿意稳定投入多少时间研究投资？**

- A. <1 小时
- B. 1–3 小时
- C. 3–7 小时
- D. 7–15 小时
- E. >15 小时

Semantic use: DIY vs delegation capacity.

---

# 5｜Circle A: Conviction (8 questions)

Goal: map **Personal Investment Priors** without rewarding dogmatism.

Response scale for CV-01 to CV-08:

```text
1 = 非常不符合
2 = 比较不符合
3 = 不确定 / 一半一半
4 = 比较符合
5 = 非常符合
```

## CV-01｜Long-horizon priors
我能够清楚说出未来 5–10 年自己最相信的 2–3 个结构性变化。

## CV-02｜Worldview over recent price
我的核心投资观点通常来自长期世界观，而不是近期价格涨跌。

## CV-03｜Noise tolerance
当市场短期反对我的判断时，如果核心证据没有变化，我仍能维持原有研究纪律。

## CV-04｜Falsifiability
对于自己的核心投资信念，我能够明确说出“什么事实出现，我就承认自己错了”。

## CV-05｜Personal vs market belief
我能清楚区分“我相信什么”和“市场现在相信什么”。

## CV-06｜Experience linkage
我的核心投资信念通常与长期职业、创业、产业或生活观察存在真实连接。

## CV-07｜Revision willingness
当现实证据改变时，即使推翻过去长期坚持的观点让我不舒服，我也愿意修改判断。

## CV-08｜Concentration of attention
相比不断追逐新机会，我更愿意长期跟踪少数真正重要的变化。

### Conviction sub-dimensions

```text
Prior Clarity: CV-01, CV-02
Noise Tolerance: CV-03, CV-08
Falsifiability: CV-04, CV-07
Belief Separation: CV-05
Experience Grounding: CV-06
```

Hard-negative rule:

> High conviction + low falsifiability must be diagnosed as **dogmatism risk**, not high-quality conviction.

---

# 6｜Circle B: Specialization (8 questions)

Goal: identify where knowledge is compounding into durable research edge.

Scale: 1–5 as above.

## SP-01｜Time accumulation
至少存在一个领域，我已经连续跟踪或实践 3 年以上。

## SP-02｜Signal discrimination
在我熟悉的领域，我通常能比普通投资者更快判断一条新闻到底重要不重要。

## SP-03｜Information advantage
在至少一个领域，我拥有公开搜索之外的一手经验、产业关系、经营数据或独特信息源。

## SP-04｜Mechanism understanding
我能用简单语言解释自己熟悉领域的价值链、利润池、关键变量和主要失败路径。

## SP-05｜Non-consensus capability
在熟悉领域，我能指出主流共识最可能错在哪里，而不只是重复市场观点。

## SP-06｜Knowledge assets
我已经形成自己的数据、笔记、模型、案例库、访谈网络或研究框架，而不是只依靠临时搜索。

## SP-07｜Focus
如果未来五年只能研究三个投资领域，我可以立即明确自己的选择。

## SP-08｜Ten-year willingness
我愿意未来 5–10 年继续在这些领域投入认知资本，即使短期没有明显交易机会。

### Specialization sub-dimensions

```text
Accumulation: SP-01, SP-08
Signal Edge: SP-02, SP-05
Information Edge: SP-03
Mechanism Depth: SP-04
Knowledge Assets: SP-06
Focus: SP-07
```

Hard-negative rule:

> Familiarity without mechanism depth is not specialization.

---

# 7｜Circle C: Asymmetry (8 questions)

Goal: assess whether the user naturally recognizes and respects non-linear payoff structures.

Scale: 1–5 as above.

## AS-01｜Left-tail first
做投资前，我通常先问“错了最多可能亏多少”，而不是先想“对了能赚多少”。

## AS-02｜Many small losses for few large wins
如果左尾严格受控，我能接受多次小错误，换取少数巨大正确。

## AS-03｜Probability vs payoff
一个机会即使胜率很高，如果赔率很差，我也不会天然喜欢它。

## AS-04｜Trend vs price
我能区分“伟大的趋势 / 伟大的公司”与“当前是不是一个好投资价格”。

## AS-05｜Strike discipline
即使非常看好一个资产，如果当前价格已经透支主要乐观情景，我愿意选择等待。

## AS-06｜Expression design
我会主动思考怎样让“判断错误的损失有限、判断正确的收益更大”，而不只是判断方向。

## AS-07｜No lottery confusion
我不会因为某个机会可能 10 倍，就忽视杠杆、流动性、融资需求或永久损失风险。

## AS-08｜Position geometry
我理解仓位、工具、期限和路径本身也是投资判断的一部分。

### Asymmetry sub-dimensions

```text
Left-Tail Discipline: AS-01, AS-07
Right-Tail Tolerance: AS-02
Probability-Payoff Separation: AS-03
Price Discipline: AS-04, AS-05
Expression Geometry: AS-06, AS-08
```

Hard-negative rule:

> High right-tail appetite + weak left-tail discipline = **lottery preference**, not asymmetry competence.

---

# 8｜Scenario Consistency (6 questions)

Scenario questions are not “correct-answer” quizzes. They test whether declared beliefs are consistent with likely behavior.

## SC-01｜Research thesis drawdown
**你研究多年的一家公司，核心经营事实暂未改变，但股价 6 个月下跌 35%。你最可能：**

- A. 立即止损，价格已经证明市场不认可
- B. 什么都不做，长期持有就不需要再研究
- C. 重新验证原 Thesis、证据、估值与反证，再决定持有 / 加减仓 / 退出
- D. 因为跌了 35%，直接加仓
- E. 先看朋友、媒体或大 V 怎么判断

Diagnostic emphasis: thesis discipline vs price anchoring vs social dependence.

## SC-02｜FOMO theme
**一个你基本不懂的新主题 3 个月上涨 150%，身边多个朋友已经赚钱，你最可能：**

- A. 立即买入，先上车再研究
- B. 先小仓位参与，避免错过
- C. 先判断是否进入自己的能力圈；若没有，不参与或进入观察清单
- D. 做空，因为涨太多
- E. 找一个相关基金 / 管理人立刻配置

Diagnostic emphasis: competence boundary + narrative susceptibility.

## SC-03｜High probability vs high payoff
**如果只能二选一，你更愿意进一步研究哪类机会？**

- A. 80% 概率赚 8%，20% 概率亏 5%
- B. 35% 概率赚 150%，65% 概率亏 15%，且亏损可严格限定
- C. 取决于组合角色、相关性、价格和可重复性，我不会只看胜率

Diagnostic emphasis: payoff literacy, not preference scoring.

## SC-04｜Enterprise opportunity vs investment liquidity
**你的企业突然出现一个高质量并购机会，需要在 30 天内投入大量现金，但你的金融资产正处于浮亏。你会：**

- A. 坚持原金融投资，不愿亏损卖出
- B. 立即清掉所有金融资产
- C. 回到事先约定的 Liquidity / Capital Constitution，根据企业与家庭优先级重新分配
- D. 临时加杠杆同时保留两边
- E. 视市场短期走势再决定

Diagnostic emphasis: capital system integration.

## SC-05｜Manager underperformance
**你委托的专业管理人连续 12 个月明显跑输同类和基准，但策略过程没有明显失真，你最可能：**

- A. 立即赎回，结果已经证明不行
- B. 永远相信管理人，不做处理
- C. 按事先定义的 Manager Thesis 检查机制、风控、容量、漂移和失效证据，再决定
- D. 因为跌得多就追加
- E. 看其他客户是否赎回再决定

Diagnostic emphasis: outcome bias + delegation governance.

## SC-06｜Falsification
**你最核心的一项长期投资判断出现了此前约定的明确证伪事实，你会：**

- A. 继续持有，因为长期逻辑不会错
- B. 寻找新理由解释为什么旧观点仍然成立
- C. 先冻结新增资本，执行预先定义的 thesis review / exit / migration protocol
- D. 等价格反弹后再承认
- E. 视仓位盈亏决定是否修改观点

Diagnostic emphasis: no silent thesis migration.

---

# 9｜Scoring and Interpretation

## 9.1 No global personality score

ECAI1 must not output a single pseudo-precise number such as “Investment Ability = 83.7”.

Allowed outputs:

```text
strong
mature
developing
weak
conflicted
unknown
```

Numeric responses may be used internally for pattern detection but must not be represented as scientific measurement.

## 9.2 Profile + Gate + Intersection

```text
ConvictionProfile
+ SpecializationProfile
+ AsymmetryProfile
+ CapitalContext
+ ScenarioConsistency
        ↓
ForceInvestmentDomain
```

## 9.3 Three-circle interpretations

### Conviction
Evaluate separately:
- clarity
- falsifiability
- independence from market belief
- willingness to revise

### Specialization
Evaluate separately:
- accumulated time
- mechanism depth
- information advantage
- knowledge assets
- focus

### Asymmetry
Evaluate separately:
- left-tail discipline
- payoff literacy
- price discipline
- expression discipline

## 9.4 Conflict flags

The engine must surface contradictions rather than average them away.

Minimum conflict flags:

```text
CF-01 HighConviction_LowFalsifiability
CF-02 HighSpecialization_LowFocus
CF-03 HighRightTail_LowLeftTailDiscipline
CF-04 HighRiskPreference_LowCapitalCapacity
CF-05 HighDIYPreference_LowResearchTime
CF-06 DeclaredDiscipline_ScenarioInconsistency
CF-07 EnterpriseBeta_PortfolioBetaOverlap
CF-08 HighBelief_LowEvidenceDiscipline
```

---

# 10｜Force Investment Domain

The central output is not an asset list. It is a **domain map**.

Each domain is classified into one of five actions:

```text
OWN      = worth personally researching and potentially expressing through valid theses
DELEGATE = strategy may be useful, but the client lacks durable edge or time
EXPLORE  = promising domain, but specialization is not yet mature
AVOID    = violates competence, survival, or governance constraints
WATCH    = strategically relevant but no current action / insufficient evidence
```

A domain statement should look like:

> `AI Enterprise Software × Founder-led Compounders × Long-duration ENG-C` → OWN / EXPLORE

not:

> “Buy technology stocks.”

---

# 11｜Return Engine Fit Contract

Engine fit consumes the three-circle profile but remains separate from it.

## ENG-C｜Compounding Fit

Positive fit signals:
- long time horizon
- business model / cash-flow understanding
- willingness to let winners compound
- tolerance for price volatility when thesis remains intact
- price discipline

Negative fit signals:
- short attention horizon
- frequent thesis switching
- inability to distinguish business quality from entry price

## ENG-R｜Reflexive Repricing Fit

Positive fit signals:
- willingness to monitor state changes
- disciplined updates
- comfort with finite windows and exits
- ability to separate narrative from reality

Negative fit signals:
- “buy and forget” behavior
- inability to update when feedback loop breaks

## ENG-X｜Convexity Fit

Positive fit signals:
- probability/payoff literacy
- tolerance for repeated bounded losses
- understanding of premium, path, expiry, liquidity
- strict left-tail budget

Negative fit signals:
- lottery preference
- inability to accept repeated small losses
- leverage addiction

Outputs:

```text
primary_fit
secondary_fit
learning_only
delegate_preferred
not_fit_currently
unknown
```

---

# 12｜Capital Constitution Report Contract

The Gold report should contain **8 core pages / sections**.

## Page 1｜Capital Mirror
Outputs:
- one-sentence capital identity
- major capital-context constraints
- three-circle summary
- primary contradiction / bottleneck

Example:

> “你不是一个高风险投资者，而是一个深研究型长期复利者；当前瓶颈不是缺少机会，而是容易把好公司等同于好价格。”

## Page 2｜Three-Circle Map
Outputs:
- Conviction profile
- Specialization profile
- Asymmetry profile
- conflict flags
- scenario consistency

## Page 3｜Force Investment Domain
Outputs:
- Primary OWN domains
- Secondary EXPLORE domains
- DELEGATE domains
- AVOID domains
- WATCH list

## Page 4｜Return Engine Fit
Outputs:
- ENG-C / ENG-R / ENG-X fit
- why
- what would improve fit
- delegation boundary

## Page 5｜Capital Blind Spots
Must generate 3–5 specific blind spots linked to questionnaire evidence.

Examples:
- “把懂行业误认为懂价格”
- “企业 Beta 与金融资产 Beta 高度重叠”
- “过度 DIY”
- “高信念但证伪纪律弱”

## Page 6｜No-Go Constitution
Must produce explicit prohibitions / constraints.

Examples:
- Do not use high leverage to express long-duration conviction.
- Do not enter unfamiliar themes solely due to price momentum.
- Do not silently migrate an invalidated thesis into a new engine identity.

## Page 7｜Capital Books & Delegation Map
Human-facing, non-prescriptive book roles:

```text
Safety / Liquidity
BOOK-C
BOOK-R
BOOK-X
Delegated Strategies
```

No specific weights are generated unless a later, separately authorized capital-allocation module exists.

## Page 8｜90-Day Learning & Review Plan
Examples:
- formalize 3 personal investment priors
- choose 1 primary Force Investment Domain
- map current holdings to EngineThesis identity
- identify delegated vs DIY strategies
- define next review trigger

---

# 13｜Gold Sample Persona (for report demo)

Use a fictional persona only.

```text
Name: 陈先生（虚构）
Age: 43
Business: 企业服务 SaaS 创始人
Entrepreneurship tenure: 12 years
Primary wealth source: private company equity + financial assets
Research time: 5–7 hours/week
Core domain experience: SaaS, enterprise software, AI applications
```

Expected sample diagnosis:

```text
Conviction: mature
Specialization: strong in enterprise software / AI applications
Asymmetry: developing; price discipline weaker than business-quality judgment
Scenario consistency: mostly disciplined, with FOMO weakness under social proof
Capital context: high technology / entrepreneurial beta concentration
Primary engine fit: ENG-C
Secondary engine fit: ENG-R
ENG-X: learning-only / delegate-preferred
```

Sample Force Investment Domain:

```text
Primary OWN:
Enterprise Software × AI Applications × Founder-led Compounders × ENG-C

EXPLORE:
AI Infrastructure

DELEGATE:
Short-cycle macro / CTA
Complex options strategies
```

Sample identity line:

> **你的真正优势不是比市场更快，而是比市场更懂。**

---

# 14｜AI Report Generation Contract

Every report claim must trace to one or more questionnaire answers or explicit external evidence added by a later research module.

Minimum provenance object:

```yaml
report_claim:
  claim_id: string
  text: string
  source_questions: [question_id]
  inference_type: direct | derived | conflict_resolution
  confidence: high | medium | low | unknown
  contradiction_flags: []
```

Hard rule:

```text
No Source → No Personalized Claim
```

If the questionnaire does not support a conclusion, output `unknown` or request follow-up information.

---

# 15｜Core Data Model (Design-Level)

```yaml
EntrepreneurCapitalProfile:
  profile_id: string
  recorded_at: datetime
  known_as_of: date
  capital_context: CapitalContext
  conviction_profile: ConvictionProfile
  specialization_profile: SpecializationProfile
  asymmetry_profile: AsymmetryProfile
  scenario_consistency: ScenarioConsistency
  conflict_flags: [ConflictFlag]
  force_investment_domains: [ForceInvestmentDomain]
  engine_fit: ReturnEngineFit
  no_go_rules: [NoGoRule]
  review_contract: ReviewContract
```

Key rule:

```text
Profile@PIT is immutable history.
New review → new profile version.
```

The system must support:

```text
CapitalConstitution@T0
CapitalConstitution@T1
CapitalConstitution@T2
```

without rewriting earlier states.

---

# 16｜ECAI1 Constitutional Invariants

## ECAI1-AX01｜Capital Mission before Allocation
No allocation logic without an explicit capital mission.

## ECAI1-AX02｜Capacity before Preference
Objective capital capacity outranks subjective risk appetite.

## ECAI1-AX03｜Survival before Alpha
No fit classification can override survival constraints.

## ECAI1-AX04｜Competence before Complexity
Complexity requires demonstrated understanding or delegation.

## ECAI1-AX05｜Conviction is not Evidence
Personal belief cannot upgrade evidence authority.

## ECAI1-AX06｜Specialization is not Truth
Deep knowledge does not make a thesis automatically correct.

## ECAI1-AX07｜Asymmetry is Price-Dependent
A large right tail can be destroyed by an unacceptable price / strike.

## ECAI1-AX08｜Fit is not Recommendation
Fit classification never grants buy / sell / size authority.

## ECAI1-AX09｜Delegation is First-Class
Choosing not to DIY is a valid capital-governance outcome.

## ECAI1-AX10｜Constitution is Versioned
Client capital state must be re-settled when life, business, competence, or market context changes materially.

---

# 17｜Hard Negatives / Anti-Patterns

The system must reject the following interpretations:

1. **High conviction = high expected return** → invalid.
2. **Entrepreneur in AI = should own AI stocks** → invalid.
3. **High risk tolerance = high risk capacity** → invalid.
4. **Strong specialization = good investment at any price** → invalid.
5. **Likes asymmetric outcomes = ENG-X fit** → invalid without left-tail discipline.
6. **Poor manager outcome = manager thesis invalid** → invalid without mechanism review.
7. **Questionnaire score = scientific personality truth** → invalid.
8. **Fit classification = trade recommendation** → invalid.
9. **Current constitution = permanent identity** → invalid.
10. **Old thesis can silently change engine after falsification** → invalid.

---

# 18｜Success Criteria

ECAI1 v0.1 is successful if a high-cognition entrepreneur can finish the diagnostic in <20 minutes and receives a report that:

1. feels more specific than a traditional risk questionnaire;
2. identifies at least one actionable **research / governance** insight without needing a security recommendation;
3. separates what the client should **OWN / DELEGATE / EXPLORE / AVOID / WATCH**;
4. surfaces contradictions instead of averaging them away;
5. can explain why ENG-C / ENG-R / ENG-X fit differs;
6. never exceeds evidence authority;
7. preserves compatibility with accepted ME0 / ME1 semantics;
8. creates a versioned artifact that can be re-settled later.

---

# 19｜Implementation Boundary for Next Stage

After human review of this design, the implementation plan may include:

- questionnaire JSON schema;
- deterministic scoring / profile rules;
- conflict-flag evaluator;
- report-generation schema;
- Gold fictional fixture;
- hard-negative fixtures;
- validator;
- CI gate;
- human review card.

It must **not** include without separate authorization:

- live portfolio sizing;
- security recommendations;
- trade execution;
- manager approval / fund selection authorization;
- ME0 / ME1 ontology mutation;
- automatic capital movement.

---

# 20｜Human Review Decision

Required next token after reviewing this written design:

```text
ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_WRITTEN_SPEC
```

If accepted, transition to implementation planning only. No implementation is authorized by this design document itself.
