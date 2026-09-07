# YMQ4-G1 NVIDIA Genesis Pair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the first strict-PIT, reproducible YMQ4 Dynamic Repricing vertical slice for NVIDIA across `T0=2022-08-26 16:00 ET` and held-out `T1=2023-05-25 16:00 ET`, persisting typed CapabilityInvocation → CapabilityResult → ResearchStateSnapshot → ResearchReceipt objects to Supabase without granting capital authority.

**Architecture:** `moonstachain/yuanli-invest` remains Canon and stores the accepted design plus a frozen implementation manifest; `moonstachain/quant-workspace` implements deterministic YMQ4 compute under a new `src/ymq4/` namespace; Supabase `ymq4` remains the private PIT evidence/state/runtime plane. G1 uses a two-stage interpretation: continuous factors estimate common-tech/rates/liquidity exposure, while timestamped NVIDIA/Fed events are handled as typed event evidence and event-associated abnormal-return diagnostics rather than being silently promoted to causal factors.

**Tech Stack:** Python >=3.11, NumPy, Pandas, DuckDB, `requests`, `psycopg[binary]`, pytest; Supabase PostgreSQL 17 `ymq4` schema; GitHub `yuanli-invest` Canon; official NVIDIA/Federal Reserve evidence plus public historical market/macro series.

**Spec:** `docs/superpowers/specs/2026-09-07-ymq4-g1-nvidia-genesis-pair-design.md`

## Global Constraints

- Target is exactly `NVDA`; hard-negative comparators are `QQQ` and `SPY`.
- Genesis T0 is exactly `2022-08-26T16:00:00-04:00`.
- Held-out T1 is exactly `2023-05-25T16:00:00-04:00` and may not influence factor choice, transforms, model windows, model family, drift metric, drift thresholds, or output semantics.
- Five input packs only: Rates / Liquidity / Earnings / Narrative / Price.
- Short rolling window = 63 trading days; long rolling window = 252 trading days.
- G1 drift metric = cosine distance; thresholds are pre-T0 empirical percentiles P50/P75/P90 only.
- `Claim Authority <= Evidence Authority`; dynamic beta and event association are not causal proof.
- `known_as_of <= evidence_cutoff` for every admitted observation.
- No new Supabase table is allowed unless implementation proves a hard contract gap and a design amendment is approved.
- `Research PASS != Capital PASS`; no Buy/Sell/Hold, target price, expected-return promise, weight, position size, or execution field.
- Supabase test writes must be transactional or cleanup-safe; smoke fixtures must not contaminate production research rows.
- Any post-T1 change to the frozen method creates a new version and invalidates the original transfer result.

---

## File Structure Lock

### `moonstachain/yuanli-invest`

- Create: `docs/ymq4/g1/implementation-manifest.json` — immutable G1 provider/model/parameter/evidence-cutoff freeze used by both T0 and T1.
- Create: `docs/ymq4/g1/evidence-events.json` — small auditable event metadata only; no bulk market data.
- Create: `docs/ymq4/g1/runtime-receipts.md` — pointers to persisted Supabase receipt IDs and Git/algorithm versions; Supabase remains runtime ledger.

### `moonstachain/quant-workspace`

