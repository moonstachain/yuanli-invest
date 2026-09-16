from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from runtime.ymq_gateway.context_compiler import compile_context
from runtime.ymq_gateway.router import route_request

RESEARCH_AUTHORITY = "RESEARCH"
POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "yci0_rp0" / "context_pack_policy.v0.1.json"


class ContextPackError(ValueError):
    """Fail-closed RP0 Context Pack contract violation."""


@dataclass(frozen=True)
class ContextPack:
    context_pack_id: str
    question_id: str
    compiled_at: str
    as_of: str
    brain_snapshot_ref: str
    historical_analogues: tuple[dict[str, Any], ...]
    yuanli_patterns: tuple[dict[str, Any], ...]
    prior_judgments: tuple[dict[str, Any], ...]
    bottleneck_migration_patterns: tuple[dict[str, Any], ...]
    hard_negatives: tuple[dict[str, Any], ...]
    prior_learning_deltas: tuple[dict[str, Any], ...]
    recommended_capabilities: tuple[dict[str, Any], ...]
    freshness_summary: dict[str, Any]
    provenance_summary: dict[str, Any]
    context_hash: str
    authority: str = RESEARCH_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _contains_forbidden_key(value: Any) -> bool:
    forbidden = {
        "buy", "sell", "buy_authorization", "sell_authorization",
        "capital_authorization", "execution_authorization",
        "position_sizing", "broker_order", "real_capital_move",
    }
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in forbidden or _contains_forbidden_key(child):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(child) for child in value)
    return False


