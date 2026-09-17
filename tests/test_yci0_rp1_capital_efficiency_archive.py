import subprocess
import sys
import unittest
from pathlib import Path

from scripts.yci0_rp1_capital_efficiency_archive import (
    audit_tag_regime,
    build_concept_coverage_diagnostics,
    latest_consecutive_window,
    manifest_entities,
    select_tag_for_target_periods,
    synthetic_receipt,
)


class CapitalEfficiencyArchiveTests(unittest.TestCase):
    def test_archive_manifest_requires_all_four_frozen_entities(self):
        self.assertEqual(set(manifest_entities()), {"MSFT", "NVDA", "ANET", "ETN"})

    def test_archive_receipt_grants_zero_downstream_authority(self):
        receipt = synthetic_receipt()
        self.assertFalse(any(receipt["authority"].values()))

    def test_script_entrypoint_imports_runtime_from_repo_root(self):
        root=Path(__file__).resolve().parents[1]
        proc=subprocess.run([sys.executable, str(root / "scripts/yci0_rp1_capital_efficiency_archive.py"), "--help"], cwd=root, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_latest_horizon_requires_one_tag_to_cover_all_target_periods(self):
        target={f"2025Q{q}" for q in range(1,5)}
        tag=select_tag_for_target_periods(
            ["OldTag", "NewTag"],
            {"OldTag": {"2025Q1", "2025Q2"}, "NewTag": {"2025Q3", "2025Q4"}},
            target,
        )
        self.assertIsNone(tag)

    def test_latest_consecutive_window_returns_latest_exact_quarters(self):
        periods=["2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1"]
        self.assertEqual(latest_consecutive_window(periods, 4), ["2024Q2", "2024Q3", "2024Q4", "2025Q1"])

    def test_missing_mandatory_operating_income_fails_closed(self):
        result = audit_tag_regime(
            available_tags={"Revenues", "Assets"},
            required_candidates={"OPERATING_INCOME": ["OperatingIncomeLoss"]},
        )
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("MISSING_TAG:OPERATING_INCOME", result["blockers"])

    def test_concept_diagnostics_expose_semantics_and_target_coverage_without_bridging(self):
        gaap={
            "OldTag": {"label":"Purchases of property and equipment", "description":"Cash paid for PP&E", "units":{"USD":[
                {"form":"10-Q","fp":"Q1","fy":2025,"start":"2025-01-01","end":"2025-03-31","filed":"2025-05-01","accn":"a1","val":10},
            ]}},
            "NewTag": {"label":"Purchases of productive assets", "description":"Cash paid for productive assets", "units":{"USD":[
                {"form":"10-K","fp":"FY","fy":2025,"start":"2025-01-01","end":"2025-12-31","filed":"2026-02-01","accn":"a2","val":40},
            ]}},
        }
        normalized={
            "OldTag":[type("F",(),{"fiscal_period":"2025Q1","source_locator":"sec://a1"})()],
            "NewTag":[type("F",(),{"fiscal_period":"2025Q4","source_locator":"sec://a2"})()],
        }
        out=build_concept_coverage_diagnostics(
            "CAPEX", ["OldTag","NewTag"], gaap, normalized, {"2025Q1","2025Q2","2025Q3","2025Q4"}
        )
        self.assertEqual([x["tag"] for x in out],["OldTag","NewTag"])
        self.assertEqual(out[0]["label"],"Purchases of property and equipment")
        self.assertEqual(out[0]["covered_target_periods"],["2025Q1"])
        self.assertEqual(out[1]["raw_accessions"],["a2"])
        self.assertEqual(out[1]["raw_facts"][0]["accn"],"a2")
        self.assertEqual(out[1]["raw_facts"][0]["fp"],"FY")

    def test_split_capex_taxonomy_cannot_be_silently_bridged(self):
        result = audit_tag_regime(
            available_tags={"PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"},
            required_candidates={"CAPEX": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"]},
            coverage={
                "PaymentsToAcquirePropertyPlantAndEquipment": {"Q1", "Q2", "Q3"},
                "PaymentsToAcquireProductiveAssets": {"FY"},
            },
            required_period_types={"Q1", "Q2", "Q3", "FY"},
        )
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("NO_SINGLE_TAG_COVERS:CAPEX", result["blockers"])


if __name__ == "__main__":
    unittest.main()
