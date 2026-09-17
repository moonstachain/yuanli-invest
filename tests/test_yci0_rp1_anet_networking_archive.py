import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "yci0_rp1_anet_networking_archive.py"

spec = importlib.util.spec_from_file_location("anet_archive", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class AristaNetworkingArchiveTests(unittest.TestCase):
    def test_frozen_series_is_four_consecutive_company_filed_quarters(self):
        self.assertEqual(
            [(row["quarter"], row["value_usd_bn"]) for row in module.SOURCES],
            [
                ("2025Q3", 2.308),
                ("2025Q4", 2.488),
                ("2026Q1", 2.709),
                ("2026Q2", 3.036),
            ],
        )
        for row in module.SOURCES:
            self.assertIn("sec.gov/Archives/edgar/data/1596532/", row["url"])
            self.assertTrue(row["accession"].startswith("0001596532-"))

    def test_validate_requires_arista_networking_identity_and_exact_revenue(self):
        raw = b"""
        <html><body>
        Exhibit 99.1 Arista Networks, Inc. Reports Third Quarter 2025 Financial Results.
        Arista Networks is an industry leader in networking for large AI, data center,
        campus, and routing environments. Revenue of $2.308 billion.
        </body></html>
        """
        checked = module.validate(raw, module.SOURCES[0])
        self.assertEqual(checked["bytes"], len(raw))
        self.assertEqual(len(checked["sha256"]), 64)

        bad = raw.replace(b"$2.308 billion", b"$9.999 billion")
        with self.assertRaisesRegex(RuntimeError, "expected revenue marker missing"):
            module.validate(bad, module.SOURCES[0])


if __name__ == "__main__":
    unittest.main()
