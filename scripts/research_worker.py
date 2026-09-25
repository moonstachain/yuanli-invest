#!/usr/bin/env python3
"""Capture exact daily Gold evidence and settle due claims through the machine Edge.

The source configuration must be reviewed, including its IANA timezone. This
command never discovers or falls back to a database/service-role credential.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from zoneinfo import ZoneInfo

from yuanli_invest.first_capture import SOURCE_FIELDS, decimal_value, settle_daily_first_capture, trade_day, validate_claim
from yuanli_invest.receipts import canonical_bytes, read_envelope, receipt_envelope
from yuanli_invest.time import instant


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_source(path: Path) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or any(not isinstance(source.get(field), str) or not source[field].strip() for field in SOURCE_FIELDS):
        raise ValueError("reviewed source identity, unit, currency and timezone are required")
    if source["target"] != "GOLD":
        raise ValueError("daily capture supports GOLD only")
    ZoneInfo(source["source_timezone"])
    return source


class MachineGateway:
    def __init__(self, endpoint: str, client_id: str, token: str, workspace_id: str):
        url = urlsplit(endpoint)
        if not (url.scheme == "https" or url.scheme == "http" and url.hostname in {"127.0.0.1", "localhost", "::1"}):
            raise ValueError("machine Edge requires HTTPS (HTTP is allowed only on loopback)")
        if url.username or url.password or url.query or url.fragment or not url.path.endswith("/research-machine"):
            raise ValueError("configure the research-machine Edge endpoint explicitly")
        if not all(isinstance(value, str) and value.strip() for value in (client_id, token, workspace_id)):
            raise ValueError("machine client ID, scoped token and workspace ID are required")
        self.endpoint, self.client_id, self.token, self.workspace_id = endpoint, client_id, token, workspace_id
        self._opener = build_opener(_NoRedirect())

    @classmethod
    def from_environment(cls):
        return cls(
            os.environ.get("YUANLI_RESEARCH_MACHINE_URL", os.environ.get("YIOS_TG1_INGEST_ENDPOINT", "")),
            os.environ.get("YIOS_TG1_MACHINE_CLIENT_ID", ""),
            os.environ.get("YIOS_TG1_MACHINE_INGEST_TOKEN", ""),
            os.environ.get("YUANLI_WORKSPACE_ID", ""),
        )

    def __call__(self, operation: str, payload: dict):
        request = Request(
            self.endpoint,
            data=canonical_bytes({"operation": operation, "workspace_id": self.workspace_id, "payload": payload}),
            headers={"Content-Type": "application/json", "x-yuanli-client-id": self.client_id, "x-yuanli-ingest-token": self.token},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=60) as response:
                result = json.load(response)
        except HTTPError as exc:
            # Do not log credential-bearing requests or arbitrary response bodies.
            raise RuntimeError(f"machine Edge HTTP {exc.code}") from exc
        if not isinstance(result, dict) or result.get("ok") is not True or "data" not in result:
            raise RuntimeError("machine Edge did not acknowledge the operation")
        return result["data"]


def wind_payload(cli_path: Path, series_id: str) -> bytes:
    request = {"question": f"提取指标代码 {series_id} 最近5期数据，仅返回该指标", "observation": "5"}
    process = subprocess.run(
        ["node", str(cli_path), "call", "economic_data", "query_economic_indicator_data", json.dumps(request, ensure_ascii=False)],
        capture_output=True, check=True, timeout=90,
    )
    return process.stdout


def capture_payloads(raw: bytes, source: dict, captured_at: str, day: str | None = None) -> list[dict]:
    """Bind exact dates to raw bytes; daily runs retain every completed source day."""
    captured = instant(captured_at)
    zone = ZoneInfo(source["source_timezone"])
    source_today = captured.astimezone(zone).date()
    requested = trade_day(day) if day is not None else None
    if requested is not None and source_today < requested:
        raise ValueError("cannot capture a future trade date")
    outer = json.loads(raw, parse_float=Decimal)
    if not isinstance(outer, dict) or outer.get("isError") is True or outer.get("ok") is False:
        raise ValueError("Wind returned an error")
    content = outer.get("content")
    if not isinstance(content, list):
        raise ValueError("Wind content is missing")
    bodies = [json.loads(item["text"], parse_float=Decimal) for item in content if isinstance(item, dict) and item.get("type") == "text" and item.get("text")]
    metrics = [metric for body in bodies if isinstance(body, dict) for metric in body.get("metrics", []) if isinstance(metric, dict) and isinstance(metric.get("meta"), dict) and metric["meta"].get("code") == source["series_id"]]
    if len(metrics) != 1:
        raise ValueError("Wind must return one exact registered series")
    dates, values = metrics[0].get("date"), metrics[0].get("value")
    if not isinstance(dates, list) or not isinstance(values, list) or len(dates) != len(values):
        raise ValueError("Wind observations are not aligned")
    selected = {}
    for stamp, value in zip(dates, values):
        if requested is not None and stamp != requested.strftime("%Y%m%d"):
            continue
        if not isinstance(stamp, str) or len(stamp) != 8 or not stamp.isascii() or not stamp.isdigit():
            raise ValueError("Wind observation date must be YYYYMMDD")
        observed = trade_day(f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}")
        if requested is None and observed >= source_today:
            continue
        if observed in selected:
            raise ValueError("duplicate exact-date Wind observations")
        if type(value) not in {int, Decimal}:
            raise ValueError("Wind price must be a JSON number")
        value = Decimal(value)
        if not value.is_finite() or abs(value.adjusted()) > 90:
            raise ValueError("Wind price is not a finite supported decimal")
        value_string = format(value, "f")
        decimal_value(value_string, "Wind price", positive=True)
        selected[observed] = value_string
    common = {
        "source_id": source["source_id"], "source_timezone": source["source_timezone"],
        "payload_base64": base64.b64encode(raw).decode("ascii"),
        "payload_sha256": hashlib.sha256(raw).hexdigest(), "captured_at": captured.isoformat(),
    }
    return [{**common, "trade_date": observed.isoformat(), "value_decimal": selected[observed]} for observed in sorted(selected)]


def capture_payload(raw: bytes, source: dict, day: str, captured_at: str) -> dict | None:
    """Compatibility adapter for one explicitly requested exact day."""
    captures = capture_payloads(raw, source, captured_at, day)
    return captures[0] if captures else None


def due_claims(gateway):
    cursor, seen = None, set()
    while True:
        response = gateway("list_due_claims", {"limit": 100, **({"cursor": cursor} if cursor is not None else {})})
        if not isinstance(response, dict) or not isinstance(response.get("items"), list):
            raise ValueError("due claims response must contain an items array")
        yield from response["items"]
        cursor = response.get("next_cursor")
        if cursor is None:
            return
        if not isinstance(cursor, str) or not cursor:
            raise ValueError("due claims cursor must be a nonempty string")
        if cursor in seen:
            raise ValueError("due claims cursor did not advance")
        seen.add(cursor)


def run_once(*, fetch, gateway, source: dict, clock, day: str | None = None) -> dict:
    result = {"status": "COMPLETE", "capture": {}, "settlements": [], "errors": []}
    try:
        raw = fetch()
        captures = capture_payloads(raw, source, instant(clock()).isoformat(), day)
        if not captures:
            result["capture"] = {"status": "INDETERMINATE_EVIDENCE", "reason": "MISSING_EXACT_TRADE_DATE" if day is not None else "NO_COMPLETED_TRADE_DATE"}
        else:
            records = []
            for capture in captures:
                try:
                    records.append(gateway("capture_first_price", capture))
                except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
                    result["errors"].append({"operation": "capture_first_price", "trade_date": capture["trade_date"], "error_type": type(exc).__name__})
            result["capture"] = {"status": "SYSTEM_ERROR" if result["errors"] else "CAPTURED", "records": records}
            if day is not None and records:
                result["capture"]["record"] = records[0]
    except (ValueError, TypeError, KeyError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        result["capture"] = {"status": "SYSTEM_ERROR", "error_type": type(exc).__name__}
        result["errors"].append({"operation": "capture_first_price", "error_type": type(exc).__name__})
    # Existing endpoint evidence can still settle other claims after a failed
    # capture. Transport failures never become scientific evidence insufficiency.
    try:
        as_of = instant(clock()).isoformat()
        for item in due_claims(gateway):
            claim_id = item.get("claim", {}).get("claim_id") if isinstance(item, dict) else None
            operation = "settle"
            try:
                if not isinstance(item, dict):
                    raise ValueError("due claim must be an object")
                stored = item.get("settlement")
                if stored is not None:
                    # Recover an interrupted learning write from the exact
                    # committed settlement; never recalculate it with a new clock.
                    validate_claim(item["claim"], item["registration"], item["trusted_source"])
                    receipt = read_envelope(stored)
                else:
                    receipt = settle_daily_first_capture({**item, "as_of": as_of})
                    if receipt["status"] != "SETTLED_RESEARCH":
                        operation = "record_claim_attempt"
                        attempt = {"claim_id": claim_id, "status": receipt["status"], "message": "Exact endpoint evidence is not ready", **receipt_envelope(receipt)}
                        if result["capture"].get("status") == "SYSTEM_ERROR" and item["claim"]["source_id"] == source["source_id"]:
                            attempt = {"claim_id": claim_id, "status": "SYSTEM_ERROR", "message": "Source capture failed; settlement evidence could not be completed"}
                        gateway(operation, attempt)
                        result["settlements"].append({"claim_id": claim_id, "status": attempt["status"]})
                        continue
                    operation = "record_settlement"
                    acknowledged = gateway(operation, {
                        "claim_id": receipt["claim_id"], "claim_sha256": receipt["claim_sha256"],
                        **receipt_envelope(receipt),
                    })
                    if receipt["status"] == "SETTLED_RESEARCH":
                        stored = acknowledged["settlement"]
                if stored is not None:
                    committed = read_envelope(stored)
                    if committed["claim_id"] != claim_id or committed["claim_sha256"] != item["registration"]["claim_sha256"] or committed["status"] != "SETTLED_RESEARCH":
                        raise ValueError("runtime acknowledged a different settlement")
                    learning = {
                        "schema_version": "gold-research-learning.v1", "claim_id": receipt["claim_id"],
                        "settlement_receipt_sha256": stored["receipt_sha256"], "accepted_learning": False,
                        "text": (
                            f"Observed direction: {committed['realized_direction']}; "
                            f"preregistered model correct: {committed['model_score']['correct']}; "
                            f"frozen no-change baseline correct: {committed['baseline_score']['correct']}. "
                            "Pending review; this result does not prove investment effectiveness."
                        ),
                    }
                    operation = "record_learning"
                    gateway(operation, {"claim_id": receipt["claim_id"], **receipt_envelope(learning)})
                result["settlements"].append({"claim_id": receipt["claim_id"], "status": receipt["status"]})
            except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
                result["errors"].append({"operation": operation, "claim_id": claim_id, "error_type": type(exc).__name__})
                if claim_id:
                    try:
                        gateway("record_claim_attempt", {"claim_id": claim_id, "status": "SYSTEM_ERROR", "message": f"{operation}: {type(exc).__name__}"})
                    except (ValueError, TypeError, KeyError, OSError, RuntimeError):
                        result["errors"].append({"operation": "record_claim_attempt", "claim_id": claim_id, "error_type": "PERSISTENCE_FAILED"})
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        result["errors"].append({"operation": "list_due_claims", "error_type": type(exc).__name__})
    if result["errors"]:
        result["status"] = "SYSTEM_ERROR"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Reviewed source identity and timezone JSON")
    parser.add_argument("--wind-cli", type=Path, required=True)
    parser.add_argument("--trade-date", help="Exact date; defaults to the previous day in the reviewed source timezone")
    args = parser.parse_args()
    try:
        source = load_source(args.source)
        now = lambda: datetime.now(timezone.utc)
        day = args.trade_date or (now().astimezone(ZoneInfo(source["source_timezone"])).date() - timedelta(days=1)).isoformat()
        gateway = MachineGateway.from_environment()
        result = run_once(fetch=lambda: wind_payload(args.wind_cli, source["series_id"]), gateway=gateway, source=source, day=day, clock=now)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        result = {"status": "SYSTEM_ERROR", "error_type": type(exc).__name__}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 2 if result["status"] == "SYSTEM_ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
