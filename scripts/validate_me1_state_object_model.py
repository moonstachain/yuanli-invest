#!/usr/bin/env python3
"""Fail-closed validation for ME1 multi-thesis state object model."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
ME1 = ROOT / "docs" / "architecture" / "me1"
FIXTURES = ME1 / "fixtures"
SUCCESSOR_MAP = ME1 / "ME1-SEMANTIC-SUCCESSOR-MAP-v0.1.json"

GENESIS_ENGINES = {"ENG-C", "ENG-R", "ENG-X"}
BOOK_ENGINE = {"BOOK-C": "ENG-C", "BOOK-R": "ENG-R", "BOOK-X": "ENG-X"}
SCHEMAS = {
    "targets": VNEXT / "research-target-v2.schema.json",
    "theses": VNEXT / "engine-thesis.schema.json",
    "passports": VNEXT / "position-passport.schema.json",
    "books": VNEXT / "book-state.schema.json",
    "projections": VNEXT / "legacy-rsv-projection.schema.json",
    "legacy_read_models": VNEXT / "legacy-rsv-read-model.schema.json",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_historical_non_regression() -> None:
    v1 = load_json(VNEXT / "research-target.schema.json")
    require(v1["$id"] == "urn:yuanli-invest:schema:vnext-research-target:1.0.0", "ResearchTarget v1 identity regressed")
    require(v1["required"] == ["target_type", "target_id", "display_name"], "ResearchTarget v1 semantics regressed")
    rsv = load_json(VNEXT / "research-state-vector.schema.json")
    require(rsv["$id"] == "urn:yuanli-invest:schema:vnext-research-state-vector:1.0.0", "RSV identity regressed")


def validate_historical_successor_policy(bundle: dict) -> None:
    historical = bundle["successor_map"]["historical_identities"]
    by_id = {item["schema_id"]: item for item in historical}
    v1 = by_id["urn:yuanli-invest:schema:vnext-research-target:1.0.0"]
    rsv = by_id["urn:yuanli-invest:schema:vnext-research-state-vector:1.0.0"]
    require(v1.get("redefined_in_place") is False, "ResearchTarget v1 cannot be redefined in place")
    require(v1.get("future_write_authority") is False, "ResearchTarget v1 cannot gain future write authority")
    require(v1.get("successor_schema_id") == "urn:yuanli-invest:schema:vnext-research-target:2.0.0", "ResearchTarget v2 successor mismatch")
    require(rsv.get("redefined_in_place") is False, "RSV cannot be redefined in place")
    require(rsv.get("future_write_authority") is False, "RSV cannot gain future write authority")
    require(bundle["successor_map"].get("next_me_stage_authorized") is False, "ME1 cannot authorize successor stages")


def validate_local_schemas() -> None:
    for path in SCHEMAS.values():
        Draft202012Validator.check_schema(load_json(path))


def _validate_instance(schema: dict, instance: dict, label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(error.message for error in errors[:8])
        raise ValueError(f"{label}: {detail}")


def validate_bundle_shapes(bundle: dict) -> None:
    validate_local_schemas()
    for key, path in SCHEMAS.items():
        schema = load_json(path)
        for index, instance in enumerate(bundle.get(key, [])):
            _validate_instance(schema, instance, f"{key}[{index}]")


def validate_identity_integrity(bundle: dict) -> None:
    id_fields = {
        "targets": "target_id",
        "theses": "engine_thesis_id",
        "passports": "position_passport_id",
        "books": "book_state_id",
        "projections": "legacy_projection_id",
        "legacy_read_models": "legacy_read_model_id",
    }
    for key, field in id_fields.items():
        values = [item[field] for item in bundle.get(key, [])]
        require(len(values) == len(set(values)), f"duplicate {field}")

    occupied: set[tuple[str, str, str]] = set()
    for book in bundle.get("books", []):
        namespace = book.get("portfolio_namespace")
        as_of = book.get("as_of")
        for membership in book.get("memberships", []):
            passport_id = membership.get("position_passport_id")
            if membership.get("membership_role") != "primary" or not passport_id:
                continue
            identity = (namespace, as_of, passport_id)
            require(identity not in occupied, "PositionPassport occupies multiple primary Books in same namespace/as-of")
            occupied.add(identity)


def validate_reference_integrity(bundle: dict) -> None:
    target_ids = {item["target_id"] for item in bundle["targets"]}
    thesis_by_id = {item["engine_thesis_id"]: item for item in bundle["theses"]}
    passport_ids = {item["position_passport_id"] for item in bundle["passports"]}
    for thesis in bundle["theses"]:
        require(thesis["target_id"] in target_ids, "Thesis references missing ResearchTarget v2")
    for passport in bundle["passports"]:
        require(passport["engine_thesis_id"] in thesis_by_id, "Passport references missing EngineThesis")
    for book in bundle["books"]:
        for membership in book["memberships"]:
            passport_id = membership.get("position_passport_id")
            if passport_id:
                require(passport_id in passport_ids, "Book membership references missing Passport")
    for projection in bundle["projections"]:
        require(projection["target_ref"] in target_ids, "Legacy projection references missing ResearchTarget v2")


def validate_engine_consistency(bundle: dict) -> None:
    thesis_by_id = {item["engine_thesis_id"]: item for item in bundle["theses"]}
    passport_by_id = {item["position_passport_id"]: item for item in bundle["passports"]}

    for thesis in bundle["theses"]:
        core = thesis["identity_core"]
        engine = core["primary_engine"]
        require(engine != "ENG-CASH", "Cash cannot be a return engine")
        if engine not in GENESIS_ENGINES:
            require(bool(core.get("engine_authority_ref")), "unknown engine requires governed authority reference")

    for passport in bundle["passports"]:
        thesis = thesis_by_id[passport["engine_thesis_id"]]
        require(passport["target_id"] == thesis["target_id"], "Passport target mismatch")
        require(passport["primary_engine"] == thesis["identity_core"]["primary_engine"], "Passport engine mismatch")
        require(passport["primary_engine"] != "ENG-CASH", "Cash cannot be a Passport engine")

    for book in bundle["books"]:
        if book["book_id"] == "BOOK-CASH":
            for membership in book["memberships"]:
                require(not membership.get("position_passport_id"), "BOOK-CASH cannot contain engine Passport")
                require(bool(membership.get("liquidity_reserve_record")), "BOOK-CASH requires liquidity reserve record")
            continue
        expected = BOOK_ENGINE[book["book_id"]]
        for membership in book["memberships"]:
            passport_id = membership.get("position_passport_id")
            require(bool(passport_id), "engine Book membership requires PositionPassport")
            require(passport_by_id[passport_id]["primary_engine"] == expected, "Book contains wrong-engine Passport")


def validate_lifecycle_consistency(bundle: dict) -> None:
    target_by_id = {item["target_id"]: item for item in bundle["targets"]}
    thesis_by_id = {item["engine_thesis_id"]: item for item in bundle["theses"]}

    for thesis in bundle["theses"]:
        status = thesis["lifecycle"]["status"]
        falsification = thesis["falsification"]
        evidence = thesis["evidence"]
        if status in {"qualified", "active", "challenged"}:
            require(bool(falsification.get("falsifier_refs")), f"{status} Thesis requires falsifier")
        if status == "active":
            require(bool(evidence.get("supporting_refs")), "active Thesis requires evidence")
        if status == "invalidated":
            require(bool(falsification.get("invalidation_reason")), "invalidated Thesis requires reason")
            require(bool(falsification.get("triggered_falsifier_refs")), "invalidated Thesis requires triggered falsifier")
        if status == "settled":
            require(bool(thesis["lifecycle"].get("settlement_ref")), "settled Thesis requires settlement_ref")
        target = target_by_id[thesis["target_id"]]
        require(target["active_status"] != "archived", "archived Target cannot receive new Thesis")

    for passport in bundle["passports"]:
        thesis = thesis_by_id[passport["engine_thesis_id"]]
        if thesis["lifecycle"]["status"] == "invalidated":
            require(passport["lifecycle"]["status"] not in {"active", "eligible"}, "invalidated Thesis cannot create/retain active capital expression")

    for history in bundle.get("thesis_histories", {}).values():
        ordered = sorted(history, key=lambda item: item["lifecycle"]["revision"])
        settled_seen = False
        for item in ordered:
            if settled_seen:
                raise ValueError("settled Thesis cannot receive a later revision")
            if item["lifecycle"]["status"] == "settled":
                settled_seen = True


def validate_no_silent_migration(bundle: dict) -> None:
    for thesis_id, history in bundle.get("thesis_histories", {}).items():
        ordered = sorted(history, key=lambda item: item["lifecycle"]["revision"])
        if not ordered:
            continue
        baseline = ordered[0]
        immutable = {
            "target_id": baseline["target_id"],
            "primary_engine": baseline["identity_core"]["primary_engine"],
            "thesis_origin": baseline["identity_core"]["thesis_origin"],
            "opened_at": baseline["identity_core"]["opened_at"],
        }
        for item in ordered[1:]:
            require(item["target_id"] == immutable["target_id"], f"{thesis_id}: target migration prohibited")
            require(item["identity_core"]["primary_engine"] == immutable["primary_engine"], f"{thesis_id}: primary engine migration prohibited")
            require(item["identity_core"]["thesis_origin"] == immutable["thesis_origin"], f"{thesis_id}: thesis origin mutation prohibited")
            require(item["identity_core"]["opened_at"] == immutable["opened_at"], f"{thesis_id}: opened_at mutation prohibited")


def validate_pit_integrity(bundle: dict) -> None:
    for thesis in bundle["theses"]:
        lifecycle = thesis["lifecycle"]
        require(parse_dt(lifecycle["valid_from"]) <= parse_dt(lifecycle["as_of"]), "valid_from exceeds as_of")
        evidence = thesis["evidence"]
        recorded = evidence.get("recorded_at")
        known = evidence.get("known_as_of")
        cutoff = evidence.get("knowledge_cutoff")
        replay = evidence.get("replay_cutoff")
        if recorded and not known:
            raise ValueError("recorded_at cannot substitute for known_as_of")
        if cutoff or replay:
            require(bool(known and cutoff and replay), "PIT evidence requires known_as_of, knowledge_cutoff, replay_cutoff")
            require(parse_dt(known) <= parse_dt(cutoff) <= parse_dt(replay), "future knowledge contamination")


def _all_false(values: dict, label: str) -> None:
    require(values and all(value is False for value in values.values()), f"{label} authority regression")


def validate_authority_integrity(bundle: dict) -> None:
    for target in bundle["targets"]:
        _all_false(target["authority"], "ResearchTarget")
    for thesis in bundle["theses"]:
        _all_false(thesis["authority"], "EngineThesis")
    for passport in bundle["passports"]:
        _all_false(passport["authority"], "PositionPassport")
        require(passport["migration_policy"]["silent_migration_prohibited"] is True, "silent migration must be prohibited")
        require(passport["migration_policy"]["governed_event_required"] is True, "governed event required")
    for book in bundle["books"]:
        _all_false(book["authority"], "BookState")
    for projection in bundle["projections"]:
        require(projection.get("auto_engine_thesis_creation_authorized") is False, "Legacy RSV cannot auto-create EngineThesis")
        _all_false(projection["projection_authority"], "Legacy projection")
    for read_model in bundle["legacy_read_models"]:
        require(read_model["projection_only"] is True, "legacy read model must be projection-only")
        require(read_model["machine_authority"] is False, "legacy read model cannot have machine authority")
        require(read_model["write_back_prohibited"] is True, "legacy read model write-back must be prohibited")
    validate_historical_successor_policy(bundle)


def load_fixture_bundle() -> dict:
    bundle = {
        "targets": load_json(FIXTURES / "research-targets-v2.json"),
        "theses": load_json(FIXTURES / "engine-theses.json"),
        "passports": load_json(FIXTURES / "position-passports.json"),
        "books": load_json(FIXTURES / "book-states.json"),
        "projections": load_json(FIXTURES / "legacy-rsv-projections.json"),
        "legacy_read_models": [
            {
                "legacy_read_model_id": "LRM-NVDA-001",
                "schema_version": "1.0.0",
                "source_new_canon_refs": ["RT2-NVDA", "ET-NVDA-C-001"],
                "target_ref": "RT2-NVDA",
                "legacy_vector_view": {},
                "projection_only": True,
                "machine_authority": False,
                "write_back_prohibited": True,
            }
        ],
        "successor_map": load_json(SUCCESSOR_MAP),
        "thesis_histories": {},
    }
    return bundle


def main() -> int:
    validate_historical_non_regression()
    bundle = load_fixture_bundle()
    validate_bundle_shapes(bundle)
    validate_historical_successor_policy(bundle)
    validate_identity_integrity(bundle)
    validate_reference_integrity(bundle)
    validate_engine_consistency(bundle)
    validate_lifecycle_consistency(bundle)
    validate_no_silent_migration(bundle)
    validate_pit_integrity(bundle)
    validate_authority_integrity(bundle)
    print(f"targets={len(bundle['targets'])} theses={len(bundle['theses'])} passports={len(bundle['passports'])} state_model=valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
