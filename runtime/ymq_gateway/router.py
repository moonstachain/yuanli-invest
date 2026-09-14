from __future__ import annotations

from .contracts import RouteDecision

FORBIDDEN_INTENTS = {"position_sizing", "broker_order", "real_capital_move"}
DENIED_EVIDENCE = {"UNKNOWN", "DENY", "BLOCKED", None}


def route_request(
    *,
    intent: str,
    requested_authority: str,
    evidence_status: str | None,
    provider: str,
) -> RouteDecision:
    if evidence_status in DENIED_EVIDENCE:
        return RouteDecision(False, "UNKNOWN_DENY", "NONE", provider)
    if intent in FORBIDDEN_INTENTS or requested_authority in {"CAPITAL", "EXECUTION"}:
        return RouteDecision(False, "AUTHORITY_DENY", "NONE", provider)
    if requested_authority != "RESEARCH":
        return RouteDecision(False, "AUTHORITY_DENY", "NONE", provider)
    return RouteDecision(True, "RESEARCH_ONLY", "RESEARCH", provider)
