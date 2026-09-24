"""Read research status or compare two receipts without contacting providers."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from scripts import ymq_gold2_learning_live as learning
from scripts.ymq_gold2_live_shadow import default_runtime_dir


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def read_status(runtime_dir: Path) -> dict:
    latest = runtime_dir / "latest.json"
    if not latest.exists():
        return {"status": "NO_RECEIPT", "message": "尚无研究回执。可先用 compare 运行离线示例。"}
    receipt = read_object(latest)
    if receipt.get("status") == "LIVE_SHADOW_RECEIPT":
        learning.validate_live_receipt(receipt)
    result = {"status": receipt.get("status", "UNKNOWN"), "receipt": receipt}
    candidate_path = runtime_dir / "learning" / "latest-learning.json"
    if candidate_path.exists():
        try:
            candidate = read_object(candidate_path)
            sources = candidate.get("source_receipts")
            if not isinstance(sources, dict):
                raise ValueError("learning receipt has no source_receipts object")
            if sources.get("current_sha256") == learning.receipt_sha256(receipt):
                delta = candidate.get("delta")
                settlement = candidate.get("settlement")
                if not isinstance(delta, dict) or not isinstance(settlement, dict):
                    raise ValueError("learning receipt has no delta or settlement object")
                for name in ("gold_price_pct", "real_rate_bps", "usd_pct"):
                    value = delta.get(name)
                    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                        raise ValueError(f"invalid learning delta: {name}")
                if not all(isinstance(delta.get(name), str) for name in ("prior_as_of", "current_as_of")) or not isinstance(settlement.get("directional_claim_score"), str):
                    raise ValueError("learning receipt is missing period or scoring state")
                attention = delta.get("attention")
                if not isinstance(attention, list) or not all(isinstance(item, str) for item in attention):
                    raise ValueError("invalid learning attention list")
                result["learning"] = candidate
        except (OSError, ValueError) as exc:
            result["learning_error"] = str(exc)
    return result


def format_summary(result: dict) -> str:
    lines = [f"状态：{result['status']}"]
    if result.get("message"):
        lines.append(result["message"])
    receipt = result.get("receipt", {})
    if receipt:
        lines.extend([
            f"研究日期：{receipt.get('as_of', '未知')}",
            f"数据截止：{receipt.get('known_as_of_min', '未知')} — {receipt.get('known_as_of_max', '未知')}",
            f"研究判断：{receipt.get('research_state', '未知')} / 估值：{receipt.get('valuation_state', '未知')}",
        ])
        for name, metric in receipt.get("provider_receipts", {}).items():
            lines.append(f"  {name}：{metric['latest_value']}（{metric.get('latest_date', '未知')}）")
        if receipt.get("unknowns"):
            lines.append("缺失证据：" + "; ".join(receipt["unknowns"]))
        if receipt.get("error"):
            lines.append("错误：" + str(receipt["error"]))
    candidate = result.get("learning", result)
    if "delta" in candidate:
        delta = candidate["delta"]
        lines.extend([
            f"比较区间：{delta['prior_as_of']} → {delta['current_as_of']}",
            f"黄金变化：{delta['gold_price_pct']:+.3f}% · 实际利率：{delta['real_rate_bps']:+.2f}bp · 美元：{delta['usd_pct']:+.3f}%",
            "需关注：" + (", ".join(delta["attention"]) or "无阈值触发"),
            "方向检验：" + candidate["settlement"]["directional_claim_score"],
        ])
    elif receipt:
        lines.append("当次学习结果：尚无匹配回执")
    if result.get("learning_error"):
        lines.append("学习回执不可读：" + result["learning_error"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="原力投研：查看研究状态、比较每日变化（离线，只读）")
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="读取本地最新研究回执")
    status.add_argument("--runtime-dir", type=Path, default=default_runtime_dir())
    compare = commands.add_parser("compare", help="比较两个已有的成功回执，不写入运行目录")
    compare.add_argument("prior", type=Path)
    compare.add_argument("current", type=Path)
    for command in (status, compare):
        command.add_argument("--json", action="store_true", help="输出完整 JSON")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            result = read_status(args.runtime_dir)
        else:
            result = learning.build_learning_candidate(
                read_object(args.prior), read_object(args.current), learning.load_contract()
            )
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) if args.json else format_summary(result))
        return 0
    except (OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"无法读取研究结果：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
