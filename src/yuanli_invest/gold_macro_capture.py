"""Bounded, read-only FRED CSV capture for GOLD2 macro research.

FRED distributes Federal Reserve H.15 DFII10 and H.10 DTWEXBGS, but this
adapter has no historical first-release vintages. Every row is a *latest*
vintage seen at capture time. The capture timestamp is a first-known bound,
not a claim about when the Fed or FRED first published a historical value.
DTWEXBGS retains its FRED distributor identity; a separate, explicit mapping
decision is required before using it as the strategy's H.10 input.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import io
import math
import subprocess
from urllib.parse import urlencode, urlsplit


MAX_RESPONSE_BYTES = 1_000_000
MAX_INTERVAL_DAYS = 3_700
MAX_ROWS = 3_700
FRED_HOST = "fred.stlouisfed.org"
_PROVIDER = "fred_graph_csv"


@dataclass(frozen=True)
class MacroSpec:
    provider_series: str
    start: date
    end_inclusive: date

    def __post_init__(self) -> None:
        if self.provider_series not in {"DFII10", "DTWEXBGS"}:
            raise ValueError("only frozen GOLD2 macro series are allowed")
        if not isinstance(self.start, date) or not isinstance(self.end_inclusive, date):
            raise ValueError("start and end must be dates")
        if self.start > self.end_inclusive or (self.end_inclusive - self.start).days > MAX_INTERVAL_DAYS:
            raise ValueError("macro capture interval is empty or too large")

    def url(self) -> str:
        query = urlencode({
            "id": self.provider_series,
            "cosd": self.start.isoformat(),
            "coed": self.end_inclusive.isoformat(),
        })
        return f"https://{FRED_HOST}/graph/fredgraph.csv?{query}"


def fetch_raw(spec: MacroSpec, *, runner=subprocess.run) -> bytes:
    """Fetch one public CSV. No API key, account, or order endpoint is used."""
    url = spec.url()
    if urlsplit(url).hostname != FRED_HOST:
        raise ValueError("unexpected macro data host")
    # curl uses the workstation's configured network path; macOS urllib can
    # hang at the same public endpoint here. -q prevents ~/.curlrc credentials,
    # and we deliberately do not follow redirects.
    marker = b"\n__YUANLI_GOLD_MACRO_RESPONSE__"
    result = runner([
        "curl", "-q", "--silent", "--show-error", "--fail",
        "--proto", "=https", "--connect-timeout", "8", "--max-time", "30",
        "--max-filesize", str(MAX_RESPONSE_BYTES),
        "--header", "Accept: text/csv",
        "--write-out", marker.decode() + "%{http_code}|%{url_effective}|%{content_type}",
        url,
    ], capture_output=True, check=False, timeout=35)
    if result.returncode != 0 or marker not in result.stdout:
        raise ValueError("public macro CSV request failed")
    raw, trailer = result.stdout.rsplit(marker, 1)
    try:
        status, effective_url, content_type = trailer.decode("ascii").split("|", 2)
    except (UnicodeError, ValueError) as exc:
        raise ValueError("invalid macro response metadata") from exc
    if status != "200" or urlsplit(effective_url).hostname != FRED_HOST or effective_url != url:
        raise ValueError("unexpected macro response status or redirect")
    if content_type.split(";", 1)[0].strip().lower() not in {"text/csv", "application/csv", "application/octet-stream"}:
        raise ValueError("unexpected macro response content type")
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("oversized macro response")
    return raw


def _instant(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("captured_at must be timezone-aware")
    return value.astimezone(timezone.utc)


def _descriptor(spec: MacroSpec) -> dict:
    if spec.provider_series == "DFII10":
        return {
            "source_series": "FRED:DFII10",
            "strategy_series_candidate": "FRED:DFII10",
            "strategy_measurement_regime_candidate": "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY",
            "measurement_regime": "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY",
            "underlying_release": "FEDERAL_RESERVE_H15",
            "unit": "PERCENT",
            "identity_mapping_required": False,
        }
    return {
        "source_series": "FRED:DTWEXBGS",
        "strategy_series_candidate": "FED:H10:DTWEXBGS",
        "strategy_measurement_regime_candidate": "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY",
        "measurement_regime": "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY",
        "underlying_release": "FEDERAL_RESERVE_H10",
        "unit": "INDEX",
        "identity_mapping_required": True,
    }


def normalize_raw(raw: bytes, spec: MacroSpec, *, captured_at: datetime) -> dict:
    """Normalize a latest-vintage CSV without inventing historical release times."""
    capture = _instant(captured_at)
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("raw CSV must be nonempty bounded bytes")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("macro CSV must be UTF-8") from exc
    reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
    try:
        csv_rows = list(reader)
    except csv.Error as exc:
        raise ValueError("malformed macro CSV") from exc
    header = csv_rows[0] if csv_rows else None
    if header != ["observation_date", spec.provider_series]:
        raise ValueError("macro CSV series/header mismatch")
    if len(csv_rows) - 1 > MAX_ROWS:
        raise ValueError("too many macro CSV rows")
    source = _descriptor(spec)
    source_hash = hashlib.sha256(raw).hexdigest()
    capture_iso = capture.isoformat()
    vintage_id = "FRED_GRAPH_LATEST_" + capture.strftime("%Y%m%dT%H%M%S%fZ") + "_" + source_hash[:12]
    observations: list[dict] = []
    seen: set[date] = set()
    missing_count = 0
    last_day: date | None = None
    for fields in csv_rows[1:]:
        if len(fields) != 2:
            raise ValueError("macro CSV row width mismatch")
        try:
            observed = date.fromisoformat(fields[0])
        except ValueError as exc:
            raise ValueError("invalid macro observation date") from exc
        if (not spec.start <= observed <= spec.end_inclusive or observed in seen
                or (last_day is not None and observed <= last_day)):
            raise ValueError("macro observation date outside range, repeated, or out of order")
        if observed > capture.date():
            raise ValueError("macro observation date is after capture date")
        seen.add(observed)
        last_day = observed
        if fields[1] in {"", "."}:
            missing_count += 1
            continue
        try:
            decimal_value = Decimal(fields[1])
        except InvalidOperation as exc:
            raise ValueError("invalid macro numeric value") from exc
        if not decimal_value.is_finite():
            raise ValueError("nonfinite macro numeric value")
        numeric_value = float(decimal_value)
        if not math.isfinite(numeric_value) or (spec.provider_series == "DTWEXBGS" and numeric_value <= 0):
            raise ValueError("invalid macro value")
        observations.append({
            "series": source["source_series"],
            "source_provider_id": _PROVIDER,
            "provider_series": spec.provider_series,
            "unit": source["unit"],
            "measurement_regime": source["measurement_regime"],
            "observed_on": observed.isoformat(),
            "observation_time_basis": "NEW_YORK_DAILY_DATE_LABEL_ONLY",
            "value": numeric_value,
            "released_at": capture_iso,
            "retrieved_at": capture_iso,
            "available_at": capture_iso,
            "release_time_basis": "FIRST_KNOWN_AT_CAPTURE_NOT_ACTUAL_PUBLICATION",
            "source_ref": spec.url(),
            "source_url": spec.url(),
            "vintage_id": vintage_id,
            "raw_sha256": source_hash,
            "pit_grade": "UNKNOWN",
            "vintage_kind": "UNKNOWN",
        })
    return {
        "schema_version": "gold-macro-fred-capture.v1",
        "provider_id": _PROVIDER,
        "distributor": "Federal Reserve Bank of St. Louis FRED graph CSV",
        "underlying_publisher": "Board of Governors of the Federal Reserve System",
        "underlying_release": source["underlying_release"],
        "provider_series": spec.provider_series,
        "source_series": source["source_series"],
        "strategy_series_candidate": source["strategy_series_candidate"],
        "measurement_regime": source["measurement_regime"],
        "strategy_measurement_regime_candidate": source["strategy_measurement_regime_candidate"],
        "identity_mapping_required": source["identity_mapping_required"],
        "identity_mapping_status": "UNDECLARED" if source["identity_mapping_required"] else "EXACT_SERIES_ID",
        "source_url": spec.url(),
        "source_ref": spec.url(),
        "raw_sha256": source_hash,
        "captured_at": capture_iso,
        "historical_release_time_verified": False,
        "pit_grade": "UNKNOWN",
        "vintage_kind": "UNKNOWN",
        "authority": "RESEARCH_EVIDENCE_ONLY",
        "action_authority": "none",
        "missing_value_rows": missing_count,
        "row_count": len(observations),
        "observations": observations,
    }