- Modify: `pyproject.toml` — add test/runtime dependencies without changing existing A-share behavior.
- Create: `src/ymq4/__init__.py` — package boundary only.
- Create: `src/ymq4/contracts.py` — typed invocation/result/state/receipt dataclasses and prohibited-field validation.
- Create: `src/ymq4/canonical.py` — canonical JSON, deterministic SHA-256, time normalization.
- Create: `src/ymq4/transforms.py` — PIT-safe delta/z-score/log-return transforms.
- Create: `src/ymq4/factor_frame.py` — align NVDA/QQQ/SPY, rates, USD/liquidity and event metadata into one daily modeling frame.
- Create: `src/ymq4/fixed_beta.py` — static least-squares baseline.
- Create: `src/ymq4/rolling_beta.py` — 63d/252d rolling least-squares with diagnostics.
- Create: `src/ymq4/tvp_kalman.py` — deterministic NumPy Kalman random-walk beta estimator.
- Create: `src/ymq4/contribution.py` — continuous driver contribution and residual accounting.
- Create: `src/ymq4/event_study.py` — event-associated abnormal-return diagnostics; preserves under-identification for joint earnings+narrative events.
- Create: `src/ymq4/property_drift.py` — cosine drift plus pre-T0 percentile calibration.
- Create: `src/ymq4/challenge.py` — common-tech/common-market hard negatives and strongest-alternative selection.
- Create: `src/ymq4/supabase_store.py` — private-schema PostgreSQL adapter using `YMQ4_SUPABASE_DB_URL`.
- Create: `src/ymq4/runtime.py` — one orchestration entry point from frozen manifest + PIT observations to typed result/receipt.
- Create: `src/ymq4/providers/csv_http.py` — strict CSV download helper with hashing and source metadata.
- Create: `src/ymq4/providers/market.py` — NVDA/QQQ/SPY daily series adapter.
- Create: `src/ymq4/providers/macro.py` — 2Y/10Y/10Y-real/USD/Fed-balance adapters and publication/revision policy metadata.
- Create: `scripts/run_ymq4_g1.py` — CLI for `--point t0|t1 --persist --reproduce-receipt <uuid>`.
- Create: `tests/ymq4/` — unit and integration tests described below.

No file under `src/strategy/` is modified.

---

### Task 1: Freeze the G1 implementation manifest and evidence-event vocabulary

**Files:**
- Create: `yuanli-invest/docs/ymq4/g1/implementation-manifest.json`
- Create: `yuanli-invest/docs/ymq4/g1/evidence-events.json`
- Test: Canon JSON validation via a lightweight Python check executed from repository root

**Interfaces:**
- Consumes: accepted design spec.
- Produces: exact keys read later by `src/ymq4/runtime.py`: `capability_id`, `contract_version`, `target`, `t0`, `t1`, `history_start`, `factors`, `windows`, `shock_normalization`, `drift`, `providers`, `event_policy`, `capital_authority`.

- [ ] **Step 1: Write the manifest with exact frozen values**

Use these values, without later T1 tuning:

```json
{
  "capability_id": "CAP-CROSS-YMQ4-DYNAMIC-REPRICING-G1",
  "contract_version": "0.1.0",
  "target": "NVDA",
  "comparators": ["QQQ", "SPY"],
  "history_start": "2020-01-02",
  "t0": "2022-08-26T16:00:00-04:00",
  "t1": "2023-05-25T16:00:00-04:00",
  "continuous_factor_columns": ["qqq_ret", "real_yield_shock", "usd_shock"],
  "challenger_columns": ["spy_ret"],
  "windows": {"short": 63, "long": 252},
  "shock_normalization": {"method": "trailing_zscore", "window": 63, "ddof": 1},
  "tvp": {"process_variance": 0.0001, "observation_variance_floor": 1e-8, "initial_covariance": 1.0},
  "drift": {"metric": "cosine_distance", "threshold_percentiles": [0.50, 0.75, 0.90], "calibration_cutoff": "2022-08-26T16:00:00-04:00"},
  "event_policy": {"association_window_trading_days": [0, 1], "joint_event_split": "forbidden", "joint_event_label": "earnings_narrative_bundle"},
  "capital_authority": "none"
}
```

Provider section must bind economic definitions rather than Capability identity:

```json
{
  "price": {"provider": "stooq_csv", "symbols": {"NVDA": "nvda.us", "QQQ": "qqq.us", "SPY": "spy.us"}},
  "rates": {"provider": "fred_csv", "series": {"US2Y": "DGS2", "US10Y": "DGS10", "US10Y_REAL": "DFII10"}},
  "liquidity": {"provider": "fred_csv", "series": {"USD_BROAD": "DTWEXBGS", "FED_ASSETS": "WALCL"}}
}
```

