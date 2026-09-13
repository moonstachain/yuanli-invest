# YMQ3-R0｜Narrative × Herding Point-in-Time Reality Audit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Date:** 2026-09-13  
**Repository:** `moonstachain/yuanli-invest`  
**Current design branch:** `ymq-os0-g0-ymq3-r0-written-spec`  
**Design authority:** `docs/superpowers/specs/2026-09-13-ymq3-r0-narrative-herding-pit-reality-audit-design.md`  
**Dependency:** accepted/frozen `YMQ-OS0-G0` object, PIT and physical-plane contracts  
**Execution mode:** preregistration-first + TDD + PIT fail-closed + leave-one-case-out + exact-head physical Reality receipts

## Goal

Build and physically audit the first `MQE3｜Narrative × Herding Engine` candidate without conflating behavioral convergence with Narrative. The experiment must test whether contemporaneous Story features add robust out-of-case information beyond Herding-only, Price/Vol, and Common-Shock controls across six frozen historical cases.

The required scientific possibility set includes `SCIENTIFIC_PASS`, `SCIENTIFIC_NO_GO`, and `SCIENTIFIC_INDETERMINATE`. A physically valid experiment that rejects the hypothesis is a successful Reality process, not a failed project.

## Architecture

R0 uses the G0 object chain:

`SourceSnapshot → ObservationPIT → FeaturePIT → StatePIT → CapabilityRun → ResearchSettlement`

with a weekly synchronized behavior clock, independently frozen historical annotations, PIT-valid contemporaneous text, four preregistered baselines, one simple multinomial classifier, frozen ablations/hard negatives, and independent Supabase/artifact readback.

Hugging Face Jobs is the preferred replaceable compute runner for the full historical experiment. GitHub remains Law/Control; Supabase/Object Storage remains Evidence/Runtime Truth. HF output never becomes Canon by itself.

## Tech Stack

- Python `3.12`
- NumPy `2.3.2`
- JSON Schema / existing YMQ-OS0 contracts
- `scikit-learn==1.8.0` for frozen multinomial LogisticRegression and metrics
- Python stdlib `unittest`, `hashlib`, `json`, `datetime`, `statistics`, `pathlib`
- PostgreSQL / Supabase + object storage
- GitHub Actions preflight
- Hugging Face Jobs/container runtime for the full compute run when credentials/authority are proven

`scikit-learn==1.8.0` is deliberately pinned before any R0 feature/outcome reveal. No library version upgrade is allowed mid-audit without preregistration revision and full rerun from raw PIT inputs.

## Global Constraints

- `Narrative != Herding`.
- Low CSAD/correlation compression is behavior evidence only.
- No case/date/feature/model/hyperparameter changes after feature/outcome reveal.
- Six case windows remain non-overlapping.
- Current held-out case never contributes observations, normalization statistics, labels-by-feature inspection, or model fitting to its own training fold.
- Modern retrospective text is never a PIT feature input.
- No synthetic LLM-generated historical evidence.
- Narrative labels are frozen independently of candidate feature values/predictions.
- The same pinned text-classification/embedding contract applies across all cases in one run.
- Trading return is not a primary metric.
- R0 produces no capital weights, position sizing, broker action, VeighNa invocation, paper/live order, or real-capital authority.
- If acceptable text provenance covers fewer than four required multimodal cases, the primary audit settles `SCIENTIFIC_INDETERMINATE` rather than backfilling weak evidence.

---

## Task 1｜Freeze preregistration, cases, annotations and source authority before feature computation

**Files:**
- Create: `config/ymq3/r0_preregistration.v0.1.json`
- Create: `config/ymq3/r0_case_annotations.v0.1.json`
- Create: `config/ymq3/r0_source_authority.v0.1.json`
- Create: `config/ymq3/r0_text_model_contract.v0.1.json`
- Create: `tests/test_ymq3_r0_preregistration.py`
- Create: `scripts/validate_ymq3_r0_preregistration.py`

**Interfaces:**
- Consumes accepted Written Spec and accepted G0 object/PIT contract.
- Produces an immutable experiment law for all later tasks.

