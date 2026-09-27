"""Annual notice text fixtures test calendar facts independently of OHLC."""
from datetime import date, datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from yuanli_invest.gold_au_official_calendar import (
    CalendarEvidenceError, SOURCES, capture_calendar, load_calendar_receipt,
    parse_annual_notice, session_window,
)

NOTICE_BODY = {
    2025: """
一、元旦：1月1日（星期三）休市，1月2日（星期四）起照常开市。2024年12月31日（星期二）晚上不进行夜盘交易。
二、春节：1月28日（星期二）至2月4日（星期二）休市，2月5日（星期三）起照常开市。1月26日（星期日）、2月8日（星期六）为周末休市。1月27日（星期一）晚上不进行夜盘交易。
三、清明节：4月4日（星期五）至4月6日（星期日）休市，4月7日（星期一）起照常开市。4月3日（星期四）晚上不进行夜盘交易。
四、劳动节：5月1日（星期四）至5月5日（星期一）休市，5月6日（星期二）起照常开市。4月27日（星期日）为周末休市。4月30日（星期三）晚上不进行夜盘交易。
五、端午节：5月31日（星期六）至6月2日（星期一）休市，6月3日（星期二）起照常开市。5月30日（星期五）晚上不进行夜盘交易。
六、国庆节、中秋节：10月1日（星期三）至10月8日（星期三）休市，10月9日（星期四）起照常开市。9月28日（星期日）、10月11日（星期六）为周末休市。9月30日（星期二）晚上不进行夜盘交易。
""",
    2026: """
一、元旦：1月1日（星期四）至1月3日（星期六）休市，1月5日（星期一）起照常开市。1月4日（星期日）为周末休市。2025年12月31日（星期三）晚上不进行夜盘交易。
二、春节：2月15日（星期日）至2月23日（星期一）休市，2月24日（星期二）起照常开市。2月14日（星期六）、2月28日（星期六）为周末休市。2月13日（星期五）晚上不进行夜盘交易。
三、清明节：4月4日（星期六）至4月6日（星期一）休市，4月7日（星期二）起照常开市。4月3日（星期五）晚上不进行夜盘交易。
四、劳动节：5月1日（星期五）至5月5日（星期二）休市，5月6日（星期三）起照常开市。5月9日（星期六）为周末休市。4月30日（星期四）晚上不进行夜盘交易。
五、端午节：6月19日（星期五）至6月21日（星期日）休市，6月22日（星期一）起照常开市。6月18日（星期四）晚上不进行夜盘交易。
六、中秋节：9月25日（星期五）至9月27日（星期日）休市，9月28日（星期一）起照常开市。9月24日（星期四）晚上不进行夜盘交易。
七、国庆节：10月1日（星期四）至10月7日（星期三）休市，10月8日（星期四）起照常开市。9月20日（星期日）、10月10日（星期六）为周末休市。9月30日（星期三）晚上不进行夜盘交易。
""",
}


def notice_fixture(year):
    published = {2025: "2024年12月23日", 2026: "2025年12月17日"}[year]
    return (f"<html><title>上海期货交易所关于{year}年休市安排的公告</title>"
            f"<p>根据中国证监会有关通知精神，现就上海期货交易所{year}年休市安排公告如下：</p>"
            + "".join(f"<p>{line}</p>" for line in NOTICE_BODY[year].splitlines())
            + f"<p>请各有关单位和广大投资者妥善安排相关事宜。</p><p>特此公告。</p>"
              f"<p>上海期货交易所</p><p>{published}</p></html>").encode()


def calendar_fixture(root: Path):
    """Local fixture has real-shaped annual source evidence, never bypasses validation."""
    folder = root.resolve() / "official-calendar"
    receipt = capture_calendar(folder, fetch=lambda url: notice_fixture(next(year for year, source in SOURCES.items() if source == url)))
    return folder / "receipt.json", receipt


