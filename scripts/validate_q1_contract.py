#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/architecture/q1/Q1-STATE.json"
SCHEMA = ROOT / "docs/architecture/q1/contracts/q1-qualification-record.schema.json"
SPEC = ROOT / "docs/architecture/q1/Q1-UNIVERSE-DATA-CONTRACT-QUALIFICATION-v1.md"
WIND = ROOT / "docs/architecture/q1/Q1-WIND-OPERATOR-TASK-SPEC-v1.md"
WIND_DIRECT = ROOT / "docs/architecture/q1/Q1-WIND-DIRECT-API-INTEGRATION-v1.md"

PROHIBITED = {
    "force_score", "target_price", "position_size", "buy_signal", "sell_signal",
    "trade_action", "expected_return", "broker_order"
}

for path in (STATE, SCHEMA, SPEC, WIND, WIND_DIRECT):
    if not path.exists():
        raise SystemExit(f"missing Q1 artifact: {path.relative_to(ROOT)}")

state = json.loads(STATE.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

assert state["stage"] == "Q1"
assert state["accepted_q0_commit"] == "f9ab0aba57be052cccf2323716731602ca028039"
assert state["seed_assets"] == 30
assert state["force_states_required"] == "unknown"
assert state["production_ingestion"] == "not_authorized"
assert state["a9_operational_canon_switch"] == "not_run_not_authorized"
assert state["rsi_frozen_change"] == "not_run_not_authorized"
assert state["live_trading"] == "architecturally_absent"
assert state["wind_official_skill_repo"] == "Wind-Information-Co-Ltd/wind-skills"
assert state["wind_official_skill_commit"] == "384e95796ad572a2a9402c14084de73a122f0a10"
assert state["wind_direct_api_contract"] == "discovered_and_pinned"
assert state["wind_qualification"] == "not_run"

for key in PROHIBITED:
    # Mentioning prohibited field names in policy text is allowed, but they must never appear as schema/state properties.
    if f'"{key}"' in STATE.read_text(encoding="utf-8") or f'"{key}"' in SCHEMA.read_text(encoding="utf-8"):
        raise SystemExit(f"prohibited Q1 state/schema field: {key}")

force_prop = schema["properties"]["force_state"]
assert force_prop == {"const": "unknown"}
print("Q1 contract validation: PASS")
