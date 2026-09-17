#!/usr/bin/env python3
"""Archive NVIDIA first-party Data Center revenue pages to private Supabase S3.

This proof has zero evidence-promotion, research, capital, or execution authority.
It only proves source reachability, expected disclosure text, raw-byte hashing, private
archive persistence, and SHA readback.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import urllib.request
from datetime import datetime, timezone

PROJECT_REF = "tbmoimbdhsrltvospwpu"
REGION = "us-east-2"
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")

SOURCES = [
    {
        "quarter": "FY26Q3",
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2026",
        "value": "51.2",
        "value_usd_bn": 51.2,
        "quarter_end": "2025-10-26",
        "released_at": "2025-11-19",
    },
    {
        "quarter": "FY26Q4",
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026",
        "value": "62.3",
        "value_usd_bn": 62.3,
        "quarter_end": "2026-01-25",
        "released_at": "2026-02-25",
    },
    {
        "quarter": "FY27Q1",
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2027",
        "value": "75.2",
        "value_usd_bn": 75.2,
        "quarter_end": "2026-04-26",
        "released_at": "2026-05-20",
    },
    {
        "quarter": "FY27Q2",
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027",
        "value": "89.0",
        "value_usd_bn": 89.0,
        "quarter_end": "2026-07-26",
        "released_at": "2026-08-26",
    },
]


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required secret binding: {name}")
    return value


def download(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 YuanliEvidenceBot/1.0", "Accept-Language": "en-US,en;q=0.9"},
    )
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=45) as resp:
        return resp.status, resp.headers.get("Content-Type", "text/html"), resp.read()


def validate(raw: bytes, spec: dict) -> dict:
    text = raw.decode("utf-8", errors="ignore")
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
    expected = f"Data Center revenue of ${spec['value']} billion"
    if expected not in visible:
        raise RuntimeError(f"expected NVIDIA disclosure not found for {spec['quarter']}: {expected}")
    sha = hashlib.sha256(raw).hexdigest()
    return {"sha256": sha, "bytes": len(raw), "expected_phrase": expected}


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
    client = s3_client(access_key, secret_key)
    client.head_bucket(Bucket=BUCKET)
    archived = []
    for spec in SOURCES:
        status, content_type, raw = download(spec["url"])
        if status != 200:
            raise RuntimeError(f"source HTTP status != 200 for {spec['quarter']}: {status}")
        checked = validate(raw, spec)
        sha = checked["sha256"]
        key = f"yci0-rp1/nvda/compute/{spec['quarter'].lower()}/{sha}.html"
        client.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=raw,
            ContentType=content_type,
            Metadata={"sha256": sha, "proof-contract": "YCI0-RP1-G2-NVDA-COMPUTE"},
        )
        reread = client.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        reread_sha = hashlib.sha256(reread).hexdigest()
        if reread_sha != sha:
            raise RuntimeError(f"S3 SHA mismatch for {spec['quarter']}: {reread_sha} != {sha}")
        archived.append({
            "quarter": spec["quarter"],
            "quarter_end": spec["quarter_end"],
            "released_at": spec["released_at"],
            "value_usd_bn": spec["value_usd_bn"],
            "metric": "Data Center revenue",
            "source_url": spec["url"],
            "http_status": status,
            "content_type": content_type,
            "bytes": len(raw),
            "sha256": sha,
            "storage_bucket": BUCKET,
            "storage_path": key,
            "storage_readback_sha256": reread_sha,
        })
    receipt = {
        "program": "YCI0-RP1",
        "gate": "G2_COMPUTE_RAW_EVIDENCE",
        "status": "PASS",
        "provider": "NVIDIA Newsroom",
        "source_role": "FIRST_PARTY_COMPANY_DISCLOSURE",
        "series_id": "NVDA_DATA_CENTER_REVENUE_QUARTERLY_USD_BN",
        "measurement_regime": "NVIDIA_QUARTERLY_DATA_CENTER_REVENUE",
        "archived": archived,
        "authority": {
            "evidence_promotion_authorized": False,
            "research_authorized": False,
            "capital_authorized": False,
            "execution_authorized": False,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