- [ ] **Step 2: Write the evidence-event vocabulary**

The event file contains metadata only, with exact types:

```json
{
  "event_types": ["earnings", "policy", "narrative", "earnings_narrative_bundle"],
  "events": [
    {"event_id": "NVDA-2022-08-08-PRELIM-Q2", "event_type": "earnings", "effective_market_date": "2022-08-08"},
    {"event_id": "NVDA-2022-08-24-Q2-FY23", "event_type": "earnings", "effective_market_date": "2022-08-25"},
    {"event_id": "FED-2022-08-26-JACKSON-HOLE", "event_type": "policy", "effective_market_date": "2022-08-26"},
    {"event_id": "NVDA-2023-05-24-Q1-FY24-AI", "event_type": "earnings_narrative_bundle", "effective_market_date": "2023-05-25"}
  ]
}
```

Each event receives its official URL, release timestamp, SHA-256 of captured evidence text, and `known_as_of`; the implementer must capture the actual values before persistence. If the exact timestamp cannot be proven, the event is rejected rather than approximated.

- [ ] **Step 3: Validate JSON and invariants**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('docs/ymq4/g1/implementation-manifest.json').read_text())
assert m['target']=='NVDA'
assert m['windows']=={'short':63,'long':252}
assert m['capital_authority']=='none'
assert m['t0'] < m['t1']
print('manifest-pass')
PY
```

Expected: `manifest-pass`.

- [ ] **Step 4: Commit Canon-side freeze**

```bash
git add docs/ymq4/g1/implementation-manifest.json docs/ymq4/g1/evidence-events.json
git commit -m "canon: freeze YMQ4-G1 NVIDIA implementation manifest"
```

---

### Task 2: Add YMQ4 typed contracts and deterministic canonical hashing

**Files:**
- Modify: `quant-workspace/pyproject.toml`
- Create: `quant-workspace/src/ymq4/__init__.py`
- Create: `quant-workspace/src/ymq4/contracts.py`
- Create: `quant-workspace/src/ymq4/canonical.py`
- Test: `quant-workspace/tests/ymq4/test_contracts.py`

**Interfaces:**
- Produces: `Invocation`, `CapabilityResult`, `ResearchStateSnapshot`, `ResearchReceipt`, `canonical_json(obj) -> str`, `sha256_json(obj) -> str`.

- [ ] **Step 1: Add dependencies**

Add runtime dependencies:

```toml
"requests>=2.32.0",
"psycopg[binary]>=3.2.0",
```

Add a dev group:

```toml
[dependency-groups]
dev = ["pytest>=8.4.0"]
```

- [ ] **Step 2: Write failing contract tests**

```python
from datetime import datetime, timezone
import pytest
from src.ymq4.contracts import Invocation, CapabilityResult


def test_invocation_requires_strict_pit():
    with pytest.raises(ValueError):
        Invocation(
            request_id="r1", capability_id="cap", contract_version="0.1",
            target_id="NVDA", as_of=datetime.now(timezone.utc),
            evidence_cutoff=datetime.now(timezone.utc), strict_pit=False,
            runtime="reference"
        )


def test_result_rejects_capital_fields():
    with pytest.raises(ValueError):
        CapabilityResult(status="success", state={"buy": True})
```

- [ ] **Step 3: Run tests and verify failure**

```bash
uv run --group dev pytest tests/ymq4/test_contracts.py -v
```

Expected: import/module failure.

- [ ] **Step 4: Implement minimal dataclasses and prohibited-field scan**

`CapabilityResult` recursively rejects keys matching:

```python
PROHIBITED = {"buy", "sell", "hold", "target_price", "position_size", "portfolio_weight", "recommended_weight", "expected_return"}
```

`Invocation.__post_init__` raises when `strict_pit is not True` or `evidence_cutoff > as_of`.

- [ ] **Step 5: Add deterministic JSON tests**

```python
from src.ymq4.canonical import sha256_json

