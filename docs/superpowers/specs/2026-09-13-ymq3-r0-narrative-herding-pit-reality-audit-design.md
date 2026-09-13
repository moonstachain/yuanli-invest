# YMQ3-R0｜Narrative × Herding Point-in-Time Reality Audit — Design

Date: 2026-09-13  
Status: `DESIGN_CANDIDATE / WRITTEN_SPEC_REVIEW_REQUIRED`  
Scope: `YMQ3-R0 only`  
Engine role: `MQE3｜Narrative × Herding Engine`  
Architecture approval basis: explicit Human instruction `同意，深度执行：YMQ3-R0｜Narrative × Herding Point-in-Time Reality Audit`  
Design base: protected `main` at `ee497283d0b402e16f43e91abc759355ebe35e5e`  
Dependency: must bind to accepted `YMQ-OS0-G0` object/time/plane contracts before physical execution.

---

## 0｜Mission

YMQ3-R0 is the Genesis Reality Audit for the Yuanli Narrative × Herding Engine.

It does **not** ask whether CSAD is a profitable trading signal.

It asks a harder scientific question:

> **Can a Point-in-Time combination of contemporaneous story diffusion and observable capital-behavior convergence distinguish persistent narrative-driven convergence from generic common-shock / forced-deleveraging co-movement, without hindsight, data revision leakage or post-reveal parameter tuning?**

The strategic problem being tested is:

`Narrative ≠ Herding`

and therefore:

`CSAD↓ / Correlation↑` alone must **not** be promoted to a Narrative claim.

R0 must physically allow the answer to be **NO**.

---

## 1｜Authority boundary

### 1.1 R0 may

- acquire/reconstruct PIT-valid market and text evidence;
- calculate frozen herding/dependency sensors;
- calculate frozen narrative diffusion sensors;
- create weekly `StatePIT` objects;
- compare candidate feature sets against preregistered baselines;
- run leave-one-case-out tests, ablations and hard negatives;
- persist Reality receipts and research settlement;
- return `PHYSICAL_PASS / SCIENTIFIC_NO_GO` when appropriate.

### 1.2 R0 may not

- claim a causal narrative mechanism merely because assets co-move;
- equate CSAD with Narrative;
- tune case windows after observing model performance;
- use modern retrospective articles as PIT model inputs;
- use revised macro data as if known at historical T0;
- rescue a weak result with deep learning, alternative windows or extra factors after reveal;
- generate portfolio weights, position sizes, broker actions or execution authority;
- promote `MQE3` to Canon based on one historical audit.

---

## 2｜R0 scientific model

YMQ3-R0 separates three layers:

```text
Story Layer
Contemporaneous narrative diffusion / breadth / coherence
          │
          ▼
Belief / Positioning Layer
What shared interpretation appears to be forming?
          │
          ▼
Behavior Layer
CSAD / CCK / dependency / flow convergence
```

The candidate explanatory chain is:

`Story → Shared Belief → Shared Positioning → Observable Herding → Repricing`

R0 does not assume every arrow is causal. It tests whether the combined observation stack is more discriminative than behavior alone.

---

## 3｜Pre-registered hypotheses

### `H0｜No Incremental Narrative Information`

Once common-shock, price and volatility controls are included, Story features add no robust out-of-case discrimination beyond Herding-only or Price-only baselines.

### `H1｜Herding Alone Is Non-Specific`

Acute common shocks and forced deleveraging can create CSAD compression / correlation spikes comparable to narrative episodes. Therefore Herding-only must exhibit material hard-negative false positives.

### `H2｜Story × Herding Incrementality` — Primary

The frozen `Story + Herding + Controls` candidate must outperform preregistered Herding-only, Text-only and Price/Common-Shock baselines on out-of-case state discrimination.

### `H3｜Persistence Structure`

Narrative-heavy convergence should, in aggregate, exhibit greater persistence and source breadth than acute mechanical common-shock convergence. Failure to observe this is a valid scientific NO-GO.

### `H4｜Dynamic Dependency Is a State Sensor, Not a Permanent Beta`