- [ ] **Step 1: Write RED tests first.** Require exact case windows:
  - `C1_DOTCOM: 1999-01-01..2002-12-31`
  - `C2_GFC: 2008-01-01..2009-12-31`
  - `C3_CHINA_LEVERAGE: 2014-07-01..2016-02-29`
  - `C4_COVID: 2020-01-01..2020-12-31`
  - `C5_INFLATION: 2021-01-01..2022-10-31`
  - `C6_AI: 2022-11-01..2026-08-31`

- [ ] **Step 2: Test zero overlap mechanically.** Any scored calendar week assigned to more than one case is invalid.

```python
def test_scored_case_windows_do_not_overlap(self):
    seen = set()
    for case in config["cases"]:
        for week in enumerate_scored_weeks(case):
            self.assertNotIn(week, seen)
            seen.add(week)
```

- [ ] **Step 3: Freeze state labels and cause tags.** State vocabulary is exactly `D0_DISPERSED`, `D1_AGGREGATING`, `D2_REFLEXIVE_ACCELERATION`, `D3_CROWDED_SATURATION`, `D4_BREAK`; cause tags remain orthogonal.

- [ ] **Step 4: Freeze phase boundaries in `r0_case_annotations.v0.1.json` using an evidence packet independent of candidate feature values.** Every annotated phase must carry `case_id`, `start_week`, `end_week`, `state_label`, `cause_tag`, `annotation_evidence_refs`, `annotation_uncertainty`.

- [ ] **Step 5: Freeze asset coverage and substitution law.** C1/C2 require US_EQ, UST, GOLD, COPPER, USD; CN_EQ optional. C3–C6 require all six unless source-authority failure explicitly makes the case indeterminate. No substitution after reveal.

- [ ] **Step 6: Freeze source tiers and text law.** `T4_RETROSPECTIVE` must be rejected as feature input. `publication_available_at <= week_end` is mandatory.

- [ ] **Step 7: Freeze model law and scientific gate.** Encode B0/B1/B2/B3/C1 feature groups, seven ablations, hard negatives, LOCO folds, classifier parameters, metrics and exact PASS/NO-GO/INDETERMINATE rules. Classifier config is frozen as:

```json
{
  "algorithm": "multinomial_logistic_regression",
  "standardizer": "StandardScaler_train_only",
  "penalty": "l2",
  "C": 1.0,
  "solver": "lbfgs",
  "class_weight": "balanced",
  "max_iter": 2000,
  "tol": 0.0001,
  "hyperparameter_search": false
}
```

- [ ] **Step 8: Pin the text model contract before corpus scoring.** Contract includes provider/model/revision, prompt/label ontology SHA, deterministic settings, and `generated_historical_facts_allowed=false`. If the final selected provider differs, revise preregistration **before** any corpus score is computed.

- [ ] **Step 9: Run:**

```bash
python -m unittest tests.test_ymq3_r0_preregistration -v
python scripts/validate_ymq3_r0_preregistration.py
```

- [ ] **Step 10: Commit preregistration before any feature computation.** Record preregistration commit SHA in all later runs.

---

## Task 2｜Build the Source Authority Inventory and stop if the evidence is not good enough

**Files:**
- Extend: `config/ymq3/r0_source_authority.v0.1.json`
- Create: `docs/architecture/ymq3/YMQ3-R0-SOURCE-AUTHORITY-AUDIT-v0.1.md`
- Create: `tests/test_ymq3_r0_source_authority.py`

**Interfaces:**
- Does not yet calculate Narrative scores.
- Establishes whether each market/text source can legally and scientifically participate in PIT replay.

- [ ] **Step 1: Inventory each required asset series with:** provider, exact series/instrument, source tier, timezone/session, price/fix definition, adjustment rule, first usable date, availability semantics, license class, storage policy, and fallback status.

- [ ] **Step 2: Inventory historical text corpora by case.** Each source family must document publication timestamp authority, archive locator strategy, licensing/storage allowance, source class and coverage period.

- [ ] **Step 3: Classify every source as `ADMIT`, `ANNOTATION_ONLY`, `UNKNOWN_DENY`, or `REJECT`.** Never convert “probably historical” into PIT-qualified.

