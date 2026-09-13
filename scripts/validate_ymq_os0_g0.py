from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ymq_os0" / "ymq_os0_contract.v0.1.json"
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas" / "ymq"
ARCH_DIR = ROOT / "docs" / "architecture" / "ymq_os0"
YIOS0_STATUS = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-STATUS-MATRIX.md"

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
EXPECTED_ENGINES = [
    ("MQE1", "Macro Reality Engine"),
    ("MQE2", "Industrial Reality Engine"),
    ("MQE3", "Narrative × Herding Engine"),
    ("MQE4", "Dynamic Transmission Engine"),
    ("MQE5", "Price × Payoff Engine"),
]
SCHEMA_FILES = {
    "source_snapshot": "source_snapshot.schema.json",
    "observation": "observation_pit.schema.json",
    "feature": "feature_pit.schema.json",
    "state": "state_pit.schema.json",
    "edge": "transmission_edge_pit.schema.json",
    "claim": "research_claim.schema.json",
    "run": "capability_run.schema.json",
    "settlement": "research_settlement.schema.json",
    "learning": "learning_delta.schema.json",
}
DOC_FILES = [
    "YMQ-OS0-CONSTITUTION-v0.1.md",
    "YMQ-OS0-OBJECT-MODEL-v0.1.md",
    "YMQ-OS0-PHYSICAL-PLANE-FREEZE-v0.1.md",
    "YMQ-OS0-HUMAN-REVIEW-CARD-v0.1.md",
]
FORBIDDEN_ACTION_SCHEMA_TOKENS = [
    "portfolio_weight_authority",
    "position_sizing_authority",
    "order_submission_authority",
    "live_execution_authority",
    "real_capital_movement_authority",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(dt.tzinfo is not None, f"timestamp must be timezone-aware: {value}")
    return dt


def validate_contract(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(CONFIG) if cfg is None else cfg
    require(cfg["identity"]["program_id"] == "YMQ-OS0-G0", "program id drift")
    require(cfg["identity"]["system_kind"] == "YIOS0_RESEARCH_SUBSYSTEM", "system kind drift")
    require(cfg["parent_authority"]["system_id"] == "YIOS0", "parent system drift")
    require(cfg["parent_authority"]["scope"] == "L2-L8_RESEARCH_SIDE_ONLY", "research scope drift")
    require(cfg["parent_authority"]["parallel_investment_os"] is False, "parallel Investment OS prohibited")
    require([p["id"] for p in cfg["physical_planes"]] == EXPECTED_PLANES, "physical plane drift")
    for plane in cfg["physical_planes"]:
        require(len(plane["primary_authority_roles"]) == 1, f"plane must have one primary role: {plane['id']}")
    require([o["type"] for o in cfg["canonical_objects"]] == EXPECTED_OBJECTS, "canonical object drift")
    require([(e["id"], e["name"]) for e in cfg["engines"]] == EXPECTED_ENGINES, "engine role drift")
    require(cfg["pit_time_semantics"]["replay_rule"] == "known_as_of <= T0", "PIT replay law drift")
    require(cfg["pit_time_semantics"]["unknown_semantics"] == "DENY", "UNKNOWN must deny")
    require(cfg["pit_time_semantics"]["later_revision_substitution_prohibited"] is True, "later revision substitution enabled")
    require(cfg["laws"]["research_pass_vs_capital_pass"] == "NOT_EQUAL", "ResearchPass must not equal CapitalPass")
    require(cfg["laws"]["authority_separation"] == ["ResearchAuthority", "CapitalAuthority", "ExecutionAuthority"], "authority separation drift")
    require(cfg["laws"]["claim_authority_le_evidence_authority"] is True, "claim authority ceiling disabled")
    require(cfg["laws"]["past_evidence_immutable"] is True, "past evidence immutability disabled")
    require(cfg["laws"]["learning_forward_only"] is True, "learning forward-only disabled")
    require(cfg["settlement_semantics"]["axes"] == ["physical_status", "scientific_status", "authority_status"], "settlement axes drift")
    require(cfg["settlement_semantics"]["single_global_pass_prohibited"] is True, "single global PASS allowed")
    require(cfg["versioning"]["current_pointer_self_authorizes"] is False, "candidate pointer self-authorizes")
    validate_provider_authority(cfg)
    validate_ymq4_lineage(cfg)
    validate_non_authorizations(cfg)


def positive_fixture_bundle() -> dict[str, Any]:
    sha40 = "a" * 40
    hash64 = "b" * 64
    return {
        "source_snapshot": {
            "source_snapshot_id": "YMQ-SS-FIXTURE-001",
            "source_id": "fixture-source",
            "source_authority_tier": "T1_OFFICIAL_PRIMARY",
            "source_class": "official_release",
            "canonical_locator": "urn:fixture:source:001",
            "retrieved_at": "2020-03-11T12:00:00Z",
            "content_sha256": hash64,
            "storage_locator": "evidence://fixture/001",
            "license_class": "TEST_FIXTURE",
            "runner_git_sha": sha40,
            "supersedes_snapshot_id": None,
            "immutable": True,
        },
        "observation": {
            "observation_id": "YMQ-OBS-FIXTURE-001",
            "series_or_fact_id": "fixture-series",
            "event_time": None,
            "observation_time": "2020-02-01T00:00:00Z",
            "release_time": "2020-03-11T08:30:00Z",
            "vintage_time": "2020-03-11T08:30:00Z",
            "known_as_of": "2020-03-11T08:30:00Z",
            "value": 1.0,
            "unit": "index",
            "source_snapshot_id": "YMQ-SS-FIXTURE-001",
            "measurement_regime": "fixture-v1",
            "pit_status": "QUALIFIED",
            "quality_flags": [],
        },
        "feature": {
            "feature_id": "YMQ-FEAT-FIXTURE-001",
            "feature_definition_version": "0.1.0",
            "as_of": "2020-03-13T23:59:59Z",
            "known_as_of": "2020-03-11T08:30:00Z",
            "input_observation_refs": ["YMQ-OBS-FIXTURE-001"],
            "transform_git_sha": sha40,
            "value": 0.5,
            "lookback_window": "TRAILING_ONLY",
            "normalization_rule": "NO_FUTURE_INPUT",
            "input_manifest_hash": "sha256:" + hash64,
        },
        "state": {
            "state_id": "YMQ-STATE-FIXTURE-001",
            "state_type": "FixtureState",
            "as_of": "2020-03-13T23:59:59Z",
            "known_as_of": "2020-03-13T23:59:59Z",
            "feature_refs": ["YMQ-FEAT-FIXTURE-001"],
            "method_version": "0.1.0",
            "state_payload": {"label": "FIXTURE"},
            "uncertainty": {"class": "known"},
            "unknown_fields": [],
            "projection_may_strengthen_unknown": False,
        },
        "edge": {
            "edge_id": "YMQ-EDGE-FIXTURE-001",
            "from_state_or_driver": "YMQ-STATE-FIXTURE-001",
            "to_state_or_asset": "FIXTURE_ASSET",
            "as_of": "2020-03-13T23:59:59Z",
            "known_as_of": "2020-03-13T23:59:59Z",
            "method": "fixture-method",
            "coefficient_or_effect": 0.1,
            "confidence_or_uncertainty": {"class": "fixture"},
            "evidence_refs": ["YMQ-STATE-FIXTURE-001"],
            "stability_window": "4w",
            "permanent_beta_claim": False,
        },
        "claim": {
            "claim_id": "YMQ-CLAIM-FIXTURE-001",
            "claim_type": "INFERENCE",
            "as_of": "2020-03-13T23:59:59Z",
            "statement": "Fixture defeasible research claim.",
            "evidence_refs": ["YMQ-STATE-FIXTURE-001"],
            "evidence_authority": "INDEPENDENT_EMPIRICAL",
            "claim_authority": "RESEARCH_SYNTHESIS",
            "falsifier": ["fixture falsifier"],
            "expiry_or_review_rule": "review on new evidence",
            "counterevidence_refs": [],
        },
        "run": {
            "run_id": "YMQ-RUN-FIXTURE-001",
            "battle_id": "YMQ-OS0-G0-FIXTURE",
            "capability_id": "CAP-FIXTURE",
            "capability_version": "0.1.0",
            "git_sha": sha40,
            "dataset_or_panel_revision": "fixture-panel@0.1.0",
            "source_revisions": ["YMQ-SS-FIXTURE-001"],
            "parameter_contract": {"frozen": True},
            "started_at": "2020-03-14T00:00:00Z",
            "completed_at": "2020-03-14T00:00:01Z",
            "artifact_hashes": ["sha256:" + hash64],
            "runner_identity": "fixture-runner",
            "baseline_id": "B0-FIXTURE",
            "hard_negative_set": ["HN-FIXTURE"],
            "ablation_set": ["ABL-FIXTURE"],
            "falsifiers": ["fixture defeat condition"],
            "output_artifact_policy": "non-secret hashed artifact",
        },
        "settlement": {
            "settlement_id": "YMQ-SETTLE-FIXTURE-001",
            "run_refs": ["YMQ-RUN-FIXTURE-001"],
            "physical_status": "PHYSICAL_PASS",
            "scientific_status": "SCIENTIFIC_NO_GO",
            "authority_status": "NONE",
            "baseline_result": {"status": "fixture"},
            "hard_negative_result": {"status": "fixture"},
            "ablation_result": {"status": "fixture"},
            "known_limitations": ["fixture only"],
            "next_authorized_stage": None,
            "settled_at": "2020-03-14T00:01:00Z",
            "receipt_is_ledger": True,
            "status_is_projection": True,
        },
        "learning": {
            "learning_id": "YMQ-LEARN-FIXTURE-001",
            "settlement_ref": "YMQ-SETTLE-FIXTURE-001",
            "proposed_change": "Use settlement only to propose a future contract revision.",
            "affected_capability_or_contract": "CAP-FIXTURE",
            "evidence_basis": ["YMQ-SETTLE-FIXTURE-001"],
            "requires_human_review": True,
            "status": "PROPOSED",
            "rewrite_past_authorized": False,
            "created_at": "2020-03-14T00:02:00Z",
        },
    }


def validate_schemas(bundle: dict[str, Any]) -> None:
    checker = FormatChecker()
    actual = sorted(p.name for p in SCHEMA_DIR.glob("*.schema.json"))
    require(actual == sorted(SCHEMA_FILES.values()), "YMQ schema file set drift")
    ids: set[str] = set()
    for key, filename in SCHEMA_FILES.items():
        schema = load_json(SCHEMA_DIR / filename)
        Draft202012Validator.check_schema(schema)
        require(schema["$id"] not in ids, f"duplicate schema id: {schema['$id']}")
        ids.add(schema["$id"])
        errors = sorted(Draft202012Validator(schema, format_checker=checker).iter_errors(bundle[key]), key=lambda e: list(e.path))
        require(not errors, f"{filename} fixture invalid: {errors[0].message if errors else ''}")
        text = (SCHEMA_DIR / filename).read_text(encoding="utf-8")
        for token in FORBIDDEN_ACTION_SCHEMA_TOKENS:
            require(token not in text, f"action authority leaked into {filename}: {token}")


def validate_pit_relations(bundle: dict[str, Any]) -> None:
    obs = bundle["observation"]
    feature = bundle["feature"]
    state = bundle["state"]
    edge = bundle["edge"]
    require(obs["pit_status"] == "QUALIFIED", "non-qualified observation cannot enter fixture research chain")
    require(obs["source_snapshot_id"] == bundle["source_snapshot"]["source_snapshot_id"], "observation/source snapshot mismatch")
    require(obs["observation_id"] in feature["input_observation_refs"], "feature does not reference observation")
    require(feature["feature_id"] in state["feature_refs"], "state does not reference feature")
    require(parse_time(obs["known_as_of"]) <= parse_time(feature["as_of"]), "future observation knowledge entered feature")
    require(parse_time(feature.get("known_as_of", feature["as_of"])) <= parse_time(state["as_of"]), "future feature knowledge entered state")
    require(parse_time(state.get("known_as_of", state["as_of"])) <= parse_time(edge["as_of"]), "future state knowledge entered transmission edge")
    require(parse_time(edge.get("known_as_of", edge["as_of"])) <= parse_time(edge["as_of"]), "future edge knowledge")


def validate_claim_authority(bundle: dict[str, Any]) -> None:
    cfg = load_json(CONFIG)
    order = cfg["laws"]["evidence_authority_order"]
    claim = bundle["claim"]
    require(claim["evidence_refs"], "claim has no evidence refs")
    require(claim["falsifier"], "claim has no falsifier")
    require(claim["evidence_authority"] in order and claim["claim_authority"] in order, "unknown authority class")
    require(order.index(claim["claim_authority"]) <= order.index(claim["evidence_authority"]), "ClaimAuthority exceeds EvidenceAuthority")


def validate_settlement_separation(settlement: dict[str, Any]) -> None:
    cfg = load_json(CONFIG)
    require("status" not in settlement, "catch-all settlement status prohibited")
    for key in ("physical_status", "scientific_status", "authority_status"):
        require(key in settlement, f"settlement axis missing: {key}")
    pair = {"physical_status": settlement["physical_status"], "scientific_status": settlement["scientific_status"]}
    require(pair in cfg["settlement_semantics"]["valid_status_combinations"], "invalid physical/scientific settlement combination")
    require(settlement["authority_status"] in {"NONE", "AWAITING_HUMAN_REVIEW", "HUMAN_ACCEPTED_RESEARCH_ONLY"}, "invalid research authority state")
    require(settlement.get("receipt_is_ledger") is True, "receipt must remain ledger")
    require(settlement.get("status_is_projection") is True, "status must remain projection")


def validate_learning_forward_only(learning: dict[str, Any]) -> None:
    require(learning.get("rewrite_past_authorized") is False, "LearningDelta cannot rewrite past evidence/settlement")
    require(learning.get("requires_human_review") is True, "LearningDelta law change must require Human review")
    require(learning.get("status") in {"PROPOSED", "UNDER_REVIEW", "ACCEPTED_FOR_FUTURE", "REJECTED"}, "invalid LearningDelta state")


def validate_provider_authority(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(CONFIG) if cfg is None else cfg
    policy = cfg["provider_policy"]
    require(policy["provider_identity_never_grants_canon"] is True, "provider identity grants Canon")
    require(policy["experiment_compute"]["authority"] == "NONE", "compute provider received authority")
    require(policy["experiment_compute"]["replaceable"] is True, "compute provider hard-wired")
    require(policy["experience_projection"]["authority"] == "PROJECTION_ONLY", "experience plane authority escalated")
    require(policy["experience_projection"]["replaceable"] is True, "experience provider hard-wired")


def validate_ymq4_lineage(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(CONFIG) if cfg is None else cfg
    lineage = cfg["ymq4_lineage"]
    require(lineage["preserve_historical_ids"] is True, "YMQ4 IDs renumbered")
    require(lineage["ymq4_equals_mqe4_canon"] is False, "YMQ4 silently promoted to MQE4 Canon")
    require(lineage["b3"]["scientific_status"] == "SCIENTIFIC_NO_GO", "YMQ4-B3 NO-GO hidden")
    require(lineage["b3"]["economic_observation"] == "DYNAMIC_BETA_DOES_NOT_BEAT_B2", "YMQ4-B3 observation rewritten")
    require(lineage["b3"]["canon_authority"] == "NONE", "YMQ4-B3 Canon authority escalated")
    status = YIOS0_STATUS.read_text(encoding="utf-8")
    for token in ("YMQ4-B3", "SCIENTIFIC_NO_GO", "DYNAMIC_BETA_DOES_NOT_BEAT_B2", "PR #72"):
        require(token in status, f"repository-local YMQ4-B3 evidence missing: {token}")


def validate_non_authorizations(cfg: dict[str, Any] | None = None) -> None:
    cfg = load_json(CONFIG) if cfg is None else cfg
    for key in (
        "capital_authorized",
        "execution_authorized",
        "broker_authorized",
        "portfolio_sizing_authorized",
        "position_sizing_authorized",
        "order_submission_authorized",
        "real_capital_movement_authorized",
        "external_runtime_mutation_authorized",
    ):
        require(cfg["authority"][key] is False, f"authority escalated: {key}")
    for key, value in cfg["non_authorizations"].items():
        require(value is False, f"non-authorization escalated: {key}")


def validate_human_docs() -> None:
    for filename in DOC_FILES:
        require((ARCH_DIR / filename).exists(), f"missing Human architecture artifact: {filename}")
    joined = "\n".join((ARCH_DIR / name).read_text(encoding="utf-8") for name in DOC_FILES)
    for _, name in EXPECTED_ENGINES:
        require(name in joined, f"Human docs missing engine name: {name}")
    for obj in EXPECTED_OBJECTS:
        require(obj in joined, f"Human docs missing canonical object: {obj}")
    for token in (
        "Reality > Belief",
        "ResearchPass != CapitalPass",
        "UNKNOWN = DENY",
        "Receipt = Ledger; Status = Projection",
        "SCIENTIFIC_NO_GO",
        "DYNAMIC_BETA_DOES_NOT_BEAT_B2",
        "ACCEPT_YMQ_OS0_G0_MACHINE_QUALIFICATION",
        "AUTHORIZE_YMQ_OS0_G0_MERGE",
    ):
        require(token in joined, f"Human docs missing constitutional token: {token}")


def validate_all() -> None:
    validate_contract()
    bundle = positive_fixture_bundle()
    validate_schemas(bundle)
    validate_pit_relations(bundle)
    validate_claim_authority(bundle)
    validate_settlement_separation(bundle["settlement"])
    validate_learning_forward_only(bundle["learning"])
    require(bundle["learning"]["settlement_ref"] == bundle["settlement"]["settlement_id"], "LearningDelta settlement reference mismatch")
    require(bundle["settlement"]["run_refs"] == [bundle["run"]["run_id"]], "settlement/run reference mismatch")
    validate_human_docs()
    print("YMQ-OS0-G0 validator: PASS")


if __name__ == "__main__":
    validate_all()