def test_hash_is_order_independent_for_mapping_keys():
    assert sha256_json({"b": 2, "a": 1}) == sha256_json({"a": 1, "b": 2})
```

- [ ] **Step 6: Implement canonical serializer**

Use `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)` and normalize datetimes to UTC ISO-8601 before hashing.

- [ ] **Step 7: Run tests and commit**

```bash
uv run --group dev pytest tests/ymq4/test_contracts.py -v
git add pyproject.toml src/ymq4 tests/ymq4/test_contracts.py
git commit -m "feat: add YMQ4 typed runtime contracts"
```

---

### Task 3: Implement PIT-safe transforms and modeling frame construction

**Files:**
- Create: `src/ymq4/transforms.py`
- Create: `src/ymq4/factor_frame.py`
- Test: `tests/ymq4/test_transforms.py`
- Test: `tests/ymq4/test_factor_frame.py`

**Interfaces:**
- Produces: `log_returns(series)`, `trailing_zscore(series, window=63)`, `build_factor_frame(prices, macro, cutoff, events) -> pd.DataFrame`.

- [ ] **Step 1: Write failing transform tests**

```python
import pandas as pd
from src.ymq4.transforms import log_returns, trailing_zscore


def test_zscore_uses_past_and_current_only():
    s = pd.Series([1.,2.,3.,4.])
    z = trailing_zscore(s, window=3)
    assert pd.isna(z.iloc[1])
    expected = (3 - 2) / 1
    assert abs(z.iloc[2] - expected) < 1e-12
```

The implementation must not use centered/two-sided windows.

- [ ] **Step 2: Implement transforms and verify**

```bash
uv run --group dev pytest tests/ymq4/test_transforms.py -v
```

- [ ] **Step 3: Write PIT frame test**

Construct synthetic observations containing one row with `known_as_of` after cutoff. Assert it never enters the frame.

```python
assert frame.index.max() <= pd.Timestamp("2022-08-26")
assert "future_value" not in frame.columns
```

- [ ] **Step 4: Implement factor-frame semantics**

Daily frame columns are exactly:

```text
nvda_ret
qqq_ret
spy_ret
real_yield_shock
usd_shock
fed_assets_state
event_type
event_id
```

`fed_assets_state` is contextual and is not part of the G1 regression matrix.

Continuous regression factors are exactly:

```python
X_COLUMNS = ["qqq_ret", "real_yield_shock", "usd_shock"]
```

- [ ] **Step 5: Run tests and commit**

```bash
uv run --group dev pytest tests/ymq4/test_transforms.py tests/ymq4/test_factor_frame.py -v
git add src/ymq4/transforms.py src/ymq4/factor_frame.py tests/ymq4
git commit -m "feat: add PIT-safe YMQ4 factor frame"
```

---

### Task 4: Implement Fixed Beta and 63d/252d Rolling Beta baselines

**Files:**
- Create: `src/ymq4/fixed_beta.py`
- Create: `src/ymq4/rolling_beta.py`
- Test: `tests/ymq4/test_beta_models.py`

**Interfaces:**
- Produces: `fit_fixed_beta(y, X) -> BetaEstimate`, `rolling_beta(y, X, window) -> pd.DataFrame`.
- `BetaEstimate` contains `intercept`, ordered `betas`, `residual_std`, `condition_number`, `n_obs`, `status`.

- [ ] **Step 1: Write synthetic coefficient-recovery test**

```python
import numpy as np, pandas as pd
from src.ymq4.fixed_beta import fit_fixed_beta


def test_fixed_beta_recovers_known_coefficients():
    rng=np.random.default_rng(7)
    X=pd.DataFrame(rng.normal(size=(500,3)), columns=["qqq_ret","real_yield_shock","usd_shock"])
    y=0.2 + X.to_numpy() @ np.array([1.4,-0.5,-0.2])
    est=fit_fixed_beta(pd.Series(y), X)
    assert np.allclose(list(est.betas.values()), [1.4,-0.5,-0.2], atol=1e-8)
