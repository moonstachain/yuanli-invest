"""Read-only GOLD2 state projection from explicitly named evidence files.

Evidence timestamps and today's observation time are distinct. File mtime is
never a health timestamp, missing state is never FLAT, and this projection has
no authority to start services, change switches, write SQLite or submit orders.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Callable, Mapping
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
LABELS = ("com.yuanli.gold2-au-0805-shfe-archive", "com.yuanli.gold2-au-0810-macro-capture",
          "com.yuanli.gold2-au-0825-request-assembly", "com.yuanli.gold2-au-0830-research-decision")
SOURCE_NAMES = ("research", "connection", "execution_control", "account_coordinator", "reconciliation", "support_ticket")
TIMES = ("checked_at", "verified_at", "observed_at", "captured_at", "recorded_at", "updated_at", "submitted_at", "retrieved_at", "started_at")
CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
MAX_JSON = 20_000_000


def _instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("aware time required")
    return parsed.astimezone(timezone.utc)


def _code(value):
    return value if isinstance(value, str) and CODE.fullmatch(value) else "UNKNOWN"


def read_evidence(spec: Mapping | None, *, as_of: datetime) -> tuple[dict, dict | None]:
    unknown = {"current_status": "UNKNOWN", "evidence_status": "UNKNOWN", "evidence_time": None,
               "checked_at": as_of.isoformat(), "source_sha256": None, "source_hash_pinned": False}
    if not isinstance(spec, Mapping) or not isinstance(spec.get("path"), str) or not spec["path"]:
        return {**unknown, "reason": "EVIDENCE_PATH_NOT_CONFIGURED"}, None
    path = Path(spec["path"])
    descriptor = None
    try:
        if not path.is_absolute():
            raise ValueError
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or not 1 <= info.st_size <= MAX_JSON:
            raise ValueError
        raw = os.read(descriptor, MAX_JSON + 1)
        if len(raw) != info.st_size:
            raise ValueError
        digest = hashlib.sha256(raw).hexdigest()
        expected = spec.get("sha256")
        if expected is not None and (not isinstance(expected, str) or expected.removeprefix("sha256:") != digest):
            return {**unknown, "current_status": "INVALID", "reason": "EVIDENCE_HASH_MISMATCH"}, None
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError
                result[key] = value
            return result
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(value, dict):
            raise ValueError
        result = {**unknown, "source_sha256": "sha256:" + digest, "source_hash_pinned": expected is not None,
                  "evidence_status": _code(value.get("status")), "reason": _code(value.get("reason"))}
        instant = next((value[key] for key in TIMES if value.get(key) is not None), None)
        if instant is None:
            return {**result, "reason": "EVIDENCE_TIME_UNKNOWN"}, value
        when = _instant(instant)
        result["evidence_time"] = when.isoformat()
        age = (as_of - when).total_seconds()
        result["age_seconds"] = int(age)
        max_age = spec.get("max_age_seconds", 300)
        if type(max_age) is not int or not 0 <= max_age <= 604800:
            raise ValueError
        result["current_status"] = ("INVALID_FUTURE_EVIDENCE" if age < 0 else
                                    "FRESH_EVIDENCE" if age <= max_age else "STALE_AS_OF_EVIDENCE")
        result["is_today_in_shanghai"] = when.astimezone(SHANGHAI).date() == as_of.astimezone(SHANGHAI).date()
        return result, None if age < 0 else value
    except FileNotFoundError:
        return {**unknown, "current_status": "NOT_RUN", "reason": "EVIDENCE_FILE_MISSING"}, None
    except (OSError, ValueError, UnicodeError, RecursionError, OverflowError):
        return {**unknown, "current_status": "INVALID", "reason": "EVIDENCE_FILE_INVALID"}, None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def observe_launchd(label: str) -> dict:
    if label not in LABELS:
        raise ValueError("fixed launchd label required")
    try:
        result = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{label}"], capture_output=True,
                                text=True, timeout=3, check=False)
        if result.returncode != 0:
            return {"label": label, "installation": "NOT_LOADED", "state": "UNKNOWN", "runs": None}
        # Only fixed numeric/status fields are retained; raw launchctl output
        # can contain paths or environment values and must never be rendered.
        raw = result.stdout[:200000]
        state = re.search(r"(?m)^\s*state = ([a-z ]+)\s*$", raw)
        runs = re.search(r"(?m)^\s*runs = (\d+)\s*$", raw)
        exit_code = re.search(r"(?m)^\s*last exit code = (-?\d+)\s*$", raw)
        return {"label": label, "installation": "LOADED", "state": state.group(1).strip() if state else "UNKNOWN",
                "runs": int(runs.group(1)) if runs else None,
                "last_exit_code": int(exit_code.group(1)) if exit_code else None,
                "run_count_is_today_success": False}
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return {"label": label, "installation": "UNKNOWN", "state": "UNKNOWN", "runs": None}


def build_operations_status(config: Mapping, *, as_of: datetime,
                            launchd_observer: Callable = observe_launchd,
                            morning_acceptance: Mapping | None = None) -> dict:
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("aware observation required")
    now = as_of.astimezone(timezone.utc)
    if not isinstance(config, Mapping) or config.get("schema_version") != "gold-au-operations-status-config.v1":
        raise ValueError("explicit operations config required")
    sources = config.get("receipt_sources", {})
    if not isinstance(sources, dict) or set(sources) - set(SOURCE_NAMES):
        raise ValueError("named evidence only")
    evidence, values = {}, {}
    for name in SOURCE_NAMES:
        evidence[name], values[name] = read_evidence(sources.get(name), as_of=now)
    tasks = []
    for label in LABELS:
        observed = launchd_observer(label)
        tasks.append({"label": label, "installation": observed.get("installation") if observed.get("installation") in {"LOADED", "NOT_LOADED"} else "UNKNOWN",
                      "state": observed.get("state") if observed.get("state") in {"running", "not running", "waiting", "exited"} else "UNKNOWN",
                      "runs": observed.get("runs") if type(observed.get("runs")) is int and observed["runs"] >= 0 else None,
                      "last_exit_code": observed.get("last_exit_code") if type(observed.get("last_exit_code")) is int else None,
                      "checked_at": now.isoformat(), "run_count_is_today_success": False})
    morning = {"status": "UNKNOWN", "decision_date": now.astimezone(SHANGHAI).date().isoformat(),
               "actionable_entry": None, "reason": "NATURAL_MORNING_NOT_CHECKED", "external_time_anchor": "NOT_VERIFIED"}
    if isinstance(morning_acceptance, Mapping):
        day = morning_acceptance.get("decision_date")
        try:
            checked = _instant(morning_acceptance.get("checked_at"))
        except (ValueError, TypeError, AttributeError, OverflowError):
            checked = None
        if day == morning["decision_date"] and checked is not None and checked <= now:
            morning.update({"status": _code(morning_acceptance.get("status")),
                            "reason": _code(morning_acceptance.get("outcome_reason", morning_acceptance.get("reason"))),
                            "actionable_entry": morning_acceptance.get("actionable_entry") if type(morning_acceptance.get("actionable_entry")) is bool else None,
                            "external_time_anchor": _code(morning_acceptance.get("external_time_anchor"))})
    research = values["research"] or {}
    price, risk = research.get("price_observation", {}), research.get("risk_policy_observation", {})
    research_details = {}
    if isinstance(price, dict):
        for key in ("atr20_cny_per_gram", "one_lot_2atr_price_risk_cny_excluding_unknown_execution_costs"):
            value = price.get(key)
            if type(value) in {int, float} and math.isfinite(value) and value >= 0:
                research_details[key] = value
        if isinstance(price.get("contract"), str) and re.fullmatch(r"au\d{4}", price["contract"]):
            research_details["contract"] = price["contract"]
        research_details["close_above_prior_20_close_high"] = price.get("close_above_prior_20_close_high") if type(price.get("close_above_prior_20_close_high")) is bool else None
    if isinstance(risk, dict):
        budget = risk.get("indicative_frozen_policy_budget_cny")
        if type(budget) in {int, float} and math.isfinite(budget) and budget >= 0:
            research_details["indicative_frozen_policy_budget_cny"] = budget
        research_details["wgc_status"] = _code(risk.get("wgc_status"))
    macro = research.get("macro_observation", {})
    if isinstance(macro, dict):
        research_details["macro_reason"] = _code(macro.get("reason"))
    control = values["execution_control"] or {}
    switches = {key: control.get(key) if type(control.get(key)) is bool else None
                for key in ("service_enabled", "claim_enabled", "production_started", "paper_grant_verified")}
    switches["current_authority"] = "NOT_ESTABLISHED_BY_STATUS_CARD"
    coordinator = values["account_coordinator"] or {}
    account = {"phase": _code(coordinator.get("phase")), "position_quantity": None,
               "pending_command": "UNKNOWN", "reconciliation_status": "UNKNOWN"}
    if type(coordinator.get("position_quantity")) is int and coordinator["position_quantity"] in {0, 1}:
        account["position_quantity"] = coordinator["position_quantity"]
    if "pending_claim_id" in coordinator:
        account["pending_command"] = "NONE_AS_OF_RECEIPT" if coordinator["pending_claim_id"] is None else "PRESENT_AS_OF_RECEIPT"
    reconciliation = values["reconciliation"] or {}
    account["reconciliation_status"] = _code(reconciliation.get("status"))
    ticket = values["support_ticket"] or {}
    ticket_details = {"ticket_id": 5163, "url": "https://www.youquant.com/m/ticket-topic/5163",
                      "status_as_of_evidence": _code(ticket.get("status")) if ticket.get("ticket_id") == 5163 else "UNKNOWN"}
    connection = values["connection"] or {}
    connection_verified = connection.get("account_readback_verified") is True and connection.get("identity_attestation_verified") is True
    account["position_basis"] = "COORDINATOR_EXPECTED_STATE_NOT_BROKER_READBACK"
    account["broker_position_quantity"] = (connection["position_quantity"] if connection_verified
        and type(connection.get("position_quantity")) is int and connection["position_quantity"] in {0, 1} else None)
    warnings = []
    if not any(row["runs"] for row in tasks):
        warnings.append("NO_SCHEDULED_RUN_COUNT_OBSERVED")
    if evidence["connection"]["current_status"] != "FRESH_EVIDENCE" or not connection_verified:
        warnings.append("CURRENT_SIMNOW_CONNECTION_NOT_VERIFIED")
    if account["position_quantity"] is None:
        warnings.append("UNKNOWN_POSITION_IS_NOT_FLAT")
    if account["broker_position_quantity"] is None:
        warnings.append("UNKNOWN_BROKER_POSITION_IS_NOT_FLAT")
    if any(value is not True for key, value in switches.items() if key != "current_authority"):
        warnings.append("FORMAL_EXECUTION_ADMISSION_NOT_PROVEN")
    return {"schema_version": "gold-au-operations-status.v1", "observed_at": now.isoformat(),
            "today_shanghai": now.astimezone(SHANGHAI).date().isoformat(), "read_only": True,
            "broker_action_authorized": False, "health": "EVIDENCE_REVIEW_REQUIRED",
            "tasks": tasks, "natural_morning": morning, "evidence": evidence,
            "research_details_as_of_evidence": research_details, "execution_switches_as_of_evidence": switches,
            "account_as_of_evidence": account, "support_ticket": ticket_details,
            "simnow_readback_verified_as_of_evidence": connection_verified,
            "warnings": warnings, "raw_evidence_rendered": False}


def render_html(result: Mapping) -> str:
    """Standalone, escaped, script-free page; JSON is a separate machine file."""
    human = {"UNKNOWN": "未知，尚未核验", "NOT_VERIFIED": "尚未核验",
             "OFFICIAL_NON_SESSION_DAY": "今日非上期所交易日", "RESEARCH_FREEZE_NOT_SCHEDULED": "今日无需晨间冻结",
             "FRESH_EVIDENCE": "回执在规定有效期内", "STALE_AS_OF_EVIDENCE": "历史回执，已超有效期",
             "READY_RESEARCH_OBSERVATION": "已取得研究观察，尚未形成事前交易指令",
             "SERVICE_DISABLED": "执行服务已关闭", "WAITING_ACCEPTANCE": "工单等待受理",
             "REPLIED_AWAITING_CLARIFICATION": "客服已回复，原生版本问题仍待澄清",
             "NOT_RUN": "尚未运行", "LOADED": "已安装", "ACCEPTED_RESEARCH_FREEZE": "自然研究截面已验收",
             "RECORDED_EXPLICIT_SKIP": "已记录明确跳过", "MISSING_NATURAL_DECISION": "缺少自然08:30截面",
             "NO_SCHEDULED_RUN_COUNT_OBSERVED": "尚未观察到定时任务实际运行",
             "CURRENT_SIMNOW_CONNECTION_NOT_VERIFIED": "尚未核验当前SimNow连接",
             "UNKNOWN_POSITION_IS_NOT_FLAT": "策略预期仓位未知",
             "UNKNOWN_BROKER_POSITION_IS_NOT_FLAT": "交易端实际仓位未知，不能视为空仓",
             "FORMAL_EXECUTION_ADMISSION_NOT_PROVEN": "正式模拟执行尚未通过准入"}
    def esc(value):
        rendered = "未知" if value is None else str(value)
        return html.escape(human.get(rendered, rendered), quote=True)
    labels = {"research": "研究证据", "connection": "SimNow连接", "execution_control": "执行开关",
              "account_coordinator": "仓位与未决指令", "reconciliation": "四方对账", "support_ticket": "工单5163"}
    rows = "".join(f"<tr><th>{esc(labels[name])}</th><td>{esc(value['current_status'])}</td><td>{esc(value['evidence_status'])}</td><td>{esc(value['evidence_time'])}</td></tr>"
                   for name, value in result["evidence"].items())
    task_rows = "".join(f"<tr><td>{esc(row['label'].split('gold2-au-')[-1])}</td><td>{esc(row['installation'])}</td><td>{esc(row['runs'])}</td><td>{esc(row['last_exit_code'])}</td></tr>"
                        for row in result["tasks"])
    details = "".join(f"<dt>{esc(key)}</dt><dd>{esc(value)}</dd>" for key, value in result["research_details_as_of_evidence"].items())
    warnings = "".join(f"<li>{esc(value)}</li>" for value in result["warnings"])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>GOLD2 只读运营状态</title><style>body{{font:16px system-ui;margin:0;background:#f5f5f1;color:#172523}}main{{max-width:1100px;margin:32px auto;padding:24px}}h1{{font-size:28px}}section{{background:white;border:1px solid #d8dfda;padding:20px;margin:18px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border-bottom:1px solid #e2e7e3;text-align:left;padding:10px;overflow-wrap:anywhere}}dt{{font-size:13px;color:#56635b}}dd{{margin:0 0 12px}}small{{color:#52615a}}.warning{{border-left:5px solid #a76515}}a{{color:#156651}}@media(max-width:700px){{main{{padding:12px}}table{{font-size:11px}}}}</style>
<main><h1>GOLD2 只读运营状态</h1><p>观察时间：{esc(result['observed_at'])} · 北京日期：{esc(result['today_shanghai'])}</p>
<p>本页仅展示已有证据。未知仓位不能视为空仓；旧回执不能证明当前连接正常。刷新需重新运行生成器。</p>
<section><h2>今日自然08:30</h2><p>{esc(result['natural_morning']['status'])} · {esc(result['natural_morning']['reason'])}</p><small>独立时间锚：{esc(result['natural_morning']['external_time_anchor'])}</small></section>
<section><h2>证据与时效</h2><table><thead><tr><th>环节</th><th>当前可判定性</th><th>回执中的状态</th><th>证据时间</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>晨间任务</h2><table><thead><tr><th>任务</th><th>已加载</th><th>累计运行次数</th><th>最近退出码</th></tr></thead><tbody>{task_rows}</tbody></table><small>累计次数和退出码不等于今日08:30验收。</small></section>
<section><h2>研究观察截面</h2><dl>{details or '<dd>没有可展示的研究证据</dd>'}</dl></section>
<section><h2>仓位、指令与执行开关</h2><p>策略账预期仓位：{esc(result['account_as_of_evidence']['position_quantity'])} 手；交易端核验仓位：{esc(result['account_as_of_evidence']['broker_position_quantity'])} 手；状态：{esc(result['account_as_of_evidence']['phase'])}；未决：{esc(result['account_as_of_evidence']['pending_command'])}；对账：{esc(result['account_as_of_evidence']['reconciliation_status'])}</p>
<p>服务：{esc(result['execution_switches_as_of_evidence']['service_enabled'])}；认领：{esc(result['execution_switches_as_of_evidence']['claim_enabled'])}；正式运行：{esc(result['execution_switches_as_of_evidence']['production_started'])}</p><small>以上均以对应回执时间为准，本页面不授予交易权限。</small></section>
<section class="warning"><h2>需要处理</h2><ul>{warnings}</ul><p><a href="https://www.youquant.com/m/ticket-topic/5163" target="_blank" rel="noopener noreferrer">优宽工单5163</a>：{esc(result['support_ticket']['status_as_of_evidence'])}</p></section></main></html>'''