def _normalize_results(brain_results: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scope = str(brain_results.get("scope", "task_bounded")).lower()
    if scope in {str(v).lower() for v in policy["full_vault_scopes_denied"]}:
        raise ContextPackError("UNBOUNDED_CONTEXT_DENIED")

    allowed = tuple(policy["allowed_categories"])
    unknown = set(brain_results) - set(allowed) - {"scope"}
    if unknown:
        raise ContextPackError(f"UNKNOWN_CONTEXT_CATEGORY:{sorted(unknown)[0]}")

    raw_items: list[dict[str, Any]] = []
    for category in allowed:
        items = brain_results.get(category, [])
        if not isinstance(items, list):
            raise ContextPackError(f"CATEGORY_NOT_LIST:{category}")
        cap = int(policy["max_items_per_category"][category])
        if len(items) > cap:
            raise ContextPackError(f"CATEGORY_BUDGET_EXCEEDED:{category}")
        for item in items:
            if not isinstance(item, Mapping):
                raise ContextPackError(f"INVALID_CONTEXT_ITEM:{category}")
            row = dict(item)
            row["category"] = category
            raw_items.append(row)
    if len(raw_items) > int(policy["max_total_items"]):
        raise ContextPackError("TOTAL_CONTEXT_BUDGET_EXCEEDED")

    raw_items.sort(key=lambda x: (str(x.get("category", "")), str(x.get("item_id", ""))))
    admitted_rows: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    admitted_freshness = set(policy["admitted_freshness_states"])
    for item in raw_items:
        item_id = str(item.get("item_id") or "")
        provenance = item.get("provenance")
        freshness = item.get("freshness")
        reason = None
        if not item_id:
            raise ContextPackError("MISSING_ITEM_ID")
        if not isinstance(provenance, Mapping) or not provenance:
            raise ContextPackError(f"MISSING_PROVENANCE:{item_id}")
        if not isinstance(freshness, Mapping) or not freshness.get("state") or not freshness.get("as_of"):
            raise ContextPackError(f"MISSING_FRESHNESS:{item_id}")
        if _contains_forbidden_key(item):
            raise ContextPackError(f"FORBIDDEN_ACTION_FIELD:{item_id}")
        if str(item.get("authority", "NONE")) != RESEARCH_AUTHORITY:
            reason = "AUTHORITY_DENY"
        elif str(freshness.get("state")) not in admitted_freshness:
            reason = "STALE_OR_UNPROVEN"
        elif str(item.get("evidence_status", "UNKNOWN")) not in {"PASS", "LIMITED"}:
            reason = "EVIDENCE_NOT_ADMITTED"
        if reason:
            blocked.append({"item_id": item_id or "UNKNOWN", "reason": reason})
            continue
        admitted_rows.append({
            "evidence_ref": item_id,
            "known_as_of": str(freshness["as_of"]),
            "status": str(item["evidence_status"]),
            "authority": RESEARCH_AUTHORITY,
            "payload": item,
        })
    return admitted_rows, blocked


def build_context_pack(question: Mapping[str, Any], brain_results: Mapping[str, Any]) -> ContextPack:
    policy = _load_policy()
    if policy.get("authority") != RESEARCH_AUTHORITY:
        raise ContextPackError("POLICY_AUTHORITY_INVALID")
    question_id = str(question.get("question_id") or "")
    as_of = str(question.get("as_of") or "")
    snapshot = str(question.get("brain_snapshot_ref") or "")
    if not question_id or not as_of or not snapshot:
        raise ContextPackError("QUESTION_CONTEXT_FIELDS_REQUIRED")

    decision = route_request(
        intent=str(question.get("intent", "research")),
        requested_authority=str(question.get("authority", "NONE")),
        evidence_status=question.get("evidence_status"),
        provider=str(policy["provider"]),
    )
    if not decision.allowed or decision.granted_authority != RESEARCH_AUTHORITY:
        raise ContextPackError(decision.reason)

    admitted_rows, blocked = _normalize_results(brain_results, policy)
    compiled = compile_context(
        as_of=_parse_time(as_of),
        evidence_rows=admitted_rows,
        max_items=max(1, int(policy["max_total_items"])),
    )
    admitted_ids = set(compiled.evidence_refs)
    admitted_items = [row["payload"] for row in admitted_rows if row["evidence_ref"] in admitted_ids]
    for denied in compiled.denied_refs:
        blocked.append({"item_id": denied, "reason": "GATEWAY_CONTEXT_DENY"})

    categorized: dict[str, tuple[dict[str, Any], ...]] = {}
    for category in policy["allowed_categories"]:
        categorized[category] = tuple(
            item for item in admitted_items if item.get("category") == category
        )

    source_ids = sorted({
        str(item["provenance"].get("source_id"))
        for item in admitted_items
        if item.get("provenance", {}).get("source_id")
    })
    blocked = sorted(blocked, key=lambda x: (x["item_id"], x["reason"]))
    freshness_summary = {
        "admitted_count": len(admitted_items),
        "blocked_count": len(blocked),
        "blocked_item_ids": [entry["item_id"] for entry in blocked],
        "blocked_reasons": blocked,
    }
    provenance_summary = {
        "brain_snapshot_ref": snapshot,
        "source_ids": source_ids,
        "all_emitted_items_have_provenance": all(bool(item.get("provenance")) for item in admitted_items),
    }
    hash_payload = {
        "question_id": question_id,
        "as_of": as_of,
        "brain_snapshot_ref": snapshot,
        "categories": {category: categorized[category] for category in policy["allowed_categories"]},
        "freshness_summary": freshness_summary,
        "provenance_summary": provenance_summary,
        "authority": RESEARCH_AUTHORITY,
    }
    context_hash = _canonical_hash(hash_payload)
    return ContextPack(
        context_pack_id=f"YCI0-RP0-CTX-{context_hash[:16]}",
        question_id=question_id,
        compiled_at=as_of,
        as_of=as_of,
        brain_snapshot_ref=snapshot,
        historical_analogues=categorized["historical_analogues"],
        yuanli_patterns=categorized["yuanli_patterns"],
        prior_judgments=categorized["prior_judgments"],
        bottleneck_migration_patterns=categorized["bottleneck_migration_patterns"],
        hard_negatives=categorized["hard_negatives"],
        prior_learning_deltas=categorized["prior_learning_deltas"],
        recommended_capabilities=categorized["recommended_capabilities"],
        freshness_summary=freshness_summary,
        provenance_summary=provenance_summary,
        context_hash=context_hash,
    )
