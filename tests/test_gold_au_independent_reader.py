"""Offline reader trust-boundary fixtures; no real key, service or CTP proof."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import hmac
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import stat
from unittest.mock import patch

from yuanli_invest.gold_au_independent_reader import IndependentReaderDelivery, ISOLATION_SOURCE, PARTIES
from yuanli_invest.gold_au_broker_facts import BrokerFactsReader, digest
from yuanli_invest.gold_au_receipt_client import ReceiptClient, canonical_bytes, object_hash
from yuanli_invest.gold_paper import PaperDenied, SIMNOW_FIRST
from scripts.youquant_gold_simnow_strategy import _verified_added_ctp_binding
from tests.test_gold_au_broker_facts import HostExchange, NOW, INVESTOR, CONTRACT, attestation, signed, verified, binding

SOURCE="sha256:"+"b"*64
KEY=b"fixture-reader-delivery-no-production-secret-000000000000000"
NATIVE={"command_id":"CMD-OPEN","contract":CONTRACT,"action":"OPEN_LONG"}
PAIR={"command_id":"CMD-CLOSE","contract":CONTRACT,"action":"CLOSE_LONG","origin_command_id":"CMD-OPEN","origin_order_id":"platform-111"}


class ReaderDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.keypath=Path(self.temp.name)/"fixture.key";self.keypath.write_bytes(KEY);self.keypath.chmod(0o600)
        self.host=HostExchange();self.now=NOW;self.stored={};self.calls=[];self.lost_ingest=False;self.corrupt_readback=False;self.bootstrap_consumed=False
        self.platforms={"platform-111":binding(),"platform-222":signed({**{k:v for k,v in binding().items() if k not in {"signature","raw_sha256"}},
            "order_id":"platform-222","order_sys_id":"      88","order_ref":"10","direction":"1","offset_flag":"3"})}
        original_order=deepcopy(self.host.rows["ReqQryOrder"][0]);original_trade=deepcopy(self.host.rows["ReqQryTrade"][0])
        self.pair_mode=False
        def platform_reader(order_id):
            p=self.platforms[order_id]
            self.host.rows["ReqQryOrder"]=[dict(original_order,OrderSysID=p["order_sys_id"],OrderRef=p["order_ref"],Direction=p["direction"],CombOffsetFlag=p["offset_flag"])]
            self.host.rows["ReqQryTrade"]=[dict(original_trade,OrderSysID=p["order_sys_id"],OrderRef=p["order_ref"],Direction=p["direction"],OffsetFlag=p["offset_flag"],TradeID="TRADE-"+order_id)]
            if self.pair_mode:self.host.rows["ReqQryInvestorPosition"]=[]
            return p
        def command_reader(command,claim):
            order_id="platform-111" if command=="CMD-OPEN" else "platform-222"
            return signed({"source":"independent_command_native_order_binding","environment":SIMNOW_FIRST,
                "account_id":INVESTOR,"contract":CONTRACT,"observed_at":NOW.isoformat(),"quantity":1,
                "command_id":command,"claim_id":"CLM-OPEN" if command=="CMD-OPEN" else "CLM-CLOSE",
                "action":"OPEN_LONG" if command=="CMD-OPEN" else "CLOSE_LONG","order_id":order_id,
                "platform_binding_sha256":self.platforms[order_id]["raw_sha256"]})
        self.facts=BrokerFactsReader(exchange=self.host,robot_id=479509,clock=lambda:self.now,
            account_attestation_reader=attestation,account_attestation_verifier=_verified_added_ctp_binding,
            independent_receipt_verifier=verified,order_binding_reader=platform_reader,command_order_binding_reader=command_reader)
        self.client=ReceiptClient(role="broker_reader",key_file=self.keypath,account_id=INVESTOR,robot_id=479509,
                                  source_sha256=SOURCE,transport=self.transport,clock=lambda:self.now)
        self.binding=signed({"source":ISOLATION_SOURCE,"environment":SIMNOW_FIRST,"account_id":INVESTOR,"robot_id":479509,
            "reader_source_sha256":SOURCE,"runtime_source_sha256":"sha256:"+"a"*64,
            "reader_process_id":f"PID-{os.getpid()}","runtime_process_id":"PID-INDEPENDENT-RUNTIME",
            "reader_key_fingerprint":"sha256:"+hashlib.sha256(KEY).hexdigest(),"runtime_key_fingerprint":"sha256:"+"c"*64,
            "order_submission_capability":False,"runtime_private_key_access":False,"runtime_ledger_write_capability":False,
            "isolation_status":"VERIFIED_BY_INDEPENDENT_CONTROL_PLANE","isolation_receipt_id":"FIXTURE-ISOLATION",
            "starts_at":(NOW-timedelta(minutes=1)).isoformat(),"expires_at":(NOW+timedelta(minutes=5)).isoformat(),
            "observed_at":NOW.isoformat(),"paired_producer_refs":{p:"PRODUCER-"+p for p in PARTIES},
            "paired_producer_key_fingerprints":{p:"sha256:"+str(i+1)*64 for i,p in enumerate(PARTIES)}})
        self.relation=signed({"source":"independent_gold2_parent_child_claim_binding_v3","environment":SIMNOW_FIRST,
            "account_id":INVESTOR,"robot_id":479509,"contract":CONTRACT,"observed_at":NOW.isoformat(),
            "parent_command_id":"CMD-OPEN","parent_claim_id":"CLM-OPEN","parent_order_id":"platform-111","parent_action":"OPEN_LONG",
            "child_command_id":"CMD-CLOSE","child_claim_id":"CLM-CLOSE","child_order_id":"platform-222","child_action":"CLOSE_LONG",
            "relationship_status":"IMMUTABLE_COORDINATOR_LINK_VERIFIED"})
        self.party_mutator=None;self.seen_cuts=[]
        self.party_keys={p:KEY+b"-test-party-"+p.encode() for p in PARTIES}
        self.binding=signed({**{k:v for k,v in self.binding.items() if k not in {"signature","raw_sha256"}},
            "paired_producer_key_fingerprints":{p:"sha256:"+hashlib.sha256(self.party_keys[p]).hexdigest() for p in PARTIES}})
        def party_reader(p):
            def read(cut):
                self.seen_cuts.append(deepcopy(cut))
                result={"source":f"independent_gold2_{p}_paired_receipt_v3","environment":SIMNOW_FIRST,
                    "account_id":INVESTOR,"robot_id":479509,"contract":CONTRACT,"observed_at":NOW.isoformat(),
                    "producer_id":"PRODUCER-"+p,"signer_key_fingerprint":self.binding["paired_producer_key_fingerprints"][p],
                    "frozen_cut_sha256":object_hash(cut),
                    "parent_native_facts_sha256":cut["parent_native_facts_sha256"],"child_native_facts_sha256":cut["child_native_facts_sha256"],
                    "parent_order_id":"platform-111","child_order_id":"platform-222","position_quantity":0,
                    "open_filled_quantity":1,"close_filled_quantity":1,"cash_cents":1000000000,"available_cents":975000000,"frozen_margin_cents":0}
                if self.party_mutator:self.party_mutator(p,result)
                result["raw_sha256"]=object_hash(result)
                result["signature"]=hmac.new(self.party_keys[p],canonical_bytes(result),hashlib.sha256).hexdigest()
                return result
            return read
        self.readers={p:party_reader(p) for p in PARTIES}
        def party_verifier(p):
            def verify(receipt):
                body={k:v for k,v in receipt.items() if k!="signature"}
                expected=hmac.new(self.party_keys[p],canonical_bytes(body),hashlib.sha256).hexdigest()
                if not hmac.compare_digest(str(receipt.get("signature")),expected):
                    return False
                return {"source":"independent_signature_verification_result_v3",
                    "status":"SIGNATURE_VERIFIED_WITH_PINNED_KEY","verified_signer_id":"PRODUCER-"+p,
                    "verified_signer_key_fingerprint":"sha256:"+hashlib.sha256(self.party_keys[p]).hexdigest(),
                    "verified_receipt_sha256":receipt.get("raw_sha256")}
            return verify
        self.verifiers={p:party_verifier(p) for p in PARTIES}
    def tearDown(self):self.temp.cleanup()
    def transport(self,url,headers,raw,timeout,bound):
        request=json.loads(raw);self.calls.append(request)
        if request["op"]=="ingest_native_evidence_v3":
            result={k:request[k] for k in ("environment","account_id","robot_id","source_sha256","evidence_id","kind","observed_at","facts_sha256","facts")}
            result.update(received_at=self.now.isoformat(),verified_at=self.now.isoformat(),source="bound_broker_reader_evidence_v3",status="EVIDENCE_RECORDED")
            self.stored[request["evidence_id"]]=deepcopy(result)
            if self.lost_ingest:raise TimeoutError("fixture committed then acknowledgement lost")
        else:
            result=deepcopy(self.stored[request["evidence_id"]]);result["status"]="EVIDENCE_READ"
            if self.corrupt_readback:result["facts"]["claim_id"]="OTHER"
        return 200,canonical_bytes(result)
    def assembled(self,**kwargs):
        path=Path(self.temp.name).resolve()/"publisher.jsonl"
        def authorize(scope):
            if self.bootstrap_consumed:raise PaperDenied("FIXTURE_BOOTSTRAP_ALREADY_CONSUMED")
            self.bootstrap_consumed=True
            return signed({"source":"independent_reader_journal_bootstrap_admission_v3","environment":SIMNOW_FIRST,
                "observed_at":self.now.isoformat(),"status":"FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED","scope_sha256":object_hash(scope)})
        values=dict(facts=self.facts,client=self.client,deployment_binding_reader=lambda:self.binding,
            deployment_binding_verifier=verified,paired_receipt_readers=self.readers,paired_receipt_verifiers=self.verifiers,
            paired_claim_binding_reader=lambda *_:self.relation,paired_claim_binding_verifier=verified,clock=lambda:self.now,
            publication_journal=path,initialize_publication_journal=not path.exists() and not self.bootstrap_consumed,
            journal_bootstrap_authorizer=authorize)
        values.update(kwargs);return IndependentReaderDelivery(**values)
    def native(self,delivery=None):return (delivery or self.assembled())(kind="NATIVE_ORDER",body=NATIVE,claim_id="CLM-OPEN",now=self.now)
    def pair(self,delivery=None):
        self.pair_mode=True
        return (delivery or self.assembled())(kind="PAIRED_TERMINAL",body=PAIR,claim_id="CLM-CLOSE",now=self.now)
    def test_native_real_query_payload_is_ingested_once_then_independently_read(self):
        result=self.native();self.assertEqual(result["status"],"EVIDENCE_READ")
        self.assertEqual(result["facts"]["claim_id"],"CLM-OPEN")
        self.assertEqual([r["op"] for r in self.calls],["ingest_native_evidence_v3","read_native_evidence_v3"])
        self.assertFalse(any(c[0] in {"Buy","Sell","CancelOrder"} for c in self.host.calls))
    def test_signed_isolation_receipt_and_actual_reader_key_process_are_required(self):
        patches=({"runtime_process_id":f"PID-{os.getpid()}"},{"runtime_key_fingerprint":self.binding["reader_key_fingerprint"]},
            {"reader_source_sha256":"sha256:"+"f"*64},{"order_submission_capability":True},{"runtime_private_key_access":True},
            {"runtime_ledger_write_capability":True},{"isolation_status":"SELF_DECLARED"},{"reader_process_id":"PID-FAKE"})
        original=self.binding
        for patch in patches:
            self.binding=signed({**{k:v for k,v in original.items() if k not in {"raw_sha256","signature"}},**patch})
            with self.assertRaises(PaperDenied):self.assembled()
        self.binding=original
        with self.assertRaisesRegex(PaperDenied,"ACTUAL_PROCESS"):self.assembled(process_id="PID-FORGED")
        self.assertEqual(self.calls,[])
    def test_runtime_principal_is_never_reader(self):
        runtime=ReceiptClient(role="runtime",key_file=self.keypath,account_id=INVESTOR,robot_id=479509,source_sha256=SOURCE,transport=self.transport,clock=lambda:self.now)
        with self.assertRaisesRegex(PaperDenied,"ROLE_OR_BINDING"):self.assembled(client=runtime)
    def test_forged_or_stale_deployment_receipt_is_not_a_gate(self):
        self.binding["isolation_status"]="VERIFIED_BY_INDEPENDENT_CONTROL_PLANE";self.binding["signature"]="00"
        with self.assertRaisesRegex(PaperDenied,"AUTHENTICITY"):self.assembled()
        self.binding=signed({**{k:v for k,v in self.binding.items() if k not in {"raw_sha256","signature"}},"observed_at":(NOW-timedelta(seconds=16)).isoformat()})
        with self.assertRaisesRegex(PaperDenied,"STALE"):self.assembled()
    def test_missing_command_native_mapping_does_not_publish(self):
        delivery=self.assembled();self.facts.command_binding_reader=None
        with self.assertRaisesRegex(PaperDenied,"BINDING_UNWIRED"):self.native(delivery)
        self.assertEqual(self.calls,[])
    def test_lost_ingest_ack_reads_exact_inclusion_and_never_unfreezes(self):
        delivery=self.assembled();self.lost_ingest=True
        result=self.native(delivery);self.assertEqual(result["status"],"EVIDENCE_READ");self.assertTrue(self.client.write_frozen)
        self.assertEqual(len(self.calls),2)
        with self.assertRaisesRegex(PaperDenied,"WRITES_FROZEN"):self.native(delivery)
        self.assertEqual(len(self.calls),2)
    def test_corrupt_readback_keeps_uncertain_and_does_not_reingest(self):
        delivery=self.assembled();self.lost_ingest=True;self.corrupt_readback=True
        with self.assertRaisesRegex(PaperDenied,"UNCONFIRMED_NO_RETRY"):self.native(delivery)
        self.assertEqual(len(self.calls),2);self.assertTrue(self.client.write_frozen)
    def test_pair_native_both_fills_and_four_distinct_signed_sources_are_bound_to_same_cut(self):
        result=self.pair();facts=result["facts"]
        self.assertEqual(result["kind"],"PAIRED_TERMINAL");self.assertEqual(facts["position_quantity"],0)
        self.assertEqual(facts["parent_claim_id"],"CLM-OPEN");self.assertEqual(len(set(p["proof_sha256"] for p in facts["reconciliation"].values())),4)
        self.assertEqual(len(self.seen_cuts),4);self.assertTrue(all(cut==self.seen_cuts[0] for cut in self.seen_cuts))
    def test_pair_missing_producer_or_relation_never_publishes(self):
        for patch in ({"paired_receipt_readers":{}},{"paired_claim_binding_reader":None},{"paired_receipt_verifiers":None}):
            with self.assertRaises(PaperDenied):self.pair(self.assembled(**patch))
        self.assertEqual(self.calls,[])
    def test_same_callback_or_cloned_producer_identity_is_denied(self):
        same=lambda _:{}
        with self.assertRaisesRegex(PaperDenied,"PRODUCERS_UNWIRED"):self.pair(self.assembled(paired_receipt_readers=dict.fromkeys(PARTIES,same)))
        self.binding=signed({**{k:v for k,v in self.binding.items() if k not in {"raw_sha256","signature"}},"paired_producer_refs":dict.fromkeys(PARTIES,"CLONED")})
        with self.assertRaisesRegex(PaperDenied,"PRODUCER_BINDING"):self.pair()
    def test_signed_but_wrong_cut_order_money_or_quantity_is_denied(self):
        patches=({"frozen_cut_sha256":"sha256:"+"0"*64},{"parent_order_id":"WRONG"},{"position_quantity":True},
            {"close_filled_quantity":0},{"cash_cents":1},{"producer_id":"PRODUCER-ledger"})
        for patch in patches:
            self.party_mutator=lambda p,r: r.update(patch) if p=="broker" else None
            with self.assertRaises(PaperDenied):self.pair()
        self.assertEqual(self.calls,[])
    def test_wrong_signed_child_parent_relation_is_denied(self):
        self.relation=signed({**{k:v for k,v in self.relation.items() if k not in {"signature","raw_sha256"}},"child_claim_id":"CLM-OTHER"})
        with self.assertRaisesRegex(PaperDenied,"CLAIM_BINDING_MISMATCH"):self.pair()
    def test_real_positions_or_pending_orders_cannot_be_hidden_by_four_agreeing_parties(self):
        self.host.positions=[{"ContractType":CONTRACT,"Type":0,"Amount":1,"Margin":1}]
        with self.assertRaisesRegex(PaperDenied,"CURRENT_BROKER_DRIFT"):self.pair()
        self.assertEqual(self.calls,[])
    def test_restart_hint_only_allows_readback_never_a_write(self):
        old=self.assembled();result=self.native(old);new=self.assembled()
        new.import_pending_readback(evidence_id=result["evidence_id"],facts_sha256=result["facts_sha256"],kind=result["kind"])
        count=len(self.calls);self.assertEqual(new.resolve_publication(result["evidence_id"])["status"],"EVIDENCE_READ")
        self.assertEqual(len(self.calls),count+1);self.assertEqual(self.calls[-1]["op"],"read_native_evidence_v3")
    def test_exact_repeated_publication_reads_inclusion_instead_of_reingesting(self):
        delivery=self.assembled();first=self.native(delivery);second=self.native(delivery)
        self.assertEqual(first["evidence_id"],second["evidence_id"])
        self.assertEqual([r["op"] for r in self.calls],
            ["ingest_native_evidence_v3","read_native_evidence_v3","read_native_evidence_v3"])
    def test_cloned_party_verifier_is_not_four_principals(self):
        same=lambda _:True
        with self.assertRaisesRegex(PaperDenied,"PRODUCERS_UNWIRED"):
            self.pair(self.assembled(paired_receipt_verifiers=dict.fromkeys(PARTIES,same)))
        self.assertEqual(self.calls,[])
    def test_boolean_or_self_reported_signer_cannot_establish_four_principals(self):
        def boolean_verifier():
            return lambda _:True
        with self.assertRaisesRegex(PaperDenied,"ACTUAL_SIGNER_NOT_VERIFIED"):
            self.pair(self.assembled(paired_receipt_verifiers={p:boolean_verifier() for p in PARTIES}))
        def wrong_key_verifier(p):
            def verify(receipt):
                return {"source":"independent_signature_verification_result_v3","status":"SIGNATURE_VERIFIED_WITH_PINNED_KEY",
                    "verified_signer_id":"PRODUCER-"+p,"verified_signer_key_fingerprint":"sha256:"+"0"*64,
                    "verified_receipt_sha256":receipt.get("raw_sha256")}
            return verify
        with self.assertRaisesRegex(PaperDenied,"ACTUAL_SIGNER_NOT_VERIFIED"):
            self.pair(self.assembled(paired_receipt_verifiers={p:wrong_key_verifier(p) for p in PARTIES}))
        self.assertEqual(self.calls,[])
    def test_pair_signing_key_identities_must_be_distinct_and_bound(self):
        original=self.binding
        self.binding=signed({**{k:v for k,v in original.items() if k not in {"signature","raw_sha256"}},
            "paired_producer_key_fingerprints":dict.fromkeys(PARTIES,"sha256:"+"1"*64)})
        with self.assertRaisesRegex(PaperDenied,"SIGNING_IDENTITIES"):self.pair()
        self.binding=original
        self.party_mutator=lambda p,r:r.update(signer_key_fingerprint="sha256:"+"0"*64) if p=="broker" else None
        with self.assertRaises(PaperDenied):self.pair()
        self.assertEqual(self.calls,[])
    def test_unknown_reader_write_remains_permanently_blocked_after_restart(self):
        old=self.assembled();self.lost_ingest=True;result=self.native(old)
        restarted_client=ReceiptClient(role="broker_reader",key_file=self.keypath,account_id=INVESTOR,robot_id=479509,
            source_sha256=SOURCE,transport=self.transport,clock=lambda:self.now)
        self.assertFalse(restarted_client.write_frozen)
        restarted=self.assembled(client=restarted_client)
        self.assertTrue(restarted.permanent_write_block)
        before=len(self.calls)
        with self.assertRaisesRegex(PaperDenied,"WRITES_FROZEN"):self.native(restarted)
        self.assertEqual(restarted.resolve_publication(result["evidence_id"])["status"],"EVIDENCE_READ")
        self.assertEqual(len(self.calls),before+1)
    def test_unconfirmed_readback_survives_restart_and_prevents_new_id_ingest(self):
        old=self.assembled();self.corrupt_readback=True
        with self.assertRaisesRegex(PaperDenied,"UNCONFIRMED"):self.native(old)
        restarted=self.assembled();self.assertIsNotNone(restarted.unconfirmed_publication_id)
        self.now=NOW+timedelta(seconds=1)
        before=len(self.calls)
        with self.assertRaisesRegex(PaperDenied,"PENDING_PUBLICATION"):self.native(restarted)
        self.assertEqual(len(self.calls),before)
    def test_journal_tamper_or_world_readable_file_denies_assembly(self):
        delivery=self.assembled();self.native(delivery)
        path=Path(self.temp.name).resolve()/"publisher.jsonl"
        raw=path.read_bytes();path.write_bytes(raw.replace(b"PublicationPrepared",b"PublicationChanged"))
        with self.assertRaises(PaperDenied):self.assembled()
        path.write_bytes(raw);path.chmod(0o644)
        with self.assertRaisesRegex(PaperDenied,"FILE_DENIED"):self.assembled()
    def test_duplicate_reader_instances_reload_shared_journal_before_new_publication(self):
        first=self.assembled();second=self.assembled()
        self.native(first);self.native(second)
        self.assertEqual([r["op"] for r in self.calls].count("ingest_native_evidence_v3"),1)
    def test_concurrent_publisher_cannot_enter_network_pipeline(self):
        delivery=self.assembled()
        with delivery.journal.publisher_guard():
            with self.assertRaisesRegex(PaperDenied,"ALREADY_RUNNING"):self.native(delivery)
        self.assertEqual(self.calls,[])
    def test_crash_after_prepared_before_acknowledged_does_not_assume_not_sent(self):
        delivery=self.assembled()
        delivery.journal.append(kind="PublicationPrepared",at=NOW.isoformat(),data={"evidence_id":"EV3-"+object_hash({"kind":"NATIVE_ORDER","observed_at":NOW.isoformat(),"facts_sha256":"sha256:"+"0"*64})[7:],
            "facts_sha256":"sha256:"+"0"*64,"kind":"NATIVE_ORDER","observed_at":NOW.isoformat()})
        restarted=self.assembled();self.assertTrue(restarted.permanent_write_block)
        with self.assertRaisesRegex(PaperDenied,"WRITES_FROZEN"):self.native(restarted)
        self.assertEqual(self.calls,[])
    def test_created_journal_lock_and_prepared_record_fsync_parent_directory(self):
        fsync=os.fsync;kinds=[]
        def tracked(descriptor):
            kinds.append("directory" if stat.S_ISDIR(os.fstat(descriptor).st_mode) else "file")
            return fsync(descriptor)
        with patch("yuanli_invest.gold_au_reader_journal.os.fsync",side_effect=tracked):
            delivery=self.assembled();self.native(delivery)
        self.assertGreaterEqual(kinds.count("directory"),5)
        self.assertGreaterEqual(kinds.count("file"),5)
        self.assertEqual(kinds[:2],["file","directory"])
    def test_first_start_requires_fresh_external_one_shot_bootstrap(self):
        with self.assertRaisesRegex(PaperDenied,"BOOTSTRAP_AUTHORITY_REQUIRED"):
            self.assembled(journal_bootstrap_authorizer=None)
        self.assertFalse((Path(self.temp.name).resolve()/"publisher.jsonl").exists())
        stale=signed({"source":"independent_reader_journal_bootstrap_admission_v3","environment":SIMNOW_FIRST,
            "observed_at":NOW.isoformat(),"status":"FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED","scope_sha256":"sha256:"+"0"*64})
        with self.assertRaisesRegex(PaperDenied,"BOOTSTRAP_NOT_FRESH"):
            self.assembled(journal_bootstrap_authorizer=lambda _:stale)
        delivery=self.assembled();self.native(delivery)
        with self.assertRaisesRegex(PaperDenied,"ALREADY_CONSUMED"):
            self.assembled(initialize_publication_journal=True)
        self.assertEqual([r["op"] for r in self.calls].count("ingest_native_evidence_v3"),1)
    def test_unknown_journal_deletion_cannot_be_treated_as_first_start(self):
        delivery=self.assembled();self.lost_ingest=True;self.native(delivery)
        (Path(self.temp.name).resolve()/"publisher.jsonl").unlink()
        with self.assertRaisesRegex(PaperDenied,"MISSING_RESUME_DENIED"):self.assembled()
        with self.assertRaisesRegex(PaperDenied,"ALREADY_CONSUMED"):
            self.assembled(initialize_publication_journal=True)
        self.assertEqual([r["op"] for r in self.calls].count("ingest_native_evidence_v3"),1)
    def test_journal_symlink_swap_after_construction_blocks_before_network(self):
        delivery=self.assembled();path=delivery.journal.path
        target=Path(self.temp.name).resolve()/"unrelated.jsonl";target.write_bytes(path.read_bytes());target.chmod(0o600)
        path.unlink();path.symlink_to(target)
        with self.assertRaises(PaperDenied):self.native(delivery)
        self.assertEqual(self.calls,[])
    def test_two_restart_readbacks_append_one_confirmed_transition(self):
        old=self.assembled();self.corrupt_readback=True
        with self.assertRaisesRegex(PaperDenied,"UNCONFIRMED"):self.native(old)
        first=self.assembled();second=self.assembled();evidence_id=first.unconfirmed_publication_id
        self.corrupt_readback=False
        first.resolve_publication(evidence_id);second.resolve_publication(evidence_id)
        self.assertEqual(sum(e["kind"]=="PublicationReadbackConfirmed" for e in first.journal.read()),1)
        self.assertIsNone(self.assembled().unconfirmed_publication_id)
    def test_v2_is_not_silently_replaced_with_native_proof(self):
        with self.assertRaisesRegex(PaperDenied,"V3_OPERATION_REQUIRED"):
            self.assembled()(kind="PRE_CLAIM",body=NATIVE,claim_id="CLM-OPEN",now=self.now)
        self.assertEqual(self.calls,[])

if __name__=="__main__":unittest.main()
