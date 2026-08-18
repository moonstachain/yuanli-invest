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
        validated += 1
    print(f"schemas={len(schemas)} objects={validated} status=valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed in CI
        print(f"validation_error: {exc}", file=sys.stderr)
        raise SystemExit(1)
