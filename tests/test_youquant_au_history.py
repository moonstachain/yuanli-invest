import hashlib
import json
import unittest
from datetime import date

from yuanli_invest.youquant_au_history import RequestSpec, contract_specs, normalize_raw


class DatedAUHistoryTests(unittest.TestCase):
    def setUp(self):
        self.spec = RequestSpec("au2412", date(2024, 10, 14), date(2024, 10, 16))
        self.payload = {
            "schema": ["time", "open", "high", "low", "close", "vol", "position"],
            "detail": {"symbol": "au2412", "contractType": "au2412", "eid": "Futures_CTP",
                       "quoteCurrency": "CNY", "quotePrecision": 2, "basePrecision": 0,
                       "priceTick": 0.02, "info": {"InstrumentName": "au2710"}},
            "data": [[1728835200000, 60000, 60200, 59900, 60100, 100, 200]],
        }

    def raw(self):
        return json.dumps(self.payload).encode()

    def test_dated_request_is_bounded(self):
        self.assertIn("symbol=au2412", self.spec.url())
        self.assertIn("eid=Futures_CTP", self.spec.url())
        self.assertIn("from=1728835200", self.spec.url())
        with self.assertRaises(ValueError):
            RequestSpec("au888", date(2024, 1, 1), date(2024, 2, 1))
        with self.assertRaises(ValueError):
            RequestSpec("au2412", date(2023, 1, 1), date(2024, 5, 1))

    def test_metadata_conflict_not_used_for_contract_identity(self):
        raw = self.raw()
        result = normalize_raw(raw, self.spec, captured_at="2026-09-25T08:00:00Z")
        self.assertEqual(result["raw_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertFalse(result["contract_metadata_usable"])
        self.assertEqual(result["bars"][0]["contract"], "au2412")
        self.assertEqual(result["bars"][0]["close"], "601")
        self.assertEqual(result["bars"][0]["pit_grade"], "LATEST_VINTAGE_ONLY")

    def test_mismatched_symbol_or_daily_label_rejected(self):
        self.payload["detail"]["symbol"] = "au888"
        with self.assertRaises(ValueError):
            normalize_raw(self.raw(), self.spec, captured_at="2026-09-25T08:00:00Z")
        self.payload["detail"]["symbol"] = "au2412"
        self.payload["data"][0][0] += 3600_000
        with self.assertRaises(ValueError):
            normalize_raw(self.raw(), self.spec, captured_at="2026-09-25T08:00:00Z")

    def test_contract_enumeration_includes_nearby_months(self):
        symbols = [spec.symbol for spec in contract_specs(date(2024, 10, 1), date(2024, 11, 1))]
        self.assertIn("au2412", symbols)
        self.assertIn("au2501", symbols)


if __name__ == "__main__":
    unittest.main()
