"""Offline CommandRobot transport tests; all HTTP calls use in-memory fakes."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tests.test_gold_au_gateway import case  # noqa: E402
from yuanli_invest.gold_au_gateway import build_entry_ticket  # noqa: E402
from yuanli_invest.gold_paper import PaperDenied  # noqa: E402
from yuanli_invest.youquant_command_transport import (  # noqa: E402
    API_URL, ApiCredentials, DurableOutbox, TransportDenied, _NoRedirect,
    _https_post, deliver_prepared_ticket,
)


class CommandTransportTests(unittest.TestCase):
    def setUp(self):
        self.args = case()
        self.ticket = build_entry_ticket(**self.args)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.outbox = DurableOutbox(Path(self.temporary.name) / "attempts.sqlite")
        self.credentials = ApiCredentials("test-access-key", "test-secret-key")
        self.network_calls = []

    def deliver(self, *, ticket=None, post=None, dry_run=True, **changes):
        arguments = dict(
            signing_key=self.args["signing_key"], grant=self.args["grant"],
            provider_snapshot=self.args["provider_snapshot"],
            ledger=self.args["ledger"], now=self.args["now"],
            dry_run=dry_run, credentials=self.credentials,
            outbox=self.outbox, http_post=post,
        )
        arguments.update(changes)
        return deliver_prepared_ticket(ticket or self.ticket, **arguments)

    def _ack(self, form):
        self.network_calls.append(form)
        return 200, b'{"code":0,"data":{"result":true,"error":null}}'

    def test_default_dry_run_never_claims_or_calls_network(self):
        result = self.deliver(post=self._ack, credentials=None, outbox=None)
        self.assertEqual(result["status"], "DRY_RUN_VALIDATED")
        self.assertFalse(result["network_attempted"])
        self.assertFalse(result["broker_fill_proven"])
        self.assertEqual(self.network_calls, [])
        self.assertIsNone(self.outbox.read(result["command_id"]))

    def test_ticket_hmac_hash_and_fresh_readback_are_required_before_claim(self):
        broken = deepcopy(self.ticket)
        broken["envelope"]["payload"]["quantity"] = 2
        with self.assertRaises(TransportDenied) as error:
            self.deliver(ticket=broken, dry_run=False, post=self._ack)
        self.assertEqual(error.exception.code, "TICKET_HASH_MISMATCH")
        stale = deepcopy(self.args["provider_snapshot"])
        stale["observed_at"] = (self.args["now"] - timedelta(seconds=16)).isoformat()
        with self.assertRaises(PaperDenied) as error:
            self.deliver(dry_run=False, provider_snapshot=stale, post=self._ack)
        self.assertEqual(error.exception.code, "STALE_PROVIDER_STATE")
        self.assertEqual(self.network_calls, [])
        self.assertIsNone(self.outbox.read(self.ticket["envelope"]["payload"]["command_id"]))

    def test_token_post_exact_arguments_and_ack_is_not_fill(self):
        result = self.deliver(dry_run=False, post=self._ack)
        self.assertEqual(result["status"], "API_ACK_NOT_FILL")
        self.assertFalse(result["broker_fill_proven"])
        self.assertEqual(len(self.network_calls), 1)
        form = parse_qs(self.network_calls[0].decode("utf-8"), strict_parsing=True)
        self.assertEqual(set(form), {"version", "access_key", "method", "args", "nonce", "sign"})
        self.assertEqual(form["version"], ["1.0"])
        self.assertEqual(form["method"], ["CommandRobot"])
        robot_id, command_text = json.loads(form["args"][0])
        self.assertEqual(robot_id, self.args["grant"].robot_id)
        self.assertEqual(json.loads(command_text), self.ticket["envelope"])
        signed = f'1.0|CommandRobot|{form["args"][0]}|{form["nonce"][0]}|test-secret-key'
        self.assertEqual(form["sign"], [hashlib.md5(signed.encode()).hexdigest()])
        self.assertNotIn("secret_key", form)
        self.assertNotIn("test-secret-key", self.network_calls[0].decode())
        row = self.outbox.read(result["command_id"])
        self.assertEqual(row["state"], "API_ACK_NOT_FILL")
        self.assertEqual(row["api_code"], 0)

    def test_timeout_and_negative_ack_are_never_resent(self):
        def timeout(form):
            self.network_calls.append(form)
            raise TimeoutError("unknown delivery")

        first = self.deliver(dry_run=False, post=timeout)
        self.assertEqual(first["status"], "DELIVERY_UNKNOWN")
        again = self.deliver(dry_run=False, post=self._ack)
        self.assertEqual(again["status"], "ALREADY_ATTEMPTED_NO_RETRY")
        self.assertEqual(len(self.network_calls), 1)

        other = DurableOutbox(Path(self.temporary.name) / "other.sqlite")
        negative = self.deliver(dry_run=False, outbox=other,
                                post=lambda form: (200, b'{"code":0,"data":{"result":false,"error":null}}'))
        self.assertEqual(negative["status"], "API_NOT_DELIVERED")
        self.assertEqual(other.read(negative["command_id"])["state"], "API_NOT_DELIVERED")

    def test_oversized_or_malformed_response_stays_ambiguous(self):
        result = self.deliver(dry_run=False, post=lambda form: (200, b"X" * 8193))
        self.assertEqual(result["status"], "DELIVERY_UNKNOWN")
        self.assertEqual(self.deliver(dry_run=False, post=self._ack)["status"],
                         "ALREADY_ATTEMPTED_NO_RETRY")

    def test_atomic_claim_blocks_parallel_duplicate_submission(self):
        def send(_):
            self.network_calls.append(True)
            return 200, b'{"code":0,"data":{"result":true,"error":null}}'

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.deliver, dry_run=False, post=send) for _ in range(2)]
            statuses = [future.result()["status"] for future in futures]
        self.assertCountEqual(statuses, ["API_ACK_NOT_FILL", "ALREADY_ATTEMPTED_NO_RETRY"])
        self.assertEqual(len(self.network_calls), 1)

    def test_outbox_conflicting_hash_refuses_reuse(self):
        body = self.ticket["envelope"]["payload"]
        first = self.outbox.claim(command_id=body["command_id"],
                                  contract_hash=body["contract_hash"],
                                  ticket_hash=self.ticket["ticket_hash"], now=self.args["now"])
        self.assertIsInstance(first, int)
        with self.assertRaises(TransportDenied) as error:
            self.outbox.claim(command_id=body["command_id"],
                              contract_hash="sha256:" + "f" * 64,
                              ticket_hash=self.ticket["ticket_hash"], now=self.args["now"])
        self.assertEqual(error.exception.code, "COMMAND_ID_CONFLICT")

    def test_https_sender_uses_fixed_post_verified_tls_and_no_redirect(self):
        class FakeResponse:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, count):
                self_count.append(count)
                return b"{}"

        class FakeOpener:
            def open(self, request, timeout):
                self.assertEqual(request.full_url, API_URL)
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(timeout, 10)
                self.assertEqual(request.data, b"safe=form")
                return FakeResponse()

        self_count = []
        owner = self
        FakeOpener.assertEqual = owner.assertEqual
        with patch("yuanli_invest.youquant_command_transport.build_opener",
                   side_effect=lambda *handlers: self._check_handlers(handlers, FakeOpener())):
            status, content = _https_post(b"safe=form")
        self.assertEqual((status, content), (200, b"{}"))
        self.assertEqual(self_count, [8193])

    def _check_handlers(self, handlers, opener):
        self.assertTrue(any(isinstance(item, _NoRedirect) for item in handlers))
        self.assertTrue(any(item.__class__.__name__ == "ProxyHandler" and item.proxies == {}
                            for item in handlers))
        self.assertTrue(any(item.__class__.__name__ == "HTTPSHandler" and
                            item._context.verify_mode.name == "CERT_REQUIRED"
                            for item in handlers))
        return opener


if __name__ == "__main__":
    unittest.main()
