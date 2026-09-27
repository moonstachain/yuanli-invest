from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from yuanli_invest.gold_au_operations_status import build_operations_status, read_evidence, render_html
from scripts.gold_au_operations_status import write_new_output

NOW = datetime.fromisoformat("2026-09-28T09:16:00+08:00")


class OperationsStatusTests(unittest.TestCase):
    def config(self, sources=None):
        return {"schema_version": "gold-au-operations-status-config.v1", "receipt_sources": sources or {}}

    def build(self, sources=None, **kwargs):
        return build_operations_status(self.config(sources), as_of=NOW,
                                       launchd_observer=lambda label: {"installation": "LOADED", "state": "waiting", "runs": 0}, **kwargs)

    def test_unknown_is_not_flat_current_health_or_approved(self):
        result = self.build()
        self.assertIsNone(result["account_as_of_evidence"]["position_quantity"])
        self.assertEqual(result["account_as_of_evidence"]["pending_command"], "UNKNOWN")
        self.assertEqual(result["evidence"]["connection"]["current_status"], "UNKNOWN")
        self.assertFalse(result["broker_action_authorized"])
        self.assertIn("UNKNOWN_POSITION_IS_NOT_FLAT", result["warnings"])
        self.assertIn("NO_SCHEDULED_RUN_COUNT_OBSERVED", result["warnings"])

    def test_old_success_is_asof_not_current_health(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            path.write_text(json.dumps({"status": "CONNECTED", "observed_at": (NOW - timedelta(days=2)).isoformat()}))
            result = self.build({"connection": {"path": str(path), "max_age_seconds": 300}})
            evidence = result["evidence"]["connection"]
            self.assertEqual(evidence["current_status"], "STALE_AS_OF_EVIDENCE")
            self.assertEqual(evidence["evidence_status"], "CONNECTED")
            self.assertFalse(evidence["is_today_in_shanghai"])
            self.assertIn("CURRENT_SIMNOW_CONNECTION_NOT_VERIFIED", result["warnings"])

    def test_mtime_never_substitutes_missing_timestamp(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"; path.write_text('{"status":"CONNECTED"}')
            result = self.build({"connection": {"path": str(path)}})
            self.assertEqual(result["evidence"]["connection"]["reason"], "EVIDENCE_TIME_UNKNOWN")
            self.assertIsNone(result["evidence"]["connection"]["evidence_time"])

    def test_hash_tamper_future_and_symlink_rejected(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            path.write_text(json.dumps({"status": "CONNECTED", "observed_at": (NOW + timedelta(seconds=1)).isoformat()}))
            evidence, value = read_evidence({"path": str(path)}, as_of=NOW)
            self.assertEqual(evidence["current_status"], "INVALID_FUTURE_EVIDENCE"); self.assertIsNone(value)
            evidence, _ = read_evidence({"path": str(path), "sha256": "a" * 64}, as_of=NOW)
            self.assertEqual(evidence["reason"], "EVIDENCE_HASH_MISMATCH")
            link = path.with_name("link"); link.symlink_to(path)
            evidence, _ = read_evidence({"path": str(link)}, as_of=NOW)
            self.assertEqual(evidence["current_status"], "INVALID")

    def test_missing_evidence_not_run_not_zero_position(self):
        with TemporaryDirectory() as temporary:
            result = self.build({"account_coordinator": {"path": str(Path(temporary) / "missing.json")}})
            self.assertEqual(result["evidence"]["account_coordinator"]["current_status"], "NOT_RUN")
            self.assertIsNone(result["account_as_of_evidence"]["position_quantity"])

    def test_whitelist_removes_credentials_accounts_and_html_injection(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            path.write_text(json.dumps({"status": "CONNECTED", "observed_at": NOW.isoformat(),
                                       "password": "SUPER_SECRET_PASSWORD", "account_id": "PRIVATE_ACCOUNT",
                                       "reason": '<script>alert("x")</script>', "token": "SUPER_TOKEN"}))
            result = self.build({"connection": {"path": str(path)}})
            raw = json.dumps(result) + render_html(result)
            for secret in ("SUPER_SECRET_PASSWORD", "PRIVATE_ACCOUNT", "SUPER_TOKEN", "<script>"):
                self.assertNotIn(secret, raw)
            self.assertIn("default-src 'none'", raw)
            self.assertFalse(result["raw_evidence_rendered"])

    def test_natural_morning_distinguishes_today_and_previous_acceptance(self):
        accepted = {"status": "ACCEPTED_RESEARCH_FREEZE", "decision_date": "2026-09-28", "checked_at": NOW.isoformat(),
                    "outcome_reason": "NO_BREAKOUT", "actionable_entry": False, "external_time_anchor": "NOT_VERIFIED"}
        result = self.build(morning_acceptance=accepted)
        self.assertEqual(result["natural_morning"]["status"], "ACCEPTED_RESEARCH_FREEZE")
        accepted["decision_date"] = "2026-09-25"
        self.assertEqual(self.build(morning_acceptance=accepted)["natural_morning"]["status"], "UNKNOWN")

    def test_html_and_json_outputs_new_directory_only(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "status"
            result = self.build(); write_new_output(output, result)
            self.assertTrue((output / "index.html").is_file())
            self.assertEqual(json.loads((output / "status.json").read_text()), result)
            with self.assertRaises(ValueError): write_new_output(output, result)
            self.assertEqual({p.name for p in output.iterdir()}, {"index.html", "status.json"})

    def test_unrecognized_source_and_naive_clock_denied(self):
        with self.assertRaises(ValueError): self.build({"password": {}})
        with self.assertRaises(ValueError): build_operations_status(self.config(), as_of=datetime.now())


if __name__ == "__main__": unittest.main()
