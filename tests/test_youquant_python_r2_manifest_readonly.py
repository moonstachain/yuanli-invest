"""Bounded offline checks for the exact-file private download diagnostic."""
import io
import json
import os
import stat
import types
import unittest
from unittest.mock import patch

from scripts import youquant_python_r2_manifest_readonly as reader


class ManifestReaderTests(unittest.TestCase):
    def payload(self, **updates):
        value = {"schema_version": "gold-au-python-range-parts.v1", "errors": [],
                 "parts": [], "received_byte_counts": {}}
        value.update(updates)
        return json.dumps(value).encode()

    def read(self, payload, *, mode=0o600, nlink=1):
        info = types.SimpleNamespace(st_mode=stat.S_IFREG | mode, st_uid=0,
                                     st_nlink=nlink, st_size=len(payload))
        directory = types.SimpleNamespace(st_mode=stat.S_IFDIR | 0o700, st_uid=0)
        raw = io.BytesIO(payload)
        raw.fileno = lambda: 17
        with patch.object(reader.os, "geteuid", return_value=0), \
             patch.object(reader.os, "lstat", return_value=directory), \
             patch.object(reader.os, "open", return_value=17) as open_file, \
             patch.object(reader.os, "fdopen", return_value=raw), \
             patch.object(reader.os, "fstat", return_value=info):
            result = reader.read_result()
        open_file.assert_called_once_with(reader.FILE, os.O_RDONLY | os.O_NOFOLLOW)
        return result

    def test_only_whitelisted_fields_and_reasons_leave_reader(self):
        result = self.read(self.payload(errors=[{"index": 0, "reason": "TimeoutError", "url": "secret"},
                                               {"index": 1, "reason": "secret"}],
                                       parts=[{"index": 2, "start": 5, "end": 7, "bytes": 3,
                                               "url": "secret", "sha256": "secret"}],
                                       received_byte_counts={"0": 123}, credential="secret"))
        self.assertNotIn("secret", json.dumps(result))
        self.assertEqual(result["errors"], [{"index": 0, "reason": "TimeoutError"},
                                            {"index": 1, "reason": "UNKNOWN_SANITIZED_REASON"}])
        self.assertEqual(result["parts"], [{"index": 2, "start": 5, "end": 7, "bytes": 3}])
        self.assertFalse(result["network_access_performed"])
        self.assertFalse(result["file_write_performed"])

    def test_metadata_denied_before_content_read(self):
        for mode, nlink in ((0o666, 1), (0o600, 2)):
            with self.subTest(mode=mode, nlink=nlink), self.assertRaisesRegex(ValueError, "PRIVATE_MANIFEST_METADATA_INVALID"):
                self.read(self.payload(), mode=mode, nlink=nlink)

    def test_oversize_and_out_of_range_counts_denied(self):
        with self.assertRaisesRegex(ValueError, "PRIVATE_MANIFEST_METADATA_INVALID"):
            self.read(b" " * 16385)
        for changes in ({"errors": [{"index": 8, "reason": "TimeoutError"}]},
                        {"errors": [{"index": 0, "reason": "TimeoutError"}] * 9},
                        {"received_byte_counts": {"8": 1}},
                        {"received_byte_counts": {"0": True}},
                        {"parts": [{"index": 0, "start": 0, "end": 1, "bytes": -1}]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.read(self.payload(**changes))

    def test_wrong_host_denied_before_file_lookup(self):
        with patch.object(reader.os, "geteuid", return_value=1000), \
             patch.object(reader.os, "lstat", side_effect=AssertionError("filesystem")), \
             self.assertRaisesRegex(ValueError, "HOST_UID_CHANGED"):
            reader.read_result()


if __name__ == "__main__":
    unittest.main()
