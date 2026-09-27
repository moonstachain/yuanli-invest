"""Durable-reader adversarial fixtures; never source of live acceptance."""
from datetime import timedelta
import json
import os
from pathlib import Path
import unittest
from tests import test_gold_au_independent_reader as fixtures
from yuanli_invest.gold_au_receipt_client import ReceiptClient, canonical_bytes, object_hash
from yuanli_invest.gold_paper import PaperDenied


class ReaderJournalReviewTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReaderDeliveryTests();self.f.setUp()
    def tearDown(self):self.f.tearDown()

    def _fresh_client(self):
        return ReceiptClient(role='broker_reader',key_file=self.f.keypath,account_id=fixtures.INVESTOR,
            robot_id=479509,source_sha256=fixtures.SOURCE,transport=self.f.transport,clock=lambda:self.f.now)

    def _rewrite(self,path,events):
        previous='0'*64
        for index,event in enumerate(events,1):
            event.update(sequence=index,previous_hash=previous)
            event['event_hash']=object_hash({k:v for k,v in event.items() if k!='event_hash'})
            previous=event['event_hash']
        path.write_bytes(b''.join(canonical_bytes(e)+b'\n' for e in events))

    def test_unknown_ingest_survives_fresh_client_and_confirmed_readback(self):
        delivery=self.f.assembled();self.f.lost_ingest=True
        reply=self.f.native(delivery)
        self.assertTrue(self.f.client.write_frozen)
        self.f.client=self._fresh_client()
        resumed=self.f.assembled()
        self.assertFalse(self.f.client.write_frozen)  # Memory-only flag is gone.
        resumed.resolve_publication(reply['evidence_id'])
        with self.assertRaisesRegex(PaperDenied,'WRITES_FROZEN'):
            self.f.native(resumed)
        self.assertTrue(resumed.permanent_write_block)
        self.assertEqual([r['op'] for r in self.f.calls].count('ingest_native_evidence_v3'),1)

    def test_lost_unknown_journal_is_not_silently_reinitialized(self):
        delivery=self.f.assembled();self.f.lost_ingest=True
        self.f.native(delivery);path=delivery.journal.path;path.unlink()
        self.f.client=self._fresh_client()
        with self.assertRaises(PaperDenied):self.f.assembled()
        self.assertFalse(path.exists())

    def test_hash_valid_invalid_timestamp_is_corruption(self):
        delivery=self.f.assembled();self.f.native(delivery)
        events=[json.loads(line) for line in delivery.journal.path.read_bytes().splitlines()]
        events[-1]['at']='not-a-time';self._rewrite(delivery.journal.path,events)
        with self.assertRaises(PaperDenied):self.f.assembled()

    def test_hash_valid_orphan_ack_is_corruption(self):
        delivery=self.f.assembled();self.f.native(delivery)
        events=[json.loads(line) for line in delivery.journal.path.read_bytes().splitlines()]
        orphan=next(e for e in events if e['kind']=='PublicationIngestAcknowledged')
        self._rewrite(delivery.journal.path,[orphan])
        with self.assertRaises(PaperDenied):self.f.assembled()

    def test_duplicate_json_keys_are_not_canonical_journal(self):
        delivery=self.f.assembled();self.f.native(delivery)
        path=delivery.journal.path;raw=path.read_bytes()
        raw=raw.replace(b'"kind":"PublicationPrepared"',b'"kind":"PublicationPrepared","kind":"PublicationPrepared"',1)
        path.write_bytes(raw)
        with self.assertRaises(PaperDenied):self.f.assembled()

    def test_torn_line_and_shared_or_readable_files_fail_closed(self):
        delivery=self.f.assembled();self.f.native(delivery)
        path=delivery.journal.path;original=path.read_bytes()
        path.write_bytes(original+b'{')
        with self.assertRaises(PaperDenied):self.f.assembled()
        path.write_bytes(original);path.chmod(0o644)
        with self.assertRaises(PaperDenied):self.f.assembled()
        path.chmod(0o600);alias=path.with_name('hardlinked-copy.jsonl');os.link(path,alias)
        with self.assertRaises(PaperDenied):self.f.assembled()

    def test_exact_readback_cannot_refresh_original_observation_time(self):
        delivery=self.f.assembled();reply=self.f.native(delivery)
        original=reply['observed_at'];self.f.now+=timedelta(seconds=60)
        stored=self.f.stored[reply['evidence_id']]
        for field in ('observed_at','received_at','verified_at'):stored[field]=self.f.now.isoformat()
        self.assertNotEqual(stored['observed_at'],original)
        with self.assertRaises(PaperDenied):delivery.resolve_publication(reply['evidence_id'])

    def test_parent_permission_change_after_construction_blocks_publication(self):
        delivery=self.f.assembled();parent=delivery.journal.path.parent
        parent.chmod(0o777)
        try:
            with self.assertRaises(PaperDenied):self.f.native(delivery)
            self.assertEqual(self.f.calls,[])
        finally:parent.chmod(0o700)

    def test_original_observation_remains_old_on_successful_restart_read(self):
        delivery=self.f.assembled();reply=self.f.native(delivery)
        observed=reply['observed_at'];self.f.now+=timedelta(seconds=30)
        self.f.binding=fixtures.signed({**{k:v for k,v in self.f.binding.items() if k not in {'signature','raw_sha256'}},
                                       'observed_at':self.f.now.isoformat()})
        self.f.stored[reply['evidence_id']]['verified_at']=self.f.now.isoformat()
        # Readback may get a fresh verification time, never a fresh observation.
        resumed=self.f.assembled()
        result=resumed.resolve_publication(reply['evidence_id'])
        self.assertEqual(result['observed_at'],observed)

    def test_captured_initialization_admission_cannot_recreate_deleted_unknown_journal(self):
        captured=[]
        def bootstrap(scope):
            admission=fixtures.signed({'source':'independent_reader_journal_bootstrap_admission_v3',
                'environment':fixtures.SIMNOW_FIRST,'observed_at':self.f.now.isoformat(),
                'status':'FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED','scope_sha256':object_hash(scope)})
            captured.append(admission)
            return admission
        delivery=self.f.assembled(journal_bootstrap_authorizer=bootstrap)
        self.f.lost_ingest=True;self.f.native(delivery)
        path=delivery.journal.path;path.unlink()
        with self.assertRaisesRegex(PaperDenied,'BOOTSTRAP_NOT_FRESH'):
            self.f.assembled(initialize_publication_journal=True,
                journal_bootstrap_authorizer=lambda _:captured[0])
        self.assertFalse(path.exists())
        self.assertEqual([r['op'] for r in self.f.calls].count('ingest_native_evidence_v3'),1)

    def test_shared_or_readable_publisher_lock_blocks_before_network(self):
        delivery=self.f.assembled();path=Path(str(delivery.journal.path)+'.lock')
        path.write_bytes(b'');path.chmod(0o644)
        with self.assertRaises(PaperDenied):self.f.native(delivery)
        self.assertEqual(self.f.calls,[])
        path.chmod(0o600);alias=path.with_name('hardlinked-lock');os.link(path,alias)
        with self.assertRaises(PaperDenied):self.f.native(delivery)
        self.assertEqual(self.f.calls,[])

if __name__=='__main__':unittest.main()
