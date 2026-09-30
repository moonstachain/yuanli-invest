#!/usr/bin/env python3
"""Sample macOS morning availability without running research or broker code.

--sample-now writes a current-state receipt only. --observe-window starts only
in the real 07:55 minute of an approved SHFE session and finishes at 09:20.
Receipts prove sampled states, never continuous availability or external time.
"""
from __future__ import annotations

import argparse
from datetime import datetime, time, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import time as timer
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
MAX_BYTES = 2_000_000


def hash_json(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("BOUNDED_REGULAR_JSON_REQUIRED")
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return value


def private_dir(path: Path) -> Path:
    path = path.expanduser().absolute()
    if path != path.resolve() or path.is_symlink():
        raise ValueError("PRIVATE_REAL_PATH_REQUIRED")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise ValueError("PRIVATE_DIRECTORY_REQUIRED")
    return path


def exclusive_json(path: Path, value: dict) -> None:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def property_values(value, key: str) -> list:
    result = []
    if isinstance(value, dict):
        if key in value:
            result.append(value[key])
        for child in value.values():
            if isinstance(child, (dict, list)):
                result.extend(property_values(child, key))
    elif isinstance(value, list):
        for child in value:
            result.extend(property_values(child, key))
    return result


def observe_host(runner=subprocess.run) -> dict:
    def command(args: list[str], *, plist=False):
        try:
            result = runner(args, capture_output=True, timeout=3, check=False)
            if result.returncode or len(result.stdout) > MAX_BYTES:
                return None
            return plistlib.loads(result.stdout) if plist else result.stdout.decode()
        except (OSError, ValueError, subprocess.SubprocessError, plistlib.InvalidFileException):
            return None
    power = command(["/usr/bin/pmset", "-g", "ps"])
    lid = property_values(command(["/usr/sbin/ioreg", "-a", "-r", "-d", "1", "-k", "AppleClamshellState"], plist=True), "AppleClamshellState")
    users = property_values(command(["/usr/sbin/ioreg", "-a", "-r", "-d", "1", "-k", "IOConsoleUsers"], plist=True), "IOConsoleUsers")
    network = command(["/usr/sbin/scutil", "--nwi"])
    console = [u for group in users if isinstance(group, list) for u in group if isinstance(u, dict)]
    return {
        "ac_power": None if power is None else "Now drawing from 'AC Power'" in power,
        "lid_open": None if not lid or any(type(x) is not bool for x in lid) else not any(lid),
        "console_session": None if not console else any(u.get("kCGSSessionOnConsoleKey") is True and u.get("kCGSessionLoginDoneKey") is True and u.get("kCGSSessionUserIDKey") == os.getuid() for u in console),
        "network_route_reachable": None if network is None else bool(re.search(r"\(Reachable\)", network)),
        "provider_endpoint_reachability": "NOT_CHECKED",
        "external_time_anchor": "NOT_VERIFIED",
        "broker_action_authorized": False,
    }


def authorize_day(config: dict, now: datetime) -> str:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("REAL_AWARE_CLOCK_REQUIRED")
    if config.get("schema_version") != "gold2-host-observer-config.v1":
        raise ValueError("CONFIG_VERSION_REQUIRED")
    day = now.astimezone(SHANGHAI).date().isoformat()
    if day >= config["expires_on_exclusive"]:
        return "EXPIRED"
    path = Path(config["calendar_receipt_path"])
    calendar = read_json(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != config["calendar_receipt_sha256"]:
        raise ValueError("CALENDAR_RECEIPT_HASH_CHANGED")
    raw = Path(calendar["raw_file"])
    if raw.is_symlink() or not raw.is_file() or raw.stat().st_size > MAX_BYTES or hashlib.sha256(raw.read_bytes()).hexdigest() != calendar["raw_sha256"]:
        raise ValueError("CALENDAR_RAW_HASH_CHANGED")
    if not calendar["coverage_start"] <= day <= calendar["coverage_end"]:
        raise ValueError("CALENDAR_COVERAGE_REQUIRED")
    if day not in calendar["sessions"]:
        return "OFFICIAL_NON_SESSION"
    local = now.astimezone(SHANGHAI)
    return "ELIGIBLE_START" if local.hour == 7 and local.minute == 55 else "MISSED_START_MINUTE"


def assess(samples: list[dict], start: datetime, end: datetime) -> dict:
    required = ("ac_power", "lid_open", "console_session", "network_route_reachable")
    failures = sorted({key for sample in samples for key in required if sample["host"].get(key) is not True})
    wall = [datetime.fromisoformat(s["observed_at"]) for s in samples]
    mono = [s["elapsed_monotonic_seconds"] for s in samples]
    gaps = [mono[i] - mono[i-1] for i in range(1, len(mono))]
    drifts = [abs((wall[i] - wall[i-1]).total_seconds() - gaps[i-1]) for i in range(1, len(wall))]
    complete = bool(wall) and start <= wall[0] < start.replace(minute=56) and end <= wall[-1] <= end.replace(second=15)
    if not complete:
        failures.append("WINDOW_ENDPOINTS_MISSING")
    if any(gap <= 0 or gap > 75 for gap in gaps):
        failures.append("SAMPLE_GAP")
    if any(drift > 5 for drift in drifts):
        failures.append("WALL_MONOTONIC_DIVERGENCE")
    if len(samples) < 85:
        failures.append("INSUFFICIENT_SAMPLES")
    return {"status": "SAMPLED_WINDOW_MET" if not failures else "SAMPLED_WINDOW_NOT_MET", "failures": sorted(set(failures)), "sample_count": len(samples), "maximum_sample_gap_seconds": max(gaps, default=None), "maximum_clock_divergence_seconds": max(drifts, default=None), "continuous_availability_proven": False, "external_time_anchor": "NOT_VERIFIED", "broker_action_authorized": False}


def observe_window(config: dict, runtime: Path) -> dict:
    now = datetime.now(timezone.utc)
    gate = authorize_day(config, now)
    if gate != "ELIGIBLE_START":
        return {"status": gate, "observed_at": now.isoformat(), "worker_started": False, "broker_action_authorized": False}
    local = now.astimezone(SHANGHAI)
    output = runtime / local.date().isoformat()
    output.mkdir(mode=0o700)  # One immutable attempt per date; restart cannot replace it.
    start = datetime.combine(local.date(), time(7, 55), SHANGHAI)
    end = datetime.combine(local.date(), time(9, 20), SHANGHAI)
    exclusive_json(output / "attempt.json", {"schema_version": "gold2-host-observer-attempt.v1", "started_at": now.isoformat(), "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "config_sha256": hash_json(config), "broker_action_authorized": False})
    origin = timer.monotonic()
    samples = []
    previous = "0" * 64
    with open(output / "samples.jsonl", "x", encoding="utf8") as stream:
        os.chmod(output / "samples.jsonl", 0o600)
        while True:
            sample = {"seq": len(samples), "observed_at": datetime.now(timezone.utc).isoformat(), "elapsed_monotonic_seconds": round(timer.monotonic() - origin, 6), "previous_sha256": previous, "host": observe_host()}
            # Timestamp after the bounded OS reads so it is an actual completion.
            sample["observed_at"] = datetime.now(timezone.utc).isoformat()
            sample["elapsed_monotonic_seconds"] = round(timer.monotonic() - origin, 6)
            previous = hash_json(sample)
            sample["sha256"] = previous
            stream.write(json.dumps(sample, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            samples.append(sample)
            remaining = (end - datetime.now(timezone.utc)).total_seconds()
            if remaining <= 0 or timer.monotonic() - origin >= 5115:
                break
            timer.sleep(min(60, remaining, max(0, 5115 - (timer.monotonic() - origin))))
    summary = {"schema_version": "gold2-host-observer-window.v1", "completed_at": datetime.now(timezone.utc).isoformat(), "window_start": start.isoformat(), "window_end": end.isoformat(), "chain_root_sha256": previous, "samples_file_sha256": hashlib.sha256((output / "samples.jsonl").read_bytes()).hexdigest(), **assess(samples, start, end)}
    exclusive_json(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sample-now", action="store_true")
    mode.add_argument("--observe-window", action="store_true")
    args = parser.parse_args()
    try:
        runtime = private_dir(args.runtime_dir)
        config = read_json(args.config)
        if args.sample_now:
            result = {"schema_version": "gold2-host-observer-current.v1", "observed_at": datetime.now(timezone.utc).isoformat(), "status": "CURRENT_STATE_ONLY", "host": observe_host(), "natural_acceptance": False}
            exclusive_json(runtime / ("current-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"), result)
        else:
            result = observe_window(config, runtime)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "OBSERVER_DENIED", "reason": type(exc).__name__, "worker_started": False, "broker_action_authorized": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