- [ ] **Step 4: Calculate case coverage before ingestion.** The primary multimodal audit is eligible only if at least four cases have acceptable text coverage, including at least two narrative-heavy cases and one acute-shock hard negative.

- [ ] **Step 5: If coverage is below threshold, freeze:**

```text
FULL_MULTIMODAL_AUDIT = INDETERMINATE
```

Behavior-only work may continue for infrastructure validation, but no Story×Herding incrementality PASS claim is allowed.

- [ ] **Step 6: Run source-authority tests and commit the audit before raw ingestion.**

---

## Task 3｜Materialize R0 PIT storage contracts without duplicating G0/YMQ4 truth tables

**Files:**
- Create: `supabase/migrations/20260913100000_ymq3_r0_panels.sql`
- Create: `tests/test_ymq3_r0_sql_contract.py`

**Interfaces:**
- Reuse `evidence.sources`, `evidence.source_snapshots`, `pit.observations`, G0 `pit.features`, and runtime run/settlement tables.
- Add R0-specific indexes/projections only where generic objects cannot represent corpus/panel membership cleanly.

**R0-specific structures:**
- `pit.narrative_documents` — document identity/index pointing to immutable source snapshot; stores publication/availability clocks, source class and case membership, not unrestricted copyrighted body text.
- `pit.case_annotations` — frozen weekly labels/cause tags/evidence refs.
- `pit.r0_weekly_panel_membership` — which asset/doc facts were eligible for which canonical week.

- [ ] **Step 1: Write SQL contract tests before migration.** Require foreign keys to existing evidence/PIT truth objects, RLS on, and no public/anon/authenticated write policy.

- [ ] **Step 2: Enforce `publication_available_at` and canonical week as explicit columns; never infer from ingestion time alone.**

- [ ] **Step 3: Do not store full licensed article text in Postgres unless the source contract explicitly permits it.** Store immutable payload in authorized object storage/NAS and retain hash/locator in Evidence Plane.

- [ ] **Step 4: Migration application is a later physical action.** Committing SQL does not prove runtime existence.

---

## Task 4｜TDD the weekly synchronized Behavior/Herding engine

**Files:**
- Create: `scripts/ymq3_r0_behavior.py`
- Create: `tests/test_ymq3_r0_behavior.py`

**Interfaces:**

```python
canonical_week_end(ts) -> datetime
weekly_last_valid(rows, week_end) -> dict
weekly_log_returns(prices) -> list[float]
trailing_scaled_returns(returns, window=52, min_periods=26) -> list
csad(zreturns_by_asset) -> float
rolling_percentile(history, value, lookback=104, min_periods=52) -> float | None
cck_beta2(history, lookback=104, min_periods=52) -> dict
rolling_dependency(history, lookback=26, min_periods=13, threshold=0.50) -> dict
```

- [ ] **Step 1: Write RED tests for global synchronization.** Friday `23:59:59 UTC` is canonical boundary; last valid local close/fix on or before boundary is used. Multi-week silent forward fill must raise/fail closed.

- [ ] **Step 2: Test current-week exclusion.** The return for week W must never enter W’s own volatility, CCK or dependency estimation window.

- [ ] **Step 3: Implement weekly scaling:** prior 52 valid weekly returns, minimum 26.

- [ ] **Step 4: Implement CSAD and trailing percentile:** previous 104 valid weeks only, minimum 52, plus `ΔCSAD`, `Δ²CSAD` and four-week low-percentile share.

- [ ] **Step 5: Implement CCK with `numpy.linalg.lstsq`:**

```text
CSAD = alpha + beta1*abs(M) + beta2*M^2 + error
```

Fit on prior 104 valid weekly observations only. Return beta2, residual diagnostics and sample count. A negative beta2 remains a sensor, never a Narrative verdict.

- [ ] **Step 6: Implement dependency state:** previous 26 valid weekly z-returns, minimum 13; return pairwise correlation matrix, average absolute correlation, density for `abs(corr) >= 0.50`, and first difference.

- [ ] **Step 7: Run:**

```bash
python -m unittest tests.test_ymq3_r0_behavior -v
```

---

## Task 5｜TDD the Story/Narrative feature engine over PIT-valid historical documents

