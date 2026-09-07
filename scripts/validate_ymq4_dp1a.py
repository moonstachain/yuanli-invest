#!/usr/bin/env python3
from __future__ import annotations
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
required = [
    ROOT / "config/ymq4/gold_source_authority.v0.1.json",
    ROOT / "supabase/migrations/20260907163100_ymq4_dp1a_reality_proof.sql",
    ROOT / "supabase/migrations/20260907171500_ymq4_dp1a_rest_rpc_hardening.sql",
    ROOT / "supabase/migrations/20260907173000_ymq4_dp1a_storage_bucket.sql",
    ROOT / "scripts/ymq4_dp1a_reality_proof.py",
    ROOT / ".github/workflows/ymq4-dp1a-reality-proof.yml",
    ROOT / "docs/architecture/ymq4/YMQ4-DP1-A-REALITY-PROOF-v0.1.md",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"missing DP1-A artifacts: {missing}")

reg = json.loads((ROOT / "config/ymq4/gold_source_authority.v0.1.json").read_text())
assert reg["battle"] == "YMQ4-DP1-A"
assert reg["core_reality_gate"]["future_leakage_tolerance"] == 0
assert reg["proof_series"]["required_output_type"] == 4

all_text = "\n".join(p.read_text(errors="ignore") for p in required)
for forbidden in [r"sk-[A-Za-z0-9]", r"sb_secret_[A-Za-z0-9_-]{12,}", r"service_role\s*[:=]\s*['\"]", r"api_key=[A-Za-z0-9]{20,}"]:
    if re.search(forbidden, all_text, flags=re.I):
        raise SystemExit(f"possible secret literal found by pattern: {forbidden}")

rpc_sql = (ROOT / "supabase/migrations/20260907171500_ymq4_dp1a_rest_rpc_hardening.sql").read_text()
for fn in ("ymq4_dp1a_ingest", "ymq4_dp1a_readback", "ymq4_dp1a_record_gate"):
    assert fn in rpc_sql
assert "grant execute" in rpc_sql.lower() and "service_role" in rpc_sql
assert "revoke all" in rpc_sql.lower() and "anon" in rpc_sql and "authenticated" in rpc_sql

bucket_sql = (ROOT / "supabase/migrations/20260907173000_ymq4_dp1a_storage_bucket.sql").read_text()
assert "ymq4-raw-evidence" in bucket_sql and "false" in bucket_sql.lower()

workflow = (ROOT / ".github/workflows/ymq4-dp1a-reality-proof.yml").read_text()
for required_secret in (
    "FRED_API_KEY",
    "YMQ4_SUPABASE_SECRET_KEY",
    "YMQ4_SUPABASE_S3_ACCESS_KEY_ID",
    "YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY",
):
    assert required_secret in workflow
assert "YMQ4_SUPABASE_SERVICE_ROLE_KEY" not in workflow

runner = (ROOT / "scripts/ymq4_dp1a_reality_proof.py").read_text()
assert '"apikey": secret_key' in runner
assert '"Authorization"' not in runner
assert "storage.supabase.co/storage/v1/s3" in runner

print("YMQ4-DP1-A validator: PASS")
