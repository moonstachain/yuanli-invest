# YMQ4-DP1-B Gold Historical PIT Backfill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and physically run a fail-closed 1978–2026 monthly Gold core PIT/as-of backfill that stops before B2–B7.

**Architecture:** Extend the DP1-A external Reality Data Plane rather than creating a parallel stack. Fetch institutional/official raw sources, archive immutable payloads to private Supabase S3, normalize source observations, derive a monthly factor panel under explicit measurement regimes, then settle coverage/leakage through `runtime.reality_gate_runs`.

**Tech Stack:** Python 3.12, urllib, boto3, openpyxl, GitHub Actions, Supabase Postgres/RPC/S3, FRED/ALFRED API, World Bank Pink Sheet XLSX.

**Spec:** `docs/superpowers/specs/2026-09-08-ymq4-dp1b-gold-historical-pit-backfill-design.md`

## Global Constraints

- `DATA REVEAL → MODEL FREEZE`.
- DP1-B must not execute or tune B2–B7.
- `future_leakage_tolerance = 0`.
- replay-window core coverage threshold = `0.80`.
- raw payloads and credentials never enter public Git.
- reconstructed market evidence retains `PIT_MARKET_RECONSTRUCTED` or `HISTORICAL_PROXY` status.

---

### Task 1: Historical panel contract and tests

**Files:**
- Create: `tests/test_ymq4_dp1b.py`
- Create: `config/ymq4/gold_dp1b_backfill.v0.1.json`

**Interfaces:**
- Produces: `month_ends(start, end)`, `latest_on_or_before(rows, decision_date)`, `build_cpi_yoy_asof(...)`, `build_monthly_panel(...)`, `coverage_report(...)` expectations used by the runner.

- [ ] Write tests for month-end calendar generation, market sampling, same-vintage CPI YoY, measurement-regime switching, zero future leakage, and replay coverage.
- [ ] Run `python -m unittest tests.test_ymq4_dp1b -v`; confirm RED because `scripts.ymq4_dp1b_backfill` does not yet exist.
- [ ] Freeze exact series/source/replay configuration in JSON.
- [ ] Commit test + config.

### Task 2: Fail-closed DP1-B database surface

**Files:**
- Create: `supabase/migrations/20260908060000_ymq4_dp1b_historical_backfill.sql`

**Interfaces:**
- Produces table `pit.decision_asof_values`.
- Produces RPCs `ymq4_dp1b_ingest_source`, `ymq4_dp1b_upsert_panel`, `ymq4_dp1b_readback`.

- [ ] Add RLS-enabled panel table keyed by `panel_id, decision_date, factor_id`.
- [ ] Add source-registry rows for World Bank Gold, CPIAUCSL, DTB3, DTWEXM, DTWEXBGS, DFII10.
- [ ] Add service-role-only bulk source/panel/readback RPCs; revoke anon/authenticated/public execute privileges.
- [ ] Validate migration text from tests/validator before cloud apply.
- [ ] Apply migration to `tbmoimbdhsrltvospwpu` only after repository version exists.

### Task 3: Source acquisition and immutable raw archive

**Files:**
- Create: `scripts/ymq4_dp1b_backfill.py`

**Interfaces:**
- `fetch_fred_series(series_id, ...) -> (raw_bytes, rows)`
- `fetch_cpi_initial_releases(...) -> dict`
- `fetch_cpi_asof_window(...) -> dict`
- `fetch_world_bank_gold(...) -> (raw_xlsx, monthly_rows)`
- `archive_raw(...) -> {sha256, path}`

- [ ] Implement FRED requests with API-key redaction and fail-closed network errors.
- [ ] Implement World Bank Pink Sheet official XLSX download and parse `Gold` monthly USD/troy-ounce column.
- [ ] Archive each raw source envelope/object to private S3, reread bytes, verify SHA and metadata SHA.
- [ ] Use DP1-B bulk ingest RPC to store source-snapshot metadata and normalized source observations.
- [ ] Keep retrieval time separate from historical known-as-of semantics.

### Task 4: Monthly PIT/as-of panel derivation

**Files:**
- Modify: `scripts/ymq4_dp1b_backfill.py`

**Interfaces:**
- Produces `pit.decision_asof_values` rows for factors `gold_usd_oz`, `usd`, `inflation_yoy`, `real_rate`.

- [ ] Generate month-end decision dates from 1978-01 through last complete month.
- [ ] Sample Gold monthly value and market factors without observations after decision date.
- [ ] For CPI, identify latest observation released by decision date and calculate YoY from a same-vintage as-of query.
- [ ] For 1978–2002 compute `DTB3 - CPI_YOY_ASOF` and label `HISTORICAL_PROXY`.
- [ ] From 2003 use DFII10; switch USD from DTWEXM to DTWEXBGS at 2006-01.
- [ ] Upsert panel via service-role-only RPC and independently read back counts.

### Task 5: Coverage, leakage and Reality Gate

**Files:**
- Modify: `scripts/ymq4_dp1b_backfill.py`
- Create: `scripts/validate_ymq4_dp1b.py`

**Interfaces:**
- `coverage_report(panel_rows, replay_windows) -> dict`
- final receipt status: `DP1B_CORE_BACKFILL_PASS`, `PARTIAL_RESEARCH_ONLY`, or `FAIL_CLOSED`.

- [ ] Count future-leakage rows; any count >0 is FAIL_CLOSED.
- [ ] Compute per-factor and per-replay-window completeness.
- [ ] Require >=80% complete months for all four factors in every replay window for PASS.
- [ ] Record measurement-regime counts and all source SHA IDs in non-secret receipt.
- [ ] Write gate to `runtime.reality_gate_runs` and read it back.
- [ ] Validator rejects secret literals, model/B2–B7 imports, missing source labels and unsafe workflow authority.

### Task 6: GitHub Actions physical backfill

**Files:**
- Create: `.github/workflows/ymq4-dp1b-historical-backfill.yml`

**Interfaces:**
- `workflow_dispatch` modes: `preflight`, `full`.
- Uses existing four DP1-A repository secrets only.

- [ ] Preflight runs validator/unit tests plus FRED/World Bank/Supabase reachability.
- [ ] Full mode installs `boto3` and `openpyxl`, runs backfill, requires a non-failing receipt and uploads non-secret artifact.
- [ ] Full job must never invoke B2–B7 scripts.
- [ ] Dispatch full on the DP1-B branch after preflight passes.

### Task 7: Independent physical verification and settlement

**Files:**
- Create: `docs/architecture/ymq4/YMQ4-DP1-B-HISTORICAL-BACKFILL-RECEIPT-v0.1.md`

**Interfaces:**
- Consumes GitHub workflow run, artifact, Supabase source snapshots, panel and reality gate.

- [ ] Verify GitHub full job actually ran and artifact binds to expected Git SHA.
- [ ] Independently query Supabase for raw-object count, source-snapshot count, panel count, leakage count and gate receipt.
- [ ] Compare DB counts with artifact receipt.
- [ ] Freeze `PASS`, `PARTIAL_RESEARCH_ONLY`, or `FAIL_CLOSED` without altering model design.
- [ ] Keep PR Draft and do not merge or start B2–B7.
