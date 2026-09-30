"""Credential-free, offline checks for the SimNow staging bundle."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.build_gold_au_simnow_bundle import (
    BundleDenied, SOURCES, _entry, build_bundle, source_bundle, verify_bundle,
)
from scripts import youquant_gold_simnow_preflight as preflight


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from yuanli_invest.gold_paper import PaperDenied  # noqa: E402
from scripts import youquant_gold_simnow_strategy as strategy  # noqa: E402


class PoisonExchange:
    def __getattribute__(self, name):
        raise AssertionError("preflight touched the exchange")


def forbidden_call(*args, **kwargs):
    raise AssertionError("preflight called a host API")


class BundlePreflightTests(unittest.TestCase):
    def test_bundle_is_deterministic_private_and_importable(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            report = build_bundle(first)
            build_bundle(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(report, verify_bundle(first))
            self.assertEqual(first.stat().st_mode & 0o777, 0o600)
            self.assertFalse(report["paper_authority_enabled"])
            self.assertFalse(report["broker_connection_verified"])
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(set(archive.namelist()), set(SOURCES) | {"deployment_manifest.json"})
                manifest = json.loads(archive.read("deployment_manifest.json"))
                self.assertFalse(manifest["credential_included"])
                self.assertFalse(manifest["paper_grant_included"])
            code = (
                "import sys; sys.path.insert(0, sys.argv[1]); "
                "import yuanli_invest.gold_paper; "
                "import youquant_gold_simnow_strategy; "
                "import youquant_gold_simnow_preflight; "
                "assert youquant_gold_simnow_preflight._module_spec_located('yuanli_invest.gold_paper'); "
                "print('IMPORT_OK')"
            )
            result = subprocess.run([sys.executable, "-c", code, str(first)],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "IMPORT_OK")

    def test_bundle_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.zip"
            build_bundle(path)
            with self.assertRaisesRegex(BundleDenied, "OUTPUT_ALREADY_EXISTS"):
                build_bundle(path)

    def test_bundle_rejects_tamper_and_unlisted_file(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.zip"
            build_bundle(original)
            with zipfile.ZipFile(original) as archive:
                entries = {name: archive.read(name) for name in archive.namelist()}
            tampered = Path(directory) / "tampered.zip"
            entries["yuanli_invest/gold_paper.py"] += b"\n# tampered\n"
            with zipfile.ZipFile(tampered, "w") as archive:
                for name, payload in entries.items():
                    archive.writestr(_entry(name), payload)
            with self.assertRaisesRegex(BundleDenied, "BUNDLE_SOURCE_HASH_MISMATCH"):
                verify_bundle(tampered)
            extra = Path(directory) / "extra.zip"
            with zipfile.ZipFile(extra, "w") as archive:
                for name, payload in entries.items():
                    archive.writestr(_entry(name), payload)
                archive.writestr(_entry("credentials.json"), b"{}")
            with self.assertRaisesRegex(BundleDenied, "BUNDLE_FILE_SET_MISMATCH"):
                verify_bundle(extra)

    def test_bundle_rejects_zip_comment_and_hidden_prefix_or_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.zip"
            build_bundle(original)
            canonical = original.read_bytes()
            # EOCD ends with a two-byte little-endian comment length.  The
            # central directory and all allowlisted source files stay intact.
            comment = b"hidden-credential-in-zip-comment"
            commented = Path(directory) / "commented.zip"
            commented.write_bytes(canonical[:-2] + len(comment).to_bytes(2, "little") + comment)
            with zipfile.ZipFile(commented) as archive:
                self.assertEqual(archive.comment, comment)
                self.assertEqual(set(archive.namelist()), set(SOURCES) | {"deployment_manifest.json"})
            with self.assertRaisesRegex(BundleDenied, "BUNDLE_BYTES_NOT_CANONICAL"):
                verify_bundle(commented)
            for label, candidate in (
                ("prefix", b"hidden-prefix" + canonical),
                ("suffix", canonical + b"hidden-suffix"),
            ):
                path = Path(directory) / (label + ".zip")
                path.write_bytes(candidate)
                with self.assertRaisesRegex(BundleDenied, "BUNDLE_BYTES_NOT_CANONICAL"):
                    verify_bundle(path)

    def test_bundle_refuses_linked_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in SOURCES.values():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            linked = root / SOURCES["yuanli_invest/gold_paper.py"]
            linked.unlink()
            linked.symlink_to(ROOT / SOURCES["yuanli_invest/gold_paper.py"])
            with self.assertRaisesRegex(BundleDenied, "SOURCE_MISSING_LINKED_OR_OUTSIDE_ROOT"):
                source_bundle(root)

    def test_bundle_rejects_source_drift_after_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            for relative in SOURCES.values():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            bundle = Path(directory) / "candidate.zip"
            build_bundle(bundle, root=root)
            changed = root / SOURCES["youquant_gold_simnow_preflight.py"]
            changed.write_bytes(changed.read_bytes() + b"\n# a new version\n")
            with self.assertRaisesRegex(BundleDenied, "BUNDLE_DOES_NOT_MATCH_CURRENT_SOURCE"):
                verify_bundle(bundle, source_root=root)

    def test_host_probe_never_invokes_host_or_broker_calls(self):
        symbols = {name: forbidden_call for name in preflight.REQUIRED_CALLABLES}
        symbols["exchange"] = PoisonExchange()
        with patch.object(preflight, "_module_spec_located", return_value=True):
            result = preflight.inspect_host(symbols)
        expected = ("HOST_SYMBOLS_PRESENT_UNVERIFIED" if sys.version_info >= (3, 12)
                    else "HOST_PREFLIGHT_BLOCKED")
        self.assertEqual(result["status"], expected)
        self.assertEqual(result["broker_api_calls"], 0)
        self.assertEqual(result["broker_api_calls_scope"], "THIS_PREFLIGHT_SCRIPT_ONLY")
        self.assertEqual(result["python_version"], "%s.%s.%s" % tuple(sys.version_info[:3]))
        self.assertTrue(all(result["module_spec_located"].values()))
        self.assertFalse(result["broker_identity_verified"])
        self.assertFalse(result["paper_authority_enabled"])
        self.assertFalse(result["module_upload_capability_verified"])

    def test_missing_symbol_or_injected_runtime_blocks_probe(self):
        symbols = {name: forbidden_call for name in preflight.REQUIRED_CALLABLES}
        symbols["exchange"] = PoisonExchange()
        with patch.object(preflight, "_module_spec_located", return_value=True):
            self.assertEqual(preflight.inspect_host({**symbols, "Sleep": None})["status"],
                             "HOST_PREFLIGHT_BLOCKED")
            self.assertFalse(preflight.inspect_host({**symbols, "exchange": False})
                             ["host_symbol_present"]["exchange"])
            self.assertEqual(preflight.inspect_host({**symbols, "GOLD2_SIMNOW_RUNTIME": object()})["status"],
                             "HOST_PREFLIGHT_BLOCKED")
        with patch.object(preflight, "_module_spec_located", return_value=False):
            self.assertEqual(preflight.inspect_host(symbols)["status"], "HOST_PREFLIGHT_BLOCKED")

    def test_module_spec_probe_does_not_import_parent_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "yuanli_invest"
            parent.mkdir()
            marker = root / "imported-parent.txt"
            (parent / "__init__.py").write_text(
                "open(%r, 'w').write('imported')\n" % str(marker), encoding="utf-8")
            (parent / "gold_paper.py").write_text("raise RuntimeError('child imported')\n", encoding="utf-8")
            with patch.object(sys, "path", [str(root), *sys.path]):
                self.assertTrue(preflight._module_spec_located("yuanli_invest.gold_paper"))
            self.assertFalse(marker.exists())

    def test_preflight_can_run_as_single_editor_file_without_broker_calls(self):
        logs = []
        namespace = {"__name__": "__main__",
                     "exchange": PoisonExchange(),
                     "GetCommand": forbidden_call,
                     "_G": forbidden_call,
                     "Sleep": forbidden_call,
                     "Log": lambda *items: logs.append(items)}
        source = (ROOT / "scripts" / "youquant_gold_simnow_preflight.py").read_text()
        tree = ast.parse(source)
        self.assertNotIn("from __future__", source)
        self.assertFalse(any(isinstance(node, (ast.AnnAssign, ast.JoinedStr))
                             or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                             and (node.returns is not None
                                  or any(arg.annotation is not None for arg in
                                         (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)))
                             for node in ast.walk(tree)))
        exec(compile(source, "youquant_gold_simnow_preflight.py", "exec"), namespace)
        self.assertEqual(logs, [])  # platform, not module loading, calls main once
        report = namespace["main"]()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "GOLD2_SIMNOW_READ_ONLY_PREFLIGHT")
        self.assertEqual(json.loads(logs[0][1]), report)
        self.assertEqual(report["broker_api_calls"], 0)
        self.assertFalse(report["paper_authority_enabled"])

    def test_strategy_entrypoint_without_runtime_never_touches_exchange(self):
        with patch.object(strategy.sys, "version_info", (3, 12, 14)), \
                patch.dict(strategy.__dict__, {"GOLD2_SIMNOW_RUNTIME": None,
                                            "Sleep": forbidden_call,
                                            "Log": forbidden_call,
                                            "exchange": PoisonExchange()}):
            with self.assertRaisesRegex(PaperDenied, "RUNTIME_NOT_CONFIGURED"):
                strategy.main()

    def test_unsupported_python_denies_before_injected_runtime_lookup(self):
        class ExplodingRuntime(strategy.GoldSimNowRuntime):
            def __getattribute__(self, name):
                raise AssertionError("unsupported host touched injected runtime")

        runtime = object.__new__(ExplodingRuntime)
        for version in ((3, 9, 2), (3, 11, 14)):
            with self.subTest(version=version), \
                    patch.object(strategy.sys, "version_info", version), \
                    patch.object(strategy, "serve") as serve, \
                    patch.dict(strategy.__dict__, {
                        "GOLD2_SIMNOW_RUNTIME": runtime,
                        "globals": forbidden_call,
                        "Sleep": forbidden_call,
                        "Log": forbidden_call,
                        "exchange": PoisonExchange(),
                    }):
                with self.assertRaisesRegex(PaperDenied, "PYTHON_VERSION_UNSUPPORTED"):
                    strategy.main()
                serve.assert_not_called()

    def test_supported_python_preserves_runtime_dispatch(self):
        from types import SimpleNamespace
        from scripts.gold_au_runtime_bootstrap import ProductionGoldSimNowRuntime
        runtime = object.__new__(ProductionGoldSimNowRuntime)
        runtime.bridge = SimpleNamespace(account_coordinator=object(), atomic_claim=None,
            required_equity_scope="SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1", receipt_validation_clock=lambda: None)
        with patch.object(strategy.sys, "version_info", (3, 12, 14)), \
                patch.object(strategy, "serve") as serve, \
                patch.dict(strategy.__dict__, {
                    "GOLD2_SIMNOW_RUNTIME": runtime,
                    "Sleep": forbidden_call,
                    "Log": forbidden_call,
                    "exchange": PoisonExchange(),
                }):
            strategy.main()
            serve.assert_called_once_with(runtime, forbidden_call, forbidden_call)

    def test_supported_python_denies_legacy_or_incomplete_production_wiring(self):
        runtime = object.__new__(strategy.GoldSimNowRuntime)
        with patch.object(strategy.sys, "version_info", (3, 12, 14)), \
                patch.object(strategy, "serve") as serve, \
                patch.dict(strategy.__dict__, {"GOLD2_SIMNOW_RUNTIME": runtime,
                    "Sleep": forbidden_call, "Log": forbidden_call}):
            with self.assertRaisesRegex(PaperDenied, "PRODUCTION_V2_FACTORY_REQUIRED"):
                strategy.main()
            serve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
