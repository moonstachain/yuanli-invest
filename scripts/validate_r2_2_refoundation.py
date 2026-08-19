#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "os-vnext"
ARCH = ROOT / "docs" / "architecture"
SD = ROOT / "packages" / "contracts" / "schemas" / "vnext"

DOCS_REQ = [
    "README.md",
    "CONSTITUTION.md",
    "RESEARCH-DEPENDENCY-GRAPH.md",
    "AUTHORITY-PRECEDENCE.md",
    "LEARNING-LOOP.md",
    "SEVEN-QUESTIONS.md",
]
SCHEMA_REQ = [
    "research-target.schema.json",
    "canonical-observation.schema.json",
    "evidence-claim.schema.json",
    "research-state-vector.schema.json",
    "capability-invocation.schema.json",
    "capability-input-bundle.schema.json",
    "capability-result.schema.json",
    "execution-receipt.schema.json",
    "future-settlement.schema.json",
    "capability-revision.schema.json",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    for name in DOCS_REQ:
        assert (DOCS / name).exists(), name
    for name in SCHEMA_REQ:
        obj = load(SD / name)
        assert obj["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert obj["type"] == "object"
        assert obj["additionalProperties"] is False

    constitution = (DOCS / "CONSTITUTION.md").read_text(encoding="utf-8")
    graph = (DOCS / "RESEARCH-DEPENDENCY-GRAPH.md").read_text(encoding="utf-8")
    loop = (DOCS / "LEARNING-LOOP.md").read_text(encoding="utf-8")
    for token in [
        "Lifetime Right-Tail Capture under Survival Constraints",
        "X := (Xs, Xa, Xp)",
        "Claim Authority <= Evidence Authority",
        "ResearchCapability",
        "Force score",
    ]:
        assert token in constitution
    assert "not a claim that market reality always follows a one-way causal law" in graph
    assert "Receipt = Ledger; Status = Projection" in loop

    state = load(ARCH / "r2_2" / "R2-2-STATE.json")
    assert state["status"] == "candidate_ready_for_human_review"
    assert state["canonical_state_candidate"] == "ResearchStateVector"
    assert state["dependency_graph_is_universal_causal_law"] is False
    assert state["migration_boundary"]["existing_gold_ids_mutated"] is False
    qualification = state["machine_qualification"]
    assert qualification["validated_head_sha"] == "919c983f6ed4b4263e78da996f9bf812b8f4edac"
    assert qualification["run_number"] == 94
    assert qualification["run_id"] == 32229450450
    assert qualification["conclusion"] == "success"
    assert qualification["contracts"] == "success"
    assert qualification["governance"] == "success"
    assert state["next_gate"] == "R2_2_HUMAN_REVIEW"

    r2 = load(ARCH / "r2" / "R2-STATE.json")
    assert r2["capability_count"] == 12
    assert r2["registry_entry_count"] == 99
    assert r2["canon_entry_count"] == 0

    canon = load(ARCH / "CANON-STATUS.json")
    assert canon["projection_semantics"] == "deterministic_non_authoritative_projection"
    assert canon["stages"]["R2_1"]["status"] == "accepted_merged"
    assert canon["stages"]["R2_2"]["status"] == "candidate_ready_for_human_review"
    assert canon["stages"]["R3A"]["status"] == "paused_not_started"
    assert canon["next_gate"] == "R2_2_HUMAN_REVIEW"

    props = load(SD / "research-state-vector.schema.json")["properties"]
    assert all(key in props for key in ["P", "Xs", "N", "V", "Xa", "Xp", "S"])
    assert props["scalar_pnx_score_prohibited"]["const"] is True
    assert props["force_classification_is_projection"]["const"] is True
    assert load(SD / "execution-receipt.schema.json")["properties"]["live_execution_authorized"]["const"] is False

    print("R2.2 Research Intelligence Canon Re-foundation validation: PASS")


if __name__ == "__main__":
    main()
