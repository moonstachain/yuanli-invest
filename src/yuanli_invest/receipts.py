"""A receipt is UTF-8 JSON bytes plus their SHA256, never a reserialized jsonb hash."""

import hashlib
import json
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def receipt_envelope(receipt: Any) -> dict[str, str]:
    payload = canonical_bytes(receipt)
    return {"receipt_json": payload.decode("utf-8"), "receipt_sha256": hashlib.sha256(payload).hexdigest()}


def read_envelope(envelope: dict[str, str]) -> Any:
    payload = envelope["receipt_json"].encode("utf-8")
    if hashlib.sha256(payload).hexdigest() != envelope["receipt_sha256"]:
        raise ValueError("receipt bytes do not match receipt_sha256")
    def invalid_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(payload, parse_constant=invalid_constant)
