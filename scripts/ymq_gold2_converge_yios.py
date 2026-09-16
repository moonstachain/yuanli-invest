#!/usr/bin/env python3
"""Compile the accepted YIOS-G1 Gold T0 state into YMQ-GOLD2 unified state.

This is a semantic convergence proof. It preserves explicit unknowns and does not
invent fiscal, crowding, valuation, capital, or execution authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ymq_gold2_compiler as gold2


ROOT = Path(__file__).resolve().parents[1]
YIOS_STATE = ROOT / "config" / "yios_g1" / "gold_state_t0.v1.json"


def load_yios_state() -> dict[str, Any]:
    return json.loads(YIOS_STATE.read_text(encoding="utf-8"))


def compile_unified_state(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("program_id") != "YIOS-G1" or source.get("case_id") != "YIOS-GOLD-001":
        raise ValueError("unexpected YIOS Gold source identity")
    if source.get("future_leakage_count") != 0:
        raise ValueError("YIOS source contains future leakage")
    reality = source["reality_state"]
    demand = source["demand_state"]
    regime = source["regime_state"]
    authority = source["authority_state"]
    if authority.get("capital_authority") is not False or authority.get("execution_authority") is not False:
        raise ValueError("YIOS source unexpectedly grants downstream authority")

    unknowns = list(source.get("unknown_state", {}).get("decisive_unknowns", []))
    unknowns += list(source.get("unknown_state", {}).get("non_decisive_unknowns", []))
    unknowns += [
        "fiscal_sovereign_state_not_explicit_in_yios_t0",
        "crowding_state_not_explicit_in_yios_t0",
        "multi_lens_valuation_not_available_at_yios_t0",
    ]

    unified = {
        "as_of": source["known_as_of"][:10],
        "known_as_of_max": source["known_as_of"][:10],
        "source_panel": reality["pit_panel"],
        "monetary_regime_state": {
            "candidate": regime["candidate"],
            "status": regime["status"],
        },
        "real_rate_state": {
            "real_rate_10y": reality["real_rate_10y"],
            "measurement_regime": reality["measurement_regime"],
        },
        "usd_state": {"usd_broad_index": reality["usd_broad_index"]},
        "inflation_state": {
            "inflation_yoy": reality["inflation_yoy"],
            "pce_yoy_percent": source["monetary_state"]["pce_yoy_percent"],
            "core_pce_yoy_percent": source["monetary_state"]["core_pce_yoy_percent"],
        },
        "fiscal_sovereign_state": "UNKNOWN_NOT_EXPLICIT_AT_T0",
        "official_demand_state": demand["official_demand"],
        "private_demand_state": demand["private_demand"],
        "narrative_state": source["narrative_state"],
        "crowding_state": "UNKNOWN_NOT_EXPLICIT_AT_T0",
        "price_state": source["price_state"],
        "implied_expectation_state": {
            "rate_cut_expectations": "RELEVANT_BUT_NOT_REALIZED_AT_T0",
            "future_path": "UNKNOWN",
        },
        "property_drift_state": "INSUFFICIENT_EVIDENCE",
        "expectation_reality_state": "INDETERMINATE",
        "valuation_state": "UNIDENTIFIABLE",
        "driver_state": {
            "supporting": regime.get("supporting_at_t0", []),
            "opposing": regime.get("opposing_at_t0", []),
        },
        "engine_state": {
            "C": "UNKNOWN",
            "R": "RESEARCH_CANDIDATE",
            "X": "UNKNOWN",
            "S": "RESEARCH_CANDIDATE",
        },
        "lifecycle_state": "未知",
        "falsifiers": source["falsifier_state"],
        "unknowns": unknowns,
        "authority_state": {
            "research_authorized": True,
            "capital_authorized": False,
            "sizing_authorized": False,
            "execution_authorized": False,
            "broker_action": False,
        },
        "source_lineage": source["source_lineage"],
    }
    gold2.validate_unified_state(unified)
    return unified


def main() -> int:
    state = compile_unified_state(load_yios_state())
    print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
