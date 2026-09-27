"""Bounded private receipt transport; no broker calls or implicit write retries.

The fixed TLS endpoint supplies independent receipt time. HMAC authenticates
requests, not response bodies: responses are trusted only over verified TLS and
must still pass identity, inclusion hash and timestamp checks. Ambiguous writes
freeze this client instance; recovering processes must additionally consult the
durable account coordinator. V1 order claims are deliberately unavailable.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import stat
import time
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

ENDPOINT = "https://tbmoimbdhsrltvospwpu.supabase.co/functions/v1/gold2-paper-control"
HOST = "tbmoimbdhsrltvospwpu.supabase.co"
REQUEST_PATH = "/functions/v1/gold2-paper-control"
MAX_BYTES = 2_100_000
ENVIRONMENT = "SIMNOW_FIRST_NORMAL"
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SIGNAL_FIELDS = ("decision_at", "forward_decision_id", "forward_decision_sha256",
                 "frozen_dataset_sha256", "outcome_contracts", "parameters_sha256",
                 "record_id", "recorded_at", "registry_id", "signal_id", "signal_sha256", "source_ref")

NATIVE_HASH_FIELDS = {"order_binding_sha256", "raw_identity_sha256", "raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"}
NATIVE_FACT_FIELDS = {"command_id", "claim_id", "instrument", "action", "order_id", "order_status", "filled_quantity", "position_quantity", "pending_order_count", "parent_claim_id", "parent_order_id", "reconciliation"} | NATIVE_HASH_FIELDS
PAIR_FIELDS = {"producer_id", "proof_sha256", "cash_cents", "available_cents", "frozen_margin_cents", "position_quantity", "open_filled_quantity", "close_filled_quantity", "parent_order_id", "child_order_id"}


class ReceiptDenied(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class ReceiptWriteAmbiguous(ReceiptDenied):
    """Do not resubmit: use separate readback and retain durable freeze."""


def canonical_bytes(value: Any) -> bytes:
    def validate(item: Any, depth: int = 0) -> None:
        if depth > 64:
            raise ReceiptDenied("JSON_TOO_DEEP")
        if item is None or isinstance(item, bool):
            return
        if isinstance(item, str):
            try:
                item.encode("utf-8", "strict")
            except UnicodeError:
                raise ReceiptDenied("INVALID_UNICODE") from None
            return
        if type(item) is int and abs(item) <= 9_007_199_254_740_991:
            return
        if isinstance(item, list):
            for child in item:
                validate(child, depth + 1)
            return
        if isinstance(item, dict) and all(isinstance(k, str) for k in item):
            for key, child in item.items():
                validate(key, depth + 1)
                validate(child, depth + 1)
            return
        raise ReceiptDenied("UNSUPPORTED_OR_NON_INTEGER_JSON")
    validate(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def object_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _instant(value: Any) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None or result.utcoffset() is None:
            raise ValueError
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise ReceiptDenied("AWARE_TIMESTAMP_REQUIRED") from None


def _id(value: Any) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ReceiptDenied("IDENTITY_REQUIRED")
    return value


def _sha(value: Any) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ReceiptDenied("SHA256_REQUIRED")
    return value


def _safe_private_key(path: Path) -> bytes:
    if not path.is_absolute():
        raise ReceiptDenied("ABSOLUTE_PRIVATE_KEY_PATH_REQUIRED")
    descriptor = None
    try:
        parent_info = path.parent.stat()
        source_root = Path(__file__).resolve().parents[2]
        if (path.parent.is_symlink() or not stat.S_ISDIR(parent_info.st_mode)
                or parent_info.st_uid != os.getuid() or stat.S_IMODE(parent_info.st_mode) != 0o700
                or path.resolve().is_relative_to(source_root)):
            raise ReceiptDenied("PRIVATE_KEY_DIRECTORY_OR_SOURCE_POLICY_DENIED")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1
                or not 32 <= info.st_size <= 4096):
            raise ReceiptDenied("PRIVATE_KEY_FILE_POLICY_DENIED")
        raw = os.read(descriptor, 4097)
        if len(raw) != info.st_size or b"\n" in raw or b"\r" in raw:
            raise ReceiptDenied("PRIVATE_KEY_BYTES_DENIED")
        raw.decode("utf-8", "strict")
        return raw
    except (OSError, UnicodeError):
        raise ReceiptDenied("PRIVATE_KEY_FILE_UNAVAILABLE") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _json_object(raw: bytes) -> dict[str, Any]:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReceiptDenied("DUPLICATE_REPLY_KEYS")
            result[key] = value
        return result
    try:
        result = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(ReceiptDenied("NONFINITE_REPLY")))
        if not isinstance(result, dict):
            raise ReceiptDenied("REPLY_OBJECT_REQUIRED")
        canonical_bytes(result)
        return result
    except (ValueError, UnicodeError, TypeError, RecursionError):
        raise ReceiptDenied("INVALID_REPLY_JSON") from None


def tls_transport(url: str, headers: Mapping[str, str], body: bytes, timeout: float,
                  max_bytes: int) -> tuple[int, bytes]:
    """One POST to the fixed verified HTTPS origin; redirects never followed."""
    if url != ENDPOINT:
        raise ReceiptDenied("FIXED_TLS_ENDPOINT_REQUIRED")
    connection = http.client.HTTPSConnection(HOST, timeout=timeout, context=ssl.create_default_context())
    deadline = time.monotonic() + timeout
    try:
        connection.request("POST", REQUEST_PATH, body, dict(headers))
        response = connection.getresponse()
        declared = response.getheader("Content-Length")
        if declared is not None and (not declared.isdigit() or int(declared) > max_bytes):
            raise ReceiptDenied("REPLY_TOO_LARGE")
        chunks, length = [], 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            if connection.sock is not None:
                connection.sock.settimeout(remaining)
            chunk = response.read1(min(65536, max_bytes - length + 1))
            if not chunk:
                break
            chunks.append(chunk)
            length += len(chunk)
            if length > max_bytes:
                raise ReceiptDenied("REPLY_TOO_LARGE")
        if time.monotonic() > deadline:
            raise TimeoutError
        return response.status, b"".join(chunks)
    finally:
        connection.close()


class ReceiptClient:
    def __init__(self, *, role: str, key_file: Path,
                 account_id: str | None = None, robot_id: int | None = None,
                 source_sha256: str | None = None, timeout_seconds: int = 10,
                 transport: Callable = tls_transport,
                 clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        if role not in {"signal", "runtime", "broker_reader"}:
            raise ReceiptDenied("ROLE_DENIED")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 15:
            raise ReceiptDenied("BOUNDED_TIMEOUT_REQUIRED")
        if role != "signal":
            _id(account_id)
            if type(robot_id) is not int or not 0 < robot_id <= 9_007_199_254_740_991:
                raise ReceiptDenied("ROBOT_ID_REQUIRED")
            _sha(source_sha256)
        self.role, self.account_id, self.robot_id, self.source_sha256 = role, account_id, robot_id, source_sha256
        self.timeout_seconds, self._transport, self._clock = timeout_seconds, transport, clock
        self._key = _safe_private_key(Path(key_file))
        self.write_frozen = False
        self._last_http_status = None

    @classmethod
    def from_config_file(cls, path: Path, *, transport: Callable = tls_transport,
                         clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        descriptor = None
        try:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_size > 16384:
                raise ReceiptDenied("CONFIG_FILE_DENIED")
            config = _json_object(os.read(descriptor, 16385))
        except OSError:
            raise ReceiptDenied("CONFIG_FILE_UNAVAILABLE") from None
        finally:
            if descriptor is not None:
                os.close(descriptor)
        if config.get("endpoint") != ENDPOINT or config.get("enabled") is not True:
            raise ReceiptDenied("CLIENT_DISABLED_OR_ENDPOINT_DENIED")
        if set(config) != {"endpoint", "enabled", "role", "key_file", "account_id", "robot_id", "source_sha256", "timeout_seconds"}:
            raise ReceiptDenied("CONFIG_SHAPE_DENIED")
        return cls(role=config["role"], key_file=Path(config["key_file"]), account_id=config["account_id"],
                   robot_id=config["robot_id"], source_sha256=config["source_sha256"],
                   timeout_seconds=config["timeout_seconds"], transport=transport, clock=clock)

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ReceiptDenied("AWARE_CLOCK_REQUIRED")
        return value.astimezone(timezone.utc)

    def _call(self, request: dict[str, Any], *, write: bool) -> dict[str, Any]:
        if write and self.write_frozen:
            raise ReceiptWriteAmbiguous("WRITES_FROZEN_READBACK_REQUIRED")
        raw = canonical_bytes(request)
        if len(raw) > MAX_BYTES:
            raise ReceiptDenied("REQUEST_TOO_LARGE")
        started = self._now()
        timestamp = started.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        material = "GOLD2-PAPER-V1\nPOST\n" + REQUEST_PATH + "\n" + timestamp + "\n" + hashlib.sha256(raw).hexdigest()
        headers = {"Content-Type": "application/json", "Content-Length": str(len(raw)),
                   "X-Gold2-Role": self.role, "X-Gold2-Timestamp": timestamp,
                   "X-Gold2-Signature": "sha256=" + hmac.new(self._key, material.encode(), hashlib.sha256).hexdigest()}
        try:
            status, response = self._transport(ENDPOINT, headers, raw, self.timeout_seconds, MAX_BYTES)
            self._last_http_status = status
            ended = self._now()
            if ended < started or (ended - started).total_seconds() > 30:
                raise ReceiptDenied("STALE_TRANSPORT_REPLY")
            if not isinstance(response, bytes) or len(response) > MAX_BYTES:
                raise ReceiptDenied("REPLY_TOO_LARGE")
            parsed = _json_object(response)
            if status not in {200, 409}:
                if not write:
                    raise ReceiptDenied("REMOTE_READ_UNAVAILABLE")
                # Even a 4xx response may be malformed/proxied. Never infer that
                # a write did not commit from an HTTP status alone.
                raise ReceiptWriteAmbiguous("WRITE_RESULT_UNKNOWN_READBACK_REQUIRED")
            return parsed
        except Exception:
            if write:
                self.write_frozen = True
                raise ReceiptWriteAmbiguous("WRITE_RESULT_UNKNOWN_READBACK_REQUIRED") from None
            raise ReceiptDenied("REMOTE_READ_NOT_VERIFIED") from None

    def _verified(self, validator: Callable, *, write: bool):
        try:
            return validator()
        except ReceiptWriteAmbiguous:
            raise
        except Exception:
            if write:
                self.write_frozen = True
                raise ReceiptWriteAmbiguous("WRITE_READBACK_INVALID_NO_RETRY") from None
            raise ReceiptDenied("READBACK_INVALID") from None

    def _scope(self, role: str) -> None:
        if self.role != role:
            raise ReceiptDenied("OPERATION_SCOPE_DENIED")

    def _proof(self, proof: dict, *, registry_id: str, record_id: str,
               record_sha256: str, registry_root_sha256: str, recorded_at: str | None = None,
               decision_at: str | None = None) -> dict:
        keys = {"status", "verifier_identity", "registry_id", "record_id", "record_sha256",
                "registry_root_sha256", "recorded_at", "anchor_received_at", "proof_sha256", "verified_at"}
        if (set(proof) != keys or proof.get("status") != "VERIFIED_EXTERNAL_TIME_AND_INCLUSION"
                or proof.get("verifier_identity") != "GOLD2_PAPER_SUPABASE_EDGE_V1"
                or proof.get("registry_id") != registry_id or proof.get("record_id") != record_id
                or proof.get("record_sha256") != record_sha256
                or proof.get("registry_root_sha256") != registry_root_sha256):
            raise ReceiptDenied("SIGNAL_PROOF_IDENTITY_MISMATCH")
        material = {key: value for key, value in proof.items() if key not in {"proof_sha256", "verified_at"}}
        if not hmac.compare_digest(object_hash(material), _sha(proof.get("proof_sha256"))):
            raise ReceiptDenied("SIGNAL_PROOF_HASH_MISMATCH")
        recorded, received, verified = map(_instant, (proof["recorded_at"], proof["anchor_received_at"], proof["verified_at"]))
        now = self._now()
        if not recorded <= received <= verified <= now or (now - verified).total_seconds() > 15:
            raise ReceiptDenied("SIGNAL_PROOF_TIME_INVALID")
        if recorded_at is not None and recorded != _instant(recorded_at):
            raise ReceiptDenied("SIGNAL_PROOF_RECORD_TIME_MISMATCH")
        local, decision = received.astimezone(ZoneInfo("Asia/Shanghai")), _instant(decision_at or proof["recorded_at"])
        if local.date() != decision.astimezone(ZoneInfo("Asia/Shanghai")).date() or (local.hour, local.minute) != (8, 30) or received < decision:
            raise ReceiptDenied("SIGNAL_PROOF_OUTSIDE_DECISION_MINUTE")
        return proof

    def anchor_signal(self, record: Mapping[str, Any], registry_root_sha256: str) -> dict:
        self._scope("signal")
        value = dict(record)
        if set(value) != set(SIGNAL_FIELDS):
            raise ReceiptDenied("SIGNAL_RECORD_SHAPE")
        _id(value["registry_id"]); _id(value["record_id"])
        _instant(value["recorded_at"]); _instant(value["decision_at"])
        digest, root = object_hash(value), _sha(registry_root_sha256)
        reply = self._call({"op": "anchor_signal", "record": value, "record_sha256": digest,
                            "registry_root_sha256": root}, write=True)
        return self._verified(lambda: self._proof(reply, registry_id=value["registry_id"], record_id=value["record_id"],
            record_sha256=digest, registry_root_sha256=root, recorded_at=value["recorded_at"], decision_at=value["decision_at"]), write=True)

    def read_signal(self, registry_id: str, record_id: str, *, expected_record_sha256: str,
                    expected_registry_root_sha256: str, expected_record: Mapping[str, Any] | None = None) -> dict:
        self._scope("signal")
        _id(registry_id); _id(record_id); _sha(expected_record_sha256); _sha(expected_registry_root_sha256)
        if expected_record is not None and (object_hash(dict(expected_record)) != expected_record_sha256
                or expected_record.get("registry_id") != registry_id or expected_record.get("record_id") != record_id):
            raise ReceiptDenied("LOCAL_RECORD_HASH_MISMATCH")
        reply = self._call({"op": "read_signal", "registry_id": registry_id, "record_id": record_id}, write=False)
        return self._verified(lambda: self._proof(reply, registry_id=registry_id, record_id=record_id,
            record_sha256=expected_record_sha256, registry_root_sha256=expected_registry_root_sha256,
            recorded_at=expected_record.get("recorded_at") if expected_record else None,
            decision_at=expected_record.get("decision_at") if expected_record else None), write=False)

    def anchor_verifier(self, candidate: Mapping[str, Any]) -> dict:
        record = {key: candidate[key] for key in SIGNAL_FIELDS}
        return self.read_signal(candidate["registry_id"], candidate["record_id"],
                                expected_record_sha256=candidate["raw_sha256"],
                                expected_registry_root_sha256=candidate["registry_root_sha256"], expected_record=record)

    def _ledger_reply(self, reply: dict, *, root: str | None = None, sequence: int | None = None, write=False) -> dict:
        required = {"account_id", "robot_id", "root_hash", "last_sequence", "anchor_received_at"}
        if not required.issubset(reply) or reply.get("account_id") != self.account_id or reply.get("robot_id") != self.robot_id:
            raise ReceiptDenied("LEDGER_IDENTITY_MISMATCH")
        _sha(reply.get("root_hash"))
        if type(reply.get("last_sequence")) is not int or reply["last_sequence"] < 1:
            raise ReceiptDenied("LEDGER_SEQUENCE_INVALID")
        if root is not None and reply["root_hash"] != root or sequence is not None and reply["last_sequence"] != sequence:
            raise ReceiptDenied("LEDGER_HEAD_MISMATCH")
        if _instant(reply["anchor_received_at"]) > self._now():
            raise ReceiptDenied("LEDGER_RECEIVED_IN_FUTURE")
        if write and (reply.get("source") != "external_append_only_ledger" or reply.get("accepted") is not True):
            raise ReceiptDenied("LEDGER_ACCEPTANCE_INVALID")
        if not write and reply.get("environment") != ENVIRONMENT:
            raise ReceiptDenied("LEDGER_ENVIRONMENT_MISMATCH")
        return reply

    def append_ledger(self, events: list[dict], root_hash: str) -> dict:
        self._scope("runtime")
        _sha(root_hash)
        if not isinstance(events, list) or not 1 <= len(events) <= 10000:
            raise ReceiptDenied("LEDGER_LENGTH_DENIED")
        previous = "0" * 64
        for index, event in enumerate(events):
            if (set(event) != {"at", "command_id", "data", "event_hash", "kind", "previous_hash", "sequence"}
                    or type(event.get("sequence")) is not int or event.get("sequence") != index + 1
                    or event.get("previous_hash") != previous):
                raise ReceiptDenied("LEDGER_CHAIN_INVALID")
            _id(event["command_id"]); _instant(event["at"])
            if not isinstance(event["data"], dict) or not isinstance(event["kind"], str) or not re.fullmatch(r"[A-Z][A-Za-z]+", event["kind"]):
                raise ReceiptDenied("LEDGER_EVENT_INVALID")
            if object_hash({k: v for k, v in event.items() if k != "event_hash"}) != event["event_hash"]:
                raise ReceiptDenied("LEDGER_EVENT_HASH_MISMATCH")
            previous = event["event_hash"]
        if previous != root_hash:
            raise ReceiptDenied("LEDGER_ROOT_MISMATCH")
        reply = self._call({"op": "append_ledger", "account_id": self.account_id, "robot_id": self.robot_id,
                            "events": events, "root_hash": root_hash}, write=True)
        return self._verified(lambda: self._ledger_reply(reply, root=root_hash, sequence=len(events), write=True), write=True)

    def read_ledger(self, *, expected_root_hash: str | None = None, expected_sequence: int | None = None) -> dict:
        self._scope("runtime")
        reply = self._call({"op": "read_ledger", "account_id": self.account_id, "robot_id": self.robot_id}, write=False)
        return self._verified(lambda: self._ledger_reply(reply, root=expected_root_hash, sequence=expected_sequence), write=False)

    def claim_order(self, *args, **kwargs):
        raise ReceiptDenied("V1_CLAIM_DISABLED_USE_ACCOUNT_COORDINATOR_V2")

    def _coordinator(self, operation: str, *, write: bool, **fields) -> dict:
        self._scope("runtime")
        reserved = {"op", "environment", "account_id", "robot_id", "source_sha256"}
        if reserved.intersection(fields):
            raise ReceiptDenied("CONFIG_IDENTITY_OVERRIDE_DENIED")
        request = {"op": operation, "environment": ENVIRONMENT, "account_id": self.account_id,
                   "robot_id": self.robot_id, "source_sha256": self.source_sha256, **fields}
        canonical_bytes(request)
        reply = self._call(request, write=write)
        return self._verified(lambda: self._coordinator_reply(reply, request), write=write)

    def _coordinator_reply(self, reply: dict, request: dict) -> dict:
        if reply.get("source") != "external_account_coordinator_v2" or any(reply.get(k) != request[k]
                for k in ("account_id", "robot_id", "environment", "source_sha256")):
            raise ReceiptDenied("COORDINATOR_IDENTITY_MISMATCH")
        if (type(reply.get("version")) is not int or reply["version"] < 0
                or reply.get("phase") not in {"FLAT", "CLAIMED", "SUBMIT_ATTEMPTED", "HELD", "FROZEN"}
                or type(reply.get("claimed")) is not bool or reply.get("position_quantity") not in {0, 1}
                or type(reply.get("position_quantity")) is not int):
            raise ReceiptDenied("COORDINATOR_STATE_INVALID")
        if not (reply.get("ledger_root_hash") == "0" * 64 and reply.get("ledger_sequence") == 0):
            _sha(reply.get("ledger_root_hash"))
        if type(reply.get("ledger_sequence")) is not int or reply["ledger_sequence"] < 0:
            raise ReceiptDenied("COORDINATOR_LEDGER_INVALID")
        if reply["ledger_sequence"] == 0 and reply.get("ledger_root_hash") != "0" * 64:
            raise ReceiptDenied("COORDINATOR_EMPTY_HEAD_INVALID")
        if _instant(reply.get("updated_at")) > self._now():
            raise ReceiptDenied("COORDINATOR_FUTURE_STATE")
        for key in ("claim_id", "command_id", "pending_claim_id", "position_origin_claim_id"):
            if reply.get(key) is not None:
                _id(reply[key])
        if (reply["phase"] == "FLAT" and (reply["position_quantity"] != 0 or reply.get("pending_claim_id") is not None
                                         or reply.get("position_origin_claim_id") is not None)
                or reply["phase"] == "HELD" and (reply["position_quantity"] != 1 or reply.get("pending_claim_id") is not None
                                                or reply.get("position_origin_claim_id") is None)
                or reply["phase"] in {"CLAIMED", "SUBMIT_ATTEMPTED"} and reply.get("pending_claim_id") is None):
            raise ReceiptDenied("COORDINATOR_PHASE_QUANTITY_INCONSISTENT")
        statuses = {"ACCOUNT_READ", "CLAIM_READ", "CLAIMED", "SUBMIT_RECORDED", "TERMINAL_RECORDED", "FROZEN",
                    "ALREADY_CLAIMED", "CONFLICT", "LEGACY_COMMAND_CONSUMED", "VERSION_CONFLICT", "ACCOUNT_BUSY",
                    "ACCOUNT_FROZEN", "OPEN_POSITION_DENIED", "CLOSE_ORIGIN_DENIED", "CLOSE_INSTRUMENT_DENIED",
                    "SUBMIT_STATE_DENIED", "TERMINAL_STATE_DENIED", "FREEZE_CLAIM_DENIED", "CLAIM_NOT_FOUND",
                    "PAIR_RECORDED", "LINKED_EXIT_DENIED", "LINKED_EXIT_CONSUMED", "PAIR_STATE_DENIED"}
        if reply.get("status") not in statuses:
            raise ReceiptDenied("COORDINATOR_STATUS_INVALID")
        success = {"read_account_state_v2": "ACCOUNT_READ", "read_claim_v2": "CLAIM_READ",
                   "claim_order_v2": "CLAIMED", "record_submit_attempt_v2": "SUBMIT_RECORDED",
                   "record_terminal_v2": "TERMINAL_RECORDED", "freeze_account_v2": "FROZEN",
                   "claim_linked_exit_v3": "CLAIMED", "complete_linked_pair_v3": "PAIR_RECORDED"}[request["op"]]
        if reply["status"] == success:
            if self._last_http_status != 200:
                raise ReceiptDenied("COORDINATOR_SUCCESS_HTTP_MISMATCH")
            if request["op"] not in {"read_account_state_v2", "read_claim_v2"}:
                if (reply["version"] != request["expected_version"] + 1
                        or reply["ledger_root_hash"] != request["ledger_root_hash"]
                        or reply["ledger_sequence"] != request["ledger_sequence"]):
                    raise ReceiptDenied("MUTATION_RECEIPT_MISMATCH")
                if request["op"] not in {"claim_order_v2", "claim_linked_exit_v3"} and reply.get("claim_id") != request.get("claim_id"):
                    raise ReceiptDenied("MUTATION_CLAIM_MISMATCH")
            if request["op"] == "record_submit_attempt_v2" and reply["phase"] != "SUBMIT_ATTEMPTED":
                raise ReceiptDenied("SUBMIT_PHASE_MISMATCH")
            if request["op"] == "record_terminal_v2" and reply["phase"] not in {"FLAT", "HELD"}:
                raise ReceiptDenied("TERMINAL_PHASE_MISMATCH")
            if request["op"] == "claim_linked_exit_v3" and (reply["position_quantity"] != 1
                    or reply.get("position_origin_claim_id") != request["parent_claim_id"]
                    or reply.get("freeze_reason") != "LINKED_EXIT_PAIR_RECONCILIATION_REQUIRED"):
                raise ReceiptDenied("LINKED_FRESH_CLAIM_RELATION_MISMATCH")
            if request["op"] == "complete_linked_pair_v3" and (reply["phase"] != "FROZEN"
                    or reply["position_quantity"] != 0 or reply.get("pending_claim_id") is not None
                    or reply.get("position_origin_claim_id") is not None
                    or reply.get("freeze_reason") != "LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED"):
                raise ReceiptDenied("LINKED_PAIR_FLAT_FREEZE_MISMATCH")
            if request["op"] == "freeze_account_v2" and (reply["phase"] != "FROZEN" or reply.get("freeze_reason") != request["reason_code"]):
                raise ReceiptDenied("FREEZE_PHASE_MISMATCH")
        elif self._last_http_status != 409 or reply["claimed"] is not False:
            raise ReceiptDenied("COORDINATOR_FAILURE_HTTP_MISMATCH")
        if reply["claimed"] is True:
            if (request["op"] not in {"claim_order_v2", "claim_linked_exit_v3"} or reply.get("status") != "CLAIMED"
                    or reply.get("command_id") != request.get("command_id")
                    or reply.get("claim_id") is None or reply.get("pending_claim_id") != reply.get("claim_id")
                    or reply["phase"] != "CLAIMED" or reply["version"] != request["expected_version"] + 1
                    or reply["ledger_root_hash"] != request["ledger_root_hash"]
                    or reply["ledger_sequence"] != request["ledger_sequence"]):
                raise ReceiptDenied("FRESH_CLAIM_NOT_VERIFIED")
        if request["op"] == "read_claim_v2" and reply.get("command_id") != request["command_id"]:
            raise ReceiptDenied("CLAIM_COMMAND_MISMATCH")
        return reply

    def claim_linked_exit_v3(self, *, command_id: str, contract_hash: str, parent_claim_id: str,
                             broker_evidence_id: str, expected_version: int,
                             ledger_root_hash: str, ledger_sequence: int) -> dict:
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        _id(command_id); _sha(contract_hash); _id(parent_claim_id); _id(broker_evidence_id)
        return self._coordinator("claim_linked_exit_v3", write=True, command_id=command_id,
            contract_hash=contract_hash, parent_claim_id=parent_claim_id, broker_evidence_id=broker_evidence_id,
            expected_version=expected_version, ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    def complete_linked_pair_v3(self, *, claim_id: str, broker_evidence_id: str, expected_version: int,
                                ledger_root_hash: str, ledger_sequence: int) -> dict:
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        return self._coordinator("complete_linked_pair_v3", write=True, claim_id=_id(claim_id),
            broker_evidence_id=_id(broker_evidence_id), expected_version=expected_version,
            ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    def read_account_state_v2(self) -> dict:
        return self._coordinator("read_account_state_v2", write=False)

    def read_claim_v2(self, command_id: str) -> dict:
        return self._coordinator("read_claim_v2", write=False, command_id=_id(command_id))

    def claim_order_v2(self, *, command_id: str, contract_hash: str, action: str, instrument: str,
                       position_origin_claim_id: str | None, broker_evidence_id: str,
                       expected_version: int, ledger_root_hash: str, ledger_sequence: int) -> dict:
        _id(command_id); _sha(contract_hash); _id(broker_evidence_id)
        if (action not in {"OPEN_LONG", "CLOSE_LONG"} or not isinstance(instrument, str) or not re.fullmatch(r"au\d{4}", instrument)
                or (action == "OPEN_LONG" and position_origin_claim_id is not None)
                or (action == "CLOSE_LONG" and position_origin_claim_id is None)):
            raise ReceiptDenied("CLAIM_ACTION_DENIED")
        if position_origin_claim_id is not None:
            _id(position_origin_claim_id)
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        return self._coordinator("claim_order_v2", write=True, command_id=command_id, contract_hash=contract_hash,
            action=action, instrument=instrument, position_origin_claim_id=position_origin_claim_id,
            broker_evidence_id=broker_evidence_id, expected_version=expected_version,
            ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    @staticmethod
    def _mutation(expected_version, ledger_root_hash, ledger_sequence):
        _sha(ledger_root_hash)
        if type(expected_version) is not int or expected_version < 0 or type(ledger_sequence) is not int or ledger_sequence < 1:
            raise ReceiptDenied("MUTATION_VERSION_OR_SEQUENCE_INVALID")

    def record_submit_attempt_v2(self, *, claim_id: str, expected_version: int,
                                 ledger_root_hash: str, ledger_sequence: int) -> dict:
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        return self._coordinator("record_submit_attempt_v2", write=True, claim_id=_id(claim_id),
            expected_version=expected_version, ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    def record_terminal_v2(self, *, claim_id: str, broker_evidence_id: str, expected_version: int,
                          ledger_root_hash: str, ledger_sequence: int) -> dict:
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        return self._coordinator("record_terminal_v2", write=True, claim_id=_id(claim_id),
            broker_evidence_id=_id(broker_evidence_id), expected_version=expected_version,
            ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    def freeze_account_v2(self, *, claim_id: str | None, reason_code: str, expected_version: int,
                         ledger_root_hash: str, ledger_sequence: int) -> dict:
        self._mutation(expected_version, ledger_root_hash, ledger_sequence)
        if claim_id is not None:
            _id(claim_id)
        if not isinstance(reason_code, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}", reason_code):
            raise ReceiptDenied("FREEZE_REASON_INVALID")
        return self._coordinator("freeze_account_v2", write=True, claim_id=claim_id, reason_code=reason_code,
            expected_version=expected_version, ledger_root_hash=ledger_root_hash, ledger_sequence=ledger_sequence)

    def ingest_broker_evidence_v2(self, *, evidence_id: str, kind: str, observed_at: str,
                                  raw_sha256: str, facts: Mapping[str, Any]) -> dict:
        """Reader key is independent of runtime; only server validates facts."""
        self._scope("broker_reader")
        _id(evidence_id); _sha(raw_sha256)
        if kind not in {"PRE_CLAIM", "TERMINAL"} or not isinstance(facts, Mapping):
            raise ReceiptDenied("BROKER_EVIDENCE_SHAPE_DENIED")
        observed = _instant(observed_at)
        if not observed <= self._now() or (self._now() - observed).total_seconds() > 30:
            raise ReceiptDenied("BROKER_EVIDENCE_OBSERVATION_STALE")
        value = dict(facts)
        digest = object_hash(value)
        request = {"op": "ingest_broker_evidence_v2", "environment": ENVIRONMENT,
                   "account_id": self.account_id, "robot_id": self.robot_id, "source_sha256": self.source_sha256,
                   "evidence_id": evidence_id, "kind": kind, "observed_at": observed_at,
                   "raw_sha256": raw_sha256, "facts_sha256": digest, "facts": value}
        reply = self._call(request, write=True)
        def validate():
            if (self._last_http_status != 200 or reply.get("source") != "bound_broker_reader_evidence_v2"
                    or reply.get("status") != "EVIDENCE_RECORDED" or reply.get("evidence_id") != evidence_id
                    or reply.get("raw_sha256") != raw_sha256 or reply.get("facts_sha256") != digest):
                raise ReceiptDenied("BROKER_EVIDENCE_RECEIPT_MISMATCH")
            received = _instant(reply.get("received_at"))
            if not observed <= received <= self._now() or (self._now() - received).total_seconds() > 15:
                raise ReceiptDenied("BROKER_EVIDENCE_RECEIPT_TIME_INVALID")
            return reply
        return self._verified(validate, write=True)

    def read_broker_evidence_v2(self, evidence_id: str, *, expected_raw_sha256: str,
                                expected_facts_sha256: str) -> dict:
        """Verify immutable reader inclusion, including after ambiguous ingest.

        Historical observed_at is allowed for audit. This read does not unfreeze
        writes, refresh historical broker facts or authorize an order mutation.
        """
        self._scope("broker_reader")
        _id(evidence_id); _sha(expected_raw_sha256); _sha(expected_facts_sha256)
        reply = self._call({"op": "read_broker_evidence_v2", "environment": ENVIRONMENT,
                           "account_id": self.account_id, "robot_id": self.robot_id,
                           "source_sha256": self.source_sha256, "evidence_id": evidence_id}, write=False)
        def validate():
            keys = {"source", "status", "evidence_id", "environment", "account_id", "robot_id", "source_sha256",
                    "kind", "observed_at", "raw_sha256", "facts_sha256", "facts", "received_at", "verified_at"}
            if (set(reply) != keys or reply.get("source") != "bound_broker_reader_evidence_v2"
                    or reply.get("status") != "EVIDENCE_READ" or reply.get("evidence_id") != evidence_id
                    or reply.get("environment") != ENVIRONMENT or reply.get("account_id") != self.account_id
                    or reply.get("robot_id") != self.robot_id or reply.get("source_sha256") != self.source_sha256
                    or reply.get("kind") not in {"PRE_CLAIM", "TERMINAL"}
                    or reply.get("raw_sha256") != expected_raw_sha256 or reply.get("facts_sha256") != expected_facts_sha256
                    or not isinstance(reply.get("facts"), dict) or object_hash(reply["facts"]) != expected_facts_sha256):
                raise ReceiptDenied("BROKER_READBACK_IDENTITY_OR_HASH_MISMATCH")
            observed, received, verified = map(_instant, (reply["observed_at"], reply["received_at"], reply["verified_at"]))
            now = self._now()
            if not observed <= received <= verified <= now or (now - verified).total_seconds() > 15:
                raise ReceiptDenied("BROKER_READBACK_TIME_INVALID")
            return reply
        return self._verified(validate, write=False)


    def _native_reply(self, reply: dict, *, evidence_id: str, facts_sha256: str, status: str, expected_kind: str | None = None) -> dict:
        if (self._last_http_status != 200 or reply.get("source") != "bound_broker_reader_evidence_v3"
                or reply.get("status") != status or reply.get("evidence_id") != evidence_id
                or reply.get("environment") != ENVIRONMENT or reply.get("account_id") != self.account_id
                or reply.get("robot_id") != self.robot_id or reply.get("source_sha256") != self.source_sha256
                or reply.get("kind") not in {"NATIVE_ORDER", "PAIRED_TERMINAL"}
                or (expected_kind is not None and reply.get("kind") != expected_kind)
                or reply.get("facts_sha256") != facts_sha256 or not isinstance(reply.get("facts"), dict)
                or object_hash(reply["facts"]) != facts_sha256):
            raise ReceiptDenied("NATIVE_EVIDENCE_READBACK_MISMATCH")
        validate_native_facts(reply["facts"], reply["kind"])
        observed, received, verified = map(_instant, (reply["observed_at"], reply["received_at"], reply["verified_at"]))
        if not observed <= received <= verified <= self._now() or (self._now() - verified).total_seconds() > 15:
            raise ReceiptDenied("NATIVE_EVIDENCE_READBACK_TIME_INVALID")
        return reply

    def ingest_native_evidence_v3(self, *, evidence_id: str, kind: str, observed_at: str,
                                  facts: Mapping[str, Any]) -> dict:
        self._scope("broker_reader")
        _id(evidence_id)
        if kind not in {"NATIVE_ORDER", "PAIRED_TERMINAL"} or not isinstance(facts, Mapping):
            raise ReceiptDenied("NATIVE_EVIDENCE_SHAPE_DENIED")
        observed = _instant(observed_at)
        if not 0 <= (self._now() - observed).total_seconds() <= 30:
            raise ReceiptDenied("NATIVE_EVIDENCE_STALE")
        validate_native_facts(facts, kind)
        digest = object_hash(dict(facts))
        request = {"op": "ingest_native_evidence_v3", "environment": ENVIRONMENT,
                   "account_id": self.account_id, "robot_id": self.robot_id, "source_sha256": self.source_sha256,
                   "evidence_id": evidence_id, "kind": kind, "observed_at": observed_at,
                   "facts_sha256": digest, "facts": dict(facts)}
        reply = self._call(request, write=True)
        return self._verified(lambda: self._native_reply(reply, evidence_id=evidence_id,
                              facts_sha256=digest, status="EVIDENCE_RECORDED", expected_kind=kind), write=True)

    def read_native_evidence_v3(self, evidence_id: str, *, expected_facts_sha256: str) -> dict:
        self._scope("broker_reader")
        _id(evidence_id); _sha(expected_facts_sha256)
        reply = self._call({"op": "read_native_evidence_v3", "environment": ENVIRONMENT,
                           "account_id": self.account_id, "robot_id": self.robot_id,
                           "source_sha256": self.source_sha256, "evidence_id": evidence_id}, write=False)
        return self._verified(lambda: self._native_reply(reply, evidence_id=evidence_id,
                              facts_sha256=expected_facts_sha256, status="EVIDENCE_READ"), write=False)


def validate_native_facts(facts: Mapping, kind: str) -> None:
    if not isinstance(facts, Mapping) or set(facts) != NATIVE_FACT_FIELDS:
        raise ReceiptDenied("NATIVE_FACT_FIELDS_INVALID")
    for field in ("command_id", "claim_id", "order_id"):
        _id(facts[field])
    for field in NATIVE_HASH_FIELDS:
        _sha(facts[field])
    if (not isinstance(facts["instrument"], str) or not re.fullmatch(r"au[0-9]{4}", facts["instrument"])
            or facts["action"] not in {"OPEN_LONG", "CLOSE_LONG"}
            or facts["order_status"] not in {"PENDING", "FILLED", "REJECTED", "CANCELED"}
            or any(type(facts[k]) is not int or facts[k] not in {0, 1}
                   for k in ("filled_quantity", "position_quantity", "pending_order_count"))
            or facts["filled_quantity"] != (1 if facts["order_status"] == "FILLED" else 0)
            or facts["order_status"] != "PENDING" and facts["pending_order_count"] != 0):
        raise ReceiptDenied("NATIVE_FACT_QUANTITY_OR_STATUS_INVALID")
    if kind == "NATIVE_ORDER":
        if any(facts[k] is not None for k in ("parent_claim_id", "parent_order_id", "reconciliation")):
            raise ReceiptDenied("NATIVE_FACT_IS_NOT_FOUR_WAY")
        return
    if (kind != "PAIRED_TERMINAL" or facts["action"] != "CLOSE_LONG" or facts["order_status"] != "FILLED"
            or facts["position_quantity"] != 0 or facts["pending_order_count"] != 0
            or not isinstance(facts["reconciliation"], Mapping)
            or set(facts["reconciliation"]) != {"broker", "execution", "ledger", "expected"}):
        raise ReceiptDenied("PAIRED_FOUR_WAY_REQUIRED")
    _id(facts["parent_claim_id"]); _id(facts["parent_order_id"])
    if facts["parent_order_id"] == facts["order_id"]:
        raise ReceiptDenied("PAIRED_ORDER_IDENTITIES_INVALID")
    parties = list(facts["reconciliation"].values())
    producers = []
    for party in parties:
        if not isinstance(party, Mapping) or set(party) != PAIR_FIELDS:
            raise ReceiptDenied("PAIRED_PARTY_FIELDS_INVALID")
        _id(party["producer_id"]); _sha(party["proof_sha256"])
        producers.append(party["producer_id"])
        if (party["parent_order_id"] != facts["parent_order_id"] or party["child_order_id"] != facts["order_id"]
                or type(party["position_quantity"]) is not int or party["position_quantity"] != 0
                or any(type(party[k]) is not int or party[k] != 1 for k in ("open_filled_quantity", "close_filled_quantity"))
                or any(type(party[k]) is not int or not 0 <= party[k] <= 2**53 - 1
                       for k in ("cash_cents", "available_cents", "frozen_margin_cents"))):
            raise ReceiptDenied("PAIRED_PARTY_QUANTITY_OR_AMOUNT_INVALID")
    if len(set(producers)) != 4:
        raise ReceiptDenied("PAIRED_INDEPENDENT_PRODUCERS_REQUIRED")
    for k in ("cash_cents", "available_cents", "frozen_margin_cents"):
        if max(p[k] for p in parties) - min(p[k] for p in parties) > 1:
            raise ReceiptDenied("PAIRED_FOUR_WAY_DRIFT")
