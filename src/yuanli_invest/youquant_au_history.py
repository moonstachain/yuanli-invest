"""Read-only capture of dated YouQuant AU daily bars.

The provider's bar timestamp is a label, not a proved exchange close or a
historical publication timestamp. Captures are retrospective evidence only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import gzip
import hashlib
import io
import json
import re
import ssl
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SCHEMA = ["time", "open", "high", "low", "close", "vol", "position"]
MAX_RESPONSE_BYTES = 2_000_000


@dataclass(frozen=True)
class RequestSpec:
    symbol: str
    start: date
    end_exclusive: date

    def __post_init__(self) -> None:
        if not re.fullmatch(r"au\d{4}", self.symbol):
            raise ValueError("only a dated SHFE AU contract is accepted")
        yy, mm = int(self.symbol[2:4]), int(self.symbol[4:6])
        if not 1 <= mm <= 12 or not 2019 <= 2000 + yy <= 2035:
            raise ValueError("invalid AU delivery month")
        if self.start >= self.end_exclusive:
            raise ValueError("empty history interval")
        if self.end_exclusive - self.start > timedelta(days=430):
            raise ValueError("history request exceeds one contract-year")

    def url(self) -> str:
        params = {
            "detail": "true", "round": "true", "feeder": "local", "event": "feed",
            "symbol": self.symbol, "eid": "Futures_CTP", "depth": "20",
            "trades": "0", "custom": "0", "period": "86400000",
            # Provider daily bar labels are midnight Asia/Shanghai. UTC-midnight
            # request boundaries silently drop the first local-labelled day.
            "from": int(datetime.combine(self.start, datetime.min.time(), SHANGHAI).timestamp()),
            "to": int(datetime.combine(self.end_exclusive, datetime.min.time(), SHANGHAI).timestamp()),
        }
        return "https://q.youquant.com/data/history?" + urlencode(params)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        raise ValueError("provider redirect blocked")


def fetch_raw(spec: RequestSpec, *, opener=None) -> bytes:
    """Fetch exactly one bounded HTTPS response without account credentials."""
    opener = opener or build_opener(
        ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), _NoRedirect()
    )
    url = spec.url()
    if urlsplit(url).hostname != "q.youquant.com":
        raise ValueError("unexpected history host")
    with opener.open(Request(url, headers={"Accept-Encoding": "gzip"}), timeout=25) as response:
        if response.status != 200 or urlsplit(response.url).hostname != "q.youquant.com":
            raise ValueError("unexpected response status or host")
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("oversized provider response")
        if response.headers.get("Content-Encoding") == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
                body = compressed.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError("oversized decoded provider response")
        return body


def _number(value: object, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("raw provider numeric field must be an integer")
    result = Decimal(value)
    if not result.is_finite() or (result <= 0 if positive else result < 0):
        raise ValueError("invalid provider numeric field")
    return result


def normalize_raw(raw: bytes, spec: RequestSpec, *, captured_at: str) -> dict:
    """Decode verified wire fields; never trust returned historical contract metadata."""
    capture = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    if capture.tzinfo is None:
        raise ValueError("capture clock requires a timezone")
    capture = capture.astimezone(timezone.utc)
    payload = json.loads(raw)
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("unsupported YouQuant history schema")
    detail = payload.get("detail")
    if not isinstance(detail, dict) or detail.get("symbol") != spec.symbol or detail.get("contractType") != spec.symbol:
        raise ValueError("requested contract identity mismatch")
    if detail.get("eid") != "Futures_CTP" or detail.get("quoteCurrency") != "CNY" or detail.get("quotePrecision") != 2:
        raise ValueError("exchange, currency or scaling mismatch")
    if detail.get("basePrecision") != 0 or detail.get("priceTick") != 0.02:
        raise ValueError("unverified AU precision or tick")
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("missing history rows")
    bars: dict[str, dict] = {}
    for row in data:
        if not isinstance(row, list) or len(row) != 7:
            raise ValueError("raw provider row width mismatch")
        stamp = row[0]
        if isinstance(stamp, bool) or not isinstance(stamp, int):
            raise ValueError("bar time must be integer milliseconds")
        label = datetime.fromtimestamp(stamp / 1000, timezone.utc).astimezone(SHANGHAI)
        if label.time() != datetime.min.time():
            raise ValueError("unexpected AU daily label time")
        day = label.date()
        if not spec.start <= day < spec.end_exclusive:
            continue
        values = [_number(value, positive=index in {1, 2, 3, 4}) for index, value in enumerate(row[1:], start=1)]
        opening, high, low, close = (value / 100 for value in values[:4])
        if not low <= min(opening, close) <= max(opening, close) <= high:
            raise ValueError("inconsistent AU OHLC")
        result = {
            "contract": spec.symbol, "date": day.isoformat(), "label_at": label.isoformat(),
            "time_semantics": "PROVIDER_DAILY_LABEL_NOT_CLOSE_TIME",
            "open": str(opening), "high": str(high), "low": str(low), "close": str(close),
            "volume": int(values[4]), "open_interest": int(values[5]),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "pit_grade": "LATEST_VINTAGE_ONLY", "captured_at": capture.isoformat(),
        }
        if day.isoformat() in bars and bars[day.isoformat()] != result:
            raise ValueError("conflicting duplicate AU daily label")
        bars[day.isoformat()] = result
    return {
        "schema_version": "youquant-au-dated-history.v1", "provider_id": "youquant_history",
        "requested_symbol": spec.symbol, "request_url": spec.url(),
        "captured_at": capture.isoformat(), "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "row_count": len(bars), "bars": [bars[day] for day in sorted(bars)],
        "historical_release_time_verified": False, "contract_metadata_usable": False,
        "metadata_observed": detail.get("info"),
        "authority": "RESEARCH_EVIDENCE_ONLY",
    }


def contract_specs(start: date, end_exclusive: date) -> list[RequestSpec]:
    """Enumerate candidate dated contracts, including every listed month."""
    if start >= end_exclusive:
        raise ValueError("empty project interval")
    first = date(start.year, start.month, 1)
    month = date(first.year, first.month, 1)
    result: list[RequestSpec] = []
    while month < end_exclusive + timedelta(days=95):
        delivery = date(month.year, month.month, 1)
        from_day = max(start, delivery - timedelta(days=400))
        to_day = min(end_exclusive, delivery)
        if from_day < to_day:
            result.append(RequestSpec(f"au{delivery.year % 100:02d}{delivery.month:02d}", from_day, to_day))
        month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
    return result
