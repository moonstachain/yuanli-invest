#!/usr/bin/env python3
"""YCI0-RP1 raw Microsoft first-party evidence archive proof.

Downloads the FY26 Q1-Q4 official Microsoft Investor Relations pages, validates
the exact PP&E cash-flow rows, writes raw bytes into the existing private
Supabase S3 evidence bucket, and reads every object back by SHA-256.

This runner does NOT promote Evidence Authority or create Research/Capital/
Execution authority. It emits a non-secret receipt for a later admission gate.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any

PROJECT_REF = "tbmoimbdhsrltvospwpu"
REGION = "us-east-2"
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")

SOURCES = {
    "FY26Q1": {
        "url": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q1/cash-flows",
        "value_millions_usd": 19394,
        "require_xbrl": True,
    },
    "FY26Q2": {
        "url": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q2/cash-flows",
        "value_millions_usd": 29876,
        "require_xbrl": True,
    },
    "FY26Q3": {
        "url": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q3/cash-flows",
        "value_millions_usd": 30876,
        "require_xbrl": True,
    },
    "FY26Q4": {
        "url": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast",
        "value_millions_usd": 35802,
        "require_xbrl": False,
    },
}


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required secret binding: {name}")
    return value


def fetch(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/152 Safari/537.36 YuanliEvidenceBot/1.0",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return (
            int(response.status),
            response.headers.get("Content-Type", "application/octet-stream"),
            response.read(),
        )


def _visible_text(text: str) -> str:
    unescaped = html.unescape(text)
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    return re.sub(r"\s+", " ", without_tags).strip()


def validation_facts(raw: bytes, *, value_millions_usd: int) -> dict[str, Any]:
    text = raw.decode("utf-8", "ignore")
    visible = _visible_text(text)
    formatted = f"{value_millions_usd:,}"
    return {
        "has_row_label": "Additions to property and equipment" in visible,
        "has_xbrl_tag": "PaymentsToAcquirePropertyPlantAndEquipment" in text,
        "has_expected_value": formatted in visible or formatted in text,
        "expected_value": formatted,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def validate_raw(
    raw: bytes,
    *,
    quarter: str,
    value_millions_usd: int,
    require_xbrl: bool,
) -> dict[str, Any]:
    facts = validation_facts(raw, value_millions_usd=value_millions_usd)
    print(json.dumps({"quarter": quarter, "validation": facts}, sort_keys=True), file=sys.stderr)
    if not facts["has_expected_value"]:
        raise RuntimeError(f"{quarter} official page missing expected PP&E value {facts['expected_value']}")
    if require_xbrl:
        if not facts["has_xbrl_tag"]:
            raise RuntimeError(f"{quarter} official page missing expected PP&E XBRL tag")
    elif not facts["has_row_label"]:
        raise RuntimeError(f"{quarter} official page missing normalized PP&E row label")
    return facts


def s3_client(access_key_id: str, secret_access_key: str):
    import boto3
    from botocore.config import Config

    endpoint = f"https://{PROJECT_REF}.storage.supabase.co/storage/v1/s3"
    return boto3.client(
        "s3",
        region_name=REGION,
        endpoint_url=endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def archive_one(client, quarter: str, spec: dict[str, Any]) -> dict[str, Any]:
    status, content_type, raw = fetch(spec["url"])
    if status != 200:
        raise RuntimeError(f"{quarter} source HTTP status {status}")
    facts = validate_raw(
        raw,
        quarter=quarter,
        value_millions_usd=int(spec["value_millions_usd"]),
        require_xbrl=bool(spec["require_xbrl"]),
    )
    sha = facts["sha256"]
    path = f"yci0-rp1/msft/fy26/{quarter.lower()}/{sha}.html"
    client.put_object(
        Bucket=BUCKET,
        Key=path,
        Body=raw,
        ContentType=content_type,
        Metadata={"sha256": sha, "proof-contract": "YCI0-RP1-G0.5"},
    )
    obj = client.get_object(Bucket=BUCKET, Key=path)
    reread = obj["Body"].read()
    reread_sha = hashlib.sha256(reread).hexdigest()
    metadata_sha = (obj.get("Metadata") or {}).get("sha256")
    if reread_sha != sha or metadata_sha != sha:
        raise RuntimeError(f"{quarter} raw storage SHA readback mismatch")
    return {
        "quarter": quarter,
        "source_url": spec["url"],
        "metric_label": "Additions to property and equipment",
        "xbrl_tag": "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment" if spec["require_xbrl"] else None,
        "value_millions_usd": spec["value_millions_usd"],
        "http_status": status,
        "content_type": content_type,
        "bytes": len(raw),
        "sha256": sha,
        "storage_bucket": BUCKET,
        "storage_path": path,
        "storage_readback_sha256": reread_sha,
    }


def main() -> int:
    access = require_env("YMQ4_SUPABASE_S3_ACCESS_KEY_ID")
    secret = require_env("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")
    client = s3_client(access, secret)
    client.head_bucket(Bucket=BUCKET)

    archived = [archive_one(client, q, spec) for q, spec in SOURCES.items()]
    receipt = {
        "program": "YCI0-RP1",
        "gate": "G0.5_RAW_EVIDENCE_HARDENING",
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": "Microsoft Investor Relations",
        "source_role": "FIRST_PARTY_COMPANY_DISCLOSURE",
        "measurement_regime": "CASH_PAID_PP&E_TOTAL_COMPANY",
        "archived": archived,
        "authority": {
            "evidence_promotion_authorized": False,
            "research_authorized": False,
            "capital_authorized": False,
            "execution_authorized": False,
        },
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