class OfficialCalendarTests(unittest.TestCase):
    def test_reopened_day_and_273_history_and_horizons(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            row = load_calendar_receipt(path)
            window = session_window(row, date(2026, 9, 28))
            self.assertEqual(row["covered_years"], [2025, 2026])
            self.assertEqual(len(row["sessions"]), 485)
            self.assertEqual(len(window["prior_sessions"]), 273)
            self.assertEqual(window["prior_sessions"][0], "2025-08-13")
            self.assertEqual(window["prior_session"], "2026-09-24")
            self.assertEqual(window["horizon_sessions"], {"5": "2026-10-12", "20": "2026-11-02"})
            self.assertIn("2026-09-24", row["holiday_notices"][1]["night_closures"])
            for closed in ("2026-09-25", "2026-09-26", "2026-09-27", "2026-10-01", "2026-10-07", "2026-10-10"):
                self.assertNotIn(closed, row["sessions"])
            self.assertIn("2026-10-08", row["sessions"])

    def test_holiday_uncovered_year_and_short_horizon_fail_closed(self):
        with TemporaryDirectory() as temporary:
            _, row = calendar_fixture(Path(temporary))
            for day, code in [(date(2026, 9, 25), "DECISION_DAY_NOT_OFFICIAL_SESSION"),
                              (date(2027, 1, 4), "UNCOVERED_CALENDAR_YEAR"),
                              (date(2026, 12, 31), "CALENDAR_WINDOW_NOT_FULLY_COVERED"),
                              (date(2025, 1, 2), "CALENDAR_WINDOW_NOT_FULLY_COVERED")]:
                with self.assertRaises(CalendarEvidenceError) as caught:
                    session_window(row, day)
                self.assertEqual(caught.exception.code, code)

    def test_no_holiday_or_session_assertion_without_matching_raw(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            row["sessions"].append("2026-09-25")
            path.write_text(json.dumps(row))
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_RECEIPT_RAW_DISAGREEMENT"):
                load_calendar_receipt(path)

    def test_raw_tamper_and_wrong_source_denied(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            raw_path = path.parent / "raw/shfe-annual-2026.html"
            raw_path.write_bytes(raw_path.read_bytes() + b"modified")
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_SOURCE_HASH_MISMATCH"):
                load_calendar_receipt(path)
        with self.assertRaisesRegex(CalendarEvidenceError, "UNSUPPORTED_SHFE_CALENDAR_SOURCE"):
            parse_annual_notice(notice_fixture(2026), 2026, "https://example.com/notice")

    def test_weekday_mismatch_and_missing_holiday_denied(self):
        raw = notice_fixture(2026).decode().replace("9月25日（星期五）", "9月25日（星期四）").encode()
        with self.assertRaisesRegex(CalendarEvidenceError, "NOTICE_WEEKDAY_MISMATCH"):
            parse_annual_notice(raw, 2026, SOURCES[2026])
        raw = notice_fixture(2026).decode().replace("六、中秋节", "六、未知假期").encode()
        with self.assertRaisesRegex(CalendarEvidenceError, "HOLIDAY_LABEL_INVENTORY_MISMATCH"):
            parse_annual_notice(raw, 2026, SOURCES[2026])

    def test_missing_bundle_and_future_capture_denied(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_CAPTURE_AFTER_DECISION"):
                load_calendar_receipt(path, as_of=datetime(2026, 1, 1, tzinfo=timezone.utc))
            Path(row["raw_file"]).unlink()
            with self.assertRaisesRegex(CalendarEvidenceError, "MISSING_CALENDAR_SOURCE"):
                load_calendar_receipt(path)

    def test_semantic_change_with_valid_weekday_still_denied_by_audited_pin(self):
        # A 7-day date shift preserves weekday syntax but cannot rewrite the
        # audited official holiday calendar simply by rehashing a receipt.
        text = notice_fixture(2026).decode().replace(
            "9月25日（星期五）至9月27日（星期日）休市，9月28日（星期一）起照常开市。9月24日（星期四）",
            "9月18日（星期五）至9月20日（星期日）休市，9月21日（星期一）起照常开市。9月17日（星期四）")
        with self.assertRaisesRegex(CalendarEvidenceError, "OFFICIAL_CALENDAR_FACTS_PIN_MISMATCH"):
            parse_annual_notice(text.encode(), 2026, SOURCES[2026])

    def test_capture_refuses_overwrite_and_unsupported_year_without_network(self):
        with TemporaryDirectory() as temporary:
            folder = Path(temporary) / "already"
            folder.mkdir()
            with self.assertRaisesRegex(CalendarEvidenceError, "IMMUTABLE_NEW_OUTPUT_DIRECTORY_REQUIRED"):
                capture_calendar(folder, fetch=lambda _: self.fail("network"))
            with self.assertRaisesRegex(CalendarEvidenceError, "UNSUPPORTED_OR_DUPLICATE_CALENDAR_YEARS"):
                capture_calendar(Path(temporary) / "unknown", years=(2027,), fetch=lambda _: self.fail("network"))

    def test_original_file_symlink_is_rejected_before_resolution(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            original = path.parent / "raw/shfe-annual-2026.html"
            moved = original.with_suffix(".target")
            original.rename(moved)
            original.symlink_to(moved)
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_SYMLINK_PATH_DENIED"):
                load_calendar_receipt(path)

    def test_parent_directory_symlink_is_rejected_before_resolution(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            alias = path.parent.parent / "alias"
            alias.symlink_to(path.parent, target_is_directory=True)
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_SYMLINK_PATH_DENIED"):
                load_calendar_receipt(alias / "receipt.json")
            # A raw-file alias directory also fails even if a rewritten bundle
            # hash matches the top-level receipt.
            bundle_path = Path(row["raw_file"])
            bundle = json.loads(bundle_path.read_bytes())
            bundle["documents"][1]["raw_file"] = str(alias / "raw/shfe-annual-2026.html")
            encoded = json.dumps(bundle).encode()
            bundle_path.write_bytes(encoded)
            import hashlib
            row["raw_sha256"] = hashlib.sha256(encoded).hexdigest()
            path.write_text(json.dumps(row))
            with self.assertRaisesRegex(CalendarEvidenceError, "CALENDAR_SYMLINK_PATH_DENIED"):
                load_calendar_receipt(path)

    def test_oversized_receipt_and_raw_are_rejected(self):
        with TemporaryDirectory() as temporary:
            path, row = calendar_fixture(Path(temporary))
            Path(row["raw_file"]).write_bytes(b"x" * 1_000_001)
            with self.assertRaisesRegex(CalendarEvidenceError, "INVALID_CALENDAR_RAW_SIZE"):
                load_calendar_receipt(path)
            path.write_bytes(b"x" * 100_001)
            with self.assertRaisesRegex(CalendarEvidenceError, "INVALID_CALENDAR_RECEIPT_FILE"):
                load_calendar_receipt(path)


if __name__ == "__main__":
    unittest.main()
