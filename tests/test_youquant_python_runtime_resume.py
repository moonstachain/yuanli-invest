"""No real network, install or credentials: bounded range-recovery branches."""
import ast
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import youquant_python_runtime_resume as resume


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.seed = self.root / "prefix.partial"; self.seed.write_bytes(b"abc")
        self.plan = {"original": {"partial_bytes": 3},
                     "asset": {"size": 6, "sha256": hashlib.sha256(b"abcdef").hexdigest(),
                               "url": resume.ASSET_URL}}

    def tearDown(self): self.temp.cleanup()

    def response(self, data=b"def", *, status=206, content_range="bytes 3-5/6", url="https://release-assets.githubusercontent.com/fixed"):
        result = io.BytesIO(data)
        result.status = status
        result.headers = {"Content-Length": str(len(data))}
        if content_range is not None: result.headers["Content-Range"] = content_range
        result.geturl = lambda: url
        return result

    def call_download(self, response, *, progress=None, plan=None):
        opener = Mock(); opener.open.return_value = response
        with patch.object(resume.urllib.request, "build_opener", return_value=opener):
            result = resume.resume_download(plan or self.plan, self.seed, self.root / "complete.tar.gz", progress=progress or (lambda *args: None))
        self.opener = opener
        return result

    def test_range_tail_matches_prefix_and_fixed_digest(self):
        events = []
        result = self.call_download(self.response(), progress=lambda *args: events.append(args))
        self.assertEqual(result["mode"], "HTTPS_RANGE_RETAINED_PREFIX")
        self.assertEqual((self.root / "complete.tar.gz").read_bytes(), b"abcdef")
        self.assertEqual(self.seed.read_bytes(), b"abc")
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.get_header("Range"), "bytes=3-")
        self.assertEqual(events[-1], ("DOWNLOAD_VERIFIED", 6, 6))

    def test_range_unsupported_new_full_download_preserves_seed(self):
        result = self.call_download(self.response(b"abcdef", status=200, content_range=None))
        self.assertEqual(result["mode"], "HTTPS_FULL_DOWNLOAD_RANGE_UNSUPPORTED")
        self.assertEqual((self.root / "complete.tar.gz").read_bytes(), b"abcdef")
        self.assertEqual(self.seed.read_bytes(), b"abc")

    def test_bad_content_range_denied_before_archive_write(self):
        for value in (None, "bytes 0-5/6", "bytes 3-5/7", "bytes 3-4/6", "invalid"):
            with self.subTest(value=value), self.assertRaisesRegex(resume.InstallDenied, "RECOVERY_CONTENT_RANGE_MISMATCH"):
                self.call_download(self.response(content_range=value))
            self.assertFalse((self.root / "complete.tar.gz").exists())

    def test_content_length_wrong_host_and_status_denied(self):
        for response, reason in ((self.response(b"de"), "RECOVERY_CONTENT_LENGTH_MISMATCH"),
                                 (self.response(url="https://evil.example/file"), "RECOVERY_FINAL_HOST_DENIED"),
                                 (self.response(status=201), "RECOVERY_HTTP_STATUS_DENIED")):
            with self.subTest(reason=reason), self.assertRaisesRegex(resume.InstallDenied, reason): self.call_download(response)
            self.assertFalse((self.root / "complete.tar.gz").exists())

    def test_final_digest_mismatch_never_qualifies(self):
        with self.assertRaisesRegex(resume.InstallDenied, "RECOVERY_FINAL_SIZE_OR_SHA256_MISMATCH"):
            self.call_download(self.response(b"xyz"))
        self.assertEqual(self.seed.read_bytes(), b"abc")

    def test_short_read_and_exceeded_size_denied(self):
        for data, reason in ((b"de", "RECOVERY_FINAL_SIZE_OR_SHA256_MISMATCH"),
                             (b"defg", "RECOVERY_SIZE_EXCEEDED")):
            response = self.response(data); response.headers = {"Content-Range": "bytes 3-5/6"}
            with self.subTest(data=data), self.assertRaisesRegex(resume.InstallDenied, reason): self.call_download(response)
            (self.root / "complete.tar.gz").unlink()

    def test_completed_copy_uses_no_network_but_requires_digest(self):
        self.seed.write_bytes(b"abcdef"); self.plan["original"]["partial_bytes"] = 6
        with patch.object(resume.urllib.request, "build_opener", side_effect=AssertionError("network reached")):
            result = resume.resume_download(self.plan, self.seed, self.root / "complete.tar.gz", progress=lambda *args: None)
        self.assertEqual(result["mode"], "VERIFIED_COMPLETE_RETAINED_COPY")

    def test_deadline_and_seed_length_guard(self):
        with patch.object(resume.time, "monotonic", side_effect=[0, 601]), \
                self.assertRaisesRegex(resume.InstallDenied, "RECOVERY_DOWNLOAD_DEADLINE_EXCEEDED"):
            self.call_download(self.response())
        (self.root / "complete.tar.gz").unlink()
        self.seed.write_bytes(b"ab")
        with self.assertRaisesRegex(resume.InstallDenied, "RECOVERY_SEED_SIZE_MISMATCH"):
            self.call_download(self.response())

    def test_dry_run_never_creates_directory_or_network(self):
        plan = {**self.plan, "recovery_target": str(self.root / "new-runtime")}
        with patch.object(resume, "recovery_plan", return_value=plan), \
                patch.object(resume, "copy_retained_partial", side_effect=AssertionError("write reached")), \
                patch.object(resume, "resume_download", side_effect=AssertionError("network reached")):
            result = resume.recover_runtime()
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse(Path(plan["recovery_target"]).exists())

    def test_hash_failure_cannot_reach_unpack_or_smoke(self):
        plan = {**self.plan, "recovery_target": str(self.root / "new-runtime")}
        with patch.object(resume, "recovery_plan", return_value=plan), \
                patch.object(resume, "copy_retained_partial", return_value={}), \
                patch.object(resume, "resume_download", side_effect=resume.InstallDenied("RECOVERY_FINAL_SIZE_OR_SHA256_MISMATCH")), \
                patch.object(resume, "unpack_verified", side_effect=AssertionError("unpack reached")), \
                patch.object(resume, "smoke_interpreter", side_effect=AssertionError("binary reached")), \
                self.assertRaisesRegex(resume.InstallDenied, "SHA256_MISMATCH"):
            resume.recover_runtime(execute=True)

    def test_default_main_inert_and_no_environment_or_broker(self):
        with patch.object(resume, "Log", lambda *args: None, create=True), \
                patch.object(resume, "recover_runtime", return_value={"status": "DRY_RUN"}) as call:
            resume.main()
        self.assertFalse(call.call_args.kwargs["execute"])
        source = Path(resume.__file__).read_text()
        ast.parse(source, feature_version=(3,9))
        self.assertNotIn("os.environ", source)
        self.assertNotIn("GetAccount", source)
        self.assertNotIn("GOLD2_SIMNOW_RUNTIME", source)


if __name__ == "__main__": unittest.main()
