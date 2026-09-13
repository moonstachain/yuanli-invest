from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ymq_os0" / "ymq_os0_contract.v0.1.json"

EXPECTED_PLANES = [
    "LAW_CONTROL",
    "EVIDENCE_RUNTIME_TRUTH",
    "EXPERIMENT_COMPUTE",
    "EXPERIENCE_PROJECTION",
]
EXPECTED_OBJECTS = [
    "SourceSnapshot",
    "ObservationPIT",
    "FeaturePIT",
    "StatePIT",
    "TransmissionEdgePIT",
    "ResearchClaim",
    "CapabilityRun",
    "ResearchSettlement",
    "LearningDelta",
]
EXPECTED_ENGINES = ["MQE1", "MQE2", "MQE3", "MQE4", "MQE5"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_contract(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(CONFIG) if cfg is None else cfg
    require(cfg["identity"]["program_id"] == "YMQ-OS0-G0", "program id drift")
    require(cfg["parent_authority"]["system_id"] == "YIOS0", "parent system drift")
    require(cfg["parent_authority"]["scope"] == "L2-L8_RESEARCH_SIDE_ONLY", "research scope drift")
    require(cfg["parent_authority"]["parallel_investment_os"] is False, "parallel Investment OS prohibited")
    require([p["id"] for p in cfg["physical_planes"]] == EXPECTED_PLANES, "physical plane drift")
    require([o["type"] for o in cfg["canonical_objects"]] == EXPECTED_OBJECTS, "canonical object drift")
    require([e["id"] for e in cfg["engines"]] == EXPECTED_ENGINES, "engine role drift")
    require(cfg["pit_time_semantics"]["replay_rule"] == "known_as_of <= T0", "PIT replay law drift")
    require(cfg["pit_time_semantics"]["unknown_semantics"] == "DENY", "UNKNOWN must deny")
    require(cfg["laws"]["research_pass_vs_capital_pass"] == "NOT_EQUAL", "ResearchPass must not equal CapitalPass")
    require(cfg["laws"]["authority_separation"] == ["ResearchAuthority", "CapitalAuthority", "ExecutionAuthority"], "authority separation drift")
    require(cfg["ymq4_lineage"]["preserve_historical_ids"] is True, "YMQ4 historical IDs must be preserved")
    require(cfg["ymq4_lineage"]["ymq4_equals_mqe4_canon"] is False, "YMQ4 must not alias MQE4 Canon")
    require(cfg["ymq4_lineage"]["b3"]["scientific_status"] == "SCIENTIFIC_NO_GO", "YMQ4-B3 NO-GO hidden")
    require(cfg["ymq4_lineage"]["b3"]["canon_authority"] == "NONE", "YMQ4-B3 authority escalated")
    for key in ("capital_authorized", "execution_authorized", "broker_authorized", "real_capital_movement_authorized"):
        require(cfg["authority"][key] is False, f"authority escalated: {key}")
    for key, value in cfg["non_authorizations"].items():
        require(value is False, f"non-authorization escalated: {key}")


def positive_fixture_bundle() -> dict[str, Any]:
    raise NotImplementedError("Task 5 validator fixture not implemented yet")


def validate_pit_relations(bundle: dict[str, Any]) -> None:
    raise NotImplementedError("Task 5 PIT relational validator not implemented yet")


def validate_claim_authority(bundle: dict[str, Any]) -> None:
    raise NotImplementedError("Task 5 claim authority validator not implemented yet")


def validate_settlement_separation(settlement: dict[str, Any]) -> None:
    raise NotImplementedError("Task 5 settlement validator not implemented yet")


def validate_learning_forward_only(learning: dict[str, Any]) -> None:
    raise NotImplementedError("Task 5 learning validator not implemented yet")


def validate_all() -> None:
    validate_contract()
    raise NotImplementedError("Tasks 3-5 not implemented yet")


if __name__ == "__main__":
    validate_all()
