"""SHFE annual-notice calendar; source bytes, never market-data dates.

The annual notices establish a planned calendar within explicitly covered
years. Unknown years and non-session decisions fail closed. This module has
no broker, scheduler, credential, or trading operation.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import ssl
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

SOURCES = {
    2025: "https://www.shfe.com.cn/publicnotice/notice/202412/t20241223_824109.html",
    2026: "https://www.shfe.com.cn/publicnotice/notice/202512/t20251217_829805.html",
}
# Independently read annual notice facts frozen on 2026-09-26. Formatting may
# change; any semantic change requires a new source audit and code review.
# These are canonical JSON digests of year/URL/publication date/holiday and
# night dates, rather than receipt-provided hashes or market-data calendars.
AUDITED_NOTICE_FACTS_SHA256 = {
    2025: "71fc606359fde3efc3e412d8a5c5ffe68edb24f9743a5573f71aac443382f076",
    2026: "6b6887b469203dc22a44e33c71fd7046671c159047850851ed73bcc24dff0ecf",
}
EXPECTED_LABELS = {
    2025: ["元旦", "春节", "清明节", "劳动节", "端午节", "国庆节、中秋节"],
    2026: ["元旦", "春节", "清明节", "劳动节", "端午节", "中秋节", "国庆节"],
}
MAX_RAW_BYTES = 1_000_000
DATE_TOKEN = r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日（星期([一二三四五六日天])）"


class CalendarEvidenceError(ValueError):
    def __init__(self, code: str, detail: str = ""):
        self.code, self.detail = code, detail
        super().__init__(code + (": " + detail if detail else ""))


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.title_parts = [], []
        self.ignored = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignored = max(0, self.ignored - 1)
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)
            if self.in_title:
                self.title_parts.append(data)


def _instant(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise CalendarEvidenceError("INVALID_CALENDAR_CAPTURE_TIME") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise CalendarEvidenceError("NAIVE_CALENDAR_CAPTURE_TIME")
    return result.astimezone(timezone.utc)


def _day(groups, default_year: int) -> date:
    year, month, day, weekday = groups
    try:
        result = date(int(year or default_year), int(month), int(day))
    except ValueError as exc:
        raise CalendarEvidenceError("INVALID_NOTICE_DATE") from exc
    if "一二三四五六日"[result.weekday()] != weekday.replace("天", "日"):
        raise CalendarEvidenceError("NOTICE_WEEKDAY_MISMATCH", result.isoformat())
    return result


def parse_annual_notice(raw: bytes, year: int, source_ref: str) -> dict:
    if SOURCES.get(year) != source_ref or year not in EXPECTED_LABELS:
        raise CalendarEvidenceError("UNSUPPORTED_SHFE_CALENDAR_SOURCE")
    if not raw or len(raw) > MAX_RAW_BYTES:
        raise CalendarEvidenceError("INVALID_CALENDAR_RAW_SIZE")
    parser = _Text()
    try:
        parser.feed(raw.decode("utf-8"))
    except UnicodeError as exc:
        raise CalendarEvidenceError("INVALID_CALENDAR_RAW_ENCODING") from exc
    compact = lambda value: re.sub(r"\s+", "", value)
    if compact("".join(parser.title_parts)) != f"上海期货交易所关于{year}年休市安排的公告":
        raise CalendarEvidenceError("ANNUAL_NOTICE_TITLE_MISMATCH")
    text = compact("".join(parser.parts))
    intro = f"根据中国证监会有关通知精神，现就上海期货交易所{year}年休市安排公告如下："
    if text.count(intro) != 1 or "请各有关单位和广大投资者" not in text:
        raise CalendarEvidenceError("ANNUAL_NOTICE_BODY_MISMATCH")
    body = text.split(intro)[1].split("请各有关单位和广大投资者")[0]
    pieces = re.split(r"[一二三四五六七]、", body)
    if pieces[0] or len(pieces) - 1 != len(EXPECTED_LABELS[year]):
        raise CalendarEvidenceError("ANNUAL_NOTICE_SECTION_COUNT_MISMATCH")
    holidays, night_dates, labels = [], [], []
    for piece in pieces[1:]:
        if "：" not in piece:
            raise CalendarEvidenceError("INVALID_NOTICE_SECTION")
        label, sentence = piece.split("：", 1)
        labels.append(label)
        pattern = r"^" + DATE_TOKEN + r"(?:至" + DATE_TOKEN + r")?休市，" + DATE_TOKEN + r"起照常开市。"
        match = re.match(pattern, sentence)
        if match is None:
            raise CalendarEvidenceError("UNPARSED_HOLIDAY_INTERVAL", label)
        start = _day(match.groups()[:4], year)
        end = _day(match.groups()[4:8], year) if match.group(6) is not None else start
        reopen = _day(match.groups()[8:12], year)
        if start.year != year or end.year != year or not start <= end < reopen or reopen.weekday() >= 5:
            raise CalendarEvidenceError("INVALID_HOLIDAY_INTERVAL", label)
        # The gap until reopening must consist only of ordinary weekend days.
        gap = end + timedelta(days=1)
        while gap < reopen:
            if gap.weekday() < 5:
                raise CalendarEvidenceError("UNEXPLAINED_REOPEN_GAP", label)
            gap += timedelta(days=1)
        rest = sentence[match.end():]
        night = re.search(DATE_TOKEN + r"晚上不进行夜盘交易。$", rest)
        if night is None:
            raise CalendarEvidenceError("MISSING_NIGHT_CLOSURE", label)
        night_day = _day(night.groups(), year)
        if night_day >= start or (start - night_day).days > 3 or night_day.weekday() >= 5:
            raise CalendarEvidenceError("INVALID_NIGHT_CLOSURE", label)
        weekend = rest[:night.start()]
        if weekend:
            if not weekend.endswith("为周末休市。"):
                raise CalendarEvidenceError("UNPARSED_NOTICE_SUFFIX", label)
            listing = weekend[:-len("为周末休市。")]
            for token in listing.split("、"):
                found = re.fullmatch(DATE_TOKEN, token)
                if found is None or _day(found.groups(), year).weekday() < 5:
                    raise CalendarEvidenceError("NON_WEEKEND_MAKEUP_SESSION", label)
        holidays.append({"name": label, "start": start.isoformat(), "end": end.isoformat(), "reopens_on": reopen.isoformat()})
        night_dates.append(night_day.isoformat())
    if labels != EXPECTED_LABELS[year]:
        raise CalendarEvidenceError("HOLIDAY_LABEL_INVENTORY_MISMATCH")
    # Publication is a source date, not an asserted first-publication instant.
    publication = re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text.split("特此公告。")[-1])
    if not publication:
        raise CalendarEvidenceError("MISSING_NOTICE_PUBLICATION_DATE")
    published_on = date(*map(int, publication[0])).isoformat()
    if date.fromisoformat(published_on).year != year - 1:
        raise CalendarEvidenceError("NOTICE_PUBLICATION_YEAR_MISMATCH")
    facts = {"year": year, "source_ref": source_ref, "source_published_on": published_on,
             "holiday_intervals": holidays, "night_closures": sorted(night_dates)}
    fact_bytes = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(fact_bytes).hexdigest() != AUDITED_NOTICE_FACTS_SHA256[year]:
        raise CalendarEvidenceError("OFFICIAL_CALENDAR_FACTS_PIN_MISMATCH")
    return facts


def _calendar_from_notices(notices: list[dict]) -> dict:
    years = sorted(row["year"] for row in notices)
    if not years or len(years) != len(set(years)) or years != list(range(years[0], years[-1] + 1)):
        raise CalendarEvidenceError("NONCONTIGUOUS_OR_DUPLICATE_CALENDAR_YEARS")
    closed = set()
    for row in notices:
        for interval in row["holiday_intervals"]:
            day, end = date.fromisoformat(interval["start"]), date.fromisoformat(interval["end"])
            while day <= end:
                closed.add(day)
                day += timedelta(days=1)
    first, last = date(years[0], 1, 1), date(years[-1], 12, 31)
    day, sessions = first, []
    while day <= last:
        if day.weekday() < 5 and day not in closed:
            sessions.append(day.isoformat())
        day += timedelta(days=1)
    return {"covered_years": years, "coverage_start": first.isoformat(), "coverage_end": last.isoformat(),
            "sessions": sessions, "holiday_notices": sorted(notices, key=lambda item: item["year"]),
            "weekend_policy": "SATURDAY_SUNDAY_CLOSED_NO_MAKEUP_TRADING",
            "calendar_basis": "OFFICIAL_ANNUAL_PLANNED_CALENDAR_SUBJECT_TO_LATER_AMENDMENTS"}


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _deny_symlink_path(path: Path) -> None:
    # Check the original spelling before resolve(), including parent folders.
    # A resolved path itself can never reveal an earlier symlink traversal.
    original = path.absolute()
    if any(component.is_symlink() for component in (original, *original.parents)):
        raise CalendarEvidenceError("CALENDAR_SYMLINK_PATH_DENIED")


def _read_document(document: dict, raw_dir: Path) -> bytes:
    if not isinstance(document, dict) or not isinstance(document.get("raw_file"), str):
        raise CalendarEvidenceError("INVALID_CALENDAR_SOURCE_DOCUMENT")
    original = Path(document["raw_file"])
    _deny_symlink_path(original)
    _deny_symlink_path(raw_dir)
    path = original.resolve()
    if path.parent != raw_dir.resolve():
        raise CalendarEvidenceError("CALENDAR_SOURCE_OUTSIDE_PRIVATE_RAW")
    try:
        if path.stat().st_size > MAX_RAW_BYTES:
            raise CalendarEvidenceError("INVALID_CALENDAR_RAW_SIZE")
        with path.open("rb") as source:
            raw = source.read(MAX_RAW_BYTES + 1)
    except OSError as exc:
        raise CalendarEvidenceError("MISSING_CALENDAR_SOURCE") from exc
    if not raw or len(raw) > MAX_RAW_BYTES or hashlib.sha256(raw).hexdigest() != document.get("raw_sha256"):
        raise CalendarEvidenceError("CALENDAR_SOURCE_HASH_MISMATCH")
    return raw


def build_calendar_receipt(documents: list[dict], raw_dir: Path) -> dict:
    notices, times = [], []
    for document in documents:
        raw = _read_document(document, raw_dir)
        notice = parse_annual_notice(raw, document["year"], document["source_ref"])
        captured = _instant(document["captured_at"])
        if captured.date() < date.fromisoformat(notice["source_published_on"]):
            raise CalendarEvidenceError("CAPTURE_PRECEDES_PUBLICATION")
        notices.append({**notice, "raw_sha256": document["raw_sha256"], "captured_at": document["captured_at"]})
        times.append(captured)
    calendar = _calendar_from_notices(notices)
    bundle_path = (raw_dir / "source-bundle.json").resolve()
    bundle = {"schema_version": "gold-au-shfe-calendar-source-bundle.v1", "documents": documents}
    raw = _json_bytes(bundle)
    # Exclusive creation preserves raw immutable evidence.
    with bundle_path.open("xb") as target:
        target.write(raw)
    bundle_path.chmod(0o600)
    return {"schema_version": "gold-au-shfe-calendar-receipt.v1", "source_kind": "SHFE_OFFICIAL",
            "status": "CAPTURED_OFFICIAL_ANNUAL_PLAN", "witnessed_at": max(times).isoformat(),
            "raw_file": str(bundle_path), "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "broker_action_authorized": False, **calendar}


def load_calendar_receipt(path: Path, *, as_of: datetime | None = None) -> dict:
    try:
        _deny_symlink_path(path)
        if path.stat().st_size > 100_000:
            raise CalendarEvidenceError("INVALID_CALENDAR_RECEIPT_FILE")
        with path.open("rb") as source:
            receipt_raw = source.read(100_001)
        if len(receipt_raw) > 100_000:
            raise CalendarEvidenceError("INVALID_CALENDAR_RECEIPT_FILE")
        row = json.loads(receipt_raw)
        if not isinstance(row, dict) or row.get("schema_version") != "gold-au-shfe-calendar-receipt.v1" or row.get("source_kind") != "SHFE_OFFICIAL":
            raise CalendarEvidenceError("OFFICIAL_CALENDAR_RECEIPT_REQUIRED")
        raw_dir = path.resolve().parent / "raw"
        bundle_raw = _read_document({"raw_file": row.get("raw_file"), "raw_sha256": row.get("raw_sha256")}, raw_dir)
        bundle = json.loads(bundle_raw)
        if not isinstance(bundle, dict) or bundle.get("schema_version") != "gold-au-shfe-calendar-source-bundle.v1":
            raise CalendarEvidenceError("INVALID_CALENDAR_SOURCE_BUNDLE")
        documents = bundle.get("documents")
        if not isinstance(documents, list) or not 1 <= len(documents) <= len(SOURCES):
            raise CalendarEvidenceError("INVALID_CALENDAR_SOURCE_INVENTORY")
        notices, times = [], []
        for document in documents:
            notice = parse_annual_notice(_read_document(document, raw_dir), document["year"], document["source_ref"])
            captured = _instant(document["captured_at"])
            if captured.date() < date.fromisoformat(notice["source_published_on"]):
                raise CalendarEvidenceError("CAPTURE_PRECEDES_PUBLICATION")
            notices.append({**notice, "raw_sha256": document["raw_sha256"], "captured_at": document["captured_at"]})
            times.append(captured)
        expected = _calendar_from_notices(notices)
        if any(row.get(key) != value for key, value in expected.items()):
            raise CalendarEvidenceError("CALENDAR_RECEIPT_RAW_DISAGREEMENT")
        if _instant(row.get("witnessed_at")) != max(times):
            raise CalendarEvidenceError("CALENDAR_WITNESS_TIME_DISAGREEMENT")
        if as_of is not None and (not isinstance(as_of, datetime) or as_of.tzinfo is None or max(times) > as_of):
            raise CalendarEvidenceError("CALENDAR_CAPTURE_AFTER_DECISION")
        return row
    except (OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise CalendarEvidenceError("MISSING_OR_INVALID_OFFICIAL_CALENDAR", type(exc).__name__) from exc


def session_window(receipt: dict, decision_day: date, *, prior_count: int = 273, horizons: tuple[int, ...] = (5, 20)) -> dict:
    """Window from a receipt already verified by ``load_calendar_receipt``."""
    if decision_day.year not in receipt.get("covered_years", []):
        raise CalendarEvidenceError("UNCOVERED_CALENDAR_YEAR")
    sessions = receipt["sessions"]
    if decision_day.isoformat() not in sessions:
        raise CalendarEvidenceError("DECISION_DAY_NOT_OFFICIAL_SESSION")
    if prior_count < 1 or any(n < 1 for n in horizons):
        raise CalendarEvidenceError("INVALID_SESSION_WINDOW_SCOPE")
    index = sessions.index(decision_day.isoformat())
    if index < prior_count or any(index + n >= len(sessions) for n in horizons):
        raise CalendarEvidenceError("CALENDAR_WINDOW_NOT_FULLY_COVERED")
    return {"decision_date": decision_day.isoformat(), "prior_sessions": sessions[index-prior_count:index],
            "prior_session": sessions[index-1],
            "horizon_sessions": {str(n): sessions[index+n] for n in horizons},
            "authority": "PLANNED_SESSION_EVIDENCE_ONLY", "broker_action_authorized": False}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        raise CalendarEvidenceError("CALENDAR_REDIRECT_BLOCKED")


def fetch_official_notice(url: str) -> bytes:
    if url not in SOURCES.values():
        raise CalendarEvidenceError("UNSUPPORTED_SHFE_CALENDAR_SOURCE")
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), _NoRedirect())
    with opener.open(Request(url, headers={"User-Agent": "GOLD2-read-only-calendar-capture/1.0"}), timeout=25) as response:
        if response.status != 200 or response.url != url:
            raise CalendarEvidenceError("UNEXPECTED_CALENDAR_HTTP_RESPONSE")
        raw = response.read(MAX_RAW_BYTES + 1)
    if not raw or len(raw) > MAX_RAW_BYTES:
        raise CalendarEvidenceError("INVALID_CALENDAR_RAW_SIZE")
    return raw


def capture_calendar(output_dir: Path, *, years: tuple[int, ...] = (2025, 2026), fetch=fetch_official_notice) -> dict:
    if not years or len(set(years)) != len(years) or any(year not in SOURCES for year in years):
        raise CalendarEvidenceError("UNSUPPORTED_OR_DUPLICATE_CALENDAR_YEARS")
    if output_dir.exists():
        raise CalendarEvidenceError("IMMUTABLE_NEW_OUTPUT_DIRECTORY_REQUIRED")
    _deny_symlink_path(output_dir)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(mode=0o700, parents=True)
    output_dir.chmod(0o700)
    documents = []
    for year in sorted(years):
        raw = fetch(SOURCES[year])
        parse_annual_notice(raw, year, SOURCES[year])
        raw_path = (raw_dir / f"shfe-annual-{year}.html").resolve()
        with raw_path.open("xb") as target:
            target.write(raw)
        raw_path.chmod(0o600)
        documents.append({"year": year, "source_ref": SOURCES[year], "raw_file": str(raw_path),
                          "raw_sha256": hashlib.sha256(raw).hexdigest(), "captured_at": datetime.now(timezone.utc).isoformat()})
    receipt = build_calendar_receipt(documents, raw_dir)
    path = output_dir / "receipt.json"
    with path.open("xb") as target:
        target.write(_json_bytes(receipt))
    path.chmod(0o600)
    return load_calendar_receipt(path)
