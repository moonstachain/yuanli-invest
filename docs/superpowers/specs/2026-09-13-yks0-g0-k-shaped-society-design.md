# YKS0-G0｜K-Shaped Society Constitution × Nine-Dimensional K Vector × Five-Country Replay Freeze

**Status:** `WRITTEN_SPEC_HUMAN_ACCEPTED`  
**Human decision:** `ACCEPT_YKS0_G0_WRITTEN_SPEC`  
**Accepted design commit:** `5094a6cb88cd6d98afaa63045e800fb2ffd34a9d`  
**Accepted spec blob:** `58a851f0840e23a6d099299c83ca94183ed7551b`  
**Implementation authority:** `NOT_AUTHORIZED`  
**Merge authority:** `NOT_AUTHORIZED`  
**Program:** `YKS0｜K-Shaped Society × Reality Distribution Regime`  
**Parent architecture:** `YIOS0｜Yuanli Investment OS Canonical Architecture v1.0`  
**Design mode:** YIOS0 Native Capability × Soul Ontology × UIG Federation × Supabase Reality Ledger × HF Blind Lab × Notion Human Atlas  
**Principal:** RAY  
**Date:** 2026-09-13  
**Authority:** Candidate design only. This document creates no Canon, scientific, capital, execution, broker, or publication authority.  
**Physical boundary:** This gate does **not** create or mutate production Supabase, Hugging Face, Notion, broker, or execution assets.

---

## 0｜Executive decision

YKS0 is admitted at design level as a **cross-domain macro-structural research capability candidate** under YIOS0. It is not a parallel OS, not a standalone knowledge base, not a Notion-first dashboard, and not a trading signal.

Its sole mother question is:

> **When aggregate growth persists but the distribution of productivity, profit, employment, wealth, regional opportunity, and social mobility changes, can that distribution regime be represented as point-in-time Reality, tested out-of-sample, and shown to add explanatory value for asset and economic outcomes?**

The system path is frozen as:

```text
External Reality
  ↓
Evidence + Vintage
  ↓
KObservation
  ↓
KState@PIT
  ↓
Nine-Dimensional K Vector
  ↓
KRegime Candidate
  ↓
KTransmission Hypothesis
  ↓
Pre-registered Blind Replay
  ↓
Scientific Settlement
  ↓
Learning Delta
  ↓
Low-authority Projection
```

YKS0 remains on the **Knowledge Spine** until separately settled. No result from YKS0 may cross directly into Capital Action or Execution.

---

# 1｜Constitution

## 1.1 Objective

YKS0 exists to convert the fuzzy human concept “K-shaped society” into a governed machine research object with:

1. explicit dimensions;
2. evidence-backed metrics;
3. point-in-time state;
4. pre-registered hypotheses and defeat conditions;
5. historical blind replay;
6. hard negatives and near twins;
7. asset-transmission tests;
8. settlement and learning receipts;
9. low-authority human/AI projections.

## 1.2 Non-objectives

YKS0 G0 does **not** authorize:

- a single synthetic “K Score”;
- a deterministic claim that GDP per capita crossing a threshold causes K divergence;
- causal promotion of `r > g` as a timing formula;
- automatic policy prescriptions;
- automatic asset allocation;
- research-to-capital conversion;
- real-time trading;
- Notion edits as Canon changes;
- Hugging Face model outputs as truth;
- Supabase runtime writes in this gate;
- production graph runtime changes;
- live external connector mutations.

## 1.3 Mother laws inherited from YIOS0

YKS0 MUST inherit without modification:

1. `Reality > Belief`
2. `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition`
3. `ResearchPass != CapitalPass`
4. `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
5. `ClaimAuthority <= EvidenceAuthority`
6. `UNKNOWN = DENY`
7. `Receipt = Ledger; Status = Projection`
8. historical evidence and settlement may not be rewritten by later learning.

## 1.4 YKS0-specific laws

### YKS-L01｜Distribution before average
Aggregate growth cannot be interpreted without asking how the increment is distributed across firms, labor, regions, and asset owners.

### YKS-L02｜Vector before score
The nine K dimensions remain independent state variables. No single scalar K score may replace them at Canon level.

### YKS-L03｜Level is insufficient
Every admitted metric should, where mathematically meaningful, expose:

`Level`, `Δ`, `Δ²`, `Breadth`, `Dispersion`, `Confidence`, and `KnownAsOf`.

### YKS-L04｜K ≠ inequality
K-shaped divergence is a structural distribution regime; income inequality is only one possible downstream manifestation.

### YKS-L05｜Production K precedes social K unless evidence disproves it
The canonical hypothesis is that structural divergence often propagates from productivity/profit to labor/wealth/opportunity. This is a hypothesis, not a law, and replay may defeat it.

### YKS-L06｜Regime is a transition object
A KRegime represents a transition pattern across multiple dimensions, not a label pasted on one metric or one year.

### YKS-L07｜Policy is endogenous
Redistribution and predistribution are part of the state vector and may alter slope, transmission, or persistence. They must not be treated as external cleanup variables only.

### YKS-L08｜PIT before hindsight
All replay uses information known by T0. Later revisions, later academic synthesis, and later outcomes are withheld until reveal.

### YKS-L09｜Projection is not authority
Notion, Web, ChatGPT, Hugging Face leaderboards, and dashboards are projections or experiment surfaces only.

### YKS-L10｜No asset claim without transmission path
Any asset implication must include an explicit path:

`KDimension/Regime → economic mechanism → control point / value capture → asset species → falsifier`.

---

# 2｜Nine-Dimensional K Vector

The canonical frontstage vector is frozen as nine independent dimensions.

| ID | Dimension | Core question | Primary structural object | Example metric families |
|---|---|---|---|---|
| K01 | `INDUSTRY` | Is value-added migrating from old to new production systems? | sector structure | new/old value-added, capital intensity, service share, IP investment |
| K02 | `FIRM` | Are frontier firms separating from median/laggard firms? | firm productivity distribution | TFP/labor productivity frontier gap, sales concentration, digital/AI adoption gap |
| K03 | `PROFIT` | Is economic surplus concentrating faster than output or employment? | profit/value capture distribution | top-decile profit share, markup, ROIC dispersion, market-cap concentration |
| K04 | `EMPLOYMENT` | Are winners producing growth with less employment diffusion? | employment diffusion | revenue share vs employment share, jobs per unit output, vacancy mix, hiring breadth |
| K05 | `LABOR` | Are skill, wage, bargaining power, or labor-share distributions diverging? | labor income distribution | wage percentiles, labor share, skill premium, occupational polarization |
| K06 | `WEALTH` | Are asset ownership and capital income compounding asymmetrically? | household balance-sheet distribution | housing/equity ownership, net wealth percentiles, capital-income share, portfolio participation |
| K07 | `REGION` | Are growth, population, capital, and opportunity concentrating spatially? | regional distribution | GDP 90/10, population inflow, fiscal capacity, firm density, housing divergence |
| K08 | `OPPORTUNITY` | Is divergence becoming persistent across generations and life outcomes? | mobility/opportunity | education access, intergenerational mobility, marriage/fertility, health, occupational transition |
| K09 | `POLICY` | Are institutions widening or compressing K slopes? | redistribution/predistribution | taxes, transfers, public services, vocational training, SME finance, housing/asset access |

### 2.1 Required state fields per dimension

Each KDimensionState MUST support:

```yaml
level: number|categorical|unknown
delta: number|categorical|unknown
delta2: number|categorical|unknown
breadth: number|categorical|unknown
dispersion: number|categorical|unknown
confidence: [LOW, MEDIUM, HIGH]
evidence_quality: [A, B, C, D, UNKNOWN]
known_as_of: date
revision_state: [ORIGINAL, REVISED, ESTIMATED, SYNTHETIC]
```

`unknown` is a first-class value and MUST NOT be coerced to neutral.

---

# 3｜Object model freeze

YKS0 requires the following semantic objects. Soul remains semantic authority; yuanli-invest owns research-domain operational use.

## 3.1 `KDimension`

```yaml
id
code
name_zh
name_en
definition
exclusions
allowed_metric_families
```

## 3.2 `KMetric`

```yaml
metric_id
dimension_id
name
formula
unit
frequency
preferred_source_class
minimum_history
pit_safe: bool
revision_risk
comparability_notes
```

## 3.3 `KObservation`

```yaml
object_id
metric_id
geo
entity_scope
observation_period
release_date
known_as_of
revision_date
value
unit
source_id
source_locator
evidence_authority
revision_state
method_note
```

## 3.4 `KState`

```yaml
state_id
geo
as_of_date
dimension_states[9]
coverage_ratio
unknown_count
evidence_manifest
compiler_version
fingerprint_sha256
```

## 3.5 `KRegime`

```yaml
regime_id
geo
as_of_date
regime_candidate
supporting_dimensions
contradicting_dimensions
transition_direction
confidence
falsifiers
status: [CANDIDATE, REPLAY_PASS, REPLAY_FAIL, SETTLED]
```

## 3.6 `KTransmission`

```yaml
transmission_id
source_dimension_or_regime
mechanism
intermediate_state
control_point
value_capture_object
asset_species
expected_direction
expected_horizon
preconditions
falsifier
```

## 3.7 `KReplayCase`

```yaml
case_id
country
t0
hidden_horizon
visible_evidence_cutoff
question
hypothesis
baseline
hard_negative_class
scoring_rule
reveal_data_locator
```

## 3.8 `KSettlement`

```yaml
settlement_id
case_or_hypothesis_id
physical_settlement
scientific_settlement
authority_settlement
verdict
score
failure_mode
learning_delta
receipt_locator
```

---

# 4｜Evidence authority and source hierarchy

## 4.1 Source grades

| Grade | Source class | Allowed claim authority |
|---|---|---|
| A1 | national statistical office / central bank / ministry / tax or administrative data | primary factual claim |
| A2 | OECD / IMF / World Bank / BIS / Eurostat / UN / ILO | primary cross-country factual claim |
| A3 | audited public company filings / exchange data / official survey microdata | firm/market factual claim |
| B1 | peer-reviewed academic research with explicit methods and data | mechanism or comparative claim |
| B2 | NBER/CEPR/working paper from identifiable researchers | provisional mechanism claim |
| B3 | reputable sell-side or policy research with reproducible data references | candidate interpretation |
| C1 | high-quality media / conference / interview | contextual evidence only |
| C2 | alternative data vendor / search/social proxy | narrative or activity proxy |
| D | uncited secondary summaries / opinion | discovery only; no settlement authority |

## 4.2 Evidence rule

No KState may be promoted from `CANDIDATE` if:

- fewer than 5 of 9 dimensions have non-UNKNOWN evidence;
- any critical dimension uses only D-grade evidence;
- `known_as_of` cannot be established;
- source revision status is unknown for a metric materially affecting the result.

## 4.3 Cross-country comparability rule

A metric may enter five-country comparative replay only if at least one of the following is true:

1. common international definition exists;
2. a documented crosswalk exists;
3. the replay explicitly treats it as country-native evidence and forbids direct level comparison.

---

# 5｜Regime taxonomy freeze

G0 freezes a six-state candidate taxonomy. It is explicitly subject to replay defeat.

| Regime | Name | Minimum pattern |
|---|---|---|
| KR0 | `BROAD_DIFFUSION` | productivity, employment, and income gains diffuse broadly; concentration stable/falling |
| KR1 | `PRODUCTIVITY_DIVERGENCE` | K02 rises materially while downstream labor/wealth K remains weak or lagged |
| KR2 | `CAPITAL_CONCENTRATION` | K02 + K03 rise; K04/K05 begin to weaken; capital captures more incremental output |
| KR3 | `ASSET_OWNERSHIP_DIVERGENCE` | K06 becomes a major amplifier; asset participation/returns dominate wealth outcomes |
| KR4 | `OPPORTUNITY_LOCK_IN` | K08 persistence rises and mobility falls; regional/educational inheritance becomes material |
| KR5 | `REDIFFUSION` | K09 and/or service/labor absorption measurably compresses one or more K slopes without requiring aggregate stagnation |

Forbidden at G0:

- numeric regime thresholds invented without historical calibration;
- forced assignment when evidence is mixed;
- treating sequence `KR0→KR1→KR2→KR3→KR4` as mandatory.

Allowed output includes `MIXED`, `UNRESOLVED`, and `REGIME_TRANSITION`.

---

# 6｜Hypothesis registry freeze

The first replay program will test eight pre-registered hypotheses.

### H1｜Frontier Divergence
When frontier-firm productivity growth persistently exceeds the median/laggard group, profit concentration tends to rise before median household income divergence becomes obvious.

### H2｜Winner-Less-Hiring
As production becomes more capital/knowledge intensive, leading firms can increase output and profits without proportional employment expansion.

### H3｜Asset Carrier Switch
When household wealth shifts from broad-participation housing toward narrower financial/ownership assets, wealth dispersion tends to rise unless asset participation broadens or redistribution offsets it.

### H4｜Regional Agglomeration
Technology-, capital-, and talent-intensive growth tends to increase regional concentration unless mobility, housing supply, or fiscal equalization strongly offsets it.

### H5｜Service Re-diffusion
A sufficiently large, labor-absorbing service sector can compress labor/employment K even while firm/profit K remains high.

### H6｜Policy Slope Compression
Predistribution institutions (education, vocational training, labor mobility, SME finance, public services) can alter K slopes more durably than transfers alone.

### H7｜Index-Median Divergence
High firm/profit K increases the probability that capitalization-weighted equity indices outperform median listed-company or median-stock outcomes.

### H8｜K-to-Asset Transmission
A correctly identified KRegime adds incremental explanatory value beyond conventional aggregate growth/inflation variables for selected asset-species outcomes.

Every H1–H8 trial MUST define defeat criteria before reveal.

---

# 7｜Five-country replay universe

Countries are frozen as:

- `CN` China
- `US` United States
- `DE` Germany
- `JP` Japan
- `KR` South Korea

Rationale:

- CN: current target regime and large manufacturing economy;
- US: strongest long-run frontier-firm/financial-asset divergence case;
- DE: strong predistribution / vocational / industrial institutions counterfactual;
- JP: mature economy with weak asset inflation periods and regional/demographic constraints;
- KR: high-speed industrialization, chaebol concentration, housing/education intensity, advanced technology exposure.

The first history window is frozen to `1990–2026` unless a case has an earlier T0 needed as a control.

---

# 8｜50-case pre-registered replay freeze

The 50 cases are frozen as **10 per country**. Final exact T0 evidence cutoffs will be bound during G2 from release calendars. G0 freezes the event window and test question.

## 8.1 China｜CN01–CN10

| Case | T0 window | Replay question |
|---|---|---|
| CN01 | 1992–1994 | Did market reform/industrialization broaden diffusion rather than create durable K divergence? |
| CN02 | 1998–2001 | Did SOE reform + WTO accession begin firm/region divergence before household wealth K? |
| CN03 | 2003–2005 | Did export/industrial deepening remain broadly labor-diffusive? |
| CN04 | 2008–2009 | Did stimulus temporarily compress employment/industry K while creating future asset/regional divergence? |
| CN05 | 2012–2013 | Did platform/mobile growth begin a frontier-firm and urban talent concentration regime? |
| CN06 | 2015–2016 | Did deleveraging/industrial policy + housing/financial shifts change the dominant K dimensions? |
| CN07 | 2018–2019 | Did trade pressure + platform scale + manufacturing upgrading widen firm/region divergence? |
| CN08 | 2020–2021 | Was post-COVID recovery K-shaped across firms, sectors, employment, and assets? |
| CN09 | 2022–2024 | Did property balance-sheet stress weaken broad household wealth diffusion while advanced manufacturing concentrated profits? |
| CN10 | 2025–2026 | Is China entering a regime of growth-with-lower-diffusion, or is the K thesis overstated? |

## 8.2 United States｜US01–US10

| Case | T0 window | Replay question |
|---|---|---|
| US01 | 1990–1991 | Was post-recession recovery still broad diffusion? |
| US02 | 1994–1995 | Did early internet/productivity gains begin frontier-firm divergence before dot-com euphoria? |
| US03 | 1998–1999 | Did tech concentration predict later profit/wealth concentration, or was it mainly a valuation episode? |
| US04 | 2001–2003 | After the tech bust, did K structurally reverse or only change carriers? |
| US05 | 2005–2006 | Did broad homeownership temporarily compress wealth K despite rising financial concentration? |
| US06 | 2009–2010 | Did QE/asset-price recovery create asset-ownership divergence ahead of labor recovery? |
| US07 | 2013–2014 | Did superstar-firm productivity/profit concentration become persistent? |
| US08 | 2017–2018 | Did tax/tech/capital concentration widen K without equivalent employment diffusion? |
| US09 | 2020–2021 | Did pandemic policy compress income K while widening wealth/asset K? |
| US10 | 2023–2025 | Did AI/frontier-capex concentration create a new winner-less-hiring regime? |

## 8.3 Germany｜DE01–DE10

| Case | T0 window | Replay question |
|---|---|---|
| DE01 | 1991–1993 | Did reunification widen regional K despite national convergence policy? |
| DE02 | 1998–2000 | Did export/industrial integration create broad labor diffusion or firm concentration? |
| DE03 | 2003–2005 | Did Hartz-era labor reforms compress unemployment K at the cost of wage dispersion? |
| DE04 | 2008–2009 | Did Kurzarbeit/industrial institutions prevent winner-less-hiring dynamics during crisis? |
| DE05 | 2011–2012 | Did Euro crisis generate regional/wealth K inside Germany or primarily external divergence? |
| DE06 | 2014–2015 | Did export-manufacturing strength preserve broad diffusion? |
| DE07 | 2017–2018 | Did digital lag limit frontier-firm K relative to US-style concentration? |
| DE08 | 2020–2021 | Did pandemic transfers and labor institutions compress household K? |
| DE09 | 2022–2023 | Did energy shock widen industry/firm/regional K? |
| DE10 | 2024–2026 | Is Germany a hard negative where weak growth, not high K concentration, dominates outcomes? |

## 8.4 Japan｜JP01–JP10

| Case | T0 window | Replay question |
|---|---|---|
| JP01 | 1990–1991 | Did asset-bubble collapse compress wealth K or merely destroy aggregate wealth? |
| JP02 | 1995–1996 | Did post-bubble stagnation produce low-growth convergence rather than K divergence? |
| JP03 | 1999–2000 | Did technology/manufacturing leaders diverge despite weak macro growth? |
| JP04 | 2003–2005 | Did export recovery create regional/firm K? |
| JP05 | 2008–2009 | Did crisis produce broad compression rather than structural K? |
| JP06 | 2013–2014 | Did Abenomics asset inflation widen ownership K before wage diffusion? |
| JP07 | 2016–2017 | Did tight labor markets compress labor K despite weak productivity diffusion? |
| JP08 | 2020–2021 | Did pandemic policy preserve broad household outcomes while corporate K changed? |
| JP09 | 2023–2024 | Did inflation/wage normalization alter labor vs asset K? |
| JP10 | 2025–2026 | Can Japan exhibit frontier-company winners without a strong society-wide K regime? |

## 8.5 South Korea｜KR01–KR10

| Case | T0 window | Replay question |
|---|---|---|
| KR01 | 1990–1992 | Did high-growth industrialization remain broadly diffusive despite chaebol concentration? |
| KR02 | 1997–1998 | Did the Asian Financial Crisis structurally increase firm/labor/wealth K? |
| KR03 | 2001–2003 | Did ICT/export recovery concentrate productivity and profits? |
| KR04 | 2007–2008 | Did pre-GFC credit/housing conditions widen wealth K? |
| KR05 | 2010–2012 | Did chaebol-led export strength exhibit winner-less-hiring? |
| KR06 | 2015–2016 | Did housing/education/capital ownership increasingly dominate household divergence? |
| KR07 | 2018–2019 | Did semiconductor concentration widen profit and regional K? |
| KR08 | 2020–2021 | Did pandemic asset inflation widen ownership K while transfers softened income K? |
| KR09 | 2022–2023 | Did rate/housing adjustment reverse wealth K or only reduce asset levels? |
| KR10 | 2024–2026 | Does AI/semiconductor concentration create a new frontier-firm K regime? |

---

# 9｜Baseline, hard-negative and near-twin design

## 9.1 Baselines

Every replay case compares YKS0 against at least three baselines:

1. `B0_AGGREGATE_ONLY` — GDP growth, inflation, unemployment, policy rate only;
2. `B1_MARKET_ONLY` — broad equity/bond/house-price outcomes only;
3. `B2_INEQUALITY_ONLY` — Gini / top-income or top-wealth concentration without structural K vector.

## 9.2 Hard-negative classes

The replay MUST contain examples where superficial K language would be wrong:

- `HN1 CYCLICAL_DISPERSION` — short-cycle winners/losers without persistent structural divergence;
- `HN2 AGGREGATE_STAGNATION` — weak growth for almost everyone, not K;
- `HN3 VALUATION_BUBBLE` — market-cap concentration without productivity/profit structural support;
- `HN4 DATA_ARTIFACT` — apparent divergence driven by revisions/definitions;
- `HN5 POLICY_COMPRESSION` — high production K but labor/household K successfully compressed;
- `HN6 ASSET_LEVEL_DROP` — falling asset prices reduce levels but do not improve participation or mobility;
- `HN7 SECTOR_ROTATION` — sector leadership changes with no lasting frontier gap;
- `HN8 REGIONAL_CATCHUP` — lagging regions genuinely catch up despite national concentration narratives.

## 9.3 Near twins

At least 10 of the 50 cases must be paired as near twins where macro growth is similar but K structure differs, or vice versa. Candidate pairs:

- US09 vs DE08 — pandemic support, different asset/labor structures;
- US10 vs JP10 — frontier winners, different social diffusion;
- CN08 vs DE08 — COVID recovery, different production/labor structures;
- CN09 vs JP06 — asset-carrier shifts with different macro regimes;
- KR08 vs US09 — asset inflation + transfers;
- DE10 vs JP02 — weak growth vs structural K;
- US03 vs JP03 — tech leaders under different market/firm concentration;
- CN05 vs US02 — early digital/platform phase;
- KR05 vs DE06 — export champion concentration;
- CN10 vs US10 — AI/advanced-manufacturing concentration under distinct financial systems.

---

# 10｜Replay scoring and defeat criteria

## 10.1 Primary outputs

For each T0, the blind runner must output:

```yaml
regime_candidate
nine_dimension_direction
three_most_binding_dimensions
expected_3y_transitions
expected_5y_transitions
asset_transmission_candidates
falsifiers
unknowns
confidence
```

## 10.2 Scoring

Initial G0 scoring rubric:

- 30% regime discrimination;
- 25% dimension-direction accuracy;
- 15% transition-order accuracy;
- 15% hard-negative rejection;
- 10% calibration of confidence/unknowns;
- 5% asset-transmission sign accuracy.

Asset returns are deliberately underweighted at G0 because YKS0 first must prove structural-state intelligence before investment alpha.

## 10.3 Program-level PASS candidate

The G3 blind replay may only be eligible for `PASS_CANDIDATE` if all are true:

- overall normalized score ≥ 0.70;
- hard-negative false accept rate ≤ 15%;
- near-twin discrimination ≥ 70%;
- no country with score < 0.55;
- unknown/calibration penalty does not exceed 0.10;
- YKS0 exceeds all three baselines on regime discrimination and hard-negative rejection;
- no hindsight leakage incident;
- all replay manifests reproducible from frozen evidence bundles.

These thresholds are **candidate thresholds** and may be modified only before the first hidden reveal, with a versioned human-approved amendment.

---

# 11｜Physical deployment map

## 11.1 GitHub｜Control / Canon / Trial law

### `moonstachain/yuanli-strategy-soul`

Future G1 physical target, not changed in G0:

```text
ontology/
  domains/
    investment/
      k_distribution.yaml