Dependency structure should differ materially across case phases, supporting `Beta_{i,t} != Constant` as a state representation. R0 does not claim that such variation produces tradable alpha.

---

## 4｜Historical case set

The six cases are fixed at design time. Exact weekly phase annotations must be frozen in the preregistration file **before feature computation** and may not be moved after model reveal.

| Case | Audit window | Role | Primary interpretation challenge |
|---|---|---|---|
| `C1_DOTCOM` | 1999-01-01 → 2002-12-31 | Narrative-heavy positive | paradigm/story diffusion, reflexive acceleration, saturation, break |
| `C2_GFC` | 2008-01-01 → 2009-12-31 | Acute shock hard negative / mixed | co-movement from funding stress and deleveraging can mimic herding |
| `C3_CHINA_LEVERAGE` | 2014-07-01 → 2016-02-29 | Narrative/reflexive positive | leverage + policy + wealth narrative → convergence → reversal |
| `C4_COVID` | 2020-01-01 → 2020-12-31 | Acute common-shock hard negative / mixed | one external shock can compress cross-asset behavior without a slow narrative epidemic |
| `C5_INFLATION` | 2021-01-01 → 2023-06-30 | Mixed regime case | inflation/commodities/rates narrative intertwined with physical Reality |
| `C6_AI` | 2022-11-01 → 2026-08-31 | Narrative-heavy positive | AI story diffusion, cross-asset reclassification and crowding |

R0 is **not** allowed to drop a difficult case because the candidate performs poorly.

### 4.1 Case labels

Weekly phase labels use the frozen state vocabulary:

- `D0_DISPERSED`
- `D1_AGGREGATING`
- `D2_REFLEXIVE_ACCELERATION`
- `D3_CROWDED_SATURATION`
- `D4_BREAK`

Each label requires an annotation evidence packet independent of the candidate model outputs. Labels are research annotations, not ground-truth laws; their uncertainty must remain visible.

### 4.2 Cause tags

A second orthogonal tag records the dominant audit challenge:

- `NARRATIVE_HEAVY`
- `COMMON_SHOCK`
- `FORCED_DELEVERAGING`
- `MIXED_REALITY_NARRATIVE`

The state label and cause tag must not be collapsed into one variable.

---

## 5｜Asset universe and coverage law

Core asset species:

1. `US_EQ` — broad U.S. equity
2. `CN_EQ` — broad China equity
3. `UST` — U.S. Treasury rate/return proxy
4. `GOLD`
5. `COPPER`
6. `USD` — broad dollar proxy

### 5.1 Coverage rule

R0 does not fabricate historical coverage.

For cases where a trustworthy PIT-valid `CN_EQ` series is unavailable or semantically inappropriate, that asset is marked `NOT_REQUIRED_FOR_CASE` rather than backfilled from a later-created benchmark.

Minimum behavioral panel:

- `C1`: US_EQ, UST, GOLD, COPPER, USD required; CN_EQ optional.
- `C2`: US_EQ, UST, GOLD, COPPER, USD required; CN_EQ optional if authority threshold is met.
- `C3–C6`: all six required unless a documented source-authority failure makes the case `INDETERMINATE`.

Any asset substitution requires a versioned source/series contract and cannot occur after model reveal.

---

## 6｜PIT source authority and text law

### 6.1 Source tiers

R0 distinguishes:

- `T1_OFFICIAL_PRIMARY` — official releases, primary filings, primary market/fix data where obtainable.
- `T2_CONTEMPORANEOUS_ARCHIVE` — date-proven contemporaneous institutional/news/archive source.
- `T3_ATTENTION_PROXY` — search/attention indices only when historical availability semantics can be reconstructed.
- `T4_RETROSPECTIVE` — modern retrospective history; permitted for audit commentary/annotation support, forbidden as PIT model input.

### 6.2 Text evidence rule

A document can enter weekly narrative features only if:

`publication_available_at <= week_end`

and the source snapshot/provenance is retained.

If source archives cannot prove publication time or licensing/availability prevents reproducible ingestion:

`TEXT_EVIDENCE_STATUS = UNKNOWN`

