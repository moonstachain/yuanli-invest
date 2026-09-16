#!/usr/bin/env python3
"""YMQ-GOLD2 G4 fail-closed historical Gold replay harness.

The harness uses only the already-governed four-factor PIT panel. It therefore
must leave expectation, official-demand, positioning and multi-lens valuation
states indeterminate when those evidence domains are absent.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from typing import Any

from scripts import ymq4_b2_fixed_beta as b2
from scripts import ymq_gold2_compiler as gold2
from scripts import ymq_gold2_property_drift as drift


BATTLE = "YMQ-GOLD2-G4"


def _date(value: str) -> date:
    return date.fromisoformat(value[:10])


def _sum(rows: list[dict[str, Any]], field: str) -> float:
    return float(sum(float(row[field]) for row in rows))


def _window_rows(rows: list[dict[str, Any]], start: str, end: str) -> list[dict[str, Any]]:
    s, e = _date(start), _date(end)
    return [row for row in rows if s <= _date(row["decision_date"]) <= e]


def build_replay_packets(panel_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    constitution = gold2.load_constitution()
    gold2.validate_constitution(constitution)
    b2.validate_panel(panel_rows)
    transformed = b2.build_transformed_rows(panel_rows)
    train, _ = b2.split_rows(transformed)
    fixed_coef = b2.fit_ols(train)
    rolling = drift.rolling_states(transformed, drift.oos_start_index(transformed))

    packets: list[dict[str, Any]] = []
    for window in constitution["replay_windows"]:
        rows = _window_rows(transformed, window["start"], window["end"])
        if not rows:
            raise ValueError(f"replay window has no PIT rows: {window['id']}")
        known_as_of_max = max(row["known_as_of"] for row in rows)
        if _date(known_as_of_max) > _date(window["end"]):
            raise ValueError(f"future leakage in replay window {window['id']}")

        # Property-drift diagnosis is eligible only inside the canonical B2 OOS era.
        if _date(window["start"]) >= b2.OOS_START:
            property_state = drift.block_summary(
                rolling,
                fixed_coef,
                _date(window["start"]),
                _date(window["end"]),
            )["property_drift_state"]
        else:
            property_state = "INSUFFICIENT_EVIDENCE"

        packet = {
            "window_id": window["id"],
            "label": window["label"],
            "t0": window["end"],
            "known_as_of_max": known_as_of_max,
            "source_panel": b2.PANEL_ID,
            "pit_rows": len(rows),
            "core_macro_summary": {
                "cumulative_gold_log_return_pct": _sum(rows, "gold_return"),
                "cumulative_usd_log_return_pct": _sum(rows, "usd_return"),
                "net_inflation_yoy_change_pp": _sum(rows, "inflation_change"),
                "net_real_rate_change_pp": _sum(rows, "real_rate_change"),
            },
            "property_drift_state": property_state,
            "expectation_reality_state": "INDETERMINATE",
            "valuation_state": "UNIDENTIFIABLE",
            "unknowns": [
                "expected_policy_path_not_in_core_panel",
                "official_demand_not_in_core_panel",
                "private_flow_positioning_not_in_core_panel",
                "narrative_crowding_not_in_core_panel",
                "monetary_regime_premium_lens_not_in_core_panel",
            ],
            "frozen_label": property_state,
            "b3_settlement": gold2.EXPECTED_B3_SETTLEMENT,
            "capital_authorized": False,
            "execution_authorized": False,
            "settlement": "PENDING_SEPARATE_OUTCOME_ADJUDICATION",
        }
        gold2.validate_replay_packet(packet)
        packets.append(packet)
    return packets


def main() -> int:
    started = datetime.now(timezone.utc)
    sb_url = b2.require_env("SUPABASE_URL")
    sb_key = b2.require_env("YMQ4_SUPABASE_SECRET_KEY")
    panel = b2.rpc(sb_url, sb_key, "ymq4_b2_read_panel", {"p_panel_id": b2.PANEL_ID})
    if not isinstance(panel, list):
        raise RuntimeError("Gold PIT panel RPC returned unexpected shape")
    packets = build_replay_packets(panel)
    receipt = {
        "battle": BATTLE,
        "status": "BLIND_REPLAY_CORE_MATERIALIZED",
        "scientific_scope": "PIT_CORE_ONLY_FAIL_CLOSED_ON_MISSING_DOMAINS",
        "git_sha": os.getenv("GITHUB_SHA", "LOCAL"),
        "panel_id": b2.PANEL_ID,
        "replay_count": len(packets),
        "replays": packets,
        "capital_authorized": False,
        "execution_authorized": False,
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({
            "battle": BATTLE,
            "status": "FAIL_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        raise SystemExit(1)
