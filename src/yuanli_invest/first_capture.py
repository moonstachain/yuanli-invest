"""Exact-date Gold adjudication from immutable, registered-source first captures.

This daily method does not claim a first release or fabricate an intraday fixing
time. Registration and observations must be read from the trusted runtime.
"""

from datetime import date
from decimal import Decimal, localcontext
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .receipts import canonical_hash, read_envelope
from .time import instant

METHOD = "daily_first_capture_v1"
SOURCE_FIELDS = ("source_id", "series_id", "target", "unit", "currency", "source_timezone")
CLAIM_FIELDS = {
    "schema_version", "method", "claim_id", "capability_version", *SOURCE_FIELDS,
    "start_trade_date", "end_trade_date", "evidence_known_as_of", "model_direction",
    "baseline_id", "baseline_direction", "neutral_band_pct", "data_mode",
}


def trade_day(value: Any) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("trade date must be YYYY-MM-DD")
    return date.fromisoformat(value)


def decimal_value(value: Any, label: str, *, positive: bool = False) -> Decimal:
    # Decimal strings cross Python, JSON and PostgreSQL without a float roundtrip.
    if not isinstance(value, str) or len(value) > 100 or not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", value):
        raise ValueError(f"{label} must be a nonnegative decimal string")
    result = Decimal(value)
    if positive and result <= 0:
        raise ValueError(f"{label} must be positive")
    return result


def validate_claim(
    claim: Mapping[str, Any], registration: Mapping[str, Any], trusted_source: Mapping[str, Any],
) -> tuple[date, date, ZoneInfo]:
    if set(claim) != CLAIM_FIELDS:
        raise ValueError("claim fields do not match gold-first-capture-claim.v1")
    if claim["schema_version"] != "gold-first-capture-claim.v1" or claim["method"] != METHOD:
        raise ValueError("unsupported daily settlement method")
    for field in ("claim_id", "capability_version", *SOURCE_FIELDS):
        if not isinstance(claim[field], str) or not claim[field].strip():
            raise ValueError(f"missing claim identity: {field}")
    if claim["target"] != "GOLD":
        raise ValueError("daily settlement supports GOLD only")
    if any(claim[field] != trusted_source.get(field) for field in SOURCE_FIELDS):
        raise ValueError("claim does not match the trusted source registry")
    if claim["data_mode"] not in {"REAL_OBSERVATIONS", "SYNTHETIC_ENGINEERING_ONLY"}:
        raise ValueError("explicit data_mode is required")
    if type(claim["model_direction"]) is not int or claim["model_direction"] not in {-1, 0, 1}:
        raise ValueError("model_direction must be -1, 0 or 1")
    if claim["baseline_id"] != "FROZEN_NO_CHANGE" or type(claim["baseline_direction"]) is not int or claim["baseline_direction"] != 0:
        raise ValueError("daily baseline must be frozen no-change direction 0")
    decimal_value(claim["neutral_band_pct"], "neutral_band_pct")
    try:
        source_zone = ZoneInfo(claim["source_timezone"])
    except ZoneInfoNotFoundError as exc:
        raise ValueError("invalid source timezone") from exc
    start, end = trade_day(claim["start_trade_date"]), trade_day(claim["end_trade_date"])
    registered = instant(registration["registered_at"])
    if not registered.astimezone(source_zone).date() < start < end:
        raise ValueError("registration day must precede start trade date and end trade date")
    if instant(claim["evidence_known_as_of"]) > registered:
        raise ValueError("decision evidence became known after registration")
    frozen = read_envelope({"receipt_json": registration["claim_json"], "receipt_sha256": registration["claim_sha256"]})
    if frozen != claim:
        raise ValueError("claim differs from its immutable registered bytes")
    return start, end, source_zone


