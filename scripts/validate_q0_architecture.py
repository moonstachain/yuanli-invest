#!/usr/bin/env python3
"""Fail-closed checks for Q0 architecture freeze candidate.

This validator checks only architecture-package invariants. It does not authorize
implementation, research admission, operational-canon activation or production.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q0 = ROOT / "docs" / "architecture" / "q0"
UNIVERSE = Q0 / "mvp-universe-30-v1.json"
STATE = Q0 / "Q0-STATE.json"
SCHEMAS = [
    Q0 / "contracts" / "force-radar-snapshot.schema.json",
    Q0 / "contracts" / "agent-run-artifact.schema.json",
]
REQUIRED_FILES = [
    ROOT / "docs" / "architecture" / "YUANLI-QUANT-AI-EQUITY-RESEARCH-SYSTEM-v1.md",
    Q0 / "repository-layout-v1.md",
    Q0 / "duckdb-logical-schema-v1.sql",
    Q0 / "agent-contracts-v1.md",
    Q0 / "mcp-tool-contract-v1.md",
    UNIVERSE,
    Q0 / "replay-eval-contract-v1.md",
    Q0 / "ci-human-gate-v1.md",
    Q0 / "Q0-HUMAN-REVIEW-CARD-v1.md",
    Q0 / "90-day-implementation-plan-v1.md",
    Q0 / "CODEX-TASK-SPEC-v1.md",
    STATE,
    *SCHEMAS,
]

BANNED_KEYS = {
    "target_price",
    "position_size",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "expected_return",
    "force_score",
    "pnx_score",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def walk_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from walk_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_keys(item)


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    assert not missing, f"missing Q0 deliverables: {missing}"

    for schema_path in SCHEMAS:
        schema = load_json(schema_path)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert schema.get("type") == "object"

    radar_schema = load_json(SCHEMAS[0])
    assert "scalar_score_prohibited" in radar_schema.get("required", []), (
        "Force Radar schema must require scalar_score_prohibited"
    )
    assert radar_schema["properties"]["scalar_score_prohibited"] == {"const": True}

    universe = load_json(UNIVERSE)
    assert universe["status"] == "candidate_seed_universe_not_investment_recommendation"
    assets = universe["assets"]
    assert len(assets) == 30, f"expected 30 seed assets, got {len(assets)}"

    asset_ids = [a["asset_id"] for a in assets]
    assert len(asset_ids) == len(set(asset_ids)), "duplicate asset_id"

    tickers = [(a["market"], a["exchange"], a["ticker"]) for a in assets]
    assert len(tickers) == len(set(tickers)), "duplicate market/exchange/ticker seed"

    assert all(a.get("initial_force_state") == "unknown" for a in assets), (
        "Q0 seed universe must not preload Force conclusions"
    )
    assert all(a.get("primary_nodes") for a in assets), "every seed asset needs value-chain coverage"

    banned_found = sorted(BANNED_KEYS.intersection(set(walk_keys(universe))))
    assert not banned_found, f"prohibited investment-action keys found: {banned_found}"

    state = load_json(STATE)
    assert state["stage"] == "Q0_ARCHITECTURE_FREEZE"
    assert state["status"] == "candidate_ready_for_human_review"
    assert state["implementation_authorization"] == "blocked_pending_hg_q0"
    assert state["authority"]["quant_workspace"] == "current_a9_operational_canon"
    assert state["authority"]["yuanli_invest"] == "target_business_canon_not_operational"
    assert state["rsi_frozen_change"] == "not_run_not_authorized"
    assert state["live_trading"] == "unavailable_by_design"
    assert state["deliverables"]["human_review_card"] == "complete"

    print("Q0 architecture validation: PASS")


if __name__ == "__main__":
    main()
