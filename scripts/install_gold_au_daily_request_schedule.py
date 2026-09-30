#!/usr/bin/env python3
"""Render the local 08:25 AU request assembly job; activate only explicitly."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gold_au_daily_request import _private_child  # noqa: E402
from scripts.gold_au_decision_worker import _private_root  # noqa: E402

LABEL = "com.yuanli.gold2-au-0825-request-assembly"


def render(runtime_dir: Path) -> dict:
    runtime = _private_root(runtime_dir)
    zone_path = Path("/etc/localtime").resolve()
    if zone_path.parts[-2:] != ("Asia", "Shanghai") or "zoneinfo" not in str(zone_path):
        raise ValueError("host timezone must be Asia/Shanghai")
    if sys.version_info < (3, 12):
        raise ValueError("Python >= 3.12 required")
    return {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(ROOT / "scripts/gold_au_daily_request.py"),
                             "--runtime-dir", str(runtime), "--execute"],
        "WorkingDirectory": str(ROOT),
        "StartCalendarInterval": [{"Weekday": weekday, "Hour": 8, "Minute": 25}
                                  for weekday in range(1, 6)],
        "RunAtLoad": False,
        "StandardOutPath": str(runtime / "logs/request_assembly_stdout.log"),
        "StandardErrorPath": str(runtime / "logs/request_assembly_stderr.log"),
    }


def install(runtime_dir: Path, *, activate: bool = False, runner=subprocess.run) -> dict:
    runtime = _private_root(runtime_dir)
    encoded = plistlib.dumps(render(runtime))
    if activate:
        _private_child(runtime, "logs")
        directory = Path.home() / "Library/LaunchAgents"
        if directory.is_symlink():
            raise ValueError("SYMLINK_LAUNCH_AGENTS_DIRECTORY")
        directory.mkdir(parents=True, exist_ok=True)
    else:
        directory = _private_child(runtime, "launchd")
    destination = directory / (LABEL + ".plist")
    if destination.is_symlink():
        raise ValueError("SYMLINK_SCHEDULE_DESTINATION")
    fd, temporary = tempfile.mkstemp(prefix=".gold-au-assembly-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    if activate:
        runner(["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL}"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        runner(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(destination)], check=True)
    return {"status": "ACTIVATED_READ_ONLY" if activate else "RENDERED_ONLY",
            "path": str(destination), "schedule": "weekdays 08:25 Asia/Shanghai",
            "broker_action_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.runtime_dir, activate=args.activate), ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "CONFIGURATION_ERROR", "reason": str(exc),
                          "broker_action_authorized": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
