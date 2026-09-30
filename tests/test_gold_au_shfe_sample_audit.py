import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.gold_au_shfe_sample_audit import audit, compare_bar


class SHFESampleAuditTests(unittest.TestCase):
    def setUp(self):
        self.bar = {
            "date": "2024-10-14", "contract": "au2412", "open": "597.38",
            "high": "604.4", "low": "597.18", "close": "603.3",
            "volume": 170494, "open_interest": 196568,
            "source_sha256": "0" * 64,
        }
        self.official = json.dumps({"o_curinstrument": [{
            "PRODUCTID": "au_f    ", "DELIVERYMONTH": "2412", "OPENPRICE": 597.38,
            "HIGHESTPRICE": 604.4, "LOWESTPRICE": 597.18, "CLOSEPRICE": 603.3,
            "VOLUME": 170494, "OPENINTEREST": 196568,
        }]}).encode()

    def test_six_fields_and_exact_contract(self):
        self.assertTrue(compare_bar(self.bar, self.official)["exact_all_six"])
        self.bar["volume"] += 1
        self.assertEqual(set(compare_bar(self.bar, self.official)["differences"]), {"volume"})
        self.bar["contract"] = "au2501"
        with self.assertRaises(ValueError):
            compare_bar(self.bar, self.official)

    def test_audit_rejects_provider_hash_mismatch(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "raw.json"
            path.write_bytes(b"source")
            capture = {"bars": [dict(self.bar)], "raw_file": str(path), "raw_sha256": "1" * 64}
            manifest = {"schema_version": "gold-au-history-capture.v1", "status": "CAPTURED",
                        "captures": [capture]}
            with self.assertRaises(ValueError):
                audit(manifest, fetch=lambda day: self.official)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            capture["raw_sha256"] = digest
            capture["bars"][0]["source_sha256"] = digest
            report, sources = audit(manifest, fetch=lambda day: self.official)
            self.assertEqual(report["compared_count"], 1)
            self.assertEqual(len(sources), 1)


if __name__ == "__main__":
    unittest.main()