R0 must not fill the gap with LLM-generated synthetic history.

### 6.3 Minimum multimodal coverage

Behavior-only analysis may cover all six cases.

The primary `Story + Herding` incrementality claim requires at least **four** complete case blocks with acceptable text provenance, including:

- at least two narrative-heavy cases;
- at least one acute shock hard negative.

If this minimum is not met:

`FULL_MULTIMODAL_AUDIT = INDETERMINATE`

while the physical data/replay audit may still PASS.

---

## 7｜Behavior/Herding sensor contract

R0 behavior sensors are frozen before reveal.

### 7.1 Daily return scaling

For asset `i` on day `t`:

`r_i,t = log(P_i,t / P_i,t-1)`

To reduce domination by structurally high-volatility assets:

`sigma_i,t-1 = realized volatility from the previous 63 valid trading observations only`

`zret_i,t = r_i,t / sigma_i,t-1`

Minimum trailing observations: `40`.

Current-day return is never used to estimate its own scaling volatility.

### 7.2 Cross-asset CSAD

`CSAD_t = mean_i |zret_i,t - mean_j(zret_j,t)|`

Weekly features:

- median daily CSAD;
- CSAD percentile using trailing-only history;
- `ΔCSAD`;
- `Δ²CSAD`;
- count of days below trailing 20th percentile.

Low CSAD is interpreted only as **behavioral convergence**.

### 7.3 CCK sensor

A frozen rolling nonlinear dispersion regression estimates whether dispersion compresses disproportionately during large common moves.

CCK outputs are secondary sensors; the regression is not allowed to define Narrative on its own.

### 7.4 Dependency sensors

At minimum:

- trailing pairwise dependency matrix;
- average absolute pairwise correlation;
- dependency network density above a frozen threshold.

DCC may be included as a preregistered secondary candidate if deterministic implementation and dependency versions are frozen before execution. R0 scientific validity may not depend on DCC being available.

---

## 8｜Story/Narrative sensor contract

Narrative features are computed weekly from PIT-valid contemporaneous documents.

Frozen feature families:

1. **Topic Share** — share of corpus assigned to the target narrative cluster.
2. **Source Breadth** — number/share of independent source classes carrying the narrative.
3. **Narrative Concentration** — topic HHI / inverse entropy.
4. **Semantic Coherence** — within-cluster coherence relative to trailing corpus.
5. **Novelty** — distance from the trailing-only narrative baseline.
6. **Counter-Narrative Share** — share of documents expressing an explicit competing narrative.
7. **Diffusion Velocity** — first difference of topic share/breadth.
8. **Diffusion Acceleration** — second difference.

### 8.1 Model/embedding law

If embeddings/LLMs are used for historical text classification:

- model/revision must be pinned;
- prompts/label ontology must be versioned;
- the same model is applied to all historical text in a run;
- modern model knowledge is allowed only as a deterministic classifier over **historical documents**, not as a source of historical facts;
- no generated narrative text enters evidence.

### 8.2 Narrative identity

Narrative cluster definitions must be frozen before model scoring and must not be renamed after seeing returns.

---

## 9｜Control variables

R0 includes controls specifically to challenge the Narrative explanation.

Minimum weekly controls:

- broad absolute market move;
- realized volatility;
- volatility-of-volatility where available;
- USD/common global factor;
- rate shock proxy;
- liquidity/funding-stress proxy where PIT-valid;
- market breadth/dispersion baseline.

The purpose is not to build the best forecasting model. The purpose is to test whether Story × Herding contributes information beyond mechanical common shocks.

---

## 10｜Frozen baseline stack

Four baselines and one candidate are evaluated with the same case folds and labels.

### `B0｜Price/Vol Only`

Price trend, absolute move, volatility and breadth only.

### `B1｜Herding Only`

CSAD/CCK/dependency features only.

### `B2｜Story Only`

Text narrative features only.

### `B3｜Common-Shock Controls`

Macro/liquidity/common-factor controls + Price/Vol, without Story/Herding.

### `C1｜Story + Herding + Controls` — Candidate

Frozen union of B1 + B2 + B3 features.

No feature selection is performed after reveal.

