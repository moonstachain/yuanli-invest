#!/usr/bin/env python3
"""Offline AU candidate sensitivity report. It cannot send broker commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
if sys.version_info < (3, 12):
    raise SystemExit("gold_au_backtest requires Python >= 3.12, as specified by pyproject.toml")

from yuanli_invest.gold_au_strategy import GoldAuDataset, run_backtest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON dataset; dated AU rows and versioned observations")
    parser.add_argument("--config", type=Path, default=ROOT / "config/ymq_gold2/gold_au_strategy.v1.json")
    parser.add_argument("--output", type=Path, help="Optional report path; otherwise stdout")
    parser.add_argument("--pit-mode", choices=("strict", "reconstructed"), default="reconstructed")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    dataset = GoldAuDataset(payload)
    runs = []
    audit_run = None
    for variant in ("price_only", "real_rate_only", "usd_only", "full"):
        for ticks in config["slippage_ticks_per_side"]:
            run = run_backtest(dataset, variant=variant, slippage_ticks=ticks,
                               pit_mode=args.pit_mode, config=config)
            if variant == "full" and ticks == config["slippage_ticks_per_side"][0]:
                audit_run = run
            runs.append({key: value for key, value in run.items()
                         if key not in {"decisions", "events", "trades", "equity_curve",
                                        "macro_filtered_opportunities"}})
    for breakout in config["sensitivity_breakout_lookbacks"]:
        for macro in config["sensitivity_macro_observations"]:
            if (breakout, macro) == (config["breakout_lookback"], config["macro_observations"]):
                continue
            for ticks in config["slippage_ticks_per_side"]:
                run = run_backtest(dataset, variant="full", breakout_lookback=breakout,
                                   macro_lookback=macro, slippage_ticks=ticks,
                                   pit_mode=args.pit_mode, config=config)
                runs.append({key: value for key, value in run.items()
                             if key not in {"decisions", "events", "trades", "equity_curve",
                                            "macro_filtered_opportunities"}})
    report = {"schema_version": "gold-au-sensitivity.v1", "input": str(args.input),
              "purpose": "EXPLORATORY_BACKTEST_NOT_PROOF_OF_TRADING_EDGE",
              "pit_mode": args.pit_mode, "runs": runs, "audit_run": audit_run}
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)


if __name__ == "__main__":
    main()
