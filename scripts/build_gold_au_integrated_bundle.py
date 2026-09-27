#!/usr/bin/env python3
"""Build an explicitly reviewed, inert, namespaced YouQuant editor candidate.

The audit manifest is mandatory and is never inferred from whatever source is
present at first run. AUDIT_APPROVED approves bytes only; the generated file
contains no grant, runtime instance, account configuration or credentials.
"""
from __future__ import annotations
import argparse
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATHS = {
    "yuanli_invest.gold_paper": "src/yuanli_invest/gold_paper.py",
    "yuanli_invest.gold_au_strategy_accounting": "src/yuanli_invest/gold_au_strategy_accounting.py",
    "yuanli_invest.gold_au_account_coordinator": "src/yuanli_invest/gold_au_account_coordinator.py",
    "yuanli_invest.gold_au_broker_facts": "src/yuanli_invest/gold_au_broker_facts.py",
    "yuanli_invest.gold_au_receipt_client": "src/yuanli_invest/gold_au_receipt_client.py",
    "scripts.youquant_gold_simnow_strategy": "scripts/youquant_gold_simnow_strategy.py",
    "scripts.gold_au_runtime_bootstrap": "scripts/gold_au_runtime_bootstrap.py",
    "scripts.gold_au_engineering_bootstrap": "scripts/gold_au_engineering_bootstrap.py",
    "yuanli_invest.gold_au_control_admission": "src/yuanli_invest/gold_au_control_admission.py",
}
MAX_SOURCE = 1_000_000
MAX_MANIFEST = 32_000
SAFE_CALLS = {"ZoneInfo", "Decimal", "timedelta", "frozenset", "re.compile", "dataclass"}


class IntegratedBundleDenied(ValueError):
    pass


