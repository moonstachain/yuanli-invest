"""Current-time public evidence observation, isolated from the 08:30 contract.

All source bytes must actually be available now. Price lookback is descriptive
as known now; its intermediate points are never historical decision evidence.
No cost assumption, account claim, signal id, or broker authority is emitted.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Mapping

from .gold_au_daily_request import _receipt
from .gold_au_live_snapshot import (SHANGHAI, MIN_PRIOR_SESSIONS, SnapshotSkip,
                                    _archive, _mapping, _fred_captures)
from .gold_au_official_calendar import CalendarEvidenceError, load_calendar_receipt
from .gold_au_strategy import DEFAULT_CONFIG, GoldAuDataset, build_decision_path, macro_gate
from .receipts import canonical_hash


class _CurrentKnownPriceLookback(GoldAuDataset):
    """Read each historical price only if strictly available at observation.

    This adapter is confined to descriptive research. It deliberately does not
    claim that today's archive was available on an earlier historical morning.
    Macro observations continue to use explicit actual-time strict PIT queries.
    """
    def __init__(self, payload: Mapping[str, Any], observed: datetime):
        super().__init__(payload)
        self.observed = observed

    def bar(self, day, contract, as_of, mode):
        return super().bar(day, contract, self.observed, "strict")

    def bars_for_day(self, day, as_of, mode):
        return super().bars_for_day(day, self.observed, "strict")


def observe_public_evidence(request: Any, *, as_of: datetime) -> dict[str, Any]:
    base = {"schema_version": "gold-au-current-research-observation.v1", "status": "BLOCKED",
            "purpose": "CURRENT_PUBLIC_EVIDENCE_RESEARCH_ONLY", "decision_frozen": False,
            "broker_action_authorized": False, "actionable_entry": False,
            "trade_admission": "NOT_EVALUATED_ACCOUNT_COST_MARGIN_REQUIRED",
            "historical_first_release_verified": False,
            "external_witness_authentication": "NOT_VERIFIED_BY_OFFLINE_MODULE"}
    try:
        if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
            raise SnapshotSkip("AWARE_OBSERVATION_TIME_REQUIRED")
        observed = as_of.astimezone(timezone.utc)
        base["observed_at"] = observed.isoformat()
        if not isinstance(request, Mapping) or request.get("schema_version") != "gold-au-research-observation-request.v1":
            raise SnapshotSkip("EXPLICIT_RESEARCH_OBSERVATION_REQUEST_REQUIRED")
        if any(key in request for key in ("cost_receipt_path", "signal_id", "valid_from", "valid_until", "action_contract")):
            raise SnapshotSkip("TRADING_CONTRACT_FIELDS_FORBIDDEN_IN_RESEARCH_OBSERVATION")
        names = [request.get(k) for k in ("calendar_receipt_path", "fred_manifest_path", "h10_mapping_receipt_path")]
        archives = request.get("shfe_manifest_paths")
        if not isinstance(archives, list) or not 1 <= len(archives) <= 8:
            raise SnapshotSkip("EXPLICIT_BOUNDED_SHFE_ARCHIVE_REQUIRED")
        names += archives
        if any(not isinstance(n, str) or not n or not Path(n).is_absolute() for n in names):
            raise SnapshotSkip("ABSOLUTE_RESEARCH_SOURCE_PATHS_REQUIRED")
        if len({str(Path(n).resolve()) for n in names}) != len(names):
            raise SnapshotSkip("CONFLICTING_RESEARCH_SOURCE_PATHS")
        proofs = []
        for name in names:
            _, proof = _receipt(Path(name), as_of=observed)
            if proof["status"] != "LOCAL_BYTES_READ":
                raise SnapshotSkip(proof["reason"])
            proofs.append(proof)
        calendar = load_calendar_receipt(Path(names[0]), as_of=observed)
        days = [date.fromisoformat(d) for d in calendar["sessions"]]
        today = observed.astimezone(SHANGHAI).date()
        # On weekends/holidays the next official session is only a contract-
        # eligibility reference; no future decision time or publication is used.
        reference = next((d for d in days if d >= today), None)
        if reference is None:
            raise SnapshotSkip("OFFICIAL_CALENDAR_REFERENCE_COVERAGE_REQUIRED")
        index = days.index(reference)
        if index < MIN_PRIOR_SESSIONS:
            raise SnapshotSkip("INSUFFICIENT_OFFICIAL_SESSION_HISTORY")
        prior = days[index - MIN_PRIOR_SESSIONS:index]
        bars, shfe = _archive(request, prior, observed)
        mapping, mapping_sha = _mapping(Path(names[2]), observed)
        macro, macro_sha = _fred_captures(Path(names[1]), observed, mapping)
        payload = {"price_quality": {"status": "LIVE_SOURCE_CHECKED", "audit_ref": "SHFE_HASH_CHECKED_CURRENT_RESEARCH"},
                   "exchange_sessions": [d.isoformat() for d in days[:index + 1]],
                   "exchange_calendar_ref": names[0], "bars": bars, "observations": macro,
                   "purpose": "CURRENT_AS_OF_LOOKBACK_DESCRIPTION_NO_HISTORICAL_SIGNALS"}
        dataset = _CurrentKnownPriceLookback(payload, observed)
        path = build_decision_path(dataset, pit_mode="strict")
        point = path[-1] if path else None
        if point is None or point.contract is None or point.atr20 is None or point.high_volatility is None:
            raise SnapshotSkip("INSUFFICIENT_CURRENT_KNOWN_PRICE_LOOKBACK")
        closes = [p.close_index for p in path[:-1] if p.close_index is not None]
        if len(closes) < 20:
            raise SnapshotSkip("INSUFFICIENT_CURRENT_KNOWN_BREAKOUT_LOOKBACK")
        gate = macro_gate(dataset, observed, pit_mode="strict")
        # No optional WGC supplied here: this observation retains unknown status.
        vol = 0.5 if point.high_volatility else 1.0
        for proof in proofs:
            _, reread = _receipt(Path(proof["path"]), as_of=observed)
            if reread.get("status") != "LOCAL_BYTES_READ" or reread.get("receipt_sha256") != proof["receipt_sha256"]:
                raise SnapshotSkip("SOURCE_CHANGED_DURING_RESEARCH_OBSERVATION")
        return {**base, "status": "READY_RESEARCH_OBSERVATION",
                "request_sha256": canonical_hash(request), "source_inventory": proofs,
                "public_dataset_sha256": canonical_hash(payload), "public_dataset": payload,
                "price_observation": {"last_completed_session": prior[-1].isoformat(),
                    "official_prior_sessions": len(prior), "eligibility_reference_session": reference.isoformat(),
                    "contract": point.contract, "chained_close_index": point.close_index,
                    "prior_20_close_high": max(closes[-20:]),
                    "close_above_prior_20_close_high": point.close_index > max(closes[-20:]),
                    "atr20_cny_per_gram": point.atr20, "high_volatility": point.high_volatility,
                    "one_lot_2atr_price_risk_cny_excluding_unknown_execution_costs": 2 * point.atr20 * 1000,
                    "calculation_availability_basis": "STRICT_ACTUAL_OBSERVATION_TIME_FOR_ALL_LOOKBACK_BYTES",
                    "intermediate_price_points_are_historical_signals": False},
                "macro_observation": gate,
                "risk_policy_observation": {"paper_equity_cny": DEFAULT_CONFIG["paper_equity_cny"],
                    "wgc_status": "UNKNOWN", "wgc_multiplier": 0.5, "volatility_multiplier": vol,
                    "indicative_frozen_policy_budget_cny": DEFAULT_CONFIG["paper_equity_cny"] * 0.005 * 0.5 * vol,
                    "account_equity_verified": False, "account_cost_margin_verified": False},
                "source_receipts": {"shfe": shfe, "fred_manifest_sha256": macro_sha, "h10_mapping_sha256": mapping_sha}}
    except (SnapshotSkip, CalendarEvidenceError) as exc:
        return {**base, "reason": exc.code}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return {**base, "reason": "MALFORMED_RESEARCH_EVIDENCE"}
