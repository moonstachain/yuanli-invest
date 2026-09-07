# YMQ4-G1 NVIDIA Genesis Pair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the first strict-PIT, reproducible YMQ4 Dynamic Repricing vertical slice for NVIDIA across `T0=2022-08-26 16:00 ET` and held-out `T1=2023-05-25 16:00 ET`, persisting typed `CapabilityInvocation → CapabilityResult → ResearchStateSnapshot → ResearchReceipt` objects to Supabase without granting capital authority.

**Architecture:** `moonstachain/yuanli-invest` remains Canon and stores the accepted design plus a frozen implementation manifest. `moonstachain/quant-workspace` implements deterministic YMQ4 compute under a new `src/ymq4/` namespace. Supabase `ymq4` remains the private PIT evidence/state/runtime plane. Continuous factors estimate common-tech/rates/liquidity exposure; timestamped NVIDIA/Fed events are handled as typed event evidence and event-associated abnormal-return diagnostics, never silently promoted to causal proof.

**Tech Stack:** Python >=3.11, NumPy, Pandas, DuckDB, `requests`, `psycopg[binary]`, pytest; Supabase PostgreSQL 17 `ymq4` schema; GitHub `yuanli-invest` Canon.

**Spec:** `docs/superpowers/specs/2026-09-07-ymq4-g1-nvidia-genesis-pair-design.md`

## Global Constraints

- Target exactly `NVDA`; hard-negative comparators exactly `QQQ`, `SPY`.
- T0 exactly `2022-08-26T16:00:00-04:00`.
- T1 exactly `2023-05-25T16:00:00-04:00`; T1 may not influence factor choice, transforms, windows, TVP parameters, drift metric, thresholds, or output semantics.
- Five packs only: Rates / Liquidity / Earnings / Narrative / Price.
- Short rolling window = 63 trading days; long rolling window = 252 trading days.
- Drift metric = cosine distance; thresholds = pre-T0 P50/P75/P90 empirical percentiles.
- `Claim Authority <= Evidence Authority`; dynamic beta and event association are not causal proof.
- Every admitted row must satisfy `known_as_of <= evidence_cutoff`.
- No new Supabase table unless a design amendment is separately approved.
- `Research PASS != Capital PASS`; no buy/sell/hold, target price, weight, position size, expected-return promise, or execution field.
- `src/strategy/` is untouched.
- Any post-T1 tuning creates a new version and invalidates the original transfer test.

---

## File Structure Lock

### Canon repo: `moonstachain/yuanli-invest`

- Create `docs/ymq4/g1/implementation-manifest.json` — frozen model/provider/parameter manifest.
- Create `docs/ymq4/g1/evidence-events.json` — auditable event metadata only.
- Create `docs/ymq4/g1/runtime-receipts.md` — pointers to persisted Supabase receipt IDs; not the runtime ledger itself.

### Quant repo: `moonstachain/quant-workspace`

- Modify `pyproject.toml`.
- Create `src/ymq4/__init__.py`.
- Create `src/ymq4/contracts.py`.
- Create `src/ymq4/canonical.py`.
- Create `src/ymq4/transforms.py`.
- Create `src/ymq4/factor_frame.py`.
- Create `src/ymq4/fixed_beta.py`.
- Create `src/ymq4/rolling_beta.py`.
- Create `src/ymq4/tvp_kalman.py`.
- Create `src/ymq4/contribution.py`.
- Create `src/ymq4/event_study.py`.
- Create `src/ymq4/property_drift.py`.
- Create `src/ymq4/challenge.py`.
- Create `src/ymq4/supabase_store.py`.
- Create `src/ymq4/runtime.py`.
- Create `src/ymq4/providers/{__init__,csv_http,market,macro}.py`.
- Create `scripts/run_ymq4_g1.py`.
- Create `tests/ymq4/` test modules.

---

### Task 1: Freeze the implementation manifest and event evidence vocabulary

**Files:**
- Create `docs/ymq4/g1/implementation-manifest.json`
- Create `docs/ymq4/g1/evidence-events.json`

**Produces:** exact values consumed by runtime: `capability_id`, `contract_version`, `target`, `t0`, `t1`, `history_start`, factor columns, windows, shock normalization, TVP parameters, drift policy, providers, event policy, capital authority.

