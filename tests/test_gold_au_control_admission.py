"""Ephemeral offline signing keys only; never a cloud admission or CTP proof."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from yuanli_invest.gold_au_control_admission import ControlAdmissionClient, PinnedControlVerifier
from yuanli_invest.gold_au_receipt_client import ReceiptClient, ReceiptDenied, ReceiptWriteAmbiguous, canonical_bytes, object_hash

NOW=datetime(2026,9,29,1,15,tzinfo=timezone.utc)
H='sha256:'+'a'*64


class ControlAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.path=Path(self.tmp.name)/'test-only.key'
        self.path.write_bytes(b'fixture-runtime-key-never-production-000000');self.path.chmod(0o600)
        self.secret=Ed25519PrivateKey.generate()
        self.public=self.secret.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        self.calls=[];self.unknown=False;self.mutation=None
        self.client=ReceiptClient(role='broker_reader',key_file=self.path,account_id='TEST-ONLY-ACCOUNT',
            robot_id=19,source_sha256=H,transport=self.transport,clock=lambda:NOW)
        self.control=ControlAdmissionClient(self.client,self.public)
        self.scope={'environment':'SIMNOW_FIRST_NORMAL','account_id':'TEST-ONLY-ACCOUNT','robot_id':19,
            'reader_source_sha256':H,'reader_process_id':'PID-123','journal_path_sha256':H,
            'bootstrap_attempt_nonce':'b'*64}

    def tearDown(self): self.tmp.cleanup()

    def signed(self,value):
        r={**value,'signer_key_fingerprint':'sha256:'+hashlib.sha256(self.public).hexdigest()}
        r['raw_sha256']=object_hash(r)
        r['signature']='ed25519:'+self.secret.sign(canonical_bytes(r)).hex()
        return r

    def transport(self,url,headers,body,timeout,maximum):
        import json
        q=json.loads(body);self.calls.append(q)
        result={k:q[k] for k in ('environment','account_id','robot_id','source_sha256')}
        result.update(deployment_id='FIXTURE-DEPLOYMENT',scope_sha256=object_hash(self.scope),observed_at=NOW.isoformat())
        if q['op']=='admit_reader_bootstrap':
            result.update(source='independent_reader_journal_bootstrap_admission_v3',status='FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED')
            if self.unknown: raise TimeoutError('fixture committed but lost ACK')
        else: result.update(source='independent_reader_bootstrap_readback_v4',status='BOOTSTRAP_READ_ONLY')
        if self.mutation: self.mutation(result)
        return 200,canonical_bytes(self.signed(result))

    def test_pinned_public_verifier_and_one_shot_exact_scope(self):
        r=self.control.admit_reader_bootstrap(self.scope)
        self.assertEqual(r['scope_sha256'],object_hash(self.scope))
        p=self.control.verifier(r);self.assertEqual(p['verified_signer_id'],'GOLD2_INDEPENDENT_CONTROL_V4')
        self.assertNotIn('private_key',vars(self.control.verifier))

    def test_other_pinned_key_and_tampering_rejected(self):
        r=self.control.admit_reader_bootstrap(self.scope)
        with self.assertRaises(ReceiptDenied): PinnedControlVerifier(b'0'*32)(r)
        r['account_id']='FAKE'
        with self.assertRaises(ReceiptDenied):self.control.verifier(r)

    def test_unknown_write_permanently_freezes_new_submission_read_only_recovers(self):
        self.unknown=True
        with self.assertRaises(ReceiptWriteAmbiguous):self.control.admit_reader_bootstrap(self.scope)
        with self.assertRaises(ReceiptWriteAmbiguous):self.control.admit_reader_bootstrap(self.scope)
        r=self.control.read_reader_bootstrap()
        self.assertEqual(r['status'],'BOOTSTRAP_READ_ONLY');self.assertTrue(self.client.write_frozen)
        self.assertEqual([q['op'] for q in self.calls],['admit_reader_bootstrap','read_reader_bootstrap'])

    def test_signed_but_wrong_account_scope_or_stale_reply_freezes(self):
        for mutation in (lambda r:r.update(account_id='OTHER'), lambda r:r.update(scope_sha256='sha256:'+'f'*64),
                         lambda r:r.update(observed_at='2026-09-29T01:14:00Z')):
            self.mutation=mutation;self.client.write_frozen=False
            with self.assertRaises(ReceiptDenied):self.control.admit_reader_bootstrap(self.scope)
            self.assertTrue(self.client.write_frozen)

    def test_reader_cannot_prepare_engineering_or_supply_identity_override(self):
        with self.assertRaises(ReceiptDenied):self.control.prepare_engineering_case(body={},broker_evidence_id='X')
        with self.assertRaises(ReceiptDenied):self.control._call('admit_reader_bootstrap',account_id='OTHER')
        self.assertEqual(self.calls,[])


if __name__=='__main__':unittest.main()
