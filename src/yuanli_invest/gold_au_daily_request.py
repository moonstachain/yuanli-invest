"""Deterministic local evidence assembly for the 08:30 research worker.

No network, accounts, orders, calendar inference, or source receipt creation.
An offline candidate has only passed local content and capture-time checks;
it never authenticates an external witness or grants broker authority.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .gold_au_live_snapshot import SHANGHAI, prepare_live_snapshot
from .receipts import canonical_hash
from .time import instant

CATALOG_SCHEMA = "gold-au-daily-request-sources.v1"
MAX_RECEIPT_BYTES = 16_000_000
MAX_SHFE_MANIFESTS = 8
REQUIRED_PATHS = ("calendar_receipt_path", "h10_mapping_receipt_path", "cost_receipt_path")


def _receipt(path: Path, *, as_of: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read bounded JSON without exposing arbitrary source payloads in errors."""
    evidence: dict[str, Any] = {"path": str(path), "status": "INVALID"}
    try:
        if path.is_symlink() or not path.is_file():
            return {}, {**evidence, "reason": "MISSING_OR_SYMLINK_RECEIPT"}
        if path.stat().st_size > MAX_RECEIPT_BYTES:
            return {}, {**evidence, "reason": "OVERSIZED_RECEIPT"}
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeError, ValueError):
        return {}, {**evidence, "reason": "UNREADABLE_OR_INVALID_RECEIPT_JSON"}
    evidence["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    if not isinstance(value, dict):
        return {}, {**evidence, "reason": "RECEIPT_OBJECT_REQUIRED"}
    # Validate actual availability against the assembler's current timestamp,
    # before a hypothetical decision-time validation can consider these bytes.
    timestamps: list[Any] = []
    for key in ("captured_at", "witnessed_at"):
        if key in value:
            timestamps.append(value[key])
    for key in ("reports", "captures"):
        rows = value.get(key)
        if isinstance(rows, list):
            timestamps.extend(row["captured_at"] for row in rows
                              if isinstance(row, Mapping) and "captured_at" in row)
    for stamp in timestamps:
        try:
            captured = instant(stamp)
        except (TypeError, ValueError):
            return {}, {**evidence, "reason": "INVALID_SOURCE_AVAILABILITY_TIME"}
        if captured > as_of:
            return {}, {**evidence, "reason": "SOURCE_NOT_YET_AVAILABLE_AT_ASSEMBLY"}
    return value, {**evidence, "status": "LOCAL_BYTES_READ", "timing_fields_checked": len(timestamps)}


def assemble_daily_request(catalog: Any, *, runtime_dir: Path,
                           decision_date: str, as_of: datetime) -> dict[str, Any]:
    """Return complete missing evidence or a worker-compatible offline request.

    The explicit catalog names the source receipts. Macro evidence is *only*
    that day's existing ``macro_captures/YYYY-MM-DD/manifest.json``. Relative
    receipt paths are relative to the private runtime; no directories are
    scanned, and no newest-file or previous-day substitution is performed.
    """
    base: dict[str, Any] = {"schema_version": "gold-au-daily-request-assembly.v1",
                           "decision_date": decision_date, "status": "BLOCKED",
                           "broker_action_authorized": False,
                           "external_witness_authentication": "NOT_VERIFIED_BY_OFFLINE_MODULE"}
    try:
        day = date.fromisoformat(decision_date)
        if day.isoformat() != decision_date:
            raise ValueError
        if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError
        observed = as_of.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return {**base, "reason": "INVALID_DATE_OR_ASSEMBLY_TIME"}
    base["assembled_at"] = observed.isoformat()
    decision = datetime.combine(day, time(8, 30), SHANGHAI).astimezone(timezone.utc)
    base["decision_at"] = decision.isoformat()
    if not isinstance(catalog, Mapping) or catalog.get("schema_version") != CATALOG_SCHEMA:
        return {**base, "reason": "EXPLICIT_SOURCE_CATALOG_REQUIRED",
                "missing_inputs": [*REQUIRED_PATHS, "shfe_manifest_paths", "daily_fred_manifest"],
                "wgc_status": "UNKNOWN_RISK_BUDGET_HALVED"}
    try:
        base["source_catalog_sha256"] = canonical_hash(catalog)
        base["source_catalog_hash_basis"] = "CANONICAL_JSON_CONTENT"
    except (TypeError, ValueError, OverflowError):
        return {**base, "reason": "INVALID_SOURCE_CATALOG_CONTENT"}
    mode = catalog.get("execution_mode")
    if mode is not None and mode != "RESEARCH_ONLY":
        return {**base, "reason": "INVALID_EXPLICIT_EXECUTION_MODE"}
    research_only = mode == "RESEARCH_ONLY"
    base["execution_mode"] = "RESEARCH_ONLY" if research_only else "DEFAULT_COST_REQUIRED"
    base["execution_cost_status"] = ("NOT_USED_RESEARCH_ONLY_EXECUTION_REQUIRES_VERIFICATION"
                                      if research_only else "REQUIRED_BEFORE_CANDIDATE")
    root = runtime_dir.expanduser().absolute()
    request: dict[str, Any] = {"schema_version": "gold-au-live-snapshot-request.v1",
                               "decision_date": decision_date}
    if research_only:
        request["execution_mode"] = "RESEARCH_ONLY"
    inventory: dict[str, Any] = {}

    def read_field(key: str, name: Any) -> None:
        if not isinstance(name, str) or not name.strip():
            inventory[key] = {"status": "MISSING", "reason": "EXPLICIT_RECEIPT_PATH_REQUIRED"}
            return
        name = name.replace("{decision_date}", decision_date)
        if "{" in name or "}" in name:
            inventory[key] = {"status": "INVALID", "reason": "UNSUPPORTED_SOURCE_PATH_TEMPLATE"}
            return
        path = Path(name).expanduser()
        if not path.is_absolute():
            path = root / path
        _, proof = _receipt(path, as_of=observed)
        inventory[key] = proof
        if proof["status"] == "LOCAL_BYTES_READ":
            request[key] = str(path.absolute())

    for key in REQUIRED_PATHS:
        if key != "cost_receipt_path" or not research_only:
            read_field(key, catalog.get(key))
    macro = root / "macro_captures" / decision_date / "manifest.json"
    read_field("fred_manifest_path", str(macro))
    names = catalog.get("shfe_manifest_paths")
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_SHFE_MANIFESTS:
        inventory["shfe_manifest_paths"] = {"status": "MISSING", "reason": "BOUNDED_EXPLICIT_SHFE_ARCHIVE_REQUIRED"}
    else:
        manifest_paths = []
        seen = set()
        for i, name in enumerate(names):
            key = "shfe_manifest_" + str(i)
            read_field(key, name)
            selected = request.pop(key, None)
            if selected is not None:
                resolved = str(Path(selected).resolve())
                if resolved in seen:
                    inventory[key] = {**inventory[key], "status": "INVALID", "reason": "DUPLICATE_SHFE_MANIFEST"}
                seen.add(resolved)
                manifest_paths.append(selected)
        if all(inventory["shfe_manifest_" + str(i)]["status"] == "LOCAL_BYTES_READ" for i in range(len(names))):
            request["shfe_manifest_paths"] = manifest_paths
    wgc = catalog.get("wgc_receipt_path")
    base["wgc_status"] = "UNKNOWN_RISK_BUDGET_HALVED"
    if wgc is not None:
        read_field("wgc_receipt_path", wgc)
        base["wgc_status"] = "LOCAL_RECEIPT_SUPPLIED_NOT_AUTHENTICATED"
    base["source_inventory"] = inventory
    unavailable = [key for key, proof in inventory.items() if proof["status"] != "LOCAL_BYTES_READ"]
    if unavailable:
        return {**base, "reason": "MISSING_OR_INVALID_PROOF_INPUTS", "missing_inputs": unavailable}
    local = observed.astimezone(SHANGHAI)
    if local.date() != day or not time(8, 10) <= local.time().replace(tzinfo=None) <= time(8, 30):
        return {**base, "reason": "OUTSIDE_0810_0830_ASSEMBLY_WINDOW"}
    # This evaluates an offline candidate at the frozen decision time after
    # separately rejecting any source bytes not available at actual assembly.
    # The live worker must re-read/revalidate the sources at 08:30 itself.
    try:
        validation = prepare_live_snapshot(request, as_of=decision)
    except (OSError, TypeError, ValueError, KeyError, AttributeError, OverflowError):
        return {**base, "reason": "MALFORMED_SOURCE_REJECTED_BY_SNAPSHOT_VALIDATOR"}
    if validation.get("status") != "READY_STRICT_RESEARCH_SIGNAL":
        return {**base, "reason": validation.get("reason", "OFFLINE_SNAPSHOT_NOT_READY"),
                "offline_validation_status": validation.get("status")}
    for key, proof in inventory.items():
        _, checked = _receipt(Path(proof["path"]), as_of=observed)
        if checked.get("status") != "LOCAL_BYTES_READ" or checked.get("receipt_sha256") != proof["receipt_sha256"]:
            return {**base, "reason": "SOURCE_CHANGED_DURING_ASSEMBLY", "changed_input": key}
    request["assembly_source_receipts"] = [
        {"path": proof["path"], "receipt_sha256": proof["receipt_sha256"]}
        for proof in inventory.values()
    ]
    request["request_source_status"] = "OFFLINE_CANDIDATE_REQUIRES_0830_REVALIDATION"
    return {**base, "status": "READY_OFFLINE_CANDIDATE", "reason": "LOCAL_CONTENT_AND_CAPTURE_BOUND_CHECKS_PASSED",
            "offline_validation_at": decision.isoformat(), "request": request,
            "request_sha256": canonical_hash(request),
            "dataset_sha256_candidate": validation["dataset_sha256"],
            "decision_frozen": False, "worker_revalidation_required": True}
