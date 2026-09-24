import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts import build_manifest

ROOT = Path(__file__).resolve().parents[1]


class DeterminismTests(unittest.TestCase):
    def test_manifest_repeats_exactly(self):
        self.assertEqual(build_manifest.build(), build_manifest.build())

    def test_manifest_preserves_paths_bytes_and_exclusions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            included = {"a/data.bin": b"\x00\xff\n", "a-note.txt": b"", "z.txt": b"research"}
            excluded = [".git/HEAD", ".venv/lib/package.py", "nested/node_modules/dependency.js", "receipts/generated/receipt.json", "nested/.cache"]
            for relative, payload in included.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            for relative in excluded:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"not part of the artifact")
            expected = [
                {"path": relative, "sha256": hashlib.sha256(included[relative]).hexdigest(), "bytes": len(included[relative])}
                for relative in sorted(included, key=Path)
            ]
            self.assertEqual(build_manifest.records(root), expected)

    def test_content_change_changes_manifest_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "record.json"
            path.write_text('{"value":1}')
            before = build_manifest.build(root)
            path.write_text('{"value":2}')
            after = build_manifest.build(root)
            self.assertNotEqual(before["artifact_hash"], after["artifact_hash"])


if __name__ == "__main__":
    unittest.main()
