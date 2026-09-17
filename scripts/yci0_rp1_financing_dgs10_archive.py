#!/usr/bin/env python3
from __future__ import annotations

import calendar
import csv
import hashlib
import io
import json
import os
import time
import urllib.request
from datetime import date, datetime, timezone

PROJECT_REF = "tbmoimbdhsrltvospwpu"
REGION = "us-east-2"
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")
SOURCE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
TARGET_MONTHS = ((2026, 4), (2026, 5), (2026, 6), (2026, 7))


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required secret binding: {name}")
    return value


def extract_month_end_points(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8")
    parsed = []
    for row in csv.DictReader(io.StringIO(text)):
        value = (row.get("DGS10") or "").strip()
        if value in {"", ".", "NA"}:
            continue
        parsed.append((date.fromisoformat(row["observation_date"]), float(value)))

    out = []
    for year, month in TARGET_MONTHS:
        month_end = date(year, month, calendar.monthrange(year, month)[1])
        candidates = [(d, v) for d, v in parsed if d.year == year and d.month == month and d <= month_end]
        if not candidates:
            raise RuntimeError(f"missing complete-month observation for {year}-{month:02d}")
        observed, value = max(candidates, key=lambda item: item[0])
        out.append({
            "month_end": month_end.isoformat(),
            "observation_date": observed.isoformat(),
            "value_pct": value,
        })
    return out


def download() -> tuple[int, str, bytes]:
    req = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "YuanliResearchEvidenceBot/1.0", "Accept": "text/csv,*/*"},
    )
    last_error = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.status, resp.headers.get("Content-Type", "text/csv"), resp.read()
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"DGS10 download failed after retries: {type(last_error).__name__}")


def s3_client(access_key: str, secret_key: str):
    import boto3
    from botocore.config import Config
    endpoint = f"https://{PROJECT_REF}.storage.supabase.co/storage/v1/s3"
    return boto3.client(
        "s3",
        region_name=REGION,
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def main() -> int:
    access_key = require_env("YMQ4_SUPABASE_S3_ACCESS_KEY_ID")
    secret_key = require_env("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")
    status, content_type, raw = download()
    if status != 200:
        raise RuntimeError(f"FRED DGS10 HTTP status != 200: {status}")
    points = extract_month_end_points(raw)
    sha = hashlib.sha256(raw).hexdigest()
    key = f"yci0-rp1/financing/dgs10/{sha}.csv"
    client = s3_client(access_key, secret_key)
    client.head_bucket(Bucket=BUCKET)
    client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=raw,
        ContentType=content_type,
        Metadata={"sha256": sha, "proof-contract": "YCI0-RP1-G5-FINANCING-DGS10"},
    )
    reread = client.get_object(Bucket=BUCKET, Key=key)["Body"].read()
    reread_sha = hashlib.sha256(reread).hexdigest()
    if reread_sha != sha:
        raise RuntimeError(f"S3 SHA mismatch: {reread_sha} != {sha}")
    print(json.dumps({
        "program": "YCI0-RP1",
        "gate": "G5_FINANCING_DGS10_RAW_EVIDENCE",
        "status": "PASS",
        "provider": "FRED / Federal Reserve H.15",
        "source_role": "OFFICIAL_STRUCTURED_SENSOR",
        "source_url": SOURCE_URL,
        "series_id": "DGS10",
        "canonical_metric_id": "AIINFRA.RATES.US10Y_NOMINAL",
        "measurement_regime": "MONTH_END_LAST_AVAILABLE_MARKET_OBSERVATION",
        "sample_policy": "last valid daily observation in each complete month Apr-Jul 2026",
        "points": points,
        "http_status": status,
        "content_type": content_type,
        "bytes": len(raw),
        "sha256": sha,
        "storage_bucket": BUCKET,
        "storage_path": key,
        "storage_readback_sha256": reread_sha,
        "authority": {
            "evidence_promotion_authorized": False,
            "research_authorized": False,
            "capital_authorized": False,
            "execution_authorized": False,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
