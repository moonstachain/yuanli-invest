"""The cloud core diagnostic is exact, read-only, and Python 3.9 compatible."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.build_gold_au_simnow_core_dryrun import (
    DIAGNOSTIC_TAIL, build_diagnostic_source, write_diagnostic,
)
from scripts.build_gold_au_simnow_single_file import build_source


class PoisonExchange:
    def __getattribute__(self, name):
        raise AssertionError("diagnostic touched broker method: " + name)


def forbidden(*args, **kwargs):
    raise AssertionError("diagnostic touched command or host persistence")


class CoreDryRunTests(unittest.TestCase):
    def test_diagnostic_entrypoint_has_no_broker_or_command_reference(self):
        tree = ast.parse(DIAGNOSTIC_TAIL)
        entrypoint = next(node for node in tree.body
                          if isinstance(node, ast.FunctionDef) and node.name == "main")
        names = {node.id for node in ast.walk(entrypoint) if isinstance(node, ast.Name)}
        attributes = {node.attr for node in ast.walk(entrypoint)
                      if isinstance(node, ast.Attribute)}
        self.assertFalse(names & {"exchange", "GetCommand", "_G", "PaperGrant"})
        self.assertFalse(attributes & {"Buy", "Sell", "CancelOrder", "GetAccount",
                                       "GetPositions", "GetOrders", "GetTicker"})

    def _run(self, **extra):
        logs = []
        namespace = {
            "__name__": "__main__",
            "exchange": PoisonExchange(),
            "GetCommand": forbidden,
            "_G": forbidden,
            "Sleep": forbidden,
            "Log": lambda *parts: logs.append(parts),
        }
        namespace.update(extra)
        source = build_diagnostic_source()
        exec(compile(source, "gold2_au_simnow_core_dryrun.py", "exec"), namespace)
        report = namespace["main"]()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "GOLD2_SIMNOW_CORE_DRYRUN")
        return report

    def test_pure_core_runs_without_host_or_broker_calls(self):
        report = self._run()
        self.assertEqual(report["status"], "CORE_PURE_FUNCTIONS_OBSERVED")
        self.assertEqual(report["reason_code"], "NONE")
        self.assertEqual(report["broker_api_calls"], 0)
        self.assertEqual(report["order_api_calls"], 0)
        self.assertFalse(report["paper_authority_enabled"])
        self.assertFalse(report["broker_connection_verified"])
        self.assertEqual(report["bundle_sha256"],
                         "sha256:" + hashlib.sha256(build_source()).hexdigest())

    def test_injected_runtime_denied_without_invocation(self):
        report = self._run(GOLD2_SIMNOW_RUNTIME=PoisonExchange())
        self.assertEqual(report["status"], "CORE_DRYRUN_BLOCKED")
        self.assertEqual(report["reason_code"], "UNEXPECTED_RUNTIME_PRESENT")
        self.assertEqual(report["order_api_calls"], 0)

    def test_private_exact_output_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagnostic.py"
            result = write_diagnostic(path)
            self.assertEqual(path.read_bytes(), build_diagnostic_source())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(result["status"], "CORE_DRYRUN_STAGED_NOT_DEPLOYED")
            with self.assertRaises(FileExistsError):
                write_diagnostic(path)


if __name__ == "__main__":
    unittest.main()
