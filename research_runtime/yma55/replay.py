from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .validation import assert_no_capital_outputs

REQUIRED_CASE_TYPES = {"GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"}
REQUIRED_MECHANISMS = {"MRM-D", "MRM-CR", "MRM-SC"}
REQUIRED_T0_KEYS = {"world", "constraint", "transmission", "hypothesis_set", "transferability_template"}


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    mechanisms = data.get("mechanisms", {})
    if set(mechanisms) != REQUIRED_MECHANISMS:
        raise ValueError("H4 manifest must contain exactly Duration, Credit and Scarcity")
    return data


def validate_replay_case(case: dict[str, Any]) -> None:
    required = {
        "episode_id",
        "mechanism_family",
        "case_type",
        "as_of",
        "evidence_cutoff",
        "evidence_status",
        "gold_qualified",
        "t0",
        "settlement",
    }
    missing = required - set(case)
    if missing:
        raise ValueError(f"replay case missing fields: {sorted(missing)}")
    if case["mechanism_family"] not in REQUIRED_MECHANISMS:
        raise ValueError("unsupported H4 mechanism family")
    if case["case_type"] not in REQUIRED_CASE_TYPES:
        raise ValueError("unsupported H4 case type")
    if set(case["t0"]) != REQUIRED_T0_KEYS:
        raise ValueError("T0 must contain exactly the five H1 projection inputs")
    if case["evidence_status"] != "hydrated" and case.get("gold_qualified"):
        raise ValueError("unhydrated replay cannot claim Gold qualification")
    hs = case["t0"]["hypothesis_set"]
    if not hs.get("pit_frozen"):
        raise ValueError("hypothesis set must be PIT-frozen")
    if not isinstance(hs.get("alternatives"), list) or not 1 <= len(hs["alternatives"]) <= 3:
        raise ValueError("hypothesis set must include 1..3 alternatives")
    if not hs.get("primary") or not hs.get("null"):
        raise ValueError("primary and null hypotheses are mandatory")
    assert_no_capital_outputs(case["t0"])
    assert_no_capital_outputs(case["settlement"])


def load_replay_case(path: Path) -> dict[str, Any]:
    case = json.loads(path.read_text(encoding="utf-8"))
    validate_replay_case(case)
    return case


def run_replay_case(case: dict[str, Any]) -> dict[str, Any]:
    """Freeze runner input before settlement is exposed.

    H4 is a reference replay harness, not an inference engine. The output proves
    that settlement/outcome data are physically excluded from T0 research input.
    """

    validate_replay_case(case)
    runner_input = {
        "episode_id": case["episode_id"],
        "mechanism_family": case["mechanism_family"],
        "case_type": case["case_type"],
        "as_of": case["as_of"],
        "evidence_cutoff": case["evidence_cutoff"],
        "evidence_status": case["evidence_status"],
        "t0": copy.deepcopy(case["t0"]),
    }
    assert "settlement" not in runner_input
    assert_no_capital_outputs(runner_input)
    frozen_research_state = {
        "hypothesis_set_id": runner_input["t0"]["hypothesis_set"]["hypothesis_set_id"],
        "resolution_state": "UNRESOLVED_AT_T0",
        "evidence_status": runner_input["evidence_status"],
    }
    return {
        "episode_id": case["episode_id"],
        "runner_input": runner_input,
        "frozen_research_state": frozen_research_state,
        "settlement": copy.deepcopy(case["settlement"]),
    }