**Files:**
- Create: `scripts/ymq3_r0_story.py`
- Create: `tests/test_ymq3_r0_story.py`

**Input contract:** each scored document row minimally contains:

```text
doc_id
case_id
source_snapshot_id
source_class
publication_available_at
week_end
topic_membership_or_score
counter_narrative_flag
embedding_or_embedding_ref
model_contract_hash
```

**Interfaces:**

```python
assert_document_pit(doc) -> None
topic_share(docs) -> float
source_breadth(docs) -> dict
narrative_concentration(docs) -> dict
semantic_coherence(docs) -> float | None
novelty(current_docs, trailing_docs) -> float | None
counter_narrative_share(docs) -> float
first_second_differences(series) -> tuple[list, list]
```

- [ ] **Step 1: Write RED tests proving retrospective/future documents are rejected.** `publication_available_at > week_end` must fail.

- [ ] **Step 2: Test that LLM/model-generated text cannot masquerade as evidence.** Rows marked `synthetic_generated=true` are rejected from Story features.

- [ ] **Step 3: Implement Topic Share, Source Breadth, HHI/inverse entropy, Semantic Coherence, Novelty, Counter-Narrative Share, Diffusion Velocity and Diffusion Acceleration exactly as preregistered.**

- [ ] **Step 4: All trailing baselines must use only weeks strictly before the scored week.**

- [ ] **Step 5: Pin model contract hash into every classified document/weekly feature.** Mixed model revisions inside one canonical run fail closed.

- [ ] **Step 6: Run:**

```bash
python -m unittest tests.test_ymq3_r0_story -v
```

---

## Task 6｜Compile the weekly R0 dataset, controls and leak-proof LOCO folds

**Files:**
- Create: `scripts/ymq3_r0_dataset.py`
- Create: `tests/test_ymq3_r0_dataset.py`

**Interfaces:**

```python
build_weekly_rows(...) -> list[dict]
validate_case_coverage(rows, prereg) -> dict
build_feature_groups(rows, prereg) -> dict
leave_one_case_out(rows, eligible_cases) -> list[Fold]
assert_no_fold_leakage(folds) -> None
```

- [ ] **Step 1: Join behavior, Story and controls only by canonical week and PIT-qualified refs.** Missing components remain explicit; do not impute from future observations.

- [ ] **Step 2: Materialize controls:** broad absolute market move, realized volatility, vol-of-vol when available, USD/common global factor, rate shock, PIT-valid funding/liquidity stress, market breadth/dispersion.

- [ ] **Step 3: Enforce coverage law by case.** C1/C2 optional CN_EQ; C3–C6 all six unless case becomes indeterminate through source-authority failure.

- [ ] **Step 4: Build LOCO folds over non-overlapping scored weeks.** Training normalization statistics are derived only from training cases. Warm-up history may support a held-out case’s trailing sensors but never becomes a scored training row under another case ID.

- [ ] **Step 5: Add explicit leakage tests:**
  - no identical scored week in train and test;
  - no held-out case annotation row in train;
  - no `known_as_of > week_end` input;
  - no future normalization statistic;
  - no future index-constituent membership reconstruction.

- [ ] **Step 6: Run:**

```bash
python -m unittest tests.test_ymq3_r0_dataset -v
```

---

## Task 7｜Implement the frozen multinomial classifier and evaluation metrics

**Files:**
- Modify: `requirements-dev.txt` to add exactly `scikit-learn==1.8.0`
- Create: `scripts/ymq3_r0_model.py`
- Create: `tests/test_ymq3_r0_model.py`

**Interfaces:**

```python
fit_fold(train_rows, feature_names, prereg) -> FrozenFoldModel
score_fold(model, test_rows) -> dict
macro_f1(y_true, y_pred) -> float
balanced_accuracy(y_true, y_pred) -> float
hard_negative_fpr(rows, predictions) -> float
```

- [ ] **Step 1: Write deterministic synthetic tests first.** Tests run the same fixture twice and require identical predictions/metrics.

- [ ] **Step 2: Use `StandardScaler` fit on train only.** Test set uses frozen train mean/scale.