```

It will contain semantic classes and relations only. Existing LinkML root remains the sole semantic source authority.

### `moonstachain/yuanli-invest`

Future operational target:

```text
research/k-shaped-society/
  README.md
  constitution.md
  dimensions/
  metrics/
  hypotheses/
  countries/
  regimes/
  transmission/
  replay/
  settlement/
```

G0 itself writes only this design spec and later, after approval, the implementation plan.

## 11.2 Supabase｜Reality Ledger

No table is created in G0. Proposed logical tables for later gate:

```text
k_metric_registry
k_observation
k_release_vintage
k_state_pit
k_regime_candidate
k_transmission_candidate
k_replay_run
k_replay_result
k_settlement
```

Required temporal columns across factual tables:

`observation_period`, `release_date`, `known_as_of`, `revision_date`.

Supabase is operational Reality storage, not semantic authority.

## 11.3 Hugging Face｜Blind Lab

No dataset/job is created in G0. Proposed later namespace:

```text
yuanli/yks0-k-reality
```

Proposed layout:

```text
raw/
normalized/
pit/
fixtures/
hard-negatives/
near-twins/
benchmark/
manifests/
receipts/
```

HF roles:

- immutable benchmark snapshots;
- blind model runners;
- embedding/classification/clustering experiments;
- leaderboard and ablation;
- reproducible dataset hash publication.

HF outputs remain `EXPERIMENT_CANDIDATE` until imported through settlement.

## 11.4 Notion｜Human Atlas

No page/database is created in G0. Proposed later surfaces:

1. `K Society Cockpit`
2. `9D K Radar`
3. `Five-Country Historical Atlas`
4. `K → Asset Transmission Map`
5. `Reality / Falsifier Review`

Direction is one-way by default:

`GitHub Canon → Projection Contract → Notion`.

Allowed reverse flow is review request only, never direct Canon mutation.

## 11.5 UIG / Brain Context Gateway

YKS0 must reuse existing federated identity/locator/relation/authority patterns.

Candidate relations:

```text
SUPPORTED_BY
CONTRADICTED_BY
DERIVED_FROM
COMPARES_WITH
TRANSMITS_TO
TESTED_BY
SETTLED_BY
SUPERSEDES
```

A YKS0 context bundle must be task-scoped and minimal, containing only the dimensions, evidence, contradictions, and transmission objects required for the question.

---

# 12｜Projection contract

Every human-facing YKS0 projection must display:

- `as_of_date`;
- `known_as_of`;
- evidence coverage;
- unknown count;
- authority state;
- runtime state;
- replay state;
- top contradictions;
- top falsifiers;
- whether the output is `CANDIDATE`, `REPLAY_PASS`, or `SETTLED`.

Forbidden UI language before settlement:

- “China is definitively in KR3”;
- “K regime proves asset X will outperform”;
- “system recommends allocation.”

Allowed language:

- “candidate regime”;
- “evidence currently supports”;
- “replay status pending”;
- “transmission hypothesis”;
- “would be falsified by …”.

---

# 13｜G0 acceptance criteria

YKS0-G0 Written Spec can be Human Accepted only if all are true:

1. YKS0 is clearly bounded as a YIOS0 Knowledge-Spine capability;
2. the nine K dimensions are frozen with exclusions;
3. object model contains no hidden second semantic authority;
4. source grades and PIT rules are explicit;
5. six-regime taxonomy remains replay-defeasible;
6. H1–H8 are pre-registered with future defeat conditions required;
7. five countries and 50 replay cases are frozen;
8. baselines, hard negatives, near twins, and candidate PASS thresholds exist;
9. GitHub/HF/Supabase/Notion/UIG physical roles are separated;
10. G0 mutates no production assets;
11. research cannot silently cross into capital or execution;
12. UNKNOWN remains first-class and may block promotion.

---

# 14｜Deferred to later gates

## G1｜Ontology × Object Model × Metric Registry

Will implement LinkML objects, compiled artifacts, validator/tests, and metric registry.

## G2｜Reality Gateway × Five-Country PIT Dataset

Will collect exact source series, bind release calendars, create PIT-safe evidence bundles, and materialize vintage-aware data.

## G3｜50-Case Pre-Registered Blind Replay

Will freeze exact T0 evidence, run blind models/baselines, reveal outcomes, and issue scientific receipts.

## G4｜K Regime × Asset Transmission Benchmark

Will test incremental value against conventional macro baselines for equities, median stocks/firms, rates, commodities, FX, housing, and selected industry/control-point baskets.

## G5｜UIG × Brain Context Gateway Shadow

Will prove zero-human-routing retrieval of latest, minimal, authority-correct K Context Bundles.

## G6｜Notion × Web Human Atlas

Will create progressive-disclosure human surfaces only after machine truth/replay paths are proven.

---

# 15｜Self-review checklist

- No `TBD`/`TODO` placeholders remain.
- No production writes are authorized.
- No second ontology root is proposed.
- No scalar K score is admitted.
- No country is assumed to follow the same regime sequence.
- No causal claim is promoted solely from correlation.
- No Notion/HF projection has truth authority.
- 50 replay cases are explicitly enumerated.
- Hard negatives and near twins are present.
- Capital and execution remain outside G0 scope.

---

# 16｜Human review decision requested

The Principal is asked to choose one of:

- `ACCEPT_YKS0_G0_WRITTEN_SPEC`
- `REQUEST_YKS0_G0_SPEC_REVISION`
- `REJECT_YKS0_G0`

Only after explicit acceptance may the program proceed to a separate implementation plan. No G1 implementation is authorized by acceptance of this document alone.