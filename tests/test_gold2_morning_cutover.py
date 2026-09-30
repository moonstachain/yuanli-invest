"""Mocked group cutover checks; never invokes a real launchctl or worker."""

from datetime import datetime
from pathlib import Path
import plistlib
import stat
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts import activate_gold2_morning_release as cutover
from scripts import prepare_gold2_morning_release as release


class FakeLaunchctl:
    def __init__(self, paths: dict[str, Path], fail_bootstrap_number: int | None = None,
                 corrupt_readback: str | None = None):
        self.paths = paths
        self.loaded = set(paths)
        self.calls: list[list[str]] = []
        self.bootstrap_count = 0
        self.fail_bootstrap_number = fail_bootstrap_number
        self.corrupt_readback = corrupt_readback

    def __call__(self, args: list[str], **_kwargs):
        self.calls.append(args)
        op = args[1]
        if op == "list":
            value = "PID\tStatus\tLabel\n" + "".join("-\t0\t" + x + "\n" for x in sorted(self.loaded))
            return subprocess.CompletedProcess(args, 0, value, "")
        if op == "print":
            label = args[-1].rsplit("/", 1)[-1]
            if label not in self.loaded:
                return subprocess.CompletedProcess(args, 113, "", "not loaded")
            path = self.paths[label]
            value = plistlib.loads(path.read_bytes())
            arguments = list(value["ProgramArguments"])
            stdout = value["StandardOutPath"]
            stderr = value["StandardErrorPath"]
            calendar = list(value["StartCalendarInterval"])
            if self.corrupt_readback == "arguments":
                arguments[-1] = "--unexpected"
            elif self.corrupt_readback == "stdout":
                stdout += ".redirected"
            elif self.corrupt_readback == "calendar":
                calendar[-1] = dict(calendar[-1], Minute=calendar[-1]["Minute"] + 1)
            output = (f"gui/501/{label} = {{\n"
                      f"\tactive count = 0\n\tpath = {path}\n\tstate = not running\n"
                      f"\tprogram = {value['ProgramArguments'][0]}\n"
                      "\targuments = {\n" + "".join("\t\t" + arg + "\n" for arg in arguments)
                      + "\t}\n"
                      f"\tworking directory = {value['WorkingDirectory']}\n"
                      f"\tstdout path = {stdout}\n\tstderr path = {stderr}\n"
                      "\tevent triggers = {\n"
                      + "".join("\t" + label + ".fixture => {\n"
                                "\t\tkeepalive = 0\n\t\tservice = " + label + "\n"
                                "\t\tstream = com.apple.launchd.calendarinterval\n"
                                "\t\tdescriptor = {\n"
                                + "".join(f'\t\t\t"{key}" => {row[key]}\n' for key in ("Minute", "Hour", "Weekday"))
                                + "\t\t}\n\t}\n" for row in calendar)
                      + "\t}\n"
                      + "\tresource coalition = {\n\t\tactive count = 1\n\t}\n}\n")
            return subprocess.CompletedProcess(args, 0, output, "")
        if op == "bootout":
            label = args[-1].rsplit("/", 1)[-1]
            if label not in self.loaded:
                return subprocess.CompletedProcess(args, 113, "", "not loaded")
            self.loaded.remove(label)
            return subprocess.CompletedProcess(args, 0, "", "")
        if op == "bootstrap":
            self.bootstrap_count += 1
            if self.bootstrap_count == self.fail_bootstrap_number:
                return subprocess.CompletedProcess(args, 5, "", "injected failure")
            label = Path(args[-1]).stem
            self.loaded.add(label)
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected launchctl operation: " + op)


