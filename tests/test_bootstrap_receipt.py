import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import verify_bootstrap_receipt as verifier

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "generated" / "bootstrap-exact-sha.json"


class BootstrapReceiptTests(unittest.TestCase):
    def test_exact_source_recomputes(self):
        subprocess.run([sys.executable, "scripts/verify_bootstrap_receipt.py"], cwd=ROOT, check=True)

    def test_transition_stops_before_activation(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["canon_transition"]["state"], "pending_registry_activation")
        self.assertEqual(receipt["canon_transition"]["current_operational_canon"], "moonstachain/quant-workspace")
        self.assertEqual(receipt["surfaces"]["research_admission"], "blocked_unassigned_evidence_reviewer")
        self.assertEqual(receipt["counts"]["approved_research_objects"], 0)


class GitArtifactTests(unittest.TestCase):
    def test_exact_blobs_include_binary_empty_and_unusual_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payloads = {
                "plain.txt": b"research\n",
                "empty.txt": b"",
                "space name.bin": b"\x00\xff\nabc blob 10\n",
                "nested/换行\n及制表\t.txt": b"exact bytes\x00",
                "large.bin": bytes(range(256)) * 1024,
            }
            for relative, payload in payloads.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            (root / "link").symlink_to("plain.txt")
            payloads["link"] = b"plain.txt"
            generated = root / "receipts/generated/ignored.json"
            generated.parent.mkdir(parents=True)
            generated.write_text("{}")
            for args in [
                ["init", "-q"],
                ["add", "."],
                ["-c", "user.name=Artifact Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"],
            ]:
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
            rows, artifact_hash = verifier.artifact_at("HEAD", root)
            expected = [
                {"path": path, "sha256": hashlib.sha256(payloads[path]).hexdigest(), "bytes": len(payloads[path])}
                for path in sorted(payloads)
            ]
            self.assertEqual(rows, expected)
            encoded = json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            self.assertEqual(artifact_hash, hashlib.sha256(encoded).hexdigest())

    def test_missing_or_truncated_blob_is_rejected(self):
        object_id = b"a" * 40
        tree = b"100644 blob " + object_id + b"\tdata.bin\0"
        responses = [object_id + b" missing\n", object_id + b" blob 10\nshort\n"]
        for payload in responses:
            with self.subTest(payload=payload):
                with mock.patch.object(verifier, "git", return_value=tree), mock.patch.object(
                    verifier.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=payload)
                ):
                    with self.assertRaises(ValueError):
                        verifier.artifact_at("HEAD")


if __name__ == "__main__":
    unittest.main()
