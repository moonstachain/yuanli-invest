# YMQ4-B2 Fixed Beta Baseline × OOS Incrementality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materialize a frozen Gold fixed-beta benchmark on the DP1-B PIT panel, evaluate it on a fixed 2007–2026 OOS window, persist/read back a Reality Receipt, and freeze the comparison gate for B3.

**Architecture:** A service-role-only public RPC exposes the four-factor DP1-B panel to a GitHub Actions research runner. The runner validates input integrity, creates deterministic monthly transformations, fits one OLS vector on 1978-02 through 2006-12, evaluates the frozen vector and intercept-only null on 2007-01 through 2026-08, then records a non-secret receipt in `runtime.reality_gate_runs` and uploads the same receipt as an artifact.

**Tech Stack:** Python 3.12, NumPy, unittest, PostgreSQL/Supabase RPC, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-08-ymq4-b2-fixed-beta-oos-design.md`

## Global Constraints

- Input panel: `gold_core_monthly_v0.1` only.
- Expected physical input: 584 months, 2,336 rows, four factor rows per month, future leakage 0.
- Train: transformed months `1978-02-28 → 2006-12-31` (347 rows).
- OOS: transformed months `2007-01-31 → 2026-08-31` (236 rows).
- One OLS coefficient vector only; no rolling/TVP/Kalman/regime-switching/feature tuning.
- B2 OOS is temporal coefficient generalization, not a tradable forecasting claim.
- No B3-B7 execution, Canon promotion, portfolio sizing, broker connection, or trading action.

---

### Task 1: Contract tests and configuration

**Files:**
- Create: `config/ymq4/gold_b2_fixed_beta.v0.1.json`
- Create: `tests/test_ymq4_b2.py`

**Interfaces:**
- Consumes: frozen B2 design.
- Produces: machine-readable split/model contract and failing tests for transformations/OLS/metrics.

- [ ] Write config encoding battle, panel id, target/features, transformation names, train/OOS boundaries, integrity expectations, null benchmark, B3 gate blocks, and non-authorizations.
- [ ] Write tests importing `scripts.ymq4_b2_fixed_beta` and covering transformations, exact split counts, synthetic OLS coefficient recovery, metrics, panel-integrity rejection, and absence of dynamic-model behavior.
- [ ] Run `python -m unittest tests.test_ymq4_b2 -v`; expected RED because the implementation module does not yet exist.

### Task 2: Minimal deterministic fixed-beta engine

**Files:**
- Create: `scripts/ymq4_b2_fixed_beta.py`
- Test: `tests/test_ymq4_b2.py`

**Interfaces:**
- Produces: `validate_panel(rows)`, `build_transformed_rows(rows)`, `split_rows(rows)`, `fit_ols(rows)`, `predict(rows, coefficients)`, `metrics(actual, predicted)`, `block_metrics(rows, actual, predicted)`.

- [ ] Implement panel validation and deterministic transformations.
- [ ] Implement one-shot OLS using `numpy.linalg.lstsq`.
- [ ] Implement null baseline, metrics and fixed-block metrics.
- [ ] Run `python -m unittest tests.test_ymq4_b2 -v`; expected GREEN.

### Task 3: Supabase readback and Reality Gate contract

**Files:**
- Create: `supabase/migrations/20260908070000_ymq4_b2_fixed_beta.sql`
- Create: `tests/test_ymq4_b2_contract.py`

**Interfaces:**
- Produces RPC `ymq4_b2_read_panel(text)` returning ordered panel rows and RPC `ymq4_b2_record_gate(...)` recording battle `YMQ4-B2`.

- [ ] Write contract test asserting service-role-only grants, revoked public/anon/authenticated access, exact panel fields, and hard-coded B2 gate identity.
- [ ] Run contract test RED because migration is absent.
- [ ] Implement migration without direct table grants.
- [ ] Apply migration to `yuanli-invest-runtime`.
- [ ] Run contract test GREEN.

### Task 4: Runtime, validator, workflow

**Files:**
- Modify: `scripts/ymq4_b2_fixed_beta.py`
- Create: `scripts/validate_ymq4_b2.py`
- Create: `.github/workflows/ymq4-b2-fixed-beta.yml`

- [ ] Add service-role RPC client and runtime `main()`.
- [ ] Add validator freezing B2 semantics and blocking dynamic/trading tokens.
- [ ] Add workflow with `preflight` and explicit `workflow_dispatch(mode=full)`.
- [ ] Preflight runs validator and both B2 test modules.
- [ ] Full job requires `YMQ4_SUPABASE_SECRET_KEY`, executes B2, requires `B2_BASELINE_MATERIALIZED_PASS`, and uploads `ymq4-b2-reality-receipt.json`.

### Task 5: Physical Reality Run and independent readback

**Files:**
- Create after PASS: `docs/architecture/ymq4/YMQ4-B2-REALITY-RECEIPT-v0.1.md`

- [ ] Verify preflight green.
- [ ] Dispatch explicit `mode=full`.
- [ ] Wait for full completion.
- [ ] Independently query Supabase for B2 gate row and compare with artifact.
- [ ] Verify executed Git SHA, source panel identity, 347/236 split, coefficient vector, OOS metrics, null metrics, block metrics and `b3_b7_executed=false`.
- [ ] Write canonical Reality Receipt and keep PR Draft/Open/Not Merged.

## Settlement

B2 closes as `YMQ4-B2｜PASS` only when `B2_BASELINE_MATERIALIZED_PASS` is physically persisted and independently read back. Separately report whether the fixed-beta model beat the intercept-only null on OOS RMSE. A negative economic result is not a B2 integrity failure.