```

- [ ] **Step 2: Run failure, implement using `np.linalg.lstsq`, rerun**

Ill-conditioned matrices with `condition_number > 1e8` return `status="unstable"` instead of pretending precision.

- [ ] **Step 3: Write rolling-window test**

Assert the first non-null 63d beta appears only after 63 complete rows and the long series only after 252 complete rows.

- [ ] **Step 4: Implement and commit**

```bash
uv run --group dev pytest tests/ymq4/test_beta_models.py -v
git add src/ymq4/fixed_beta.py src/ymq4/rolling_beta.py tests/ymq4/test_beta_models.py
git commit -m "feat: add fixed and rolling YMQ4 beta models"
```

---

### Task 5: Implement deterministic TVP/Kalman beta estimation

**Files:**
- Create: `src/ymq4/tvp_kalman.py`
- Test: `tests/ymq4/test_tvp_kalman.py`

**Interfaces:**
- Produces: `fit_tvp_beta(y, X, process_variance, observation_variance_floor, initial_covariance) -> TVPResult`.
- `TVPResult.beta_path` has index aligned to inputs and columns identical to `X_COLUMNS`.

- [ ] **Step 1: Write constant-beta test**

Synthetic data with stable coefficients should converge close to the true values in the final 50 observations.

```python
assert np.allclose(result.beta_path.tail(50).mean().to_numpy(), true_beta, atol=0.12)
```

- [ ] **Step 2: Write regime-change test**

Generate coefficient `rate_beta=-0.2` for first half and `-1.0` for second half. Assert the terminal estimate is more negative than the midpoint estimate.

- [ ] **Step 3: Implement a random-walk state model in NumPy**

Use one state per factor plus intercept; no hidden optimization or auto-tuning. `process_variance`, `initial_covariance`, and floor come only from the manifest.

- [ ] **Step 4: Add numerical fail-closed behavior**

Non-finite covariance, singular update, or insufficient observations returns `status="fail_closed"` with a warning list.

- [ ] **Step 5: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_tvp_kalman.py -v
git add src/ymq4/tvp_kalman.py tests/ymq4/test_tvp_kalman.py
git commit -m "feat: add deterministic TVP Kalman beta estimator"
```

---

### Task 6: Implement contribution, event diagnostics, property drift, and hard-negative challenge

**Files:**
- Create: `src/ymq4/contribution.py`
- Create: `src/ymq4/event_study.py`
- Create: `src/ymq4/property_drift.py`
- Create: `src/ymq4/challenge.py`
- Test: `tests/ymq4/test_interpretation.py`

**Interfaces:**
- Produces: `driver_contributions(beta, shock_row)`, `event_abnormal_return(frame, event_date, window=(0,1))`, `calibrate_drift_thresholds(pre_t0_beta_short, pre_t0_beta_long)`, `classify_drift(value, thresholds)`, `select_strongest_alternative(...)`.

- [ ] **Step 1: Write contribution conservation test**

```python
from src.ymq4.contribution import driver_contributions

def test_continuous_contribution_is_beta_times_shock():
    c=driver_contributions({"Rates":-0.5},{"Rates":2.0})
    assert c["Rates"] == -1.0
```

- [ ] **Step 2: Write joint-event under-identification test**

For `event_type="earnings_narrative_bundle"`, the event study may emit `associated_abnormal_return`, but must emit:

```python
{"earnings_split": None, "narrative_split": None, "identification_status": "underidentified"}
```

It must never arbitrarily split 50/50.

- [ ] **Step 3: Write drift-threshold test**

Threshold calibration only consumes beta pairs whose timestamp is strictly before T0. Assert T1 samples do not alter thresholds.

- [ ] **Step 4: Write hard-negative test**

If NVDA and QQQ move nearly identically and idiosyncratic residual is small, the strongest alternative must be `broad_tech_common_factor` rather than an NVIDIA-specific story.

- [ ] **Step 5: Implement and run tests**

