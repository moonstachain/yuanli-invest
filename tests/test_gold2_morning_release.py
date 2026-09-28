"""Safety gates for a non-Desktop, unactivated morning release candidate."""

from pathlib import Path
import plistlib
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import prepare_gold2_morning_release as release


class MorningReleaseTests(unittest.TestCase):
    def test_import_probe_uses_python_no_bytecode_flag_under_isolation(self):
        with patch.object(release.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as runner:
            release._run_python(Path("/tmp/fixed-release"), ["-I", "-c", "print('ok')"])
            argv = runner.call_args.args[0]
            self.assertEqual(argv[1:4], ["-B", "-I", "-c"])

    def test_refuses_desktop_and_symlink_release_base(self):
        with self.assertRaisesRegex(release.ReleaseDenied, "NON_DESKTOP"):
            release.check_release_base(Path.home() / "Desktop/gold2-release")
        with TemporaryDirectory() as temporary:
            home = Path(temporary).resolve() / "home"
            real = home / ".yuanli/releases/real"
            real.mkdir(parents=True)
            link = real / "alias"
            link.symlink_to(real, target_is_directory=True)
            with patch.object(release.Path, "home", return_value=home):
                with self.assertRaisesRegex(release.ReleaseDenied, "NONCANONICAL_RELEASE_BASE|SYMLINK_RELEASE_PARENT"):
                    release.check_release_base(link / "gold2-au")
                with self.assertRaisesRegex(release.ReleaseDenied, "RELEASE_PATH_TRAVERSAL"):
                    release.check_release_base(home / ".yuanli/releases/../../Desktop/gold2-bypass")

    def test_dirty_git_source_aborts_before_any_release_write(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary).resolve() / "home"
            runtime = home / ".yuanli/runtime/gold_au_decision"
            runtime.mkdir(parents=True, mode=0o700)
            with patch.object(release.Path, "home", return_value=home), \
                    patch.object(release, "_git", return_value=b"?? scripts/secret.py\n"), \
                    patch.object(release, "_private_directory") as make_private:
                with self.assertRaisesRegex(release.ReleaseDenied, "SOURCE_NOT_CLEAN_GIT"):
                    release.prepare(runtime=runtime,
                                    base=home / ".yuanli/releases/gold2-au", stage_release=True)
                make_private.assert_not_called()

    def test_failed_stage_removes_candidate_without_touching_launchagents(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary).resolve() / "home"
            (home / ".yuanli").mkdir(parents=True, mode=0o700)
            runtime = home / ".yuanli/runtime/gold_au_decision"
            runtime.mkdir(parents=True, mode=0o700)
            agents = home / "Library/LaunchAgents"
            agents.mkdir(parents=True)
            existing = agents / "com.yuanli.gold2-au-0830-research-decision.plist"
            existing.write_bytes(b"unchanged-loaded-job")
            base = home / ".yuanli/releases/gold2-au"
            with patch.object(release.Path, "home", return_value=home), \
                    patch.object(release, "_code_inventory", return_value=("a" * 40, [("scripts/x.py", b"safe")], "b" * 64)), \
                    patch.object(release, "_safe_venv_files", return_value=[]), \
                    patch.object(release, "_venv_hash", return_value="c" * 64), \
                    patch.object(release, "_copy_venv", side_effect=release.ReleaseDenied("INJECTED_FAILURE")), \
                    patch.object(release.subprocess, "run") as runner:
                with self.assertRaisesRegex(release.ReleaseDenied, "INJECTED_FAILURE"):
                    release.prepare(runtime=runtime,
                                    base=base, stage_release=True)
                runner.assert_not_called()
            self.assertEqual(existing.read_bytes(), b"unchanged-loaded-job")
            self.assertEqual(list(base.iterdir()), [])

    def test_venv_rebinds_editable_install_and_shebang_without_copying_keys(self):
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            source = parent / "source"
            venv = source / ".venv"
            site = venv / "lib/python3.12/site-packages"
            bin_dir = venv / "bin"
            site.mkdir(parents=True)
            bin_dir.mkdir()
            pth_name = "__editable__.yuanli_invest-0.1.0.pth"
            (site / pth_name).write_text(str(source / "src") + "\n")
            (venv / "pyvenv.cfg").write_text("command = " + str(source / ".venv/bin/python") + "\n")
            (bin_dir / "pip").write_text("#!" + str(source / ".venv/bin/python") + "\n")
            (bin_dir / "pip").chmod(0o755)
            stage = parent / "stage"
            stage.mkdir()
            with patch.object(release, "ROOT", source):
                release._copy_venv(stage)
            copied = stage / ".venv"
            self.assertEqual((copied / "lib/python3.12/site-packages" / pth_name).read_text().strip(),
                             str(stage / "src"))
            self.assertNotIn(str(source), (copied / "pyvenv.cfg").read_text())
            self.assertTrue((copied / "bin/pip").read_text().startswith("#!" + str(stage)))
            self.assertEqual((copied / "bin/pip").stat().st_mode & 0o777, 0o700)
            self.assertEqual((copied / "pyvenv.cfg").stat().st_mode & 0o777, 0o600)

    def test_venv_rejects_private_file_and_desktop_link(self):
        with TemporaryDirectory() as temporary:
            venv = Path(temporary)
            (venv / ".env").write_text("never copy")
            with self.assertRaisesRegex(release.ReleaseDenied, "SENSITIVE_FILE_IN_VENV"):
                release._safe_venv_files(venv)
            (venv / ".env").unlink()
            link = venv / "desktop-code"
            link.symlink_to(release.ROOT / "scripts/gold_au_decision_worker.py")
            with self.assertRaisesRegex(release.ReleaseDenied, "DESKTOP_SYMLINK_IN_VENV"):
                release._safe_venv_files(venv)
            link.unlink()
            with TemporaryDirectory() as other:
                private = Path(other) / "external-private-fixture"
                private.write_text("do not follow")
                link.symlink_to(private)
                with self.assertRaisesRegex(release.ReleaseDenied, "EXTERNAL_VENV_SYMLINK_NOT_ALLOWLISTED"):
                    release._safe_venv_files(venv)

    def test_plist_contract_prevents_run_at_load_and_desktop_worker(self):
        stage = Path.home() / ".yuanli/releases/gold2-au/reviewed"
        runtime = Path.home() / ".yuanli/runtime/gold_au_decision"
        suffix, worker, _, hour, minute = release.WORKERS[0]
        valid = {
            "Label": "com.yuanli.gold2-au-" + suffix,
            "ProgramArguments": [str(stage / ".venv/bin/python"), str(stage / "scripts" / worker),
                                 "--runtime-dir", str(runtime), "--execute"],
            "WorkingDirectory": str(stage),
            "StartCalendarInterval": [{"Weekday": day, "Hour": hour, "Minute": minute}
                                      for day in range(1, 6)],
            "RunAtLoad": False,
            "StandardOutPath": str(runtime / "logs/shfe_stdout.log"),
            "StandardErrorPath": str(runtime / "logs/shfe_stderr.log"),
        }
        release.validate_candidate_plist(plistlib.loads(plistlib.dumps(valid)), stage=stage,
                                         runtime=runtime, label_suffix=suffix, worker=worker,
                                         hour=hour, minute=minute)
        for field, value in (("RunAtLoad", True),
                             ("ProgramArguments", [str(stage / ".venv/bin/python"),
                                                   str(release.ROOT / "scripts" / worker),
                                                   "--runtime-dir", str(runtime), "--execute"]),
                             ("StandardErrorPath", str(runtime / "logs/wrong.log")),
                             ("StandardOutPath", str(runtime / "logs/../other.log"))):
            bad = dict(valid)
            bad[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(release.ReleaseDenied, "CANDIDATE_PLIST"):
                release.validate_candidate_plist(bad, stage=stage, runtime=runtime,
                                                 label_suffix=suffix, worker=worker,
                                                 hour=hour, minute=minute)
        extra = dict(valid, KeepAlive=True)
        with self.assertRaisesRegex(release.ReleaseDenied, "CANDIDATE_PLIST"):
            release.validate_candidate_plist(extra, stage=stage, runtime=runtime,
                                             label_suffix=suffix, worker=worker, hour=hour, minute=minute)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
