"""Independent adversarial review: synthetic trust boundaries, no acceptance."""
from copy import deepcopy
from datetime import timedelta
import unittest
from tests import test_gold_au_independent_reader as fixtures
from yuanli_invest.gold_paper import PaperDenied


class IndependentReaderReviewTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReaderDeliveryTests();self.f.setUp()
    def tearDown(self):self.f.tearDown()

    def test_lost_ack_readback_never_unfreezes_or_republishes(self):
        delivery=self.f.assembled();self.f.lost_ingest=True
        reply=self.f.native(delivery)
        self.assertTrue(self.f.client.write_frozen)
        for _ in range(2):
            self.assertEqual(delivery.resolve_publication(reply['evidence_id'])['facts_sha256'],reply['facts_sha256'])
        with self.assertRaisesRegex(PaperDenied,'WRITES_FROZEN'):
            self.f.native(delivery)
        ops=[r['op'] for r in self.f.calls]
        self.assertEqual(ops.count('ingest_native_evidence_v3'),1)
        self.assertTrue(self.f.client.write_frozen)

    def test_resume_hint_same_id_cannot_change_expected_hash_or_kind(self):
        delivery=self.f.assembled();reply=self.f.native(delivery)
        count=len(self.f.calls)
        with self.assertRaisesRegex(PaperDenied,'RESUME_HINT_CONFLICT'):
            delivery.import_pending_readback(evidence_id=reply['evidence_id'],facts_sha256='sha256:'+'0'*64,kind=reply['kind'])
        with self.assertRaisesRegex(PaperDenied,'RESUME_HINT_CONFLICT'):
            delivery.import_pending_readback(evidence_id=reply['evidence_id'],facts_sha256=reply['facts_sha256'],kind='PAIRED_TERMINAL')
        self.assertEqual(len(self.f.calls),count)

    def test_matching_hash_cannot_replace_paired_relationship(self):
        self.f.relation=fixtures.signed({**{k:v for k,v in self.f.relation.items() if k not in {'signature','raw_sha256'}},
                                        'parent_order_id':'OTHER-NATIVE-PARENT'})
        with self.assertRaisesRegex(PaperDenied,'CLAIM_BINDING_MISMATCH'):
            self.f.pair()
        self.assertEqual(self.f.calls,[])

    def test_delivery_of_v3_cannot_act_as_v2_or_release_production_gate(self):
        delivery=self.f.assembled()
        for kind in ('PRE_CLAIM','TERMINAL','ORDER_SUBMIT'):
            with self.assertRaisesRegex(PaperDenied,'V3_OPERATION_REQUIRED'):
                delivery(kind=kind,body=fixtures.NATIVE,claim_id='CLM-OPEN',now=self.f.now)
        from scripts.gold_au_runtime_bootstrap import ProductionGoldSimNowRuntime
        from tests.test_gold_simnow_strategy import Harness
        h=Harness()
        runtime=ProductionGoldSimNowRuntime(h.bridge,h.runtime.grant,h.runtime.signing_key,clock=lambda:h.now)
        self.assertEqual(runtime.production_entry_block_reason,'LINKED_PROTECTIVE_EXIT_REAL_ACCEPTANCE_REQUIRED')
        self.assertEqual(self.f.calls,[])

    def test_four_distinct_labels_signed_by_one_actual_key_are_denied(self):
        # Keep four claimed fingerprints/IDs; signatures and verifier's pinned
        # actual key all come from one key. Self-reported labels cannot pass.
        self.f.party_keys=dict.fromkeys(fixtures.PARTIES,fixtures.KEY+b'-one-shared-signer')
        with self.assertRaisesRegex(PaperDenied,'ACTUAL_SIGNER_NOT_VERIFIED'):
            self.f.pair()
        self.assertEqual(self.f.calls,[])

    def test_four_distinct_boolean_verifiers_are_not_signer_proofs(self):
        callbacks={p:(lambda receipt: True) for p in fixtures.PARTIES}
        self.assertEqual(len({id(cb) for cb in callbacks.values()}),4)
        with self.assertRaisesRegex(PaperDenied,'ACTUAL_SIGNER_NOT_VERIFIED'):
            self.f.pair(self.f.assembled(paired_receipt_verifiers=callbacks))
        self.assertEqual(self.f.calls,[])

    def test_signed_party_receipt_predating_exact_requested_cut_is_denied(self):
        self.f.party_mutator=lambda p,r:r.update(observed_at=(self.f.now-timedelta(seconds=1)).isoformat()) if p=='broker' else None
        with self.assertRaisesRegex(PaperDenied,'SCOPE_OR_FILL_MISMATCH'):
            self.f.pair()
        self.assertEqual(self.f.calls,[])

    def test_same_publication_id_is_only_read_again_not_ingested_twice(self):
        delivery=self.f.assembled();first=self.f.native(delivery);second=self.f.native(delivery)
        self.assertEqual(first['evidence_id'],second['evidence_id'])
        self.assertEqual([r['op'] for r in self.f.calls].count('ingest_native_evidence_v3'),1)
        self.assertEqual(self.f.calls[-1]['op'],'read_native_evidence_v3')

    def test_signed_party_receipt_outside_15_second_window_never_publishes(self):
        self.f.party_mutator=lambda p,r:r.update(observed_at=(self.f.now-timedelta(seconds=16)).isoformat()) if p=='broker' else None
        with self.assertRaisesRegex(PaperDenied,'STALE'):
            self.f.pair()
        self.assertEqual(self.f.calls,[])

if __name__=='__main__':unittest.main()
