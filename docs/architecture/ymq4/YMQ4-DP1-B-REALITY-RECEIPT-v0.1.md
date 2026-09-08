# YMQ4-DP1-B｜Gold 1978–2026 Historical PIT Backfill Reality Receipt v0.1

**Settlement:** `DP1B_CORE_BACKFILL_PASS`  
**Battle:** `YMQ4-DP1-B`  
**Panel:** `gold_core_monthly_v0.1`  
**Completed:** `2026-09-08T06:29:26.391211+00:00`

## 1. What this receipt proves

A physical historical Gold research data plane was executed from governed external sources through immutable raw-object capture, provenance snapshots, PIT/as-of reconstruction, monthly decision-state materialization, database readback, replay-window coverage audit, future-leakage audit, and a persisted Reality Gate receipt.

This is a **data-plane closure only**. It does not promote any research thesis to Canon and does not authorize B3-B7, portfolio sizing, broker connectivity, or trading action.

## 2. Execution identity

- GitHub Actions run: `34194178721`
- PR: `#69`
- Source branch at launch: `ymq4-dp1b-gold-historical-pit-backfill`
- PR head at launch: `9c2fa05a8753d4e3926c74f922702da141f436f0`
- Executed PR merge SHA: `eaccf43ee02fd1e91b5da4b39f92433d73f00e0d`
- Reality Gate run id: `df45f989-7295-4da4-8492-f8f8500690d6`
- Runtime interval: `2026-09-08T06:20:01.203004+00:00` → `2026-09-08T06:29:26.391211+00:00`

## 3. Physical panel settlement

```text
period: 1978-01-31 → 2026-08-31
month-end states: 584
core factors: 4
panel_rows: 2336
null_values: 0
distinct_keys: 2336
future_leakage: 0
B2-B7 executed during DP1-B: false
```

Independent Supabase readback reproduced the physical panel state after the workflow completed:

| Factor | Rows |
|---|---:|
| `gold_usd_oz` | 584 |
| `usd` | 584 |
| `inflation_yoy` | 584 |
| `real_rate` | 584 |
| **Total** | **2336** |

Measurement-regime row counts:

| Regime | Rows |
|---|---:|
| `1978_2002_proxy` | 1200 |
| `2003_2005_tips_legacy_usd` | 144 |
| `2006_plus_modern` | 992 |

## 4. Replay coverage gate

The frozen pass threshold was `>= 0.80` complete-month coverage, requiring all four core factors in a month. Physical settlement was:

| Replay window | Complete / Expected | Coverage | Result |
|---|---:|---:|---|
| Gold 1978–1979 | 24 / 24 | 1.00 | PASS |
| GFC 2008–2009 | 24 / 24 | 1.00 | PASS |
| COVID 2020 | 12 / 12 | 1.00 | PASS |
| Rate Shock 2022 | 12 / 12 | 1.00 | PASS |
| 2023–2026 current regime, clamped to 2026-08 | 44 / 44 | 1.00 | PASS |

All five replay windows therefore passed without lowering the preregistered threshold.

## 5. Future-leakage gate

Database constraint and independent post-run query both returned:

```text
known_as_of > decision_date: 0 rows
future_leakage_tolerance: 0
result: PASS
```

No post-reveal relaxation was made.

## 6. Repository-scope closure

The later stacked-PR repository failure was traced to a YIM0 validator scope-window bug: `validate_yim0_methodology_projection.py` used a fixed historical `BASE_SHA...HEAD` diff and therefore misclassified legitimate post-YIM0 YMQ4 files as YIM0 modifications.

The fix changed the validator to audit only YIM0's frozen `semantic_merge_commit` diff. A regression test was added in `tests/test_yim0_scope_window.py`.

Fresh repository-gates run `34195906929` passed both jobs:

```text
governance: PASS
contracts:  PASS
YIM0 validator: PASS
full unit test suite: PASS
```

Therefore PR #69 reached repository-wide clean state while remaining Draft/Open/Not Merged.

## 7. Successor authorization boundary

After repository-wide clean closure, B2 was separately authorized as the next research battle. That later authorization does not retroactively change the DP1-B runtime claim above: DP1-B itself executed no B2-B7 model logic.
