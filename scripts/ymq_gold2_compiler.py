#!/usr/bin/env python3
"""YMQ-GOLD2 governed Gold research compiler.

This module deliberately compiles research states only. It cannot create capital,
sizing, broker, or execution authority. It also preserves the YMQ4-B3 scientific
no-go as immutable benchmark history.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION_PATH = ROOT / "config" / "ymq_gold2" / "gold2_constitution.v0.1.json"
EXPECTED_B3_SETTLEMENT = "DYNAMIC_BETA_DOES_NOT_BEAT_B2"
PANEL_ID = "gold_core_monthly_v0.1"


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value[:10])
    except Exception as exc:
        raise ValueError(f"invalid ISO date: {value!r}") from exc


def load_constitution(path: Path | None = None) -> dict[str, Any]:
    p = path or CONSTITUTION_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def _assert_zero_action_authority(authority: Mapping[str, Any]) -> None:
    forbidden = (
        "capital_authorized",
        "sizing_authorized",
        "execution_authorized",
        "broker_action",
    )
    for field in forbidden:
        if authority.get(field) is not False:
            raise ValueError(f"{field} must be explicitly false")


def validate_constitution(c: Mapping[str, Any]) -> None:
    if c.get("program") != "YMQ-GOLD2":
        raise ValueError("wrong program identity")
    upstream = c.get("upstream_authority", {})
    if upstream.get("pit_panel") != PANEL_ID:
        raise ValueError("Gold PIT panel identity drift")
    if upstream.get("dynamic_beta_settlement") != EXPECTED_B3_SETTLEMENT:
        raise ValueError("YMQ4-B3 scientific no-go must remain immutable")
    authority = c.get("authority", {})
    _assert_zero_action_authority(authority)
    if authority.get("live_scheduler_authorized") is not False:
        raise ValueError("live scheduler is not authorized by GOLD2 constitution")
    if authority.get("canon_promotion_authorized") is not False:
        raise ValueError("Canon promotion is not authorized by GOLD2 constitution")
    if c.get("human_triangulation", {}).get("machine_may_fill_human_slots") is not False:
        raise ValueError("machine may not fabricate human judgments")


def validate_unified_state(state: Mapping[str, Any], c: Mapping[str, Any] | None = None) -> None:
    c = c or load_constitution()
    validate_constitution(c)
    required = c["unified_state"]["required_fields"]
    missing = [field for field in required if field not in state]
    if missing:
        raise ValueError(f"missing unified-state fields: {missing}")
    if state.get("source_panel") != PANEL_ID:
        raise ValueError("unapproved source panel")
    if _parse_date(str(state["known_as_of_max"])) > _parse_date(str(state["as_of"])):
        raise ValueError("future leakage: known_as_of_max is after state as_of")

    allowed = c["allowed_states"]
    enum_checks = {
        "property_drift_state": "property_drift",
        "expectation_reality_state": "expectation_reality",
        "valuation_state": "valuation",
        "lifecycle_state": "lifecycle",
    }
    for state_field, enum_name in enum_checks.items():
        if state[state_field] not in allowed[enum_name]:
            raise ValueError(f"unsupported {state_field}: {state[state_field]!r}")

    engine_state = state.get("engine_state")
    if not isinstance(engine_state, Mapping) or set(engine_state) != {"C", "R", "X", "S"}:
        raise ValueError("engine_state must preserve independent C/R/X/S fields")
    _assert_zero_action_authority(state.get("authority_state", {}))


def classify_property_drift(
    *,
    stable_factor_share: float,
    residual_persistence: float,
    independent_evidence_count: int,
) -> str:
    """Classify explanatory-property drift without claiming alpha.

    `stable_factor_share` is the share of explanatory contribution attributable to
    the previously dominant factor family. `residual_persistence` is a bounded
    diagnostic for unexplained persistence. These are research diagnostics, not
    a trading signal.
    """
    if not 0.0 <= stable_factor_share <= 1.0:
        raise ValueError("stable_factor_share must be in [0,1]")
    if not 0.0 <= residual_persistence <= 1.0:
        raise ValueError("residual_persistence must be in [0,1]")
    if independent_evidence_count < 2:
        return "INSUFFICIENT_EVIDENCE"
    if independent_evidence_count >= 4 and stable_factor_share <= 0.25 and residual_persistence >= 0.75:
        return "DRIFT_CONFIRMED_RESEARCH_ONLY"
    if stable_factor_share <= 0.45 and residual_persistence >= 0.60:
        return "DRIFT_CANDIDATE"
    if stable_factor_share >= 0.60 and residual_persistence <= 0.40:
        return "STABLE_PROPERTY"
    return "INSUFFICIENT_EVIDENCE"


def classify_expectation_reality(
    reality_score: float,
    expectation_score: float,
    evidence_complete: bool,
) -> str:
    """Compile a bounded research label from normalized [-1,1] scores."""
    if not evidence_complete:
        return "INDETERMINATE"
    for value in (reality_score, expectation_score):
        if not -1.0 <= value <= 1.0:
            raise ValueError("scores must be in [-1,1]")
    if reality_score * expectation_score < 0 and abs(reality_score) >= 0.5 and abs(expectation_score) >= 0.5:
        return "DIVERGENT"
    if abs(reality_score) >= 0.6 and abs(expectation_score) >= 0.6 and reality_score * expectation_score > 0:
        return "CONFIRMED"
    if reality_score - expectation_score >= 0.4:
        return "REALITY_LED"
    if expectation_score - reality_score >= 0.4:
        return "EXPECTATION_LED"
    return "INDETERMINATE"


def classify_valuation(lens_states: Mapping[str, str]) -> str:
    """Combine three Gold valuation lenses without emitting a target price."""
    c = load_constitution()
    required = set(c["valuation_lenses"])
    if set(lens_states) != required:
        return "UNIDENTIFIABLE"
    allowed = {"UNDERPRICED", "FAIR", "OVERPRICED", "UNIDENTIFIABLE"}
    if any(value not in allowed for value in lens_states.values()):
        raise ValueError("unsupported valuation-lens state")
    if "UNIDENTIFIABLE" in lens_states.values():
        return "UNIDENTIFIABLE"
    counts = Counter(lens_states.values())
    state, n = counts.most_common(1)[0]
    return state if n >= 2 else "UNIDENTIFIABLE"


def validate_replay_packet(packet: Mapping[str, Any]) -> None:
    if "t0" not in packet or "known_as_of_max" not in packet or "frozen_label" not in packet:
        raise ValueError("incomplete replay packet")
    if _parse_date(str(packet["known_as_of_max"])) > _parse_date(str(packet["t0"])):
        raise ValueError("post-T0 evidence entered replay state")
    if packet.get("b3_settlement", EXPECTED_B3_SETTLEMENT) != EXPECTED_B3_SETTLEMENT:
        raise ValueError("B3 scientific history rewritten")
    if packet.get("capital_authorized", False) or packet.get("execution_authorized", False):
        raise ValueError("replay research may not create capital or execution authority")


def build_triangulation(*, machine_state_judgment: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(machine_state_judgment, Mapping):
        raise ValueError("machine judgment must be an object")
    if not machine_state_judgment.get("known_as_of"):
        raise ValueError("machine judgment requires known_as_of")
    return {
        "ray_regime_judgment": "PENDING_HUMAN_EVIDENCE",
        "yiru_timing_judgment": "PENDING_HUMAN_EVIDENCE",
        "machine_state_judgment": dict(machine_state_judgment),
        "settlement": "PENDING_REALITY",
        "attribution": "PENDING_SETTLEMENT",
    }


def build_live_shadow_packet(*, as_of: str, state: str, lifecycle: str) -> dict[str, Any]:
    c = load_constitution()
    if state not in c["allowed_states"]["live_shadow"]:
        raise ValueError("unsupported live-shadow state")
    if lifecycle not in c["allowed_states"]["lifecycle"]:
        raise ValueError("unsupported lifecycle state")
    _parse_date(as_of)
    return {
        "program": "YMQ-GOLD2",
        "target": "GOLD",
        "as_of": as_of,
        "research_state": state,
        "lifecycle_state": lifecycle,
        "capital_authorized": False,
        "sizing_authorized": False,
        "execution_authorized": False,
        "broker_action": False,
        "scheduler_authorized": False,
    }


def main() -> int:
    c = load_constitution()
    validate_constitution(c)
    print("YMQ-GOLD2 constitution: PASS")
    print(f"B3 preserved: {EXPECTED_B3_SETTLEMENT}")
    print("Capital/Execution/Scheduler: DENY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