---

## 11｜Frozen evaluation method

### 11.1 Unit of evaluation

Weekly `StatePIT` rows.

### 11.2 Cross-case generalization

Use **leave-one-case-out** evaluation.

For each eligible held-out case:

- train preprocessing/model on all other eligible cases;
- compute normalization parameters from training data only;
- freeze the model;
- score the held-out case;
- never fit on weeks from the held-out case.

### 11.3 Frozen classifier

R0 uses one simple interpretable multiclass classifier:

- multinomial logistic regression;
- L2 regularization;
- `C = 1.0`;
- class-weight balanced;
- max iterations fixed in config;
- no hyperparameter search.

If the approved runtime cannot provide the dependency reproducibly, an equivalent deterministic linear implementation may be used only if frozen before any R0 outcome reveal.

### 11.4 Primary metrics

Across held-out predictions:

- Macro F1;
- Balanced Accuracy;
- hard-negative false-positive rate for `D1/D2/D3` narrative-convergence states during acute common-shock blocks;
- per-case Macro F1;
- confusion matrix.

### 11.5 Secondary metrics

- state-transition order consistency;
- persistence of D1/D2/D3 episodes;
- narrative breadth before/during herding persistence;
- dependency-network change statistics;
- lead/lag diagnostics reported descriptively only.

No trading-return metric is a primary R0 success criterion.

---

## 12｜Primary scientific gate

`STORY_HERDING_INCREMENTAL_PASS` requires all of the following on the eligible multimodal case set:

1. candidate Macro F1 > each of B0, B1, B2 and B3;
2. candidate Balanced Accuracy > each of B0, B1, B2 and B3;
3. candidate improves Macro F1 versus `B1 Herding Only` in at least `4` eligible case blocks, or in every eligible block if fewer than 4 multimodal blocks exist but the minimum four-case coverage requirement is exactly met;
4. hard-negative false-positive rate for narrative-convergence states is `<= 20%`;
5. zero PIT leakage violations;
6. no post-reveal case/window/feature/model changes.

If any gate fails:

`STORY_HERDING_DOES_NOT_CLEAR_R0`

This is a valid scientific result.

### 12.1 Integrity settlement

Independent of the scientific result:

`R0_MATERIALIZED_PASS` requires:

- case windows exactly match preregistration;
- all used documents/observations carry PIT provenance;
- asset coverage rules are obeyed;
- feature hashes are reproducible;
- fold assignments are deterministic;
- physical run/receipt readback agrees;
- no future leakage is found.

Therefore valid outcomes include:

- `PHYSICAL_PASS / SCIENTIFIC_PASS`
- `PHYSICAL_PASS / SCIENTIFIC_NO_GO`
- `PHYSICAL_PASS / SCIENTIFIC_INDETERMINATE`
- `PHYSICAL_FAIL`

A single ambiguous `PASS` is forbidden.

---

## 13｜Ablation matrix

R0 must execute these frozen ablations:

1. remove Story features;
2. remove Herding features;
3. remove common-shock controls;
4. remove dependency sensors, retain CSAD only;
5. remove CSAD, retain dependency sensors;
6. remove counter-narrative features;
7. use only Level features, removing `Δ/Δ²`.

The aim is not to find the best subset after reveal. The aim is to understand what actually contributes.

---

## 14｜Hard negatives

R0 pre-registers two classes of hard negatives.

### HN-A｜Acute common shock

Blocks inside GFC/COVID in which cross-asset co-movement is dominated by immediate shared shock/funding stress rather than slow story diffusion.

Expected challenge:

`Herding↑` may occur without the candidate having the right to call it narrative-driven convergence.

### HN-B｜Forced deleveraging / liquidity cascade

Blocks with rapid correlation convergence, volatility spike and funding stress.

Expected challenge:

Behavioral convergence can be mechanically induced.

Hard-negative block boundaries must be frozen in the preregistration config before model execution.

---

## 15｜State output

R0 may produce weekly low-authority state objects containing:

```text
NarrativeState
HerdingState
DependencyState
ControlShockState
CompositeAuditState
Uncertainty
EvidenceRefs
```

