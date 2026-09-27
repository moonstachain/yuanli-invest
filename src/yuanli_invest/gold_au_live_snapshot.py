"""Read-only 08:10→08:30 AU snapshot from locally captured source bytes.

This module does not fetch data, install a scheduler, authenticate witnesses,
or submit an order. A current-day daily bar is never invented. Publication of
unknown first-release vintages is conservatively bounded by actual capture.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from .gold_au_strategy import (
    DEFAULT_CONFIG, GoldAuDataset, build_current_snapshot_path, evaluate_current_snapshot_signal,
)
from .gold_macro_capture import MacroSpec, normalize_raw as normalize_fred
from .gold_au_official_calendar import CalendarEvidenceError, load_calendar_receipt
from .receipts import canonical_hash
from .time import instant

SHANGHAI = ZoneInfo("Asia/Shanghai")
SHA = set("0123456789abcdef")
MIN_PRIOR_SESSIONS = 273  # ATR20 plus 252 prior ATR observations, including chain seed.
MAX_ARCHIVE_MANIFESTS = 8
MAX_ARCHIVE_REPORTS = 1200
MAX_RAW_BYTES = 1_000_000
MAX_PINNED_RECEIPT_BYTES = 16_000_000


class SnapshotSkip(ValueError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(code)


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise SnapshotSkip("MISSING_OR_INVALID_" + label.upper(), str(exc)) from exc
    if not isinstance(value, dict):
        raise SnapshotSkip("INVALID_" + label.upper(), "JSON object required")
    return value, hashlib.sha256(raw).hexdigest()


def _time(value: Any, label: str) -> datetime:
    try:
        return instant(value)
    except ValueError as exc:
        raise SnapshotSkip("INVALID_" + label.upper(), "timezone-aware timestamp required") from exc


def _within_capture(value: Any, decision_at: datetime, label: str) -> datetime:
    captured = _time(value, label)
    if captured > decision_at:
        raise SnapshotSkip("FUTURE_" + label.upper(), "capture after 08:30 decision")
    return captured


def _read_raw(path_text: Any, expected_sha: Any, manifest_path: Path, label: str) -> bytes:
    if not isinstance(path_text, str) or not isinstance(expected_sha, str) or len(expected_sha) != 64 or any(c not in SHA for c in expected_sha):
        raise SnapshotSkip("MISSING_" + label.upper() + "_RAW_IDENTITY")
    path = Path(path_text).resolve()
    # Raw bytes and their receipt must live together in the private archive.
    if path.parent != (manifest_path.parent / "raw").resolve():
        raise SnapshotSkip("RAW_PATH_OUTSIDE_" + label.upper() + "_ARCHIVE")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SnapshotSkip("MISSING_" + label.upper() + "_RAW", str(exc)) from exc
    if not raw or len(raw) > MAX_RAW_BYTES or hashlib.sha256(raw).hexdigest() != expected_sha:
        raise SnapshotSkip("RAW_HASH_MISMATCH_" + label.upper())
    return raw


def _receipt_source_raw(receipt: Mapping[str, Any], path: Path, label: str) -> None:
    # Calendar/mapping/cost receipts have an immutable local source document,
    # even though an offline validator cannot establish the witness's identity.
    _read_raw(receipt.get("raw_file"), receipt.get("raw_sha256"), path, label)


def _verify_source_pins(request: Mapping[str, Any]) -> None:
    """Optional complete identity freeze for assembled daily requests.

    Legacy caller requests without this field retain their existing behavior.
    Once supplied, the pin set must identify every source receipt exactly,
    including each SHFE manifest and the optional WGC receipt. Raw source
    hashes remain independently checked by the normalizers afterwards.
    """
    if "assembly_source_receipts" not in request:
        return
    keys = ["calendar_receipt_path", "fred_manifest_path", "h10_mapping_receipt_path"]
    if request.get("execution_mode") != "RESEARCH_ONLY":
        keys.append("cost_receipt_path")
    sources = [request.get(key) for key in keys]
    archives = request.get("shfe_manifest_paths")
    if not isinstance(archives, list) or not 1 <= len(archives) <= MAX_ARCHIVE_MANIFESTS:
        raise SnapshotSkip("INVALID_PINNED_SOURCE_REQUEST")
    sources.extend(archives)
    if request.get("wgc_receipt_path"):
        sources.append(request["wgc_receipt_path"])
    if any(not isinstance(name, str) or not name for name in sources):
        raise SnapshotSkip("INVALID_PINNED_SOURCE_REQUEST")
    expected = {}
    for name in sources:
        path = Path(name)
        identity = str(path.resolve())
        if identity in expected:
            raise SnapshotSkip("CONFLICTING_PINNED_SOURCE_PATHS")
        expected[identity] = path
    pins = request.get("assembly_source_receipts")
    if not isinstance(pins, list) or not 1 <= len(pins) <= MAX_ARCHIVE_MANIFESTS + 5:
        raise SnapshotSkip("INVALID_ASSEMBLY_SOURCE_PINS")
    pinned = {}
    for pin in pins:
        if not isinstance(pin, Mapping) or set(pin) != {"path", "receipt_sha256"}:
            raise SnapshotSkip("INVALID_ASSEMBLY_SOURCE_PIN")
        name, digest = pin["path"], pin["receipt_sha256"]
        if (not isinstance(name, str) or not name or not isinstance(digest, str)
                or len(digest) != 64 or any(c not in SHA for c in digest)):
            raise SnapshotSkip("INVALID_ASSEMBLY_SOURCE_PIN")
        identity = str(Path(name).resolve())
        if identity in pinned:
            reason = "DUPLICATE_ASSEMBLY_SOURCE_PIN" if pinned[identity] == digest else "CONFLICTING_ASSEMBLY_SOURCE_PIN"
            raise SnapshotSkip(reason)
        pinned[identity] = digest
    if set(pinned) != set(expected):
        raise SnapshotSkip("ASSEMBLY_SOURCE_PIN_INVENTORY_MISMATCH")
    for identity, path in expected.items():
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_PINNED_RECEIPT_BYTES:
                raise SnapshotSkip("PINNED_SOURCE_RECEIPT_UNAVAILABLE")
            raw = path.read_bytes()
        except OSError as exc:
            raise SnapshotSkip("PINNED_SOURCE_RECEIPT_UNAVAILABLE") from exc
        if hashlib.sha256(raw).hexdigest() != pinned[identity]:
            raise SnapshotSkip("PINNED_SOURCE_RECEIPT_HASH_MISMATCH")


def _official_day(raw: bytes, day: date) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        raise SnapshotSkip("INVALID_SHFE_RAW_JSON") from exc
    if not isinstance(payload, dict) or payload.get("report_date") != day.strftime("%Y%m%d"):
        raise SnapshotSkip("SHFE_RAW_REPORT_DATE_MISMATCH")
    records = payload.get("o_curinstrument")
    if not isinstance(records, list):
        raise SnapshotSkip("MISSING_SHFE_CONTRACT_ROWS")
    result = []
    seen = set()
    for item in records:
        if not isinstance(item, Mapping) or str(item.get("PRODUCTID", "")).strip() != "au_f":
            continue
        month = str(item.get("DELIVERYMONTH", ""))
        if len(month) != 4 or not month.isdigit():
            continue
        contract = "au" + month
        if contract in seen:
            raise SnapshotSkip("DUPLICATE_SHFE_AU_CONTRACT")
        try:
            numbers = {key: float(item[name]) for key, name in {
                "open": "OPENPRICE", "high": "HIGHESTPRICE", "low": "LOWESTPRICE",
                "close": "CLOSEPRICE", "open_interest": "OPENINTEREST", "volume": "VOLUME"
            }.items()}
        except (KeyError, TypeError, ValueError):
            continue  # inactive contract row
        if (not all(math.isfinite(value) for value in numbers.values())
                or min(numbers["open"], numbers["high"], numbers["low"], numbers["close"]) <= 0
                or numbers["open_interest"] <= 0 or numbers["volume"] <= 0
                or not numbers["low"] <= min(numbers["open"], numbers["close"])
                or not max(numbers["open"], numbers["close"]) <= numbers["high"]):
            continue
        seen.add(contract)
        result.append({"date": day.isoformat(), "contract": contract, **numbers})
    if not result:
        raise SnapshotSkip("NO_TRADABLE_SHFE_AU_ROWS", day.isoformat())
    return sorted(result, key=lambda row: row["contract"])


def _archive(request: Mapping[str, Any], prior_days: list[date], decision_at: datetime) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    names = request.get("shfe_manifest_paths")
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_ARCHIVE_MANIFESTS:
        raise SnapshotSkip("MISSING_OR_UNBOUNDED_SHFE_ARCHIVE")
    by_day: dict[date, dict[str, Any]] = {}
    sources = []
    total = 0
    for name in names:
        path = Path(name)
        manifest, manifest_sha = _read_json(path, "shfe_manifest")
        if (manifest.get("schema_version") != "gold-au-shfe-daily-capture.v1" or
                manifest.get("mode") != "EXECUTE" or manifest.get("status") not in {"CAPTURED", "PARTIAL_FAILURE"}):
            raise SnapshotSkip("INVALID_SHFE_MANIFEST_KIND")
        reports = manifest.get("reports")
        if not isinstance(reports, list):
            raise SnapshotSkip("INVALID_SHFE_REPORT_INVENTORY")
        total += len(reports)
        if total > MAX_ARCHIVE_REPORTS:
            raise SnapshotSkip("UNBOUNDED_SHFE_REPORT_INVENTORY")
        sources.append({"manifest": str(path.resolve()), "manifest_sha256": manifest_sha})
        for report in reports:
            if not isinstance(report, Mapping):
                raise SnapshotSkip("INVALID_SHFE_REPORT")
            try:
                day = date.fromisoformat(report["date"])
            except (KeyError, TypeError, ValueError) as exc:
                raise SnapshotSkip("INVALID_SHFE_REPORT_DATE") from exc
            if day not in prior_days:
                continue
            if day in by_day:
                raise SnapshotSkip("DUPLICATE_SHFE_REPORT_DAY", day.isoformat())
            capture = _within_capture(report.get("captured_at"), decision_at, "shfe_capture")
            raw = _read_raw(report.get("raw_file"), report.get("raw_sha256"), path, "shfe")
            normalized = _official_day(raw, day)
            captured_rows = report.get("bars")
            if not isinstance(captured_rows, list) or len(captured_rows) != len(normalized):
                raise SnapshotSkip("SHFE_MANIFEST_RAW_DISAGREEMENT", day.isoformat())
            captured = {row.get("contract"): row for row in captured_rows if isinstance(row, Mapping)}
            if set(captured) != {row["contract"] for row in normalized}:
                raise SnapshotSkip("SHFE_CONTRACT_INVENTORY_DISAGREEMENT", day.isoformat())
            for bar in normalized:
                check = captured[bar["contract"]]
                for field in ("open", "high", "low", "close", "volume", "open_interest"):
                    try:
                        if float(check.get(field)) != bar[field]:
                            raise SnapshotSkip("SHFE_MANIFEST_RAW_DISAGREEMENT", day.isoformat())
                    except (TypeError, ValueError) as exc:
                        raise SnapshotSkip("SHFE_MANIFEST_RAW_DISAGREEMENT", day.isoformat()) from exc
                if check.get("source_sha256") != report["raw_sha256"]:
                    raise SnapshotSkip("SHFE_BAR_RAW_HASH_DISAGREEMENT")
            by_day[day] = {"captured_at": capture, "raw_sha256": report["raw_sha256"],
                           "source_ref": "https://www.shfe.com.cn/data/tradedata/future/dailydata/kx" + day.strftime("%Y%m%d") + ".dat",
                           "bars": normalized}
    missing = [day.isoformat() for day in prior_days if day not in by_day]
    if missing:
        raise SnapshotSkip("MISSING_REQUIRED_SHFE_SESSIONS", ",".join(missing[:5]))
    output = []
    for day in prior_days:
        source = by_day[day]
        captured_at = source["captured_at"].isoformat()
        for row in source["bars"]:
            output.append({**row,
                           # These placeholder costs are never used for the
                           # current decision. Only the selected prior-day
                           # contract receives witnessed current cost terms.
                           "margin_per_lot_cny": 1.0,
                           "fee_open_per_lot_cny": 0.0,
                           "fee_close_today_per_lot_cny": 0.0,
                           "fee_close_yesterday_per_lot_cny": 0.0,
                           "execution_cost_grade": "ASSUMPTION",
                           "execution_cost_basis": "HISTORICAL_NOT_USED_BY_LIVE_SIGNAL",
                           "first_published_at": captured_at, "retrieved_at": captured_at,
                           "available_at": captured_at,
                           "source_ref": source["source_ref"],
                           "vintage_id": "SHFE_WITNESSED_CAPTURE_" + source["raw_sha256"][:16],
                           "raw_sha256": source["raw_sha256"],
                           "pit_grade": "CONSERVATIVE", "vintage_kind": "REVISION",
                           "release_time_basis": "CAPTURE_UPPER_BOUND_NOT_FIRST_RELEASE"})
    return output, sources


def _fred_captures(path: Path, decision_at: datetime, mapping: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str]:
    manifest, manifest_sha = _read_json(path, "fred_manifest")
    if (manifest.get("schema_version") != "gold-macro-capture.v1" or manifest.get("status") != "CAPTURED"
            or manifest.get("provider_id") != "fred_graph_csv"):
        raise SnapshotSkip("INVALID_FRED_MANIFEST_KIND")
    captures = manifest.get("captures")
    if not isinstance(captures, list) or len(captures) != 2:
        raise SnapshotSkip("REQUIRE_BOTH_FRED_SERIES")
    observations = []
    seen = set()
    for capture in captures:
        series = capture.get("provider_series")
        if series not in {"DFII10", "DTWEXBGS"} or series in seen:
            raise SnapshotSkip("DUPLICATE_OR_WRONG_FRED_SERIES")
        seen.add(series)
        captured = _within_capture(capture.get("captured_at"), decision_at, "fred_capture")
        raw = _read_raw(capture.get("raw_file"), capture.get("raw_sha256"), path, "fred")
        source_url = capture.get("source_url")
        parsed = urlsplit(source_url if isinstance(source_url, str) else "")
        query = parse_qs(parsed.query)
        if parsed.scheme != "https" or parsed.hostname != "fred.stlouisfed.org" or parsed.path != "/graph/fredgraph.csv":
            raise SnapshotSkip("WRONG_FRED_SOURCE_URL")
        try:
            spec = MacroSpec(series, date.fromisoformat(query["cosd"][0]), date.fromisoformat(query["coed"][0]))
        except (KeyError, IndexError, ValueError) as exc:
            raise SnapshotSkip("WRONG_FRED_SOURCE_URL") from exc
        if spec.url() != source_url:
            raise SnapshotSkip("FRED_SOURCE_QUERY_MISMATCH")
        normalized = normalize_fred(raw, spec, captured_at=captured)
        expected = {key: value for key, value in capture.items() if key not in {"raw_file", "status"}}
        if normalized != expected:
            raise SnapshotSkip("FRED_MANIFEST_RAW_DISAGREEMENT", series)
        for source in normalized["observations"]:
            row = dict(source)
            if series == "DTWEXBGS":
                if source["series"] != mapping["source_series"] or source["measurement_regime"] != mapping["source_measurement_regime"]:
                    raise SnapshotSkip("H10_DISTRIBUTOR_MAPPING_MISMATCH")
                row["source_series"] = source["series"]
                row["series"] = mapping["strategy_series"]
                row["measurement_regime"] = mapping["strategy_measurement_regime"]
            elif source["series"] != "FRED:DFII10":
                raise SnapshotSkip("DFII10_SOURCE_ID_MISMATCH")
            # Never backdate the public CSV value to its observation date.
            row.update({"released_at": captured.isoformat(), "retrieved_at": captured.isoformat(),
                        "available_at": captured.isoformat(), "pit_grade": "CONSERVATIVE",
                        "vintage_kind": "REVISION", "release_time_basis": "CAPTURE_UPPER_BOUND_NOT_FIRST_RELEASE"})
            observations.append(row)
    if seen != {"DFII10", "DTWEXBGS"}:
        raise SnapshotSkip("REQUIRE_BOTH_FRED_SERIES")
    return observations, manifest_sha


def _mapping(path: Path, decision_at: datetime) -> tuple[dict[str, Any], str]:
    row, digest = _read_json(path, "h10_mapping")
    required = {"schema_version": "gold-h10-live-mapping.v1",
                "status": "WITNESSED_FOR_LIVE_PIT",
                "source_series": "FRED:DTWEXBGS",
                "source_measurement_regime": "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY",
                "strategy_series": "FED:H10:DTWEXBGS",
                "strategy_measurement_regime": "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY",
                "unit": "INDEX", "underlying_release": "FEDERAL_RESERVE_H10"}
    if any(row.get(key) != value for key, value in required.items()):
        raise SnapshotSkip("H10_LIVE_MAPPING_NOT_WITNESSED")
    if not isinstance(row.get("witnessed_by"), str) or not row["witnessed_by"]:
        raise SnapshotSkip("H10_MAPPING_WITNESS_MISSING")
    _within_capture(row.get("witnessed_at"), decision_at, "h10_mapping_witness")
    _receipt_source_raw(row, path, "h10_mapping")
    return row, digest


def _calendar(path: Path, decision_day: date, decision_at: datetime) -> tuple[list[date], dict[str, Any]]:
    row, digest = _read_json(path, "calendar")
    if row.get("schema_version") != "gold-au-shfe-calendar-receipt.v1" or row.get("source_kind") != "SHFE_OFFICIAL":
        raise SnapshotSkip("OFFICIAL_CALENDAR_RECEIPT_REQUIRED")
    _within_capture(row.get("witnessed_at"), decision_at, "calendar_witness")
    _receipt_source_raw(row, path, "calendar")
    try:
        validated = load_calendar_receipt(path, as_of=decision_at)
    except CalendarEvidenceError as exc:
        raise SnapshotSkip(exc.code, exc.detail) from exc
    if row != validated:
        raise SnapshotSkip("CALENDAR_SOURCE_CHANGED_DURING_VALIDATION")
    sessions = row.get("sessions")
    if not isinstance(sessions, list):
        raise SnapshotSkip("MISSING_EXCHANGE_SESSIONS")
    try:
        days = [date.fromisoformat(value) for value in sessions]
    except (TypeError, ValueError) as exc:
        raise SnapshotSkip("INVALID_EXCHANGE_SESSION_DATE") from exc
    if days != sorted(set(days)) or any(day.weekday() >= 5 for day in days):
        raise SnapshotSkip("UNSORTED_OR_WEEKEND_EXCHANGE_SESSION")
    if decision_day not in days:
        raise SnapshotSkip("DECISION_DAY_NOT_OFFICIAL_SESSION")
    return days, {"receipt_path": str(path.resolve()), "receipt_sha256": digest,
                  "source_raw_sha256": row["raw_sha256"]}


def _cost(path: Path, decision_at: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    row, digest = _read_json(path, "cost")
    if row.get("schema_version") != "gold-au-live-cost-receipt.v1" or row.get("source_kind") != "SHFE_AND_SIMNOW_CAPTURE":
        raise SnapshotSkip("ACTUAL_COST_MARGIN_RECEIPT_REQUIRED")
    captured = _within_capture(row.get("captured_at"), decision_at, "cost_capture")
    if captured.astimezone(SHANGHAI).date() != decision_at.astimezone(SHANGHAI).date():
        raise SnapshotSkip("STALE_COST_MARGIN_RECEIPT", "current Shanghai decision-day capture required")
    _receipt_source_raw(row, path, "cost")
    terms = row.get("contract_terms")
    if not isinstance(terms, list) or not terms:
        raise SnapshotSkip("MISSING_COST_CONTRACT_TERMS")
    by_contract = {}
    for term in terms:
        if not isinstance(term, Mapping) or term.get("contract") in by_contract:
            raise SnapshotSkip("DUPLICATE_OR_INVALID_COST_TERM")
        contract = term.get("contract")
        if not isinstance(contract, str) or not contract.startswith("au") or len(contract) != 6:
            raise SnapshotSkip("INVALID_COST_CONTRACT")
        numbers = {}
        for field in ("margin_per_lot_cny", "fee_open_per_lot_cny", "fee_close_today_per_lot_cny", "fee_close_yesterday_per_lot_cny"):
            try:
                numbers[field] = float(term[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise SnapshotSkip("INVALID_COST_VALUE", field) from exc
            if numbers[field] < 0 or (field == "margin_per_lot_cny" and numbers[field] == 0):
                raise SnapshotSkip("INVALID_COST_VALUE", field)
            if not math.isfinite(numbers[field]):
                raise SnapshotSkip("INVALID_COST_VALUE", field)
        by_contract[contract] = numbers
    return by_contract, {"receipt_path": str(path.resolve()), "receipt_sha256": digest,
                         "source_raw_sha256": row["raw_sha256"]}


def _wgc(path: Path | None, decision_at: datetime) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if path is None:
        return [], None
    row, digest = _read_json(path, "wgc")
    if row.get("schema_version") != "gold-wgc-manual-witness.v1" or row.get("source_kind") != "WGC_PRIMARY":
        raise SnapshotSkip("INVALID_WGC_WITNESS")
    _within_capture(row.get("witnessed_at"), decision_at, "wgc_witness")
    _receipt_source_raw(row, path, "wgc")
    values = row.get("observations")
    if not isinstance(values, list) or len(values) > 6:
        raise SnapshotSkip("INVALID_WGC_OBSERVATIONS")
    result = []
    for value in values:
        if not isinstance(value, Mapping):
            raise SnapshotSkip("INVALID_WGC_OBSERVATION")
        try:
            day = date.fromisoformat(value["observed_on"])
            tonnes = float(value["net_tonnes"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SnapshotSkip("INVALID_WGC_OBSERVATION") from exc
        if not math.isfinite(tonnes):
            raise SnapshotSkip("INVALID_WGC_OBSERVATION")
        captured = row["witnessed_at"]
        result.append({"series": "WGC:GLOBAL_OFFICIAL_NET_PURCHASES", "unit": "TONNES",
                       "measurement_regime": DEFAULT_CONFIG["measurement_regimes"]["WGC:GLOBAL_OFFICIAL_NET_PURCHASES"],
                       "observed_on": day.isoformat(), "value": tonnes,
                       "released_at": captured, "retrieved_at": captured, "available_at": captured,
                       "source_ref": row.get("source_ref", str(path.resolve())),
                       "vintage_id": "WGC_WITNESSED_" + row["raw_sha256"][:12],
                       "raw_sha256": row["raw_sha256"], "pit_grade": "CONSERVATIVE",
                       "vintage_kind": "REVISION", "release_time_basis": "WITNESS_UPPER_BOUND_NOT_FIRST_RELEASE"})
    return result, {"receipt_path": str(path.resolve()), "receipt_sha256": digest}


def prepare_live_snapshot(request: Mapping[str, Any], *, as_of: datetime) -> dict[str, Any]:
    """Return a strict signal+dataset or an explicit skip; no side effects."""
    try:
        if not isinstance(request, Mapping) or request.get("schema_version") != "gold-au-live-snapshot-request.v1":
            raise SnapshotSkip("INVALID_SNAPSHOT_REQUEST")
        execution_mode = request.get("execution_mode", "COST_CHECKED_RESEARCH")
        if not isinstance(execution_mode, str) or execution_mode not in {"RESEARCH_ONLY", "COST_CHECKED_RESEARCH"}:
            raise SnapshotSkip("INVALID_EXECUTION_MODE")
        research_only = execution_mode == "RESEARCH_ONLY"
        if research_only and "cost_receipt_path" in request:
            raise SnapshotSkip("RESEARCH_ONLY_CANNOT_ASSERT_EXECUTION_COST")
        when = _time(as_of, "as_of")
        local = when.astimezone(SHANGHAI)
        if not time(8, 10) <= local.timetz().replace(tzinfo=None) <= time(8, 30):
            raise SnapshotSkip("OUTSIDE_0810_0830_WINDOW")
        day = local.date()
        if request.get("decision_date") != day.isoformat():
            raise SnapshotSkip("DECISION_DATE_MISMATCH")
        decision_at = datetime.combine(day, time(8, 30), SHANGHAI).astimezone(timezone.utc)
        if when < decision_at:
            return {"schema_version": "gold-au-live-snapshot.v1", "status": "COLLECTING_BEFORE_DECISION",
                    "as_of": when.isoformat(), "broker_action_authorized": False}
        _verify_source_pins(request)
        required_paths = ["calendar_receipt_path", "fred_manifest_path", "h10_mapping_receipt_path"]
        if not research_only:
            required_paths.append("cost_receipt_path")
        for key in required_paths:
            if not isinstance(request.get(key), str) or not request[key]:
                raise SnapshotSkip("MISSING_" + key.upper())
        calendar, calendar_ref = _calendar(Path(request["calendar_receipt_path"]), day, when)
        index = calendar.index(day)
        if index < MIN_PRIOR_SESSIONS:
            raise SnapshotSkip("INSUFFICIENT_OFFICIAL_SESSION_HISTORY", str(index))
        prior = calendar[index - MIN_PRIOR_SESSIONS:index]
        bars, shfe_sources = _archive(request, prior, when)
        mapping, mapping_sha = _mapping(Path(request["h10_mapping_receipt_path"]), when)
        macro, macro_sha = _fred_captures(Path(request["fred_manifest_path"]), when, mapping)
        by_series = {series: [row for row in macro if row["series"] == series] for series in ("FRED:DFII10", "FED:H10:DTWEXBGS")}
        for series, rows in by_series.items():
            if len(rows) < 20:
                raise SnapshotSkip("INSUFFICIENT_" + series.replace(":", "_") + "_ROWS")
            newest = max(date.fromisoformat(row["observed_on"]) for row in rows)
            if (day - newest).days > DEFAULT_CONFIG["macro_max_age_calendar_days"]:
                raise SnapshotSkip("STALE_" + series.replace(":", "_") + "_OBSERVATION", newest.isoformat())
        terms, cost_ref = ({}, None) if research_only else _cost(Path(request["cost_receipt_path"]), when)
        wgc, wgc_ref = _wgc(Path(request["wgc_receipt_path"]) if request.get("wgc_receipt_path") else None, when)
        dataset = {"price_quality": {"status": "LIVE_SOURCE_CHECKED",
                                     "audit_ref": "SHFE_RAW_HASH_AND_NORMALIZER_" + canonical_hash(shfe_sources),
                                     "scope": "PRIOR_OFFICIAL_REPORTS_ONLY"},
                   "exchange_sessions": [d.isoformat() for d in calendar[:index + 1]],
                   "exchange_calendar_ref": calendar_ref["receipt_path"],
                   "bars": bars, "observations": macro + wgc,
                   "execution_cost_status": "DEFERRED_TO_EXECUTION_GATE" if research_only else "WITNESSED",
                   "purpose": "STRICT_0830_LIVE_SNAPSHOT_ONLY_NOT_HISTORICAL_BACKTEST"}
        preliminary = GoldAuDataset(dataset)
        path = build_current_snapshot_path(preliminary, as_of=when)
        if not path or path[-1].decision_date != day or path[-1].contract is None:
            raise SnapshotSkip("NO_ELIGIBLE_OFFICIAL_AU_CONTRACT")
        selected = path[-1].contract
        if not research_only and selected not in terms:
            raise SnapshotSkip("MISSING_SELECTED_CONTRACT_COST_MARGIN", selected)
        for bar in bars:
            if not research_only and bar["date"] == prior[-1].isoformat() and bar["contract"] == selected:
                bar.update(terms[selected])
                bar["execution_cost_grade"] = "CONSERVATIVE"
                bar["execution_cost_basis"] = "ACTUAL_WITNESSED_AS_OF_DECISION"
                bar["execution_cost_receipt_sha256"] = cost_ref["receipt_sha256"]
                break
        final_dataset = GoldAuDataset(dataset)
        signal = evaluate_current_snapshot_signal(final_dataset, as_of=when)
        _verify_source_pins(request)
        return {"schema_version": "gold-au-live-snapshot.v1", "status": "READY_STRICT_RESEARCH_SIGNAL",
                "as_of": when.isoformat(), "decision_at": decision_at.isoformat(),
                "execution_mode": execution_mode,
                "dataset_sha256": canonical_hash(dataset), "dataset": dataset, "signal": signal,
                "source_receipts": {"shfe": shfe_sources, "fred_manifest_sha256": macro_sha,
                                    "h10_mapping_sha256": mapping_sha, "calendar": calendar_ref,
                                    "cost": cost_ref, "wgc": wgc_ref},
                "external_witness_authentication": "NOT_VERIFIED_BY_OFFLINE_MODULE",
                "broker_action_authorized": False}
    except SnapshotSkip as exc:
        return {"schema_version": "gold-au-live-snapshot.v1", "status": "SKIPPED",
                "reason": exc.code, "detail": exc.detail, "broker_action_authorized": False}
