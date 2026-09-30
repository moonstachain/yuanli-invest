from __future__ import annotations

from dataclasses import dataclass

from yuanli_invest.context import CompiledContext


@dataclass(frozen=True)
class RouteDecision:
    allowed: bool
    reason: str
    granted_authority: str
    provider: str
