"""The editor artifact is exact, source-pinned and inert without a runtime."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.build_gold_au_simnow_single_file import (
    ADAPTER, ACCOUNTING, AUDITED_SHA256, CORE, SingleFileDenied, build_source,
    verify_file, write_file,
)
from yuanli_invest.gold_paper import PaperDenied, action_hash


ROOT = Path(__file__).resolve().parents[1]


class PoisonExchange:
    def __getattribute__(self, name):
        raise AssertionError("editor source touched the broker")


def forbidden_call(*args, **kwargs):
    raise AssertionError("editor source called a host API")


class SingleFileTests(unittest.TestCase):
    def test_deterministic_private_exact_source(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.py"
            second = Path(directory) / "second.py"
            report = write_file(first)
            write_file(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(report, verify_file(first))
            self.assertEqual(first.stat().st_mode & 0o777, 0o600)
            self.assertFalse(report["paper_authority_enabled"])
            self.assertFalse(report["broker_connection_verified"])
            self.assertFalse(report["runtime_configured"])

    def test_no_runtime_does_not_touch_host_or_broker(self):
        source = build_source()
        namespace = {"__name__": "__main__", "exchange": PoisonExchange(),
                     "Sleep": forbidden_call, "Log": forbidden_call,
                     "GetCommand": forbidden_call, "_G": forbidden_call}
        exec(compile(source, "gold2_au_simnow_single_file.py", "exec"), namespace)
        body = {"contract": "au26012", "action": "OPEN_LONG"}
        self.assertEqual(namespace["action_hash"](body), action_hash(body))
        with patch.object(namespace["sys"], "version_info", (3, 12, 14)), \
                self.assertRaisesRegex(namespace["PaperDenied"], "RUNTIME_NOT_CONFIGURED"):
            namespace["main"]()

    def test_bundled_entrypoint_denies_unsupported_python_before_host_lookup(self):
        namespace = {"__name__": "__main__"}
        exec(compile(build_source(), "gold2_au_simnow_single_file.py", "exec"), namespace)
        namespace.update({"GOLD2_SIMNOW_RUNTIME": PoisonExchange(),
                          "globals": forbidden_call, "Sleep": forbidden_call,
                          "Log": forbidden_call, "exchange": PoisonExchange()})
        with patch.object(namespace["sys"], "version_info", (3, 9, 2)), \
                self.assertRaisesRegex(namespace["PaperDenied"], "PYTHON_VERSION_UNSUPPORTED"):
            namespace["main"]()

    def test_tamper_and_overwrite_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.py"
            write_file(path)
            with self.assertRaisesRegex(SingleFileDenied, "OUTPUT_ALREADY_EXISTS"):
                write_file(path)
            path.write_bytes(path.read_bytes() + b"\n# unreviewed tail\n")
            with self.assertRaisesRegex(SingleFileDenied, "OUTPUT_DOES_NOT_MATCH_AUDITED_SOURCE"):
                verify_file(path)

    def test_symlink_and_source_drift_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            for relative in (CORE, ADAPTER, ACCOUNTING):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            self.assertEqual(build_source(root), build_source())
            changed = root / ADAPTER
            changed.write_bytes(changed.read_bytes() + b"\n# unreviewed change\n")
            with self.assertRaisesRegex(SingleFileDenied, "SOURCE_NOT_AUDITED_VERSION"):
                build_source(root)
            changed.unlink()
            changed.symlink_to(ROOT / ADAPTER)
            with self.assertRaisesRegex(SingleFileDenied, "SOURCE_MISSING_LINKED_OR_OUTSIDE_ROOT"):
                build_source(root)

    def test_pins_match_checked_in_source(self):
        import hashlib
        for relative in (CORE, ADAPTER, ACCOUNTING):
            with self.subTest(relative=relative):
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                                 AUDITED_SHA256[relative])


if __name__ == "__main__":
    unittest.main()
