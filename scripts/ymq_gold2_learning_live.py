#!/usr/bin/env python3
"""YMQ-GOLD2 G7 — provider-neutral daily Learning Live post-processor.

Consumes normalized successful Gold Live Shadow receipts only. It does not read
provider credentials, call external providers, accept learning, or grant any
capital, sizing, execution, broker, VeighNa, asset-promotion, or Canon authority.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "ymq_gold2" / "gold2_learning_live.v0.1.json"
DENY_FIELDS = (
    "accepted_learning_authorized",
    "capital_authorized",
    "sizing_authorized",
    "execution_authorized",
    "broker_action",
    "veighna_authorized",
    "asset_promotion_authorized",
    "canon_promotion_authorized",
)
STATE_FIELDS = (
    "property_drift_state",
    "expectation_reality_state",
    "valuation_state",
    "research_state",
    "lifecycle_state",
)


def load_contract(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or CONTRACT_PATH).read_text(encoding="utf-8"))


def validate_contract(cfg: Mapping[str, Any]) -> None:
    if cfg.get("status") != "HUMAN_AUTHORIZED_RESEARCH_LEARNING_ONLY":
        raise ValueError("Learning Live is not Human-authorized for research")
    authority = cfg.get("authority", {})
    if authority.get("research_learning_authorized") is not True:
        raise ValueError("research learning authority missing")
    scheduler_flag = authority.get("production_scheduler_integration_authorized")
    if not isinstance(scheduler_flag, bool):
        raise ValueError("production scheduler integration gate must be explicit boolean")
    for field in DENY_FIELDS:
        if authority.get(field) is not False:
            raise ValueError(f"forbidden Learning Live authority enabled: {field}")
    storage = cfg.get("storage", {})
    if storage.get("root_relative_to_shadow_runtime") != "learning":
        raise ValueError("learning storage root drift")
    if storage.get("git_persistence") is not False:
        raise ValueError("runtime learning may not persist to Git")
    if storage.get("raw_provider_body_persistence") is not False:
        raise ValueError("raw provider bodies may not enter Learning Live")
    settlement = cfg.get("settlement", {})
    if settlement.get("directional_scoring_requires_preregistered_claim") is not True:
        raise ValueError("post-hoc directional scoring is prohibited")
    if settlement.get("missing_claim_state") != "NOT_SCORABLE":
        raise ValueError("missing claim must remain NOT_SCORABLE")
    thresholds = cfg.get("attention_thresholds", {})
    for key in ("gold_price_pct_abs", "real_rate_bps_abs", "usd_pct_abs"):
        value = thresholds.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"invalid attention threshold: {key}")


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def receipt_sha256(receipt: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(receipt).encode("utf-8")).hexdigest()


def _as_day(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except Exception as exc:
        raise ValueError(f"invalid {field}") from exc


def _require_live(receipt: Mapping[str, Any]) -> None:
    if receipt.get("status") != "LIVE_SHADOW_RECEIPT":
        raise ValueError("Learning Live requires LIVE_SHADOW_RECEIPT")


def _metric_value(receipt: Mapping[str, Any], name: str) -> float:
    providers = receipt.get("provider_receipts")
    if not isinstance(providers, Mapping) or name not in providers:
        raise ValueError(f"missing provider receipt: {name}")
    raw = providers[name].get("latest_value") if isinstance(providers[name], Mapping) else None
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raise ValueError(f"non-numeric provider value: {name}")
    return float(raw)


def validate_live_receipt(receipt: Mapping[str, Any]) -> tuple[date, date]:
    _require_live(receipt)
    as_of = _as_day(receipt.get("as_of"), "as_of")
    known = _as_day(receipt.get("known_as_of_max"), "known_as_of_max")
    if known > as_of:
        raise ValueError("future-dated evidence")
    for metric in ("gold_price", "real_rate", "usd"):
        _metric_value(receipt, metric)
    return as_of, known


def _validate_pit(prior: Mapping[str, Any], current: Mapping[str, Any]) -> tuple[date, date, date, date]:
    prior_day, prior_known = validate_live_receipt(prior)
    current_day, current_known = validate_live_receipt(current)
    if current_known < prior_known:
        raise ValueError("known_as_of regression")
    return prior_day, current_day, prior_known, current_known


def _state_transitions(prior: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    transitions: dict[str, Any] = {}
    for field in STATE_FIELDS:
        before = prior.get(field)
        after = current.get(field)
        if before != after:
            transitions[field] = {"from": before, "to": after}
    return transitions


def build_state_delta(
    prior: Mapping[str, Any], current: Mapping[str, Any], cfg: Mapping[str, Any]
) -> dict[str, Any]:
    validate_contract(cfg)
    prior_day, current_day, prior_known, current_known = _validate_pit(prior, current)
    if current_day <= prior_day:
        raise ValueError("daily delta requires a later as_of")

    prior_gold = _metric_value(prior, "gold_price")
    current_gold = _metric_value(current, "gold_price")
    prior_real = _metric_value(prior, "real_rate")
    current_real = _metric_value(current, "real_rate")
    prior_usd = _metric_value(prior, "usd")
    current_usd = _metric_value(current, "usd")
    if prior_gold == 0 or prior_usd == 0:
        raise ValueError("percentage delta denominator may not be zero")

    gold_pct = (current_gold / prior_gold - 1.0) * 100.0
    real_bps = (current_real - prior_real) * 100.0
    usd_pct = (current_usd / prior_usd - 1.0) * 100.0
    thresholds = cfg["attention_thresholds"]
    attention: list[str] = []
    if abs(gold_pct) >= float(thresholds["gold_price_pct_abs"]):
        attention.append("gold_price_pct")
    if abs(real_bps) >= float(thresholds["real_rate_bps_abs"]):
        attention.append("real_rate_bps")
    if abs(usd_pct) >= float(thresholds["usd_pct_abs"]):
        attention.append("usd_pct")

    prior_unknowns = set(map(str, prior.get("unknowns") or []))
    current_unknowns = set(map(str, current.get("unknowns") or []))
    return {
        "prior_as_of": prior_day.isoformat(),
        "current_as_of": current_day.isoformat(),
        "prior_known_as_of": prior_known.isoformat(),
        "current_known_as_of": current_known.isoformat(),
        "known_as_of_days_advanced": (current_known - prior_known).days,
        "gold_price_pct": gold_pct,
        "real_rate_bps": real_bps,
        "usd_pct": usd_pct,
        "attention": attention,
        "state_transitions": _state_transitions(prior, current),
        "unknowns_resolved": sorted(prior_unknowns - current_unknowns),
        "unknowns_added": sorted(current_unknowns - prior_unknowns),
    }


def build_settlement(
    prior: Mapping[str, Any],
    current: Mapping[str, Any],
    delta: Mapping[str, Any],
    cfg: Mapping[str, Any],
) -> dict[str, Any]:
    validate_contract(cfg)
    _validate_pit(prior, current)
    claim = prior.get("preregistered_directional_claim")
    directional_score = "PENDING_FUTURE_HORIZON" if claim else cfg["settlement"]["missing_claim_state"]
    return {
        "pit_integrity": "PASS",
        "directional_claim_score": directional_score,
        "regime_detection_lag": cfg["settlement"]["regime_detection_lag_without_preregistered_event"],
        "decision_regret": cfg["settlement"]["decision_regret_without_decision_object"],
        "state_transition_observed": bool(delta.get("state_transitions")),
        "unknowns_resolved_count": len(delta.get("unknowns_resolved") or []),
        "unknowns_added_count": len(delta.get("unknowns_added") or []),
        "attention_count": len(delta.get("attention") or []),
    }


def build_learning_candidate(
    prior: Mapping[str, Any], current: Mapping[str, Any], cfg: Mapping[str, Any]
) -> dict[str, Any]:
    validate_contract(cfg)
    prior_day, _ = validate_live_receipt(prior)
    current_day, _ = validate_live_receipt(current)
    if current_day == prior_day:
        return {
            "program": cfg["program"],
            "battle": cfg["battle"],
            "status": cfg["settlement"]["same_day_duplicate_state"],
            "as_of": current_day.isoformat(),
            "accepted_learning": False,
            "authority": dict(cfg["authority"]),
        }
    if current_day < prior_day:
        raise ValueError("current receipt predates prior receipt")

    delta = build_state_delta(prior, current, cfg)
    settlement = build_settlement(prior, current, delta, cfg)
    prior_unknowns = set(map(str, prior.get("unknowns") or []))
    current_unknowns = set(map(str, current.get("unknowns") or []))
    denominator = max(1, len(prior_unknowns | current_unknowns))
    return {
        "program": cfg["program"],
        "battle": cfg["battle"],
        "status": "LEARNING_CANDIDATE_ONLY",
        "as_of": current_day.isoformat(),
        "source_receipts": {
            "prior_sha256": receipt_sha256(prior),
            "current_sha256": receipt_sha256(current),
        },
        "delta": delta,
        "settlement": settlement,
        "unknown_rate": len(current_unknowns) / denominator,
        "accepted_learning": False,
        "authority": dict(cfg["authority"]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def find_previous_daily_receipt(
    current: Mapping[str, Any], candidates: Iterable[Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    current_day, _ = validate_live_receipt(current)
    eligible: list[tuple[date, str, Mapping[str, Any]]] = []
    for candidate in candidates:
        if candidate.get("status") != "LIVE_SHADOW_RECEIPT":
            continue
        try:
            candidate_day, _ = validate_live_receipt(candidate)
        except ValueError:
            continue
        if candidate_day >= current_day:
            continue
        eligible.append((candidate_day, receipt_sha256(candidate), candidate))
    if not eligible:
        return None
    eligible.sort(key=lambda row: (row[0], row[1]))
    return eligible[-1][2]


def write_learning_candidate(candidate: Mapping[str, Any], runtime_root: Path) -> Path:
    learning_root = runtime_root / "learning"
    day = str(candidate.get("as_of") or date.today().isoformat())
    daily = learning_root / day
    daily.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    target = daily / f"learning-{stamp}.json"
    text = json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    target.write_text(text, encoding="utf-8")
    (learning_root / "latest-learning.json").write_text(text, encoding="utf-8")
    return target


def load_runtime_receipts(runtime_root: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in sorted(runtime_root.glob("????-??-??/receipt-*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            receipts.append(value)
    return receipts


def process_current_receipt(
    current: Mapping[str, Any], runtime_root: Path, cfg: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    config = dict(cfg or load_contract())
    validate_contract(config)
    validate_live_receipt(current)
    prior = find_previous_daily_receipt(current, load_runtime_receipts(runtime_root))
    if prior is None:
        return {
            "program": config["program"],
            "battle": config["battle"],
            "status": "LEARNING_WARMUP_PENDING",
            "as_of": current.get("as_of"),
            "accepted_learning": False,
            "authority": dict(config["authority"]),
        }
    candidate = build_learning_candidate(prior, current, config)
    if candidate["status"] == "LEARNING_CANDIDATE_ONLY":
        target = write_learning_candidate(candidate, runtime_root)
        candidate = {**candidate, "learning_receipt_path": str(target)}
    return candidate


if __name__ == "__main__":
    raise SystemExit("Learning Live is a post-processor; invoke through the Gold Live Shadow runtime.")