def _first_capture(observations, claim, day, as_of, source_zone):
    matches = []
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("capture must be an object")
        if row.get("source_id") != claim["source_id"] or row.get("trade_date") != day.isoformat():
            continue
        if row.get("source_timezone") != claim["source_timezone"]:
            raise ValueError("capture timezone disagrees with trusted source")
        decimal_value(row.get("value_decimal"), "capture value", positive=True)
        if not isinstance(row.get("capture_id"), str) or not row["capture_id"]:
            raise ValueError("capture_id is required")
        if not isinstance(row.get("payload_sha256"), str) or not re.fullmatch("[a-f0-9]{64}", row["payload_sha256"]):
            raise ValueError("capture payload_sha256 must be a lowercase SHA256")
        captured = instant(row["first_captured_at"])
        if captured.astimezone(source_zone).date() < day:
            raise ValueError("capture predates its trade date")
        matches.append((captured, row))
    if not matches:
        return None, "MISSING_EXACT_TRADE_DATE"
    first_time = min(when for when, _ in matches)
    if first_time > as_of:
        return None, "NOT_YET_CAPTURED"
    first = [row for when, row in matches if when == first_time]
    if len({canonical_hash(row) for row in first}) != 1:
        raise ValueError("conflicting first capture records")
    return first[0], "EXACT_DATE_FIRST_CAPTURE"


def settle_daily_first_capture(payload: Mapping[str, Any]) -> dict[str, Any]:
    claim, registration, trusted_source = (payload.get(key) for key in ("claim", "registration", "trusted_source"))
    if not all(isinstance(item, dict) for item in (claim, registration, trusted_source)):
        raise ValueError("claim, registration and trusted_source objects are required")
    start, end, source_zone = validate_claim(claim, registration, trusted_source)
    as_of = instant(payload.get("as_of"))
    if as_of < instant(registration["registered_at"]):
        raise ValueError("settlement predates registration")
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise ValueError("observations must be an array")
    receipt = {
        "schema_version": "gold-first-capture-settlement.v1", "method": METHOD,
        "claim_id": claim["claim_id"], "claim_sha256": registration["claim_sha256"],
        "as_of": as_of.isoformat(), "data_mode": claim["data_mode"],
        "status": "NOT_DUE", "model_score": None, "baseline_score": None,
        "selected_capture_ids": {},
    }
    if as_of.astimezone(source_zone).date() <= end:
        return receipt
    opening, opening_status = _first_capture(observations, claim, start, as_of, source_zone)
    closing, closing_status = _first_capture(observations, claim, end, as_of, source_zone)
    receipt["endpoint_status"] = {"start": opening_status, "end": closing_status}
    if opening is None or closing is None:
        receipt["status"] = "INDETERMINATE_EVIDENCE"
        return receipt
    opening_value = decimal_value(opening["value_decimal"], "opening value", positive=True)
    closing_value = decimal_value(closing["value_decimal"], "closing value", positive=True)
    band = decimal_value(claim["neutral_band_pct"], "neutral_band_pct")
    with localcontext() as context:
        context.prec = max(50, sum(len(value) for value in (opening["value_decimal"], closing["value_decimal"], claim["neutral_band_pct"])) + 10)
        numerator = (closing_value - opening_value) * 100
        threshold = band * opening_value
        direction = 1 if numerator > threshold else -1 if numerator < -threshold else 0
        return_decimal = str(numerator / opening_value)
    receipt.update({
        "status": "SETTLED_RESEARCH", "outcome_return_pct_decimal": return_decimal,
        "realized_direction": direction,
        "model_score": {"direction": claim["model_direction"], "correct": direction == claim["model_direction"]},
        "baseline_score": {"baseline_id": "FROZEN_NO_CHANGE", "direction": 0, "correct": direction == 0},
        "selected_capture_ids": {"start": opening["capture_id"], "end": closing["capture_id"]},
        "outcome_semantics": "DAILY_FIRST_CAPTURE_EXACT_DATES_NO_PNL_OR_TRADABILITY_CLAIM",
    })
    return receipt
