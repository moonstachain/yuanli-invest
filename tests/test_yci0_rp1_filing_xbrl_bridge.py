import unittest
import json
from pathlib import Path
from decimal import Decimal

from runtime.yci0_rp1.capital_efficiency_reconstruction import FilingFact
from runtime.yci0_rp1.filing_xbrl_bridge import (
    build_disaggregation_bridge_fact,
    build_filing_instant_bridge_fact,
    build_same_standard_q4_bridge_fact,
    parse_xbrl_instance,
    apply_filing_bridge_rules,
)


def xbrl(*body: str) -> bytes:
    return ("""<?xml version='1.0' encoding='utf-8'?>
<xbrl xmlns='http://www.xbrl.org/2003/instance'
      xmlns:us-gaap='http://fasb.org/us-gaap/2025'
      xmlns:nvda='http://www.nvidia.com/20260125'
      xmlns:xbrldi='http://xbrl.org/2006/xbrldi'>
%s
</xbrl>""" % "\n".join(body)).encode()


def instant_context(cid: str, instant: str, dimension: str | None = None) -> str:
    scenario = "" if dimension is None else (
        "<scenario><xbrldi:explicitMember dimension='us-gaap:StatementOfFinancialPositionLocationBalanceAxis'>"
        f"{dimension}</xbrldi:explicitMember></scenario>"
    )
    return f"<context id='{cid}'><entity><identifier scheme='x'>1</identifier></entity><period><instant>{instant}</instant></period>{scenario}</context>"


def duration_context(cid: str, start: str, end: str) -> str:
    return f"<context id='{cid}'><entity><identifier scheme='x'>1</identifier></entity><period><startDate>{start}</startDate><endDate>{end}</endDate></period></context>"


