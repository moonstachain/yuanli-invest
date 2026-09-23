import unittest

from runtime.yci0_rp0.audit import AuditError, build_reality_audit
from runtime.yci0_rp0.shadow import ShadowError, freeze_shadow
from runtime.yci0_rp0.narrative_transmission import NarrativeTransmissionCard
from runtime.yci0_rp0.price_payoff import PricePayoffCard
from runtime.yci0_rp0.projection_compiler import ResearchProjection


def projection():
    n=NarrativeTransmissionCard(
        narrative_stage='D2', dominant_story='x', narrative_gap_hypothesis='y',
        primary_chain=('a','b'), current_bottleneck='a', next_bottleneck_hypothesis='b',
        common_shock_branch='common shock', hard_negative_branch='hard negative', evidence_refs=('e1',),
    )
    p=PricePayoffCard(
        implied_belief='i', scenarios={'BULL':'b','BASE':'base','BEAR':'bear','HARD_NEGATIVE':'h'},
        defeat_condition='capex decelerates', survival_cost='preserve optionality',
        book_mapping={'S':'s','C':'c','R':'r','X':'x'}, evidence_refs=('p1',),
    )
    return ResearchProjection(
        projection_id='proj-1', question_id='YCI0-RP0-CQ-001', as_of='2026-09-17T00:00:00Z',
        reality_as_of='2026-09-17T00:00:00Z', context_pack_id='ctx-1', narrative=n, price_payoff=p,
        defeat_condition='capex decelerates', confidence='MEDIUM', evidence_refs=('e1','p1'), audit_eligible=True,
    )


def audit(verdict='PASS'):
    return build_reality_audit(
        projection(), hard_negative='AI monetization fails', evidence_gap='power-load PIT series incomplete',
        common_shock='real yields rise sharply', survival_risk='avoid capital impairment',
        defeat_condition='capex decelerates', verdict=verdict, reviewer='HUMAN_PRINCIPAL',
    )


class ShadowTests(unittest.TestCase):
    def test_audit_requires_all_six_load_bearing_fields(self):
        base=dict(
            projection=projection(), hard_negative='h', evidence_gap='e', common_shock='c',
            survival_risk='s', defeat_condition='d', verdict='PASS', reviewer='human',
        )
        for field in ('hard_negative','evidence_gap','common_shock','survival_risk','defeat_condition','verdict'):
            kwargs=dict(base); kwargs[field]=''
            with self.subTest(field=field):
                with self.assertRaises(AuditError): build_reality_audit(**kwargs)

    def test_shadow_denied_when_audit_not_pass(self):
        for verdict in ('OPEN','BLOCKED','UNKNOWN','NO_GO'):
            with self.subTest(verdict=verdict):
                with self.assertRaises(ShadowError):
                    freeze_shadow(projection(), audit(verdict), shadow_authorized=True, t0_known_as_of='2026-09-17T00:00:00Z')

    def test_shadow_denied_when_shadow_authority_absent(self):
        with self.assertRaises(ShadowError):
            freeze_shadow(projection(), audit('PASS'), shadow_authorized=False, t0_known_as_of='2026-09-17T00:00:00Z')

    def test_shadow_t0_hashes_and_schedule_are_immutable(self):
        s=freeze_shadow(projection(), audit('PASS'), shadow_authorized=True, t0_known_as_of='2026-09-17T00:00:00Z')
        self.assertTrue(s.t0_evidence_hash)
        self.assertTrue(s.t0_context_hash)
        self.assertTrue(s.t0_projection_hash)
        self.assertEqual(tuple(s.review_schedule.keys()), ('T+30','T+90','T+180'))
        self.assertFalse(s.capital_authorized)
        self.assertFalse(s.execution_authorized)
        with self.assertRaises(Exception):
            s.t0_projection_hash='mutated'

    def test_shadow_schedule_is_future_only_and_no_fake_settlement(self):
        s=freeze_shadow(projection(), audit('PASS'), shadow_authorized=True, t0_known_as_of='2026-09-17T00:00:00Z')
        self.assertEqual(s.status, 'SHADOW_PREREGISTERED')
        self.assertIsNone(s.settlement_result)
        self.assertGreater(s.review_schedule['T+30'], s.t0_known_as_of)
        self.assertGreater(s.review_schedule['T+90'], s.review_schedule['T+30'])
        self.assertGreater(s.review_schedule['T+180'], s.review_schedule['T+90'])


if __name__=='__main__': unittest.main()
