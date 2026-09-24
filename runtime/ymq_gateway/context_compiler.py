from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .contracts import CompiledContext

ADMITTED_STATUSES = {"PASS", "LIMITED"}


def _parse_time(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compile_context(
    *,
    as_of: datetime,
    evidence_rows: Iterable[dict[str, Any]],
    max_items: int = 20,
) -> CompiledContext:
    if max_items < 1:
        raise ValueError("max_items must be >= 1")

    admitted: list[dict[str, Any]] = []
    denied: list[str] = []
    for row in evidence_rows:
        ref = str(row["evidence_ref"])
        known_as_of = _parse_time(row["known_as_of"])
        status = str(row.get("status", "UNKNOWN"))
        authority = str(row.get("authority", "NONE"))
        if known_as_of > as_of or status not in ADMITTED_STATUSES or authority == "NONE":
            denied.append(ref)
            continue
        if len(admitted) < max_items:
            admitted.append(row)

    return CompiledContext(
        as_of=as_of,
        evidence_refs=tuple(str(row["evidence_ref"]) for row in admitted),
        denied_refs=tuple(denied),
        items=tuple(admitted),
    )