def _bounded_file(path: Path, limit: int) -> bytes:
    descriptor = None
    try:
        if not path.is_absolute() or path.is_symlink():
            raise IntegratedBundleDenied("ABSOLUTE_UNLINKED_FILE_REQUIRED")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit or info.st_nlink != 1:
            raise IntegratedBundleDenied("REGULAR_BOUNDED_SINGLE_LINK_FILE_REQUIRED")
        payload = os.read(descriptor, limit + 1)
        if len(payload) != info.st_size:
            raise IntegratedBundleDenied("SOURCE_CHANGED_DURING_READ")
        return payload
    except OSError:
        raise IntegratedBundleDenied("SOURCE_OR_MANIFEST_UNAVAILABLE") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _safe_expression(node: ast.AST | None) -> None:
    if node is None or isinstance(node, ast.Lambda):
        return
    for child in ast.walk(node):
        if isinstance(child, (ast.NamedExpr, ast.Await, ast.Yield, ast.YieldFrom, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            raise IntegratedBundleDenied("IMPORT_TIME_DYNAMIC_EXPRESSION_DENIED")
        if isinstance(child, ast.Call) and ast.unparse(child.func) not in SAFE_CALLS:
            raise IntegratedBundleDenied("IMPORT_TIME_CALL_NOT_AUDITED")


def _validate_ast(source: str, module_name: str) -> None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise IntegratedBundleDenied("SOURCE_AST_INVALID") from None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for value in [*node.decorator_list, *node.args.defaults, *node.args.kw_defaults]:
                _safe_expression(value)
            continue
        if isinstance(node, ast.ClassDef):
            for value in [*node.bases, *node.decorator_list, *(item.value for item in node.keywords)]:
                _safe_expression(value)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for value in [*child.decorator_list, *child.args.defaults, *child.args.kw_defaults]:
                        _safe_expression(value)
                elif isinstance(child, (ast.Assign, ast.AnnAssign)):
                    _safe_expression(child.value)
                elif not (isinstance(child, ast.Pass) or isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant)):
                    raise IntegratedBundleDenied("IMPORT_TIME_CLASS_STARTUP_DENIED")
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(not isinstance(target, ast.Name) for target in targets):
                raise IntegratedBundleDenied("IMPORT_TIME_STATE_MUTATION_DENIED")
            if any(target.id in {"GOLD2_SIMNOW_RUNTIME", "signing_key", "runtime", "grant", "exchange", "Sleep", "Log"} for target in targets):
                raise IntegratedBundleDenied("EMBEDDED_AUTHORITY_CONFIGURATION_DENIED")
            _safe_expression(node.value)
            continue
        raise IntegratedBundleDenied("IMPORT_TIME_STARTUP_DENIED")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level != 1:
                    raise IntegratedBundleDenied("LOCAL_IMPORT_OUTSIDE_BUNDLE")
                modules = [module_name.rsplit(".", 1)[0] + "." + (node.module or "")]
            else:
                modules = [node.module or ""]
        else:
            continue
        for name in modules:
            if name == "__future__":
                continue
            if name.startswith(("yuanli_invest", "scripts")):
                if name not in MODULE_PATHS:
                    raise IntegratedBundleDenied("LOCAL_IMPORT_OUTSIDE_BUNDLE")
            elif (name.split(".", 1)[0] not in sys.stdlib_module_names
                    and not (module_name == "yuanli_invest.gold_au_control_admission"
                             and name in {"cryptography.hazmat.primitives.asymmetric.ed25519", "cryptography.exceptions"})):
                raise IntegratedBundleDenied("NON_STDLIB_IMPORT_DENIED")
    compile(source, module_name, "exec")


def read_audit_manifest(path: Path) -> tuple[dict, str]:
    raw = _bounded_file(Path(path), MAX_MANIFEST)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise IntegratedBundleDenied("MANIFEST_DUPLICATE_KEYS")
            result[key] = value
        return result
    try:
        manifest = json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, UnicodeError):
        raise IntegratedBundleDenied("MANIFEST_JSON_INVALID") from None
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "status", "audit_id", "runtime_configured", "deployment_verified", "modules"}
            or manifest.get("schema_version") != "gold-au-integrated-source-audit.v1"
            or manifest.get("status") != "AUDIT_APPROVED"
            or manifest.get("runtime_configured") is not False or manifest.get("deployment_verified") is not False
            or not isinstance(manifest.get("audit_id"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", manifest["audit_id"])
            or not isinstance(manifest.get("modules"), dict) or set(manifest["modules"]) != set(MODULE_PATHS)):
        raise IntegratedBundleDenied("EXPLICIT_APPROVED_SOURCE_AUDIT_REQUIRED")
    for name, relative in MODULE_PATHS.items():
        entry = manifest["modules"][name]
        if (not isinstance(entry, dict) or set(entry) != {"path", "sha256"} or entry.get("path") != relative
                or not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
            raise IntegratedBundleDenied("AUDIT_SOURCE_PIN_SHAPE_INVALID")
    return manifest, hashlib.sha256(raw).hexdigest()


def build_source(manifest_path: Path, *, root: Path = ROOT) -> bytes:
    if sys.version_info < (3, 12):
        raise IntegratedBundleDenied("PYTHON_VERSION_UNSUPPORTED")
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise IntegratedBundleDenied("SOURCE_ROOT_INVALID")
    root = root.resolve(strict=True)
    manifest, manifest_hash = read_audit_manifest(manifest_path)
    embedded = {}
    for name, relative in sorted(MODULE_PATHS.items()):
        path = root / relative
        if not path.resolve().is_relative_to(root) or any(parent.is_symlink() for parent in path.parents if parent != root and parent.is_relative_to(root)):
            raise IntegratedBundleDenied("SOURCE_PARENT_LINKED_OR_OUTSIDE_ROOT")
        raw = _bounded_file(path, MAX_SOURCE)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest["modules"][name]["sha256"]:
            raise IntegratedBundleDenied("SOURCE_DRIFT_FROM_APPROVED_PIN")
        try:
            source = raw.decode("utf-8", "strict")
        except UnicodeError:
            raise IntegratedBundleDenied("SOURCE_ENCODING_INVALID") from None
        if "\r" in source or source.startswith("\ufeff"):
            raise IntegratedBundleDenied("SOURCE_ENCODING_INVALID")
        _validate_ast(source, name)
        embedded[name] = {"path": relative, "sha256": digest, "source_b64": base64.b64encode(raw).decode("ascii")}
    literal = repr(embedded)
    header = f'''#!/opt/yuanli-gold2-runtime/python312
# GOLD2 integrated audited source candidate; not deployed or authorized.
# source_audit_sha256={manifest_hash}
import sys as _gold2_sys
if _gold2_sys.version_info < (3, 12):
    raise RuntimeError("PYTHON_VERSION_UNSUPPORTED")
import base64 as _gold2_base64
import hashlib as _gold2_hashlib
import importlib.abc as _gold2_import_abc
import importlib.util as _gold2_import_util
import types as _gold2_types
_GOLD2_BUNDLE_SOURCES = {literal}
_GOLD2_BUNDLE_AUDIT_SHA256 = "{manifest_hash}"
_gold2_names = set(_GOLD2_BUNDLE_SOURCES) | {{"yuanli_invest", "scripts"}}
if any(name in _gold2_sys.modules for name in _gold2_names):
    raise RuntimeError("BUNDLE_MODULE_NAMESPACE_ALREADY_BOUND")

class _Gold2AuditedLoader(_gold2_import_abc.MetaPathFinder, _gold2_import_abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in _GOLD2_BUNDLE_SOURCES:
            return _gold2_import_util.spec_from_loader(fullname, self, origin="gold2-audited-static-source")
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        item = _GOLD2_BUNDLE_SOURCES[module.__name__]
        raw = _gold2_base64.b64decode(item["source_b64"], validate=True)
        if _gold2_hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise RuntimeError("BUNDLE_SOURCE_HASH_MISMATCH")
        module.__file__ = "/gold2-audited-bundle/" + item["path"]
        exec(compile(raw, module.__file__, "exec"), module.__dict__)

for _gold2_package_name in ("yuanli_invest", "scripts"):
    _gold2_package = _gold2_types.ModuleType(_gold2_package_name)
    _gold2_package.__path__ = []
    _gold2_package.__package__ = _gold2_package_name
    _gold2_package.__spec__ = _gold2_import_util.spec_from_loader(_gold2_package_name, loader=None, is_package=True)
    _gold2_sys.modules[_gold2_package_name] = _gold2_package
_gold2_loader = _Gold2AuditedLoader()
_gold2_sys.meta_path.insert(0, _gold2_loader)
try:
    for _gold2_module_name in sorted(_GOLD2_BUNDLE_SOURCES):
        __import__(_gold2_module_name)
finally:
    _gold2_sys.meta_path.remove(_gold2_loader)
_gold2_core = _gold2_sys.modules["yuanli_invest.gold_paper"]
_gold2_strategy = _gold2_sys.modules["scripts.youquant_gold_simnow_strategy"]
_gold2_bootstrap = _gold2_sys.modules["scripts.gold_au_runtime_bootstrap"]
_gold2_engineering = _gold2_sys.modules["scripts.gold_au_engineering_bootstrap"]

def engineering_main():
    # Separate entry; a production runtime never becomes engineering by a flag.
    _gold2_runtime = globals().get("GOLD2_ENGINEERING_RUNTIME")
    return _gold2_engineering.serve_engineering(_gold2_runtime, globals().get("Sleep"), globals().get("Log"))

def main():
    # An external program must independently construct and authorize runtime.
    _gold2_runtime = globals().get("GOLD2_SIMNOW_RUNTIME")
    if _gold2_runtime is None:
        raise _gold2_core.PaperDenied("RUNTIME_NOT_CONFIGURED")
    _gold2_strategy.GOLD2_SIMNOW_RUNTIME = _gold2_runtime
    _gold2_strategy.Sleep = globals().get("Sleep")
    _gold2_strategy.Log = globals().get("Log")
    return _gold2_strategy.main()
'''
    result = header.encode("utf-8")
    compile(result, "gold2_integrated_audited_candidate.py", "exec")
    return result


def write_file(output: Path, manifest_path: Path, *, root: Path = ROOT) -> dict:
    output = Path(output)
    if (not output.is_absolute() or output.suffix != ".py" or not output.parent.is_dir()
            or output.parent.is_symlink() or output.is_symlink()):
        raise IntegratedBundleDenied("NEW_PRIVATE_PY_OUTPUT_REQUIRED")
    parent = output.parent.stat()
    if parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700:
        raise IntegratedBundleDenied("PRIVATE_OUTPUT_PARENT_REQUIRED")
    payload = build_source(manifest_path, root=root)
    try:
        descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError:
        raise IntegratedBundleDenied("OUTPUT_ALREADY_EXISTS_OR_UNAVAILABLE") from None
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload); stream.flush(); os.fsync(stream.fileno())
    return {"status": "INTEGRATED_SOURCE_CANDIDATE_WRITTEN_NOT_DEPLOYED", "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload), "source_audit_approved": True, "runtime_configured": False,
            "broker_authority_embedded": False, "deployment_verified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.execute:
            if args.output is None:
                raise IntegratedBundleDenied("EXPLICIT_OUTPUT_REQUIRED")
            result = write_file(args.output, args.manifest)
        else:
            payload = build_source(args.manifest)
            result = {"status": "DRY_RUN_INTEGRATED_SOURCE_NOT_WRITTEN", "bytes": len(payload),
                      "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(), "runtime_configured": False,
                      "broker_authority_embedded": False, "deployment_verified": False}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (IntegratedBundleDenied, OSError) as exc:
        print(json.dumps({"status": "DENIED", "reason": str(exc) if isinstance(exc, IntegratedBundleDenied) else "FILESYSTEM_UNAVAILABLE"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