```bash
uv run --group dev pytest tests/ymq4/test_interpretation.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/ymq4/contribution.py src/ymq4/event_study.py src/ymq4/property_drift.py src/ymq4/challenge.py tests/ymq4/test_interpretation.py
git commit -m "feat: add YMQ4 attribution drift and challenge layer"
```

---

### Task 7: Add private Supabase runtime adapter and atomic Result/State/Receipt persistence

**Files:**
- Create: `src/ymq4/supabase_store.py`
- Test: `tests/ymq4/test_supabase_store.py`
- Create: `.env.example` entries only; never commit secrets

**Interfaces:**
- Consumes: `YMQ4_SUPABASE_DB_URL`.
- Produces: `load_observations(economic_ids, cutoff)`, `insert_invocation(invocation)`, `persist_result_bundle(invocation, result, snapshot, receipt)`.

- [ ] **Step 1: Write query-construction unit tests**

Assert the observation query includes both:

```sql
known_as_of <= %s
```

and deterministic ordering:

```sql
ORDER BY economic_id, observed_at, known_as_of, observation_id
```

- [ ] **Step 2: Implement fully qualified private-schema SQL**

All table references are explicit `ymq4.<table>`; do not change Supabase exposed-schema settings.

- [ ] **Step 3: Persist the runtime bundle in one transaction**

Transaction order:

```text
capability_invocations
→ capability_results
→ research_state_snapshots
→ research_receipts
→ commit
```

Any failure rolls back the whole bundle.

- [ ] **Step 4: Add optional real-database integration test**

The test is skipped unless `YMQ4_SUPABASE_DB_URL` exists. It creates a unique test request, writes the four runtime objects inside a transaction, verifies them, then rolls back.

```bash
uv run --group dev pytest tests/ymq4/test_supabase_store.py -v
```

Expected without secret: unit tests PASS; integration test SKIPPED.

- [ ] **Step 5: Commit**

```bash
git add src/ymq4/supabase_store.py tests/ymq4/test_supabase_store.py .env.example
git commit -m "feat: add YMQ4 Supabase runtime store"
```

---

### Task 8: Build provider adapters and ingest the five PIT input packs

**Files:**
- Create: `src/ymq4/providers/__init__.py`
- Create: `src/ymq4/providers/csv_http.py`
- Create: `src/ymq4/providers/market.py`
- Create: `src/ymq4/providers/macro.py`
- Test: `tests/ymq4/test_providers.py`

**Interfaces:**
- Produces normalized provider rows compatible with the existing `ymq4.observations` schema.

- [ ] **Step 1: Write fixture-based parser tests**

No unit test uses live internet. Store tiny CSV strings in tests and verify dates, missing values, decimal parsing, source hash, and deterministic symbol mapping.

- [ ] **Step 2: Implement HTTP helper with byte-level hash**

`fetch_csv(url)` returns `(dataframe, sha256, fetched_at)` and raises on non-200 or empty content.

- [ ] **Step 3: Implement market adapter**

For NVDA/QQQ/SPY, store trading-date close observations and provenance that identifies whether source prices are adjusted. Compute returns in `factor_frame.py`, not in the provider layer.

- [ ] **Step 4: Implement macro adapter with admission policy**

Economic IDs:

```text
US2Y
US10Y
US10Y_REAL
USD_BROAD
FED_ASSETS
```

Each series mapping must define `revision_policy` and `publication_lag_policy`. If a series cannot establish defensible PIT availability for T0/T1, ingest it with `authority_class="proxy"` and force a warning/degrade state; do not fabricate a vintage timestamp.

- [ ] **Step 5: Ingest official event evidence**

Use only official NVIDIA and Federal Reserve source material referenced by the Canon event manifest. Store the event as `value_text` plus exact release/known timestamps and provenance; bulk article text is not committed to GitHub.

- [ ] **Step 6: PIT admission check before commit to Supabase**

Run a dry validation that counts rows violating:

```sql
known_as_of < observed_at
```

or missing both numeric/text values. Zero violations are required.

- [ ] **Step 7: Run tests and commit**

