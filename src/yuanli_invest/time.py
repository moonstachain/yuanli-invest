"""Explicit timezone-aware timestamps at research input boundaries."""

from datetime import datetime, timezone


def instant(value: str | datetime) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("invalid timestamp") from exc
    if not isinstance(value, datetime):
        raise ValueError("time must be an explicit timestamp")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone is required")
    return value.astimezone(timezone.utc)
