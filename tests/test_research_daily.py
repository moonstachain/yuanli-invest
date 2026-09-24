from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import install_research_schedule as installer
from scripts import research_daily as daily
from tests.test_daily_first_capture import daily_bundle


NOW = datetime(2026, 9, 24, 0, 10, tzinfo=timezone.utc)


def provider_bytes(cli, code):
    payload = {"metrics": [{"meta": {"code": code}, "date": ["20260923"], "value": [102.0]}]}
    return json.dumps({"content": [{"type": "text", "text": json.dumps(payload)}]}).encode()


class DailyRunTests(unittest.TestCase):
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