```bash
uv run --group dev pytest tests/ymq4/test_providers.py -v
git add src/ymq4/providers tests/ymq4/test_providers.py
git commit -m "feat: add YMQ4 G1 provider adapters"
```

---

### Task 9: Implement the one-command runtime and reproduce-before-persist discipline

**Files:**
- Create: `src/ymq4/runtime.py`
- Create: `scripts/run_ymq4_g1.py`
- Test: `tests/ymq4/test_runtime.py`

**Interfaces:**
- Produces: `run_point(point: Literal["t0","t1"], manifest, store, persist=False) -> RuntimeBundle`.
- `RuntimeBundle` contains invocation, result, snapshot, receipt.

- [ ] **Step 1: Write a synthetic end-to-end runtime test**

Feed deterministic fixture data and assert all of these exist:

```python
bundle.result.state["dominant_driver"]
bundle.result.state["driver_contributions"]
bundle.result.state["property_drift_state"]
bundle.result.state["strongest_alternative"]
bundle.result.state["strongest_falsifier"]
bundle.result.state["residual"]
bundle.receipt.receipt_sha256
```

- [ ] **Step 2: Enforce `t1` manifest freeze**

`run_point("t1")` reads the same factor columns, windows, TVP parameters, drift thresholds and event policy recorded by T0. Runtime raises if a parameter checksum differs.

- [ ] **Step 3: Implement reliability semantics**

Minimum rules:

```text
fail_closed: PIT breach, missing long-window history, numerical failure
unknown: no driver exceeds uncertainty / hard-negative challenge
partial: at least one pack is proxy/missing but computation remains interpretable
success: all mandatory packs admitted and computation stable
```

- [ ] **Step 4: Generate receipt before persistence**

Receipt hash includes canonical invocation, sorted evidence references, algorithm version, manifest hash and typed result. Persistence is refused when a recomputed hash disagrees.

- [ ] **Step 5: Implement CLI**

Examples:

```bash
uv run python scripts/run_ymq4_g1.py --point t0 --manifest ../yuanli-invest/docs/ymq4/g1/implementation-manifest.json --persist
uv run python scripts/run_ymq4_g1.py --point t1 --manifest ../yuanli-invest/docs/ymq4/g1/implementation-manifest.json --persist
uv run python scripts/run_ymq4_g1.py --reproduce-receipt <receipt_uuid>
```

- [ ] **Step 6: Run all tests and commit**

```bash
uv run --group dev pytest tests/ymq4 -v
git add src/ymq4/runtime.py scripts/run_ymq4_g1.py tests/ymq4/test_runtime.py
git commit -m "feat: add YMQ4 G1 runtime orchestration"
```

---

### Task 10: Execute T0, freeze its method checksum, then execute held-out T1 without tuning

**Files:**
- Modify: `yuanli-invest/docs/ymq4/g1/runtime-receipts.md`
- Supabase: existing `ymq4.*` tables only
- No model-code changes are permitted between T0 and T1 unless T1 is invalidated and a new spec version is created.

**Interfaces:**
- Produces: one persisted T0 runtime bundle, one persisted held-out T1 bundle, reproduction evidence for both.

- [ ] **Step 1: Pre-run gate**

Verify:

```bash
uv run --group dev pytest tests/ymq4 -v
```

Expected: all unit tests PASS; real Supabase integration PASS when secret is present.

- [ ] **Step 2: Register replay cases**

Use IDs:

```text
YMQ4-G1-NVDA-T0-20220826
YMQ4-G1-NVDA-T1-20230525
```

Both rows carry exact `t0`/knowledge cutoff and the same preregistered manifest hash.

- [ ] **Step 3: Run T0 without persistence first**

```bash
uv run python scripts/run_ymq4_g1.py --point t0 --manifest <manifest-path>
```

Review only structural validity: PIT status, five-pack coverage, numerical stability, challenge output, residual visibility, and prohibited-field scan. Do **not** tune for a preferred economic conclusion.

- [ ] **Step 4: Persist T0 and capture receipt**

