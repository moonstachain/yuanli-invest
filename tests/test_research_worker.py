import base64
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import research_worker as worker
from scripts import research_sink
from scripts import ymq_gold2_live_shadow as shadow
from tests.test_daily_first_capture import daily_bundle
from yuanli_invest.receipts import read_envelope, receipt_envelope
from yuanli_invest.first_capture import settle_daily_first_capture


def raw_wind(value="102.000000000000000001", day="20260909"):
    # String construction preserves provider numeric token precision.
    inner = '{"metrics":[{"meta":{"code":"S0031645"},"date":["' + day + '"],"value":[' + value + ']}]}'
    return json.dumps({"content": [{"type": "text", "text": inner}], "isError": False}, ensure_ascii=False).encode()


class CaptureAdapterTests(unittest.TestCase):
    def test_daily_capture_retains_exact_completed_dates_and_shared_raw_bytes(self):
        source = daily_bundle()["trusted_source"]
        inner = {"metrics": [{"meta": {"code": source["series_id"]}, "date": ["20260911", "20260909", "20260910", "20260908"], "value": [104, 102, 103, 100]}]}
        raw = json.dumps({"content": [{"type": "text", "text": json.dumps(inner)}]}).encode()
        captures = worker.capture_payloads(raw, source, "2026-09-09T23:30:00Z")
        # Source-local date is already September 10 even though UTC is still 9.
        self.assertEqual([item["trade_date"] for item in captures], ["2026-09-08", "2026-09-09"])
        self.assertEqual([item["value_decimal"] for item in captures], ["100", "102"])
        for item in captures:
            self.assertEqual(base64.b64decode(item["payload_base64"]), raw)
            self.assertEqual(item["payload_sha256"], hashlib.sha256(raw).hexdigest())

    def test_decimal_capture_binds_original_raw_bytes(self):
        raw = raw_wind()
        record = worker.capture_payload(raw, daily_bundle()["trusted_source"], "2026-09-09", "2026-09-09T18:00:00Z")
        self.assertEqual(record["value_decimal"], "102.000000000000000001")
        self.assertEqual(base64.b64decode(record["payload_base64"]), raw)
        self.assertEqual(record["payload_sha256"], hashlib.sha256(raw).hexdigest())

    def test_missing_exact_date_is_evidence_gap_not_nearest_price(self):
        self.assertIsNone(worker.capture_payload(raw_wind(day="20260908"), daily_bundle()["trusted_source"], "2026-09-09", "2026-09-09T18:00:00Z"))

    def test_bad_or_wrong_series_price_is_rejected(self):
        for value in ("NaN", "Infinity", "true", '"102"', "0", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                worker.capture_payload(raw_wind(value), daily_bundle()["trusted_source"], "2026-09-09", "2026-09-09T18:00:00Z")
        with self.assertRaisesRegex(ValueError, "exact registered series"):
            worker.capture_payload(raw_wind().replace(b"S0031645", b"DIFFERENT"), daily_bundle()["trusted_source"], "2026-09-09", "2026-09-09T18:00:00Z")


class WorkerTests(unittest.TestCase):
    def test_one_capture_failure_does_not_skip_other_dates_or_due_queue(self):
        source = daily_bundle()["trusted_source"]
        inner = {"metrics": [{"meta": {"code": source["series_id"]}, "date": ["20260908", "20260909"], "value": [100, 102]}]}
        raw = json.dumps({"content": [{"type": "text", "text": json.dumps(inner)}]}).encode()
        calls = []
        def gateway(operation, payload):
            calls.append((operation, payload))
            if operation == "capture_first_price" and payload["trade_date"] == "2026-09-08":
                raise OSError("offline")
            return {"items": []} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=lambda: raw, gateway=gateway, source=source, clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual([operation for operation, _ in calls], ["capture_first_price", "capture_first_price", "list_due_claims"])
        self.assertEqual(result["errors"][0]["trade_date"], "2026-09-08")

    def test_interrupted_learning_recovers_original_settlement_without_recompute(self):
        bundle = daily_bundle()
        committed = receipt_envelope(settle_daily_first_capture(bundle))
        bundle["settlement"] = committed
        calls = []
        def gateway(operation, payload):
            calls.append((operation, payload))
            return {"items": [bundle]} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 12, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "COMPLETE")
        self.assertNotIn("record_settlement", [op for op, _ in calls])
        learning = read_envelope(calls[-1][1])
        self.assertEqual(learning["settlement_receipt_sha256"], committed["receipt_sha256"])

    def test_insufficient_endpoint_evidence_never_creates_learning(self):
        bundle = daily_bundle(); bundle["observations"] = []
        calls = []
        def gateway(operation, payload):
            calls.append((operation, payload))
            return {"items": [bundle]} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["settlements"][0]["status"], "INDETERMINATE_EVIDENCE")
        self.assertNotIn("record_learning", [op for op, _ in calls])
        attempt = calls[-1]
        self.assertEqual(attempt[0], "record_claim_attempt")
        self.assertEqual(read_envelope(attempt[1])["status"], "INDETERMINATE_EVIDENCE")

    def test_capture_then_read_due_then_record_exact_receipt_bytes(self):
        calls = []
        bundle = daily_bundle()
        def gateway(operation, payload):
            calls.append((operation, payload))
            if operation == "list_due_claims":
                return {"items": [bundle]}
            if operation == "record_settlement":
                return {"settlement": payload}
            return {"id": "stored"}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual([op for op, _ in calls], ["capture_first_price", "list_due_claims", "record_settlement", "record_learning"])
        persisted = calls[2][1]
        receipt = read_envelope(persisted)
        self.assertEqual(receipt["status"], "SETTLED_RESEARCH")
        self.assertEqual(persisted["claim_sha256"], bundle["registration"]["claim_sha256"])
        learning = read_envelope(calls[3][1])
        self.assertEqual(learning["settlement_receipt_sha256"], persisted["receipt_sha256"])
        self.assertFalse(learning["accepted_learning"])

    def test_missing_capture_does_not_block_other_due_claims(self):
        gateway = mock.Mock(return_value={"items": []})
        result = worker.run_once(fetch=lambda: raw_wind(day="20260908"), gateway=gateway, source=daily_bundle()["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["capture"]["status"], "INDETERMINATE_EVIDENCE")
        self.assertEqual(result["status"], "COMPLETE")
        gateway.assert_called_once_with("list_due_claims", {"limit": 100})

    def test_transport_error_is_not_scientific_indeterminate(self):
        calls = []
        def gateway(operation, payload):
            calls.append(operation)
            if operation == "capture_first_price":
                raise RuntimeError("offline")
            return {"items": []}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=daily_bundle()["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual(result["capture"]["status"], "SYSTEM_ERROR")
        self.assertEqual(calls, ["capture_first_price", "list_due_claims"])

    def test_invalid_registered_claim_cannot_persist_settlement(self):
        bundle = daily_bundle(); bundle["claim"]["model_direction"] = -1
        calls = []
        def gateway(operation, payload):
            calls.append(operation)
            return {"items": [bundle]} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertNotIn("record_settlement", calls)
        self.assertEqual(calls[-1], "record_claim_attempt")

    def test_source_failure_persists_system_error_instead_of_evidence_gap(self):
        bundle = daily_bundle(); bundle["observations"] = []
        calls = []
        def gateway(operation, payload):
            calls.append((operation, payload))
            return {"items": [bundle]} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=mock.Mock(side_effect=OSError("offline")), gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual(calls[-1][0], "record_claim_attempt")
        self.assertEqual(calls[-1][1]["status"], "SYSTEM_ERROR")

    def test_failed_attempt_persistence_keeps_original_failure(self):
        bundle = daily_bundle(); bundle["claim"]["model_direction"] = -1
        def gateway(operation, payload):
            if operation == "record_claim_attempt":
                raise RuntimeError("offline")
            return {"items": [bundle]} if operation == "list_due_claims" else {}
        result = worker.run_once(fetch=raw_wind, gateway=gateway, source=bundle["trusted_source"], day="2026-09-09", clock=lambda: datetime(2026, 9, 10, 18, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual([error["error_type"] for error in result["errors"]], ["ValueError", "PERSISTENCE_FAILED"])

    def test_pagination_reaches_later_claims_and_rejects_repeated_cursor(self):
        gateway = mock.Mock(side_effect=[
            {"items": ["first"], "next_cursor": "one"},
            {"items": ["second"], "next_cursor": None},
        ])
        self.assertEqual(list(worker.due_claims(gateway)), ["first", "second"])
        self.assertEqual(gateway.call_args.args, ("list_due_claims", {"limit": 100, "cursor": "one"}))
        gateway = mock.Mock(return_value={"items": [], "next_cursor": "stuck"})
        with self.assertRaisesRegex(ValueError, "cursor did not advance"):
            list(worker.due_claims(gateway))
        self.assertEqual(gateway.call_count, 2)


class MachineGatewayTests(unittest.TestCase):
    def test_service_role_environment_never_substitutes_machine_token(self):
        with mock.patch.dict(os.environ, {"SUPABASE_URL": "https://example.invalid", "YMQ4_SUPABASE_SECRET_KEY": "HIGH_PRIVILEGE"}, clear=True):
            with self.assertRaises(ValueError):
                worker.MachineGateway.from_environment()

    def test_request_uses_scoped_headers_and_workspace_body(self):
        gateway = worker.MachineGateway("https://example.invalid/functions/v1/research-machine", "machine-one", "SCOPED_TOKEN", "workspace-one")
        response = BytesIO(b'{"ok":true,"data":[]}')
        with mock.patch.object(gateway._opener, "open", return_value=response) as opened:
            self.assertEqual(gateway("list_due_claims", {}), [])
        request = opened.call_args.args[0]
        self.assertNotIn("SCOPED_TOKEN", request.full_url)
        self.assertEqual(request.get_header("X-yuanli-ingest-token"), "SCOPED_TOKEN")
        self.assertEqual(json.loads(request.data), {"operation": "list_due_claims", "workspace_id": "workspace-one", "payload": {}})

    def test_legacy_sink_does_not_fall_back_to_service_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); client = root / "client.py"; client.touch()
            env = {"YIOS_TG1_PRODUCT_SINK_ENABLED": "true", "YIOS_TG1_SINK_CLIENT": str(client), "SUPABASE_URL": "https://example.invalid", "YMQ4_SUPABASE_SECRET_KEY": "HIGH_PRIVILEGE"}
            with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(shadow.subprocess, "run") as run:
                result = shadow.emit_product_sink(root / "receipt.json", root)
            self.assertEqual(result["status"], "PRODUCT_SINK_CREDENTIALS_NOT_PROJECTED")
            run.assert_not_called()

    def test_sink_transmits_new_receipt_and_learning_envelopes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); receipt = root / "receipt.json"; learning = root / "learning.json"
            receipt.write_text('{"status":"LIVE_SHADOW_RECEIPT"}')
            learning.write_text('{"accepted_learning":false}')
            gateway = mock.Mock(return_value={"snapshot_id": "saved"})
            with mock.patch("sys.argv", ["research_sink", "--receipt", str(receipt), "--learning", str(learning)]), mock.patch.object(research_sink.MachineGateway, "from_environment", return_value=gateway), mock.patch("builtins.print"):
                self.assertEqual(research_sink.main(), 0)
            operation, payload = gateway.call_args.args
            self.assertEqual(operation, "ingest_receipt")
            self.assertEqual(read_envelope(payload)["status"], "LIVE_SHADOW_RECEIPT")
            self.assertEqual(hashlib.sha256(payload["learning_json"].encode()).hexdigest(), payload["learning_sha256"])


if __name__ == "__main__":
    unittest.main()
