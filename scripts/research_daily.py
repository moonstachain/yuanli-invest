#!/usr/bin/env python3
"""One daily machine run: collect once, ingest once, capture and settle claims."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

from yuanli_invest.time import instant

if __package__:
    from . import ymq_gold2_live_shadow as shadow
    from .research_sink import publish_receipt
    from .research_worker import MachineGateway, load_source, run_once, wind_payload
else:
    import ymq_gold2_live_shadow as shadow
    from research_sink import publish_receipt
    from research_worker import MachineGateway, load_source, run_once, wind_payload

SCHEDULE_ZONE = ZoneInfo("Asia/Shanghai")


def run_daily(*, cfg, source, cli_path, runtime_dir, gateway, fetch=wind_payload, clock=lambda: datetime.now(timezone.utc)):
    shadow.validate_activation(cfg)
    day = instant(clock()).astimezone(SCHEDULE_ZONE).date()
    state = shadow.pilot_state(day, cfg)
    if state != "ACTIVE":
        return {"status": f"PILOT_{state}"}
    source_zone = ZoneInfo(source["source_timezone"])
    metrics = cfg["provider"]["metrics"]
    if source["series_id"] != metrics["gold_price"]["code"]:
        raise ValueError("reviewed Gold source does not match the collector series")
    raw, failures = {}, {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {name: pool.submit(fetch, cli_path, spec["code"]) for name, spec in metrics.items()}
        for name, future in pending.items():
            try:
                raw[name] = future.result()
            except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
                failures[name] = type(exc).__name__
    try:
        if failures:
            raise RuntimeError("provider collection incomplete")
        parsed = {name: shadow.parse_wind_cli_response(data.decode("utf-8"), expected_code=metrics[name]["code"]) for name, data in raw.items()}
        receipt = shadow.build_receipt(parsed, cfg, as_of=day)
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        receipt = {"program": cfg["program"], "battle": cfg["battle"], "as_of": day.isoformat(), "generated_at": instant(clock()).isoformat(), "status": "PROVIDER_FAIL_CLOSED", "error_type": type(exc).__name__, "authority": dict(cfg["authority"])}
    target = shadow.write_receipt(receipt, runtime_dir)
    learning = shadow.emit_learning_live(receipt, runtime_dir) if receipt["status"] == "LIVE_SHADOW_RECEIPT" else {}
    learning_path = learning.get("learning_receipt_path")
    errors = []
    if learning.get("status") == "LEARNING_FAIL_CLOSED":
        errors.append({"operation": "learning_live", "error_type": learning.get("error_type")})
    try:
        publish_receipt(
            gateway, receipt,
            learning=json.loads(Path(learning_path).read_text()) if learning_path else None,
            runner_commit=os.getenv("GITHUB_SHA", "LOCAL"),
        )
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        errors.append({"operation": "ingest_receipt", "error_type": type(exc).__name__})
    def captured_gold():
        if "gold_price" not in raw:
            raise RuntimeError("Gold source capture unavailable")
        return raw["gold_price"]
    trade_date = (instant(clock()).astimezone(source_zone).date() - timedelta(days=1)).isoformat()
    worker = run_once(fetch=captured_gold, gateway=gateway, source=source, day=trade_date, clock=clock)
    return {
        "status": "SYSTEM_ERROR" if errors or worker["status"] == "SYSTEM_ERROR" or receipt["status"] == "PROVIDER_FAIL_CLOSED" else "COMPLETE",
        "receipt_path": str(target), "snapshot_status": receipt["status"], "worker": worker, "errors": errors,
    }


def main() -> int:
    try:
        if not str(Path("/etc/localtime").resolve()).endswith("/Asia/Shanghai"):
            raise ValueError("launchd host timezone must be Asia/Shanghai")
        cfg = shadow.load_activation()
        source = load_source(Path(os.environ["YUANLI_RESEARCH_SOURCE_CONFIG"]))
        runtime_dir = shadow.default_runtime_dir()
        runtime_dir.mkdir(parents=True, exist_ok=True)
        with (runtime_dir / "daily-machine.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print(json.dumps({"status": "ALREADY_RUNNING"}))
                return 0
            result = run_daily(cfg=cfg, source=source, cli_path=shadow.default_cli_path(), runtime_dir=runtime_dir, gateway=MachineGateway.from_environment())
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        result = {"status": "SYSTEM_ERROR", "error_type": type(exc).__name__}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 2 if result["status"] == "SYSTEM_ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
