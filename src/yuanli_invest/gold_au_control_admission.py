"""Narrow signed control receipts over the existing bounded TLS transport.

The control plane owns an Ed25519 private key; readers/runtimes receive only
its pinned public key. This optional verifier requires cryptography on the
native host. Missing verification never falls back to HMAC or self-signing.
Unknown writes freeze ReceiptClient; readback is a separate read-only call.
"""
from __future__ import annotations

import hashlib
import re
from typing import Mapping, Any

from yuanli_invest.gold_au_receipt_client import (
    ReceiptClient, ReceiptDenied, canonical_bytes, object_hash, ENVIRONMENT, _instant,
)


class PinnedControlVerifier:
    def __init__(self, public_key: bytes):
        if not isinstance(public_key, bytes) or len(public_key) != 32:
            raise ReceiptDenied("CONTROL_PUBLIC_KEY_REQUIRED")
        self.public_key = public_key
        self.fingerprint = "sha256:" + hashlib.sha256(public_key).hexdigest()

    def __call__(self, receipt: Mapping[str, Any]) -> dict:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            from cryptography.exceptions import InvalidSignature
        except ImportError:
            raise ReceiptDenied("CONTROL_ED25519_VERIFIER_UNAVAILABLE") from None
        if not isinstance(receipt, Mapping):
            raise ReceiptDenied("CONTROL_RECEIPT_REQUIRED")
        value = dict(receipt)
        signature = value.pop("signature", None)
        if (not isinstance(signature, str) or not re.fullmatch(r"ed25519:[0-9a-f]{128}", signature)
                or value.get("signer_key_fingerprint") != self.fingerprint
                or value.get("raw_sha256") != object_hash({k:v for k,v in value.items() if k != "raw_sha256"})):
            raise ReceiptDenied("CONTROL_SIGNATURE_OR_HASH_DENIED")
        try:
            Ed25519PublicKey.from_public_bytes(self.public_key).verify(bytes.fromhex(signature[8:]), canonical_bytes(value))
        except (InvalidSignature, ValueError):
            raise ReceiptDenied("CONTROL_SIGNATURE_OR_HASH_DENIED") from None
        return {"source":"independent_signature_verification_result_v3",
            "status":"SIGNATURE_VERIFIED_WITH_PINNED_KEY",
            "verified_signer_id":"GOLD2_INDEPENDENT_CONTROL_V4",
            "verified_signer_key_fingerprint":self.fingerprint,
            "verified_receipt_sha256":value["raw_sha256"]}


class ControlAdmissionClient:
    def __init__(self, receipt_client: ReceiptClient, control_public_key: bytes):
        if type(receipt_client) is not ReceiptClient or receipt_client.role not in {"runtime", "broker_reader"}:
            raise ReceiptDenied("CONTROL_CLIENT_ROLE_DENIED")
        self.client = receipt_client
        self.verifier = PinnedControlVerifier(control_public_key)

    def _call(self, op: str, **fields) -> dict:
        reader = op.endswith("reader_bootstrap")
        if self.client.role != ("broker_reader" if reader else "runtime"):
            raise ReceiptDenied("CONTROL_CLIENT_ROLE_DENIED")
        if set(fields)&{"op", "environment", "account_id", "robot_id", "source_sha256"}:
            raise ReceiptDenied("CONTROL_IDENTITY_OVERRIDE_DENIED")
        request = {"op":op,"environment":ENVIRONMENT,"account_id":self.client.account_id,
            "robot_id":self.client.robot_id,"source_sha256":self.client.source_sha256,**fields}
        write = not op.startswith("read_")
        reply = self.client._call(request, write=write)
        def verify():
            self.verifier(reply)
            if self.client._last_http_status != 200 or any(reply.get(k) != request[k]
                    for k in ("environment", "account_id", "robot_id", "source_sha256")):
                raise ReceiptDenied("CONTROL_REPLY_BINDING_DENIED")
            sources = {
                "prepare_engineering_case":("independent_gold2_engineering_preparation_v4","ENGINEERING_PREPARED"),
                "read_engineering_case":("independent_gold2_engineering_readback_v4","ENGINEERING_READ_ONLY"),
                "admit_reader_bootstrap":("independent_reader_journal_bootstrap_admission_v3","FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED"),
                "read_reader_bootstrap":("independent_reader_bootstrap_readback_v4","BOOTSTRAP_READ_ONLY"),
            }
            if (reply.get("source"),reply.get("status")) != sources[op]:
                raise ReceiptDenied("CONTROL_REPLY_TYPE_DENIED")
            age = (self.client._now() - _instant(reply.get("observed_at"))).total_seconds()
            if age < 0 or (write and age > 15):
                raise ReceiptDenied("CONTROL_ADMISSION_STALE")
            if op == "admit_reader_bootstrap" and reply.get("scope_sha256") != object_hash(fields["scope"]):
                raise ReceiptDenied("CONTROL_BOOTSTRAP_SCOPE_MISMATCH")
            if op == "prepare_engineering_case" and any(reply.get(k) != fields["body"][k]
                    for k in ("command_id", "contract_hash")):
                raise ReceiptDenied("CONTROL_ENGINEERING_CONTRACT_MISMATCH")
            return reply
        return self.client._verified(verify, write=write)

    def prepare_engineering_case(self, *, body: Mapping, broker_evidence_id: str) -> dict:
        return self._call("prepare_engineering_case",body=dict(body),broker_evidence_id=broker_evidence_id)

    def read_engineering_case(self) -> dict:
        return self._call("read_engineering_case")

    def admit_reader_bootstrap(self, scope: Mapping) -> dict:
        return self._call("admit_reader_bootstrap",scope=dict(scope))

    def read_reader_bootstrap(self) -> dict:
        return self._call("read_reader_bootstrap")
