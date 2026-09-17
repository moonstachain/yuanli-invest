import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from runtime.yci0_rp1.capital_efficiency_reconstruction import FilingFact

from scripts.yci0_rp1_capital_efficiency_archive import (
    audit_tag_regime,
    build_concept_coverage_diagnostics,
    _normalize_tag,
    latest_consecutive_window,
    manifest_entities,
    select_tag_for_target_periods,
    select_optional_tag_for_target_periods,
    merge_optional_alias_series,
    select_mandatory_source_for_target_periods,
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

    def test_cumulative_flow_can_reconstruct_q4_from_q3_ytd_and_fy_without_q1(self):
        tag_obj={"units":{"USD":[
            {"form":"10-Q","fp":"Q3","fy":2024,"start":"2023-01-30","end":"2023-10-29","filed":"2023-11-21","accn":"q3","val":815},
            {"form":"10-K","fp":"FY","fy":2024,"start":"2023-01-30","end":"2024-01-28","filed":"2024-02-21","accn":"fy","val":1069},
        ]}}
        facts, blockers=_normalize_tag(
            "NVDA","0001045810","CAPEX","PaymentsToAcquireProductiveAssets",tag_obj,
            {"q3":"2023-11-21T00:00:00Z","fy":"2024-02-21T00:00:00Z"},
            "rawsha","US_GAAP_COMPANY_LEVEL",
        )
        self.assertEqual(blockers,[])
        self.assertEqual([(f.fiscal_period, f.value) for f in facts],[("2024Q4",254)])

    def test_sparse_single_optional_tag_is_allowed_and_missing_periods_remain_zero_semantics(self):
        tag, regime_break = select_optional_tag_for_target_periods(
            ["LongTermDebtCurrent", "DebtCurrent"],
            {"LongTermDebtCurrent": {"2024Q4", "2026Q3", "2026Q4"}, "DebtCurrent": set()},
            {"2024Q4","2025Q1","2025Q2","2025Q3","2025Q4","2026Q1","2026Q2","2026Q3","2026Q4"},
        )
        self.assertEqual(tag,"LongTermDebtCurrent")
        self.assertFalse(regime_break)

    def test_split_optional_tags_without_bridge_still_fail_closed(self):
        tag, regime_break = select_optional_tag_for_target_periods(
            ["LongTermDebtCurrent", "DebtCurrent"],
            {"LongTermDebtCurrent": {"2025Q4"}, "DebtCurrent": {"2026Q1"}},
            {"2025Q4","2026Q1"},
        )
        self.assertIsNone(tag)
        self.assertTrue(regime_break)

    def test_mandatory_bridge_source_requires_full_target_coverage(self):
        source=select_mandatory_source_for_target_periods(
            ["MarketableSecuritiesCurrent","DebtSecuritiesCurrent"],
            {"MarketableSecuritiesCurrent":{"2026Q1","2026Q2"},"DebtSecuritiesCurrent":{"2026Q4"}},
            {"2026Q1","2026Q2","2026Q3","2026Q4"},
            {"2026Q1","2026Q2","2026Q3","2026Q4"},
        )
        self.assertEqual(source,"__BRIDGE__")

    def test_partial_mandatory_bridge_cannot_bypass_single_tag_gate(self):
        source=select_mandatory_source_for_target_periods(
            ["MarketableSecuritiesCurrent","DebtSecuritiesCurrent"],
            {"MarketableSecuritiesCurrent":{"2026Q1","2026Q2"},"DebtSecuritiesCurrent":{"2026Q4"}},
            {"2026Q1","2026Q2","2026Q3","2026Q4"},
            {"2026Q3","2026Q4"},
        )
        self.assertIsNone(source)

    def test_optional_alias_union_requires_overlap_value_equivalence(self):
        def f(period,value,tag):
            return FilingFact(entity_id="NVDA",fiscal_period=period,known_as_of="2026-01-01T00:00:00Z",source_locator=f"sec://{tag}",content_hash=f"{tag}-{period}",concept="CURRENT_MATURITIES_LONG_TERM_DEBT",value=Decimal(str(value)),unit="USD",accounting_regime="US_GAAP_COMPANY_LEVEL")
        series,proof,regime_break=merge_optional_alias_series(["LongTermDebtCurrent","DebtCurrent"],{"LongTermDebtCurrent":[f("2026Q3",999,"lt"),f("2026Q4",999,"lt")],"DebtCurrent":[f("2026Q4",999,"d"),f("2027Q1",1000,"d")]})
        self.assertFalse(regime_break)
        self.assertEqual([x.fiscal_period for x in series],["2026Q3","2026Q4","2027Q1"])
        self.assertEqual(proof["status"],"PASS")
        self.assertEqual(proof["overlap_periods"],["2026Q4"])

    def test_optional_alias_union_fails_closed_on_overlap_value_mismatch(self):
        def f(period,value,tag):
            return FilingFact(entity_id="NVDA",fiscal_period=period,known_as_of="2026-01-01T00:00:00Z",source_locator=f"sec://{tag}",content_hash=f"{tag}-{period}",concept="CURRENT_MATURITIES_LONG_TERM_DEBT",value=Decimal(str(value)),unit="USD",accounting_regime="US_GAAP_COMPANY_LEVEL")
        series,proof,regime_break=merge_optional_alias_series(["LongTermDebtCurrent","DebtCurrent"],{"LongTermDebtCurrent":[f("2026Q4",999,"lt")],"DebtCurrent":[f("2026Q4",1000,"d")]})
        self.assertTrue(regime_break)
        self.assertEqual(series,[])
        self.assertEqual(proof["reason"],"OPTIONAL_ALIAS_VALUE_MISMATCH")

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
