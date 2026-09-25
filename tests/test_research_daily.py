from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import install_research_schedule as installer
from scripts import research_daily as daily
from tests.test_daily_first_capture import daily_bundle
from yuanli_invest.receipts import read_envelope, receipt_envelope


NOW = datetime(2026, 9, 24, 0, 10, tzinfo=timezone.utc)


def provider_bytes(cli, code):
    payload = {"metrics": [{"meta": {"code": code}, "date": ["20260923"], "value": [102.0]}]}
    return json.dumps({"content": [{"type": "text", "text": json.dumps(payload)}]}).encode()


class DailyRunTests(unittest.TestCase):
    def test_delayed_endpoint_is_captured_next_run_and_same_raw_retry_is_idempotent(self):
        bundle = daily_bundle()
        claim = bundle["claim"]
        claim.update(start_trade_date="2026-09-17", end_trade_date="2026-09-23", evidence_known_as_of="2026-09-16T10:00:00Z")
        frozen = receipt_envelope(claim)
        bundle["registration"].update(registered_at="2026-09-16T12:00:00Z", claim_json=frozen["receipt_json"], claim_sha256=frozen["receipt_sha256"])
        opening = bundle["observations"][0]
        opening.update(trade_date="2026-09-17", first_captured_at="2026-09-17T18:00:00Z")
        records = {(opening["trade_date"], opening["payload_sha256"]): opening}
        now, days = [NOW], [["20260922"]]
        calls, settlements = [], []
        def fetch(cli, code):
            if code != "S0031645":
                return provider_bytes(cli, code)
            inner = {"metrics": [{"meta": {"code": code}, "date": days[0], "value": [102] * len(days[0])}]}
            return json.dumps({"content": [{"type": "text", "text": json.dumps(inner)}]}).encode()
        def gateway(operation, payload):
            calls.append((operation, payload))
            if operation == "capture_first_price":
                key = payload["trade_date"], payload["payload_sha256"]
                if key not in records:
                    records[key] = {**payload, "capture_id": f"capture-{len(records)}", "first_captured_at": now[0].isoformat()}
                return records[key]
            if operation == "list_due_claims":
                return {"items": [] if settlements else [{**bundle, "observations": list(records.values())}]}
            if operation == "record_settlement":
                settlements.append(read_envelope(payload))
                return {"settlement": payload}
            return {}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(daily.shadow, "emit_learning_live", return_value={}):
            first = self.run_daily(Path(directory), fetch, gateway, now[0])
            self.assertEqual(first["worker"]["settlements"][0]["status"], "INDETERMINATE_EVIDENCE")
            now[0] = datetime(2026, 9, 25, 0, 10, tzinfo=timezone.utc)
            days[0] = ["20260922", "20260923", "20260924", "20260925", "20260926"]
            second = self.run_daily(Path(directory), fetch, gateway, now[0])
            after_capture = dict(records)
            first_seen = now[0].isoformat()
            now[0] += timedelta(hours=1)
            third = self.run_daily(Path(directory), fetch, gateway, now[0])
        self.assertEqual(second["worker"]["settlements"][0]["status"], "SETTLED_RESEARCH")
        self.assertEqual(third["worker"]["status"], "COMPLETE")
        self.assertEqual(records, after_capture)
        self.assertEqual(len(settlements), 1)
        self.assertEqual(sum(operation == "list_due_claims" for operation, _ in calls), 3)
        self.assertEqual({record["trade_date"] for record in records.values()}, {"2026-09-17", "2026-09-22", "2026-09-23", "2026-09-24"})
        closing = next(record for record in records.values() if record["capture_id"] == settlements[0]["selected_capture_ids"]["end"])
        self.assertEqual(closing["trade_date"], "2026-09-23")
        self.assertEqual(closing["first_captured_at"], first_seen)

    def run_daily(self, root, fetch, gateway, now=NOW):
        return daily.run_daily(
            cfg=daily.shadow.load_activation(), source=daily_bundle()["trusted_source"],
            cli_path=Path("/unused/cli.mjs"), runtime_dir=root, gateway=gateway,
            fetch=fetch, clock=lambda: now,
        )

    def test_each_provider_is_read_once_with_one_ingest_and_gold_capture(self):
        fetch = mock.Mock(side_effect=provider_bytes)
        calls = []
        def gateway(operation, payload):
            calls.append((operation, payload))
            return {"items": []} if operation == "list_due_claims" else {}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(daily.shadow, "emit_learning_live", return_value={}) as learning, mock.patch.object(daily.shadow, "emit_product_sink") as old_sink:
            result = self.run_daily(Path(directory), fetch, gateway)
            self.assertEqual(len(list(Path(directory).glob("2026-09-24/*.json"))), 1)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertCountEqual([call.args[1] for call in fetch.call_args_list], ["G1147404", "M0000271", "S0031645"])
        self.assertEqual([op for op, _ in calls], ["ingest_receipt", "capture_first_price", "list_due_claims"])
        self.assertEqual(calls[1][1]["trade_date"], "2026-09-23")
        learning.assert_called_once()
        old_sink.assert_not_called()

    def test_non_gold_provider_failure_still_captures_gold_and_processes_due(self):
        def fetch(cli, code):
            if code == "M0000271":
                raise subprocess.CalledProcessError(1, "provider")
            return provider_bytes(cli, code)
        calls = []
        def gateway(operation, payload):
            calls.append(operation)
            return {"items": []} if operation == "list_due_claims" else {}
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_daily(Path(directory), fetch, gateway)
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual(result["snapshot_status"], "PROVIDER_FAIL_CLOSED")
        self.assertEqual(result["worker"]["capture"]["status"], "CAPTURED")
        self.assertEqual(calls, ["ingest_receipt", "capture_first_price", "list_due_claims"])

    def test_snapshot_transport_failure_still_runs_worker(self):
        def gateway(operation, payload):
            if operation == "ingest_receipt":
                raise OSError("offline")
            return {"items": []} if operation == "list_due_claims" else {}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(daily.shadow, "emit_learning_live", return_value={}):
            result = self.run_daily(Path(directory), provider_bytes, gateway)
        self.assertEqual(result["status"], "SYSTEM_ERROR")
        self.assertEqual(result["worker"]["capture"]["status"], "CAPTURED")
        self.assertEqual(result["errors"], [{"operation": "ingest_receipt", "error_type": "OSError"}])

    def test_expired_window_does_not_read_write_or_call_gateway(self):
        fetch, gateway = mock.Mock(), mock.Mock()
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_daily(Path(directory), fetch, gateway, datetime(2026, 10, 16, tzinfo=timezone.utc))
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assertEqual(result, {"status": "PILOT_EXPIRED"})
        fetch.assert_not_called()
        gateway.assert_not_called()

    def test_schedule_rejects_other_host_timezones_before_activation(self):
        with mock.patch("sys.argv", ["installer", "--activate"]), mock.patch.object(installer, "host_timezone", return_value="UTC"), mock.patch.object(installer.subprocess, "run") as run, mock.patch("builtins.print"):
            self.assertEqual(installer.main(), 2)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