- [ ] **Step 3: Use `LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', class_weight='balanced', max_iter=2000, tol=1e-4)`.** Do not add hyperparameter search, CV tuning or feature selection.

- [ ] **Step 4: Fail closed if a training fold lacks enough state classes for the preregistered multiclass experiment or if the solver emits a convergence failure.** Do not silently collapse labels, raise iterations or alter tolerance after reveal.

- [ ] **Step 5: Return model metadata including sklearn version, feature order, scaler statistics and coefficient hash so the fold is reproducible.**

- [ ] **Step 6: Run:**

```bash
python -m unittest tests.test_ymq3_r0_model -v
```

If `scikit-learn==1.8.0` cannot install in the approved Python 3.12 runner, stop before any real R0 feature/outcome reveal and revise the preregistration/version contract. Do not substitute a new algorithm after seeing case results.

---

## Task 8｜Implement the baseline/ablation/hard-negative audit and scientific settlement

**Files:**
- Create: `scripts/ymq3_r0_audit.py`
- Create: `tests/test_ymq3_r0_audit.py`

**Interfaces:**

```python
run_baseline(name, rows, folds, prereg) -> dict
run_candidate(rows, folds, prereg) -> dict
run_ablations(rows, folds, prereg) -> dict
run_hard_negatives(rows, predictions, prereg) -> dict
settle_physical(integrity) -> str
settle_science(results, coverage, integrity, prereg) -> str
build_research_settlement(...) -> dict
```

- [ ] **Step 1: Evaluate B0/B1/B2/B3/C1 on identical eligible folds.** No model-specific case dropping.

- [ ] **Step 2: Compute aggregate Macro F1, Balanced Accuracy, per-case Macro F1, confusion matrices and hard-negative FPR.**

- [ ] **Step 3: Execute all seven frozen ablations:** Story removed; Herding removed; controls removed; CSAD-only; dependency-only; counter-narrative removed; Level-only/no Δ/Δ².

- [ ] **Step 4: Execute frozen hard-negative blocks.** GFC/COVID/common-shock blocks must challenge false attribution of convergence to Narrative.

- [ ] **Step 5: Encode the scientific gate literally:** candidate must beat all four baselines on aggregate Macro F1 and Balanced Accuracy; beat Herding-only per-case Macro F1 in at least four eligible cases (all four if exactly four qualify); hard-negative FPR <=20%; zero leakage; zero post-reveal changes.

- [ ] **Step 6: Encode valid settlement states separately:**

```text
PHYSICAL_PASS / SCIENTIFIC_PASS
PHYSICAL_PASS / SCIENTIFIC_NO_GO
PHYSICAL_PASS / SCIENTIFIC_INDETERMINATE
PHYSICAL_FAIL
```

Authority remains `NONE/AWAITING_HUMAN_REVIEW` regardless of scientific result.

- [ ] **Step 7: Unit-test all four settlement branches using synthetic metrics.** A scientific NO-GO must not become `PHYSICAL_FAIL`; insufficient text coverage must become INDETERMINATE.

---

## Task 9｜Build provider-neutral full-run wrapper, GitHub preflight and HF Jobs path

**Files:**
- Create: `config/ymq3/r0_compute_provider.v0.1.json`
- Create: `scripts/ymq3_r0_job.py`
- Create: `scripts/validate_ymq3_r0.py`
- Create: `.github/workflows/ymq3-r0-reality-audit.yml`
- Create: `tests/test_ymq3_r0_job.py`

**Interfaces:**
- `ymq3_r0_job.py` receives exact preregistration SHA, code SHA, source/panel revisions and output location; produces a non-secret JSON receipt on stdout.
- GitHub Actions PR mode runs only preflight/tests; full physical audit requires an explicit manual authorization path.

- [ ] **Step 1: Validator checks all preregistration hashes, source-authority status, G0 contract version, dependency versions and forbidden authority fields.**

- [ ] **Step 2: GitHub workflow `pull_request` runs preflight only:** install pinned dependencies, validator, all YMQ3 tests, no external writes.

- [ ] **Step 3: Add `workflow_dispatch` with `mode=preflight|full` but make `full` fail closed unless the required runtime credential/authorization marker exists.** Never trigger expensive/full Reality execution from ordinary PR pushes.

