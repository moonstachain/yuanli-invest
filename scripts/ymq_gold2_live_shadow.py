#!/usr/bin/env python3
"""YMQ-GOLD2 30-day read-only Gold Live Shadow.

Wind is an evidence provider only. This runner may schedule research receipts but
may never create capital, sizing, execution, broker, VeighNa or Canon authority.
Raw provider bodies are hashed in memory and are not persisted to Git.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ACTIVATION_PATH = ROOT / "config" / "ymq_gold2" / "gold2_live_shadow.activation.v0.1.json"
ACTION_DENY_FIELDS = (
    "capital_authorized",
    "sizing_authorized",
    "execution_authorized",
    "broker_action",
    "veighna_authorized",
    "canon_promotion_authorized",
)


def load_activation(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or ACTIVATION_PATH).read_text(encoding="utf-8"))


def validate_activation(cfg: Mapping[str, Any]) -> None:
    if cfg.get("status") != "HUMAN_AUTHORIZED_ACTIVE_SHADOW_ONLY":
        raise ValueError("live shadow is not Human-authorized")
    start = date.fromisoformat(str(cfg["start_date"]))
    end = date.fromisoformat(str(cfg["end_date_exclusive"]))
    if (end - start).days != int(cfg.get("pilot_days", -1)):
        raise ValueError("pilot window does not match pilot_days")
    authority = cfg.get("authority", {})
    if authority.get("research_authorized") is not True:
        raise ValueError("research authority must be explicit")
    if authority.get("live_scheduler_authorized") is not True:
        raise ValueError("scheduler authority not granted")
    for field in ACTION_DENY_FIELDS:
        if authority.get(field) is not False:
            raise ValueError(f"forbidden authority enabled: {field}")
    provider = cfg.get("provider", {})
    if provider.get("authority") != "EVIDENCE_ONLY":
        raise ValueError("provider authority must remain EVIDENCE_ONLY")
    if provider.get("raw_body_git_persistence") is not False:
        raise ValueError("raw provider body persistence must stay disabled")


def pilot_state(day: date, cfg: Mapping[str, Any]) -> str:
    start = date.fromisoformat(str(cfg["start_date"]))
    end = date.fromisoformat(str(cfg["end_date_exclusive"]))
    if day < start:
        return "NOT_STARTED"
    if day >= end:
        return "EXPIRED"
    return "ACTIVE"


def _inner_payload(stdout: str) -> dict[str, Any]:
    outer = json.loads(stdout)
    if outer.get("ok") is False or outer.get("isError") is True:
        raise ValueError(f"Wind provider error: {outer.get('code') or outer.get('message') or 'unknown'}")
    content = outer.get("content")
    if not isinstance(content, list):
        raise ValueError("Wind response missing content")
    for item in content:
        if isinstance(item, Mapping) and item.get("type") == "text" and item.get("text"):
            payload = json.loads(str(item["text"]))
            if isinstance(payload, dict):
                return payload
    raise ValueError("Wind response missing JSON text payload")


def parse_wind_cli_response(stdout: str, *, expected_code: str) -> dict[str, Any]:
    payload = _inner_payload(stdout)
    metrics = payload.get("metrics")
    if not isinstance(metrics, list):
        raise ValueError("Wind response missing metrics")
    matches = [m for m in metrics if isinstance(m, Mapping) and m.get("meta", {}).get("code") == expected_code]
    if len(matches) != 1:
        raise ValueError(f"Wind metric identity mismatch for {expected_code}")
    metric = dict(matches[0])
    dates = metric.get("date") or []
    values = metric.get("value") or []
    if not dates or len(dates) != len(values):
        raise ValueError(f"Wind metric {expected_code} has no aligned observations")
    metric["latest_date"] = str(dates[-1])
    metric["latest_value"] = values[-1]
    metric["raw_sha256"] = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    return metric


def query_wind_metric(cli_path: Path, code: str, *, observation: str = "5") -> dict[str, Any]:
    request = {
        "question": f"提取指标代码 {code} 最近{observation}期数据，仅返回该指标",
        "observation": str(observation),
    }
    proc = subprocess.run(
        [
            "node",
            str(cli_path),
            "call",
            "economic_data",
            "query_economic_indicator_data",
            json.dumps(request, ensure_ascii=False),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Wind CLI failed with exit={proc.returncode}: {proc.stderr.strip()[:300]}")
    return parse_wind_cli_response(proc.stdout, expected_code=code)


def _iso_from_wind_day(value: str) -> str:
    value = str(value)
    if len(value) != 8 or not value.isdigit():
        raise ValueError(f"invalid Wind date: {value}")
    return date(int(value[:4]), int(value[4:6]), int(value[6:8])).isoformat()


def build_receipt(metrics: Mapping[str, Mapping[str, Any]], cfg: Mapping[str, Any], *, as_of: date) -> dict[str, Any]:
    required = {"real_rate", "usd", "gold_price"}
    if set(metrics) != required:
        raise ValueError("minimum Reality Spine incomplete")
    defaults = cfg["research_defaults"]
    provider_receipts: dict[str, Any] = {}
    known_dates: list[str] = []
    for name in sorted(metrics):
        metric = metrics[name]
        value = metric.get("latest_value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError(f"non-finite or non-numeric provider value: {name}")
        known = _iso_from_wind_day(str(metric["latest_date"]))
        if known > as_of.isoformat():
            raise ValueError("future-dated provider evidence")
        known_dates.append(known)
        provider_receipts[name] = {
            "provider": "WIND",
            "metric_code": metric.get("meta", {}).get("code"),
            "metric_name": metric.get("meta", {}).get("name"),
            "source": metric.get("meta", {}).get("source"),
            "unit": metric.get("meta", {}).get("unit"),
            "latest_date": known,
            "latest_value": metric.get("latest_value"),
            "raw_sha256": metric.get("raw_sha256"),
        }
    unknowns = [
        "ust_context",
        "inflation_expectations",
        "policy_path_expectations",
        "official_demand_if_authoritative",
        "private_flow_positioning_if_authoritative",
        "narrative_crowding_if_authoritative",
        "property_drift_not_recomputed_daily; carry-forward from qualified G1 through 2026-08",
    ]
    return {
        "program": cfg["program"],
        "battle": cfg["battle"],
        "status": "LIVE_SHADOW_RECEIPT",
        "as_of": as_of.isoformat(),
        "known_as_of_max": max(known_dates),
        "known_as_of_min": min(known_dates),
        "provider_receipts": provider_receipts,
        "property_drift_state": defaults["property_drift_state"],
        "property_drift_lineage": defaults["property_drift_lineage"],
        "expectation_reality_state": defaults["expectation_reality_state"],
        "valuation_state": defaults["valuation_state"],
        "drivers": ["gold_price", "real_rate", "usd"],
        "falsifiers": [],
        "unknowns": unknowns,
        "research_state": defaults["research_state"],
        "lifecycle_state": defaults["lifecycle_state"],
        "authority": dict(cfg["authority"]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_receipt(receipt: Mapping[str, Any], runtime_dir: Path) -> Path:
    day = str(receipt.get("as_of") or date.today().isoformat())
    daily = runtime_dir / day
    daily.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    target = daily / f"receipt-{stamp}.json"
    text = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    target.write_text(text, encoding="utf-8")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "latest.json").write_text(text, encoding="utf-8")
    return target


def emit_learning_live(
    receipt: Mapping[str, Any],
    runtime_dir: Path,
    *,
    learning_cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run G7 only when its separate production integration gate is explicit."""
    cfg: dict[str, Any] = {}
    try:
        try:
            from scripts import ymq_gold2_learning_live as learning
        except ImportError:
            import ymq_gold2_learning_live as learning  # type: ignore
        cfg = dict(learning_cfg or learning.load_contract())
        learning.validate_contract(cfg)
        if cfg["authority"].get("production_scheduler_integration_authorized") is not True:
            return {
                "program": cfg["program"],
                "battle": cfg["battle"],
                "status": "LEARNING_INTEGRATION_NOT_AUTHORIZED",
                "as_of": receipt.get("as_of"),
                "accepted_learning": False,
                "authority": dict(cfg["authority"]),
            }
        learning.validate_live_receipt(receipt)
        return learning.process_current_receipt(receipt, runtime_dir, cfg)
    except Exception as exc:
        return {
            "program": cfg.get("program", "YMQ-GOLD2"),
            "battle": cfg.get("battle", "G7-LEARNING-LIVE"),
            "status": "LEARNING_FAIL_CLOSED",
            "as_of": receipt.get("as_of"),
            "error_type": type(exc).__name__,
            "accepted_learning": False,
            "authority": dict(cfg.get("authority", {})),
        }


