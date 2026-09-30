#!/usr/bin/env python3
"""Prepare a content-addressed non-Desktop GOLD2 release candidate and plists.

Default is read-only inventory. --stage copies reviewed Git code and the existing
venv to a private release. It never installs/loads plist files or runs a worker.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
WORKERS = (
    ("0805-shfe-archive", "gold_au_shfe_archive_worker.py", "install_gold_au_shfe_archive_schedule", 8, 5),
    ("0810-macro-capture", "gold_macro_daily_worker.py", "install_gold_macro_capture_schedule", 8, 10),
    ("0825-request-assembly", "gold_au_daily_request.py", "install_gold_au_daily_request_schedule", 8, 25),
    ("0830-research-decision", "gold_au_decision_worker.py", "install_gold_au_decision_schedule", 8, 30),
)
LOG_FILES = {
    "0805-shfe-archive": ("shfe_stdout.log", "shfe_stderr.log"),
    "0810-macro-capture": ("macro_stdout.log", "macro_stderr.log"),
    "0825-request-assembly": ("request_assembly_stdout.log", "request_assembly_stderr.log"),
    "0830-research-decision": ("stdout.log", "stderr.log"),
}
EXCLUDE = {"__pycache__", ".DS_Store"}
SENSITIVE_NAMES = {".env", ".netrc", ".pypirc", "pip.conf", "credentials.json", "id_rsa", "id_ed25519"}


class ReleaseDenied(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.DEVNULL)


def _is_desktop(path: Path) -> bool:
    return path.absolute().is_relative_to(Path.home() / "Desktop")


def check_release_base(base: Path) -> Path:
    if ".." in base.parts:
        raise ReleaseDenied("RELEASE_PATH_TRAVERSAL")
    base = base.expanduser().absolute()
    if base != base.resolve(strict=False):
        raise ReleaseDenied("NONCANONICAL_RELEASE_BASE")
    if _is_desktop(base) or base.is_relative_to(ROOT) or base == Path.home():
        raise ReleaseDenied("RELEASE_MUST_BE_PRIVATE_NON_DESKTOP")
    if not base.is_relative_to(Path.home() / ".yuanli" / "releases"):
        raise ReleaseDenied("RELEASE_BASE_NOT_ALLOWLISTED")
    current = base
    while current != Path.home() and current != current.parent:
        if current.is_symlink():
            raise ReleaseDenied("SYMLINK_RELEASE_PARENT")
        current = current.parent
    return base


def check_private_runtime(runtime: Path) -> Path:
    if ".." in runtime.parts:
        raise ReleaseDenied("RUNTIME_PATH_TRAVERSAL")
    runtime = runtime.expanduser().absolute()
    if (runtime != runtime.resolve(strict=False) or _is_desktop(runtime)
            or not runtime.is_relative_to(Path.home() / ".yuanli/runtime")):
        raise ReleaseDenied("RUNTIME_OUTSIDE_PRIVATE_NONDESKTOP_ROOT")
    current = runtime
    while current != Path.home() and current != current.parent:
        if current.is_symlink():
            raise ReleaseDenied("SYMLINK_RUNTIME_PARENT")
        current = current.parent
    if (not runtime.is_dir() or runtime.stat().st_uid != os.getuid()
            or stat.S_IMODE(runtime.stat().st_mode) != 0o700):
        raise ReleaseDenied("PRIVATE_RUNTIME_REQUIRED_FOR_RENDER")
    return runtime


def _private_directory(path: Path) -> None:
    # ~/.yuanli predates this tool and can be 0755. Do not change its mode or
    # any unrelated state; all new release directories below it are private.
    boundary = Path.home() / ".yuanli"
    if path == boundary:
        if (path.is_symlink() or not path.is_dir() or path.stat().st_uid != os.getuid()
                or stat.S_IMODE(path.stat().st_mode) & 0o022):
            raise ReleaseDenied("INSECURE_YUANLI_PARENT")
        return
    if not path.is_relative_to(boundary):
        raise ReleaseDenied("RELEASE_DIRECTORY_OUTSIDE_ALLOWLIST")
    if path.exists():
        if path.is_symlink() or not path.is_dir() or path.stat().st_uid != os.getuid() or stat.S_IMODE(path.stat().st_mode) != 0o700:
            raise ReleaseDenied("INSECURE_RELEASE_DIRECTORY")
    else:
        _private_directory(path.parent)
        path.mkdir(mode=0o700)


def _code_inventory() -> tuple[str, list[tuple[str, bytes]], str]:
    # An untracked private file under scripts/src must not silently enter a release.
    status = _git("status", "--porcelain=v1", "--untracked-files=all", "--", "scripts", "src", "pyproject.toml")
    if status:
        raise ReleaseDenied("SOURCE_NOT_CLEAN_GIT")
    names = [x.decode() for x in _git("ls-files", "-z", "--", "scripts", "src", "pyproject.toml").split(b"\0") if x]
    if not names or not all(x.startswith(("scripts/", "src/")) or x == "pyproject.toml" for x in names):
        raise ReleaseDenied("INVALID_GIT_SOURCE_INVENTORY")
    rows = []
    for name in sorted(names):
        path = ROOT / name
        if path.is_symlink() or not path.is_file() or path.name in SENSITIVE_NAMES:
            raise ReleaseDenied("UNSAFE_GIT_SOURCE_FILE")
        rows.append((name, path.read_bytes()))
    git_head = _git("rev-parse", "HEAD").decode().strip()
    inventory_hash = sha(json.dumps([(name, sha(data)) for name, data in rows], separators=(",", ":")).encode())
    return git_head, rows, inventory_hash


def _safe_venv_files(venv: Path) -> list[Path]:
    if venv.is_symlink() or not venv.is_dir():
        raise ReleaseDenied("MISSING_OR_SYMLINK_VENV")
    rows = []
    for path in sorted(venv.rglob("*")):
        if path.name in EXCLUDE or path.suffix == ".pyc" or any(p in EXCLUDE for p in path.relative_to(venv).parts):
            continue
        if path.name in SENSITIVE_NAMES:
            raise ReleaseDenied("SENSITIVE_FILE_IN_VENV")
        if path.is_symlink():
            _validate_venv_symlink(path, venv)
        elif not path.is_file() and not path.is_dir():
            raise ReleaseDenied("SPECIAL_FILE_IN_VENV")
        if path.is_file() and not path.is_symlink():
            rows.append(path)
    return rows


def _validate_venv_symlink(path: Path, venv: Path) -> None:
    target = path.resolve(strict=True)
    if _is_desktop(target):
        raise ReleaseDenied("DESKTOP_SYMLINK_IN_VENV")
    if target.is_relative_to(venv):
        return
    # The only external venv links are the three Python launcher names. A
    # symlink to a private file elsewhere would survive the copy by reference.
    python = (venv / "bin/python").resolve(strict=True) if (venv / "bin/python").exists() else None
    if (path.parent != venv / "bin" or path.name not in {"python", "python3", "python3.12"}
            or target != python or not target.is_file() or not (target.stat().st_mode & 0o111)):
        raise ReleaseDenied("EXTERNAL_VENV_SYMLINK_NOT_ALLOWLISTED")


def _venv_hash(venv: Path, files: list[Path]) -> str:
    rows = [(str(p.relative_to(venv)), sha(p.read_bytes())) for p in files]
    links = [(str(p.relative_to(venv)), os.readlink(p)) for p in sorted(venv.rglob("*")) if p.is_symlink()]
    return sha(json.dumps({"files": rows, "links": links}, separators=(",", ":")).encode())


def _copy_code(stage: Path, files: list[tuple[str, bytes]]) -> None:
    for name, data in files:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        target.write_bytes(data)
        target.chmod(0o600)


def _copy_venv(stage: Path) -> None:
    shutil.copytree(ROOT / ".venv", stage / ".venv", symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    old = str(ROOT).encode()
    new = str(stage).encode()
    for path in (stage / ".venv").rglob("*"):
        if path.is_symlink():
            _validate_venv_symlink(path, stage / ".venv")
            continue
        if path.is_dir():
            path.chmod(0o700)
            continue
        if not path.is_file():
            raise ReleaseDenied("SPECIAL_FILE_AFTER_COPY")
        data = path.read_bytes()
        if old in data:
            if len(data) > 1_000_000:
                raise ReleaseDenied("DESKTOP_PATH_IN_LARGE_VENV_FILE")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ReleaseDenied("DESKTOP_PATH_IN_BINARY_VENV_FILE") from exc
            path.write_bytes(data.replace(old, new))
        if old in path.read_bytes():
            raise ReleaseDenied("DESKTOP_PATH_REMAINS_IN_VENV")
        executable = stat.S_IMODE(path.stat().st_mode) & 0o111
        path.chmod(0o700 if path.parent.name == "bin" or executable else 0o600)
    # Editable install must resolve the copied source rather than the Desktop tree.
    pth = stage / ".venv/lib/python3.12/site-packages/__editable__.yuanli_invest-0.1.0.pth"
    if not pth.is_file() or pth.read_text().strip() != str(stage / "src"):
        raise ReleaseDenied("EDITABLE_PTH_NOT_REBOUND")
    if old in (stage / ".venv/pyvenv.cfg").read_bytes():
        raise ReleaseDenied("PYVENV_CFG_STILL_REFERENCES_DESKTOP")


def _run_python(stage: Path, args: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    environment = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "PYTHONDONTWRITEBYTECODE": "1"}
    # -I ignores PYTHON* environment variables; -B must be an interpreter flag
    # or import probes would create unmanifested __pycache__ under the release.
    return subprocess.run([str(stage / ".venv/bin/python"), "-B", *args], cwd=stage, env=environment,
                          capture_output=True, text=True, timeout=timeout, check=False)


def _validate_python(stage: Path) -> dict:
    code = "import json,sys,yuanli_invest;print(json.dumps({'prefix':sys.prefix,'version':list(sys.version_info[:3]),'module':yuanli_invest.__file__,'paths':sys.path}))"
    probe = _run_python(stage, ["-I", "-c", code])
    if probe.returncode:
        raise ReleaseDenied("STAGED_PYTHON_START_FAILED")
    data = json.loads(probe.stdout)
    if (data["prefix"] != str(stage / ".venv") or data["version"] < [3, 12]
            or not Path(data["module"]).is_relative_to(stage / "src")
            or any(_is_desktop(Path(p)) for p in data["paths"] if p)):
        raise ReleaseDenied("STAGED_PYTHON_POINTS_TO_DESKTOP_OR_WRONG_VERSION")
    checks = []
    for _, worker, _, _, _ in WORKERS:
        result = _run_python(stage, [str(stage / "scripts" / worker), "--help"])
        checks.append({"worker": worker, "exit_code": result.returncode,
                       "help_has_runtime_dir": "--runtime-dir" in result.stdout,
                       "stderr_present": bool(result.stderr),
                       "sha256": sha((stage / "scripts" / worker).read_bytes())})
    preflight = _run_python(stage, [str(stage / "scripts/gold_au_morning_preflight.py"), "--help"])
    if (not all(row["exit_code"] == 0 and row["help_has_runtime_dir"] and not row["stderr_present"] for row in checks)
            or preflight.returncode != 0):
        raise ReleaseDenied("STAGED_WORKER_IMPORT_OR_HELP_FAILED")
    return {"version": data["version"], "prefix_matches_release": True,
            "module_under_release": True, "sys_path_excludes_desktop": True,
            "workers_help_only": checks, "preflight_help_only": True}


def validate_candidate_plist(candidate: dict, *, stage: Path, runtime: Path,
                             label_suffix: str, worker: str, hour: int, minute: int) -> None:
    required_keys = {"Label", "ProgramArguments", "WorkingDirectory", "StartCalendarInterval",
                     "RunAtLoad", "StandardOutPath", "StandardErrorPath"}
    expected_label = "com.yuanli.gold2-au-" + label_suffix
    expected_args = [str(stage / ".venv/bin/python"), str(stage / "scripts" / worker),
                     "--runtime-dir", str(runtime), "--execute"]
    expected_calendar = [{"Weekday": day, "Hour": hour, "Minute": minute} for day in range(1, 6)]
    log_root = runtime / "logs"
    expected_stdout, expected_stderr = LOG_FILES[label_suffix]
    stdout = candidate.get("StandardOutPath")
    stderr = candidate.get("StandardErrorPath")
    if (set(candidate) != required_keys
            or candidate.get("Label") != expected_label or candidate.get("ProgramArguments") != expected_args
            or candidate.get("WorkingDirectory") != str(stage) or candidate.get("StartCalendarInterval") != expected_calendar
            or candidate.get("RunAtLoad") is not False or "EnvironmentVariables" in candidate
            or not isinstance(stdout, str) or not isinstance(stderr, str)
            or stdout != str(log_root / expected_stdout) or stderr != str(log_root / expected_stderr)
            or any(_is_desktop(Path(arg)) for arg in expected_args if arg.startswith("/"))):
        raise ReleaseDenied("CANDIDATE_PLIST_CONTRACT_MISMATCH")


def _render_plists(stage: Path, runtime: Path) -> dict:
    runtime = check_private_runtime(runtime)
    candidate_dir = stage / "candidate-plists"
    candidate_dir.mkdir(mode=0o700)
    rows = []
    for label_suffix, worker, installer, hour, minute in WORKERS:
        code = ("import base64,plistlib,sys;from pathlib import Path;"
                f"sys.path.insert(0,{str(stage)!r});"
                f"from scripts.{installer} import render;"
                f"print(base64.b64encode(plistlib.dumps(render(Path({str(runtime)!r})))).decode())")
        result = _run_python(stage, ["-I", "-c", code])
        if result.returncode:
            raise ReleaseDenied("INSTALLER_RENDER_FAILED")
        raw = base64.b64decode(result.stdout.strip(), validate=True)
        candidate = plistlib.loads(raw)
        expected_label = "com.yuanli.gold2-au-" + label_suffix
        expected_args = [str(stage / ".venv/bin/python"), str(stage / "scripts" / worker),
                         "--runtime-dir", str(runtime), "--execute"]
        expected_calendar = [{"Weekday": day, "Hour": hour, "Minute": minute} for day in range(1, 6)]
        validate_candidate_plist(candidate, stage=stage, runtime=runtime,
                                 label_suffix=label_suffix, worker=worker, hour=hour, minute=minute)
        path = candidate_dir / (expected_label + ".plist")
        path.write_bytes(raw)
        path.chmod(0o600)
        rows.append({"label": expected_label, "relative_path": str(path.relative_to(stage)),
                     "sha256": sha(raw), "program_arguments": expected_args,
                     "working_directory": str(stage), "calendar": expected_calendar,
                     "run_at_load": False})
    return {"count": len(rows), "rows": rows, "loaded_or_activated": False}


def prepare(*, runtime: Path, base: Path, stage_release: bool) -> dict:
    base = check_release_base(base)
    runtime = check_private_runtime(runtime)
    git_head, files, code_hash = _code_inventory()
    venv = ROOT / ".venv"
    venv_files = _safe_venv_files(venv)
    venv_hash = _venv_hash(venv, venv_files)
    base_executable = (venv / "bin/python").resolve(strict=True)
    if _is_desktop(base_executable):
        raise ReleaseDenied("BASE_PYTHON_ON_DESKTOP")
    release_id = f"{git_head[:12]}-{code_hash[:12]}-{venv_hash[:12]}"
    destination = base / release_id
    report = {"schema_version": "gold2-nondesktop-release-candidate.v1",
              "status": "INVENTORIED_ONLY", "prepared_at": datetime.now(timezone.utc).isoformat(),
              "release_id": release_id, "release_path": str(destination),
              "source_git_head": git_head, "source_code_sha256": code_hash,
              "source_tracked_file_count": len(files), "source_venv_sha256": venv_hash,
              "external_base_python_path": str(base_executable),
              "external_base_python_sha256": sha(base_executable.read_bytes()),
              "external_base_dependency_not_copied": True,
              "private_runtime_path": str(runtime), "credentials_copied": False,
              "launch_agents_loaded_or_changed": False, "business_workers_executed": False,
              "natural_0830_accepted": False,
              "limitations": ["The external base Python executable is hashed; its standard-library tree is neither copied nor pinned by this manifest and must be rechecked at cutover.",
                              "This user-writable release is content-addressed, not OS-immutable; activation requires hash readback.",
                              "A rendered plist and --help imports do not prove launchd TCC or a natural trading-day capture."]}
    if not stage_release:
        return report
    if destination.exists() or destination.is_symlink():
        raise ReleaseDenied("RELEASE_ALREADY_EXISTS_REVIEW_EXISTING_CANDIDATE")
    _private_directory(base)
    stage = Path(tempfile.mkdtemp(prefix=".stage-", dir=base))
    stage.chmod(0o700)
    try:
        _copy_code(stage, files)
        _copy_venv(stage)
        # Atomic name is chosen before rendering so Python/.pth/plist paths are final.
        # A failed validation removes this unactivated candidate; no loaded job
        # or LaunchAgents plist is touched.
        final = destination
        # Rebind references from temporary path to final release path in the small
        # venv text files. CLI entry-point shebangs and editable paths must be final.
        for path in (stage / ".venv").rglob("*"):
            if path.is_file() and not path.is_symlink() and str(stage).encode() in path.read_bytes():
                data = path.read_bytes()
                if len(data) > 1_000_000:
                    raise ReleaseDenied("STAGING_PATH_IN_LARGE_VENV_FILE")
                path.write_bytes(data.replace(str(stage).encode(), str(final).encode()))
        # Work in the final path only after an atomic rename; this is not an
        # installation or an activation of any launchd job.
        stage.rename(final)
        stage = final
        python = _validate_python(stage)
        plists = _render_plists(stage, runtime)
        report.update(status="PREPARED_NOT_ACTIVATED", python=python, candidate_plists=plists,
                      source_file_hashes={name: sha(data) for name, data in files},
                      staged_venv_sha256=_venv_hash(stage / ".venv", _safe_venv_files(stage / ".venv")),
                      editable_pth_sha256=sha((stage / ".venv/lib/python3.12/site-packages/__editable__.yuanli_invest-0.1.0.pth").read_bytes()),
                      pyvenv_cfg_sha256=sha((stage / ".venv/pyvenv.cfg").read_bytes()))
        manifest = stage / "release-manifest.json"
        manifest.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
        manifest.chmod(0o600)
        return report
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    parser.add_argument("--release-base", type=Path,
                        default=Path.home() / ".yuanli/releases/gold2-au")
    parser.add_argument("--stage", action="store_true", help="create a candidate release; never activate")
    parser.add_argument("--receipt", type=Path, help="optional exclusive JSON receipt outside the release")
    args = parser.parse_args()
    try:
        report = prepare(runtime=args.runtime_dir.expanduser().absolute(),
                         base=args.release_base, stage_release=args.stage)
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(args.receipt, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(report, output, sort_keys=True, indent=2, ensure_ascii=False)
                output.write("\n")
        print(json.dumps({"status": report["status"], "release_id": report["release_id"],
                          "release_path": report["release_path"], "candidate_count": report.get("candidate_plists", {}).get("count", 0),
                          "launch_agents_changed": False, "business_workers_executed": False}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "DENIED", "reason": str(exc),
                          "launch_agents_changed": False, "business_workers_executed": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
