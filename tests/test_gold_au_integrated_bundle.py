"""Synthetic audit fixtures; no deployment, credentials or broker calls."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from scripts.build_gold_au_integrated_bundle import (ROOT, MODULE_PATHS, IntegratedBundleDenied,
    build_source, write_file)


class IntegratedBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name) / "fixture-root"
        self.root.mkdir(mode=0o700)
        modules = {}
        for name, relative in MODULE_PATHS.items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
            modules[name] = {"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
        self.manifest = Path(self.temp.name) / "audit.json"
        self.audit = {"schema_version": "gold-au-integrated-source-audit.v1", "status": "AUDIT_APPROVED",
                      "audit_id": "SYNTHETIC-TEST-ONLY", "runtime_configured": False,
                      "deployment_verified": False, "modules": modules}
        self.save_manifest()

    def tearDown(self):
        self.temp.cleanup()

    def save_manifest(self):
        self.manifest.write_text(json.dumps(self.audit, sort_keys=True))

    def payload(self):
        return build_source(self.manifest, root=self.root)

    def subprocess_check(self, prelude: str, checks: str) -> subprocess.CompletedProcess:
        path = Path(self.temp.name) / "candidate.py"
        path.write_bytes(self.payload())
        code = "import sys,json\n" + prelude + "\nsource=open(sys.argv[1],'rb').read()\nnamespace={}\n" + checks
        return subprocess.run([sys.executable, "-I", "-c", code, str(path)], capture_output=True, text=True, timeout=15, check=False)

    def test_compilation_determinism_and_explicit_audit_hash(self):
        first = self.payload()
        self.assertEqual(first, self.payload())
        compile(first, "candidate.py", "exec")
        self.assertIn(hashlib.sha256(self.manifest.read_bytes()).hexdigest().encode(), first)
        tree = ast.parse(first)
        self.assertFalse(any(isinstance(node, ast.If) and any(isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                            and child.func.id == "main" for child in ast.walk(node)) for node in tree.body))

    def test_actual_modules_import_without_host_calls_and_none_runtime_inert(self):
        checks = '''calls=[]
def forbidden(*args,**kwargs):
    calls.append("HOST")
    raise AssertionError("host called")
namespace.update({name:forbidden for name in ("GetCommand","_G","Sleep","Log","exchange","Buy","Sell","CancelOrder")})
namespace["GOLD2_SIMNOW_RUNTIME"]=None
exec(compile(source,"candidate.py","exec"),namespace)
from scripts import gold_au_runtime_bootstrap as boot
from scripts import youquant_gold_simnow_strategy as strategy
from yuanli_invest import gold_paper as core
assert callable(boot.build_runtime)
assert boot.YouQuantBridge is strategy.YouQuantBridge
assert strategy.PaperLedger is core.PaperLedger
assert "GOLD2_SIMNOW_RUNTIME" not in strategy.__dict__
try:
    namespace["main"]()
except core.PaperDenied as error:
    assert error.code=="RUNTIME_NOT_CONFIGURED"
else:
    raise AssertionError("main started")
assert calls==[]
print("IMPORT_AND_NONE_RUNTIME_INERT_PASS")
'''
        result = self.subprocess_check("", checks)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INERT_PASS", result.stdout)

    def test_namespaces_isolate_time_helpers_and_global_dicts(self):
        checks = '''exec(compile(source,"candidate.py","exec"),namespace)
from yuanli_invest import gold_paper as core
from yuanli_invest import gold_au_broker_facts as facts
from yuanli_invest import gold_au_receipt_client as receipts
from scripts import youquant_gold_simnow_strategy as strategy
assert core.__dict__ is not facts.__dict__
assert receipts.__dict__ is not strategy.__dict__
assert core._time.__module__=="yuanli_invest.gold_paper"
assert receipts._instant.__module__=="yuanli_invest.gold_au_receipt_client"
assert strategy.YouQuantBridge.__module__=="scripts.youquant_gold_simnow_strategy"
assert core.PaperGrant.__module__=="yuanli_invest.gold_paper"
print("NAMESPACE_ISOLATION_PASS")
'''
        result = self.subprocess_check("", checks)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_python39_guard_precedes_decode_import_and_host_callbacks(self):
        checks = '''calls=[]
def forbidden(*args,**kwargs):
    calls.append("HOST")
    raise AssertionError("host called")
namespace.update({name:forbidden for name in ("GetCommand","_G","Sleep","Log","exchange")})
sys.version_info=(3,9,2)
try:
    exec(compile(source,"candidate.py","exec"),namespace)
except RuntimeError as error:
    assert str(error)=="PYTHON_VERSION_UNSUPPORTED"
else:
    raise AssertionError("older interpreter loaded")
assert calls==[]
assert "yuanli_invest" not in sys.modules
assert "scripts" not in sys.modules
assert "_GOLD2_BUNDLE_SOURCES" not in namespace
print("PYTHON39_GUARD_PASS")
'''
        result = self.subprocess_check("", checks)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_module_namespace_not_overwritten(self):
        checks = '''import types
sentinel=types.ModuleType("yuanli_invest")
sys.modules["yuanli_invest"]=sentinel
try:
    exec(compile(source,"candidate.py","exec"),namespace)
except RuntimeError as error:
    assert str(error)=="BUNDLE_MODULE_NAMESPACE_ALREADY_BOUND"
else:
    raise AssertionError("namespace overwritten")
assert sys.modules["yuanli_invest"] is sentinel
print("EXISTING_NAMESPACE_REJECTED")
'''
        result = self.subprocess_check("", checks)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_drift_and_symlink_refused(self):
        path = self.root / MODULE_PATHS["yuanli_invest.gold_paper"]
        path.write_bytes(path.read_bytes() + b"\n# unreviewed drift\n")
        with self.assertRaisesRegex(IntegratedBundleDenied, "SOURCE_DRIFT"): self.payload()
        path.unlink(); path.symlink_to(ROOT / MODULE_PATHS["yuanli_invest.gold_paper"])
        with self.assertRaises(IntegratedBundleDenied): self.payload()

    def test_manifest_symlink_unapproved_or_unknown_source_refused(self):
        self.audit["status"] = "WAIT_FINAL_PIN"; self.save_manifest()
        with self.assertRaisesRegex(IntegratedBundleDenied, "EXPLICIT_APPROVED"): self.payload()
        self.audit["status"] = "AUDIT_APPROVED"
        self.audit["modules"]["malicious.module"] = {"path": "malicious.py", "sha256": "0" * 64}
        self.save_manifest()
        with self.assertRaises(IntegratedBundleDenied): self.payload()
        linked = self.manifest.with_name("link.json"); linked.symlink_to(self.manifest)
        with self.assertRaises(IntegratedBundleDenied): build_source(linked, root=self.root)

    def test_audited_hash_does_not_allow_startup_or_nonstdlib_import(self):
        name = "scripts.gold_au_runtime_bootstrap"
        path = self.root / MODULE_PATHS[name]
        original = path.read_text()
        for appended, code in (("\nmain()\n", "IMPORT_TIME_STARTUP_DENIED"),
                               ("\nimport requests\n", "NON_STDLIB_IMPORT_DENIED"),
                               ("\nruntime = object()\n", "EMBEDDED_AUTHORITY_CONFIGURATION_DENIED")):
            path.write_text(original + appended)
            self.audit["modules"][name]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.save_manifest()
            with self.subTest(code=code), self.assertRaisesRegex(IntegratedBundleDenied, code): self.payload()

    def test_private_output_no_overwrite_and_no_implicit_write(self):
        output = Path(self.temp.name) / "candidate.py"
        self.payload()
        self.assertFalse(output.exists())
        receipt = write_file(output, self.manifest, root=self.root)
        self.assertFalse(receipt["runtime_configured"])
        self.assertFalse(receipt["deployment_verified"])
        self.assertEqual(receipt["sha256"], "sha256:" + hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(IntegratedBundleDenied): write_file(output, self.manifest, root=self.root)


if __name__ == "__main__": unittest.main()
