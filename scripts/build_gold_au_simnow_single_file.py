#!/usr/bin/env python3
"""Stage one audited, credential-free YouQuant editor source file.

This flattens the frozen paper core and adapter without changing their logic.
It never supplies GOLD2_SIMNOW_RUNTIME, a PaperGrant, account credentials, or
broker access.  Dry-run is the default; execution writes a new private file.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = "src/yuanli_invest/gold_paper.py"
ADAPTER = "scripts/youquant_gold_simnow_strategy.py"
ACCOUNTING = "src/yuanli_invest/gold_au_strategy_accounting.py"
# A changed source must be reviewed and explicitly re-pinned.  This prevents a
# later unreviewed edit from silently becoming paste-ready strategy code.
AUDITED_SHA256 = {
    CORE: "c3d903d0e1eda8da8b7bea73be57d45af4be4848522d303d4f8d826117cb9289",
    ADAPTER: "b48b8dddefaf4299eaa04af21c422704a214968169a7aa335e0375ffb20040c2",
    ACCOUNTING: "1c268f4054327600153da26841218f41dedffa9f2496e8c63f6ecadb9873f8ad",
}
MAX_SOURCE_BYTES = 1_000_000


class SingleFileDenied(ValueError):
    """Fixed safe refusal reason; never include source or credentials."""


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_pinned(root: Path, relative: str) -> str:
    root = Path(root).resolve(strict=True)
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise SingleFileDenied("SOURCE_MISSING_LINKED_OR_OUTSIDE_ROOT")
    payload = path.read_bytes()
    if not payload or len(payload) > MAX_SOURCE_BYTES or _sha(payload) != AUDITED_SHA256[relative]:
        raise SingleFileDenied("SOURCE_NOT_AUDITED_VERSION")
    try:
        source = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SingleFileDenied("SOURCE_ENCODING_INVALID") from exc
    if source.encode("utf-8") != payload or "\r" in source:
        raise SingleFileDenied("SOURCE_ENCODING_INVALID")
    return source


def _defined_names(tree: ast.Module) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _strip_imports(source: str, *, core_exports: set[str], adapter: bool, accounting: bool = False) -> str:
    """Blank only known imports, preserving all other source lines verbatim."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    removed = set()
    found_core_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if node.level or [alias.name for alias in node.names] != ["annotations"]:
                raise SingleFileDenied("UNEXPECTED_FUTURE_IMPORT")
        elif isinstance(node, ast.ImportFrom) and node.module == "yuanli_invest.gold_paper":
            if not (adapter or accounting) or node.level or any(alias.asname or alias.name not in core_exports
                                                  for alias in node.names):
                raise SingleFileDenied("UNREVIEWED_CORE_IMPORT")
            found_core_import = True
        elif isinstance(node, ast.ImportFrom) and node.module == "yuanli_invest.gold_au_strategy_accounting":
            if adapter or accounting or node.level or [alias.name for alias in node.names] != ["validate_strategy_subledger_mark"]:
                raise SingleFileDenied("UNREVIEWED_ACCOUNTING_IMPORT")
        elif isinstance(node, ast.ImportFrom) and (node.level or (node.module or "").startswith("yuanli_invest")):
            raise SingleFileDenied("UNREVIEWED_LOCAL_IMPORT")
        elif isinstance(node, ast.Import) and any(alias.name.startswith("yuanli_invest")
                                                  for alias in node.names):
            raise SingleFileDenied("UNREVIEWED_LOCAL_IMPORT")
        else:
            continue
        removed.update(range(node.lineno, node.end_lineno + 1))
    if (adapter or accounting) and not found_core_import:
        raise SingleFileDenied("CORE_IMPORT_MISSING")
    return "".join("\n" if index in removed else line
                   for index, line in enumerate(lines, start=1))


def build_source(root: Path = ROOT) -> bytes:
    """Return exact audited bytes for one editor; no embedded authority."""
    core = _read_pinned(root, CORE)
    adapter = _read_pinned(root, ADAPTER)
    accounting = _read_pinned(root, ACCOUNTING)
    core_tree = ast.parse(core)
    adapter_tree = ast.parse(adapter)
    core_exports = _defined_names(core_tree)
    accounting_exports = _defined_names(ast.parse(accounting))
    if (core_exports & _defined_names(adapter_tree) or core_exports & accounting_exports
            or accounting_exports & _defined_names(adapter_tree)):
        raise SingleFileDenied("TOP_LEVEL_NAME_COLLISION")
    core_flat = _strip_imports(core, core_exports=core_exports, adapter=False)
    adapter_flat = _strip_imports(adapter, core_exports=core_exports, adapter=True)
    accounting_flat = _strip_imports(accounting, core_exports=core_exports, adapter=False, accounting=True)
    header = (
        "# GOLD2 AU SimNow staged single editor source; NOT DEPLOYED OR AUTHORIZED.\n"
        "# No credentials, PaperGrant, GOLD2_SIMNOW_RUNTIME or broker connection.\n"
        f"# core_sha256={AUDITED_SHA256[CORE]}\n"
        f"# adapter_sha256={AUDITED_SHA256[ADAPTER]}\n"
        f"# accounting_sha256={AUDITED_SHA256[ACCOUNTING]}\n"
        "from __future__ import annotations\n\n"
    )
    combined = (header + core_flat.rstrip("\n") + "\n\n" + accounting_flat.rstrip("\n") + "\n\n"
                + adapter_flat.rstrip("\n") + "\n").encode("utf-8")
    compile(combined, "gold2_au_simnow_single_file.py", "exec")
    return combined


def verify_file(path: Path, *, root: Path = ROOT) -> dict:
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise SingleFileDenied("OUTPUT_MISSING_OR_LINKED")
    expected = build_source(root)
    if path.stat().st_size != len(expected) or path.read_bytes() != expected:
        raise SingleFileDenied("OUTPUT_DOES_NOT_MATCH_AUDITED_SOURCE")
    return {"status": "SINGLE_FILE_VERIFIED_NOT_DEPLOYED",
            "sha256": "sha256:" + _sha(expected), "bytes": len(expected),
            "paper_authority_enabled": False, "broker_connection_verified": False,
            "runtime_configured": False}


def write_file(output: Path, *, root: Path = ROOT) -> dict:
    output = Path(output)
    if not output.is_absolute() or output.suffix != ".py":
        raise SingleFileDenied("OUTPUT_MUST_BE_ABSOLUTE_PY")
    if not output.parent.is_dir() or output.parent.is_symlink() or output.is_symlink():
        raise SingleFileDenied("OUTPUT_PARENT_INVALID")
    payload = build_source(root)
    try:
        descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SingleFileDenied("OUTPUT_ALREADY_EXISTS") from exc
    try:
        with os.fdopen(descriptor, "wb") as raw:
            raw.write(payload)
            raw.flush()
            os.fsync(raw.fileno())
        return verify_file(output, root=root)
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="write a new staged .py at --output")
    mode.add_argument("--verify", type=Path, help="verify an existing staged .py")
    parser.add_argument("--output", type=Path, help="absolute new .py path for --execute")
    args = parser.parse_args()
    if args.verify is not None:
        result = verify_file(args.verify)
    elif args.execute:
        if args.output is None:
            parser.error("--execute requires --output")
        result = write_file(args.output)
    else:
        payload = build_source()
        result = {"status": "DRY_RUN_NO_FILE_WRITTEN",
                  "sha256": "sha256:" + _sha(payload), "bytes": len(payload),
                  "paper_authority_enabled": False, "runtime_configured": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