- [ ] **Step 1: Write the frozen manifest**

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
  "providers": {
    "price": {"provider": "stooq_csv", "symbols": {"NVDA": "nvda.us", "QQQ": "qqq.us", "SPY": "spy.us"}},
    "rates": {"provider": "fred_csv", "series": {"US2Y": "DGS2", "US10Y": "DGS10", "US10Y_REAL": "DFII10"}},
    "liquidity": {"provider": "fred_csv", "series": {"USD_BROAD": "DTWEXBGS", "FED_ASSETS": "WALCL"}}
  },
  "capital_authority": "none"
}
```

- [ ] **Step 2: Write exact official event source URLs and conservative timestamp law**

Use these source URLs:

```text
NVDA-2022-08-08-PRELIM-Q2
https://nvidianews.nvidia.com/news/nvidia-announces-preliminary-financial-resultsfor-second-quarter-fiscal-2023

NVDA-2022-08-24-Q2-FY23
https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2023

FED-2022-08-26-JACKSON-HOLE
https://www.federalreserve.gov/newsevents/speech/files/powell20220826a.pdf

NVDA-2023-05-24-Q1-FY24-AI
https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2024
```

Rules:

```text
- If an official source proves exact release time, use it.
- Powell Jackson Hole uses 2022-08-26T10:00:00-04:00 because the official Fed release says "For release on delivery 10:00 a.m. EDT".
- NVIDIA 2022-08-24 uses the official preannouncement schedule: public results approximately 1:20 p.m. PT; encode 2022-08-24T16:20:00-04:00 and effective market date 2022-08-25.
- If an NVIDIA page proves only a calendar date and no exact time, use a conservative `known_as_of` of 23:59:59 ET on that date and make the event effective on the next U.S. trading session. Never guess an earlier time.
- `earnings_narrative_bundle` may not be split into earnings and narrative shares.
```

- [ ] **Step 3: Validate the manifest**

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

- [ ] **Step 4: Commit**

```bash
git add docs/ymq4/g1/implementation-manifest.json docs/ymq4/g1/evidence-events.json
git commit -m "canon: freeze YMQ4-G1 NVIDIA implementation manifest"
```

---

### Task 2: Add typed contracts and deterministic receipt hashing

**Files:**
- Modify `quant-workspace/pyproject.toml`
- Create `src/ymq4/{__init__,contracts,canonical}.py`
- Create `tests/ymq4/test_contracts.py`

**Produces:** `Invocation`, `CapabilityResult`, `ResearchStateSnapshot`, `ResearchReceipt`, `canonical_json()`, `sha256_json()`.

- [ ] **Step 1: Add dependencies**

```toml
"requests>=2.32.0",
"psycopg[binary]>=3.2.0",

[dependency-groups]
dev = ["pytest>=8.4.0"]
```

- [ ] **Step 2: Write failing tests**

```python
from datetime import datetime, timezone
import pytest
from src.ymq4.contracts import Invocation, CapabilityResult


def test_invocation_requires_strict_pit():
    now=datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        Invocation("r1","cap","0.1","NVDA",now,now,"reference",False)


def test_result_rejects_capital_fields():
    with pytest.raises(ValueError):
        CapabilityResult(status="success", state={"buy": True})
```

- [ ] **Step 3: Verify failure**

```bash
uv run --group dev pytest tests/ymq4/test_contracts.py -v
```

- [ ] **Step 4: Implement contracts**

Recursively reject:

```python
PROHIBITED = {"buy","sell","hold","target_price","position_size","portfolio_weight","recommended_weight","expected_return"}
```

`Invocation` rejects `strict_pit=False` and `evidence_cutoff > as_of`.

- [ ] **Step 5: Add deterministic hash test and implementation**

```python
from src.ymq4.canonical import sha256_json

def test_hash_is_mapping_order_independent():
    assert sha256_json({"b":2,"a":1}) == sha256_json({"a":1,"b":2})
```

Canonical JSON uses `sort_keys=True`, separators `(',', ':')`, UTF-8, and UTC ISO-8601 datetime normalization.

- [ ] **Step 6: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_contracts.py -v
git add pyproject.toml src/ymq4 tests/ymq4/test_contracts.py
git commit -m "feat: add YMQ4 typed runtime contracts"
```

---

