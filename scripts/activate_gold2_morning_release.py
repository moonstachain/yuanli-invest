#!/usr/bin/env python3
"""Review or atomically cut over four GOLD2 morning LaunchAgents.

The default command is read-only. --activate requires a reviewed release ID
and an exact old-state digest from a fresh plan. It never runs a worker or
kickstarts a job. A failed group cutover restores all four old plist bytes and
their loaded registration, or emits ROLLBACK_INCOMPLETE for manual recovery.

Run this one-time cutover from the original Desktop Git checkout, not from the
staged release: its own ROOT pins the four known old worker paths for rollback.
The operator scripts must byte-match the reviewed release manifest. After a
successful cutover, this command deliberately cannot plan a second migration.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import stat
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import prepare_gold2_morning_release as release  # noqa: E402


class CutoverDenied(ValueError):
    pass


@dataclass(frozen=True)
class Job:
    label: str
    path: Path
    old_bytes: bytes
    old_mode: int
    old_sha256: str
    old_program: str
    old_working_directory: str
    candidate_bytes: bytes
    candidate_sha256: str
    new_program: str
    new_working_directory: str


@dataclass(frozen=True)
class CutoverPlan:
    release_path: Path
    runtime: Path
    release_id: str
    release_manifest_sha256: str
    old_state_sha256: str
    jobs: tuple[Job, ...]


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_release(path: Path) -> Path:
    if ".." in path.parts:
        raise CutoverDenied("RELEASE_PATH_TRAVERSAL")
    path = path.expanduser().absolute()
    base = release.check_release_base(Path.home() / ".yuanli/releases/gold2-au")
    if path.parent != base or path.is_symlink() or path != path.resolve(strict=False) or not path.is_dir():
        raise CutoverDenied("RELEASE_NOT_FIXED_PRIVATE_CANDIDATE")
    if path.stat().st_uid != os.getuid() or stat.S_IMODE(path.stat().st_mode) != 0o700:
        raise CutoverDenied("INSECURE_RELEASE_DIRECTORY")
    return path


def _check_operator_checkout() -> None:
    if not release._is_desktop(ROOT) or not (ROOT / ".git").exists():
        raise CutoverDenied("ACTIVATION_OPERATOR_CHECKOUT_REQUIRED")


def _check_operator_source(expected_files: dict) -> None:
    for name in ("scripts/activate_gold2_morning_release.py", "scripts/prepare_gold2_morning_release.py"):
        path = ROOT / name
        if path.is_symlink() or not path.is_file() or _sha(path.read_bytes()) != expected_files.get(name):
            raise CutoverDenied("OPERATOR_TOOL_NOT_FROZEN_RELEASE_MATCH:" + name)


def _check_logs(runtime: Path) -> None:
    logs = runtime / "logs"
    if (logs.is_symlink() or not logs.is_dir() or logs.stat().st_uid != os.getuid()
            or stat.S_IMODE(logs.stat().st_mode) != 0o700):
        raise CutoverDenied("INSECURE_RUNTIME_LOG_DIRECTORY")
    for stdout, stderr in release.LOG_FILES.values():
        for name in (stdout, stderr):
            path = logs / name
            if path.is_symlink():
                raise CutoverDenied("SYMLINK_LOG_TARGET")
            if path.exists() and (not path.is_file() or path.stat().st_uid != os.getuid()
                                  or stat.S_IMODE(path.stat().st_mode) & 0o022):
                raise CutoverDenied("INSECURE_LOG_TARGET")


def _source_hashes(path: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for base in (path / "scripts", path / "src"):
        if base.is_symlink() or not base.is_dir():
            raise CutoverDenied("MISSING_RELEASE_SOURCE_DIRECTORY")
        for file in base.rglob("*"):
            if file.is_symlink():
                raise CutoverDenied("SOURCE_SYMLINK")
            if file.is_file():
                relative = file.relative_to(path)
                # Normal scheduled Python imports create these after cutover.
                # Only bytecode inside its standard cache directory is ignored;
                # all other unexpected files still break the manifest comparison.
                if "__pycache__" in relative.parts and file.suffix == ".pyc":
                    continue
                hashes[str(relative)] = _sha(file.read_bytes())
    project = path / "pyproject.toml"
    if project.is_symlink() or not project.is_file():
        raise CutoverDenied("MISSING_RELEASE_PROJECT")
    hashes["pyproject.toml"] = _sha(project.read_bytes())
    return hashes


def _release_inventory(path: Path, runtime: Path) -> tuple[dict, str]:
    path = _canonical_release(path)
    runtime = release.check_private_runtime(runtime)
    _check_logs(runtime)
    manifest_path = path / "release-manifest.json"
    if (manifest_path.is_symlink() or not manifest_path.is_file()
            or stat.S_IMODE(manifest_path.stat().st_mode) != 0o600):
        raise CutoverDenied("UNTRUSTED_RELEASE_MANIFEST")
    raw_manifest = manifest_path.read_bytes()
    if len(raw_manifest) > 200_000:
        raise CutoverDenied("OVERSIZED_RELEASE_MANIFEST")
    manifest = json.loads(raw_manifest)
    if not isinstance(manifest, dict):
        raise CutoverDenied("INVALID_RELEASE_MANIFEST")
    if (manifest.get("schema_version") != "gold2-nondesktop-release-candidate.v1"
            or manifest.get("status") != "PREPARED_NOT_ACTIVATED"
            or manifest.get("release_path") != str(path)
            or manifest.get("release_id") != path.name
            or manifest.get("private_runtime_path") != str(runtime)
            or manifest.get("launch_agents_loaded_or_changed") is not False
            or manifest.get("business_workers_executed") is not False
            or not re.fullmatch(r"[0-9a-f]{12}(?:-[0-9a-f]{12}){2}", path.name)):
        raise CutoverDenied("RELEASE_MANIFEST_IDENTITY_MISMATCH")
    expected_files = manifest.get("source_file_hashes")
    if not isinstance(expected_files, dict) or not expected_files:
        raise CutoverDenied("SOURCE_FILE_HASHES_MISSING")
    actual_files = _source_hashes(path)
    if actual_files != expected_files or len(actual_files) != manifest.get("source_tracked_file_count"):
        raise CutoverDenied("RELEASE_SOURCE_HASH_MISMATCH")
    _check_operator_source(expected_files)
    inventory_hash = _sha(json.dumps(sorted(actual_files.items()), separators=(",", ":")).encode())
    if inventory_hash != manifest.get("source_code_sha256"):
        raise CutoverDenied("RELEASE_SOURCE_INVENTORY_MISMATCH")
    venv = path / ".venv"
    files = release._safe_venv_files(venv)
    if release._venv_hash(venv, files) != manifest.get("staged_venv_sha256"):
        raise CutoverDenied("RELEASE_VENV_HASH_MISMATCH")
    pth = venv / "lib/python3.12/site-packages/__editable__.yuanli_invest-0.1.0.pth"
    cfg = venv / "pyvenv.cfg"
    if (not pth.is_file() or pth.read_text().strip() != str(path / "src")
            or _sha(pth.read_bytes()) != manifest.get("editable_pth_sha256")
            or not cfg.is_file() or _sha(cfg.read_bytes()) != manifest.get("pyvenv_cfg_sha256")):
        raise CutoverDenied("EDITABLE_VENV_BINDING_MISMATCH")
    base_python = Path(manifest.get("external_base_python_path", ""))
    if (not base_python.is_absolute() or release._is_desktop(base_python)
            or base_python != (venv / "bin/python").resolve(strict=True)
            or _sha(base_python.read_bytes()) != manifest.get("external_base_python_sha256")):
        raise CutoverDenied("BASE_PYTHON_DEPENDENCY_CHANGED")
    # Imports and --help stay read-only. They confirm release paths, not TCC
    # or a natural scheduled decision.
    release._validate_python(path)
    return manifest, _sha(raw_manifest)


def _launchctl(args: list[str], runner=subprocess.run) -> subprocess.CompletedProcess[str]:
    return runner(["launchctl", *args], capture_output=True, text=True, timeout=8, check=False)


def _check_exact_loaded_label_set(*, runner=subprocess.run) -> None:
    reply = _launchctl(["list"], runner=runner)
    if reply.returncode:
        raise CutoverDenied("LAUNCHD_LABEL_INVENTORY_UNAVAILABLE")
    actual = {parts[-1] for line in reply.stdout.splitlines()
              if (parts := line.split()) and parts[-1].startswith("com.yuanli.gold2-au-")}
    expected = {"com.yuanli.gold2-au-" + suffix for suffix, *_ in release.WORKERS}
    if actual != expected:
        raise CutoverDenied("EXTRA_OR_MISSING_GOLD2_LAUNCHD_LABEL")


def _loaded_state(label: str, path: Path, *, runner=subprocess.run,
                  allow_absent: bool = False) -> dict | None:
    reply = _launchctl(["print", f"gui/{os.getuid()}/{label}"], runner=runner)
    if reply.returncode:
        if allow_absent:
            return None
        raise CutoverDenied("LAUNCHD_JOB_NOT_LOADED:" + label)
    lines = reply.stdout.splitlines()
    def field(name: str) -> str | None:
        # launchctl repeats names such as `active count` in nested coalitions;
        # only the single-tab, job-level fields describe this LaunchAgent.
        matches = [line[1:].removeprefix(name + " = ") for line in lines
                   if line.startswith("\t" + name + " = ")]
        return matches[0] if len(matches) == 1 else None
    def simple_block(name: str) -> list[str] | None:
        starts = [index for index, line in enumerate(lines) if line == "\t" + name + " = {"]
        if len(starts) != 1:
            return None
        result = []
        for line in lines[starts[0] + 1:]:
            if line.strip() == "}":
                return result
            result.append(line.strip())
        return None
    arguments = simple_block("arguments")
    calendars = []
    for index, line in enumerate(lines):
        if line.strip() != "descriptor = {":
            continue
        parent = [part.strip() for part in lines[max(0, index - 6):index]]
        if ("service = " + label not in parent
                or "stream = com.apple.launchd.calendarinterval" not in parent):
            raise CutoverDenied("LAUNCHD_CALENDAR_SOURCE_MISMATCH:" + label)
        values = {}
        for body_line in lines[index + 1:]:
            body_line = body_line.strip()
            if body_line == "}":
                break
            match = re.fullmatch(r'"(Minute|Hour|Weekday)" => ([0-9]+)', body_line)
            if match is None or match.group(1) in values:
                raise CutoverDenied("LAUNCHD_CALENDAR_DESCRIPTOR_INVALID:" + label)
            values[match.group(1)] = int(match.group(2))
        if set(values) != {"Minute", "Hour", "Weekday"}:
            raise CutoverDenied("LAUNCHD_CALENDAR_DESCRIPTOR_INCOMPLETE:" + label)
        calendars.append(values)
    result = {"state": field("state"), "active_count": field("active count"),
              "path": field("path"), "program": field("program"),
              "working_directory": field("working directory"),
              "arguments": arguments, "stdout_path": field("stdout path"),
              "stderr_path": field("stderr path"),
              "calendar": sorted(calendars, key=lambda row: row["Weekday"])}
    if result["path"] != str(path) or result["state"] != "not running" or result["active_count"] != "0":
        raise CutoverDenied("LAUNCHD_JOB_NOT_IDLE_OR_WRONG_PATH:" + label)
    if (arguments is None or len(arguments) != 5 or len(calendars) != 5
            or len({row["Weekday"] for row in calendars}) != 5
            or result["stdout_path"] is None or result["stderr_path"] is None):
        raise CutoverDenied("LAUNCHD_CONFIGURATION_READBACK_INCOMPLETE:" + label)
    return result


def _old_jobs(release_path: Path, runtime: Path, manifest: dict,
              *, runner=subprocess.run) -> tuple[Job, ...]:
    agent_dir = Path.home() / "Library/LaunchAgents"
    if (agent_dir.is_symlink() or agent_dir != agent_dir.resolve(strict=False)
            or not agent_dir.is_dir() or agent_dir.stat().st_uid != os.getuid()
            or stat.S_IMODE(agent_dir.stat().st_mode) != 0o700):
        raise CutoverDenied("UNTRUSTED_LAUNCHAGENTS_DIRECTORY")
    rows = manifest.get("candidate_plists", {}).get("rows")
    if not isinstance(rows, list) or len(rows) != 4 or manifest.get("candidate_plists", {}).get("count") != 4:
        raise CutoverDenied("INCOMPLETE_CANDIDATE_PLISTS")
    by_label = {row.get("label"): row for row in rows if isinstance(row, dict)}
    expected_labels = {"com.yuanli.gold2-au-" + suffix for suffix, *_ in release.WORKERS}
    if set(by_label) != expected_labels:
        raise CutoverDenied("CANDIDATE_LABEL_SET_MISMATCH")
    jobs = []
    for suffix, worker, _, hour, minute in release.WORKERS:
        label = "com.yuanli.gold2-au-" + suffix
        destination = agent_dir / (label + ".plist")
        if destination.is_symlink() or not destination.is_file() or destination.stat().st_uid != os.getuid():
            raise CutoverDenied("UNTRUSTED_OLD_PLIST:" + label)
        old = destination.read_bytes()
        old_mode = stat.S_IMODE(destination.stat().st_mode)
        parsed_old = plistlib.loads(old)
        old_args = parsed_old.get("ProgramArguments")
        expected_stdout, expected_stderr = release.LOG_FILES[suffix]
        if (set(parsed_old) != {"Label", "ProgramArguments", "WorkingDirectory", "StartCalendarInterval",
                                "RunAtLoad", "StandardOutPath", "StandardErrorPath"}
                or parsed_old.get("Label") != label or parsed_old.get("RunAtLoad") is not False
                or not isinstance(old_args, list) or len(old_args) != 5
                or old_args[0] != str(ROOT / ".venv/bin/python")
                or old_args[1] != str(ROOT / "scripts" / worker)
                or old_args[2:] != ["--runtime-dir", str(runtime), "--execute"]
                or parsed_old.get("WorkingDirectory") != str(ROOT)
                or parsed_old.get("StandardOutPath") != str(runtime / "logs" / expected_stdout)
                or parsed_old.get("StandardErrorPath") != str(runtime / "logs" / expected_stderr)
                or parsed_old.get("StartCalendarInterval") != [
                    {"Weekday": day, "Hour": hour, "Minute": minute} for day in range(1, 6)]):
            raise CutoverDenied("OLD_PLIST_CONTRACT_MISMATCH:" + label)
        loaded = _loaded_state(label, destination, runner=runner)
        if (loaded["program"] != old_args[0]
                or loaded["arguments"] != old_args
                or loaded["working_directory"] != parsed_old.get("WorkingDirectory")
                or loaded["stdout_path"] != parsed_old.get("StandardOutPath")
                or loaded["stderr_path"] != parsed_old.get("StandardErrorPath")
                or loaded["calendar"] != parsed_old.get("StartCalendarInterval")):
            raise CutoverDenied("OLD_PLIST_LAUNCHD_MISMATCH:" + label)
        row = by_label[label]
        candidate_path = release_path / row.get("relative_path", "")
        if (candidate_path.parent != release_path / "candidate-plists"
                or candidate_path.name != label + ".plist" or candidate_path.is_symlink()
                or not candidate_path.is_file() or stat.S_IMODE(candidate_path.stat().st_mode) != 0o600):
            raise CutoverDenied("CANDIDATE_FILE_PATH_MISMATCH:" + label)
        candidate = candidate_path.read_bytes()
        if _sha(candidate) != row.get("sha256"):
            raise CutoverDenied("CANDIDATE_PLIST_HASH_MISMATCH:" + label)
        parsed_new = plistlib.loads(candidate)
        release.validate_candidate_plist(parsed_new, stage=release_path, runtime=runtime,
                                         label_suffix=suffix, worker=worker, hour=hour, minute=minute)
        if old == candidate:
            raise CutoverDenied("CANDIDATE_ALREADY_INSTALLED:" + label)
        jobs.append(Job(label, destination, old, old_mode, _sha(old), old_args[0],
                        parsed_old["WorkingDirectory"], candidate, _sha(candidate),
                        parsed_new["ProgramArguments"][0], parsed_new["WorkingDirectory"]))
    return tuple(jobs)


def collect_plan(release_path: Path, runtime: Path, *, runner=subprocess.run) -> CutoverPlan:
    _check_operator_checkout()
    release_path = _canonical_release(release_path)
    runtime = release.check_private_runtime(runtime)
    manifest, manifest_hash = _release_inventory(release_path, runtime)
    _check_exact_loaded_label_set(runner=runner)
    jobs = _old_jobs(release_path, runtime, manifest, runner=runner)
    old_state_rows = [{"label": job.label, "sha256": job.old_sha256, "mode": job.old_mode,
                       "program": job.old_program, "working_directory": job.old_working_directory,
                       "loaded": "not running"} for job in jobs]
    digest = _sha(json.dumps(old_state_rows, sort_keys=True, separators=(",", ":")).encode())
    return CutoverPlan(release_path, runtime, manifest["release_id"], manifest_hash, digest, jobs)


def _outside_worker_window(now: datetime) -> bool:
    local = now.astimezone(ZoneInfo("Asia/Shanghai"))
    return not ((local.hour, local.minute) >= (7, 30) and (local.hour, local.minute) < (10, 0))


def _atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".gold2-cutover-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _write_phase(directory: Path, name: str, receipt: dict) -> None:
    path = directory / name
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write((json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode())
        output.flush()
        os.fsync(output.fileno())


def _command(args: list[str], *, runner=subprocess.run) -> None:
    reply = _launchctl(args, runner=runner)
    if reply.returncode:
        raise CutoverDenied("LAUNCHCTL_COMMAND_FAILED:" + " ".join(args[:2]))


def _verify_job(job: Job, *, new: bool, runner=subprocess.run) -> None:
    wanted_bytes = job.candidate_bytes if new else job.old_bytes
    wanted_mode = 0o600 if new else job.old_mode
    wanted = plistlib.loads(wanted_bytes)
    if (job.path.is_symlink() or job.path.read_bytes() != wanted_bytes
            or stat.S_IMODE(job.path.stat().st_mode) != wanted_mode):
        raise CutoverDenied("PLIST_READBACK_MISMATCH:" + job.label)
    loaded = _loaded_state(job.label, job.path, runner=runner)
    if (loaded["program"] != wanted["ProgramArguments"][0]
            or loaded["arguments"] != wanted["ProgramArguments"]
            or loaded["working_directory"] != wanted["WorkingDirectory"]
            or loaded["stdout_path"] != wanted["StandardOutPath"]
            or loaded["stderr_path"] != wanted["StandardErrorPath"]
            or loaded["calendar"] != wanted["StartCalendarInterval"]):
        raise CutoverDenied("LAUNCHD_READBACK_MISMATCH:" + job.label)


def _rollback(plan: CutoverPlan, *, runner=subprocess.run) -> list[str]:
    errors = []
    for job in plan.jobs:
        try:
            state = _loaded_state(job.label, job.path, runner=runner, allow_absent=True)
            if state is not None:
                _command(["bootout", f"gui/{os.getuid()}/{job.label}"], runner=runner)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(job.label + ":BOOTOUT:" + str(exc))
    for job in plan.jobs:
        try:
            _atomic_write(job.path, job.old_bytes, job.old_mode)
        except OSError as exc:
            errors.append(job.label + ":RESTORE:" + str(exc))
    for job in plan.jobs:
        try:
            _command(["bootstrap", f"gui/{os.getuid()}", str(job.path)], runner=runner)
            _verify_job(job, new=False, runner=runner)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(job.label + ":BOOTSTRAP_OR_VERIFY:" + str(exc))
    return errors


def activate(plan: CutoverPlan, *, expected_release_id: str, expected_old_state_sha256: str,
             expected_manifest_sha256: str, now: datetime, runner=subprocess.run) -> dict:
    if (expected_release_id != plan.release_id or expected_old_state_sha256 != plan.old_state_sha256
            or expected_manifest_sha256 != plan.release_manifest_sha256):
        raise CutoverDenied("REVIEWED_RELEASE_OR_STATE_DIGEST_MISMATCH")
    if not _outside_worker_window(now):
        raise CutoverDenied("WORKER_SCHEDULE_WINDOW")
    if _sha((plan.release_path / "release-manifest.json").read_bytes()) != plan.release_manifest_sha256:
        raise CutoverDenied("MANIFEST_CHANGED_AFTER_PLAN")
    _check_exact_loaded_label_set(runner=runner)
    for job in plan.jobs:
        if (plan.release_path / "candidate-plists" / (job.label + ".plist")).read_bytes() != job.candidate_bytes:
            raise CutoverDenied("CANDIDATE_CHANGED_AFTER_PLAN:" + job.label)
        _verify_job(job, new=False, runner=runner)
    cutovers = plan.runtime / "cutovers"
    if cutovers.exists():
        if (cutovers.is_symlink() or not cutovers.is_dir() or cutovers.stat().st_uid != os.getuid()
                or stat.S_IMODE(cutovers.stat().st_mode) != 0o700):
            raise CutoverDenied("INSECURE_CUTOVER_DIRECTORY")
    else:
        cutovers.mkdir(mode=0o700)
    lock_path = cutovers / ".lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        if stat.S_IMODE(os.fstat(lock_fd).st_mode) != 0o600 or os.fstat(lock_fd).st_uid != os.getuid():
            raise CutoverDenied("INSECURE_CUTOVER_LOCK")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        transaction = Path(tempfile.mkdtemp(prefix="cutover-", dir=cutovers))
        transaction.chmod(0o700)
        receipt = {"schema_version": "gold2-launchd-cutover.v1", "status": "BACKED_UP_NOT_MUTATED",
                   "release_id": plan.release_id, "release_manifest_sha256": plan.release_manifest_sha256,
                   "old_state_sha256": plan.old_state_sha256, "transaction_path": str(transaction),
                   "business_workers_executed": False, "kickstart_called": False,
                   "jobs": []}
        for job in plan.jobs:
            backup = transaction / (job.label + ".old.plist")
            _atomic_write(backup, job.old_bytes, 0o600)
            receipt["jobs"].append({"label": job.label, "old_sha256": job.old_sha256,
                                    "old_mode": oct(job.old_mode), "candidate_sha256": job.candidate_sha256,
                                    "old_loaded_state": "not running", "backup": str(backup)})
        _write_phase(transaction, "00-backed-up.json", receipt)
        previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        def interrupted(_signum, _frame):
            raise CutoverDenied("CUTOVER_INTERRUPTED")
        for sig in previous:
            signal.signal(sig, interrupted)
        try:
            for job in plan.jobs:
                if not _outside_worker_window(datetime.now(ZoneInfo("Asia/Shanghai"))):
                    raise CutoverDenied("WORKER_SCHEDULE_WINDOW_REACHED")
                if job.path.read_bytes() != job.old_bytes:
                    raise CutoverDenied("OLD_PLIST_CHANGED_DURING_CUTOVER")
                _command(["bootout", f"gui/{os.getuid()}/{job.label}"], runner=runner)
                _atomic_write(job.path, job.candidate_bytes, 0o600)
                _command(["bootstrap", f"gui/{os.getuid()}", str(job.path)], runner=runner)
                _verify_job(job, new=True, runner=runner)
            receipt["status"] = "ACTIVATED_GROUP_READBACK"
            receipt["launchd_fields_verified"] = ["idle_state", "plist_path", "program", "arguments",
                                                   "working_directory", "stdout_path", "stderr_path",
                                                   "five_weekday_calendar_descriptors"]
            _write_phase(transaction, "01-activated-readback.json", receipt)
            return receipt
        except BaseException as exc:
            receipt["status"] = "ACTIVATION_FAILED_ROLLBACK_PENDING"
            receipt["failure_type"] = type(exc).__name__
            receipt["failure_reason"] = str(exc)
            phase_error = None
            try:
                _write_phase(transaction, "01-failed-before-rollback.json", receipt)
            except OSError as phase_exc:
                phase_error = str(phase_exc)
            errors = _rollback(plan, runner=runner)
            if phase_error:
                errors.append("FAILURE_PHASE_WRITE:" + phase_error)
            receipt["status"] = "ROLLED_BACK_VERIFIED" if not errors else "ROLLBACK_INCOMPLETE"
            receipt["rollback_errors"] = errors
            try:
                _write_phase(transaction, "02-rollback-result.json", receipt)
            except OSError as phase_exc:
                errors.append("ROLLBACK_PHASE_WRITE:" + str(phase_exc))
            if errors:
                raise CutoverDenied("ROLLBACK_INCOMPLETE:" + str(transaction)) from exc
            raise CutoverDenied("CUTOVER_FAILED_ROLLED_BACK:" + str(transaction)) from exc
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    finally:
        os.close(lock_fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--expected-release-id")
    parser.add_argument("--expected-old-state-sha256")
    parser.add_argument("--expected-manifest-sha256")
    args = parser.parse_args()
    try:
        plan = collect_plan(args.release, args.runtime_dir)
        if args.activate:
            if not args.expected_release_id or not args.expected_old_state_sha256 or not args.expected_manifest_sha256:
                raise CutoverDenied("EXPLICIT_REVIEW_DIGESTS_REQUIRED")
            receipt = activate(plan, expected_release_id=args.expected_release_id,
                               expected_old_state_sha256=args.expected_old_state_sha256,
                               expected_manifest_sha256=args.expected_manifest_sha256,
                               now=datetime.now(ZoneInfo("Asia/Shanghai")))
            print(json.dumps({"status": receipt["status"], "transaction_path": receipt["transaction_path"],
                              "release_id": plan.release_id}, sort_keys=True))
        else:
            print(json.dumps({"status": "PLAN_READ_ONLY", "release_id": plan.release_id,
                              "release_path": str(plan.release_path), "release_manifest_sha256": plan.release_manifest_sha256,
                              "old_state_sha256": plan.old_state_sha256,
                              "jobs": [{"label": job.label, "old_sha256": job.old_sha256,
                                        "candidate_sha256": job.candidate_sha256,
                                        "old_mode": oct(job.old_mode)} for job in plan.jobs],
                              "launch_agents_changed": False, "business_workers_executed": False}, sort_keys=True))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "DENIED", "reason": str(exc),
                          "business_workers_executed": False}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
