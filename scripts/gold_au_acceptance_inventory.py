#!/usr/bin/env python3
"""Read-only evidence inventory. Never grants execution or starts observation.

Matching file bytes verifies artifact integrity, not producer identity. A local
matrix cannot authenticate SimNow, four independent parties or an expert.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

REQUIRED_CASES = frozenset({
    "natural0830", "readonly_connection", "native_python312", "identity_and_cost",
    "independent_four_way", "linked_protective_exit", "engineering_round_trip",
    "daily_settlement", "expert_review_1", "expert_review_2", "concurrency",
})


def inspect(matrix_path: Path, *, observed_at: datetime | None = None) -> dict:
    now = observed_at or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("AWARE_INVENTORY_CLOCK_REQUIRED")
    raw = matrix_path.read_bytes()
    matrix = json.loads(raw)
    if (not isinstance(matrix, dict)
            or matrix.get("schema_version") != "gold-au-engineering-acceptance-matrix.v1"
            or not isinstance(matrix.get("items"), list)):
        raise ValueError("INVALID_ACCEPTANCE_MATRIX")
    indexed = {}
    for row in matrix["items"]:
        if not isinstance(row, dict) or row.get("case_id") not in REQUIRED_CASES:
            raise ValueError("UNKNOWN_ACCEPTANCE_CASE")
        if row["case_id"] in indexed:
            raise ValueError("DUPLICATE_ACCEPTANCE_CASE")
        indexed[row["case_id"]] = row
    rows = []
    for case in sorted(REQUIRED_CASES):
        row = indexed.get(case)
        status = "MISSING_CASE"
        digest = None
        if row is not None:
            status = "ACTUAL_EVIDENCE_NOT_PROVIDED"
            if row.get("kind") != "ACTUAL_REQUIRED":
                status = "REHEARSAL_OR_CANDIDATE_NOT_ACTUAL"
            elif row.get("status") == "PASS":
                status = "INVALID_ACTUAL_RECEIPT"
                ref, expected, stamp = (row.get(k) for k in
                    ("evidence_ref", "evidence_sha256", "evidence_observed_at"))
                if isinstance(ref, str) and isinstance(expected, str) and isinstance(stamp, str):
                    try:
                        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                        path = Path(ref)
                        if not path.is_absolute():
                            raise ValueError("ABSOLUTE_RECEIPT_PATH_REQUIRED")
                        if path.is_symlink() or not path.is_file() or path.stat().st_size > 16_000_000:
                            raise ValueError("BOUNDED_REAL_RECEIPT_REQUIRED")
                        if when.tzinfo is None or when.utcoffset() is None or when > now:
                            raise ValueError("ACTUAL_RECEIPT_FUTURE_OR_NAIVE")
                        payload = path.read_bytes()
                        digest = "sha256:" + hashlib.sha256(payload).hexdigest()
                        if digest != expected:
                            raise ValueError("RECEIPT_HASH_MISMATCH")
                        fact = json.loads(payload)
                        if not isinstance(fact, dict):
                            raise ValueError("JSON_RECEIPT_OBJECT_REQUIRED")
                        if (fact.get("kind") in {"REHEARSAL", "REHEARSAL_ONLY", "SYNTHETIC"}
                                or str(fact.get("status", "")).startswith("REHEARSAL")):
                            raise ValueError("REHEARSAL_CANNOT_SATISFY_ACTUAL_CASE")
                        identity = row.get("identity")
                        if (not isinstance(identity, dict)
                                or identity.get("environment") != "SIMNOW_FIRST_NORMAL"):
                            raise ValueError("PAPER_ENVIRONMENT_REQUIRED")
                        if case not in {"natural0830", "expert_review_1", "expert_review_2", "concurrency", "native_python312"}:
                            if not identity.get("account_id") or not identity.get("robot_id"):
                                raise ValueError("REAL_ACCOUNT_ROBOT_IDENTITY_REQUIRED")
                        status = "ARTIFACT_INTEGRITY_CHECKED_IDENTITY_NOT_AUTHENTICATED"
                    except (OSError, ValueError, TypeError):
                        status = "INVALID_ACTUAL_RECEIPT"
        rows.append({"case_id": case, "status": status, "readback_sha256": digest})
    return {
        "schema_version": "gold-au-acceptance-inventory.v1",
        "observed_at": now.astimezone(timezone.utc).isoformat(),
        "matrix_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "items": rows,
        "actual_evidence_missing_or_invalid": sum(r["status"] !=
            "ARTIFACT_INTEGRITY_CHECKED_IDENTITY_NOT_AUTHENTICATED" for r in rows),
        "authority": "READ_ONLY_ARTIFACT_INVENTORY",
        "producer_identity_authenticated": False,
        "observation_start_authorized": False,
        "broker_action_authorized": False,
        "non_claims": ["No local matrix, hash or PASS label establishes independent source identity",
                       "No engineering fill, settlement or expert review is inferred",
                       "Observation start still requires separate verified operational admission"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.matrix)
    encoded = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as target:
        target.write(encoded)
    print(json.dumps({"status": "READ_ONLY_INVENTORY_WRITTEN", "missing_or_invalid":
        result["actual_evidence_missing_or_invalid"], "broker_action_authorized": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
