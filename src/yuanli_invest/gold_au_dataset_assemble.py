"""Assemble private retrospective AU/FRED evidence into GOLD2 strategy rows.

Source bytes and normalized captures are checked against each other.  Every
historical bar and observation remains UNKNOWN PIT / UNKNOWN vintage: capture
in September 2026 is the first *proved* availability, not historical release.
The returned dataset is research-only and quality-blocked for trading claims.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from .gold_macro_capture import MacroSpec, normalize_raw as normalize_macro
from .youquant_au_history import RequestSpec, normalize_raw as normalize_au


AU_MANIFEST_SCHEMA = "gold-au-history-capture.v1"
MACRO_MANIFEST_SCHEMA = "gold-macro-capture.v1"
SHFE_MANIFEST_SCHEMA = "gold-au-shfe-daily-capture.v1"
MAPPING_SCHEMA = "gold-h10-source-mapping.v1"
DATASET_SCHEMA = "gold-au-reconstructed-dataset.v1"
SHANGHAI = ZoneInfo("Asia/Shanghai")


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value, hashlib.sha256(raw).hexdigest()


def _captured(value: Any, label: str, assembled_at: datetime) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} has no timezone")
    parsed = parsed.astimezone(timezone.utc)
    if parsed > assembled_at:
        raise ValueError(f"{label} is after assembly time")
    return parsed


def _read_raw(capture: Mapping[str, Any], manifest_path: Path) -> bytes:
    raw_name = capture.get("raw_file")
    expected = capture.get("raw_sha256")
    if not isinstance(raw_name, str) or not isinstance(expected, str) or len(expected) != 64:
        raise ValueError("raw file/hash missing")
    raw_dir = (manifest_path.parent / "raw").resolve()
    path = Path(raw_name).resolve()
    if path.parent != raw_dir or not path.is_file():
        raise ValueError("raw file outside immutable capture directory or missing")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("raw SHA256 mismatch")
    return raw


def _au_spec(capture: Mapping[str, Any]) -> RequestSpec:
    url = urlsplit(str(capture.get("request_url", "")))
    if url.scheme != "https" or url.hostname != "q.youquant.com" or url.path != "/data/history":
        raise ValueError("unexpected dated AU source URL")
    query = parse_qs(url.query, strict_parsing=True)
    try:
        symbol = query["symbol"][0]
        start = datetime.fromtimestamp(int(query["from"][0]), SHANGHAI).date()
        end_exclusive = datetime.fromtimestamp(int(query["to"][0]), SHANGHAI).date()
    except (KeyError, IndexError, ValueError) as exc:
        raise ValueError("incomplete AU request identity") from exc
    spec = RequestSpec(symbol, start, end_exclusive)
    if spec.url() != capture["request_url"] or capture.get("requested_symbol") != symbol:
        raise ValueError("AU request URL and normalized symbol disagree")
    return spec


def _macro_spec(capture: Mapping[str, Any]) -> MacroSpec:
    url = urlsplit(str(capture.get("source_url", "")))
    if url.scheme != "https" or url.hostname != "fred.stlouisfed.org" or url.path != "/graph/fredgraph.csv":
        raise ValueError("unexpected FRED source URL")
    query = parse_qs(url.query, strict_parsing=True)
    try:
        spec = MacroSpec(query["id"][0], date.fromisoformat(query["cosd"][0]), date.fromisoformat(query["coed"][0]))
    except (KeyError, IndexError, ValueError) as exc:
        raise ValueError("incomplete FRED request identity") from exc
    if spec.url() != capture["source_url"] or spec.provider_series != capture.get("provider_series"):
        raise ValueError("FRED request URL and normalized series disagree")
    return spec


def _checked_decimal(value: Any, field: str, *, positive: bool = True) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field} invalid")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} invalid") from exc
    if not result.is_finite() or (result <= 0 if positive else result < 0):
        raise ValueError(f"{field} invalid")
    return result


def _strategy_bar(source: Mapping[str, Any], *, captured_at: str, source_ref: str,
                  raw_sha256: str, provider_id: str) -> dict[str, Any]:
    if source.get("source_sha256") != raw_sha256:
        raise ValueError("bar source SHA differs from raw capture")
    day = date.fromisoformat(source["date"])
    if day.weekday() >= 5:
        raise ValueError("weekend bar reached strategy conversion")
    opening = _checked_decimal(source["open"], "open")
    high = _checked_decimal(source["high"], "high")
    low = _checked_decimal(source["low"], "low")
    close = _checked_decimal(source["close"], "close")
    if not low <= min(opening, close) <= max(opening, close) <= high:
        raise ValueError("OHLC relationship invalid")
    oi = _checked_decimal(source["open_interest"], "open_interest", positive=False)
    volume = _checked_decimal(source["volume"], "volume", positive=False)
    margin = close * Decimal("1000") * Decimal("0.20")
    return {
        "contract": source["contract"], "date": day.isoformat(),
        "open": float(opening), "high": float(high), "low": float(low), "close": float(close),
        "open_interest": float(oi), "volume": float(volume),
        "margin_per_lot_cny": float(margin),
        "fee_open_per_lot_cny": 40.0,
        "fee_close_today_per_lot_cny": 40.0,
        "fee_close_yesterday_per_lot_cny": 40.0,
        "execution_cost_grade": "ASSUMPTION",
        "first_published_at": captured_at,
        "retrieved_at": captured_at,
        "available_at": captured_at,
        "vintage_id": provider_id.upper() + "_LATEST_CAPTURE_" + raw_sha256[:16],
        "vintage_kind": "UNKNOWN", "pit_grade": "UNKNOWN",
        "raw_sha256": raw_sha256, "source_ref": source_ref,
        "source_provider_id": provider_id,
        "release_time_basis": "FIRST_KNOWN_AT_CAPTURE_NOT_ACTUAL_PUBLICATION",
    }


def _official_bars(raw: bytes, day: str) -> dict[str, dict[str, str]]:
    payload = json.loads(raw)
    rows = payload.get("o_curinstrument")
    if not isinstance(rows, list):
        raise ValueError("SHFE official daily source missing contract rows")
    result: dict[str, dict[str, str]] = {}
    for item in rows:
        if not isinstance(item, dict) or str(item.get("PRODUCTID", "")).strip() != "au_f":
            continue
        month = str(item.get("DELIVERYMONTH", ""))
        if len(month) != 4 or not month.isdigit():
            continue
        contract = "au" + month
        try:
            values = {name: _checked_decimal(item[key], name, positive=name not in {"volume", "open_interest"})
                      for name, key in {
                          "open": "OPENPRICE", "high": "HIGHESTPRICE", "low": "LOWESTPRICE", "close": "CLOSEPRICE",
                          "volume": "VOLUME", "open_interest": "OPENINTEREST",
                      }.items()}
        except (KeyError, ValueError):
            continue  # inactive official row, not a tradable bar
        if values["volume"] <= 0 or values["open_interest"] <= 0:
            continue
        if not values["low"] <= min(values["open"], values["close"]) <= max(values["open"], values["close"]) <= values["high"]:
            continue
        if contract in result:
            raise ValueError("duplicate official AU contract")
        result[contract] = {"date": day, "contract": contract,
                            **{name: str(value) for name, value in values.items()}}
    if not result:
        raise ValueError("official SHFE day contains no valid AU bars")
    return result


def _mapping(path: Path) -> tuple[dict[str, Any], str]:
    mapping, digest = _read_json(path)
    exact = {
        "schema_version": MAPPING_SCHEMA,
        "status": "EXPLICIT_RETROSPECTIVE_ALIAS_ONLY",
        "source_provider_id": "fred_graph_csv",
        "source_series": "FRED:DTWEXBGS",
        "source_measurement_regime": "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY",
        "strategy_series": "FED:H10:DTWEXBGS",
        "strategy_measurement_regime": "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY",
        "unit": "INDEX",
        "underlying_release": "FEDERAL_RESERVE_H10",
        "allowed_use": "RETROSPECTIVE_EXPLORATORY_RESEARCH_ONLY",
        "historical_release_time_verified": False,
        "pit_grade": "UNKNOWN",
        "vintage_kind": "UNKNOWN",
        "action_authority": "none",
    }
    if any(mapping.get(key) != expected for key, expected in exact.items()) or not mapping.get("identity_basis"):
        raise ValueError("FRED-to-H10 mapping not explicitly frozen for retrospective use")
    return mapping, digest


def assemble_dataset(
    *,
    au_manifest_path: Path,
    macro_manifest_path: Path | None,
    shfe_manifest_path: Path | None,
    h10_mapping_path: Path,
    audit_report_path: Path,
    assembled_at: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify original source bytes, quarantine bad dates, then assemble rows."""
    now = assembled_at or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("assembly time must have timezone")
    now = now.astimezone(timezone.utc)
    mapping, mapping_hash = _mapping(h10_mapping_path)
    au, au_hash = _read_json(au_manifest_path)
    if au.get("schema_version") != AU_MANIFEST_SCHEMA or au.get("status") != "CAPTURED" or au.get("provider_id") != "youquant_history" or au.get("historical_release_time_verified") is not False:
        raise ValueError("complete retrospective dated AU manifest required")
    _captured(au.get("captured_at"), "AU manifest capture", now)
    audit, audit_hash = _read_json(audit_report_path)
    if audit.get("schema_version") != "gold-au-shfe-contract-sample-audit.v1" or audit.get("provider_manifest_sha256") != au_hash:
        raise ValueError("sample audit does not reference this AU manifest")
    vendor: dict[tuple[str, str], dict[str, Any]] = {}
    weekend_quarantine: list[dict[str, str]] = []
    hashes_verified = 0
    captures = au.get("captures")
    requested_contracts = au.get("requested_contracts")
    if (not isinstance(captures, list) or not isinstance(requested_contracts, list)
            or not requested_contracts or len(requested_contracts) != len(set(requested_contracts))
            or len(captures) != len(requested_contracts)):
        raise ValueError("AU capture inventory incomplete")
    captured_contracts: set[str] = set()
    for capture in captures:
        spec = _au_spec(capture)
        if spec.symbol in captured_contracts:
            raise ValueError("duplicate AU captured contract")
        captured_contracts.add(spec.symbol)
        raw = _read_raw(capture, au_manifest_path)
        hashes_verified += 1
        observed = normalize_au(raw, spec, captured_at=capture["captured_at"])
        normalized_capture = {key: value for key, value in capture.items() if key != "raw_file"}
        if observed != normalized_capture:
            raise ValueError("AU normalized capture differs from verified raw source")
        _captured(capture["captured_at"], "AU row capture", now)
        for bar in capture["bars"]:
            day = date.fromisoformat(bar["date"])
            if day.weekday() >= 5:
                weekend_quarantine.append({"date": bar["date"], "contract": bar["contract"], "reason": "WEEKEND_PROVIDER_LABEL"})
                continue
            key = (bar["date"], bar["contract"])
            if key in vendor:
                raise ValueError("duplicate dated AU bar across captures")
            vendor[key] = _strategy_bar(bar, captured_at=capture["captured_at"],
                                        source_ref=capture["request_url"], raw_sha256=capture["raw_sha256"],
                                        provider_id="youquant_history")
    if captured_contracts != set(requested_contracts):
        raise ValueError("AU captured contract identities differ from requested inventory")

    official_by_day: dict[str, dict[str, dict[str, Any]]] = {}
    shfe_errors: list[str] = []
    shfe_hash = None
    if shfe_manifest_path is not None:
        shfe, shfe_hash = _read_json(shfe_manifest_path)
        if (shfe.get("schema_version") != SHFE_MANIFEST_SCHEMA or shfe.get("mode") != "EXECUTE"
                or shfe.get("historical_release_time_verified") is not False
                or shfe.get("status") not in {"CAPTURED", "PARTIAL_FAILURE"}):
            raise ValueError("SHFE retrospective daily manifest required")
        _captured(shfe.get("captured_at"), "SHFE manifest capture", now)
        interval = shfe.get("interval")
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError("SHFE capture interval missing")
        start, end = (date.fromisoformat(item) for item in interval)
        if start > end:
            raise ValueError("SHFE capture interval invalid")
        expected_days = {day for day, _ in vendor if start <= date.fromisoformat(day) <= end}
        if not isinstance(shfe.get("reports"), list) or not isinstance(shfe.get("errors"), list):
            raise ValueError("SHFE report/error inventory missing")
        if shfe.get("requested_days") != len(expected_days):
            raise ValueError("SHFE requested day count differs from AU source inventory")
        for failure in shfe.get("errors", []):
            shfe_errors.append(date.fromisoformat(failure["date"]).isoformat())
        if len(shfe_errors) != len(set(shfe_errors)):
            raise ValueError("duplicate SHFE error date")
        if (shfe.get("status") == "CAPTURED") != (len(shfe_errors) == 0):
            raise ValueError("SHFE status/error inventory mismatch")
        for report in shfe.get("reports", []):
            day = date.fromisoformat(report["date"])
            if day.weekday() >= 5 or report["date"] in official_by_day or report["date"] in shfe_errors:
                raise ValueError("invalid or duplicate official report day")
            raw = _read_raw(report, shfe_manifest_path)
            hashes_verified += 1
            _captured(report["captured_at"], "SHFE report capture", now)
            source_rows = _official_bars(raw, report["date"])
            reported = {bar["contract"]: bar for bar in report["bars"]}
            if len(reported) != len(report["bars"]) or set(reported) != set(source_rows):
                raise ValueError("SHFE manifest contract inventory differs from raw source")
            official_by_day[report["date"]] = {}
            for contract, parsed in source_rows.items():
                normalized = reported[contract]
                if any(str(normalized.get(key)) != str(value) for key, value in parsed.items()):
                    raise ValueError("SHFE normalized report differs from raw source")
                if normalized.get("source_sha256") != report["raw_sha256"]:
                    raise ValueError("SHFE bar hash mismatch")
                official_by_day[report["date"]][contract] = _strategy_bar(
                    normalized, captured_at=report["captured_at"],
                    source_ref="https://www.shfe.com.cn/data/tradedata/future/dailydata/kx" + day.strftime("%Y%m%d") + ".dat",
                    raw_sha256=report["raw_sha256"], provider_id="shfe_official_daily",
                )
        if set(official_by_day) | set(shfe_errors) != expected_days:
            raise ValueError("SHFE report/error dates do not cover requested AU dates exactly")

    common_keys = {(day, contract) for day, contracts in official_by_day.items()
                   for contract in contracts if (day, contract) in vendor}
    fields = ("open", "high", "low", "close", "volume", "open_interest")
    official_vendor_comparison = {
        "common_contract_day_bars": len(common_keys),
        "field_mismatch_counts": {
            field: sum(Decimal(str(vendor[key][field])) != Decimal(str(
                official_by_day[key[0]][key[1]][field])) for key in common_keys)
            for field in fields
        },
        "official_only_contract_day_bars": sum(
            (day, contract) not in vendor for day, contracts in official_by_day.items()
            for contract in contracts
        ),
        "vendor_only_on_official_report_day_bars": sum(
            day in official_by_day and contract not in official_by_day[day]
            for day, contract in vendor
        ),
    }

    rows_by_day: dict[str, dict[str, dict[str, Any]]] = {}
    quarantined_error_bars = 0
    for (day, contract), bar in vendor.items():
        if day in shfe_errors:
            quarantined_error_bars += 1
            continue
        if day in official_by_day:
            continue  # official report replaces the entire vendor day
        rows_by_day.setdefault(day, {})[contract] = bar
    for day, official in official_by_day.items():
        rows_by_day[day] = official
    bars = [rows_by_day[day][contract] for day in sorted(rows_by_day) for contract in sorted(rows_by_day[day])]

    observations: list[dict[str, Any]] = []
    macro_hash = None
    macro_status = "MISSING_CAPTURE"
    if macro_manifest_path is not None:
        macro, macro_hash = _read_json(macro_manifest_path)
        if macro.get("schema_version") != MACRO_MANIFEST_SCHEMA or macro.get("status") != "CAPTURED" or macro.get("provider_id") != "fred_graph_csv" or macro.get("historical_release_time_verified") is not False:
            raise ValueError("complete retrospective FRED macro capture required")
        _captured(macro.get("captured_at"), "macro manifest capture", now)
        series_seen: set[str] = set()
        for capture in macro.get("captures", []):
            raw = _read_raw(capture, macro_manifest_path)
            hashes_verified += 1
            spec = _macro_spec(capture)
            if spec.provider_series in series_seen:
                raise ValueError("duplicate FRED macro capture")
            series_seen.add(spec.provider_series)
            capture_at = _captured(capture["captured_at"], "macro row capture", now)
            observed = normalize_macro(raw, spec, captured_at=capture_at)
            normalized_capture = {key: value for key, value in capture.items() if key not in {"raw_file", "status"}}
            if observed != normalized_capture:
                raise ValueError("macro normalized capture differs from verified raw source")
            for row in capture["observations"]:
                if row["pit_grade"] != "UNKNOWN" or row["vintage_kind"] != "UNKNOWN":
                    raise ValueError("macro vintage/PIT claim exceeds source")
                admitted = dict(row)
                if spec.provider_series == "DTWEXBGS":
                    if row["series"] != mapping["source_series"] or row["measurement_regime"] != mapping["source_measurement_regime"] or row["unit"] != mapping["unit"]:
                        raise ValueError("FRED H10 alias source mismatch")
                    admitted["source_series"] = row["series"]
                    admitted["source_measurement_regime"] = row["measurement_regime"]
                    admitted["series"] = mapping["strategy_series"]
                    admitted["measurement_regime"] = mapping["strategy_measurement_regime"]
                    admitted["mapping_ref"] = str(h10_mapping_path.resolve())
                    admitted["mapping_sha256"] = mapping_hash
                elif row["series"] != "FRED:DFII10":
                    raise ValueError("DFII10 source identity mismatch")
                observations.append(admitted)
        if series_seen != {"DFII10", "DTWEXBGS"}:
            raise ValueError("both frozen macro series are required")
        macro_status = "LATEST_VINTAGE_ONLY"

    official_retained_bars = sum(bar["source_provider_id"] == "shfe_official_daily" for bar in bars)
    vendor_retained_bars = len(bars) - official_retained_bars
    all_retained_bars_official = bool(bars) and vendor_retained_bars == 0
    price_quality = {
        "status": ("OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED" if all_retained_bars_official
                   else "UNVERIFIED_VENDOR_OHLC"),
        "audit_ref": str(audit_report_path.resolve()),
        "audit_sha256": audit_hash,
        "audit_scope": "VENDOR_SAMPLE_COMPARISON_NOT_OFFICIAL_FULL_HISTORY_CERTIFICATION",
        "reason": (
            "All retained AU daily OHLC bars are from SHA-verified SHFE reports; "
            "SHFE HTTP-error dates were excluded. Historical first publication/availability, "
            "intraday execution path and actual costs remain unverified."
            if all_retained_bars_official else
            "Retained AU bars include vendor OHLC with unresolved source mismatches; "
            "historical first publication/availability, intraday execution path and costs remain unverified."
        ),
        "retained_bar_source_coverage": ("ALL_OFFICIAL_SHFE_DAILY" if all_retained_bars_official
                                         else "MIXED_OFFICIAL_AND_VENDOR_OR_VENDOR_ONLY"),
        "official_retained_bars": official_retained_bars,
        "vendor_retained_bars": vendor_retained_bars,
        "official_report_days": len(official_by_day),
        "shfe_http_error_dates_excluded": len(shfe_errors),
        "official_repair_days": len(official_by_day),
    }
    dataset = {
        "schema_version": DATASET_SCHEMA,
        "authority": "RETROSPECTIVE_EXPLORATORY_RESEARCH_ONLY",
        "action_authority": "none",
        "assembled_at": now.isoformat(),
        "price_quality": price_quality,
        "cost_assumptions": {"margin_fraction_of_notional": 0.20, "fee_cny_per_side": 40.0, "grade": "ASSUMPTION"},
        "bars": bars,
        "observations": observations,
    }
    report = {
        "schema_version": "gold-au-dataset-assembly-report.v1",
        "status": "DATA_QUALITY_BLOCKED" if macro_status != "MISSING_CAPTURE" else "INCOMPLETE_MACRO_AND_DATA_QUALITY_BLOCKED",
        "assembled_at": now.isoformat(),
        "raw_sha_verified_count": hashes_verified,
        "au_manifest_sha256": au_hash,
        "macro_manifest_sha256": macro_hash,
        "shfe_manifest_sha256": shfe_hash,
        "h10_mapping_sha256": mapping_hash,
        "audit_report_sha256": audit_hash,
        "vendor_bars_before_quarantine": len(vendor),
        "weekend_quarantine_count": len(weekend_quarantine),
        "weekend_quarantine": weekend_quarantine,
        "shfe_error_dates_quarantined": sorted(shfe_errors),
        "shfe_error_date_count": len(shfe_errors),
        "shfe_error_vendor_bars_quarantined": quarantined_error_bars,
        "official_repair_days": len(official_by_day),
        "official_repair_bars": sum(map(len, official_by_day.values())),
        "official_retained_bars": official_retained_bars,
        "vendor_retained_bars": vendor_retained_bars,
        "retained_bar_source_coverage": price_quality["retained_bar_source_coverage"],
        "official_vendor_comparison": official_vendor_comparison,
        "vendor_contract_metadata_unusable_count": len(captures),
        "assembled_bars": len(bars),
        "macro_observations": len(observations),
        "macro_status": macro_status,
        "wgc_historical_observations": 0,
        "price_quality": price_quality,
        "pit_grade": "UNKNOWN",
        "vintage_kind": "UNKNOWN",
        "historical_release_time_verified": False,
        "cost_grade": "ASSUMPTION",
        "action_authority": "none",
    }
    return dataset, report