### Task 3: Implement PIT-safe transforms and factor frame

**Files:**
- Create `src/ymq4/transforms.py`
- Create `src/ymq4/factor_frame.py`
- Create `tests/ymq4/test_transforms.py`
- Create `tests/ymq4/test_factor_frame.py`

**Produces:** `log_returns(series)`, `trailing_zscore(series, window=63)`, `build_factor_frame(...)`.

- [ ] **Step 1: Write failing trailing-window test**

```python
import pandas as pd
from src.ymq4.transforms import trailing_zscore

def test_trailing_zscore_is_not_centered():
    s=pd.Series([1.,2.,3.,4.])
    z=trailing_zscore(s,3)
    assert pd.isna(z.iloc[1])
    assert abs(z.iloc[2]-1.0) < 1e-12
```

- [ ] **Step 2: Implement transforms and verify**

```bash
uv run --group dev pytest tests/ymq4/test_transforms.py -v
```

- [ ] **Step 3: Write PIT cutoff test**

A synthetic row with `known_as_of` after cutoff must not enter the model frame.

- [ ] **Step 4: Implement exact frame columns**

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

Regression factors exactly:

```python
X_COLUMNS=["qqq_ret","real_yield_shock","usd_shock"]
```

`FED_ASSETS` is contextual only in G1.

- [ ] **Step 5: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_transforms.py tests/ymq4/test_factor_frame.py -v
git add src/ymq4/transforms.py src/ymq4/factor_frame.py tests/ymq4
git commit -m "feat: add PIT-safe YMQ4 factor frame"
```

---

### Task 4: Implement Fixed Beta and Rolling Beta baselines

**Files:**
- Create `src/ymq4/fixed_beta.py`
- Create `src/ymq4/rolling_beta.py`
- Create `tests/ymq4/test_beta_models.py`

**Produces:** `fit_fixed_beta(y,X)` and `rolling_beta(y,X,window)`.

- [ ] **Step 1: Write coefficient-recovery test**

```python
import numpy as np, pandas as pd
from src.ymq4.fixed_beta import fit_fixed_beta

def test_fixed_beta_recovers_coefficients():
    rng=np.random.default_rng(7)
    X=pd.DataFrame(rng.normal(size=(500,3)),columns=["qqq_ret","real_yield_shock","usd_shock"])
    y=0.2 + X.to_numpy() @ np.array([1.4,-0.5,-0.2])
    est=fit_fixed_beta(pd.Series(y),X)
    assert np.allclose(list(est.betas.values()),[1.4,-0.5,-0.2],atol=1e-8)
```

- [ ] **Step 2: Implement with `np.linalg.lstsq`**

If condition number `>1e8`, emit `status="unstable"` rather than silent precision.

- [ ] **Step 3: Write rolling-window availability test**

First valid short estimate only after 63 complete rows; first valid long estimate only after 252 complete rows.

- [ ] **Step 4: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_beta_models.py -v
git add src/ymq4/fixed_beta.py src/ymq4/rolling_beta.py tests/ymq4/test_beta_models.py
git commit -m "feat: add fixed and rolling YMQ4 beta models"
```

---

### Task 5: Implement deterministic TVP/Kalman beta

**Files:**
- Create `src/ymq4/tvp_kalman.py`
- Create `tests/ymq4/test_tvp_kalman.py`

**Produces:** `fit_tvp_beta(...) -> TVPResult` with `beta_path` aligned to factor-frame index.

- [ ] **Step 1: Write constant-beta convergence test**

```python
assert np.allclose(result.beta_path.tail(50).mean().to_numpy(), true_beta, atol=0.12)
```

- [ ] **Step 2: Write regime-change test**

Synthetic rate beta changes from `-0.2` to `-1.0`; terminal estimate must be more negative than midpoint estimate.

- [ ] **Step 3: Implement NumPy random-walk Kalman filter**

Use only manifest parameters; no optimizer or auto-tuning.

- [ ] **Step 4: Add fail-closed numerics**

Non-finite covariance, singular update, or insufficient observations returns `status="fail_closed"` with warnings.

