"""Local, single-attempt CommandRobot delivery for prepared GOLD2 paper tickets.

Only the token-authenticated YouQuant ``POST /api/v1`` form is supported.  A
successful API response acknowledges command delivery, not a broker order or
fill.  The separate paper runtime must read back and reconcile those facts.

The SQLite outbox reserves a command *before* any network call.  A reserved
command is never automatically resent, including after a crash or timeout.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import ssl
import time
from typing import Any, Callable, Mapping
from urllib.parse import urlencode
from urllib.request import (
    HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener,
)

from .gold_paper import PaperDenied, PaperGrant, PaperLedger, admit_command, verify_command


API_URL = "https://www.youquant.com/api/v1"
API_VERSION = "1.0"
API_METHOD = "CommandRobot"
MAX_COMMAND_BYTES = 16_384
MAX_RESPONSE_BYTES = 8_192
TIMEOUT_SECONDS = 10
TICKET_FIELDS = frozenset({
    "schema_version", "status", "signal_id", "prior_signal_registration",
    "prepared_at", "envelope",
    "evidence", "planned_one_lot_loss_cny", "allowed_one_lot_loss_cny",
    "stop_basis", "roll_before_max_hold", "transport_attempted", "ticket_hash",
})


class TransportDenied(ValueError):
    """Safe, credential-free reason for refusing a local delivery attempt."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, repr=False)
class ApiCredentials:
    access_key: str
    secret_key: str

    def __post_init__(self) -> None:
        if not self.access_key or not self.secret_key or not isinstance(self.access_key, str) or not isinstance(self.secret_key, str):
            raise TransportDenied("MISSING_API_CREDENTIALS")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_json_bytes(value)).hexdigest()


def _validate_ticket(ticket: Mapping[str, Any], signing_key: bytes) -> tuple[dict[str, Any], str]:
    if not isinstance(ticket, Mapping) or set(ticket) != TICKET_FIELDS:
        raise TransportDenied("INVALID_PREPARED_TICKET")
    if (ticket["schema_version"] != "gold-au-gateway-ticket.v1"
            or ticket["status"] != "PREPARED_NOT_SENT"
            or ticket["transport_attempted"] is not False):
        raise TransportDenied("TICKET_NOT_PREPARED")
    material = {key: value for key, value in ticket.items() if key != "ticket_hash"}
    try:
        expected_hash = _digest(material)
    except (TypeError, ValueError) as exc:
        raise TransportDenied("INVALID_PREPARED_TICKET") from exc
    if ticket["ticket_hash"] != expected_hash:
        raise TransportDenied("TICKET_HASH_MISMATCH")
    body = verify_command(ticket["envelope"], signing_key)
    evidence = ticket["evidence"]
    if (not isinstance(evidence, Mapping)
            or ticket["signal_id"] != evidence.get("signal_id")
            or ticket["prior_signal_registration"] != evidence.get("prior_signal_registration")
            or body["evidence_hash"] != _digest(evidence)
            or ticket["prepared_at"] != body["issued_at"]):
        raise TransportDenied("TICKET_COMMAND_BINDING_MISMATCH")
    if body["action"] != "OPEN_LONG" or body["reason"] != "ENTRY":
        raise TransportDenied("TICKET_NOT_GATEWAY_ENTRY")
    command_text = _json_bytes(ticket["envelope"]).decode("utf-8")
    if len(command_text.encode("utf-8")) > MAX_COMMAND_BYTES:
        raise TransportDenied("COMMAND_TOO_LARGE")
    return body, command_text


class DurableOutbox:
    """SQLite atomic claim; status changes never make a command retryable."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.is_absolute() or not self.path.parent.is_dir() or self.path.is_symlink():
            raise TransportDenied("INVALID_OUTBOX_PATH")
        if not self.path.exists():
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(fd)
        self._connect_and_initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _connect_and_initialize(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS command_attempts ("
                         "command_id TEXT PRIMARY KEY, contract_hash TEXT NOT NULL, "
                         "ticket_hash TEXT NOT NULL, nonce INTEGER NOT NULL, "
                         "state TEXT NOT NULL, reserved_at TEXT NOT NULL, "
                         "response_sha256 TEXT, api_code INTEGER)")
            conn.execute("CREATE TABLE IF NOT EXISTS nonce_state ("
                         "singleton INTEGER PRIMARY KEY CHECK (singleton = 1), last_nonce INTEGER NOT NULL)")

    def claim(self, *, command_id: str, contract_hash: str, ticket_hash: str,
              now: datetime) -> int | None:
        """Return a unique nonce or None if this exact command was claimed."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            old = conn.execute("SELECT contract_hash FROM command_attempts WHERE command_id=?",
                               (command_id,)).fetchone()
            if old is not None:
                conn.execute("ROLLBACK")
                if old[0] != contract_hash:
                    raise TransportDenied("COMMAND_ID_CONFLICT")
                return None
            previous = conn.execute("SELECT last_nonce FROM nonce_state WHERE singleton=1").fetchone()
            nonce = max(time.time_ns() // 1_000_000,
                        (previous[0] + 1) if previous is not None else 0)
            conn.execute("INSERT INTO nonce_state(singleton, last_nonce) VALUES (1, ?) "
                         "ON CONFLICT(singleton) DO UPDATE SET last_nonce=excluded.last_nonce", (nonce,))
            conn.execute("INSERT INTO command_attempts VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)",
                         (command_id, contract_hash, ticket_hash, nonce,
                          "ATTEMPT_RESERVED", now.isoformat()))
            conn.execute("COMMIT")
            return nonce
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def record_result(self, command_id: str, state: str, *, response_sha256: str | None,
                      api_code: int | None) -> None:
        if state not in {"API_ACK_NOT_FILL", "API_NOT_DELIVERED", "API_REJECTED", "DELIVERY_UNKNOWN"}:
            raise TransportDenied("INVALID_OUTBOX_STATE")
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("BEGIN IMMEDIATE")
                updated = conn.execute("UPDATE command_attempts SET state=?, response_sha256=?, api_code=? "
                                       "WHERE command_id=? AND state='ATTEMPT_RESERVED'",
                                       (state, response_sha256, api_code, command_id)).rowcount
                if updated != 1:
                    raise TransportDenied("OUTBOX_STATE_CONFLICT")

    def read(self, command_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT contract_hash, ticket_hash, nonce, state, reserved_at, "
                               "response_sha256, api_code FROM command_attempts WHERE command_id=?",
                               (command_id,)).fetchone()
        if row is None:
            return None
        keys = ("contract_hash", "ticket_hash", "nonce", "state", "reserved_at",
                "response_sha256", "api_code")
        return dict(zip(keys, row))


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request: Request, fp: Any, code: int,
                         msg: str, headers: Any, newurl: str) -> None:
        return None


