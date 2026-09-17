import unittest
from decimal import Decimal

from runtime.yci0_rp1.capital_efficiency_reconstruction import (
    FilingFact, reconstruct_entity_observations,
)


def entity_spec():
    return {
        "entity_id": "TEST",
        "tax_rate_min": "0",
        "tax_rate_max": "0.50",
        "minimum_invested_capital_delta": "100",
        "near_zero_nopat": "1",
        "required_raw_quarters_incremental_roic": 11,
        "required_raw_quarters_ttm": 7,
        "accounting_regime": "GAAP_V1",
    }


def quarter_facts(n=11, tax_rate=Decimal("0.20"), invested_step=Decimal("200"), regime="GAAP_V1"):
    rows=[]
    for i in range(n):
        year=2023 + i // 4
        q=i % 4 + 1
        period=f"{year}Q{q}"
        known=f"{year}-{q*3:02d}-28T00:00:00Z"
        revenue=Decimal("1000") + Decimal(i)*Decimal("50")
        op=Decimal("200") + Decimal(i)*Decimal("10")
        pretax=Decimal("180") + Decimal(i)*Decimal("9")
        tax=pretax*tax_rate
        cfo=Decimal("210") + Decimal(i)*Decimal("11")
        capex=Decimal("100") + Decimal(i)*Decimal("4")
        assets=Decimal("5000") + Decimal(i)*invested_step
        vals={
            "REVENUE": revenue, "OPERATING_INCOME": op, "PRETAX_INCOME": pretax,
            "INCOME_TAX_EXPENSE": tax, "OPERATING_CASH_FLOW": cfo, "CAPEX": capex,
            "TOTAL_ASSETS": assets, "CASH": Decimal("500"),
            "CURRENT_MARKETABLE_SECURITIES": Decimal("100"),
            "TOTAL_CURRENT_LIABILITIES": Decimal("900"), "SHORT_TERM_BORROWINGS": Decimal("100"),
            "CURRENT_MATURITIES_LONG_TERM_DEBT": Decimal("50"),
            "CURRENT_FINANCE_LEASE_LIABILITIES": Decimal("20"),
        }
        for concept,value in vals.items():
            rows.append(FilingFact(
                entity_id="TEST", fiscal_period=period, known_as_of=known,
                source_locator=f"sec://{period}/{concept}", content_hash=f"h-{period}-{concept}",
                concept=concept, value=value, unit="USD", accounting_regime=regime,
            ))
    return rows