- [ ] **Step 5: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_tvp_kalman.py -v
git add src/ymq4/tvp_kalman.py tests/ymq4/test_tvp_kalman.py
git commit -m "feat: add deterministic TVP Kalman beta estimator"
```

---

### Task 6: Implement contributions, event diagnostics, drift, and hard negatives

**Files:**
- Create `src/ymq4/contribution.py`
- Create `src/ymq4/event_study.py`
- Create `src/ymq4/property_drift.py`
- Create `src/ymq4/challenge.py`
- Create `tests/ymq4/test_interpretation.py`

**Produces:** contribution map, event-associated abnormal return, pre-T0 drift thresholds/state, strongest alternative.

- [ ] **Step 1: Write contribution test**

```python
from src.ymq4.contribution import driver_contributions

def test_contribution_is_beta_times_shock():
    assert driver_contributions({"Rates":-0.5},{"Rates":2.0})["Rates"] == -1.0
```

- [ ] **Step 2: Write joint-event under-identification test**

For `earnings_narrative_bundle`, output:

```python
{"earnings_split":None,"narrative_split":None,"identification_status":"underidentified"}
```

Never split 50/50.

- [ ] **Step 3: Write drift calibration test**

T1 samples must not change P50/P75/P90 thresholds calibrated strictly before T0.

- [ ] **Step 4: Write hard-negative test**

If NVDA and QQQ move almost identically and residual is small, strongest alternative must be `broad_tech_common_factor`.

- [ ] **Step 5: Implement and commit**

```bash
uv run --group dev pytest tests/ymq4/test_interpretation.py -v
git add src/ymq4/contribution.py src/ymq4/event_study.py src/ymq4/property_drift.py src/ymq4/challenge.py tests/ymq4/test_interpretation.py
git commit -m "feat: add YMQ4 attribution drift and challenge layer"
```

---

### Task 7: Add private Supabase runtime adapter and atomic persistence

**Files:**
- Create `src/ymq4/supabase_store.py`
- Create `tests/ymq4/test_supabase_store.py`
- Modify `.env.example`

**Produces:** `load_observations(...)`, `insert_invocation(...)`, `persist_result_bundle(...)`.

- [ ] **Step 1: Write SQL-shape unit tests**

Observation SQL must include:

```sql
known_as_of <= %s
ORDER BY economic_id, observed_at, known_as_of, observation_id
```

- [ ] **Step 2: Implement fully qualified private-schema SQL**

Use `ymq4.<table>` explicitly; do not expose `ymq4` through public Data API settings.

- [ ] **Step 3: Implement one-transaction persistence**

```text
capability_invocations
→ capability_results
→ research_state_snapshots
→ research_receipts
→ COMMIT
```

Any exception rolls back all four.

- [ ] **Step 4: Add optional real-database integration test**

Run only when `YMQ4_SUPABASE_DB_URL` is set; unique test IDs are written and rolled back.

- [ ] **Step 5: Run and commit**

```bash
uv run --group dev pytest tests/ymq4/test_supabase_store.py -v
git add src/ymq4/supabase_store.py tests/ymq4/test_supabase_store.py .env.example
git commit -m "feat: add YMQ4 Supabase runtime store"
```

---

### Task 8: Build provider adapters and ingest the five PIT packs

**Files:**
- Create `src/ymq4/providers/{__init__,csv_http,market,macro}.py`
- Create `tests/ymq4/test_providers.py`

**Produces:** provider rows compatible with existing `ymq4.observations`.

- [ ] **Step 1: Write fixture-only parser tests**

No unit test uses live internet. Verify date parsing, missing values, decimal parsing, source SHA-256, symbol/series mapping.

- [ ] **Step 2: Implement `fetch_csv(url)`**

Returns `(dataframe, sha256, fetched_at)`; raises on non-200 or empty content.

- [ ] **Step 3: Implement market adapter**

NVDA/QQQ/SPY daily close rows; returns are computed later in factor frame. Provenance must record provider adjustment semantics.

- [ ] **Step 4: Implement macro adapter**

Economic IDs exactly:

```text
US2Y
US10Y
US10Y_REAL
USD_BROAD
FED_ASSETS
```

Every mapping has `revision_policy` and `publication_lag_policy`. If PIT availability cannot be defended, ingest as `authority_class="proxy"` and force a degraded result; never fabricate `vintage_at`.

- [ ] **Step 5: Ingest official event evidence**

Use only the four official URLs in Task 1. Store extracted evidence text in Supabase `value_text` with source hash and exact/conservative `known_as_of` under Task 1 law.

- [ ] **Step 6: Run PIT admission audit**

Reject rows where `known_as_of < observed_at`, both values are null, or the source policy is missing.

- [ ] **Step 7: Run tests and commit**

```bash
uv run --group dev pytest tests/ymq4/test_providers.py -v
git add src/ymq4/providers tests/ymq4/test_providers.py
git commit -m "feat: add YMQ4 G1 provider adapters"
```

---

### Task 9: Implement one-command runtime and receipt reproduction

**Files:**
- Create `src/ymq4/runtime.py`
- Create `scripts/run_ymq4_g1.py`
- Create `tests/ymq4/test_runtime.py`

**Produces:** `run_point(point, manifest, store, persist=False) -> RuntimeBundle`.

- [ ] **Step 1: Write synthetic end-to-end test**

Assert the bundle contains:

```python
bundle.result.state["dominant_driver"]
bundle.result.state["driver_contributions"]
bundle.result.state["property_drift_state"]
bundle.result.state["strongest_alternative"]
bundle.result.state["strongest_falsifier"]
bundle.result.state["residual"]
bundle.receipt.receipt_sha256
```

- [ ] **Step 2: Enforce T1 freeze checksum**

T1 uses the same manifest/factor/windows/TVP/drift/event policy checksum recorded at T0; mismatch raises and refuses persistence.

- [ ] **Step 3: Implement reliability states**

```text
fail_closed = PIT breach, missing long history, numerical failure
unknown = no driver separable from uncertainty/hard negative
partial = at least one pack proxy/missing but computation still interpretable
success = mandatory packs admitted and computation stable
```

- [ ] **Step 4: Hash before persistence**

Receipt SHA covers canonical invocation, sorted evidence refs, algorithm version, manifest hash, result state. Reproduction recomputes and compares the same hash.

- [ ] **Step 5: Implement CLI**

Exact commands after execution worktrees are created as siblings named `yuanli-invest-g1` and `quant-workspace-g1`:

```bash
cd quant-workspace-g1
export YMQ4_MANIFEST_PATH="../yuanli-invest-g1/docs/ymq4/g1/implementation-manifest.json"
uv run python scripts/run_ymq4_g1.py --point t0 --manifest "$YMQ4_MANIFEST_PATH"
uv run python scripts/run_ymq4_g1.py --point t1 --manifest "$YMQ4_MANIFEST_PATH"
```

- [ ] **Step 6: Run all tests and commit**

```bash
uv run --group dev pytest tests/ymq4 -v
git add src/ymq4/runtime.py scripts/run_ymq4_g1.py tests/ymq4/test_runtime.py
git commit -m "feat: add YMQ4 G1 runtime orchestration"
```

---

### Task 10: Execute T0, freeze the method checksum, then run held-out T1

**Files:**
- Create/modify `yuanli-invest/docs/ymq4/g1/runtime-receipts.md`
- Supabase existing `ymq4.*` tables only

**Produces:** two persisted runtime bundles and two reproduced receipt hashes.

- [ ] **Step 1: Full pre-run test gate**

```bash
cd quant-workspace-g1
uv run --group dev pytest tests/ymq4 -v
```

All unit tests PASS; Supabase integration PASS when `YMQ4_SUPABASE_DB_URL` is present.

- [ ] **Step 2: Register exact replay case IDs**

```text
YMQ4-G1-NVDA-T0-20220826
YMQ4-G1-NVDA-T1-20230525
```

Both reference the identical preregistered manifest hash.

- [ ] **Step 3: Dry-run T0**

```bash
export YMQ4_MANIFEST_PATH="../yuanli-invest-g1/docs/ymq4/g1/implementation-manifest.json"
uv run python scripts/run_ymq4_g1.py --point t0 --manifest "$YMQ4_MANIFEST_PATH"
```

Review only structural validity: PIT, five-pack coverage, numerical stability, residual visibility, challenger output, prohibited-field scan. Do not tune toward a desired driver conclusion.

- [ ] **Step 4: Persist T0 and capture machine IDs**

```bash
T0_JSON="$(uv run python scripts/run_ymq4_g1.py --point t0 --manifest "$YMQ4_MANIFEST_PATH" --persist --json)"
T0_RECEIPT_ID="$(printf '%s' "$T0_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["receipt_id"])')"
T0_RESULT_HASH="$(printf '%s' "$T0_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["typed_state_sha256"])')"
printf '%s\n' "$T0_RECEIPT_ID" "$T0_RESULT_HASH"
```

- [ ] **Step 5: Reproduce T0**

```bash
uv run python scripts/run_ymq4_g1.py --reproduce-receipt "$T0_RECEIPT_ID" --json
```

Expected JSON field: `"reproduction_status":"REPRODUCED"` and the same `typed_state_sha256`.

- [ ] **Step 6: Freeze T0 method checksum**

Runtime records SHA-256 over manifest JSON, factor list, transform parameters, windows, TVP parameters, drift thresholds, quant Git SHA. T1 must present the identical value.

- [ ] **Step 7: Persist held-out T1 with no code/config change**

```bash
T1_JSON="$(uv run python scripts/run_ymq4_g1.py --point t1 --manifest "$YMQ4_MANIFEST_PATH" --persist --json)"
T1_RECEIPT_ID="$(printf '%s' "$T1_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["receipt_id"])')"
T1_RESULT_HASH="$(printf '%s' "$T1_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["typed_state_sha256"])')"
printf '%s\n' "$T1_RECEIPT_ID" "$T1_RESULT_HASH"
```

If T1 exposes a method defect, invalidate the transfer test and version a new method; do not patch while preserving the original T1 identity.

- [ ] **Step 8: Reproduce T1**

```bash
uv run python scripts/run_ymq4_g1.py --reproduce-receipt "$T1_RECEIPT_ID" --json
```

Expected: `REPRODUCED` and identical `typed_state_sha256`.

- [ ] **Step 9: Record runtime pointers in Canon**

`runtime-receipts.md` records T0/T1 request/result/snapshot/receipt IDs, manifest hash, quant commit SHA, status, and reproduction status only. It must not convert research state into capital advice.

- [ ] **Step 10: Commit Canon runtime pointers**

```bash
cd ../yuanli-invest-g1
git add docs/ymq4/g1/runtime-receipts.md
git commit -m "receipt: record YMQ4-G1 NVIDIA Genesis Pair runtime pointers"
```

---

## Final Verification Gate

Run:

```bash
cd ../quant-workspace-g1
uv run --group dev pytest tests/ymq4 -v
uv run python scripts/run_ymq4_g1.py --reproduce-receipt "$T0_RECEIPT_ID" --json
uv run python scripts/run_ymq4_g1.py --reproduce-receipt "$T1_RECEIPT_ID" --json
```

Then verify Supabase minimum cardinality:

```sql
select count(*) from ymq4.capability_invocations where target_id='NVDA';
select count(*) from ymq4.capability_results r join ymq4.capability_invocations i using(request_id) where i.target_id='NVDA';
select count(*) from ymq4.research_state_snapshots where target_id='NVDA';
select count(*) from ymq4.research_receipts rr join ymq4.capability_invocations i using(request_id) where i.target_id='NVDA';
```

Expected G1 minimum: at least 2 real NVDA invocations, 2 results, 2 snapshots, 2 receipts, zero known PIT violations, and T0/T1 reproduction success.

Allowed final settlement: `PASS`, `PARTIAL`, or `FAIL_CLOSED`. A scientifically disappointing driver result is not engineering failure. Hidden leakage, non-reproducibility, post-T1 retuning, or capital-authority leakage is failure.

## Self-Review Coverage

- Genesis pair / held-out law: Tasks 1, 9, 10.
- Five packs: Tasks 1, 8.
- PIT observation law: Tasks 3, 7, 8.
- Fixed / Rolling / TVP: Tasks 4, 5.
- Contribution + residual: Task 6.
- Property drift: Task 6.
- Hard negatives: Task 6.
- Invocation → Result → State → Receipt: Tasks 7, 9, 10.
- Receipt reproduction: Tasks 2, 9, 10.
- No capital authority: Tasks 1, 2, 9, final gate.
- No T1 tuning: Tasks 1, 9, 10.
- No new Supabase tables: Global Constraints + Tasks 7, 10.

No `TBD`, `TODO`, hidden tuning step, or unresolved placeholder is permitted by this plan.