```bash
uv run python scripts/run_ymq4_g1.py --point t0 --manifest <manifest-path> --persist
```

Record `request_id`, `result_id`, `snapshot_id`, `receipt_id`, manifest SHA-256, quant Git commit SHA and Canon Git commit SHA.

- [ ] **Step 5: Reproduce T0 receipt**

```bash
uv run python scripts/run_ymq4_g1.py --reproduce-receipt <t0-receipt-id>
```

Expected: `REPRODUCED` and identical typed-state hash.

- [ ] **Step 6: Freeze T0 method checksum**

Compute and record SHA-256 over:

```text
manifest JSON
factor-column list
transform parameters
rolling windows
TVP parameters
drift thresholds
quant commit SHA
```

This checksum is required verbatim by T1.

- [ ] **Step 7: Run held-out T1**

No code/config changes are allowed after Step 6.

```bash
uv run python scripts/run_ymq4_g1.py --point t1 --manifest <manifest-path> --persist
```

If T1 reveals a method defect, label the original transfer test invalidated; do not patch and preserve the same test identity.

- [ ] **Step 8: Reproduce T1 receipt**

```bash
uv run python scripts/run_ymq4_g1.py --reproduce-receipt <t1-receipt-id>
```

Expected: identical typed-state hash.

- [ ] **Step 9: Write runtime pointer ledger**

`runtime-receipts.md` records identifiers and statuses only, e.g.:

```text
T0: receipt=<uuid> status=<success|partial|unknown|fail_closed> manifest_sha256=<hash> quant_commit=<sha>
T1: receipt=<uuid> status=<success|partial|unknown|fail_closed> manifest_sha256=<same hash> quant_commit=<same sha>
```

It must not rewrite the scientific result as a capital recommendation.

- [ ] **Step 10: Commit Canon-side runtime pointers**

```bash
git add docs/ymq4/g1/runtime-receipts.md
git commit -m "receipt: record YMQ4-G1 NVIDIA Genesis Pair runtime pointers"
```

---

## Final Verification Gate

Before claiming `YMQ4-G1 PASS`, run and archive the following evidence:

```bash
uv run --group dev pytest tests/ymq4 -v
uv run python scripts/run_ymq4_g1.py --reproduce-receipt <t0-receipt-id>
uv run python scripts/run_ymq4_g1.py --reproduce-receipt <t1-receipt-id>
```

Then verify in Supabase:

```sql
select count(*) from ymq4.capability_invocations where target_id='NVDA';
select count(*) from ymq4.capability_results r join ymq4.capability_invocations i using(request_id) where i.target_id='NVDA';
select count(*) from ymq4.research_state_snapshots where target_id='NVDA';
select count(*) from ymq4.research_receipts rr join ymq4.capability_invocations i using(request_id) where i.target_id='NVDA';
```

Expected G1 minimum: two real invocations, two results, two snapshots, two receipts, plus zero PIT-violation findings.

The final G1 settlement may be `PASS`, `PARTIAL`, or `FAIL_CLOSED`. A scientifically disappointing driver result does **not** constitute engineering failure; hidden leakage, non-reproducibility, method retuning after T1, or capital-authority leakage does.

## Spec Coverage Self-Review

- Genesis pair and held-out law: Tasks 1, 9, 10.
- Five input packs: Tasks 1, 8.
- Canonical PIT observation: Tasks 3, 7, 8.
- Fixed / Rolling / TVP: Tasks 4, 5.
- Driver contribution + residual: Task 6.
- Property drift: Task 6.
- Hard negatives and competing explanation: Task 6.
- Runtime Invocation → Result → State → Receipt: Tasks 7, 9, 10.
- Receipt reproduction: Tasks 2, 9, 10.
- No capital authority: Tasks 1, 2, 9, final gate.
- No T1 retuning: Tasks 1, 9, 10.
- No new Supabase tables: Global Constraint + Tasks 7, 10.

No placeholder or post-hoc tuning step is permitted by this plan.
