#!/usr/bin/env python3
"""YMQ4-DP1-A physical closure proof.

Proof chain:
GitHub Actions -> FRED/ALFRED initial release -> immutable raw object ->
Supabase S3 private bucket -> service-role-only RPC -> evidence.source_snapshots +
pit.observations -> RPC readback -> runtime.reality_gate_runs.

The worker uses two deliberately separate backend credentials:
- modern Supabase secret key (`sb_secret_...`) for PostgREST RPC, sent on `apikey` only;
- dedicated Supabase S3 access key pair for raw object storage.

Fail-closed on missing secrets, missing four-clock semantics, as-of mismatch,
raw SHA mismatch, database readback mismatch, or any external/API error.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations"
SERIES_ID = os.getenv("YMQ4_PROOF_SERIES", "CPIAUCSL")
OBS_START = os.getenv("YMQ4_PROOF_OBS_START", "2020-02-01")
OBS_END = os.getenv("YMQ4_PROOF_OBS_END", OBS_START)
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")
SUPABASE_PROJECT_REF = os.getenv("YMQ4_SUPABASE_PROJECT_REF", "tbmoimbdhsrltvospwpu")
SUPABASE_REGION = os.getenv("YMQ4_SUPABASE_REGION", "us-east-2")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required secret/env missing: {name}")
    return value


def request_bytes(url: str, headers: dict[str, str] | None = None, data: bytes | None = None, method: str | None = None) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, dict(resp.headers.items()), resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()
        raise RuntimeError(f"HTTP {e.code} for {url}: {body[:500]!r}") from e


def fred_url(api_key: str, **overrides: Any) -> str:
    params = {
        "series_id": SERIES_ID,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": OBS_START,
        "observation_end": OBS_END,
        "output_type": 4,
    }
    params.update(overrides)
    return FRED_ENDPOINT + "?" + urllib.parse.urlencode(params)


def redact_api_key(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    q2 = [(k, "REDACTED" if k == "api_key" else v) for k, v in q]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(q2), parsed.fragment))


def parse_initial(raw: bytes) -> dict[str, Any]:
    payload = json.loads(raw)
    rows = [o for o in payload.get("observations", []) if o.get("value") not in (None, ".")]
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one non-missing initial observation, got {len(rows)}")
    row = rows[0]
    release = row.get("realtime_start")
    if not release:
        raise RuntimeError("initial-release row lacks realtime_start; cannot establish four clocks")
    if row.get("date") != OBS_START:
        raise RuntimeError(f"unexpected observation date: {row.get('date')} != {OBS_START}")
    return {
        "series_id": SERIES_ID,
        "value": float(row["value"]),
        "observation_date": row["date"],
        "release_date": release,
        "vintage_date": release,
        "known_as_of": release,
    }


def crosscheck_asof(api_key: str, initial: dict[str, Any]) -> bytes:
    d = initial["known_as_of"]
    url = fred_url(api_key, output_type=1, realtime_start=d, realtime_end=d)
    _, _, raw = request_bytes(url)
    payload = json.loads(raw)
    rows = [o for o in payload.get("observations", []) if o.get("value") not in (None, ".")]
    if len(rows) != 1:
        raise RuntimeError(f"as-of crosscheck expected one observation, got {len(rows)}")
    if abs(float(rows[0]["value"]) - initial["value"]) > 1e-12:
        raise RuntimeError("initial-release value does not match same-day as-of read")
    return raw


def rpc_headers(secret_key: str) -> dict[str, str]:
    if not secret_key.startswith("sb_secret_"):
        raise RuntimeError("YMQ4_SUPABASE_SECRET_KEY must be a modern sb_secret_ key")
    return {"apikey": secret_key, "Content-Type": "application/json"}


def rpc(supabase_url: str, secret_key: str, function_name: str, payload: dict[str, Any]) -> Any:
    url = supabase_url.rstrip("/") + "/rest/v1/rpc/" + function_name
    _, _, raw = request_bytes(url, rpc_headers(secret_key), json.dumps(payload).encode(), "POST")
    return json.loads(raw or b"null")


def s3_client(access_key_id: str, secret_access_key: str):
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise RuntimeError("boto3 is required for the full DP1-A S3 proof") from exc
    endpoint = f"https://{SUPABASE_PROJECT_REF}.storage.supabase.co/storage/v1/s3"
    return boto3.client(
        "s3",
        region_name=SUPABASE_REGION,
        endpoint_url=endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def verify_private_bucket(client) -> None:
    try:
        client.head_bucket(Bucket=BUCKET)
    except Exception as exc:
        raise RuntimeError(f"required private raw bucket is not reachable: {BUCKET}") from exc


def upload_raw_s3(client, path: str, raw: bytes, expected_sha: str) -> None:
    client.put_object(
        Bucket=BUCKET,
        Key=path,
        Body=raw,
        ContentType="application/json",
        Metadata={"sha256": expected_sha, "proof-contract": "YMQ4-DP1-A"},
    )
    obj = client.get_object(Bucket=BUCKET, Key=path)
    reread = obj["Body"].read()
    got = hashlib.sha256(reread).hexdigest()
    if got != expected_sha:
        raise RuntimeError(f"raw storage SHA mismatch: {got} != {expected_sha}")
    metadata_sha = (obj.get("Metadata") or {}).get("sha256")
    if metadata_sha != expected_sha:
        raise RuntimeError(f"raw storage metadata SHA mismatch: {metadata_sha} != {expected_sha}")


def main() -> int:
    started = datetime.now(timezone.utc)
    fred_api_key = require_env("FRED_API_KEY")
    sb_url = require_env("SUPABASE_URL")
    sb_secret_key = require_env("YMQ4_SUPABASE_SECRET_KEY")
    s3_access_key_id = require_env("YMQ4_SUPABASE_S3_ACCESS_KEY_ID")
    s3_secret_access_key = require_env("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")
    git_sha = os.getenv("GITHUB_SHA", "LOCAL")

    expected_url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
    if sb_url.rstrip("/") != expected_url:
        raise RuntimeError(f"SUPABASE_URL project-ref mismatch: {sb_url!r} != {expected_url!r}")

    initial_url = fred_url(fred_api_key)
    http_status, headers, raw_initial = request_bytes(initial_url)
    initial = parse_initial(raw_initial)
    raw_asof = crosscheck_asof(fred_api_key, initial)

    envelope = json.dumps({
        "proof_contract": "YMQ4-DP1-A",
        "initial_release_response": json.loads(raw_initial),
        "same_day_asof_response": json.loads(raw_asof),
    }, separators=(",", ":"), sort_keys=True).encode()
    sha = hashlib.sha256(envelope).hexdigest()
    retrieved_at = datetime.now(timezone.utc)
    object_path = f"fred/{SERIES_ID}/{retrieved_at.strftime('%Y/%m/%d/%H%M%S')}-{sha}.json"

    storage = s3_client(s3_access_key_id, s3_secret_access_key)
    verify_private_bucket(storage)
    upload_raw_s3(storage, object_path, envelope, sha)

    ingest = rpc(sb_url, sb_secret_key, "ymq4_dp1a_ingest", {
        "p_source_id": "fred_cpiaucsl",
        "p_retrieved_at": retrieved_at.isoformat(),
        "p_http_status": http_status,
        "p_content_type": headers.get("Content-Type", "application/json"),
        "p_sha256": sha,
        "p_storage_bucket": BUCKET,
        "p_storage_path": object_path,
        "p_request_template": redact_api_key(initial_url),
        "p_runner_commit": git_sha,
        "p_series_id": initial["series_id"],
        "p_value_numeric": initial["value"],
        "p_observation_date": initial["observation_date"],
        "p_release_date": initial["release_date"],
        "p_vintage_date": initial["vintage_date"],
        "p_known_as_of": initial["known_as_of"],
        "p_pit_status": "PIT_STRICT_INITIAL_RELEASE",
        "p_measurement_regime": "DP1A_PROOF",
    })
    if not isinstance(ingest, list) or len(ingest) != 1:
        raise RuntimeError(f"ingest RPC expected one row, got {ingest!r}")
    snapshot_id = ingest[0]["snapshot_id"]
    observation_id = ingest[0]["observation_id"]

    reread = rpc(sb_url, sb_secret_key, "ymq4_dp1a_readback", {
        "p_series_id": SERIES_ID,
        "p_observation_date": initial["observation_date"],
        "p_known_as_of": initial["known_as_of"],
    })
    if not isinstance(reread, list) or len(reread) != 1:
        raise RuntimeError(f"readback RPC expected one row, got {reread!r}")
    row = reread[0]
    if row["snapshot_id"] != snapshot_id or row["observation_id"] != observation_id:
        raise RuntimeError("RPC identity readback mismatch")
    if row["sha256"] != sha or row["storage_bucket"] != BUCKET or row["storage_path"] != object_path:
        raise RuntimeError("provenance readback mismatch")
    if abs(float(row["value_numeric"]) - initial["value"]) > 1e-12:
        raise RuntimeError("PIT observation readback value mismatch")
    for clock in ("observation_date", "release_date", "vintage_date", "known_as_of"):
        if row[clock] != initial[clock]:
            raise RuntimeError(f"four-clock readback mismatch for {clock}: {row[clock]} != {initial[clock]}")

    receipt = {
        "battle": "YMQ4-DP1-A",
        "status": "PASS",
        "git_sha": git_sha,
        "source": "FRED/ALFRED",
        "series_id": SERIES_ID,
        "four_clocks": {k: initial[k] for k in ("observation_date", "release_date", "vintage_date", "known_as_of")},
        "value": initial["value"],
        "raw_sha256": sha,
        "storage": {"bucket": BUCKET, "path": object_path, "transport": "Supabase S3"},
        "snapshot_id": snapshot_id,
        "pit_observation_id": observation_id,
        "checks": {
            "external_runtime": "PASS",
            "source_reachability": "PASS",
            "initial_release": "PASS",
            "same_day_asof_crosscheck": "PASS",
            "raw_storage_sha_readback": "PASS",
            "modern_secret_rpc_ingest": "PASS",
            "pit_ledger_write_readback": "PASS",
            "provenance_readback": "PASS"
        },
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    gate_run_id = rpc(sb_url, sb_secret_key, "ymq4_dp1a_record_gate", {
        "p_battle_id": "YMQ4-DP1-A",
        "p_git_sha": git_sha,
        "p_started_at": receipt["started_at"],
        "p_completed_at": receipt["completed_at"],
        "p_gate_status": "PASS",
        "p_receipt": receipt,
    })
    receipt["reality_gate_run_id"] = gate_run_id
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"battle": "YMQ4-DP1-A", "status": "FAIL_CLOSED", "error": repr(exc)}, indent=2), file=sys.stderr)
        raise
