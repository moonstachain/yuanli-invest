#!/usr/bin/env python3
"""Fail-closed validation for M1.2 candidate semantic contracts.

M1.2 is candidate-only: legacy v1.0 schemas must remain byte-identical and the
new contracts must not authorize trading, target prices, position sizing, Q1
Force generation, or portfolio-survival semantics at the asset level.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
M1 = ROOT / "docs" / "architecture" / "m1"
CONTRACTS = M1 / "contracts"
STATE = M1 / "M1-2-STATE.json"
SPEC = M1 / "M1-2-EXTREME-SURVIVAL-SEMANTIC-CONTRACT-SPLIT-v0.1.md"

CANDIDATE_FILES = [
    "structural-right-tail-profile.schema.json",
    "tail-activation-snapshot.schema.json",
    "payoff-convexity-context.schema.json",
    "issuer-durability-gate.schema.json",
    "valuation-context.schema.json",
    "portfolio-survival-policy.schema.json",
    "portfolio-survival-snapshot.schema.json",
    "force-asset-snapshot.schema.json",
]

LEGACY_BLOBS = {
    ROOT / "packages/contracts/schemas/convexity-profile.schema.json": "6c150e03ae3163517153bdd9683cbd083a675198",
    ROOT / "packages/contracts/schemas/force-triangle-snapshot.schema.json": "0e3be577a7daee5038e04401f760a75136be76ef",
}

PROHIBITED_ACTION_KEYS = {
    "position_size",
    "target_price",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "recommended_weight",
    "target_weight",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def walk_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from walk_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_keys(item)


def main() -> None:
    assert SPEC.exists() and STATE.exists()
    missing = [name for name in CANDIDATE_FILES if not (CONTRACTS / name).exists()]
    assert not missing, f"missing M1.2 candidate schemas: {missing}"

    schemas = {}
    for name in CANDIDATE_FILES:
        schema = load(CONTRACTS / name)
        Draft202012Validator.check_schema(schema)
        assert schema["$id"].startswith("urn:yuanli-invest:m1:"), name
        schemas[name] = schema

    # Legacy v1.0 contracts cannot be changed in place by M1.2.
    for path, expected_blob in LEGACY_BLOBS.items():
        assert git_blob_sha(path) == expected_blob, f"legacy contract drift: {path}"

    all_candidate_keys = set()
    for schema in schemas.values():
        all_candidate_keys.update(walk_keys(schema))
    assert not (PROHIBITED_ACTION_KEYS & all_candidate_keys), (
        f"prohibited action keys: {sorted(PROHIBITED_ACTION_KEYS & all_candidate_keys)}"
    )

    tail = schemas["tail-activation-snapshot.schema.json"]
    causal = tail["properties"]["causal_status"]["enum"]
    assert causal == ["predictive", "causal_candidate", "identified", "unknown"]

    issuer = schemas["issuer-durability-gate.schema.json"]
    assert issuer["properties"]["portfolio_survival_semantics_prohibited"] == {"const": True}

    force = schemas["force-asset-snapshot.schema.json"]
    assert "survival_gate" not in force["properties"]
    assert "portfolio_survival_snapshot_id" not in force["properties"]
    assert force["properties"]["portfolio_survival_excluded"] == {"const": True}
    assert force["properties"]["scalar_score_prohibited"] == {"const": True}

    survival = schemas["portfolio-survival-snapshot.schema.json"]
    assert "subject_id" not in survival["properties"]
    assert survival["properties"]["action_fields_prohibited"] == {"const": True}

    valuation = schemas["valuation-context.schema.json"]
    assert valuation["properties"]["fourth_vertex_prohibited"] == {"const": True}

    state = load(STATE)
    assert state["status"] == "candidate_started"
    assert state["legacy_contracts"] == "unchanged"
    assert state["q1_force_state_generation"] == "prohibited"
    assert state["production_ingestion"] == "not_authorized"
    assert state["rsi_frozen_change"] == "not_authorized"
    assert state["live_trading"] == "unavailable_by_design"

    print("M1.2 Extreme/Survival semantic contract validation: PASS")


if __name__ == "__main__":
    main()
