"""Bind local OMS transitions to the account-wide durable v2 coordinator.

Evidence IDs must come from a separately authenticated broker-reader receipt.
This module has no reader key, no order API and no blind mutation retries.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Mapping

from yuanli_invest.gold_paper import PaperDenied, PaperLedger, SIMNOW_FIRST
from yuanli_invest.gold_au_receipt_client import object_hash, validate_native_facts, ReceiptDenied


class AccountCoordinator:
    def __init__(self, client: Any, broker_evidence_reader: Callable[..., Mapping[str, Any]],
                 persist: Callable[[PaperLedger], None]):
        if not callable(broker_evidence_reader):
            raise PaperDenied("NO_INDEPENDENT_COORDINATOR_BROKER_EVIDENCE")
        self.client = client
        self.broker_evidence_reader = broker_evidence_reader
        if not callable(persist):
            raise PaperDenied("NO_COORDINATOR_DURABLE_LEDGER")
        self.persist = persist

    def _state(self) -> Mapping[str, Any]:
        try:
            return self.client.read_account_state_v2()
        except Exception as exc:
            raise PaperDenied("ACCOUNT_COORDINATOR_READ_UNCERTAIN") from exc

    def _evidence(self, *, kind: str, body: Mapping, claim_id: str | None, now: datetime) -> str:
        try:
            receipt = self.broker_evidence_reader(kind=kind, body=dict(body), claim_id=claim_id, now=now)
        except Exception as exc:
            raise PaperDenied("INDEPENDENT_BROKER_EVIDENCE_UNAVAILABLE") from exc
        # The reader verifies its own signed transport before returning this
        # receipt; the coordinator separately checks stored facts and freshness.
        if (not isinstance(receipt, Mapping) or receipt.get("source") != "bound_broker_reader_evidence_v2"
                or receipt.get("status") != "EVIDENCE_RECORDED"
                or not isinstance(receipt.get("evidence_id"), str)):
            raise PaperDenied("INDEPENDENT_BROKER_EVIDENCE_NOT_ACCEPTED")
        return receipt["evidence_id"]

    @staticmethod
    def _head(ledger: PaperLedger) -> dict[str, Any]:
        ledger.verify_chain()
        if not ledger.events:
            raise PaperDenied("ACCOUNT_COORDINATOR_UNINITIALIZED_LEDGER")
        return {"ledger_root_hash": ledger.root_hash, "ledger_sequence": len(ledger.events)}

    @property
    def supports_linked_protection(self) -> bool:
        return all(callable(getattr(self.client, name, None)) for name in
                   ("claim_linked_exit_v3", "complete_linked_pair_v3"))

    def _native_evidence(self, *, kind: str, body: Mapping, claim_id: str, now: datetime) -> Mapping:
        try:
            receipt = self.broker_evidence_reader(kind=kind, body=dict(body), claim_id=claim_id, now=now)
        except Exception as exc:
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_UNAVAILABLE") from exc
        if (not isinstance(receipt, Mapping) or receipt.get("source") != "bound_broker_reader_evidence_v3"
                or receipt.get("status") != "EVIDENCE_READ"
                or receipt.get("account_id") != self.client.account_id
                or receipt.get("robot_id") != self.client.robot_id or receipt.get("environment") != SIMNOW_FIRST
                or receipt.get("kind") != kind
                or not isinstance(receipt.get("evidence_id"), str)
                or not isinstance(receipt.get("facts"), Mapping)):
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_NOT_ACCEPTED")
        # Transport inclusion and canonical hashes are verified by the separate
        # reader delivery adapter. The SQL admission independently uses stored
        # evidence, never these runtime-supplied facts.
        facts = receipt["facts"]
        try:
            validate_native_facts(facts, kind)
        except ReceiptDenied as exc:
            raise PaperDenied("NATIVE_RECOVERY_FACTS_INVALID") from exc
        if object_hash(dict(facts)) != receipt.get("facts_sha256"):
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_HASH_MISMATCH")
        if (facts.get("claim_id") != claim_id or facts.get("command_id") != body.get("command_id")
                or facts.get("instrument") != body.get("contract")
                or facts.get("action") != body.get("action")):
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_SCOPE_MISMATCH")
        try:
            observed = datetime.fromisoformat(str(receipt["observed_at"]).replace("Z", "+00:00"))
            received = datetime.fromisoformat(str(receipt["received_at"]).replace("Z", "+00:00"))
            verified = datetime.fromisoformat(str(receipt["verified_at"]).replace("Z", "+00:00"))
        except (KeyError, ValueError) as exc:
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_TIME_INVALID") from exc
        if (any(t.tzinfo is None for t in (observed, received, verified))
                or not observed <= received <= verified <= now
                or not 0 <= (now - observed).total_seconds() <= 30
                or (now - verified).total_seconds() > 15):
            raise PaperDenied("NATIVE_RECOVERY_EVIDENCE_STALE")
        return receipt

    def claim_linked_exit(self, body: Mapping, ledger: PaperLedger, now: datetime) -> Mapping:
        """One permanent child close under a still-locked filled parent.

        The signed-entry ledger is the narrow contingent authority. This never
        invents order mapping, frees the parent, or authorizes an additional lot.
        """
        if not self.supports_linked_protection:
            raise PaperDenied("LINKED_PROTECTIVE_PROTOCOL_UNAVAILABLE")
        state = self._state()
        parent_id = state.get("pending_claim_id")
        if (not parent_id or state.get("command_id") != body.get("origin_command_id")
                or state.get("phase") not in {"SUBMIT_ATTEMPTED", "FROZEN"}
                or body.get("action") != "CLOSE_LONG"):
            raise PaperDenied("LINKED_PROTECTIVE_PARENT_MISMATCH")
        parents = [e for e in ledger.events if e["kind"] == "ActionAdmitted"
                   and e["command_id"] == body["origin_command_id"]]
        if len(parents) != 1:
            raise PaperDenied("LINKED_PROTECTIVE_AUTHORITY_MISSING")
        original = parents[0]["data"].get("body", {})
        if (original.get("action") != "OPEN_LONG" or original.get("contract") != body.get("contract")
                or original.get("action_contract_id") != body.get("origin_action_contract_id")
                or original.get("account_id") != self.client.account_id
                or original.get("quantity") != 1 or not original.get("stop_price")):
            raise PaperDenied("LINKED_PROTECTIVE_AUTHORITY_MISMATCH")
        native = self._native_evidence(kind="NATIVE_ORDER", body=original, claim_id=parent_id, now=now)
        facts = native["facts"]
        if (facts.get("order_id") != body.get("origin_order_id") or facts.get("order_status") != "FILLED"
                or facts.get("filled_quantity") != 1 or facts.get("position_quantity") != 1
                or facts.get("pending_order_count") != 0):
            raise PaperDenied("LINKED_PROTECTIVE_PARENT_NOT_EXACTLY_FILLED")
        ledger.append("LinkedExitClaimRequested", body["command_id"], now.isoformat(), {
            "source_sha256": self.client.source_sha256, "contract_hash": body["contract_hash"],
            "parent_claim_id": parent_id, "origin_command_id": body["origin_command_id"],
            "origin_order_id": body["origin_order_id"], "origin_action_contract_id": body["origin_action_contract_id"],
            "instrument": body["contract"], "action": "CLOSE_LONG", "reason": body["reason"],
            "broker_evidence_id": native["evidence_id"]})
        self.persist(ledger)
        try:
            result = self.client.claim_linked_exit_v3(command_id=body["command_id"],
                contract_hash=body["contract_hash"], parent_claim_id=parent_id,
                broker_evidence_id=native["evidence_id"], expected_version=state["version"], **self._head(ledger))
        except Exception as exc:
            raise PaperDenied("LINKED_PROTECTIVE_CLAIM_UNCERTAIN_NO_SUBMIT") from exc
        if (result.get("claimed") is not True or result.get("command_id") != body["command_id"]
                or result.get("position_origin_claim_id") != parent_id):
            raise PaperDenied("LINKED_PROTECTIVE_CLAIM_NOT_FRESH")
        return result

    def recover_uncertain_submission(self, ledger: PaperLedger, now: datetime) -> Mapping:
        """Read-only order discovery: exact native mapping, never a resubmit.

        A missing order, ambiguous record or lost service remains locked. A
        recovered ID only allows native terminal observation, not a new order.
        """
        state = self._state()
        command_id = state.get("command_id")
        claim_id = state.get("pending_claim_id")
        attempts = [e for e in ledger.events if e["kind"] == "OrderSubmitAttempted"
                    and e["command_id"] == command_id]
        submitted = [e for e in ledger.events if e["kind"] == "OrderSubmitted" and e["command_id"] == command_id]
        if len(attempts) != 1 or submitted or not claim_id:
            raise PaperDenied("UNCERTAIN_SUBMISSION_RECOVERY_SCOPE_MISMATCH")
        actions = [e for e in ledger.events if e["kind"] == "ActionAdmitted" and e["command_id"] == command_id]
        if len(actions) != 1 or state.get("phase") not in {"SUBMIT_ATTEMPTED", "FROZEN"}:
            raise PaperDenied("UNCERTAIN_SUBMISSION_RECOVERY_SCOPE_MISMATCH")
        body = {**actions[0]["data"]["body"], "command_id": command_id}
        native = self._native_evidence(kind="NATIVE_ORDER", body=body, claim_id=claim_id, now=now)
        facts = native["facts"]
        if not facts.get("order_id") or facts.get("order_status") not in {"PENDING", "FILLED", "REJECTED", "CANCELED"}:
            return {"status": "UNCERTAIN_ORDER_REQUIRES_NATIVE_MAPPING", "command_id": command_id}
        if getattr(self.client, "write_frozen", False):
            return {"status": "UNCERTAIN_ORDER_ID_OBSERVED_CLIENT_WRITE_FROZEN",
                    "command_id": command_id, "order_id": facts["order_id"],
                    "requires": "NEW_PROCESS_EXACT_EXTERNAL_LEDGER_AND_ACCOUNT_READBACK"}
        ledger.append("OrderSubmitted", command_id, now.isoformat(), {"order_id": facts["order_id"],
            "recovered_readonly": True, "claim_id": claim_id, "broker_evidence_id": native["evidence_id"],
            "order_binding_sha256": facts["order_binding_sha256"]})
        self.persist(ledger)
        return {"status": "UNCERTAIN_ORDER_ID_RECOVERED_READONLY", "command_id": command_id,
                "order_id": facts["order_id"]}

    def complete_linked_pair(self, body: Mapping, ledger: PaperLedger, now: datetime) -> Mapping:
        state = self._state()
        child = state.get("pending_claim_id")
        if state.get("command_id") != body.get("command_id") or not child:
            raise PaperDenied("LINKED_PAIR_SCOPE_MISMATCH")
        proof = self._native_evidence(kind="PAIRED_TERMINAL", body=body, claim_id=child, now=now)
        facts = proof["facts"]
        if (facts.get("order_status") != "FILLED" or facts.get("position_quantity") != 0
                or facts.get("parent_claim_id") != state.get("position_origin_claim_id")):
            raise PaperDenied("LINKED_PAIR_NOT_FLAT_AND_MATCHED")
        ledger.append("LinkedPairReconciled", body["command_id"], now.isoformat(), {
            "source_sha256": self.client.source_sha256, "claim_id": child,
            "parent_claim_id": facts["parent_claim_id"], "broker_evidence_id": proof["evidence_id"]})
        self.persist(ledger)
        try:
            result = self.client.complete_linked_pair_v3(claim_id=child, broker_evidence_id=proof["evidence_id"],
                expected_version=state["version"], **self._head(ledger))
        except Exception as exc:
            raise PaperDenied("LINKED_PAIR_COMPLETION_UNCERTAIN_READBACK_ONLY") from exc
        if (result.get("phase") != "FROZEN" or result.get("pending_claim_id") is not None
                or type(result.get("position_quantity")) is not int or result["position_quantity"] != 0
                or result.get("position_origin_claim_id") is not None
                or result.get("freeze_reason") != "LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED"):
            raise PaperDenied("LINKED_PAIR_NOT_FROZEN_FLAT")
        # Reconciled is allowed only after the paired remote receipt. Keep the
        # incident freeze; a fresh grant/operator flag cannot reopen this book.
        for command_id in (body["origin_command_id"], body["command_id"]):
            ledger.append("OrderFilledReconciled", command_id, now.isoformat(),
                          {"paired_evidence_id": proof["evidence_id"], "account_remains_frozen": True})
        self.persist(ledger)
        return result

    def claim(self, body: Mapping[str, Any], ledger: PaperLedger, now: datetime) -> Mapping[str, Any]:
        self._head(ledger)
        state = self._state()
        if state.get("pending_claim_id") is not None or state.get("phase") == "FROZEN":
            raise PaperDenied("ACCOUNT_COORDINATOR_PENDING_OR_FROZEN")
        evidence_id = self._evidence(kind="PRE_CLAIM", body=body, claim_id=None, now=now)
        origin = state.get("position_origin_claim_id") if body["action"] == "CLOSE_LONG" else None
        ledger.append("OrderClaimRequested", body["command_id"], now.isoformat(), {
            "source_sha256": self.client.source_sha256, "contract_hash": body["contract_hash"],
            "action": body["action"], "instrument": body["contract"],
            "position_origin_claim_id": origin, "broker_evidence_id": evidence_id})
        self.persist(ledger)
        try:
            receipt = self.client.claim_order_v2(command_id=body["command_id"], contract_hash=body["contract_hash"],
                action=body["action"], instrument=body["contract"],
                position_origin_claim_id=origin,
                broker_evidence_id=evidence_id, expected_version=state["version"], **self._head(ledger))
        except Exception as exc:
            raise PaperDenied("ACCOUNT_COORDINATOR_CLAIM_UNCERTAIN_NO_SUBMIT") from exc
        if receipt.get("claimed") is not True or receipt.get("command_id") != body["command_id"]:
            raise PaperDenied("ACCOUNT_COORDINATOR_CLAIM_NOT_FRESH")
        return receipt

    def submission_data(self, command_id: str, data: Mapping) -> dict[str, Any]:
        state = self._state()
        if state.get("phase") != "CLAIMED" or state.get("command_id") != command_id or not state.get("pending_claim_id"):
            raise PaperDenied("ACCOUNT_COORDINATOR_SUBMIT_SCOPE_MISMATCH")
        return {**dict(data), "source_sha256": self.client.source_sha256, "claim_id": state["pending_claim_id"]}

    def prepare_submit(self, command_id: str, ledger: PaperLedger) -> Mapping[str, Any]:
        state = self._state()
        if state.get("phase") != "CLAIMED" or state.get("command_id") != command_id or not state.get("pending_claim_id"):
            raise PaperDenied("ACCOUNT_COORDINATOR_SUBMIT_SCOPE_MISMATCH")
        attempts = [e for e in ledger.events if e["command_id"] == command_id and e["kind"] == "OrderSubmitAttempted"]
        if len(attempts) != 1:
            raise PaperDenied("ACCOUNT_COORDINATOR_SUBMIT_LEDGER_MISMATCH")
        try:
            receipt = self.client.record_submit_attempt_v2(claim_id=state["pending_claim_id"],
                expected_version=state["version"], **self._head(ledger))
        except Exception as exc:
            raise PaperDenied("ACCOUNT_COORDINATOR_SUBMIT_RECEIPT_UNCERTAIN_NO_SUBMIT") from exc
        if receipt.get("phase") != "SUBMIT_ATTEMPTED" or receipt.get("command_id") != command_id:
            raise PaperDenied("ACCOUNT_COORDINATOR_SUBMIT_RECEIPT_MISMATCH")
        return receipt

    def terminal(self, body: Mapping[str, Any], ledger: PaperLedger, now: datetime) -> Mapping[str, Any]:
        state = self._state()
        if state.get("command_id") != body["command_id"] or not state.get("pending_claim_id"):
            raise PaperDenied("ACCOUNT_COORDINATOR_TERMINAL_SCOPE_MISMATCH")
        receipt_id = self._evidence(kind="TERMINAL", body=body, claim_id=state["pending_claim_id"], now=now)
        ledger.append("OrderTerminalReconciled", body["command_id"], now.isoformat(), {
            "source_sha256": self.client.source_sha256, "claim_id": state["pending_claim_id"],
            "broker_evidence_id": receipt_id})
        self.persist(ledger)
        try:
            result = self.client.record_terminal_v2(claim_id=state["pending_claim_id"],
                broker_evidence_id=receipt_id, expected_version=state["version"], **self._head(ledger))
        except Exception as exc:
            raise PaperDenied("ACCOUNT_COORDINATOR_TERMINAL_UNCERTAIN_READBACK_ONLY") from exc
        if result.get("pending_claim_id") is not None or result.get("phase") not in {"FLAT", "HELD"}:
            raise PaperDenied("ACCOUNT_COORDINATOR_TERMINAL_NOT_RELEASED")
        return result

    def verify_restart(self, ledger: PaperLedger, *, require_idle: bool = True) -> Mapping[str, Any]:
        """Read only: mismatched local/external evidence is never rewritten here."""
        try:
            external = self.client.read_ledger(expected_root_hash=ledger.root_hash,
                expected_sequence=len(ledger.events))
        except Exception as exc:
            raise PaperDenied("RESTART_EXTERNAL_LEDGER_MISMATCH_OR_UNAVAILABLE") from exc
        state = self._state()
        pending = state.get("pending_claim_id") is not None or state.get("phase") == "FROZEN"
        if pending and require_idle:
            raise PaperDenied("RESTART_PENDING_REQUIRES_READONLY_RECOVERY")
        return {"status": "RESTART_VERIFIED_READONLY_RECOVERY" if pending else "RESTART_VERIFIED_NO_PENDING",
                "external_ledger": external, "account_state": state}
