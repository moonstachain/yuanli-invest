#!/usr/bin/env python3
"""Render or explicitly activate the single daily machine job."""

import argparse
import getpass
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

from scripts.research_worker import MachineGateway, load_source
from scripts import ymq_gold2_live_shadow as shadow

REPO = Path(__file__).resolve().parents[1]


def host_timezone():
    return str(Path("/etc/localtime").resolve()).rsplit("zoneinfo/", 1)[-1]


def main():
    parser = argparse.ArgumentParser(description="Render the 08:10 Asia/Shanghai machine schedule; activation is explicit.")
    parser.add_argument("--activate", action="store_true", help="Replace the existing same-label launchd job; never run immediately")
    parser.add_argument("--output", type=Path, help="Review file path (render only)")
    args = parser.parse_args()
    try:
        if args.activate and args.output:
            raise ValueError("--output is for review; omit it when activating")
        if host_timezone() != "Asia/Shanghai":
            raise ValueError("launchd host timezone must be Asia/Shanghai")
        source_path = Path(os.environ["YUANLI_RESEARCH_SOURCE_CONFIG"]).expanduser().resolve(strict=True)
        source = load_source(source_path)
        cfg = shadow.load_activation()
        shadow.validate_activation(cfg)
        if source["series_id"] != cfg["provider"]["metrics"]["gold_price"]["code"]:
            raise ValueError("reviewed source must match the Gold collector series")
        endpoint = os.environ["YUANLI_RESEARCH_MACHINE_URL"]
        client = os.environ["YIOS_TG1_MACHINE_CLIENT_ID"]
        workspace = os.environ["YUANLI_WORKSPACE_ID"]
        MachineGateway(endpoint, client, "configuration-validation-only", workspace)
        node = Path(os.environ.get("NODE_BIN") or shutil.which("node") or "").resolve()
        cli = Path(os.environ["WIND_MCP_CLI"]).expanduser().resolve(strict=True)
        if not node.is_file() or not os.access(node, os.X_OK):
            raise ValueError("set an executable NODE_BIN")
        runtime_dir = Path(os.environ.get("YMQ_GOLD2_SHADOW_DIR", str(Path.home() / ".yuanli/runtime/ymq_gold2_live_shadow"))).expanduser().resolve()
        label = "com.yuanli.ymq-gold2-live-shadow"
        keychain = os.environ.get("YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE", "yuanli.yios-tg1.machine-ingest-token")
        account = os.environ.get("YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_ACCOUNT", getpass.getuser())
        # Same label as the old collector prevents a second scheduled writer.
        plist = {
            "Label": label,
            "ProgramArguments": [str(REPO / "scripts/run_ymq_gold2_live_shadow_machine.sh")],
            "WorkingDirectory": str(REPO),
            "EnvironmentVariables": {
                "PYTHON_BIN": sys.executable,
                "WIND_MCP_CLI": str(cli),
                "YMQ_GOLD2_SHADOW_DIR": str(runtime_dir),
                "YUANLI_RESEARCH_SOURCE_CONFIG": str(source_path),
                "YUANLI_RESEARCH_MACHINE_URL": endpoint,
                "YUANLI_WORKSPACE_ID": workspace,
                "YIOS_TG1_MACHINE_CLIENT_ID": client,
                "YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE": keychain,
                "YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_ACCOUNT": account,
                "PATH": f"{node.parent}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
            },
            "StartCalendarInterval": {"Hour": 8, "Minute": 10},
            "RunAtLoad": False,
            "StandardOutPath": str(runtime_dir / "logs/stdout.log"),
            "StandardErrorPath": str(runtime_dir / "logs/stderr.log"),
        }
        destination = (Path.home() / "Library/LaunchAgents" / f"{label}.plist") if args.activate else (args.output or runtime_dir / "launchd" / f"{label}.plist")
        if args.activate:
            subprocess.run(["/usr/bin/security", "find-generic-password", "-a", account, "-s", keychain], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(plistlib.dumps(plist))
        if args.activate:
            (runtime_dir / "logs").mkdir(parents=True, exist_ok=True)
            subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(destination)], check=True)
        print(json.dumps({"status": "ACTIVATED" if args.activate else "RENDERED_ONLY", "path": str(destination), "schedule": "08:10 Asia/Shanghai", "run_at_load": False}))
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "CONFIGURATION_ERROR", "error_type": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
