#!/usr/bin/env python3
"""Render a local 08:30 research-only launchd job; activate explicitly."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

LABEL = "com.yuanli.gold2-au-0830-research-decision"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gold_au_decision_worker import _private_root  # noqa: E402


def render(runtime_dir: Path) -> dict:
    runtime = _private_root(runtime_dir)
    zone_path = Path("/etc/localtime").resolve()
    if zone_path.parts[-2:] != ("Asia", "Shanghai") or "zoneinfo" not in str(zone_path):
        raise ValueError("host timezone must be Asia/Shanghai")
    if sys.version_info < (3, 12):
        raise ValueError("Python >= 3.12 required")
    return {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(ROOT / "scripts/gold_au_decision_worker.py"),
                             "--runtime-dir", str(runtime), "--execute"],
        "WorkingDirectory": str(ROOT),
        "StartCalendarInterval": [{"Weekday": weekday, "Hour": 8, "Minute": 30}
                                  for weekday in range(1, 6)],
        "RunAtLoad": False,
        "StandardOutPath": str(runtime / "logs/stdout.log"),
        "StandardErrorPath": str(runtime / "logs/stderr.log"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="render destination; default is runtime/launchd")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    try:
        if args.activate and args.output:
            raise ValueError("--output is incompatible with --activate")
        runtime = _private_root(args.runtime_dir)
        plist = render(runtime)
        encoded = plistlib.dumps(plist)
        if args.activate:
            destination = Path.home() / "Library/LaunchAgents" / (LABEL + ".plist")
            (runtime / "logs").mkdir(mode=0o700, exist_ok=True)
            (runtime / "requests").mkdir(mode=0o700, exist_ok=True)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(encoded)
            subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL}"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(destination)], check=True)
        else:
            destination = args.output or runtime / "launchd" / (LABEL + ".plist")
            destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            destination.write_bytes(encoded)
        print(json.dumps({"status": "ACTIVATED_READ_ONLY" if args.activate else "RENDERED_ONLY",
                          "path": str(destination), "schedule": "weekdays 08:30 Asia/Shanghai",
                          "broker_action_authorized": False}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "CONFIGURATION_ERROR", "reason": str(exc),
                          "broker_action_authorized": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
