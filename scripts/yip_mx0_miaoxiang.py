#!/usr/bin/env python3
"""YIP-MX0 Miaoxiang evidence-only adapter primitives."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "yip_mx0" / "miaoxiang_gold_golden_query.v0.1.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or CONFIG_PATH).read_text(encoding="utf-8"))


def load_api_key() -> str:
    key = os.getenv("EM_API_KEY", "").strip()
    if key:
        return key
    proc = subprocess.run(
        ["security", "find-generic-password", "-a", os.getenv("USER", "liming"), "-s", "yuanli.miaoxiang.api", "-w"],
        check=False, capture_output=True, text=True, timeout=10,
    )
    key = proc.stdout.strip() if proc.returncode == 0 else ""
    if not key:
        raise RuntimeError("Miaoxiang credential is not configured in EM_API_KEY or macOS Keychain")
    return key


def default_runtime_dir() -> Path:
    env = os.getenv("YIP_MX0_RUNTIME_DIR", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".yuanli" / "runtime" / "yip_mx0"


def extract_tool_text(payload: Mapping[str, Any]) -> str:
    if payload.get("isError") is True:
        raise ValueError("Miaoxiang tool returned an error")
    texts = [
        str(item.get("text"))
        for item in payload.get("content", [])
        if isinstance(item, Mapping) and item.get("type") == "text" and item.get("text") is not None
    ]
    if len(texts) != 1:
        raise ValueError("expected exactly one text payload")
    return texts[0]


def _unit_from_label(label: str) -> str | None:
    match = re.search(r"\(([^()]*(?:美元|人民币)[^()]*)\)$", label)
    return match.group(1) if match else None


def extract_series_candidates(text: str, *, series_contains: str) -> list[dict[str, Any]]:
    payload = json.loads(text)
    matches: list[dict[str, Any]] = []
    raw_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    for sheet in payload.get("data", []):
        columns = sheet.get("columns") or []
        if len(columns) < 3:
            continue
        frequency = "daily" if "日" in str(columns[0]) else "weekly" if "周" in str(columns[0]) else "unknown"
        dates = [str(v) for v in columns[2:]]
        for row in sheet.get("items") or []:
            if len(row) < 3 or series_contains not in str(row[0]):
                continue
            observations = [(d, v) for d, v in zip(dates, row[2:]) if v not in (None, "", "--")]
            if not observations:
                continue
            latest_date, latest_raw = observations[0]
            matches.append({
                "series_label": str(row[0]),
                "source": str(row[1]),
                "latest_date": latest_date,
                "latest_value": float(latest_raw),
                "frequency": frequency,
                "unit": _unit_from_label(str(row[0])),
                "raw_sha256": raw_sha,
            })
    return matches


def parse_macro_text(text: str, *, series_contains: str) -> dict[str, Any]:
    matches = extract_series_candidates(text, series_contains=series_contains)
    if not matches:
        raise ValueError(f"series not found: {series_contains}")
    if len(matches) != 1:
        raise ValueError(f"ambiguous series match: {series_contains}")
    return matches[0]


def build_receipt(metric: Mapping[str, Any], *, as_of: date) -> dict[str, Any]:
    known = str(metric["latest_date"])
    if known > as_of.isoformat():
        raise ValueError("future-dated provider evidence")
    return {
        "program": "YIP-MX0",
        "status": "REALITY_PROOF_RECEIPT",
        "as_of": as_of.isoformat(),
        "known_as_of": known,
        "provider": "EASTMONEY_MIAOXIANG",
        "authority": "EVIDENCE_ONLY",
        "capital_authorized": False,
        "execution_authorized": False,
        "canon_promotion_authorized": False,
        "metric": dict(metric),
    }


def compare_gold_sources(
    mx_metric: Mapping[str, Any], wind_metric: Mapping[str, Any], *, gap_threshold_pct: float = 0.5
) -> dict[str, Any]:
    mx_value = float(mx_metric["latest_value"])
    wind_value = float(wind_metric["latest_value"])
    gap_pct = (mx_value / wind_value - 1.0) * 100.0
    same_day = str(mx_metric["latest_date"]) == str(wind_metric["latest_date"])
    status = "ALIGNED_WITHIN_THRESHOLD"
    if not same_day or abs(gap_pct) > gap_threshold_pct:
        status = "REQUIRES_SEMANTIC_RECONCILIATION"
    return {
        "status": status,
        "same_observation_date": same_day,
        "gap_pct": gap_pct,
        "provider_failure_inferred": False,
        "miaoxiang": dict(mx_metric),
        "wind": dict(wind_metric),
    }


def build_triangle_receipt(text: str, *, as_of: date) -> dict[str, Any]:
    gold = parse_macro_text(text, series_contains="伦敦金现")
    usd = parse_macro_text(text, series_contains="美元指数")
    real_rates = extract_series_candidates(text, series_contains="国债实际收益率")
    known_dates = [gold["latest_date"], usd["latest_date"]] + [r["latest_date"] for r in real_rates]
    if any(str(d) > as_of.isoformat() for d in known_dates):
        raise ValueError("future-dated provider evidence")
    exact_wind_equivalent = [r for r in real_rates if "长期国债平均实际收益率" in r["series_label"] and "大于10年" in r["series_label"]]
    return {
        "program": "YIP-MX0",
        "battle": "MIAOXIANG_API_REALITY_PROOF_X_GOLD_GOLDEN_QUERY",
        "status": "REALITY_PROOF_RECEIPT",
        "as_of": as_of.isoformat(),
        "known_as_of": max(known_dates),
        "provider": "EASTMONEY_MIAOXIANG",
        "authority": "EVIDENCE_ONLY",
        "capital_authorized": False,
        "sizing_authorized": False,
        "execution_authorized": False,
        "canon_promotion_authorized": False,
        "metrics": {"gold_price": gold, "usd": usd},
        "real_rate_candidates": real_rates,
        "real_rate_semantic_state": "EXACT_WIND_GT10Y_AVG_EQUIVALENT" if exact_wind_equivalent else "NO_EXACT_WIND_GT10Y_AVG_EQUIVALENT",
        "unknowns": [] if exact_wind_equivalent else ["wind_gt10y_average_real_yield_exact_equivalent"],
    }


def write_private_artifacts(raw_record: Mapping[str, Any], receipt: Mapping[str, Any], runtime_dir: Path) -> dict[str, Any]:
    day = str(receipt.get("as_of") or date.today().isoformat())
    daily = runtime_dir / day
    daily.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    raw_text = json.dumps(dict(raw_record), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    raw_path = daily / f"miaoxiang-gold-triangle-{stamp}.raw.json"
    receipt_path = daily / f"miaoxiang-gold-triangle-{stamp}.receipt.json"
    raw_path.write_text(raw_text, encoding="utf-8")
    receipt_path.write_text(json.dumps(dict(receipt), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"raw": raw_path, "receipt": receipt_path, "sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest()}


async def query_mcp_tool(
    *, endpoint: str, api_key: str, tool: str, query: str,
    transport_factory=None, session_factory=None,
) -> dict[str, Any]:
    if transport_factory is None or session_factory is None:
        from mcp.client.streamable_http import streamablehttp_client
        from mcp import ClientSession
        transport_factory = transport_factory or streamablehttp_client
        session_factory = session_factory or ClientSession
    async with transport_factory(
        endpoint,
        headers={"em_api_key": api_key},
        timeout=45,
        sse_read_timeout=120,
    ) as (read, write, _get_session_id):
        async with session_factory(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, {"query": query})
            if hasattr(result, "model_dump"):
                return result.model_dump(mode="json")
            if isinstance(result, Mapping):
                return dict(result)
            raise TypeError("unsupported MCP tool result type")


def run_live_once(*, as_of: date | None = None) -> dict[str, Any]:
    import asyncio

    cfg = load_config()
    key = load_api_key()
    payload = asyncio.run(query_mcp_tool(
        endpoint=cfg["provider"]["endpoint"],
        api_key=key,
        tool=cfg["golden_query"]["tool"],
        query=cfg["golden_query"]["query"],
    ))
    text = extract_tool_text(payload)
    today = as_of or date.today()
    receipt = build_triangle_receipt(text, as_of=today)
    receipt["provider_contract"] = {
        "endpoint": cfg["provider"]["endpoint"],
        "tool": cfg["golden_query"]["tool"],
        "raw_body_git_persistence": cfg["provider"]["raw_body_git_persistence"],
    }
    raw_record = {
        "program": cfg["program"],
        "provider": cfg["provider"]["name"],
        "tool": cfg["golden_query"]["tool"],
        "query": cfg["golden_query"]["query"],
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "response": payload,
    }
    paths = write_private_artifacts(raw_record, receipt, default_runtime_dir())
    return {
        "status": receipt["status"],
        "as_of": receipt["as_of"],
        "known_as_of": receipt["known_as_of"],
        "provider": receipt["provider"],
        "gold_price": receipt["metrics"]["gold_price"],
        "usd": receipt["metrics"]["usd"],
        "real_rate_candidates": receipt["real_rate_candidates"],
        "real_rate_semantic_state": receipt["real_rate_semantic_state"],
        "raw_path": str(paths["raw"]),
        "receipt_path": str(paths["receipt"]),
        "raw_sha256": paths["sha256"],
        "authority": receipt["authority"],
    }


def main() -> int:
    try:
        print(json.dumps(run_live_once(), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({
            "program": "YIP-MX0",
            "status": "PROVIDER_FAIL_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
            "authority": "EVIDENCE_ONLY",
        }, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
