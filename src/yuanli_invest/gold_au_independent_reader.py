"""Independent V3 reader assembly and delivery; no order API or runtime key.

This module implements provenance checks and one-shot publish/readback. It does
not establish OS isolation, create principals, deploy a reader, or grant trading
permission. Deployment isolation must be attested by an external verifier.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import os
from pathlib import Path
import re
import secrets
from typing import Any

from .gold_au_broker_facts import BrokerFactsReader
from .gold_au_receipt_client import (ReceiptClient, ReceiptDenied, ReceiptWriteAmbiguous,
                                    object_hash, validate_native_facts)
from .gold_au_reader_journal import ReaderPublicationJournal
from .gold_paper import PaperDenied, SIMNOW_FIRST

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
SHA = re.compile(r"sha256:[0-9a-f]{64}\Z")
PARTIES = ("broker", "execution", "ledger", "expected")
ISOLATION_SOURCE = "independent_gold2_reader_deployment_binding_v3"


def _identifier(value: Any) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise PaperDenied("INDEPENDENT_READER_IDENTIFIER_INVALID")
    return value


def _time(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise PaperDenied("INDEPENDENT_READER_TIME_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PaperDenied("INDEPENDENT_READER_AWARE_TIME_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _fresh(value: Any, now: datetime, seconds: int = 15) -> datetime:
    observed = _time(value)
    if not 0 <= (now - observed).total_seconds() <= seconds:
        raise PaperDenied("INDEPENDENT_READER_RECEIPT_STALE")
    return observed


def _money(value: Any) -> int:
    if isinstance(value, bool):
        raise PaperDenied("INDEPENDENT_READER_MONEY_INVALID")
    try:
        cents = Decimal(str(value)) * 100
    except (InvalidOperation, ValueError) as exc:
        raise PaperDenied("INDEPENDENT_READER_MONEY_INVALID") from exc
    if (not cents.is_finite() or cents < 0 or cents != cents.to_integral_value()
            or cents > 9007199254740991):
        raise PaperDenied("INDEPENDENT_READER_MONEY_INVALID")
    return int(cents)


def _signed(receipt: Any, verifier: Callable, *, source: str, now: datetime,
            signer_id: str | None = None, signer_key_fingerprint: str | None = None) -> Mapping:
    if (not isinstance(receipt, Mapping) or receipt.get("source") != source
            or receipt.get("environment") != SIMNOW_FIRST or not callable(verifier)):
        raise PaperDenied("INDEPENDENT_READER_SIGNED_SOURCE_REQUIRED")
    try:
        accepted = verifier(receipt)
    except Exception as exc:
        raise PaperDenied("INDEPENDENT_READER_AUTHENTICITY_UNVERIFIED") from exc
    material = {k: v for k, v in receipt.items() if k not in {"raw_sha256", "signature"}}
    if signer_id is not None:
        # The fingerprint must be the verifier's actual pinned verification key,
        # never a field copied from the signed input. Boolean-only verification
        # cannot establish four independent signing principals.
        if (not isinstance(accepted, Mapping)
                or accepted.get("source") != "independent_signature_verification_result_v3"
                or accepted.get("status") != "SIGNATURE_VERIFIED_WITH_PINNED_KEY"
                or accepted.get("verified_signer_id") != signer_id
                or accepted.get("verified_signer_key_fingerprint") != signer_key_fingerprint
                or accepted.get("verified_receipt_sha256") != receipt.get("raw_sha256")):
            raise PaperDenied("INDEPENDENT_PAIRED_ACTUAL_SIGNER_NOT_VERIFIED")
    elif accepted is not True:
        raise PaperDenied("INDEPENDENT_READER_AUTHENTICITY_UNVERIFIED")
    if (not isinstance(receipt.get("raw_sha256"), str)
            or object_hash(material) != receipt["raw_sha256"]):
        raise PaperDenied("INDEPENDENT_READER_AUTHENTICITY_UNVERIFIED")
    _fresh(receipt.get("observed_at"), now)
    return receipt


class IndependentReaderDelivery:
    """A separately attested reader principal, never an OMS constructor.

    Callbacks are configuration dependencies, not authorization. The accepted
    external binding and verifiers must establish each identity in deployment.
    No V2 delegate is inferred; existing PRE_CLAIM/TERMINAL remain separately
    wired until their own real producer/transport acceptance is obtained.
    """
    def __init__(self, *, facts: BrokerFactsReader, client: ReceiptClient,
                 deployment_binding_reader: Callable[[], Mapping], deployment_binding_verifier: Callable,
                 paired_receipt_readers: Mapping[str, Callable[[Mapping], Mapping]] | None,
                 paired_receipt_verifiers: Mapping[str, Callable] | None,
                 paired_claim_binding_reader: Callable[[str, str], Mapping] | None = None,
                 paired_claim_binding_verifier: Callable | None = None,
                 clock: Callable[[], datetime], publication_journal: Path,
                 initialize_publication_journal: bool=False,
                 journal_bootstrap_authorizer: Callable[[Mapping],Mapping] | None=None,
                 process_id: str | None = None):
        if type(facts) is not BrokerFactsReader or type(client) is not ReceiptClient:
            raise PaperDenied("INDEPENDENT_READER_REAL_ADAPTER_REQUIRED")
        if (client.role != "broker_reader" or facts.robot_id != client.robot_id
                or not callable(deployment_binding_reader) or not callable(deployment_binding_verifier)
                or not callable(clock)):
            raise PaperDenied("INDEPENDENT_READER_ROLE_OR_BINDING_DENIED")
        self.facts, self.client = facts, client
        self.binding_reader, self.binding_verifier = deployment_binding_reader, deployment_binding_verifier
        self.party_readers = dict(paired_receipt_readers or {})
        self.party_verifiers, self.clock = dict(paired_receipt_verifiers or {}), clock
        self.claim_binding_reader, self.claim_binding_verifier = paired_claim_binding_reader, paired_claim_binding_verifier
        actual_process_id = f"PID-{os.getpid()}"
        if process_id is not None and process_id != actual_process_id:
            raise PaperDenied("INDEPENDENT_READER_ACTUAL_PROCESS_MISMATCH")
        self.process_id = actual_process_id
        self.pending_publication: dict[str, dict] = {}
        self.unconfirmed_publication_id: str | None = None
        self.permanent_write_block = False
        self._binding(self._now())
        journal_binding={"environment":SIMNOW_FIRST,"account_id":client.account_id,
            "robot_id":client.robot_id,"reader_source_sha256":client.source_sha256}
        if initialize_publication_journal:
            if not callable(journal_bootstrap_authorizer):
                raise PaperDenied("READER_JOURNAL_ONE_SHOT_BOOTSTRAP_AUTHORITY_REQUIRED")
            scope={**journal_binding,"reader_process_id":self.process_id,
                "journal_path_sha256":"sha256:"+hashlib.sha256(str(publication_journal).encode()).hexdigest(),
                "bootstrap_attempt_nonce":secrets.token_hex(32)}
            admission=_signed(journal_bootstrap_authorizer(scope),self.binding_verifier,
                source="independent_reader_journal_bootstrap_admission_v3",now=self._now())
            if (admission.get("status")!="FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED"
                    or admission.get("scope_sha256")!=object_hash(scope)):
                raise PaperDenied("READER_JOURNAL_BOOTSTRAP_NOT_FRESH")
        self.journal = ReaderPublicationJournal(publication_journal,journal_binding,
            initialize=initialize_publication_journal,clock=clock)
        self._restore_journal()

    def _restore_journal(self) -> None:
        prepared=set();acknowledged=set();self.unconfirmed_publication_id=None
        for event in self.journal.read():
            data=event["data"];evidence_id=_identifier(data.get("evidence_id"))
            if event["kind"]=="PublicationPrepared":
                self.import_pending_readback(evidence_id=evidence_id,facts_sha256=data["facts_sha256"],kind=data["kind"])
                self.unconfirmed_publication_id=evidence_id;prepared.add(evidence_id)
            elif event["kind"]=="PublicationIngestAcknowledged":
                acknowledged.add(evidence_id)
            elif event["kind"]=="PublicationIngestUnknown":
                self.permanent_write_block=True
            elif event["kind"]=="PublicationReadbackConfirmed":
                if self.unconfirmed_publication_id==evidence_id:self.unconfirmed_publication_id=None
        if prepared-acknowledged:
            # Prepared is persisted before transmission. A crash before a
            # durable acknowledgement can never be treated as "not sent".
            self.permanent_write_block=True

    def _now(self) -> datetime:
        return _time(self.clock())

    def _binding(self, now: datetime) -> Mapping:
        try:
            receipt = _signed(self.binding_reader(), self.binding_verifier,
                              source=ISOLATION_SOURCE, now=now)
        except PaperDenied:
            raise
        except Exception as exc:
            raise PaperDenied("INDEPENDENT_READER_DEPLOYMENT_RECEIPT_UNAVAILABLE") from exc
        key_fingerprint = "sha256:" + hashlib.sha256(self.client._key).hexdigest()
        if (receipt.get("account_id") != self.client.account_id or receipt.get("robot_id") != self.client.robot_id
                or receipt.get("reader_source_sha256") != self.client.source_sha256
                or receipt.get("reader_process_id") != self.process_id
                or receipt.get("reader_process_id") == receipt.get("runtime_process_id")
                or receipt.get("reader_key_fingerprint") != key_fingerprint
                or not isinstance(receipt.get("runtime_key_fingerprint"), str)
                or not SHA.fullmatch(receipt["runtime_key_fingerprint"])
                or receipt["runtime_key_fingerprint"] == key_fingerprint
                or receipt.get("runtime_source_sha256") == receipt.get("reader_source_sha256")
                or not isinstance(receipt.get("runtime_source_sha256"), str)
                or not SHA.fullmatch(receipt["runtime_source_sha256"])
                or receipt.get("order_submission_capability") is not False
                or receipt.get("runtime_private_key_access") is not False
                or receipt.get("runtime_ledger_write_capability") is not False
                or receipt.get("isolation_status") != "VERIFIED_BY_INDEPENDENT_CONTROL_PLANE"
                or not _time(receipt.get("starts_at")) <= now < _time(receipt.get("expires_at"))):
            raise PaperDenied("INDEPENDENT_READER_ISOLATION_NOT_ATTESTED")
        _identifier(receipt.get("runtime_process_id"))
        _identifier(receipt.get("isolation_receipt_id"))
        return receipt

    def _native(self, *, command_id: str, claim_id: str, contract: str, action: str) -> Mapping:
        value = self.facts.native_order_evidence_v3(command_id=command_id, claim_id=claim_id,
                                                   contract=contract, action=action)
        now = self._now()
        if (not isinstance(value, Mapping) or value.get("source") != "independent_native_order_payload_v3"
                or value.get("environment") != SIMNOW_FIRST or value.get("account_id") != self.client.account_id
                or value.get("robot_id") != self.client.robot_id or value.get("kind") != "NATIVE_ORDER"
                or not isinstance(value.get("facts"), Mapping)
                or object_hash(value["facts"]) != value.get("facts_sha256")
                or value["facts"].get("command_id") != command_id or value["facts"].get("claim_id") != claim_id
                or value["facts"].get("instrument") != contract or value["facts"].get("action") != action):
            raise PaperDenied("INDEPENDENT_READER_NATIVE_PAYLOAD_INVALID")
        observed = _fresh(value.get("observed_at"), now)
        if not observed <= _time(value.get("available_at")) <= now:
            raise PaperDenied("INDEPENDENT_READER_NATIVE_AVAILABILITY_INVALID")
        try:
            validate_native_facts(value["facts"], "NATIVE_ORDER")
        except ReceiptDenied as exc:
            raise PaperDenied("INDEPENDENT_READER_NATIVE_FACTS_INVALID") from exc
        return value

    def _pair(self, body: Mapping, claim_id: str, binding: Mapping, started: datetime) -> Mapping:
        if (set(self.party_readers) != set(PARTIES)
                or len({id(self.party_readers[p]) for p in PARTIES}) != 4
                or not all(callable(self.party_readers[p]) for p in PARTIES)
                or set(self.party_verifiers) != set(PARTIES)
                or len({id(self.party_verifiers[p]) for p in PARTIES}) != 4
                or not all(callable(self.party_verifiers[p]) for p in PARTIES)):
            raise PaperDenied("INDEPENDENT_PAIRED_PRODUCERS_UNWIRED")
        producer_refs = binding.get("paired_producer_refs")
        if (not isinstance(producer_refs, Mapping) or set(producer_refs) != set(PARTIES)
                or len(set(producer_refs.values())) != 4):
            raise PaperDenied("INDEPENDENT_PAIRED_PRODUCER_BINDING_REQUIRED")
        for ref in producer_refs.values():
            _identifier(ref)
        producer_keys = binding.get("paired_producer_key_fingerprints")
        if (not isinstance(producer_keys, Mapping) or set(producer_keys) != set(PARTIES)
                or not all(isinstance(value, str) and SHA.fullmatch(value) for value in producer_keys.values())
                or len(set(producer_keys.values())) != 4):
            raise PaperDenied("INDEPENDENT_PAIRED_SIGNING_IDENTITIES_REQUIRED")
        if not callable(self.claim_binding_reader) or not callable(self.claim_binding_verifier):
            raise PaperDenied("INDEPENDENT_PAIRED_CLAIM_BINDING_UNWIRED")
        relation = _signed(self.claim_binding_reader(body["command_id"], claim_id), self.claim_binding_verifier,
                           source="independent_gold2_parent_child_claim_binding_v3", now=self._now())
        parent_command_id = _identifier(body.get("origin_command_id"))
        parent_claim_id = _identifier(relation.get("parent_claim_id"))
        if (relation.get("account_id") != self.client.account_id or relation.get("robot_id") != self.client.robot_id
                or relation.get("contract") != body["contract"] or relation.get("parent_command_id") != parent_command_id
                or relation.get("child_command_id") != body["command_id"] or relation.get("child_claim_id") != claim_id
                or relation.get("parent_order_id") != body.get("origin_order_id")
                or relation.get("child_action") != "CLOSE_LONG" or relation.get("parent_action") != "OPEN_LONG"
                or relation.get("relationship_status") != "IMMUTABLE_COORDINATOR_LINK_VERIFIED"):
            raise PaperDenied("INDEPENDENT_PAIRED_CLAIM_BINDING_MISMATCH")
        parent = self._native(command_id=parent_command_id, claim_id=parent_claim_id,
                              contract=body["contract"], action="OPEN_LONG")
        child = self._native(command_id=body["command_id"], claim_id=claim_id,
                             contract=body["contract"], action="CLOSE_LONG")
        pf, cf = parent["facts"], child["facts"]
        if (pf["order_status"] != "FILLED" or cf["order_status"] != "FILLED"
                or pf["filled_quantity"] != 1 or cf["filled_quantity"] != 1
                or pf["position_quantity"] != 0 or cf["position_quantity"] != 0
                or pf["pending_order_count"] != 0 or cf["pending_order_count"] != 0
                or pf["order_id"] != body.get("origin_order_id") or pf["order_id"] == cf["order_id"]
                or relation.get("child_order_id") != cf["order_id"]
                or pf["raw_account_sha256"] != cf["raw_account_sha256"]
                or pf["raw_positions_sha256"] != cf["raw_positions_sha256"]):
            raise PaperDenied("INDEPENDENT_PAIRED_NATIVE_FILLS_NOT_FLAT_AND_BOUND")
        current = self.facts.read_current(body["contract"])
        now = self._now()
        if (current.get("environment") != SIMNOW_FIRST or current.get("account_id") != self.client.account_id
                or current.get("contract") != body["contract"] or current.get("positions") != []
                or current.get("pending_order_count") != 0 or current.get("pending_orders") != []
                or current.get("raw_account_sha256") != cf["raw_account_sha256"]):
            raise PaperDenied("INDEPENDENT_PAIRED_CURRENT_BROKER_DRIFT")
        _fresh(current.get("observed_at"), now)
        native_amounts = {"cash_cents": _money(current["broker_equity"]),
                          "available_cents": _money(current["available"]),
                          "frozen_margin_cents": _money(current["frozen_margin"])}
        cut = {"source": "gold2_paired_frozen_evidence_cut_v3", "environment": SIMNOW_FIRST,
            "account_id": self.client.account_id, "robot_id": self.client.robot_id,
            "contract": body["contract"], "parent_command_id": parent_command_id,
            "parent_claim_id": parent_claim_id, "parent_order_id": pf["order_id"],
            "child_command_id": body["command_id"], "child_claim_id": claim_id, "child_order_id": cf["order_id"],
            "parent_native_facts_sha256": parent["facts_sha256"], "child_native_facts_sha256": child["facts_sha256"],
            "native_account_sha256": cf["raw_account_sha256"], "requested_at": now.isoformat()}
        cut_hash = object_hash(cut)
        parties = {}
        for party in PARTIES:
            receipt = _signed(self.party_readers[party](dict(cut)), self.party_verifiers[party],
                              source=f"independent_gold2_{party}_paired_receipt_v3", now=self._now(),
                              signer_id=producer_refs[party], signer_key_fingerprint=producer_keys[party])
            if (receipt.get("account_id") != self.client.account_id or receipt.get("robot_id") != self.client.robot_id
                    or receipt.get("contract") != body["contract"] or receipt.get("producer_id") != producer_refs[party]
                    or receipt.get("signer_key_fingerprint") != producer_keys[party]
                    or _time(receipt.get("observed_at")) < _time(cut["requested_at"])
                    or receipt.get("frozen_cut_sha256") != cut_hash
                    or receipt.get("parent_native_facts_sha256") != parent["facts_sha256"]
                    or receipt.get("child_native_facts_sha256") != child["facts_sha256"]
                    or receipt.get("parent_order_id") != pf["order_id"] or receipt.get("child_order_id") != cf["order_id"]
                    or type(receipt.get("position_quantity")) is not int or receipt["position_quantity"] != 0
                    or type(receipt.get("open_filled_quantity")) is not int or receipt["open_filled_quantity"] != 1
                    or type(receipt.get("close_filled_quantity")) is not int or receipt["close_filled_quantity"] != 1):
                raise PaperDenied("INDEPENDENT_PAIRED_RECEIPT_SCOPE_OR_FILL_MISMATCH")
            amounts = {key: receipt.get(key) for key in native_amounts}
            if (any(type(value) is not int or not 0 <= value <= 9007199254740991 for value in amounts.values())
                    or any(abs(amounts[key] - native_amounts[key]) > 1 for key in amounts)):
                raise PaperDenied("INDEPENDENT_PAIRED_NATIVE_MONEY_DRIFT")
            parties[party] = {"producer_id": producer_refs[party], "proof_sha256": receipt["raw_sha256"],
                **amounts, "position_quantity": 0, "open_filled_quantity": 1, "close_filled_quantity": 1,
                "parent_order_id": pf["order_id"], "child_order_id": cf["order_id"]}
        facts = {**cf, "parent_claim_id": parent_claim_id, "parent_order_id": pf["order_id"], "reconciliation": parties}
        try:
            validate_native_facts(facts, "PAIRED_TERMINAL")
        except ReceiptDenied as exc:
            raise PaperDenied("INDEPENDENT_PAIRED_FACTS_INVALID") from exc
        if (self._now() - started).total_seconds() > 15:
            raise PaperDenied("INDEPENDENT_PAIRED_COLLECTION_STALE")
        return {"kind": "PAIRED_TERMINAL", "observed_at": started.isoformat(), "facts": facts,
                "facts_sha256": object_hash(facts)}

    def __call__(self, *, kind: str, body: Mapping, claim_id: str, now: datetime) -> Mapping:
        with self.journal.publisher_guard():
            self._restore_journal()
            return self._publish(kind=kind,body=body,claim_id=claim_id,now=now)

    def _publish(self, *, kind: str, body: Mapping, claim_id: str, now: datetime) -> Mapping:
        started = self._now()
        if abs((started - _time(now)).total_seconds()) > 15:
            raise PaperDenied("INDEPENDENT_READER_REQUEST_STALE")
        binding = self._binding(started)
        if self.client.write_frozen or self.permanent_write_block:
            raise PaperDenied("INDEPENDENT_READER_WRITES_FROZEN_READBACK_ONLY")
        if self.unconfirmed_publication_id is not None:
            raise PaperDenied("INDEPENDENT_READER_PENDING_PUBLICATION_READBACK_ONLY")
        if not isinstance(body, Mapping) or kind not in {"NATIVE_ORDER", "PAIRED_TERMINAL"}:
            raise PaperDenied("INDEPENDENT_READER_V3_OPERATION_REQUIRED")
        _identifier(body.get("command_id")); _identifier(claim_id)
        if kind == "NATIVE_ORDER":
            value = self._native(command_id=body["command_id"], claim_id=claim_id,
                                 contract=body["contract"], action=body["action"])
        else:
            if body.get("action") != "CLOSE_LONG":
                raise PaperDenied("INDEPENDENT_PAIRED_CLOSE_ONLY")
            value = self._pair(body, claim_id, binding, started)
        if (self._now() - started).total_seconds() > 15:
            raise PaperDenied("INDEPENDENT_READER_COLLECTION_STALE")
        evidence_id = "EV3-" + object_hash({"kind": kind, "observed_at": value["observed_at"],
                                           "facts_sha256": value["facts_sha256"]})[7:]
        if evidence_id in self.pending_publication:
            return self._resolve_publication_locked(evidence_id)
        self.journal.append(kind="PublicationPrepared",at=self._now().isoformat(),data={"evidence_id":evidence_id,
            "facts_sha256":value["facts_sha256"],"kind":kind,"observed_at":value["observed_at"]})
        self.pending_publication[evidence_id] = {"facts_sha256": value["facts_sha256"], "kind": kind}
        self.unconfirmed_publication_id=evidence_id
        # A previous unknown reader write prevents a new ingestion. The exact
        # prior ID can be read separately via resolve_publication; it is never
        # replaced with a new ID or retried after uncertainty.
        if self.client.write_frozen:
            raise PaperDenied("INDEPENDENT_READER_WRITES_FROZEN_READBACK_ONLY")
        try:
            self.client.ingest_native_evidence_v3(evidence_id=evidence_id, kind=kind,
                                                 observed_at=value["observed_at"], facts=value["facts"])
            self.journal.append(kind="PublicationIngestAcknowledged",at=self._now().isoformat(),data={"evidence_id":evidence_id})
        except ReceiptWriteAmbiguous:
            self.permanent_write_block=True
            self.journal.append(kind="PublicationIngestUnknown",at=self._now().isoformat(),data={"evidence_id":evidence_id})
            return self._resolve_publication_locked(evidence_id)
        return self._resolve_publication_locked(evidence_id)

    def resolve_publication(self, evidence_id: str) -> Mapping:
        """Exact immutable readback, including after lost acknowledgement.

        This neither refreshes native observations nor unfreezes client writes.
        Reload the durable original ID/SHA/kind before reading. Imported audit
        hints remain read-only. The same publisher lock serializes confirmed
        local hints so two recovery workers cannot append duplicate transitions.
        """
        with self.journal.publisher_guard():
            self._restore_journal()
            return self._resolve_publication_locked(evidence_id)

    def _resolve_publication_locked(self,evidence_id: str) -> Mapping:
        _identifier(evidence_id)
        expected = self.pending_publication.get(evidence_id)
        if expected is None:
            raise PaperDenied("INDEPENDENT_READER_UNKNOWN_PUBLICATION_ID")
        try:
            result = self.client.read_native_evidence_v3(evidence_id,
                expected_facts_sha256=expected["facts_sha256"])
        except ReceiptDenied as exc:
            raise PaperDenied("INDEPENDENT_READER_PUBLICATION_UNCONFIRMED_NO_RETRY") from exc
        if (result.get("kind") != expected["kind"]
                or "EV3-"+object_hash({"kind":result.get("kind"),"observed_at":result.get("observed_at"),
                    "facts_sha256":result.get("facts_sha256")})[7:]!=evidence_id):
            raise PaperDenied("INDEPENDENT_READER_PUBLICATION_KIND_MISMATCH")
        if self.unconfirmed_publication_id==evidence_id:
            self.journal.append(kind="PublicationReadbackConfirmed",at=self._now().isoformat(),data={"evidence_id":evidence_id})
            self.unconfirmed_publication_id=None
        return result

    def import_pending_readback(self, *, evidence_id: str, facts_sha256: str, kind: str) -> None:
        """Audit-only resume hint; readback still verifies inclusion and identity."""
        _identifier(evidence_id)
        if not isinstance(facts_sha256, str) or not SHA.fullmatch(facts_sha256) or kind not in {"NATIVE_ORDER", "PAIRED_TERMINAL"}:
            raise PaperDenied("INDEPENDENT_READER_RESUME_HINT_INVALID")
        old = self.pending_publication.get(evidence_id)
        value = {"facts_sha256": facts_sha256, "kind": kind}
        if old is not None and old != value:
            raise PaperDenied("INDEPENDENT_READER_RESUME_HINT_CONFLICT")
        self.pending_publication[evidence_id] = value


def build_independent_reader(*, receipt_config: Path, facts: BrokerFactsReader,
                             deployment_binding_reader: Callable, deployment_binding_verifier: Callable,
                             paired_receipt_readers: Mapping[str, Callable] | None,
                             paired_receipt_verifiers: Mapping[str, Callable] | None,
                             paired_claim_binding_reader: Callable | None = None,
                             paired_claim_binding_verifier: Callable | None = None,
                             clock: Callable[[], datetime], publication_journal: Path,
                             initialize_publication_journal: bool=False,
                             journal_bootstrap_authorizer: Callable | None=None,
                             process_id: str | None = None) -> IndependentReaderDelivery:
    """Load only an existing private reader principal; create no key or service."""
    client = ReceiptClient.from_config_file(receipt_config, clock=clock)
    return IndependentReaderDelivery(facts=facts, client=client,
        deployment_binding_reader=deployment_binding_reader, deployment_binding_verifier=deployment_binding_verifier,
        paired_receipt_readers=paired_receipt_readers, paired_receipt_verifiers=paired_receipt_verifiers,
        paired_claim_binding_reader=paired_claim_binding_reader, paired_claim_binding_verifier=paired_claim_binding_verifier,
        clock=clock, publication_journal=publication_journal,
        initialize_publication_journal=initialize_publication_journal,
        journal_bootstrap_authorizer=journal_bootstrap_authorizer,process_id=process_id)
