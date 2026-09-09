# YMQ4-B3 Dynamic Beta Reality Challenge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute one preregistered 60-month rolling-OLS dynamic-beta challenge against the canonical B2 Gold fixed-beta baseline and settle the YMQ4 core hypothesis without post-result tuning.

**Architecture:** Reuse the B2 PIT panel readback and deterministic transformations. A B3 runner creates 236 strictly prior-window coefficient states, evaluates them on the identical B2 OOS window, compares them to the canonical B2 Reality Gate and four frozen blocks, stores only a non-secret receipt in `runtime.reality_gate_runs`, and freezes a coefficient-state SHA for auditability.

**Tech Stack:** Python 3.12, NumPy, unittest, PostgreSQL/Supabase RPC, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-08-ymq4-b3-dynamic-beta-challenge-design.md`

## Global Constraints

- Panel: `gold_core_monthly_v0.1`; 584 months; 2,336 factor rows; future leakage tolerance 0.
- Reuse B2 transformations unchanged.
- OOS: `2007-01-31 → 2026-08-31`, 236 rows.
- Dynamic estimator: one 60-month rolling OLS with intercept.
- Each OOS coefficient vector uses exactly 60 prior transformed rows ending at `t-1`; no current-target leakage.
- Canonical B2 Reality Gate: `8907b60a-445c-4396-8e51-29e6f36620fb`.
- Victory: overall RMSE lower than B2, overall MAE no higher than B2, positive RMSE incrementality in at least 3/4 frozen blocks.
- No Kalman/TVP/DCC/HMM/regime switching/window search/narrative/B4-B7/portfolio/broker/trading.
- Consume temporary full-run authorization before writing post-result settlement documents.

---

### Task 1: Freeze machine contract and RED tests

**Files:**
- Create: `config/ymq4/gold_b3_dynamic_beta.v0.1.json`
- Create: `tests/test_ymq4_b3.py`

**Interfaces:**
- Consumes: B2 public transformation/model helpers.
- Produces: frozen 60-month rolling contract and tests for chronology, exact OOS count, rolling coefficient recovery, gate logic and forbidden complexity.

- [ ] Encode the fixed window, B2 canonical metrics/gate id, OOS blocks, victory conditions and non-authorizations in config.
- [ ] Write tests importing `scripts.ymq4_b3_dynamic_beta` for exact 236 rolling predictions, 60-row prior windows, no current-target estimation, deterministic coefficient-state hash, B2 gate logic and no complex-model surfaces.
- [ ] Run B3 tests and observe RED because implementation does not exist.

### Task 2: Implement minimal rolling dynamic-beta engine

**Files:**
- Create: `scripts/ymq4_b3_dynamic_beta.py`
- Test: `tests/test_ymq4_b3.py`

**Interfaces:**
- Produces: `rolling_dynamic_predictions(transformed, window=60)`, `coefficient_state_sha(states)`, `compare_to_b2(...)`, and runtime `main()`.

- [ ] Import B2 `validate_panel`, `build_transformed_rows`, `fit_ols`, `predict`, `metrics`, `block_metrics`, OOS boundaries and blocks instead of reimplementing transformations.
- [ ] For every OOS month fit exactly 60 prior transformed rows and reject chronology/window drift.
- [ ] Calculate overall and four-block metrics plus deterministic ordered coefficient-state SHA.
- [ ] Separate physical status `B3_DYNAMIC_BETA_MATERIALIZED_PASS` from scientific label `DYNAMIC_BETA_BEATS_B2` / `DYNAMIC_BETA_DOES_NOT_BEAT_B2`.
- [ ] Run unit tests GREEN.

### Task 3: Supabase baseline-readback and gate contract

**Files:**
- Create: `tests/test_ymq4_b3_contract.py`
- Create: `supabase/migrations/20260908123000_ymq4_b3_dynamic_beta.sql`

**Interfaces:**
- Produces: `ymq4_b3_read_b2_canonical(uuid) returns jsonb`; `ymq4_b3_record_gate(...) returns uuid`.

- [ ] Write RED contract tests requiring service-role-only RPCs, hard-coded `YMQ4-B3`, canonical B2 battle/gate validation, B4-B7/trading false checks, and no direct table grants.
- [ ] Implement the migration with `security definer`, explicit revokes from public/anon/authenticated, and execute grants only to service_role.
- [ ] Apply migration to Supabase project `tbmoimbdhsrltvospwpu`.
- [ ] Run contract tests GREEN.

### Task 4: Validator and workflow

**Files:**
- Create: `scripts/validate_ymq4_b3.py`
- Create: `.github/workflows/ymq4-b3-dynamic-beta.yml`

**Interfaces:**
- Preflight validates frozen contract and both test modules.
- Durable full execution requires explicit `workflow_dispatch(mode=full)`.
- Temporary PR carrier may execute only while `.ymq4/authorizations/YMQ4-B3-FULL` contains `AUTHORIZED_YMQ4_B3_FULL_ONCE`.

- [ ] Validator freezes window=60, B2 gate id/metrics, OOS, victory law and forbidden complexity/trading tokens.
- [ ] Workflow preflight runs validator + tests.
- [ ] Full path requires `YMQ4_SUPABASE_SECRET_KEY`, executes runner, requires physical PASS receipt, and uploads `ymq4-b3-reality-receipt.json`.
- [ ] Verify repository gates and B3 preflight GREEN before any full authorization marker exists.

### Task 5: One physical challenge and independent settlement

**Files:**
- Temporary create/delete: `.ymq4/authorizations/YMQ4-B3-FULL`
- Create after authorization consumption: `docs/architecture/ymq4/YMQ4-B3-REALITY-RECEIPT-v0.1.md`
- Modify after settlement: `config/ymq4/gold_b3_dynamic_beta.v0.1.json`

- [ ] Create one-shot marker only after preflight GREEN.
- [ ] Let the PR carrier run once; wait for physical full completion.
- [ ] Read artifact and independently query Supabase `runtime.reality_gate_runs` for B3.
- [ ] Verify 584/2336/0 input integrity, 236 OOS predictions, 60-row windows, canonical B2 gate, coefficient-state SHA, metrics, four block comparisons and B4-B7/trading false.
- [ ] Delete one-shot marker **before** any settlement-doc/config commit.
- [ ] Verify follow-up CI GREEN and full job skipped.
- [ ] Write canonical Reality Receipt and update config to `reality_proof_pass` with both physical and scientific settlement.
- [ ] Run final repository gates + B3 preflight; full job must remain skipped.
- [ ] Keep B3 PR Draft/Open/Not Merged unless separately authorized.

## Settlement

`YMQ4-B3｜PASS` means the experiment was physically and methodologically valid. Separately freeze either `DYNAMIC_BETA_BEATS_B2` or `DYNAMIC_BETA_DOES_NOT_BEAT_B2`. A negative scientific result is a valid B3 closure and does not authorize a more complex rescue model.