def _https_post(form: bytes) -> tuple[int, bytes]:
    """Fixed HTTPS endpoint, verified TLS, no proxy/redirect, bounded read."""
    opener = build_opener(ProxyHandler({}), _NoRedirect(),
                          HTTPSHandler(context=ssl.create_default_context()))
    request = Request(API_URL, data=form,
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      method="POST")
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        content = response.read(MAX_RESPONSE_BYTES + 1)
        return response.status, content


def _token_form(credentials: ApiCredentials, robot_id: int,
                command_text: str, nonce: int) -> bytes:
    args = json.dumps([robot_id, command_text], ensure_ascii=False, separators=(",", ":"))
    material = f"{API_VERSION}|{API_METHOD}|{args}|{nonce}|{credentials.secret_key}"
    signature = hashlib.md5(material.encode("utf-8")).hexdigest()  # nosec: vendor token protocol
    return urlencode({"version": API_VERSION, "access_key": credentials.access_key,
                      "method": API_METHOD, "args": args, "nonce": nonce,
                      "sign": signature}).encode("utf-8")


def deliver_prepared_ticket(
    ticket: Mapping[str, Any], *, signing_key: bytes, grant: PaperGrant,
    provider_snapshot: Mapping[str, Any], ledger: PaperLedger,
    now: datetime | None = None, dry_run: bool = True,
    credentials: ApiCredentials | None = None,
    outbox: DurableOutbox | None = None,
    http_post: Callable[[bytes], tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    """Admit then optionally attempt one API delivery; never claim a fill."""
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise TransportDenied("NAIVE_NOW")
    body, command_text = _validate_ticket(ticket, signing_key)
    admitted = admit_command(ticket["envelope"], signing_key, grant,
                             provider_snapshot, ledger, now)
    if admitted["decision"] != "ALLOW":
        raise TransportDenied("COMMAND_ALREADY_ADMITTED")
    command_id = body["command_id"]
    if dry_run:
        return {"status": "DRY_RUN_VALIDATED", "command_id": command_id,
                "contract_hash": body["contract_hash"], "network_attempted": False,
                "broker_fill_proven": False}
    if http_post is None and abs((datetime.now(timezone.utc) - now.astimezone(timezone.utc)).total_seconds()) > 5:
        raise TransportDenied("LIVE_CLOCK_MISMATCH")
    if not isinstance(credentials, ApiCredentials) or not isinstance(outbox, DurableOutbox):
        raise TransportDenied("LIVE_TRANSPORT_NOT_CONFIGURED")
    if grant.robot_id != body["robot_id"]:
        raise TransportDenied("ROBOT_ID_MISMATCH")
    nonce = outbox.claim(command_id=command_id, contract_hash=body["contract_hash"],
                         ticket_hash=ticket["ticket_hash"], now=now)
    if nonce is None:
        return {"status": "ALREADY_ATTEMPTED_NO_RETRY", "command_id": command_id,
                "network_attempted": False, "broker_fill_proven": False}
    response_hash = None
    api_code = None
    try:
        form = _token_form(credentials, body["robot_id"], command_text, nonce)
        status_code, raw = (http_post or _https_post)(form)
        if status_code != 200 or not isinstance(raw, bytes) or len(raw) > MAX_RESPONSE_BYTES:
            state = "DELIVERY_UNKNOWN"
        else:
            response_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
            parsed = json.loads(raw)
            if not isinstance(parsed, dict) or type(parsed.get("code")) is not int:
                state = "DELIVERY_UNKNOWN"
            else:
                api_code = parsed["code"]
                data = parsed.get("data")
                if api_code != 0:
                    state = "API_REJECTED"
                elif not isinstance(data, dict) or data.get("error") is not None:
                    state = "DELIVERY_UNKNOWN"
                elif data.get("result") is True:
                    state = "API_ACK_NOT_FILL"
                elif data.get("result") is False:
                    state = "API_NOT_DELIVERED"
                else:
                    state = "DELIVERY_UNKNOWN"
    except Exception:
        # The request may have reached YouQuant even when the client timed out.
        # Neither a timeout nor a malformed reply permits automatic resend.
        state = "DELIVERY_UNKNOWN"
    outbox.record_result(command_id, state, response_sha256=response_hash,
                         api_code=api_code)
    return {"status": state, "command_id": command_id,
            "network_attempted": True, "broker_fill_proven": False,
            "api_code": api_code}
