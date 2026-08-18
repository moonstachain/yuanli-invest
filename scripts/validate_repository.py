#!/usr/bin/env python3
"""Validate Yuanli Invest schemas and versioned research objects."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas"

OBJECT_SCHEMAS = {
    "Narrative": "narrative",
    "Observation": "observation",
    "Evidence": "evidence",
    "StageSnapshot": "stage-snapshot",
    "ParadigmSnapshot": "paradigm-snapshot",
    "ConvexityProfile": "convexity-profile",
    "ForceTriangleSnapshot": "force-triangle-snapshot",
    "AssetMapping": "asset-mapping",
    "Thesis": "thesis",
    "ScoreSnapshot": "score-snapshot",
    "CompanyMaster": "company-master",
    "MarketSnapshot": "market-snapshot",
    "AnalystObservation": "analyst-observation",
    "BriefSnapshot": "brief-snapshot",
    "SourceRecord": "source-record",
    "ResearchEvent": "research-event",
    "Outcome": "outcome",
    "LearningCandidate": "learning-candidate",
    "ReleaseManifest": "release-manifest",
    "Replay": "replay",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_registry():
    schemas: dict[str, dict] = {}
    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        schema_id = schema.get("$id", "")
        if not schema_id.startswith("urn:yuanli-invest:schema:"):
            raise ValueError(f"{path}: unstable schema id {schema_id!r}")
        if schema_id in schemas:
            raise ValueError(f"duplicate schema id: {schema_id}")
        schemas[schema_id] = schema
        registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return schemas, registry


def iter_object_files():
    for base in (ROOT / "canon", ROOT / "events"):
        if not base.exists():
            continue
        yield from sorted(path for path in base.rglob("*.json") if path.is_file())


def main() -> int:
    schemas, registry = schema_registry()
    seen: set[tuple[str, str]] = set()
    objects: list[tuple[Path, dict]] = []
    object_by_id: dict[str, dict] = {}
    validated = 0
    for path in iter_object_files():
        instance = load_json(path)
        object_type = instance.get("object_type")
        schema_name = OBJECT_SCHEMAS.get(object_type)
        if not schema_name:
            raise ValueError(f"{path}: unknown object_type {object_type!r}")
        schema_id = f"urn:yuanli-invest:schema:{schema_name}:1.0.0"
        validator = Draft202012Validator(
            schemas[schema_id], registry=registry, format_checker=FormatChecker()
        )
        errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(error.message for error in errors[:10])
            raise ValueError(f"{path}: {detail}")
        identity = (instance["id"], instance["version"])
        if identity in seen:
            raise ValueError(f"duplicate object version: {identity}")
        seen.add(identity)
        objects.append((path, instance))
        current = object_by_id.get(instance["id"])
        if current and current["object_type"] != "ResearchEvent" and instance["object_type"] != "ResearchEvent":
            raise ValueError(f"duplicate object id across types: {instance['id']}")
        object_by_id[instance["id"]] = instance
        validated += 1

    evidence_ids = {item["id"] for _, item in objects if item["object_type"] == "Evidence"}
    narrative_ids = {item["id"] for _, item in objects if item["object_type"] == "Narrative"}
    company_ids = {item["id"] for _, item in objects if item["object_type"] == "CompanyMaster"}
    source_record_ids = {item["id"] for _, item in objects if item["object_type"] == "SourceRecord"}
    subject_ids = {item["id"] for _, item in objects if item["object_type"] != "ResearchEvent"}

    tickers: set[tuple[str, str]] = set()
    for path, item in objects:
        for field in ("evidence_ids", "counter_evidence_ids", "identity_evidence_ids"):
            missing = set(item.get(field, [])) - evidence_ids
            if missing:
                raise ValueError(f"{path}: missing {field} references {sorted(missing)}")
        if "narrative_id" in item and item["narrative_id"] not in narrative_ids:
            raise ValueError(f"{path}: missing narrative {item['narrative_id']}")
        if "company_id" in item and item["company_id"] is not None and item["company_id"] not in company_ids:
            raise ValueError(f"{path}: missing company {item['company_id']}")
        if "source_record_id" in item and item["source_record_id"] not in source_record_ids:
            raise ValueError(f"{path}: missing source record {item['source_record_id']}")
        if item["object_type"] == "ResearchEvent" and item["subject_id"] not in subject_ids:
            raise ValueError(f"{path}: missing event subject {item['subject_id']}")
        if item["object_type"] == "CompanyMaster":
            identity = (item["exchange"], item["ticker"])
            if identity in tickers:
                raise ValueError(f"duplicate company identity: {identity}")
            tickers.add(identity)
    print(f"schemas={len(schemas)} objects={validated} status=valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed in CI
        print(f"validation_error: {exc}", file=sys.stderr)
        raise SystemExit(1)
