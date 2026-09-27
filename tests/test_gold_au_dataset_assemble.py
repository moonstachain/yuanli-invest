import hashlib
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from yuanli_invest.gold_au_dataset_assemble import assemble_dataset  # noqa: E402
from yuanli_invest.gold_au_strategy import GoldAuDataset  # noqa: E402
from yuanli_invest.gold_macro_capture import MacroSpec, normalize_raw as normalize_macro  # noqa: E402
from yuanli_invest.youquant_au_history import RequestSpec, normalize_raw as normalize_au  # noqa: E402
from gold_au_dataset_assemble import run as run_cli  # noqa: E402
from gold_au_shfe_daily_capture import normalize_daily  # noqa: E402


CAPTURED_AT = "2026-09-25T08:00:00+00:00"
SHFE_AT = "2026-09-25T08:01:00+00:00"
NOW = datetime.fromisoformat("2026-09-25T09:00:00+00:00")


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False), encoding="utf-8")


class AssemblyFixture:
    def __init__(self, root):
        self.root = root
        self.au_dir = root / "au"
        self.macro_dir = root / "macro"
        self.shfe_dir = root / "shfe"
        for folder in (self.au_dir, self.macro_dir, self.shfe_dir):
            (folder / "raw").mkdir(parents=True)
        self.mapping = ROOT / "config" / "ymq_gold2" / "fred_h10_mapping.v1.json"
        self._write_au()
        self._write_macro()
        self._write_shfe()

    def _write_au(self):
        spec = RequestSpec("au2412", date(2024, 10, 13), date(2024, 10, 16))
        def stamp(day):
            return int(datetime.fromisoformat(day + "T00:00:00+08:00").timestamp() * 1000)
        raw = json.dumps({
            "schema": ["time", "open", "high", "low", "close", "vol", "position"],
            "detail": {"symbol": "au2412", "contractType": "au2412", "eid": "Futures_CTP",
                       "quoteCurrency": "CNY", "quotePrecision": 2, "basePrecision": 0,
                       "priceTick": 0.02, "info": {"InstrumentName": "au2710"}},
            "data": [
                [stamp("2024-10-13"), 60000, 60200, 59900, 60100, 100, 200],
                [stamp("2024-10-14"), 60100, 60300, 60000, 60200, 101, 201],
                [stamp("2024-10-15"), 60200, 60400, 60100, 60300, 102, 202],
            ],
        }).encode()
        capture = normalize_au(raw, spec, captured_at=CAPTURED_AT)
        raw_file = self.au_dir / "raw" / (capture["raw_sha256"] + ".json")
        raw_file.write_bytes(raw)
        capture["raw_file"] = str(raw_file)
        self.au_path = self.au_dir / "manifest.json"
        write_json(self.au_path, {
            "schema_version": "gold-au-history-capture.v1", "status": "CAPTURED",
            "provider_id": "youquant_history", "captured_at": CAPTURED_AT,
            "historical_release_time_verified": False,
            "requested_contracts": ["au2412"], "captures": [capture],
        })
        self.audit_path = self.root / "audit.json"
        write_json(self.audit_path, {
            "schema_version": "gold-au-shfe-contract-sample-audit.v1",
            "provider_manifest_sha256": hashlib.sha256(self.au_path.read_bytes()).hexdigest(),
            "field_mismatch_counts": {"open": 1},
            "sampling_scope": "one bar per contract; no full-history certification",
        })

    def _write_macro(self):
        captures = []
        for series, value in (("DFII10", "1.50"), ("DTWEXBGS", "122.500")):
            spec = MacroSpec(series, date(2024, 10, 14), date(2024, 10, 14))
            raw = (f"observation_date,{series}\n2024-10-14,{value}\n").encode()
            capture = normalize_macro(raw, spec, captured_at=datetime.fromisoformat(CAPTURED_AT))
            raw_file = self.macro_dir / "raw" / (series.lower() + "-" + capture["raw_sha256"] + ".csv")
            raw_file.write_bytes(raw)
            capture["raw_file"] = str(raw_file)
            capture["status"] = "CAPTURED"
            captures.append(capture)
        self.macro_path = self.macro_dir / "manifest.json"
        write_json(self.macro_path, {
            "schema_version": "gold-macro-capture.v1", "status": "CAPTURED",
            "provider_id": "fred_graph_csv", "captured_at": CAPTURED_AT,
            "historical_release_time_verified": False,
            "captures": captures,
        })

    def _write_shfe(self):
        raw = json.dumps({"o_curinstrument": [{
            "PRODUCTID": "au_f", "DELIVERYMONTH": "2412",
            "OPENPRICE": "610.00", "HIGHESTPRICE": "613.00", "LOWESTPRICE": "609.00",
            "CLOSEPRICE": "612.00", "VOLUME": "1000", "OPENINTEREST": "3000",
        }]}).encode()
        report = normalize_daily(raw, "2024-10-14")
        report["captured_at"] = SHFE_AT
        raw_file = self.shfe_dir / "raw" / "kx20241014.dat"
        raw_file.write_bytes(raw)
        report["raw_file"] = str(raw_file)
        self.shfe_path = self.shfe_dir / "manifest.json"
        write_json(self.shfe_path, {
            "schema_version": "gold-au-shfe-daily-capture.v1", "mode": "EXECUTE",
            "status": "PARTIAL_FAILURE", "historical_release_time_verified": False,
            "captured_at": SHFE_AT, "interval": ["2024-10-14", "2024-10-15"],
            "requested_days": 2, "reports": [report],
            "errors": [{"date": "2024-10-15", "error_type": "HTTPError"}],
        })

    def assemble(self, *, shfe=True, macro=True):
        return assemble_dataset(
            au_manifest_path=self.au_path,
            macro_manifest_path=self.macro_path if macro else None,
            shfe_manifest_path=self.shfe_path if shfe else None,
            h10_mapping_path=self.mapping,
            audit_report_path=self.audit_path,
            assembled_at=NOW,
        )


class DatasetAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = AssemblyFixture(Path(self.temp.name))

    def test_official_day_overrides_vendor_and_404_day_is_quarantined(self):
        dataset, report = self.fixture.assemble()
        self.assertEqual(report["weekend_quarantine_count"], 1)
        self.assertEqual(report["shfe_error_dates_quarantined"], ["2024-10-15"])
        self.assertEqual(report["shfe_error_vendor_bars_quarantined"], 1)
        self.assertEqual(report["official_repair_days"], 1)
        self.assertEqual(report["assembled_bars"], 1)
        self.assertEqual(report["official_vendor_comparison"]["common_contract_day_bars"], 1)
        self.assertEqual(report["official_vendor_comparison"]["field_mismatch_counts"], {
            "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1, "open_interest": 1,
        })
        bar = dataset["bars"][0]
        self.assertEqual(bar["date"], "2024-10-14")
        self.assertEqual(bar["open"], 610.0)
        self.assertEqual(bar["volume"], 1000.0)
        self.assertEqual(bar["source_provider_id"], "shfe_official_daily")
        self.assertEqual(bar["first_published_at"], SHFE_AT)
        self.assertEqual(bar["pit_grade"], "UNKNOWN")
        self.assertEqual(bar["vintage_kind"], "UNKNOWN")
        self.assertEqual(bar["execution_cost_grade"], "ASSUMPTION")
        self.assertEqual(bar["margin_per_lot_cny"], 612 * 1000 * 0.2)
        self.assertEqual(bar["fee_open_per_lot_cny"], 40.0)
        self.assertEqual(dataset["price_quality"]["status"], "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED")
        self.assertEqual(dataset["price_quality"]["retained_bar_source_coverage"], "ALL_OFFICIAL_SHFE_DAILY")
        self.assertEqual(dataset["price_quality"]["official_retained_bars"], 1)
        self.assertEqual(dataset["price_quality"]["vendor_retained_bars"], 0)
        self.assertEqual(dataset["price_quality"]["shfe_http_error_dates_excluded"], 1)
        self.assertIn("Historical first publication/availability", dataset["price_quality"]["reason"])
        self.assertEqual(report["official_retained_bars"], report["assembled_bars"])
        self.assertEqual(report["status"], "DATA_QUALITY_BLOCKED")
        GoldAuDataset(dataset)

    def test_h10_alias_is_explicit_and_source_identity_retained(self):
        dataset, report = self.fixture.assemble()
        self.assertEqual(len(dataset["observations"]), 2)
        h10 = next(row for row in dataset["observations"] if row["series"] == "FED:H10:DTWEXBGS")
        self.assertEqual(h10["source_series"], "FRED:DTWEXBGS")
        self.assertEqual(h10["source_measurement_regime"], "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY")
        self.assertEqual(h10["measurement_regime"], "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY")
        self.assertEqual(h10["released_at"], CAPTURED_AT)
        self.assertEqual(h10["available_at"], CAPTURED_AT)
        self.assertEqual(h10["pit_grade"], "UNKNOWN")
        self.assertEqual(report["wgc_historical_observations"], 0)
        self.assertFalse(report["historical_release_time_verified"])

    def test_raw_or_normalized_tamper_fails_closed(self):
        au = json.loads(self.fixture.au_path.read_text())
        raw_path = Path(au["captures"][0]["raw_file"])
        original = raw_path.read_bytes()
        raw_path.write_bytes(original + b" ")
        with self.assertRaisesRegex(ValueError, "raw SHA256 mismatch"):
            self.fixture.assemble()
        raw_path.write_bytes(original)
        au["captures"][0]["bars"][1]["close"] = "999.99"
        write_json(self.fixture.au_path, au)
        # Keep the audit bound to this newly written manifest, isolating the
        # stronger normalized-vs-raw check from the audit hash check.
        audit = json.loads(self.fixture.audit_path.read_text())
        audit["provider_manifest_sha256"] = hashlib.sha256(self.fixture.au_path.read_bytes()).hexdigest()
        write_json(self.fixture.audit_path, audit)
        with self.assertRaisesRegex(ValueError, "normalized capture differs"):
            self.fixture.assemble()

    def test_missing_macro_remains_incomplete_and_dry_run_writes_nothing(self):
        dataset, report = self.fixture.assemble(macro=False, shfe=False)
        self.assertEqual(dataset["observations"], [])
        self.assertEqual(dataset["price_quality"]["status"], "UNVERIFIED_VENDOR_OHLC")
        self.assertGreater(report["vendor_retained_bars"], 0)
        self.assertEqual(report["status"], "INCOMPLETE_MACRO_AND_DATA_QUALITY_BLOCKED")
        destination = Path(self.temp.name) / "assembled"
        result = run_cli(
            au_manifest=self.fixture.au_path, macro_manifest=self.fixture.macro_path,
            shfe_manifest=self.fixture.shfe_path, mapping=self.fixture.mapping,
            audit_report=self.fixture.audit_path, output_dir=destination,
            execute=False, now=NOW,
        )
        self.assertEqual(result["status"], "DATA_QUALITY_BLOCKED")
        self.assertFalse(destination.exists())

    def test_future_capture_and_mapping_drift_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "after assembly time"):
            assemble_dataset(
                au_manifest_path=self.fixture.au_path,
                macro_manifest_path=self.fixture.macro_path,
                shfe_manifest_path=None,
                h10_mapping_path=self.fixture.mapping,
                audit_report_path=self.fixture.audit_path,
                assembled_at=datetime.fromisoformat("2024-10-14T09:00:00+00:00"),
            )
        changed = json.loads(self.fixture.mapping.read_text())
        changed["strategy_series"] = "MADE_UP:H10"
        changed_path = Path(self.temp.name) / "bad-mapping.json"
        write_json(changed_path, changed)
        with self.assertRaisesRegex(ValueError, "mapping not explicitly frozen"):
            assemble_dataset(
                au_manifest_path=self.fixture.au_path,
                macro_manifest_path=self.fixture.macro_path,
                shfe_manifest_path=None,
                h10_mapping_path=changed_path,
                audit_report_path=self.fixture.audit_path,
                assembled_at=NOW,
            )

    def test_capture_inventory_requires_exact_contract_identity(self):
        manifest = json.loads(self.fixture.au_path.read_text())
        manifest["requested_contracts"] = ["au2502"]
        write_json(self.fixture.au_path, manifest)
        audit = json.loads(self.fixture.audit_path.read_text())
        audit["provider_manifest_sha256"] = hashlib.sha256(self.fixture.au_path.read_bytes()).hexdigest()
        write_json(self.fixture.audit_path, audit)
        with self.assertRaisesRegex(ValueError, "contract identities differ"):
            self.fixture.assemble()

    def test_official_inventory_cannot_silently_drop_requested_day(self):
        manifest = json.loads(self.fixture.shfe_path.read_text())
        manifest["errors"] = []
        manifest["status"] = "CAPTURED"
        write_json(self.fixture.shfe_path, manifest)
        with self.assertRaisesRegex(ValueError, "report/error dates do not cover"):
            self.fixture.assemble()
        manifest["requested_days"] = 1
        write_json(self.fixture.shfe_path, manifest)
        with self.assertRaisesRegex(ValueError, "requested day count differs"):
            self.fixture.assemble()


if __name__ == "__main__":
    unittest.main()
