#!/usr/bin/env python3
"""YMQ4-DP1-A physical closure proof.

Proof chain:
GitHub Actions -> FRED/ALFRED initial release -> immutable raw object ->
Supabase evidence.source_snapshots -> pit.observations -> readback -> receipt.

Fail-closed: missing secrets, missing realtime_start, inconsistent as-of value,
failed storage hash readback, or failed DB readback causes non-zero exit.
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
    _, _, reread = request_bytes(supabase_url.rstrip("/") + "/storage/v1/object/authenticated/" + urllib.parse.quote(BUCKET) + "/" + urllib.parse.quote(path, safe="/"), sb_headers(service_key))
    got = hashlib.sha256(reread).hexdigest()
    if got != expected_sha:
        raise RuntimeError(f"raw storage SHA mismatch: {got} != {expected_sha}")


def rest_post(supabase_url: str, service_key: str, table_path: str, row: dict[str, Any], prefer: str = "return=representation") -> list[dict[str, Any]]:
    url = supabase_url.rstrip("/") + "/rest/v1/" + table_path
    headers = sb_headers(service_key)
    headers["Prefer"] = prefer
    _, _, raw = request_bytes(url, headers, json.dumps(row).encode(), "POST")
    return json.loads(raw or b"[]")


def rest_get(supabase_url: str, service_key: str, table_path: str, query: str) -> list[dict[str, Any]]:
    url = supabase_url.rstrip("/") + "/rest/v1/" + table_path + "?" + query
    _, _, raw = request_bytes(url, sb_headers(service_key))
    return json.loads(raw or b"[]")


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

    snapshots = rest_post(sb_url, sb_key, "evidence.source_snapshots", {
        "source_id": "fred_cpiaucsl",
        "retrieved_at": retrieved_at.isoformat(),
        "http_status": http_status,
        "content_type": headers.get("Content-Type", "application/json"),
        "sha256": sha,
        "storage_bucket": BUCKET,
        "storage_path": object_path,
        "request_template": redact_api_key(initial_url),
        "runner_commit": git_sha,
    })
    if not snapshots:
        snapshots = rest_get(sb_url, sb_key, "evidence.source_snapshots", f"source_id=eq.fred_cpiaucsl&sha256=eq.{sha}&select=*")
    if len(snapshots) != 1:
        raise RuntimeError(f"snapshot readback expected one row, got {len(snapshots)}")
    snapshot_id = snapshots[0]["snapshot_id"]

    rest_post(sb_url, sb_key, "pit.observations", {
        "series_id": initial["series_id"],
        "value_numeric": initial["value"],
        "observation_date": initial["observation_date"],
        "release_date": initial["release_date"],
        "vintage_date": initial["vintage_date"],
        "known_as_of": initial["known_as_of"],
        "source_snapshot_id": snapshot_id,
        "pit_status": "PIT_STRICT_INITIAL_RELEASE",
        "measurement_regime": "DP1A_PROOF",
    }, prefer="resolution=ignore-duplicates,return=representation")
    reread = rest_get(sb_url, sb_key, "pit.observations", f"series_id=eq.{SERIES_ID}&observation_date=eq.{initial['observation_date']}&known_as_of=eq.{initial['known_as_of']}&select=*")
    if len(reread) != 1:
        raise RuntimeError(f"PIT observation readback expected one row, got {len(reread)}")
    if abs(float(reread[0]["value_numeric"]) - initial["value"]) > 1e-12:
        raise RuntimeError("PIT observation readback value mismatch")

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
        "pit_observation_id": reread[0]["observation_id"],
        "checks": {
            "external_runtime": "PASS",
            "source_reachability": "PASS",
            "initial_release": "PASS",
            "same_day_asof_crosscheck": "PASS",
            "raw_storage_sha_readback": "PASS",
            "pit_ledger_write_readback": "PASS"
        },
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    rest_post(sb_url, sb_key, "runtime.reality_gate_runs", {
        "battle_id": "YMQ4-DP1-A",
        "git_sha": git_sha,
        "started_at": receipt["started_at"],
        "completed_at": receipt["completed_at"],
        "gate_status": "PASS",
        "receipt": receipt,
    })
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"battle": "YMQ4-DP1-A", "status": "FAIL_CLOSED", "error": repr(exc)}, indent=2), file=sys.stderr)
        raise