`CompositeAuditState` may use D0–D4 vocabulary only as a research-state estimate.

It is not a Market Clock Canon state and carries no Capital Authority.

---

## 16｜Expected implementation artifacts after Written Spec acceptance

```text
docs/architecture/ymq3/
├── YMQ3-R0-PREREGISTRATION-v0.1.md
├── YMQ3-R0-CASE-ANNOTATION-CARD-v0.1.md
├── YMQ3-R0-REALITY-RECEIPT-v0.1.md
└── YMQ3-R0-HUMAN-REVIEW-CARD-v0.1.md

config/ymq3/
├── ymq3_r0_preregistration.v0.1.json
├── ymq3_r0_asset_registry.v0.1.json
├── ymq3_r0_case_annotations.v0.1.json
└── ymq3_r0_feature_contract.v0.1.json

scripts/
├── ymq3_r0_build_pit_panel.py
├── ymq3_r0_herding.py
├── ymq3_r0_narrative.py
├── ymq3_r0_evaluate.py
└── validate_ymq3_r0.py

tests/
└── test_ymq3_r0.py

.github/workflows/
└── ymq3-r0-reality-audit.yml
```

Possible Evidence/Runtime migrations and HF Job adapters are implementation details to be specified in the implementation plan. They must reuse YMQ-OS0 contracts rather than creating a parallel ontology.

---

## 17｜HF / remote-runner contract

R0 is runner-independent.

Preferred future carrier:

`GitHub frozen contract → HF Job/container → Evidence/Runtime Truth Plane → independent readback → GitHub receipt`

Required runner properties:

- exact Git SHA;
- immutable input revisions;
- no interactive post-reveal tuning;
- secrets remain outside artifacts/logs;
- output hashes written to receipt;
- repeat run can reproduce the same deterministic feature artifacts within defined numerical tolerance.

HF Dataset/Model repositories are optional projections/artifact stores. R0 cannot fail scientifically merely because HF write scope is unavailable; it must be possible to run the same frozen container contract on another authorized runner.

---

## 18｜Data-leakage kill gates

Immediate `PHYSICAL_FAIL` if any occurs:

- a macro value uses a vintage released after the evaluation week;
- a text document was published after its assigned week;
- normalization uses future observations;
- phase labels are moved after feature/model reveal;
- feature/model hyperparameters are tuned against held-out case performance;
- modern retrospective text enters the feature corpus;
- a future index constituent list is used to reconstruct past breadth without point-in-time membership handling;
- a missing historical value is filled from a later revision without an explicit preregistered rule.

---

## 19｜Scientific non-claims

Even if R0 passes, it does **not** prove:

- narratives cause asset prices;
- every low-CSAD regime is narrative-driven;
- Story × Herding predicts returns;
- the five D0–D4 states are universal market laws;
- the candidate generalizes to every country/asset/time period;
- any portfolio should trade the signal.

A PASS means only that the frozen candidate showed incremental historical state-discrimination under this preregistered audit.

---

## 20｜Next-stage law

If R0 is `PHYSICAL_PASS / SCIENTIFIC_PASS`, the next admissible battle is a separately authorized shadow/live-state replication, not immediate capital use.

Suggested next stage:

`YMQ3-R1｜Forward Shadow Narrative-Herding State Runtime`

If R0 is `PHYSICAL_PASS / SCIENTIFIC_NO_GO`, the next action is **not** automatic model rescue. The LearningDelta must identify which hypothesis failed and any new candidate requires a fresh preregistration.

If R0 is `INDETERMINATE` due to text authority/coverage, the next battle is a Data Authority / Corpus Recovery battle rather than a model-complexity battle.

---

## 21｜Strategic closure

The R0 test is intentionally hostile to the attractive story that “Narrative can now be quantified.”

The engine earns admission only if it can survive the stronger claim:

> **When markets suddenly move together, can the system show — using only what was knowable at that time — whether a shared story was actually diffusing, or whether everyone was merely being hit by the same shock?**

That is the minimum Reality standard before Narrative × Herding can become a trusted Yuanli research capability.