class CapitalEfficiencyReconstructionTests(unittest.TestCase):
    def test_eleven_quarters_produce_four_consecutive_incremental_roic_observations(self):
        out=reconstruct_entity_observations(quarter_facts(11), entity_spec())
        roic=[x for x in out if x.component == "INCREMENTAL_ROIC" and x.status == "PASS"]
        self.assertEqual(len(roic), 4)
        self.assertEqual(roic[0].fiscal_period, "2024Q4")
        self.assertEqual(roic[-1].fiscal_period, "2025Q3")

    def test_ten_quarters_are_insufficient_for_four_incremental_roic_points(self):
        out=reconstruct_entity_observations(quarter_facts(10), entity_spec())
        roic=[x for x in out if x.component == "INCREMENTAL_ROIC" and x.status == "PASS"]
        self.assertEqual(len(roic), 3)

    def test_seven_quarters_produce_four_ttm_cash_conversion_and_capital_intensity_points(self):
        out=reconstruct_entity_observations(quarter_facts(7), entity_spec())
        cash=[x for x in out if x.component == "CASH_CONVERSION" and x.status == "PASS"]
        burden=[x for x in out if x.component == "CAPITAL_INTENSITY" and x.status == "PASS"]
        self.assertEqual(len(cash), 4)
        self.assertEqual(len(burden), 4)
        self.assertEqual(burden[-1].value, Decimal("472") / Decimal("4900"))
        self.assertEqual(cash[-1].value, Decimal("1038") / Decimal("784"))

    def test_operating_invested_capital_formula_is_frozen(self):
        out=reconstruct_entity_observations(quarter_facts(11), entity_spec())
        roic=[x for x in out if x.component == "INCREMENTAL_ROIC" and x.status == "PASS"][-1]
        inputs=roic.formula_inputs
        self.assertEqual(inputs["operating_invested_capital_t"], Decimal("5670"))
        self.assertEqual(inputs["operating_invested_capital_t_minus_4"], Decimal("4870"))

    def test_optional_current_interest_bearing_components_default_to_zero_when_not_separately_disclosed(self):
        facts=[f for f in quarter_facts(11) if f.concept not in {"SHORT_TERM_BORROWINGS", "CURRENT_MATURITIES_LONG_TERM_DEBT", "CURRENT_FINANCE_LEASE_LIABILITIES"}]
        out=reconstruct_entity_observations(facts, entity_spec())
        roic=[x for x in out if x.component == "INCREMENTAL_ROIC" and x.fiscal_period == "2025Q3"][0]
        self.assertEqual(roic.status, "PASS")
        self.assertEqual(roic.formula_inputs["short_term_borrowings_t"], Decimal("0"))
        self.assertEqual(roic.formula_inputs["current_maturities_long_term_debt_t"], Decimal("0"))
        self.assertEqual(roic.formula_inputs["current_finance_lease_liabilities_t"], Decimal("0"))

    def test_tax_rate_outside_zero_to_fifty_percent_fails_nopat_components_closed(self):
        out=reconstruct_entity_observations(quarter_facts(11, Decimal("0.60")), entity_spec())
        latest=[x for x in out if x.fiscal_period == "2025Q3"]
        by={x.component:x for x in latest}
        self.assertEqual(by["INCREMENTAL_ROIC"].status, "UNKNOWN")
        self.assertEqual(by["CASH_CONVERSION"].status, "UNKNOWN")
        self.assertIn("TAX_RATE_OUT_OF_RANGE", by["INCREMENTAL_ROIC"].reason)

    def test_near_zero_or_nonmeaningful_invested_capital_delta_fails_incremental_roic_closed(self):
        out=reconstruct_entity_observations(quarter_facts(11, invested_step=Decimal("10")), entity_spec())
        roic=[x for x in out if x.component == "INCREMENTAL_ROIC"][-1]
        self.assertEqual(roic.status, "UNKNOWN")
        self.assertEqual(roic.reason, "INVESTED_CAPITAL_DELTA_NOT_MEANINGFUL")

    def test_near_zero_nopat_fails_cash_conversion_closed(self):
        facts=quarter_facts(11)
        patched=[]
        for f in facts:
            if f.concept == "OPERATING_INCOME" and f.fiscal_period >= "2024Q4":
                patched.append(f.__class__(**{**f.__dict__, "value": Decimal("0.1")}))
            else:
                patched.append(f)
        out=reconstruct_entity_observations(patched, entity_spec())
        cash=[x for x in out if x.component == "CASH_CONVERSION" and x.fiscal_period == "2025Q3"][0]
        self.assertEqual(cash.status, "UNKNOWN")
        self.assertEqual(cash.reason, "NOPAT_NEAR_ZERO")

    def test_accounting_regime_break_prevents_cross_regime_ttm(self):
        facts=quarter_facts(11)
        facts=[f.__class__(**{**f.__dict__, "accounting_regime": ("GAAP_V2" if f.fiscal_period >= "2025Q1" else f.accounting_regime)}) for f in facts]
        out=reconstruct_entity_observations(facts, entity_spec())
        latest=[x for x in out if x.fiscal_period == "2025Q3"]
        self.assertTrue(latest)
        self.assertTrue(all(x.status == "UNKNOWN" for x in latest))
        self.assertTrue(all("ACCOUNTING_REGIME_BREAK" in x.reason for x in latest))

    def test_receipt_hash_is_deterministic_and_covers_every_required_source_fact(self):
        facts=quarter_facts(11)
        one=reconstruct_entity_observations(facts, entity_spec())
        two=reconstruct_entity_observations(list(reversed(facts)), entity_spec())
        a=[x for x in one if x.component == "INCREMENTAL_ROIC" and x.fiscal_period == "2025Q3"][0]
        b=[x for x in two if x.component == "INCREMENTAL_ROIC" and x.fiscal_period == "2025Q3"][0]
        self.assertEqual(a.calculation_receipt_sha256, b.calculation_receipt_sha256)
        self.assertEqual(a.source_fact_count, len(a.source_hashes))
        self.assertGreaterEqual(a.source_fact_count, 20)
        self.assertEqual(a.known_as_of, max(a.source_known_as_of))


if __name__ == "__main__":
    unittest.main()