def plan_fixture(temporary: str):
    parent = Path(temporary)
    runtime = parent / "runtime"
    runtime.mkdir(mode=0o700)
    (runtime / "logs").mkdir(mode=0o700)
    agents = parent / "Library/LaunchAgents"
    agents.mkdir(parents=True, mode=0o700)
    stage = parent / "candidate"
    stage.mkdir(mode=0o700)
    candidates = stage / "candidate-plists"
    candidates.mkdir(mode=0o700)
    manifest = stage / "release-manifest.json"
    manifest.write_bytes(b"synthetic manifest for transaction-level tests")
    jobs = []
    paths = {}
    for suffix, worker, _, hour, minute in release.WORKERS:
        label = "com.yuanli.gold2-au-" + suffix
        path = agents / (label + ".plist")
        stdout, stderr = release.LOG_FILES[suffix]
        old = {"Label": label, "ProgramArguments": ["/old/.venv/bin/python", "/old/scripts/" + worker,
                                                   "--runtime-dir", str(runtime), "--execute"],
               "WorkingDirectory": "/old", "RunAtLoad": False,
               "StartCalendarInterval": [{"Weekday": day, "Hour": hour, "Minute": minute} for day in range(1, 6)],
               "StandardOutPath": str(runtime / "logs" / stdout),
               "StandardErrorPath": str(runtime / "logs" / stderr)}
        new = dict(old, ProgramArguments=[str(stage / ".venv/bin/python"), str(stage / "scripts" / worker),
                                          "--runtime-dir", str(runtime), "--execute"],
                   WorkingDirectory=str(stage))
        old_bytes = plistlib.dumps(old)
        new_bytes = plistlib.dumps(new)
        (candidates / (label + ".plist")).write_bytes(new_bytes)
        path.write_bytes(old_bytes)
        path.chmod(0o644)
        paths[label] = path
        jobs.append(cutover.Job(label, path, old_bytes, 0o644, cutover._sha(old_bytes), "/old/.venv/bin/python", "/old",
                                new_bytes, cutover._sha(new_bytes), str(stage / ".venv/bin/python"), str(stage)))
    plan = cutover.CutoverPlan(stage, runtime, "reviewed-release", cutover._sha(manifest.read_bytes()),
                               "b" * 64, tuple(jobs))
    return plan, paths


