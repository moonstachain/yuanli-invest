"""Publish immutable dated receipts and an atomically replaced latest snapshot."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def _atomic_write(target: Path, text: str) -> None:
    descriptor, name = tempfile.mkstemp(dir=target.parent, prefix=".receipt-")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def write_receipt(
    receipt: Mapping[str, Any],
    runtime_root: Path,
    *,
    prefix: str = "receipt",
    latest_name: str = "latest.json",
) -> Path:
    """Keep each run, exposing only complete JSON files to concurrent readers."""
    day = date.fromisoformat(str(receipt.get("as_of") or date.today().isoformat()))
    daily = runtime_root / day.isoformat()
    text = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    daily.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    target = daily / f"{prefix}-{stamp}-{uuid4().hex}.json"
    _atomic_write(target, text)
    _atomic_write(runtime_root / latest_name, text)
    return target
