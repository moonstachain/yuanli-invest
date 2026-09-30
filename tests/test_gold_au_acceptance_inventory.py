from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gold_au_acceptance_inventory import inspect


class AcceptanceInventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 9, 26, 11, tzinfo=timezone.utc)

    def matrix(self, row):
        path = self.root / "matrix.json"
        path.write_text(json.dumps({"schema_version": "gold-au-engineering-acceptance-matrix.v1",
                                    "items": [row]}))
        return path

    def row(self, fact, stamp="2026-09-26T10:00:00+00:00"):
        path = self.root / "evidence.json"
        path.write_text(json.dumps(fact))
        return {"case_id": "readonly_connection", "kind": "ACTUAL_REQUIRED", "status": "PASS",
                "identity": {"environment": "SIMNOW_FIRST_NORMAL", "account_id": "TEST-ONLY", "robot_id": 1},
                "evidence_ref": str(path), "evidence_observed_at": stamp,
                "evidence_sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()}

    def result(self, row):
        result = inspect(self.matrix(row), observed_at=self.now)
        case = next(r for r in result["items"] if r["case_id"] == "readonly_connection")
        self.assertFalse(result["broker_action_authorized"])
        self.assertFalse(result["observation_start_authorized"])
        return case["status"]

    def test_rehearsal_bytes_never_satisfy_actual_pass(self):
        self.assertEqual(self.result(self.row({"kind": "REHEARSAL"})), "INVALID_ACTUAL_RECEIPT")

    def test_hash_tampering_rejected(self):
        row = self.row({"kind": "ACTUAL"})
        Path(row["evidence_ref"]).write_text('{"kind":"DIFFERENT"}')
        self.assertEqual(self.result(row), "INVALID_ACTUAL_RECEIPT")

    def test_future_receipt_rejected(self):
        self.assertEqual(self.result(self.row({"kind": "ACTUAL"}, "2026-09-28T01:15:00Z")), "INVALID_ACTUAL_RECEIPT")

    def test_valid_bytes_still_do_not_authenticate_identity(self):
        self.assertEqual(self.result(self.row({"kind": "ACTUAL"})),
                         "ARTIFACT_INTEGRITY_CHECKED_IDENTITY_NOT_AUTHENTICATED")

    def test_duplicate_and_unknown_cases_rejected(self):
        path = self.matrix({"case_id": "not_a_case"})
        with self.assertRaisesRegex(ValueError, "UNKNOWN_ACCEPTANCE_CASE"):
            inspect(path, observed_at=self.now)
        row = self.row({"kind": "ACTUAL"})
        path.write_text(json.dumps({"schema_version": "gold-au-engineering-acceptance-matrix.v1", "items": [row, row]}))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ACCEPTANCE_CASE"):
            inspect(path, observed_at=self.now)


if __name__ == "__main__":
    unittest.main()