def product_sink_enabled() -> bool:
    return os.getenv("YIOS_TG1_PRODUCT_SINK_ENABLED", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def _source_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        value = proc.stdout.strip()
        if proc.returncode == 0 and len(value) == 40:
            return value
    except Exception:
        pass
    return "LOCAL"


def emit_product_sink(receipt_path: Path, runtime_dir: Path) -> dict[str, Any]:
    """Optionally project a persisted G6 receipt into the governed TG1 Reality Sink.

    The hook is disabled by default. It never owns credentials and never writes
    them to disk. An unattended machine runtime must receive credentials through
    an independently authorized machine/runtime secret projection.
    """
    if not product_sink_enabled():
        return {
            "status": "PRODUCT_SINK_DISABLED",
            "authority": "SHADOW_ONLY",
        }

    client_raw = os.getenv("YIOS_TG1_SINK_CLIENT", "").strip()
    if not client_raw:
        return {
            "status": "PRODUCT_SINK_CLIENT_MISSING",
            "authority": "SHADOW_ONLY",
        }
    client = Path(client_raw).expanduser()
    if not client.is_file():
        return {
            "status": "PRODUCT_SINK_CLIENT_MISSING",
            "authority": "SHADOW_ONLY",
        }

    machine_ready = all(
        os.getenv(name, "").strip()
        for name in (
            "YIOS_TG1_MACHINE_INGEST_TOKEN",
            "YIOS_TG1_INGEST_ENDPOINT",
            "YIOS_TG1_MACHINE_CLIENT_ID",
        )
    )
    direct_ready = bool(
        os.getenv("SUPABASE_URL", "").strip()
        and os.getenv("YMQ4_SUPABASE_SECRET_KEY", "").strip()
    )
    if not (machine_ready or direct_ready):
        return {
            "status": "PRODUCT_SINK_CREDENTIALS_NOT_PROJECTED",
            "authority": "SHADOW_ONLY",
        }

    argv = [
        sys.executable,
        str(client),
        "--receipt",
        str(receipt_path),
        "--runner-commit",
        _source_commit(),
        "--config-version",
        "gold2_live_shadow.activation.v0.1",
    ]
    learning_path = runtime_dir / "learning" / "latest-learning.json"
    if learning_path.is_file():
        argv.extend(["--learning", str(learning_path)])

    try:
        proc = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if proc.returncode != 0:
            return {
                "status": "PRODUCT_SINK_FAIL_CLOSED",
                "exit_code": proc.returncode,
                "authority": "SHADOW_ONLY",
            }
        payload = json.loads(proc.stdout)
        if not isinstance(payload, dict):
            raise ValueError("sink client returned non-object JSON")
        if payload.get("authority") != "SHADOW_ONLY":
            raise ValueError("sink authority mismatch")
        return payload
    except Exception as exc:
        return {
            "status": "PRODUCT_SINK_FAIL_CLOSED",
            "error_type": type(exc).__name__,
            "authority": "SHADOW_ONLY",
        }


def default_cli_path() -> Path:
    env = os.getenv("WIND_MCP_CLI")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".agents" / "skills" / "wind-mcp-skill" / "scripts" / "cli.mjs"


def default_runtime_dir() -> Path:
    env = os.getenv("YMQ_GOLD2_SHADOW_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".yuanli" / "runtime" / "ymq_gold2_live_shadow"


def main() -> int:
    cfg = load_activation()
    validate_activation(cfg)
    today = date.today()
    state = pilot_state(today, cfg)
    if state != "ACTIVE":
        receipt = {
            "program": cfg["program"],
            "battle": cfg["battle"],
            "status": f"PILOT_{state}",
            "as_of": today.isoformat(),
            "authority": dict(cfg["authority"]),
        }
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0

    cli = default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(f"Wind MCP CLI not found: {cli}")
    metric_cfg = cfg["provider"]["metrics"]
    try:
        metrics = {
            name: query_wind_metric(cli, spec["code"])
            for name, spec in metric_cfg.items()
        }
        receipt = build_receipt(metrics, cfg, as_of=today)
    except Exception as exc:
        receipt = {
            "program": cfg["program"],
            "battle": cfg["battle"],
            "status": "PROVIDER_FAIL_CLOSED",
            "as_of": today.isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
            "unknowns": list(metric_cfg),
            "authority": dict(cfg["authority"]),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        runtime_dir = default_runtime_dir()
        target = write_receipt(receipt, runtime_dir)
        sink_result = emit_product_sink(target, runtime_dir)
        print(json.dumps({
            "receipt": str(target),
            "product_sink_status": sink_result.get("status"),
            **receipt,
        }, ensure_ascii=False, indent=2))
        return 2

    runtime_dir = default_runtime_dir()
    target = write_receipt(receipt, runtime_dir)
    learning_result = emit_learning_live(receipt, runtime_dir)
    sink_result = emit_product_sink(target, runtime_dir)
    print(json.dumps({
        "receipt": str(target),
        "learning_status": learning_result.get("status"),
        "product_sink_status": sink_result.get("status"),
        **receipt,
    }, ensure_ascii=False, indent=2))
    sink_failed = sink_result.get("status") in {
        "PRODUCT_SINK_CLIENT_MISSING",
        "PRODUCT_SINK_CREDENTIALS_NOT_PROJECTED",
        "PRODUCT_SINK_FAIL_CLOSED",
    }
    return 3 if sink_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
