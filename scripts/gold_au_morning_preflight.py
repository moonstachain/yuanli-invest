#!/usr/bin/env python3
"""Current-time, read-only morning readiness; never run a scheduled worker.

The only subprocesses are launchctl print, Python version and pmset -g. Future
session seed checks are static proposals, not a simulated 08:30 or acceptance.
No network, broker, receipt-service key or trading SQLite write is available.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from scripts.gold_au_operations_rehearsal import audit_tasks, EXPECTED, read_json
from scripts.gold_au_research_diagnostic import accept_natural_morning
from scripts.gold_au_shfe_archive_worker import prepare_archive
from yuanli_invest.gold_au_live_snapshot import SHANGHAI, _mapping
from yuanli_invest.gold_au_official_calendar import load_calendar_receipt, session_window


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(root: Path, value) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("EXPLICIT_PATH_REQUIRED")
    path = Path(value)
    return path if path.is_absolute() else root / path


def python_version(executable: Path, runner=subprocess.run) -> dict:
    """Interpreter inspection is isolated and never imports project code."""
    try:
        reply = runner([str(executable), "-I", "-c", "import json,sys;print(json.dumps(list(sys.version_info[:3])))"],
                       capture_output=True, text=True, timeout=5, check=False)
        version = json.loads(reply.stdout[:128])
        if reply.returncode or not isinstance(version, list) or len(version) != 3 or any(type(i) is not int for i in version):
            raise ValueError
        return {"status": "VERIFIED_LOCAL_PYTHON312" if tuple(version) >= (3, 12, 0) else "UNSUPPORTED",
                "version": version, "cloud_python_verified": False}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"status": "UNKNOWN", "version": None, "cloud_python_verified": False}


def inspect_power(runner=subprocess.run) -> dict:
    result = {"status": "HOST_AWAKE_AT_TRIGGER_NOT_GUARANTEED", "changed": False,
              "sleep_minutes": {}, "target_day_wake_proof": "UNKNOWN", "read_only": True,
              "current_prevent_idle_sleep_assertion": "UNKNOWN", "assertion_survives_until_monday": "UNKNOWN"}
    try:
        reply = runner(["pmset", "-g", "custom"], capture_output=True, text=True, timeout=3, check=False)
        if reply.returncode:
            return result
        current = None
        for line in reply.stdout[:30000].splitlines():
            if line.strip() in {"Battery Power:", "AC Power:"}:
                current = line.strip().rstrip(":")
            match = re.fullmatch(r"\s*sleep\s+(\d+)\s*", line)
            if current and match:
                result["sleep_minutes"][current] = int(match.group(1))
        assertions = runner(["pmset", "-g", "assertions"], capture_output=True, text=True, timeout=3, check=False)
        match = re.search(r"(?m)^\s*PreventUserIdleSystemSleep\s+(\d+)\s*$", assertions.stdout[:50000])
        if assertions.returncode == 0 and match:
            result["current_prevent_idle_sleep_assertion"] = int(match.group(1)) > 0
    except (OSError, subprocess.SubprocessError):
        pass
    return result


def inspect_automation(path: Path, *, as_of: datetime, decision_day: str, probe_sha256: str) -> dict:
    result = {"status": "UNKNOWN", "source_sha256": None, "changed": False,
              "schedule_is_future_acceptance": True, "broker_action_authorized": False}
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 100000:
            raise ValueError
        raw = path.read_bytes(); value = tomllib.loads(raw.decode())
        prompt = value.get("prompt", "")
        if not isinstance(prompt, str):
            raise ValueError
        lifecycle = value.get("status")
        accept_days = re.findall(r"(?<!\S)--accept-day[ \t]+(\d{4}-\d{2}-\d{2})(?!\d)", prompt)
        observer_windows = re.findall(r"\d{4}-\d{2}-\d{2}北京时间09:15–09:20", prompt)
        rules = {
            "correct_id": value.get("id") == "gold2-au-simnow",
            "active": lifecycle == "ACTIVE",
            "heartbeat": value.get("kind") == "heartbeat",
            "weekday_0915_schedule": value.get("rrule") == "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=15",
            "explicit_natural_accept_day": accept_days == [decision_day],
            "single_attempt_window": observer_windows == [f"{decision_day}北京时间09:15–09:20"] and "09:18:20" in prompt,
            "correct_readonly_probe_hash": probe_sha256.removeprefix("sha256:") in prompt,
            "no_backfill": "不把09:15成本回填08:30" in prompt,
            "formal_permission_deny": "保持正式交易权限DENY" in prompt,
            "watchdog_90_seconds": "外部90秒watchdog" in prompt,
            "no_order_or_cancel": "禁止下单、撤单" in prompt,
            "no_retry": "失败不得清除标记或重试" in prompt,
            "quiet_until_actionable": "未变化" in prompt and "保持安静" in prompt,
        }
        updated = value.get("updated_at")
        if type(updated) is not int or updated > int(as_of.timestamp() * 1000):
            raise ValueError
        other_rules_match = all(value for name, value in rules.items() if name != "active")
        if other_rules_match and lifecycle == "ACTIVE":
            status = "CONFIGURED_NOT_EXECUTED"
        elif lifecycle == "PAUSED":
            status = "PAUSED_CONFIGURED" if other_rules_match else "PAUSED_CONFIG_MISMATCH"
        else:
            status = "CONFIG_MISMATCH"
        result.update({"status": status, "lifecycle_status": lifecycle,
                       "requested_decision_day": decision_day,
                       "source_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(), "rules": rules,
                       "name": value.get("name"), "updated_at": datetime.fromtimestamp(updated/1000, timezone.utc).isoformat(),
                       "notification_policy_from_prompt": "MEANINGFUL_EVENT_ONLY"})
    except (OSError, ValueError, UnicodeError):
        result["reason"] = "AUTOMATION_MISSING_OR_INVALID"
    return result


def collect_preflight(runtime: Path, *, decision_day: str, as_of: datetime, launch_dir: Path,
                      automation_path: Path, repo: Path = ROOT, task_observer=None,
                      version_reader=python_version, power_reader=inspect_power) -> dict:
    if as_of.tzinfo is None or date.fromisoformat(decision_day).isoformat() != decision_day:
        raise ValueError("REAL_AWARE_OBSERVATION_AND_CANONICAL_DAY_REQUIRED")
    now = as_of.astimezone(timezone.utc)
    source_path, archive_path = runtime / "daily_request_sources.json", runtime / "shfe_archive_sources.json"
    sources, archive = read_json(source_path), read_json(archive_path)
    kwargs = {"as_of": now, "launch_dir": launch_dir}
    if task_observer is not None:
        kwargs["observer"] = task_observer
    tasks = audit_tasks(runtime, **kwargs)
    for item in tasks:
        script = EXPECTED[item["label"]][2]
        try:
            config = plistlib.loads((launch_dir / (item["label"] + ".plist")).read_bytes())
            args = config.get("ProgramArguments", [])
            item["exact_repo_arguments_match"] = (args == [str(repo / ".venv/bin/python"), str(repo / "scripts" / script),
                                                        "--runtime-dir", str(runtime), "--execute"]
                                                 and config.get("WorkingDirectory") == str(repo))
            item["worker_source_sha256"] = _sha(repo / "scripts" / script)
        except (OSError,ValueError,plistlib.InvalidFileException):
            item.update(exact_repo_arguments_match=False, worker_source_sha256=None)
    calendar_path = _resolve(runtime, sources.get("calendar_receipt_path"))
    if _resolve(runtime, archive.get("calendar_receipt_path")) != calendar_path:
        raise ValueError("PRODUCER_CALENDAR_MISMATCH")
    calendar = load_calendar_receipt(calendar_path, as_of=now)
    window = session_window(calendar, date.fromisoformat(decision_day), prior_count=273, horizons=(5, 20))
    seeds = archive.get("seed_manifest_paths")
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= 8:
        raise ValueError("EXPLICIT_BOUNDED_SEEDS_REQUIRED")
    def forbidden_fetch(*args):
        raise AssertionError("preflight cannot fetch")
    proposal = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[_resolve(runtime, p) for p in seeds],
                               decision_day=date.fromisoformat(decision_day), observed_at=now,
                               output_dir=runtime / "shfe_archives" / decision_day,
                               execute=False, fetch_missing=False, fetch=forbidden_fetch)
    mapping_path = _resolve(runtime, sources.get("h10_mapping_receipt_path"))
    mapping, mapping_sha = _mapping(mapping_path, now)
    natural = accept_natural_morning(runtime, decision_date=decision_day, as_of=now)
    for key, row in natural["inputs"].items():
        row["dependency_role"] = ("EXECUTION_ONLY_NOT_RESEARCH_INPUT" if key == "account_cost_margin" and sources.get("execution_mode") == "RESEARCH_ONLY"
                                  else "RESEARCH_NATURAL_DAY_INPUT")
        if row["status"] == "MISSING_OR_INVALID" and date.fromisoformat(decision_day) > now.astimezone(SHANGHAI).date():
            row["preflight_interpretation"] = "EXPECTED_NOT_RUN_BEFORE_TARGET_DAY"
    probe_sha = _sha(repo / "scripts/youquant_gold_simnow_readonly_cost_probe.py")
    automation = inspect_automation(automation_path, as_of=now, decision_day=decision_day, probe_sha256=probe_sha)
    version = version_reader(repo / ".venv/bin/python")
    power = power_reader()
    research_static_ok = (all(i["installation"] == "LOADED" and i["config_status"] == "MATCHES_FROZEN_WEEKDAY_SCHEDULE"
                     and i["exact_repo_arguments_match"] for i in tasks)
                 and version["status"] == "VERIFIED_LOCAL_PYTHON312"
                 and sources.get("execution_mode") == "RESEARCH_ONLY"
                 and proposal["retained_reports"] == 273 and proposal["missing_official_sessions"] == [])
    research_static_status = ("STATIC_PREREQUISITES_VERIFIED_ACCEPTANCE_PENDING" if research_static_ok
                              else "STATIC_PREREQUISITES_INCOMPLETE")
    return {"schema_version": "gold-au-natural-morning-preflight.v2", "kind": "CURRENT_READONLY_PREFLIGHT",
            "observed_at": now.isoformat(), "observed_shanghai": now.astimezone(SHANGHAI).isoformat(),
            "decision_date": decision_day, "status": research_static_status, "status_scope": "RESEARCH_STATIC_ONLY",
            "research_static_status": research_static_status,
            "research_static_prerequisites_verified": research_static_ok,
            "simnow_observer_status": automation["status"],
            "simnow_observer_configuration_ready": automation["status"] == "CONFIGURED_NOT_EXECUTED",
            "natural_acceptance": natural, "static_prerequisites_verified": research_static_ok,
            "actual_acceptance_pass_count": 0, "formal_observation_started": False,
            "scheduled_workers_started": False, "broker_action_authorized": False,
            "network_requests": 0, "original_runtime_modified": False, "power_settings_changed": False,
            "tasks": tasks, "python": version, "host_power": power, "automation": automation,
            "calendar": {"status": "OFFICIAL_BYTES_VERIFIED_FOR_PLANNED_SESSION", "receipt_sha256": _sha(calendar_path),
                         "raw_sha256": calendar["raw_sha256"], **{k:v for k,v in window.items() if k != "prior_sessions"}},
            "shfe_seed": {"status": "VERIFIED_EXISTING_RAW_BYTES_NOT_NATURAL_CAPTURE", "prior_sessions": proposal["requested_days"],
                          "retained_reports": proposal["retained_reports"], "missing_official_sessions": proposal["missing_official_sessions"],
                          "interval": proposal["interval"], "new_requests": 0, "source_manifests": proposal["source_manifests"]},
            "source_catalogs": {"daily_request_sha256": _sha(source_path), "archive_sha256": _sha(archive_path),
                                "execution_mode": sources.get("execution_mode"), "h10_mapping_sha256": "sha256:" + mapping_sha,
                                "h10_witnessed_at": mapping["witnessed_at"]},
            "producer_sequence": [{"time_shanghai": "08:05", "job": "SHFE_ARCHIVE", "deadline": "08:10", "network": "ZERO_IF_VERIFIED_SEED_COMPLETE"},
                                  {"time_shanghai": "08:10", "job": "FRED_CAPTURE", "start_deadline": "08:20", "network": "TWO_PUBLIC_BOUNDED_GETS"},
                                  {"time_shanghai": "08:25", "job": "LOCAL_REQUEST_ASSEMBLY", "deadline": "08:30", "network": "NONE"},
                                  {"time_shanghai": "08:30", "job": "LOCAL_RESEARCH_FREEZE", "network": "NONE"}],
            "simnow_observer_schedule": {"time_shanghai": "09:15", "job": "READONLY_ACCEPTANCE_HEARTBEAT",
                                         "not_before": decision_day+"T09:15:00+08:00", "status": automation["status"]},
            "unresolved_runtime_requirements": ["MAC_AWAKE_AND_USER_SESSION_PRESENT_0805_0835", "PUBLIC_NETWORK_AND_FRED_CURRENT_BYTES_AT_0810",
                                                "REAL_NATURAL_0830_TRIGGER_AND_FROZEN_LOG", "INDEPENDENT_TIME_ANCHOR_NOT_ESTABLISHED_BY_LOCAL_LOG"],
            "interpretation": "Research readiness excludes the independent 09:15 SimNow observer. Future missing daily inputs, zero runs and installed schedules cannot become an accepted natural decision. 09:15 costs cannot backfill 08:30."}


def write_report(directory: Path, report: dict) -> None:
    if not directory.is_absolute() or directory.exists() or directory.is_symlink():
        raise ValueError("NEW_ABSOLUTE_OUTPUT_DIRECTORY_REQUIRED")
    directory.mkdir(mode=0o700, parents=False)
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()
    loaded = sum(i["installation"] == "LOADED" for i in report["tasks"])
    verified = sum(i["exact_repo_arguments_match"] for i in report["tasks"])
    day = report["decision_date"]
    texts = {"preflight.json": raw, f"{day}-晨间就绪清单.md": (
        f"# {day} 自然晨间就绪清单\n\n"
        +f"真实检查时点：{report['observed_shanghai']}。研究静态状态：{report['research_static_status']}；SimNow 只读观察者状态：{report['simnow_observer_status']}。自然验收仍为 {report['natural_acceptance']['status']}。\n\n"
        +f"晨间任务加载 {loaded}/4；精确仓库参数一致 {verified}/4；本地解释器：{report['python']['status']}。各任务真实运行计数：{[i['runs'] for i in report['tasks']]}，不代表已通过自然验收。上期所已验证历史报告 {report['shfe_seed']['retained_reports']} 个；缺失的先前交易日：{report['shfe_seed']['missing_official_sessions']}。目标日 08:05 仍需自然生成当日归档回执。08:10 两列 FRED 数据、08:25 请求和 08:30 冻结结果只能等待真实自然时点取得，不提前制造。\n\n"
        +f"研究配置：{report['source_catalogs']['execution_mode']}。RESEARCH_ONLY 的晨间研究不要求 09:15 账户成本输入；成本与保证金仍是执行必需条件，不能事后回填 08:30。09:15 heartbeat 配置状态：{report['simnow_observer_status']}；它独立于研究静态预检，且配置不等于已执行。\n\n"
        +f"当前防闲置睡眠断言：{report['host_power']['current_prevent_idle_sleep_assertion']}；其目标日存续未知。系统空闲睡眠设置需留意，人工睡眠、关机和断网仍不保证任务执行。请在目标日 07:55–09:20 插电保持 Mac 唤醒且登录用户会话。没有修改能耗、系统时间或账户设置，也未改变现有防睡眠进程。\n\n"
        +"自然决定本地账本不等于独立时间证明。验收须保留真实开始时间、输入取得时间、冻结哈希与独立收讫；缺失或超时记明确失败/跳过，不重放补造。本次未触发日任务，未读取凭据、连接 broker 或调用浏览器，未开始正式观察。\n").encode()}
    for name, payload in texts.items():
        fd = os.open(directory/name, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream: stream.write(payload)
    manifest = {"kind": "CURRENT_READONLY_PREFLIGHT", "observed_at": report["observed_at"],
                "files": {name:"sha256:"+hashlib.sha256(payload).hexdigest() for name,payload in texts.items()},
                "broker_action_authorized": False, "natural_acceptance_promoted": False}
    fd = os.open(directory/"manifest.json", os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd,"w") as stream: stream.write(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir",type=Path,required=True)
    parser.add_argument("--decision-date",required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    try:
        report=collect_preflight(args.runtime_dir,decision_day=args.decision_date,as_of=datetime.now(timezone.utc),
                                 launch_dir=Path.home()/"Library/LaunchAgents",
                                 automation_path=Path.home()/".codex/automations/gold2-au-simnow/automation.toml")
        write_report(args.output_dir,report)
        print(json.dumps({"status":report["status"],"research_static_status":report["research_static_status"],
                          "simnow_observer_status":report["simnow_observer_status"],
                          "natural_acceptance":report["natural_acceptance"]["status"],
                          "output_dir":str(args.output_dir),"broker_action_authorized":False}))
        return 0
    except (OSError,ValueError,KeyError,TypeError):
        print(json.dumps({"status":"PREFLIGHT_FAILED_CLOSED","broker_action_authorized":False}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
