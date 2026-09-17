#!/usr/bin/env python3
"""Archive Eaton first-party Electrical Americas order-growth releases to private S3.

This proof has zero promotion/research/capital/execution authority. It validates only
source identity, exact same-regime disclosure markers, raw-byte hashing, private archive,
and SHA readback.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT_REF = "tbmoimbdhsrltvospwpu"
REGION = "us-east-2"
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")

SOURCES = [
    {
        "quarter": "2025Q3",
        "url": "https://www.eaton.com/us/en-us/company/news-insights/news-releases/2025/eaton-reports-record-third-quarter-2025-results-with-accelerating-orders.html",
        "value_pct": 7.0,
        "quarter_end": "2025-09-30",
        "released_at": "2025-11-04",
    },
    {
        "quarter": "2025Q4",
        "url": "https://www.eaton.com/my/en-us/company/news-insights/news-releases/2026/eaton-reports-record-fourth-quarter-2025-results.html",
        "value_pct": 16.0,
        "quarter_end": "2025-12-31",
        "released_at": "2026-02-03",
    },
    {
        "quarter": "2026Q1",
        "url": "https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-reports-record-first-quarter-2026-results.html",
        "value_pct": 42.0,
        "quarter_end": "2026-03-31",
        "released_at": "2026-05-05",
    },
    {
        "quarter": "2026Q2",
        "url": "https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-reports-record-second-quarter-2026-results.html",
        "value_pct": 41.0,
        "quarter_end": "2026-06-30",
        "released_at": "2026-07-31",
    },
]


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required secret binding: {name}")
    return value


def http_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, connect=5, read=5, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=frozenset(["GET"]))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "Mozilla/5.0 YuanliEvidenceBot/1.0", "Accept-Language": "en-US,en;q=0.9"})
    return session


def validate(raw: bytes, value_pct: float, quarter: str) -> dict:
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw.decode("utf-8", errors="ignore"))).lower()
    if "electrical americas" not in visible:
        raise RuntimeError(f"Electrical Americas marker missing for {quarter}")
    if "twelve-month rolling average" not in visible:
        raise RuntimeError(f"rolling-average marker missing for {quarter}")
    value = str(int(value_pct))
    if f"up {value}%" not in visible:
        raise RuntimeError(f"expected {value}% order-growth marker missing for {quarter}")
    sha = hashlib.sha256(raw).hexdigest()
    return {"sha256": sha, "bytes": len(raw)}


def s3_client(access_key: str, secret_key: str):
    import boto3
    from botocore.config import Config
    endpoint = f"https://{PROJECT_REF}.storage.supabase.co/storage/v1/s3"
    return boto3.client(
        "s3", region_name=REGION, endpoint_url=endpoint,
        aws_access_key_id=access_key, aws_secret_access_key=secret_key,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def main() -> int:
    access_key = require_env("YMQ4_SUPABASE_S3_ACCESS_KEY_ID")
    secret_key = require_env("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")
    s3 = s3_client(access_key, secret_key)
    s3.head_bucket(Bucket=BUCKET)
    session = http_session()
    archived = []
    for spec in SOURCES:
        response = session.get(spec["url"], timeout=(20, 60))
        response.raise_for_status()
        raw = response.content
        checked = validate(raw, spec["value_pct"], spec["quarter"])
        sha = checked["sha256"]
        key = f"yci0-rp1/eaton/power-grid/{spec['quarter'].lower()}/{sha}.html"
        s3.put_object(Bucket=BUCKET, Key=key, Body=raw, ContentType=response.headers.get("Content-Type", "text/html"), Metadata={"sha256": sha, "proof-contract": "YCI0-RP1-G3-EATON-POWER"})
        reread = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        reread_sha = hashlib.sha256(reread).hexdigest()
        if reread_sha != sha:
            raise RuntimeError(f"S3 SHA mismatch for {spec['quarter']}: {reread_sha} != {sha}")
        archived.append({
            "quarter": spec["quarter"], "quarter_end": spec["quarter_end"],
            "released_at": spec["released_at"], "value_pct": spec["value_pct"],
            "metric": "Electrical Americas rolling-12-month organic order growth",
            "source_url": spec["url"], "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type", "text/html"),
            "bytes": len(raw), "sha256": sha, "storage_bucket": BUCKET,
            "storage_path": key, "storage_readback_sha256": reread_sha,
        })
    receipt = {
        "program": "YCI0-RP1", "gate": "G3_POWER_GRID_RAW_EVIDENCE", "status": "PASS",
        "provider": "Eaton", "source_role": "FIRST_PARTY_COMPANY_DISCLOSURE",
        "series_id": "ETN_ELECTRICAL_AMERICAS_R12M_ORDER_ORGANIC_GROWTH_PCT",
        "measurement_regime": "EATON_ELECTRICAL_AMERICAS_R12M_ORGANIC_ORDER_GROWTH",
        "proxy_boundary": "Electrical infrastructure demand proxy; not AI-only or data-center-only orders",
        "archived": archived,
        "authority": {"evidence_promotion_authorized": False, "research_authorized": False, "capital_authorized": False, "execution_authorized": False},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
