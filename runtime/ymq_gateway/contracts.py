from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CompiledContext:
    as_of: datetime
    evidence_refs: tuple[str, ...]
    denied_refs: tuple[str, ...]
    items: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class RouteDecision:
    allowed: bool
    reason: str
    granted_authority: str
    provider: str
