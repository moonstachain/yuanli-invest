"""Offline tests: host-only readback and bounded, pinned runtime installation."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts import youquant_python_host_readonly as probe
from scripts import youquant_python_runtime_install as installer


class ProbeTests(unittest.TestCase):
    def test_fixed_absolute_allowlist_only(self):
        with patch.object(probe.os.path, "isfile", return_value=False) as checked:
            result = probe.host_facts()
        self.assertEqual(len(result["allowed_interpreters"]), 9)
        self.assertEqual([call.args[0] for call in checked.call_args_list], list(probe.INTERPRETER_PATHS))
        for name in ("network_access_performed", "file_write_performed", "environment_access_performed",
                     "account_access_performed", "broker_action_authorized", "production_started"):
            self.assertFalse(result[name])

    def test_probe_isolated_subprocess_no_inherited_environment(self):
        with patch.object(probe.os.path, "isfile", return_value=True), \
                patch.object(probe.os, "access", return_value=True), \
                patch.object(probe.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "[3,12,14]", "")) as run:
            result = probe.host_facts()
        self.assertEqual(run.call_count, 9)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["env"], {})
            self.assertEqual(call.kwargs["timeout"], 3)
            self.assertEqual(call.args[0][1:3], ["-I", "-B"])
        self.assertTrue(all(item["meets_production_minimum"] for item in result["allowed_interpreters"]))

    def test_failed_or_invalid_versions_do_not_qualify(self):
        for value in ("[3,9,2]", "[true,12,14]", "not-json"):
            with self.subTest(value=value), patch.object(probe.os.path, "isfile", return_value=True), \
                    patch.object(probe.os, "access", return_value=True), \
                    patch.object(probe.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, value, "")):
                result = probe.host_facts()
            self.assertFalse(any(item.get("meets_production_minimum") for item in result["allowed_interpreters"]))

    def test_timeout_is_bounded_and_sanitized(self):
        with patch.object(probe.os.path, "isfile", return_value=True), \
                patch.object(probe.os, "access", return_value=True), \
                patch.object(probe.subprocess, "run", side_effect=subprocess.TimeoutExpired("private", 3)):
            result = probe.host_facts()
        self.assertTrue(all(item["reason"] == "TimeoutExpired" for item in result["allowed_interpreters"]))
        self.assertNotIn("private", json.dumps(result))

    def test_main_logs_once_without_broker_or_runtime(self):
        logs = []
        with patch.object(probe, "Log", lambda *args: logs.append(args), create=True), \
                patch.object(probe.os.path, "isfile", return_value=False):
            probe.main()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "GOLD2_PYTHON_HOST_READONLY")


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.uid = os.geteuid()
        self.host = {"system": "Linux", "machine": "x86_64", "libc": "glibc 2.31", "uid": self.uid}
        self.base = str(self.root / ".yuanli-gold2-runtime")

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, **kwargs):
        with patch.object(installer, "_host", return_value=self.host), patch.object(installer.os, "getcwd", return_value=str(self.root)):
            return installer.installation_plan(kwargs.pop("base", self.base),
                                               expected_machine=kwargs.pop("expected_machine", "x86_64"),
                                               expected_uid=kwargs.pop("expected_uid", self.uid), **kwargs)

    def make_tar(self, members):
        path = self.root / "archive.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, kind, content in members:
                item = tarfile.TarInfo(name)
                if kind == "file":
                    data = content.encode()
                    item.size = len(data)
                    item.mode = 0o755
                    archive.addfile(item, io.BytesIO(data))
                elif kind == "symlink":
                    item.type = tarfile.SYMTYPE
                    item.linkname = content
                    archive.addfile(item)
                elif kind == "hardlink":
                    item.type = tarfile.LNKTYPE
                    item.linkname = content
                    archive.addfile(item)
                elif kind == "fifo":
                    item.type = tarfile.FIFOTYPE
                    archive.addfile(item)
                elif kind == "dir":
                    item.type = tarfile.DIRTYPE
                    archive.addfile(item)
        return path

    def test_fixed_official_release_pin(self):
        result = self.plan()
        self.assertEqual(result["python_version"], "3.12.14")
        self.assertEqual(result["asset"]["sha256"], "269b2c99e4db15b242bf01832f4fea1e8f1a664f273cff519393f296e9820b41")
        self.assertEqual(result["asset"]["size"], 34270188)
        self.assertNotIn("latest", result["asset"]["url"])
        self.assertFalse(Path(result["target"]).exists())

    def test_wrong_system_arch_libc_and_host_pins_fail_closed(self):
        cases = (("system", "Darwin", "UNSUPPORTED_SYSTEM_OR_ARCHITECTURE"),
                 ("machine", "i686", "UNSUPPORTED_SYSTEM_OR_ARCHITECTURE"),
                 ("libc", "glibc 2.16", "GLIBC_2_17_REQUIRED"),
                 ("libc", "musl 1.2.5", "GLIBC_2_17_REQUIRED"),
                 ("uid", None, "PROCESS_UID_REQUIRED"))
        for field, value, reason in cases:
            with self.subTest(field=field, value=value):
                old = self.host[field]; self.host[field] = value
                with self.assertRaisesRegex(installer.InstallDenied, reason): self.plan()
                self.host[field] = old
        with self.assertRaisesRegex(installer.InstallDenied, "HOST_PIN_MISMATCH"):
            self.plan(expected_uid=self.uid + 1)
        with self.assertRaisesRegex(installer.InstallDenied, "REVIEWED_HOST_PINS_REQUIRED"):
            self.plan(expected_machine=None)

    def test_root_process_explicitly_bound_and_limited_to_fixed_dedicated_path(self):
        self.host["uid"] = 0
        with patch.object(installer.os, "access", return_value=True):
            plan = self.plan(base="/opt/yuanli-gold2-runtime", expected_uid=0)
        self.assertTrue(plan["process_is_root"])
        self.assertFalse(plan["system_python_modified"])
        with self.assertRaisesRegex(installer.InstallDenied, "DEDICATED_INSTALL_BASE_REQUIRED"):
            self.plan(expected_uid=0)

    def test_arbitrary_and_system_paths_rejected(self):
        for path in ("/usr", "/usr/bin", "/opt", "/root", ".yuanli-gold2-runtime"):
            with self.subTest(path=path), self.assertRaisesRegex(installer.InstallDenied, "DEDICATED_INSTALL_BASE_REQUIRED"):
                self.plan(base=path)

    def test_symlink_and_unsafe_existing_base_rejected(self):
        base = Path(self.base)
        base.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(installer.InstallDenied, "SYMLINK_INSTALL_PATH"): self.plan()
        base.unlink(); base.mkdir(mode=0o755)
        with self.assertRaisesRegex(installer.InstallDenied, "UNSAFE_EXISTING_DEDICATED_BASE"): self.plan()

    def test_existing_target_never_overwritten(self):
        result = self.plan()
        Path(result["base"]).mkdir(mode=0o700)
        Path(result["target"]).mkdir(mode=0o700)
        with self.assertRaisesRegex(installer.InstallDenied, "INSTALL_TARGET_ALREADY_EXISTS"): self.plan()

    def test_dry_run_no_network_or_write(self):
        with patch.object(installer, "_host", return_value=self.host), \
                patch.object(installer.os, "getcwd", return_value=str(self.root)), \
                patch.object(installer, "download_verified", side_effect=AssertionError("network reached")):
            result = installer.install_runtime(self.base, expected_machine="x86_64", expected_uid=self.uid)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse(Path(self.base).exists())

    def test_download_hosts_https_only(self):
        for url in ("http://github.com/asset", "https://evil.example/asset", "https://github.com.evil.example/asset",
                    "https://user:password@github.com/asset", "https://github.com:8443/asset"):
            self.assertFalse(installer._download_url_allowed(url))
        self.assertTrue(installer._download_url_allowed("https://release-assets.githubusercontent.com/asset"))

    def test_hash_mismatch_prevents_unpack_or_interpreter(self):
        with patch.object(installer, "_host", return_value=self.host), \
                patch.object(installer.os, "getcwd", return_value=str(self.root)), \
                patch.object(installer, "download_verified", side_effect=installer.InstallDenied("ARCHIVE_SIZE_OR_SHA256_MISMATCH")), \
                patch.object(installer, "unpack_verified", side_effect=AssertionError("unpack reached")), \
                patch.object(installer, "smoke_interpreter", side_effect=AssertionError("binary reached")):
            with self.assertRaisesRegex(installer.InstallDenied, "SHA256_MISMATCH"):
                installer.install_runtime(self.base, expected_machine="x86_64", expected_uid=self.uid, execute=True)
        self.assertTrue(Path(self.base).exists())

    def download_response(self, payload):
        response = io.BytesIO(payload)
        response.geturl = lambda: "https://release-assets.githubusercontent.com/fixed-asset"
        opener = unittest.mock.Mock()
        opener.open.return_value = response
        return opener

    def test_download_exact_bytes_and_hash_checked(self):
        data = b"verified fixed bytes"
        asset = {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/20260924/fixed",
                 "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        target = self.root / "download.tar.gz"
        with patch.object(installer.urllib.request, "build_opener", return_value=self.download_response(data)):
            result = installer.download_verified(asset, target)
        self.assertEqual(result, {"bytes": len(data), "sha256": asset["sha256"]})
        self.assertEqual(target.read_bytes(), data)

    def test_download_real_hash_short_read_and_size_limit_branches(self):
        for name, size, digest, reason in (("hash", 4, "0" * 64, "ARCHIVE_SIZE_OR_SHA256_MISMATCH"),
                                         ("short", 5, hashlib.sha256(b"data").hexdigest(), "ARCHIVE_SIZE_OR_SHA256_MISMATCH"),
                                         ("over", 3, hashlib.sha256(b"data").hexdigest(), "DOWNLOAD_SIZE_EXCEEDED")):
            asset = {"url": "https://github.com/fixed-asset", "size": size, "sha256": digest}
            with self.subTest(name=name), \
                    patch.object(installer.urllib.request, "build_opener", return_value=self.download_response(b"data")), \
                    self.assertRaisesRegex(installer.InstallDenied, reason):
                installer.download_verified(asset, self.root / name)

    def test_download_deadline_bounded(self):
        asset = {"url": "https://github.com/fixed-asset", "size": 4, "sha256": hashlib.sha256(b"data").hexdigest()}
        with patch.object(installer.urllib.request, "build_opener", return_value=self.download_response(b"data")), \
                patch.object(installer.time, "monotonic", side_effect=[0, 121]), \
                self.assertRaisesRegex(installer.InstallDenied, "DOWNLOAD_DEADLINE_EXCEEDED"):
            installer.download_verified(asset, self.root / "download.tar.gz")

    def test_traversal_absolute_and_other_root_rejected_before_writes(self):
        for path in ("../escape", "/absolute", "python/../../escape", "different/bin/python", "python\\escape"):
            with self.subTest(path=path):
                source = self.make_tar([(path, "file", "payload")])
                destination = self.root / "unpacked"; destination.mkdir(exist_ok=True)
                with self.assertRaisesRegex(installer.InstallDenied, "ARCHIVE_PATH_DENIED"):
                    installer.unpack_verified(source, destination)
                self.assertEqual(list(destination.iterdir()), [])

    def test_symlink_escape_hardlink_fifo_duplicate_rejected(self):
        cases = (([("python/bin/link", "symlink", "../../../escape")], "ARCHIVE_LINK_ESCAPE"),
                 ([("python/bin/link", "symlink", "/etc/passwd")], "ARCHIVE_LINK_DENIED"),
                 ([("python/bin/link", "hardlink", "python/bin/python3.12")], "ARCHIVE_SPECIAL_FILE_DENIED"),
                 ([("python/fifo", "fifo", "")], "ARCHIVE_SPECIAL_FILE_DENIED"),
                 ([("python/a", "file", "a"), ("python/a", "file", "b")], "ARCHIVE_DUPLICATE_PATH"),
                 ([("python/other", "file", "x"), ("python/lib", "symlink", "other"), ("python/lib/evil", "file", "x")], "ARCHIVE_LINK_ANCESTOR_DENIED"))
        for members, reason in cases:
            with self.subTest(reason=reason):
                source = self.make_tar(members)
                destination = self.root / "unpacked"; destination.mkdir(exist_ok=True)
                with self.assertRaisesRegex(installer.InstallDenied, reason): installer.unpack_verified(source, destination)
                self.assertEqual(list(destination.iterdir()), [])

    def test_link_target_directory_symlink_dotdot_escape_denied(self):
        # Lexically python/c stays in the archive. Physically b points to python
        # so b/../c would escape its root. Validation must reject before writes.
        source = self.make_tar([("python", "dir", ""), ("python/c", "file", "x"),
                                ("python/b", "symlink", "."),
                                ("python/a", "symlink", "b/../c")])
        destination = self.root / "unpacked"; destination.mkdir()
        with self.assertRaisesRegex(installer.InstallDenied, "ARCHIVE_LINK_TARGET_ANCESTOR_DENIED"):
            installer.unpack_verified(source, destination)
        self.assertEqual(list(destination.iterdir()), [])

    def test_safe_dotdot_alias_to_regular_file_is_retained(self):
        source = self.make_tar([("python/share/terminfo/a/item", "file", "trusted data"),
                                ("python/share/terminfo/b/alias", "symlink", "../a/item")])
        destination = self.root / "unpacked"; destination.mkdir(mode=0o700)
        installer.unpack_verified(source, destination)
        self.assertEqual((destination / "python/share/terminfo/b/alias").read_text(), "trusted data")

    def test_missing_and_cyclic_link_targets_denied(self):
        for members, reason in (([("python/a", "symlink", "missing")], "ARCHIVE_LINK_TARGET_MISSING"),
                                ([("python/a", "symlink", "b"), ("python/b", "symlink", "a")], "ARCHIVE_LINK_CYCLE_OR_DEPTH_EXCEEDED")):
            with self.subTest(reason=reason):
                source = self.make_tar(members)
                destination = self.root / "unpacked"; destination.mkdir(exist_ok=True)
                with self.assertRaisesRegex(installer.InstallDenied, reason): installer.unpack_verified(source, destination)
                self.assertEqual(list(destination.iterdir()), [])

    def test_member_count_and_unpacked_size_caps(self):
        source = self.make_tar([("python/a", "file", "1234"), ("python/b", "file", "1234")])
        destination = self.root / "unpacked"; destination.mkdir()
        for name, value, reason in (("MAX_MEMBERS", 1, "ARCHIVE_MEMBER_LIMIT_EXCEEDED"),
                                    ("MAX_MEMBER_BYTES", 3, "ARCHIVE_MEMBER_SIZE_EXCEEDED"),
                                    ("MAX_UNPACKED_BYTES", 7, "ARCHIVE_UNPACK_LIMIT_EXCEEDED")):
            with self.subTest(name=name), patch.object(installer, name, value), self.assertRaisesRegex(installer.InstallDenied, reason):
                installer.unpack_verified(source, destination)
        self.assertEqual(list(destination.iterdir()), [])

    def test_safe_archive_internal_link_no_outside_writes(self):
        source = self.make_tar([("python/bin/python3.12", "file", "fixed payload"),
                                ("python/bin/python3", "symlink", "python3.12")])
        destination = self.root / "unpacked"; destination.mkdir(mode=0o700)
        result = installer.unpack_verified(source, destination)
        self.assertEqual(result["members"], 2)
        self.assertEqual((destination / "python/bin/python3").read_text(), "fixed payload")
        self.assertTrue(os.access(str(destination / "python/bin/python3.12"), os.X_OK))

    def test_execution_receipt_only_after_exact_binary_smoke(self):
        source_bytes = self.make_tar([("python/bin/python3.12", "file", "not executed")]).read_bytes()
        def download(asset, destination):
            destination.write_bytes(source_bytes)
            return {"bytes": len(source_bytes), "sha256": hashlib.sha256(source_bytes).hexdigest()}
        with patch.object(installer, "_host", return_value=self.host), \
                patch.object(installer.os, "getcwd", return_value=str(self.root)), \
                patch.object(installer, "download_verified", side_effect=download), \
                patch.object(installer, "smoke_interpreter", return_value={"version": [3,12,14], "stdlib_smoke": "PASS"}):
            result = installer.install_runtime(self.base, expected_machine="x86_64", expected_uid=self.uid, execute=True)
        self.assertEqual(result["status"], "INSTALLED_NOT_PRODUCTION_ENABLED")
        self.assertFalse(result["production_started"])
        self.assertTrue((Path(result["plan"]["target"]) / "install-receipt.json").is_file())

    def test_default_main_only_dry_run_and_no_broker_imports(self):
        logs = []
        with patch.object(installer, "Log", lambda *args: logs.append(args), create=True), \
                patch.object(installer, "install_runtime", return_value={"status": "DRY_RUN"}) as operation:
            installer.main()
        self.assertFalse(operation.call_args.kwargs["execute"])
        for module in (probe, installer):
            source = Path(module.__file__).read_text()
            tree = ast.parse(source, feature_version=(3,9))
            names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
            self.assertFalse(names & {"exchange", "exchanges", "GetAccount", "GetPositions", "GetOrders", "eval"})
            self.assertNotIn("os.environ", source)
            self.assertNotIn("extractall(", source)
        self.assertEqual(len(logs), 1)


if __name__ == "__main__":
    unittest.main()
