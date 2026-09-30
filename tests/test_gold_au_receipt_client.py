from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from yuanli_invest.gold_au_receipt_client import (ENDPOINT, ENVIRONMENT, REQUEST_PATH, ReceiptClient,
    ReceiptDenied, ReceiptWriteAmbiguous, canonical_bytes, object_hash)

NOW = datetime.fromisoformat("2026-09-28T08:30:05+08:00")
ROOT = "sha256:" + "a" * 64
SOURCE = "sha256:" + "b" * 64


def record():
    return {"decision_at": "2026-09-28T08:30:00+08:00", "recorded_at": "2026-09-28T08:30:01+08:00",
            "registry_id": "registry-1", "record_id": "record-1", "signal_id": "signal-1",
            "signal_sha256": ROOT, "source_ref": "test-reference", "frozen_dataset_sha256": ROOT,
            "parameters_sha256": ROOT, "forward_decision_id": "forward-1",
            "forward_decision_sha256": ROOT, "outcome_contracts": []}


def proof():
    value = {"status": "VERIFIED_EXTERNAL_TIME_AND_INCLUSION", "verifier_identity": "GOLD2_PAPER_SUPABASE_EDGE_V1",
             "registry_id": "registry-1", "record_id": "record-1", "record_sha256": object_hash(record()),
             "registry_root_sha256": ROOT, "recorded_at": record()["recorded_at"],
             "anchor_received_at": "2026-09-28T08:30:02+08:00"}
    return {**value, "proof_sha256": object_hash(value), "verified_at": NOW.isoformat()}


class ReceiptClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.key = Path(self.temp.name) / "key"
        self.key.write_bytes(b"test-only-no-production-key-000000000000000000000")
        os.chmod(self.key, 0o600)
        self.calls = []
        self.reply, self.http_status = proof(), 200

    def tearDown(self):
        self.temp.cleanup()

    def transport(self, url, headers, body, timeout, bound):
        self.calls.append((url, headers, body, timeout, bound))
        return self.http_status, canonical_bytes(self.reply)

    def client(self, role="signal", **kwargs):
        return ReceiptClient(role=role, key_file=self.key, account_id="account-1" if role != "signal" else None,
                             robot_id=479509 if role != "signal" else None, source_sha256=SOURCE if role != "signal" else None,
                             transport=self.transport, clock=lambda: NOW, **kwargs)

    def test_exact_hmac_and_fixed_tls_material(self):
        self.client().anchor_signal(record(), ROOT)
        url, headers, raw, timeout, bound = self.calls[0]
        self.assertEqual(url, ENDPOINT)
        material = "GOLD2-PAPER-V1\nPOST\n" + REQUEST_PATH + "\n" + headers["X-Gold2-Timestamp"] + "\n" + hashlib.sha256(raw).hexdigest()
        signature = "sha256=" + hmac.new(self.key.read_bytes(), material.encode(), hashlib.sha256).hexdigest()
        self.assertEqual(headers["X-Gold2-Signature"], signature)
        self.assertEqual(timeout, 10)
        self.assertEqual(headers["X-Gold2-Role"], "signal")
        self.assertNotIn(self.key.read_text(), repr(self.client()))

    def test_canonical_unicode_and_integer_only(self):
        self.assertEqual(canonical_bytes({"黄金": 1, "a": [True, None]}), b'{"a":[true,null],"\xe9\xbb\x84\xe9\x87\x91":1}')
        for bad in (1.0, float("nan"), 2**53, "\ud800", {1: "x"}):
            with self.subTest(bad=repr(bad)), self.assertRaises(ReceiptDenied):
                canonical_bytes(bad)

    def test_private_key_rejects_symlink_permission_and_newline(self):
        os.chmod(self.key, 0o644)
        with self.assertRaises(ReceiptDenied): self.client()
        os.chmod(self.key, 0o600)
        link = self.key.with_name("link"); link.symlink_to(self.key)
        with self.assertRaises(ReceiptDenied): ReceiptClient(role="signal", key_file=link)
        self.key.write_bytes(self.key.read_bytes() + b"\n")
        with self.assertRaises(ReceiptDenied): self.client()

    def test_endpoint_config_disabled_and_override_denied(self):
        config = self.key.with_name("config.json")
        config.write_text(json.dumps({"endpoint": "https://evil.invalid", "enabled": True}))
        with self.assertRaises(ReceiptDenied): ReceiptClient.from_config_file(config)
        config.write_text(json.dumps({"endpoint": ENDPOINT, "enabled": False}))
        with self.assertRaises(ReceiptDenied): ReceiptClient.from_config_file(config)

    def test_anchor_wrong_hash_time_or_identity_freezes(self):
        for key, value in (("record_id", "another"), ("proof_sha256", SOURCE),
                           ("verified_at", (NOW - timedelta(seconds=16)).isoformat()),
                           ("anchor_received_at", "2026-09-28T08:31:01+08:00")):
            self.reply = {**proof(), key: value}
            client = self.client()
            with self.subTest(key=key), self.assertRaises(ReceiptWriteAmbiguous):
                client.anchor_signal(record(), ROOT)
            self.assertTrue(client.write_frozen)

    def test_ambiguous_write_never_retries_then_only_readback(self):
        def timeout(*args):
            self.calls.append(args)
            raise TimeoutError("secret should never escape")
        client = ReceiptClient(role="signal", key_file=self.key, transport=timeout, clock=lambda: NOW)
        with self.assertRaises(ReceiptWriteAmbiguous) as caught: client.anchor_signal(record(), ROOT)
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(len(self.calls), 1)
        with self.assertRaises(ReceiptWriteAmbiguous): client.anchor_signal(record(), ROOT)
        self.assertEqual(len(self.calls), 1)
        client._transport = self.transport
        client.read_signal("registry-1", "record-1", expected_record_sha256=object_hash(record()),
                           expected_registry_root_sha256=ROOT, expected_record=record())
        self.assertTrue(client.write_frozen)

    def test_redirect_and_disabled_write_are_ambiguous(self):
        for status in (301, 401, 503):
            self.http_status, self.reply = status, {"status": "SERVICE_DISABLED"}
            with self.subTest(status=status), self.assertRaises(ReceiptWriteAmbiguous):
                self.client().anchor_signal(record(), ROOT)
        self.assertEqual(len(self.calls), 3)

    def test_duplicate_keys_and_oversized_reply_rejected(self):
        for raw in (b'{"status":"A","status":"B"}', b" " * 2_100_001):
            client = ReceiptClient(role="signal", key_file=self.key,
                                   transport=lambda *args: (200, raw), clock=lambda: NOW)
            with self.subTest(size=len(raw)), self.assertRaises(ReceiptWriteAmbiguous):
                client.anchor_signal(record(), ROOT)

    def test_read_does_not_anchor_or_gain_authority(self):
        got = self.client().read_signal("registry-1", "record-1", expected_record_sha256=object_hash(record()),
                                       expected_registry_root_sha256=ROOT, expected_record=record())
        self.assertEqual(got, proof())
        self.assertEqual(json.loads(self.calls[0][2])["op"], "read_signal")
        self.assertNotIn("broker_action_authorized", got)

    def test_roles_cannot_cross_and_v1_claim_unavailable(self):
        client = self.client("runtime")
        with self.assertRaises(ReceiptDenied): client.anchor_signal(record(), ROOT)
        with self.assertRaises(ReceiptDenied): client.claim_order("whatever")
        self.assertEqual(self.calls, [])

    def event(self):
        event = {"at": NOW.isoformat(), "command_id": "command-1", "data": {"quantity": 1},
                 "kind": "OrderClaimRequested", "previous_hash": "0" * 64, "sequence": 1}
        return {**event, "event_hash": object_hash(event)}

    def test_ledger_chain_and_remote_head_binding(self):
        event = self.event()
        self.reply = {"source": "external_append_only_ledger", "accepted": True, "account_id": "account-1",
                      "robot_id": 479509, "last_sequence": 1, "root_hash": event["event_hash"], "anchor_received_at": NOW.isoformat()}
        client = self.client("runtime")
        client.append_ledger([event], event["event_hash"])
        tampered = {**event, "data": {"quantity": 2}}
        with self.assertRaises(ReceiptDenied): client.append_ledger([tampered], event["event_hash"])
        self.reply["robot_id"] = 123
        with self.assertRaises(ReceiptWriteAmbiguous): client.append_ledger([event], event["event_hash"])

    def coordinator(self, **overrides):
        return {"source": "external_account_coordinator_v2", "status": "CLAIMED", "claimed": True,
                "version": 1, "claim_id": "claim-1", "command_id": "command-1", "phase": "CLAIMED",
                "pending_claim_id": "claim-1", "position_quantity": 0, "position_origin_claim_id": None,
                "account_id": "account-1", "robot_id": 479509, "environment": ENVIRONMENT,
                "source_sha256": SOURCE, "ledger_root_hash": ROOT, "ledger_sequence": 1,
                "updated_at": NOW.isoformat(), "freeze_reason": None, **overrides}

    def claim(self, client):
        return client.claim_order_v2(command_id="command-1", contract_hash=ROOT, action="OPEN_LONG", instrument="au2612",
            position_origin_claim_id=None, broker_evidence_id="evidence-1", expected_version=0, ledger_root_hash=ROOT, ledger_sequence=1)

    def test_fresh_v2_claim_config_identity_and_version(self):
        self.reply = self.coordinator()
        client = self.client("runtime")
        self.assertTrue(self.claim(client)["claimed"])
        request = json.loads(self.calls[0][2])
        self.assertEqual(request["account_id"], "account-1")
        self.assertEqual(request["source_sha256"], SOURCE)
        self.reply = self.coordinator(version=2)
        with self.assertRaises(ReceiptWriteAmbiguous): self.claim(client)

    def test_already_claimed_never_grants_second_submit(self):
        self.reply = self.coordinator(status="ALREADY_CLAIMED", claimed=False)
        self.http_status = 409
        self.assertFalse(self.claim(self.client("runtime"))["claimed"])

    def test_v2_remote_identity_tamper(self):
        for key, value in (("account_id", "other"), ("source_sha256", ROOT), ("environment", "REAL"), ("robot_id", 1)):
                self.reply = self.coordinator(**{key: value})
                with self.subTest(key=key), self.assertRaises(ReceiptWriteAmbiguous): self.claim(self.client("runtime"))

    def test_empty_remote_head_only_zero_sequence_special_case(self):
        self.reply = self.coordinator(status="ACCOUNT_READ", claimed=False, version=0, phase="FLAT", claim_id=None,
            command_id=None, pending_claim_id=None, ledger_root_hash="0" * 64, ledger_sequence=0)
        self.assertEqual(self.client("runtime").read_account_state_v2()["phase"], "FLAT")
        self.reply["ledger_sequence"] = 1
        with self.assertRaises(ReceiptDenied): self.client("runtime").read_account_state_v2()

    def test_submit_receipt_must_bind_claim_and_exact_ledger_head(self):
        self.reply = self.coordinator(status="SUBMIT_RECORDED", claimed=False, phase="SUBMIT_ATTEMPTED", version=2, ledger_sequence=2)
        client = self.client("runtime")
        client.record_submit_attempt_v2(claim_id="claim-1", expected_version=1, ledger_root_hash=ROOT, ledger_sequence=2)
        self.reply["claim_id"] = "wrong-claim"
        with self.assertRaises(ReceiptWriteAmbiguous):
            client.record_submit_attempt_v2(claim_id="claim-1", expected_version=1, ledger_root_hash=ROOT, ledger_sequence=2)

    def test_terminal_receipt_and_freeze_state_require_proven_phase(self):
        self.reply = self.coordinator(status="TERMINAL_RECORDED", claimed=False, phase="HELD", version=3,
            pending_claim_id=None, position_quantity=1, position_origin_claim_id="claim-1", ledger_sequence=3)
        self.client("runtime").record_terminal_v2(claim_id="claim-1", broker_evidence_id="terminal-evidence",
            expected_version=2, ledger_root_hash=ROOT, ledger_sequence=3)
        self.reply = self.coordinator(status="FROZEN", claimed=False, phase="FROZEN", version=4,
                                     ledger_sequence=4, freeze_reason="ORDER_STATE_UNKNOWN")
        self.client("runtime").freeze_account_v2(claim_id="claim-1", reason_code="ORDER_STATE_UNKNOWN",
            expected_version=3, ledger_root_hash=ROOT, ledger_sequence=4)
        self.reply["phase"] = "HELD"
        with self.assertRaises(ReceiptWriteAmbiguous):
            self.client("runtime").freeze_account_v2(claim_id="claim-1", reason_code="ORDER_STATE_UNKNOWN",
                expected_version=3, ledger_root_hash=ROOT, ledger_sequence=4)

    def test_unknown_or_wrong_http_coordinator_status_cannot_submit(self):
        for status, http in (("FAKE_SUCCESS", 200), ("CLAIMED", 409), ("ALREADY_CLAIMED", 200)):
            self.reply = self.coordinator(status=status, claimed=status == "CLAIMED")
            self.http_status = http
            with self.subTest(status=status, http=http), self.assertRaises(ReceiptWriteAmbiguous):
                self.claim(self.client("runtime"))

    def test_reader_has_independent_scope_and_exact_fact_hash(self):
        facts = {"position_quantity": 0, "pending_order_count": 0}
        self.reply = {"source": "bound_broker_reader_evidence_v2", "status": "EVIDENCE_RECORDED",
                      "evidence_id": "evidence-1", "facts_sha256": object_hash(facts), "raw_sha256": ROOT,
                      "received_at": NOW.isoformat()}
        client = self.client("broker_reader")
        client.ingest_broker_evidence_v2(evidence_id="evidence-1", kind="PRE_CLAIM", observed_at=NOW.isoformat(),
                                        raw_sha256=ROOT, facts=facts)
        self.assertEqual(self.calls[-1][1]["X-Gold2-Role"], "broker_reader")
        with self.assertRaises(ReceiptDenied): self.claim(client)
        with self.assertRaises(ReceiptDenied):
            self.client("runtime").ingest_broker_evidence_v2(evidence_id="evidence-1", kind="PRE_CLAIM",
                                                            observed_at=NOW.isoformat(), raw_sha256=ROOT, facts=facts)
        self.reply["facts_sha256"] = SOURCE
        with self.assertRaises(ReceiptWriteAmbiguous):
            client.ingest_broker_evidence_v2(evidence_id="evidence-1", kind="PRE_CLAIM", observed_at=NOW.isoformat(),
                                            raw_sha256=ROOT, facts=facts)

    def test_reader_future_observation_denied_before_http(self):
        with self.assertRaises(ReceiptDenied):
            self.client("broker_reader").ingest_broker_evidence_v2(evidence_id="evidence-1", kind="PRE_CLAIM",
                observed_at=(NOW + timedelta(seconds=1)).isoformat(), raw_sha256=ROOT, facts={})
        self.assertEqual(self.calls, [])

    def test_reader_unknown_write_recovers_only_by_bound_readback(self):
        client = self.client("broker_reader")
        client._transport = lambda *args: (_ for _ in ()).throw(TimeoutError())
        facts = {"position_quantity": 0, "pending_order_count": 0}
        digest = object_hash(facts)
        with self.assertRaises(ReceiptWriteAmbiguous):
            client.ingest_broker_evidence_v2(evidence_id="evidence-1", kind="PRE_CLAIM", observed_at=NOW.isoformat(),
                                           raw_sha256=ROOT, facts=facts)
        self.reply = {"source": "bound_broker_reader_evidence_v2", "status": "EVIDENCE_READ", "evidence_id": "evidence-1",
            "environment": ENVIRONMENT, "account_id": "account-1", "robot_id": 479509, "source_sha256": SOURCE,
            "kind": "PRE_CLAIM", "observed_at": (NOW - timedelta(days=1)).isoformat(),
            "raw_sha256": ROOT, "facts_sha256": digest, "facts": facts,
            "received_at": (NOW - timedelta(days=1) + timedelta(seconds=1)).isoformat(), "verified_at": NOW.isoformat()}
        client._transport = self.transport
        client.read_broker_evidence_v2("evidence-1", expected_raw_sha256=ROOT, expected_facts_sha256=digest)
        self.assertTrue(client.write_frozen)
        self.assertNotIn("broker_action_authorized", self.reply)
        self.reply["facts"]["position_quantity"] = 1
        with self.assertRaises(ReceiptDenied):
            client.read_broker_evidence_v2("evidence-1", expected_raw_sha256=ROOT, expected_facts_sha256=digest)


if __name__ == "__main__": unittest.main()
