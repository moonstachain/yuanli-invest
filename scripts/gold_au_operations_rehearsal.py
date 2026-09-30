#!/usr/bin/env python3
"""Offline REHEARSAL of public research -> non-trading signal -> local receipt.

No fake 08:30, replayed publication, broker callback, remote receipt service or
runtime mutation is used. The CLI uses the real process clock and only existing
explicit public evidence paths. Natural morning acceptance is read-only.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from scripts.gold_au_research_diagnostic import accept_natural_morning
from yuanli_invest.gold_au_official_calendar import load_calendar_receipt
from yuanli_invest.gold_au_operations_status import LABELS, SHANGHAI, observe_launchd
from yuanli_invest.gold_au_research_diagnostic import observe_public_evidence
from yuanli_invest.gold_au_strategy import DEFAULT_CONFIG
from yuanli_invest.receipts import canonical_hash

EXPECTED = {
    LABELS[0]: (8, 5, "gold_au_shfe_archive_worker.py"),
    LABELS[1]: (8, 10, "gold_macro_daily_worker.py"),
    LABELS[2]: (8, 25, "gold_au_daily_request.py"),
    LABELS[3]: (8, 30, "gold_au_decision_worker.py"),
}
CASE_CONDITIONS = {
    "natural0830": ["官方交易日真实08:30自然触发", "四输入真实取得时间不晚于决策", "不可回放补造", "完整冻结回执与独立时间锚"],
    "readonly_connection": ["SimNow第一套正常环境", "真实账户/仓位/委托/行情读回", "空返回保留UNKNOWN", "来源时间与绑定身份一致"],
    "native_python312": ["优宽原生策略解释器>=3.12", "同一进程原生API可调用", "子进程核心测试不替代原生验收"],
    "identity_and_cost": ["专属账户/机器人/真实au合约绑定", "真实费用上界与保证金", "5跳双边费用风险复算<=5000且不超现有预算", "PaperGrant完整但不由演练生成"],
    "independent_four_way": ["交易端/执行/不可变账/预期四方独立证据", "仓位与成交数量精确一致", "现金/可用/冻结保证金误差最多1分", "不能复制一方充作四方"],
    "linked_protective_exit": ["已证实开仓来源与native终态", "V3 linkedclose验证", "无未决仓位绕过账户锁", "120秒到时仅减仓", "保护退出阻断须显式记录且不冒充已保护"],
    "engineering_round_trip": ["ENGINEERING_ONLY一次最多一手多头开平", "止损距离<=4元/克", "最长120秒禁止过夜", "实际成交与费用可核对", "不计正式策略样本"],
    "daily_settlement": ["SimNow原生日结归档", "今昨仓/成交/费用/资金核对", "基准价更新不双计", "次日原生读回相符"],
    "expert_review_1": ["蒙熊本人独立机制/指标/反例/停止条件判断", "不能由机器代签", "记录原始意见与查看证据截面"],
    "expert_review_2": ["蒙熊/RAY/机器同一冻结证据独立提交", "先提交再揭盲", "分歧与失败意见保留"],
}


def read_json(path: Path) -> dict:
    if not path.is_absolute() or path.is_symlink() or not path.is_file() or path.stat().st_size > 20_000_000:
        raise ValueError("EXPLICIT_BOUNDED_UNLINKED_JSON_REQUIRED")
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return value


def audit_tasks(runtime: Path, *, as_of: datetime, launch_dir: Path,
                observer: Callable = observe_launchd) -> list[dict]:
    result = []
    for label, (hour, minute, script) in EXPECTED.items():
        row = {"label": label, "checked_at": as_of.isoformat(), "config_status": "UNKNOWN",
               "installation": "UNKNOWN", "runs": None, "last_exit_code": None,
               "natural_morning_success": "NOT_ESTABLISHED_BY_CONFIGURATION_OR_RUN_COUNT"}
        path = launch_dir / (label + ".plist")
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 100000:
                raise ValueError
            raw = path.read_bytes(); config = plistlib.loads(raw)
            expected_schedule = [{"Hour": hour, "Minute": minute, "Weekday": weekday} for weekday in range(1, 6)]
            args = config.get("ProgramArguments")
            valid_args = (isinstance(args, list) and len(args) == 5 and all(isinstance(value, str) for value in args)
                          and Path(args[0]).is_file() and Path(args[1]).name == script
                          and Path(args[1]).is_file() and args[2:] == ["--runtime-dir", str(runtime), "--execute"])
            correct = (config.get("Label") == label and config.get("RunAtLoad") is False
                       and config.get("KeepAlive") in {None, False} and config.get("StartCalendarInterval") == expected_schedule
                       and valid_args)
            row.update({"config_status": "MATCHES_FROZEN_WEEKDAY_SCHEDULE" if correct else "CONFIG_MISMATCH",
                        "plist_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
                        "schedule_shanghai": f"WEEKDAY_1_TO_5_{hour:02d}:{minute:02d}",
                        "run_at_load": config.get("RunAtLoad") is True, "program_args_match": bool(valid_args)})
        except (OSError, ValueError, TypeError, plistlib.InvalidFileException):
            row["config_status"] = "MISSING_OR_INVALID"
        loaded = observer(label)
        row["installation"] = loaded.get("installation") if loaded.get("installation") in {"LOADED", "NOT_LOADED"} else "UNKNOWN"
        row["runs"] = loaded.get("runs") if type(loaded.get("runs")) is int and loaded["runs"] >= 0 else None
        row["last_exit_code"] = loaded.get("last_exit_code") if type(loaded.get("last_exit_code")) is int else None
        result.append(row)
    return result


def local_receipt(signal: dict, research: dict, *, now: datetime) -> dict:
    material = {"schema_version": "gold-au-local-rehearsal-receipt.v1", "status": "LOCAL_REHEARSAL_HASH_RECEIPT",
                "purpose": "REHEARSAL_ONLY", "received_at": now.isoformat(),
                "research_sha256": canonical_hash(research), "signal_sha256": canonical_hash(signal),
                "independent_time_authority": False, "broker_action_authorized": False,
                "natural_decision_frozen": False, "engineering_order_count": 0, "formal_order_count": 0}
    return {**material, "receipt_sha256": canonical_hash(material)}


def verify_local_receipt(receipt: dict, signal: dict, research: dict) -> bool:
    expected = local_receipt(signal, research, now=datetime.fromisoformat(receipt["received_at"]))
    if receipt != expected or signal.get("purpose") != "REHEARSAL_ONLY" or signal.get("broker_order_authorized") is not False:
        raise ValueError("LOCAL_REHEARSAL_RECEIPT_MISMATCH")
    return True


def research_to_rehearsal_signal(research: dict, *, now: datetime) -> dict:
    if (research.get("status") != "READY_RESEARCH_OBSERVATION" or research.get("broker_action_authorized") is not False
            or research.get("decision_frozen") is not False):
        raise ValueError("NONTRADING_RESEARCH_OBSERVATION_REQUIRED")
    price, macro, risk = (research["price_observation"], research["macro_observation"], research["risk_policy_observation"])
    breakout = price.get("close_above_prior_20_close_high") is True
    macro_pass = macro.get("pass") is True
    return {"schema_version": "gold-au-rehearsal-research-signal.v1", "purpose": "REHEARSAL_ONLY",
            "observed_at": now.isoformat(), "clock_basis": "ACTUAL_PROCESS_CLOCK_NOT_0830_DECISION",
            "eligibility_reference_session": price["eligibility_reference_session"],
            "last_completed_session": price["last_completed_session"], "contract_reference": price["contract"],
            "breakout": breakout, "macro_filter_pass": macro_pass, "macro_reason": macro.get("reason"),
            "research_conditions_met": breakout and macro_pass,
            "research_reason": "NO_BREAKOUT" if not breakout else "MACRO_FILTER_REJECTED" if not macro_pass else "RESEARCH_CANDIDATE_ONLY",
            "stop_only_one_lot_loss_cny": price["one_lot_2atr_price_risk_cny_excluding_unknown_execution_costs"],
            "indicative_strategy_budget_cny": risk["indicative_frozen_policy_budget_cny"],
            "execution_cost_status": "UNKNOWN", "margin_status": "UNKNOWN", "wgc_status": risk["wgc_status"],
            "actionable_entry": False, "action_block": "REHEARSAL_NO_0830_FREEZE_NO_ACCOUNT_ADMISSION",
            "broker_order_authorized": False, "independent_time_anchor": "NOT_VERIFIED",
            "frozen_parameters_sha256": canonical_hash(DEFAULT_CONFIG), "research_sha256": canonical_hash(research)}


def engineering_test_contract(*, signal: dict, now: datetime) -> dict:
    material = {"schema_version": "gold-au-engineering-test-contract-candidate.v1", "purpose": "ENGINEERING_ONLY",
                "created_at": now.isoformat(), "status": "PENDING_NATIVE_ADMISSION_NOT_AN_ORDER",
                "environment": "SIMNOW_FIRST_NORMAL", "account_id": "UNKNOWN_PENDING_PRIVATE_ATTESTATION",
                "robot_id": None, "grant": "NOT_CREATED", "contract_reference": signal["contract_reference"],
                "actual_contract_requires_current_metadata_oi_check": True, "action_sequence": ["OPEN_LONG", "CLOSE_LONG"],
                "maximum_quantity_lots": 1, "maximum_round_trips": 1, "paper_strategy_equity_cny": "5000000",
                "session": "LIQUID_SHFE_DAY_SESSION_OFFICIAL_SESSION_CONFIRMED",
                "risk": {"maximum_planned_loss_cny": "5000", "must_not_exceed_existing_strategy_budget": True,
                         "maximum_stop_distance_cny_per_gram": "4", "maximum_margin_fraction": "0.30",
                         "fees": "ACTUAL_WITNESSED_ROUND_TRIP_UPPER_REQUIRED", "slippage_ticks_per_side": 5,
                         "tick_cny_per_gram": "0.02", "multiplier_grams_per_lot": 1000,
                         "budget_formula": "stop_distance*1000+2*5*0.02*1000+actual_round_trip_fee_upper<=min(5000,strategy_budget)",
                         "native_quote_margin_fee_status": "UNKNOWN"},
                "maximum_hold_seconds": 120, "timeout_action": "ONLY_REDUCE_WITH_VERIFIED_LINKED_CLOSE",
                "overnight_allowed": False, "repeat_test_allowed": False, "unknown_fill_action": "FREEZE_READBACK_NO_RESUBMIT",
                "close_requires": ["VERIFIED_NATIVE_TERMINAL_READBACK", "V3_LINKED_CLOSE_ORIGIN", "FOUR_WAY_RECONCILIATION", "NATIVE_SETTLEMENT_ARCHIVE"],
                "broker_action_authorized": False, "counts_as_strategy_return_sample": False,
                "starts_formal_30_day_clock": False, "frozen_formal_2atr_rule_changed": False,
                "source_rehearsal_signal_sha256": canonical_hash(signal)}
    return {**material, "contract_sha256": canonical_hash(material)}


def perform_rehearsal(request_path: Path, runtime: Path, *, now: datetime,
                      launch_dir: Path, observer: Callable = observe_launchd,
                      research_observer: Callable = observe_public_evidence) -> dict:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("AWARE_ACTUAL_CLOCK_REQUIRED")
    request = read_json(request_path)
    before = hashlib.sha256(request_path.read_bytes()).hexdigest()
    research = research_observer(request, as_of=now)
    if hashlib.sha256(request_path.read_bytes()).hexdigest() != before:
        raise ValueError("REHEARSAL_REQUEST_CHANGED")
    calendar = load_calendar_receipt(Path(request["calendar_receipt_path"]), as_of=now)
    today = now.astimezone(SHANGHAI).date().isoformat()
    sessions = calendar["sessions"]
    next_session = next((day for day in sessions if day >= today), None)
    last_session = next((day for day in reversed(sessions) if day < today), None)
    target = next_session or today
    natural = accept_natural_morning(runtime, decision_date=target, as_of=now)
    tasks = audit_tasks(runtime, as_of=now, launch_dir=launch_dir, observer=observer)
    base = {"schema_version": "gold-au-offline-operations-rehearsal.v1", "purpose": "REHEARSAL_ONLY", "kind": "REHEARSAL",
            "observed_at": now.isoformat(), "clock_changed": False, "network_calls": 0, "broker_calls": 0,
            "original_runtime_modified": False, "natural_0830_not_manufactured": True,
            "engineering_orders": 0, "formal_orders": 0, "observation_30_days_started": False,
            "request_sha256": "sha256:" + before, "tasks": tasks, "natural_morning_acceptance": natural,
            "calendar_status": "OFFICIAL_NON_SESSION_DAY" if today not in sessions else "OFFICIAL_SESSION_DAY",
            "last_completed_session": last_session, "next_official_session": next_session,
            "research": research, "broker_action_authorized": False}
    if research.get("status") != "READY_RESEARCH_OBSERVATION":
        return {**base, "status": "REHEARSAL_BLOCKED_PUBLIC_RESEARCH", "reason": research.get("reason", "UNKNOWN")}
    signal = research_to_rehearsal_signal(research, now=now)
    receipt = local_receipt(signal, research, now=now)
    verify_local_receipt(receipt, signal, research)
    hashes = {"research": canonical_hash(research), "signal": canonical_hash(signal), "receipt": canonical_hash(receipt)}
    chain, previous = [], "sha256:" + "0" * 64
    for index, name in enumerate(("research", "signal", "receipt"), 1):
        stage = {"sequence": index, "purpose": "REHEARSAL_ONLY", "stage": name, "at": now.isoformat(),
                 "payload_sha256": hashes[name], "previous_hash": previous}
        stage["stage_sha256"] = canonical_hash(stage)
        chain.append(stage); previous = stage["stage_sha256"]
    return {**base, "status": "REHEARSAL_LOCAL_PIPELINE_VERIFIED_NOT_NATURAL_NOT_SIMNOW", "signal": signal,
            "receipt": receipt, "receipt_verification": "VERIFIED_LOCAL_REHEARSAL_INTEGRITY_ONLY",
            "stage_chain": chain, "stage_chain_root_sha256": previous,
            "engineering_test_contract": engineering_test_contract(signal=signal, now=now),
            "data_freshness": {"shfe_last_completed_matches_official_calendar": signal["last_completed_session"] == last_session,
                               "macro": "AS_OF_EXISTING_CAPTURE_NOT_RECHECKED_AGAINST_LATEST_RELEASE",
                               "wgc": "UNKNOWN", "account_fee_margin": "UNKNOWN"}}


def verify_rehearsal(result: dict) -> bool:
    if result.get("purpose") != "REHEARSAL_ONLY" or result.get("broker_action_authorized") is not False:
        raise ValueError("REHEARSAL_AUTHORITY_MISMATCH")
    verify_local_receipt(result["receipt"], result["signal"], result["research"])
    contract = result["engineering_test_contract"]
    material = {key: value for key, value in contract.items() if key != "contract_sha256"}
    if (contract.get("contract_sha256") != canonical_hash(material)
            or contract.get("source_rehearsal_signal_sha256") != canonical_hash(result["signal"])
            or contract.get("maximum_quantity_lots") != 1 or contract.get("maximum_hold_seconds") != 120
            or contract.get("broker_action_authorized") is not False
            or contract.get("risk", {}).get("maximum_planned_loss_cny") != "5000"
            or contract.get("risk", {}).get("maximum_stop_distance_cny_per_gram") != "4"):
        raise ValueError("ENGINEERING_CONTRACT_MISMATCH")
    previous = "sha256:" + "0" * 64
    for index, event in enumerate(result["stage_chain"], 1):
        if (event["sequence"] != index or event["previous_hash"] != previous
                or event["payload_sha256"] != canonical_hash(result[event["stage"]])
                or event["stage_sha256"] != canonical_hash({k:v for k,v in event.items() if k != "stage_sha256"})):
            raise ValueError("REHEARSAL_CHAIN_MISMATCH")
        previous = event["stage_sha256"]
    if len(result["stage_chain"]) != 3 or previous != result["stage_chain_root_sha256"]:
        raise ValueError("REHEARSAL_ROOT_MISMATCH")
    return True


def engineering_acceptance_matrix(result: dict, *, rehearsal_file_sha256: str) -> dict:
    """An unfilled real-evidence matrix; rehearsal never upgrades actual status."""
    items = []
    for case_id, conditions in CASE_CONDITIONS.items():
        items.append({"case_id": case_id, "kind": "ACTUAL_REQUIRED", "status": "PENDING" if case_id == "natural0830" else "NOT_RUN",
                      "evidence_ref": None, "evidence_sha256": None, "evidence_observed_at": None,
                      "identity": {"environment": "SIMNOW_FIRST_NORMAL", "account_id": None, "robot_id": None, "contract": None},
                      "success_conditions": conditions,
                      "offline_evidence": {"kind": "REHEARSAL", "status": "DOES_NOT_ESTABLISH_ACTUAL_PASS",
                                           "ref": "rehearsal-result.json", "sha256": rehearsal_file_sha256,
                                           "observed_at": result["observed_at"]}})
    concurrency = []
    for case_id, condition in (("duplicate_command", "同command同body重复无第二单"),
                               ("conflicting_command", "同command不同body拒绝且不改原判"),
                               ("account_mutual_exclusion", "多机器人同账户仅一份有效pending"),
                               ("unknown_submit_restart", "未知提交/重启只读核对不重发"),
                               ("partial_fill_rejected_cancel", "部分成交/拒单/撤单均按原生终态处理"),
                               ("disconnect_expiry", "断线/超时/失效不续签不补单")):
        concurrency.append({"case_id": case_id, "kind": "ACTUAL_REQUIRED", "status": "NOT_RUN",
                            "evidence_ref": None, "evidence_sha256": None, "evidence_observed_at": None,
                            "success_condition": condition})
    return {"schema_version": "gold-au-engineering-acceptance-matrix.v1", "observed_at": result["observed_at"],
            "purpose": "ENGINEERING_ONLY_PREPARED_ACCEPTANCE_NOT_EXECUTED", "broker_action_authorized": False,
            "formal_30_day_start_allowed": False, "required_engineering_contract_sha256": result["engineering_test_contract"]["contract_sha256"],
            "items": items, "concurrency_cases": concurrency,
            "actual_pass_count": 0, "unknown_is_failure_to_establish_pass": True,
            "rehearsal_may_fill_actual_status": False}


def write_new_result(output: Path, result: dict) -> None:
    if not output.is_absolute() or output.exists() or not output.parent.is_dir() or output.parent.is_symlink():
        raise ValueError("NEW_PRIVATE_OUTPUT_REQUIRED")
    output.mkdir(mode=0o700)
    documents = {"rehearsal-result.json": result}
    if "engineering_test_contract" in result:
        documents["ENGINEERING-ONLY-contract.json"] = result["engineering_test_contract"]
    for name, value in documents.items():
        fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2); stream.write("\n")
    if "engineering_test_contract" in result:
        rehearsal_hash = "sha256:" + hashlib.sha256((output / "rehearsal-result.json").read_bytes()).hexdigest()
        matrix = engineering_acceptance_matrix(result, rehearsal_file_sha256=rehearsal_hash)
        fd = os.open(output / "ENGINEERING-acceptance-matrix.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(matrix, stream, ensure_ascii=False, sort_keys=True, indent=2); stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    try:
        if args.verify is not None:
            if any(value is not None for value in (args.request, args.runtime_dir, args.output_dir)):
                raise ValueError("VERIFY_IS_READ_ONLY")
            verify_rehearsal(read_json(args.verify))
            print(json.dumps({"status": "VERIFIED_LOCAL_REHEARSAL_INTEGRITY_ONLY", "broker_action_authorized": False}))
            return 0
        if any(value is None for value in (args.request, args.runtime_dir, args.output_dir)):
            raise ValueError("EXPLICIT_REHEARSAL_INPUT_OUTPUT_REQUIRED")
        result = perform_rehearsal(args.request, args.runtime_dir, now=datetime.now(timezone.utc),
                                   launch_dir=Path.home() / "Library" / "LaunchAgents")
        if "receipt" in result:
            verify_rehearsal(result)
        write_new_result(args.output_dir, result)
        print(json.dumps({"status": result["status"], "broker_action_authorized": False, "output_dir": str(args.output_dir)}))
        return 0 if "receipt" in result else 2
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"status": "REHEARSAL_DENIED", "reason": "EXPLICIT_PUBLIC_EVIDENCE_OR_OUTPUT_INVALID", "broker_action_authorized": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
