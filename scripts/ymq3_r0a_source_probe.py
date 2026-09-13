from __future__ import annotations

from datetime import datetime
import re
from typing import Any

RIGHTS_AXES = [
    "processing_authority",
    "raw_storage_authority",
    "derived_feature_storage_authority",
    "redistribution_authority",
]
REQUIRED_RECEIPT_FIELDS = [
    "run_id",
    "source_id",
    "probe_locator",
    "observed_at",
    "provider_status",
    "sample_historical_locator",
    "sample_publication_timestamp",
    "sample_available_at",
    "sample_archive_capture_at",
    "sample_retrieved_at",
    "historical_range_observed",
    "machine_access_observed",
    "terms_locator_observed",
    "rights_verdict_observed",
    "content_or_metadata_hash",
    "notes",
]
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_optional_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(dt.tzinfo is not None, f"timestamp must be timezone-aware: {value}")
    return dt


def rights_verdict(source_record: dict[str, Any]) -> str:
    values = [source_record.get(axis, "UNKNOWN") for axis in RIGHTS_AXES]
    require(all(v in {"ALLOW", "DENY", "UNKNOWN"} for v in values), "invalid source rights value")
    processing = source_record.get("processing_authority", "UNKNOWN")
    if processing == "DENY":
        return "DENY"
    if processing == "UNKNOWN":
        return "UNKNOWN_DENY"
    if any(v == "UNKNOWN" for v in values[1:]):
        return "PROCESSING_ONLY_BOUNDARIES_UNRESOLVED"
    if any(v == "DENY" for v in values[1:]):
        return "PROCESSING_ALLOWED_STORAGE_OR_REDISTRIBUTION_BOUNDED"
    return "ALLOW_FOR_DECLARED_ROLE"


def build_probe_receipt(source_record: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    require(bool(source_record.get("source_id")), "source_id required")
    receipt = {
        "run_id": observed.get("run_id"),
        "source_id": source_record["source_id"],
        "probe_locator": observed.get("probe_locator"),
        "observed_at": observed.get("observed_at"),
        "provider_status": observed.get("provider_status"),
        "sample_historical_locator": observed.get("sample_historical_locator"),
        "sample_publication_timestamp": observed.get("sample_publication_timestamp"),
        "sample_available_at": observed.get("sample_available_at"),
        "sample_archive_capture_at": observed.get("sample_archive_capture_at"),
        "sample_retrieved_at": observed.get("sample_retrieved_at", observed.get("observed_at")),
        "historical_range_observed": observed.get("historical_range_observed"),
        "machine_access_observed": observed.get("machine_access_observed"),
        "terms_locator_observed": observed.get("terms_locator_observed"),
        "rights_verdict_observed": rights_verdict(source_record),
        "content_or_metadata_hash": observed.get("content_or_metadata_hash"),
        "notes": observed.get("notes", ""),
    }
    validate_probe_receipt(receipt)
    return receipt


def validate_probe_receipt(receipt: dict[str, Any]) -> None:
    for field in REQUIRED_RECEIPT_FIELDS:
        require(field in receipt, f"missing receipt field: {field}")
    require(bool(receipt["run_id"]), "run_id required")
    require(bool(receipt["source_id"]), "source_id required")
    require(bool(receipt["probe_locator"]), "probe_locator required")
    require(bool(receipt["provider_status"]), "provider_status required")
    require(bool(receipt["machine_access_observed"]), "machine access observation required")
    require(receipt["rights_verdict_observed"] in {
        "DENY",
        "UNKNOWN_DENY",
        "PROCESSING_ONLY_BOUNDARIES_UNRESOLVED",
        "PROCESSING_ALLOWED_STORAGE_OR_REDISTRIBUTION_BOUNDED",
        "ALLOW_FOR_DECLARED_ROLE",
    }, "invalid rights verdict")
    require(isinstance(receipt["content_or_metadata_hash"], str) and HASH_RE.fullmatch(receipt["content_or_metadata_hash"]) is not None, "invalid sha256 hash")

    observed = parse_optional_time(receipt["observed_at"])
    publication = parse_optional_time(receipt["sample_publication_timestamp"])
    available = parse_optional_time(receipt["sample_available_at"])
    archive = parse_optional_time(receipt["sample_archive_capture_at"])
    retrieved = parse_optional_time(receipt["sample_retrieved_at"])
    require(observed is not None and retrieved is not None, "observed/retrieved clocks required")
    require(retrieved <= observed, "retrieved_at cannot be after observed_at")
    if publication is not None and available is not None:
        require(publication <= available, "available_at cannot precede publication timestamp")
    if publication is not None and archive is not None:
        require(publication <= archive, "archive capture cannot precede claimed publication timestamp")
    if available is not None and retrieved is not None:
        require(available <= retrieved, "retrieval cannot precede known availability")
