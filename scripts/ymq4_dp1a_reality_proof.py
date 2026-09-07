#!/usr/bin/env python3
"""YMQ4-DP1-A physical closure proof.

Proof chain:
GitHub Actions -> FRED/ALFRED initial release -> immutable raw object ->
Supabase Storage -> service-role-only RPC -> evidence.source_snapshots +
pit.observations -> RPC readback -> runtime.reality_gate_runs.

Fail-closed on missing secrets, missing four-clock semantics, as-of mismatch,
raw SHA mismatch, database readback mismatch, or any HTTP error.
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


def sb_headers(service_key: str, content_type: str = "application/json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": content_type,
    }


def ensure_bucket(supabase_url: str, service_key: str) -> None:
    body = json.dumps({"id": BUCKET, "name": BUCKET, "public": False}).encode()
    url = supabase_url.rstrip("/") + "/storage/v1/bucket"
    try:
        request_bytes(url, sb_headers(service_key), body, "POST")
    except RuntimeError as exc:
        status, _, raw = request_bytes(url + "/" + urllib.parse.quote(BUCKET), sb_headers(service_key))
        if status != 200:
            raise exc
        info = json.loads(raw)
        if info.get("id") != BUCKET or info.get("public") is True:
            raise RuntimeError("existing bucket does not satisfy private-bucket contract")


def upload_raw(supabase_url: str, service_key: str, path: str, raw: bytes, expected_sha: str) -> None:
    base = supabase_url.rstrip("/") + "/storage/v1/object/" + urllib.parse.quote(BUCKET) + "/" + urllib.parse.quote(path, safe="/")
    headers = sb_headers(service_key, "application/json")
    headers["x-upsert"] = "false"
    request_bytes(base, headers, raw, "POST")
    download = supabase_url.rstrip("/") + "/storage/v1/object/authenticated/" + urllib.parse.quote(BUCKET) + "/" + urllib.parse.quote(path, safe="/")
    _, _, reread = request_bytes(download, sb_headers(service_key))
    got = hashlib.sha256(reread).hexdigest()
    if got != expected_sha:
        raise RuntimeError(f"raw storage SHA mismatch: {got} != {expected_sha}")


def rpc(supabase_url: str, service_key: str, function_name: str, payload: dict[str, Any]) -> Any:
    url = supabase_url.rstrip("/") + "/rest/v1/rpc/" + function_name
    _, _, raw = request_bytes(url, sb_headers(service_key), json.dumps(payload).encode(), "POST")
    return json.loads(raw or b"null")


def main() -> int:
    started = datetime.now(timezone.utc)
    api_key = require_env("FRED_API_KEY")
    sb_url = require_env("SUPABASE_URL")
    sb_key = require_env("SUPABASE_SERVICE_ROLE_KEY")
    git_sha = os.getenv("GITHUB_SHA", "LOCAL")

    initial_url = fred_url(api_key)
    http_status, headers, raw_initial = request_bytes(initial_url)
    initial = parse_initial(raw_initial)
    raw_asof = crosscheck_asof(api_key, initial)

    envelope = json.dumps({
        "proof_contract": "YMQ4-DP1-A",
        "initial_release_response": json.loads(raw_initial),
        "same_day_asof_response": json.loads(raw_asof),
    }, separators=(",", ":"), sort_keys=True).encode()
    sha = hashlib.sha256(envelope).hexdigest()
    retrieved_at = datetime.now(timezone.utc)
    object_path = f"fred/{SERIES_ID}/{retrieved_at.strftime('%Y/%m/%d/%H%M%S')}-{sha}.json"

    ensure_bucket(sb_url, sb_key)
    upload_raw(sb_url, sb_key, object_path, envelope, sha)

    ingest = rpc(sb_url, sb_key, "ymq4_dp1a_ingest", {
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

    reread = rpc(sb_url, sb_key, "ymq4_dp1a_readback", {
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
        "storage": {"bucket": BUCKET, "path": object_path},
        "snapshot_id": snapshot_id,
        "pit_observation_id": observation_id,
        "checks": {
            "external_runtime": "PASS",
            "source_reachability": "PASS",
            "initial_release": "PASS",
            "same_day_asof_crosscheck": "PASS",
            "raw_storage_sha_readback": "PASS",
            "service_role_rpc_ingest": "PASS",
            "pit_ledger_write_readback": "PASS",
            "provenance_readback": "PASS"
        },
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    gate_run_id = rpc(sb_url, sb_key, "ymq4_dp1a_record_gate", {
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