class MorningCutoverTests(unittest.TestCase):
    def test_staged_operator_invocation_and_unmatched_operator_bytes_denied(self):
        with patch.object(cutover, "ROOT", Path("/tmp/gold2-staged-release")):
            with self.assertRaisesRegex(cutover.CutoverDenied, "ACTIVATION_OPERATOR_CHECKOUT_REQUIRED"):
                cutover.collect_plan(Path("/tmp/unused"), Path("/tmp/unused"))
        with TemporaryDirectory() as temporary:
            operator = Path(temporary)
            scripts = operator / "scripts"
            scripts.mkdir()
            expected = {}
            for name in ("activate_gold2_morning_release.py", "prepare_gold2_morning_release.py"):
                (scripts / name).write_bytes(b"reviewed")
                expected["scripts/" + name] = cutover._sha(b"reviewed")
            with patch.object(cutover, "ROOT", operator):
                cutover._check_operator_source(expected)
                (scripts / "activate_gold2_morning_release.py").write_bytes(b"changed")
                with self.assertRaisesRegex(cutover.CutoverDenied, "OPERATOR_TOOL_NOT_FROZEN_RELEASE_MATCH"):
                    cutover._check_operator_source(expected)

    def test_unknown_old_worker_is_not_a_valid_rollback_target(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            plan, paths = plan_fixture(str(home))
            first = plan.jobs[0]
            wrong = plistlib.loads(first.path.read_bytes())
            wrong["ProgramArguments"][1] = "/old/scripts/other.py"
            first.path.write_bytes(plistlib.dumps(wrong))
            rows = [{"label": job.label, "relative_path": "candidate-plists/" + job.label + ".plist",
                     "sha256": job.candidate_sha256} for job in plan.jobs]
            manifest = {"candidate_plists": {"count": 4, "rows": rows}}
            with patch.object(cutover.Path, "home", return_value=home), \
                    patch.object(cutover, "ROOT", Path("/old")):
                with self.assertRaisesRegex(cutover.CutoverDenied, "OLD_PLIST_CONTRACT_MISMATCH"):
                    cutover._old_jobs(plan.release_path, plan.runtime, manifest, runner=FakeLaunchctl(paths))

    def test_loaded_readback_rejects_wrong_args_logs_or_calendar(self):
        with TemporaryDirectory() as temporary:
            plan, paths = plan_fixture(temporary)
            # The fake output includes a nested coalition `active count = 1`,
            # as real macOS launchctl print does. It must not override the
            # top-level idle count of zero.
            cutover._verify_job(plan.jobs[0], new=False, runner=FakeLaunchctl(paths))
            for corruption in ("arguments", "stdout", "calendar"):
                with self.subTest(corruption=corruption):
                    runner = FakeLaunchctl(paths, corrupt_readback=corruption)
                    with self.assertRaisesRegex(cutover.CutoverDenied, "LAUNCHD_READBACK_MISMATCH"):
                        cutover._verify_job(plan.jobs[0], new=False, runner=runner)

    def test_only_standard_bytecode_cache_is_excluded_from_source_hashes(self):
        with TemporaryDirectory() as temporary:
            stage = Path(temporary)
            (stage / "scripts/__pycache__").mkdir(parents=True)
            (stage / "src/pkg").mkdir(parents=True)
            (stage / "scripts/worker.py").write_bytes(b"print('reviewed')")
            (stage / "src/pkg/model.py").write_bytes(b"value = 1")
            (stage / "pyproject.toml").write_bytes(b"[project]\n")
            cache = stage / "scripts/__pycache__/worker.cpython-312.pyc"
            cache.write_bytes(b"post-cutover bytecode")
            hashes = cutover._source_hashes(stage)
            self.assertNotIn(str(cache.relative_to(stage)), hashes)
            self.assertIn("scripts/worker.py", hashes)
            (stage / "scripts/unreviewed.py").write_bytes(b"unreviewed")
            self.assertIn("scripts/unreviewed.py", cutover._source_hashes(stage))

    def test_window_and_review_digest_stop_before_launchctl_mutation(self):
        with TemporaryDirectory() as temporary:
            plan, paths = plan_fixture(temporary)
            runner = FakeLaunchctl(paths)
            with self.assertRaisesRegex(cutover.CutoverDenied, "REVIEWED_RELEASE"):
                cutover.activate(plan, expected_release_id="wrong", expected_old_state_sha256=plan.old_state_sha256,
                                 expected_manifest_sha256=plan.release_manifest_sha256,
                                 now=datetime(2026, 9, 28, 14, tzinfo=ZoneInfo("Asia/Shanghai")), runner=runner)
            self.assertEqual(runner.calls, [])
            with self.assertRaisesRegex(cutover.CutoverDenied, "WORKER_SCHEDULE_WINDOW"):
                cutover.activate(plan, expected_release_id=plan.release_id,
                                 expected_old_state_sha256=plan.old_state_sha256,
                                 expected_manifest_sha256=plan.release_manifest_sha256,
                                 now=datetime(2026, 9, 28, 8, 30, tzinfo=ZoneInfo("Asia/Shanghai")), runner=runner)
            self.assertEqual(runner.calls, [])
            self.assertFalse((plan.runtime / "cutovers").exists())

    def test_extra_loaded_gold2_label_rejected(self):
        with TemporaryDirectory() as temporary:
            plan, paths = plan_fixture(temporary)
            runner = FakeLaunchctl(paths)
            runner.loaded.add("com.yuanli.gold2-au-unreviewed")
            with self.assertRaisesRegex(cutover.CutoverDenied, "EXTRA_OR_MISSING"):
                cutover.activate(plan, expected_release_id=plan.release_id,
                                 expected_old_state_sha256=plan.old_state_sha256,
                                 expected_manifest_sha256=plan.release_manifest_sha256,
                                 now=datetime(2026, 9, 28, 14, tzinfo=ZoneInfo("Asia/Shanghai")), runner=runner)
            self.assertEqual([call[1] for call in runner.calls], ["list"])

    def test_mocked_third_bootstrap_failure_restores_all_four(self):
        with TemporaryDirectory() as temporary:
            plan, paths = plan_fixture(temporary)
            runner = FakeLaunchctl(paths, fail_bootstrap_number=3)
            with patch.object(cutover, "_outside_worker_window", return_value=True):
                with self.assertRaisesRegex(cutover.CutoverDenied, "CUTOVER_FAILED_ROLLED_BACK"):
                    cutover.activate(plan, expected_release_id=plan.release_id,
                                     expected_old_state_sha256=plan.old_state_sha256,
                                     expected_manifest_sha256=plan.release_manifest_sha256,
                                     now=datetime(2026, 9, 28, 14, tzinfo=ZoneInfo("Asia/Shanghai")), runner=runner)
            self.assertEqual(runner.loaded, set(paths))
            self.assertFalse(any(call[1] == "kickstart" for call in runner.calls))
            self.assertEqual(sum(call[1] == "bootout" for call in runner.calls), 6)
            for job in plan.jobs:
                self.assertEqual(job.path.read_bytes(), job.old_bytes)
                self.assertEqual(stat.S_IMODE(job.path.stat().st_mode), job.old_mode)
            transactions = list((plan.runtime / "cutovers").glob("cutover-*/"))
            self.assertEqual(len(transactions), 1)
            directory = transactions[0]
            self.assertTrue((directory / "00-backed-up.json").is_file())
            self.assertTrue((directory / "01-failed-before-rollback.json").is_file())
            self.assertIn('"status": "ROLLED_BACK_VERIFIED"', (directory / "02-rollback-result.json").read_text())
            self.assertEqual(len(list(directory.glob("*.old.plist"))), 4)

    def test_mocked_success_uses_bootout_replace_bootstrap_and_readback(self):
        with TemporaryDirectory() as temporary:
            plan, paths = plan_fixture(temporary)
            runner = FakeLaunchctl(paths)
            with patch.object(cutover, "_outside_worker_window", return_value=True):
                result = cutover.activate(plan, expected_release_id=plan.release_id,
                                          expected_old_state_sha256=plan.old_state_sha256,
                                          expected_manifest_sha256=plan.release_manifest_sha256,
                                          now=datetime(2026, 9, 28, 14, tzinfo=ZoneInfo("Asia/Shanghai")), runner=runner)
            self.assertEqual(result["status"], "ACTIVATED_GROUP_READBACK")
            self.assertEqual([call[1] for call in runner.calls].count("bootout"), 4)
            self.assertEqual([call[1] for call in runner.calls].count("bootstrap"), 4)
            self.assertFalse(any(call[1] == "kickstart" for call in runner.calls))
            for job in plan.jobs:
                self.assertEqual(job.path.read_bytes(), job.candidate_bytes)
                self.assertEqual(stat.S_IMODE(job.path.stat().st_mode), 0o600)
            directory = Path(result["transaction_path"])
            self.assertTrue((directory / "00-backed-up.json").is_file())
            self.assertTrue((directory / "01-activated-readback.json").is_file())

    def test_log_directory_and_target_symlink_denied(self):
        with TemporaryDirectory() as temporary, TemporaryDirectory() as other:
            runtime = Path(temporary)
            logs = runtime / "logs"
            logs.mkdir(mode=0o700)
            target = logs / "stdout.log"
            target.symlink_to(Path(other) / "other.log")
            with self.assertRaisesRegex(cutover.CutoverDenied, "SYMLINK_LOG_TARGET"):
                cutover._check_logs(runtime)
            target.unlink()
            logs.chmod(0o755)
            with self.assertRaisesRegex(cutover.CutoverDenied, "INSECURE_RUNTIME_LOG_DIRECTORY"):
                cutover._check_logs(runtime)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
