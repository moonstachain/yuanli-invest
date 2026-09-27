"""Local-only official completed AU history for independently signed exits.

This module owns calendar/raw-SHFE pipeline dependencies. The production cloud
broker facts module only accepts an injected daily history reader; it does not
import or re-export this local capture implementation.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
import hashlib
import json
from typing import Any

from .gold_au_broker_facts import _contract, _fresh, _time, digest
from .gold_paper import PaperDenied, SHANGHAI


class OfficialDailyHistoryReader:
    """Re-read official source bytes and a validated official annual calendar.

    ``snapshot_reader`` returns receipt dictionaries containing exact raw bytes,
    report_date, obtained_at, available_at, sha256 and the dated official URL.
    These are newly observed completed history, never historical first versions.
    """

    def __init__(self, *, calendar_path: Any, snapshot_reader: Callable[[list[str]], list[Mapping]],
                 clock: Callable[[], datetime], count: int = 21):
        if type(count) is not int or not 11 <= count <= 273:
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_COUNT_INVALID")
        self.calendar_path, self.snapshot_reader, self.clock, self.count = calendar_path, snapshot_reader, clock, count

    def __call__(self, contract: str, now: datetime) -> dict:
        from pathlib import Path
        from .gold_au_dataset_assemble import _official_bars
        from .gold_au_official_calendar import load_calendar_receipt, session_window
        contract = _contract(contract)
        start = _time(self.clock())
        _fresh(now, start, 15)
        calendar = load_calendar_receipt(Path(self.calendar_path), as_of=now)
        window = session_window(calendar, _time(now).astimezone(SHANGHAI).date(), prior_count=self.count, horizons=())
        expected = window["prior_sessions"]
        snapshots = self.snapshot_reader(expected)
        if not isinstance(snapshots, list) or len(snapshots) != len(expected):
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_INCOMPLETE")
        bars = []
        for receipt, day in zip(snapshots, expected):
            if not isinstance(receipt, Mapping) or receipt.get("report_date") != day:
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_DATE_MISMATCH")
            compact = day.replace("-", "")
            if receipt.get("source_url") not in {f"https://www.shfe.com.cn/data/dailydata/kx/kx{compact}.dat", f"https://www.shfe.cn/data/dailydata/kx/kx{compact}.dat"}:
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_URL_MISMATCH")
            raw = receipt.get("raw_bytes")
            if not isinstance(raw, bytes) or not 0 < len(raw) <= 2_000_000 or receipt.get("raw_sha256") != "sha256:" + hashlib.sha256(raw).hexdigest():
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_RAW_HASH_MISMATCH")
            obtained, available = _time(receipt.get("obtained_at")), _time(receipt.get("available_at"))
            complete = datetime.combine(date.fromisoformat(day), datetime.min.time(), SHANGHAI) + timedelta(hours=15)
            if not complete <= obtained <= available <= _time(now):
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_NOT_COMPLETED_OR_FUTURE")
            payload = json.loads(raw)
            # Date embedded in official payload must bind to URL/receipt.
            embedded = payload.get("report_date")
            if not isinstance(embedded, str) or embedded.replace("-", "") != compact:
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_RAW_DATE_MISMATCH")
            parsed = _official_bars(raw, day)
            if contract not in parsed:
                raise PaperDenied("OFFICIAL_DAILY_HISTORY_CONTRACT_MISSING")
            bars.append({"date": day, "close": parsed[contract]["close"], "raw_sha256": receipt["raw_sha256"]})
        end = _time(self.clock())
        if end < start or end - start > timedelta(seconds=15):
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_READ_LATE")
        result = {"source": "independent_shfe_dated_daily_close_readback", "contract": contract,
            "observed_at": start.isoformat(), "available_at": end.isoformat(), "verified_session_calendar": True,
            "last_completed_session_date": expected[-1], "next_session_date": window["decision_date"],
            "calendar_raw_sha256": calendar["raw_sha256"], "bars": bars,
            "vintage_scope": "COMPLETED_LATEST_OBSERVED_HISTORY_NOT_HISTORICAL_FIRST_RELEASE"}
        result["raw_sha256"] = digest(result)
        return result