class FilingXbrlBridgeTests(unittest.TestCase):
    def test_parse_xbrl_preserves_zero_dimension_context_semantics(self):
        raw=xbrl(
            instant_context('c0','2026-01-25'),
            instant_context('c1','2026-01-25','nvda:MarketableSecuritiesMember'),
            "<nvda:MarketableSecuritiesAndEquitySecuritiesFVNI contextRef='c0' unitRef='usd'>51951</nvda:MarketableSecuritiesAndEquitySecuritiesFVNI>",
            "<nvda:MarketableSecuritiesAndEquitySecuritiesFVNI contextRef='c1' unitRef='usd'>51951</nvda:MarketableSecuritiesAndEquitySecuritiesFVNI>",
        )
        facts=parse_xbrl_instance(raw)
        zero=[f for f in facts if f.concept=='MarketableSecuritiesAndEquitySecuritiesFVNI' and not f.dimensions]
        self.assertEqual(len(zero),1)
        self.assertEqual(zero[0].instant,'2026-01-25')
        self.assertEqual(zero[0].value,Decimal('51951'))

    def test_same_standard_q4_bridge_uses_filed_fy_minus_same_tag_q3_ytd(self):
        annual=xbrl(
            duration_context('fy','2023-01-30','2024-01-28'),
            "<us-gaap:PaymentsToAcquireProductiveAssets contextRef='fy' unitRef='usd'>1069</us-gaap:PaymentsToAcquireProductiveAssets>",
        )
        q3=FilingFact(
            entity_id='NVDA', fiscal_period='2024Q3', known_as_of='2023-11-21T00:00:00Z',
            source_locator='sec-companyfacts://CIK0001045810/us-gaap/PaymentsToAcquireProductiveAssets?accessions=q3',
            content_hash='q3hash', concept='CAPEX', value=Decimal('815'), unit='USD', accounting_regime='US_GAAP_COMPANY_LEVEL',
        )
        fact,proof=build_same_standard_q4_bridge_fact(
            entity_id='NVDA', fiscal_period='2024Q4', normalized_concept='CAPEX',
            standard_tag='PaymentsToAcquireProductiveAssets', annual_raw=annual, annual_raw_sha256='annualsha',
            annual_accession='0001045810-24-000029', annual_known_as_of='2024-02-21T21:23:17Z',
            annual_start='2023-01-30', annual_end='2024-01-28', q3_ytd_fact=q3,
            accounting_regime='US_GAAP_COMPANY_LEVEL',
        )
        self.assertEqual(proof['status'],'PASS')
        self.assertEqual(fact.value,Decimal('254'))
        self.assertEqual(fact.fiscal_period,'2024Q4')
        self.assertEqual(fact.known_as_of,'2024-02-21T21:23:17Z')

    def test_disaggregation_bridge_reconciles_same_instant_before_emitting_current_sum(self):
        anchor=xbrl(
            instant_context('a','2026-01-25'),
            "<nvda:MarketableSecuritiesAndEquitySecuritiesFVNI contextRef='a' unitRef='usd'>51951</nvda:MarketableSecuritiesAndEquitySecuritiesFVNI>",
        )
        current=xbrl(
            instant_context('now','2026-04-26'), instant_context('prior','2026-01-25'),
            "<us-gaap:DebtSecuritiesCurrent contextRef='now' unitRef='usd'>37098</us-gaap:DebtSecuritiesCurrent>",
            "<us-gaap:EquitySecuritiesFvNi contextRef='now' unitRef='usd'>30237</us-gaap:EquitySecuritiesFvNi>",
            "<us-gaap:DebtSecuritiesCurrent contextRef='prior' unitRef='usd'>39065</us-gaap:DebtSecuritiesCurrent>",
            "<us-gaap:EquitySecuritiesFvNi contextRef='prior' unitRef='usd'>12886</us-gaap:EquitySecuritiesFvNi>",
        )
        anchor_fact,anchor_proof=build_filing_instant_bridge_fact(
            entity_id='NVDA', fiscal_period='2026Q4', normalized_concept='CURRENT_MARKETABLE_SECURITIES',
            concept='MarketableSecuritiesAndEquitySecuritiesFVNI', raw=anchor, raw_sha256='anchor-sha',
            accession='0001045810-26-000021', known_as_of='2026-02-25T00:00:00Z', instant='2026-01-25',
            accounting_regime='US_GAAP_COMPANY_LEVEL',
        )
        self.assertEqual(anchor_proof['status'],'PASS')
        fact,proof=build_disaggregation_bridge_fact(
            entity_id='NVDA', fiscal_period='2027Q1', normalized_concept='CURRENT_MARKETABLE_SECURITIES',
            component_concepts=('DebtSecuritiesCurrent','EquitySecuritiesFvNi'), raw=current, raw_sha256='q1-sha',
            accession='0001045810-26-000052', known_as_of='2026-05-20T00:00:00Z', instant='2026-04-26',
            reconcile_instant='2026-01-25', anchor_fact=anchor_fact, accounting_regime='US_GAAP_COMPANY_LEVEL',
        )
        self.assertEqual(proof['status'],'PASS')
        self.assertEqual(proof['reconciled_prior_sum'], '51951')
        self.assertEqual(fact.value,Decimal('67335'))

    def test_disaggregation_bridge_fails_closed_when_overlap_does_not_reconcile(self):
        anchor=xbrl(instant_context('a','2026-01-25'), "<nvda:MarketableSecuritiesAndEquitySecuritiesFVNI contextRef='a' unitRef='usd'>51951</nvda:MarketableSecuritiesAndEquitySecuritiesFVNI>")
        current=xbrl(
            instant_context('now','2026-04-26'), instant_context('prior','2026-01-25'),
            "<us-gaap:DebtSecuritiesCurrent contextRef='now' unitRef='usd'>37098</us-gaap:DebtSecuritiesCurrent>",
            "<us-gaap:EquitySecuritiesFvNi contextRef='now' unitRef='usd'>30237</us-gaap:EquitySecuritiesFvNi>",
            "<us-gaap:DebtSecuritiesCurrent contextRef='prior' unitRef='usd'>39065</us-gaap:DebtSecuritiesCurrent>",
            "<us-gaap:EquitySecuritiesFvNi contextRef='prior' unitRef='usd'>12000</us-gaap:EquitySecuritiesFvNi>",
        )
        anchor_fact,_=build_filing_instant_bridge_fact(
            entity_id='NVDA', fiscal_period='2026Q4', normalized_concept='CURRENT_MARKETABLE_SECURITIES', concept='MarketableSecuritiesAndEquitySecuritiesFVNI',
            raw=anchor, raw_sha256='anchor-sha', accession='a', known_as_of='2026-02-25T00:00:00Z', instant='2026-01-25', accounting_regime='US_GAAP_COMPANY_LEVEL')
        fact,proof=build_disaggregation_bridge_fact(
            entity_id='NVDA', fiscal_period='2027Q1', normalized_concept='CURRENT_MARKETABLE_SECURITIES', component_concepts=('DebtSecuritiesCurrent','EquitySecuritiesFvNi'),
            raw=current, raw_sha256='q1-sha', accession='b', known_as_of='2026-05-20T00:00:00Z', instant='2026-04-26', reconcile_instant='2026-01-25',
            anchor_fact=anchor_fact, accounting_regime='US_GAAP_COMPANY_LEVEL')
        self.assertIsNone(fact)
        self.assertEqual(proof['status'],'UNKNOWN')
        self.assertEqual(proof['reason'],'DISAGGREGATION_RECONCILIATION_MISMATCH')

    def test_bridge_contract_freezes_fallback_only_nvda_three_filing_surface(self):
        path=Path(__file__).resolve().parents[1]/"config/yci0_rp1/capital_efficiency_filing_bridges.v0.1.json"
        cfg=json.loads(path.read_text())
        self.assertTrue(cfg["fallback_only"])
        self.assertEqual(cfg["authority"],"RESEARCH")
        nvda=cfg["entities"]["NVDA"]
        self.assertEqual(set(nvda["filings"]),{"FY2026_10K","FY2027_Q1_10Q","FY2027_Q2_10Q"})
        self.assertEqual([r["proof_type"] for r in nvda["rules"]],["FILING_INSTANT_XBRL","DISAGGREGATION_RECONCILIATION","DISAGGREGATION_RECONCILIATION"])

    def test_config_driven_bridge_extends_historical_series_to_full_target_window(self):
        base=[]
        periods=["2024Q4","2025Q1","2025Q2","2025Q3","2025Q4","2026Q1","2026Q2","2026Q3"]
        for i,period in enumerate(periods):
            base.append(FilingFact(entity_id="NVDA",fiscal_period=period,known_as_of=f"2025-01-{i+1:02d}T00:00:00Z",source_locator=f"sec://{period}",content_hash=f"h{i}",concept="CURRENT_MARKETABLE_SECURITIES",value=Decimal(100+i),unit="USD",accounting_regime="US_GAAP_COMPANY_LEVEL"))
        anchor=xbrl(instant_context('a','2026-01-25'), "<nvda:MarketableSecuritiesAndEquitySecuritiesFVNI contextRef='a' unitRef='usd'>51951</nvda:MarketableSecuritiesAndEquitySecuritiesFVNI>")
        q1=xbrl(instant_context('n','2026-04-26'),instant_context('p','2026-01-25'),"<us-gaap:DebtSecuritiesCurrent contextRef='n' unitRef='usd'>37098</us-gaap:DebtSecuritiesCurrent>","<us-gaap:EquitySecuritiesFvNi contextRef='n' unitRef='usd'>30237</us-gaap:EquitySecuritiesFvNi>","<us-gaap:DebtSecuritiesCurrent contextRef='p' unitRef='usd'>39065</us-gaap:DebtSecuritiesCurrent>","<us-gaap:EquitySecuritiesFvNi contextRef='p' unitRef='usd'>12886</us-gaap:EquitySecuritiesFvNi>")
        q2=xbrl(instant_context('n','2026-07-26'),instant_context('p','2026-01-25'),"<us-gaap:DebtSecuritiesCurrent contextRef='n' unitRef='usd'>34143</us-gaap:DebtSecuritiesCurrent>","<us-gaap:EquitySecuritiesFvNi contextRef='n' unitRef='usd'>42783</us-gaap:EquitySecuritiesFvNi>","<us-gaap:DebtSecuritiesCurrent contextRef='p' unitRef='usd'>39065</us-gaap:DebtSecuritiesCurrent>","<us-gaap:EquitySecuritiesFvNi contextRef='p' unitRef='usd'>12886</us-gaap:EquitySecuritiesFvNi>")
        rules=[
            {"rule_id":"anchor","proof_type":"FILING_INSTANT_XBRL","normalized_concept":"CURRENT_MARKETABLE_SECURITIES","fiscal_period":"2026Q4","filing_id":"fy26","concept":"MarketableSecuritiesAndEquitySecuritiesFVNI","instant":"2026-01-25"},
            {"rule_id":"q1","proof_type":"DISAGGREGATION_RECONCILIATION","normalized_concept":"CURRENT_MARKETABLE_SECURITIES","fiscal_period":"2027Q1","filing_id":"q1","components":["DebtSecuritiesCurrent","EquitySecuritiesFvNi"],"instant":"2026-04-26","reconcile_instant":"2026-01-25","anchor_rule_id":"anchor"},
            {"rule_id":"q2","proof_type":"DISAGGREGATION_RECONCILIATION","normalized_concept":"CURRENT_MARKETABLE_SECURITIES","fiscal_period":"2027Q2","filing_id":"q2","components":["DebtSecuritiesCurrent","EquitySecuritiesFvNi"],"instant":"2026-07-26","reconcile_instant":"2026-01-25","anchor_rule_id":"anchor"},
        ]
        filings={"fy26":{"accession":"a"},"q1":{"accession":"b"},"q2":{"accession":"c"}}
        series,proofs,blockers=apply_filing_bridge_rules(entity_id="NVDA",accounting_regime="US_GAAP_COMPANY_LEVEL",base_series={"CURRENT_MARKETABLE_SECURITIES":base},rules=rules,filings=filings,raw_by_filing={"fy26":anchor,"q1":q1,"q2":q2},raw_sha_by_filing={"fy26":"s0","q1":"s1","q2":"s2"},known_as_of_by_accession={"a":"2026-02-25T00:00:00Z","b":"2026-05-20T00:00:00Z","c":"2026-08-26T00:00:00Z"})
        self.assertEqual(blockers,[])
        out=series["CURRENT_MARKETABLE_SECURITIES"]
        self.assertEqual(len(out),11)
        self.assertEqual([f.fiscal_period for f in out[-3:]],["2026Q4","2027Q1","2027Q2"])
        self.assertEqual([f.value for f in out[-3:]],[Decimal("51951"),Decimal("67335"),Decimal("76926")])
        self.assertEqual([p["status"] for p in proofs],["PASS","PASS","PASS"])


if __name__ == '__main__':
    unittest.main()
