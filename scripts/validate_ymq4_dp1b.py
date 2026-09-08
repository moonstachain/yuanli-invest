#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
required = [
    ROOT / "config/ymq4/gold_dp1b_backfill.v0.1.json",
    ROOT / "docs/architecture/ymq4/YMQ4-DP1-B-REALITY-RECEIPT-v0.1.md",
    ROOT / "docs/superpowers/specs/2026-09-08-ymq4-dp1b-gold-historical-pit-backfill-design.md",
    ROOT / "docs/superpowers/plans/2026-09-08-ymq4-dp1b-gold-historical-pit-backfill.md",
    ROOT / "scripts/ymq4_dp1b_backfill.py",
    ROOT / "supabase/migrations/20260908060000_ymq4_dp1b_historical_backfill.sql",
    ROOT / ".github/workflows/ymq4-dp1b-historical-backfill.yml",
    ROOT / "tests/test_ymq4_dp1b.py",
    ROOT / "tests/test_ymq4_dp1b_contract.py",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"missing DP1-B artifacts: {missing}")

config = json.loads((ROOT / "config/ymq4/gold_dp1b_backfill.v0.1.json").read_text())
assert config["battle"] == "YMQ4-DP1-B"
assert config["status"] == "reality_proof_pass"
assert config["future_leakage_tolerance"] == 0
assert config["minimum_replay_month_coverage"] == 0.80
assert config["core_factors"] == ["gold_usd_oz", "usd", "inflation_yoy", "real_rate"]
settlement = config["settlement"]
assert settlement["gate_status"] == "DP1B_CORE_BACKFILL_PASS"
assert settlement["panel_rows"] == 2336
assert settlement["months"] == 584
assert settlement["future_leakage"] == 0
assert settlement["all_replay_windows_pass"] is True
assert settlement["b2_b7_executed"] is False
source_ids = {item["source_id"] for item in config["sources"].values()}
required_source_ids = {
    "worldbank_pinksheet_gold", "fred_cpiaucsl", "fred_dtb3",
    "fred_dtwexm", "fred_dtwexbgs", "fred_dfii10",
}
assert source_ids == required_source_ids
assert config["sources"]["gold"]["source_class"] == "PIT_MARKET_RECONSTRUCTED"

receipt = (ROOT / "docs/architecture/ymq4/YMQ4-DP1-B-REALITY-RECEIPT-v0.1.md").read_text()
for token in (
    "DP1B_CORE_BACKFILL_PASS",
    "panel_rows: 2336",
    "future_leakage: 0",
    "B2-B7 executed: false",
    "df45f989-7295-4da4-8492-f8f8500690d6",
):
    assert token in receipt, f"reality receipt missing settlement token: {token}"

migration = (ROOT / "supabase/migrations/20260908060000_ymq4_dp1b_historical_backfill.sql").read_text()
low_migration = migration.lower()
for token in ("pit.decision_asof_values", "known_as_of <= decision_date", "enable row level security"):
    assert token in low_migration
for fn in ("ymq4_dp1b_ingest_source", "ymq4_dp1b_upsert_panel", "ymq4_dp1b_readback", "ymq4_dp1b_record_gate"):
    assert fn in migration
assert "revoke all" in low_migration and "anon" in low_migration and "authenticated" in low_migration
assert "grant execute" in low_migration and "service_role" in low_migration

workflow = (ROOT / ".github/workflows/ymq4-dp1b-historical-backfill.yml").read_text()
for secret in (
    "FRED_API_KEY", "YMQ4_SUPABASE_SECRET_KEY",
    "YMQ4_SUPABASE_S3_ACCESS_KEY_ID", "YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY",
):
    assert secret in workflow, f"workflow missing secret contract: {secret}"
assert "intentionally disabled until TDD implementation is green" not in workflow
assert "github.event_name == 'workflow_dispatch' && inputs.mode == 'full'" in workflow

runner = (ROOT / "scripts/ymq4_dp1b_backfill.py").read_text()
for semantic in (
    "PIT_MARKET_RECONSTRUCTED", "PIT_STRICT_ASOF_DERIVED", "PIT_DERIVED_PROXY",
    "DTB3_MINUS_CPI_YOY_ASOF", "DFII10", "DTWEXM", "DTWEXBGS",
    "future_leakage_count", "coverage_report", "DP1B_CORE_BACKFILL_PASS",
):
    assert semantic in runner, f"runner missing frozen semantic: {semantic}"

# No model or execution escalation may enter this data-plane battle.
for forbidden_runtime in (
    "import models", "from models", "rolling_beta", "kalman", "tvp_beta",
    "broker", "place_order", "submit_order", "portfolio_size",
):
    if forbidden_runtime in runner.lower():
        raise SystemExit(f"DP1-B runner contains forbidden execution/model token: {forbidden_runtime}")

all_text = "\n".join(p.read_text(errors="ignore") for p in required)
for forbidden_secret in (
    r"sb_secret_[A-Za-z0-9_-]{12,}",
    r"service_role\s*[:=]\s*['\"][A-Za-z0-9._-]{12,}",
    r"api_key=[A-Za-z0-9]{20,}",
):
    if re.search(forbidden_secret, all_text, flags=re.I):
        raise SystemExit(f"possible secret literal found: {forbidden_secret}")

print("YMQ4-DP1-B validator: PASS")
