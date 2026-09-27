import json
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.gold_au_shfe_daily_capture import normalize_daily, run


class SHFEDailyCaptureTests(unittest.TestCase):
    def raw(self):
        return json.dumps({"o_curinstrument": [
            {"PRODUCTID": "au_f    ", "DELIVERYMONTH": "2302", "OPENPRICE": 388.64,
             "HIGHESTPRICE": 390.24, "LOWESTPRICE": 387.64, "CLOSEPRICE": 389.78,
             "VOLUME": 14858, "OPENINTEREST": 63108},
            {"PRODUCTID": "au_f    ", "DELIVERYMONTH": "2304", "OPENPRICE": "",
             "HIGHESTPRICE": "", "LOWESTPRICE": "", "CLOSEPRICE": 391.2,
             "VOLUME": 0, "OPENINTEREST": 0},
        ]}).encode()

    def test_normalize_strips_old_product_id_and_skips_inactive(self):
        result = normalize_daily(self.raw(), "2022-08-08")
        self.assertEqual([row["contract"] for row in result["bars"]], ["au2302"])
        self.assertEqual(result["bars"][0]["open"], "388.64")

    def test_dry_run_excludes_weekend_vendor_label(self):
        provider = {"schema_version": "gold-au-history-capture.v1", "captures": [{
            "bars": [{"date": "2022-08-07"}, {"date": "2022-08-08"}]}]}
        with TemporaryDirectory() as directory:
            result = run(provider_manifest=provider, start=date(2022, 8, 7), end=date(2022, 8, 8),
                         output_dir=Path(directory) / "out", execute=False)
            self.assertEqual(result["requested_days"], 1)


if __name__ == "__main__":
    unittest.main()