- [ ] **Step 4: HF Jobs remains the preferred compute provider, but do not assume the chat-session OAuth is available inside GitHub Actions.** The current chat identity proves only that an HF account with `jobs` scope exists. Before a full run, separately verify the actual trusted runtime credential and runner identity.

- [ ] **Step 5: Bind the exact Git SHA and preregistration SHA through environment variables rather than free-form placeholders.** The canonical runner invocation is:

```bash
python -m scripts.ymq3_r0_job \
  --prereg-sha "$YMQ3_PREREG_SHA" \
  --git-sha "$GITHUB_SHA" \
  --mode full
```

Both variables must be non-empty and checked against the repository/run metadata before computation starts. Do not expose token values in logs or receipts.

- [ ] **Step 6: Persist runtime receipt to Supabase `runtime.reality_gate_runs` / G0 ResearchSettlement lineage and upload the same non-secret receipt artifact.** Receipt includes input manifest hash, code SHA, prereg SHA, source panel revisions, physical/scientific/authority states, metrics hashes and artifact hash.

---

## Task 10｜Physical Reality Run, independent readback, Human Review Gate

**Files created only after a real run:**
- Create: `docs/architecture/ymq3/YMQ3-R0-REALITY-RECEIPT-v0.1.md`
- Create: `docs/architecture/ymq3/YMQ3-R0-HUMAN-REVIEW-CARD-v0.1.md`

**Preconditions:**
- G0 object/PIT contracts are accepted and stable for the run;
- preregistration commit predates feature/outcome reveal;
- source-authority audit is frozen;
- required market/text evidence is physically accessible under its license;
- Supabase/runtime credential path is authorized;
- HF/container runner identity is proven;
- no later edit has changed cases/features/gates without a preregistration revision.

- [ ] **Step 1: Run a fresh preflight at the exact execution SHA.** Require all tests/validators GREEN.

- [ ] **Step 2: Launch exactly one canonical full Reality Run.** If infrastructure fails before science executes, record fail-closed infrastructure evidence; repair infrastructure only, never scientific thresholds/windows/features after reveal.

- [ ] **Step 3: Independently read back:** exact run id; code/prereg/source revisions; case/fold counts; feature hashes; leakage count; B0–B3/C1 metrics; ablations; hard negatives; settlement states; `trading_action=false`.

- [ ] **Step 4: Compare artifact hash with Supabase receipt.** Any mismatch is `PHYSICAL_FAIL` until explained and rerun under a newly recorded physical run identity.

- [ ] **Step 5: Write Reality Receipt with no rhetorical rescue.** If candidate loses, state `PHYSICAL_PASS / SCIENTIFIC_NO_GO`; if text coverage is insufficient, state `PHYSICAL_PASS / SCIENTIFIC_INDETERMINATE`.

- [ ] **Step 6: Keep PR Draft/Open/Not Merged and create the Human Review Card.** The scientific result itself does not grant Canon authority.

Required next Human decision after a physically settled R0:

`ACCEPT_YMQ3_R0_REALITY_SETTLEMENT`

A later merge/Canon admission, if warranted, must remain separately authorized. R0 never grants Capital Authority.

---

## Dependency and commit discipline

Recommended commit boundaries:

1. preregistration RED/tests;
2. preregistration/config GREEN;
3. source authority audit;
4. SQL contract;
5. behavior engine;
6. Story engine;
7. dataset/leakage compiler;
8. pinned classifier;
9. audit/gate engine;
10. runtime wrapper/preflight;
11. physical receipt/review card after actual execution.

Do not squash away the preregistration-before-reveal chronology before Human Review; the commit history is part of the audit trail.

## Completion evidence

Different claims require different evidence:

- **R0 implementation candidate exists:** exact-head tests/validator GREEN.
- **R0 data plane exists:** independent Supabase/object-storage readback.
- **R0 physically ran:** exact run receipt + artifact/database hash agreement.
- **R0 scientific result:** only the preregistered gate outcome from the canonical run.
- **R0 Canon authority:** separate Human acceptance + any separately authorized merge/admission.

No completion statement may collapse Physical, Scientific and Authority status into one `PASS`.