"""Offline checks for a single exact temporary owner-controlled relay."""
import hashlib
import io
from pathlib import Path
import queue
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch
from scripts import youquant_python_runtime_recover_relay as relay


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.token = "x" * 40
        self.asset = {"url": relay.RELAY_URL, "size": 10,
                      "sha256": hashlib.sha256(b"abcdefghij").hexdigest()}

    def tearDown(self):
        self.temp.cleanup()

    def response(self, *, url=None, status=206, content_range="bytes 2-5/10", data=b"cdef"):
        result = io.BytesIO(data)
        result.status = status
        result.headers = {"Content-Range": content_range, "Content-Length": str(len(data))}
        result.geturl = lambda: relay.RELAY_URL if url is None else url
        return result

    def part(self, response, *, asset=None, token=None):
        opener = Mock()
        opener.open.return_value = response
        with patch.object(relay.urllib.request, "build_opener", return_value=opener), \
             patch.object(relay, "RELAY_TOKEN", self.token if token is None else token):
            result = relay.download_part(asset or self.asset, (0,2,5), self.root / "part-00.bin",
                                         time.monotonic()+100, threading.Event(), queue.Queue(maxsize=1024))
        return result, opener

    def test_exact_endpoint_header_and_30_second_timeout(self):
        result, opener = self.part(self.response())
        call = opener.open.call_args
        self.assertEqual(call.kwargs["timeout"], 30)
        self.assertEqual(call.args[0].full_url, relay.RELAY_URL)
        self.assertEqual(call.args[0].get_header("X-gold2-install-token"), self.token)
        self.assertEqual(call.args[0].get_header("Range"), "bytes=2-5")
        self.assertNotIn(self.token, repr(result))
        self.assertEqual(result["sha256"], hashlib.sha256(b"cdef").hexdigest())

    def test_all_redirects_are_rejected(self):
        with self.assertRaisesRegex(relay.InstallDenied, "RELAY_REDIRECT_DENIED"):
            relay._RelayNoRedirect().redirect_request(None,None,302,"",{},relay.RELAY_URL)

    def test_other_host_path_query_and_final_redirect_denied_before_file(self):
        for endpoint in (relay.RELAY_URL + "?anything=1", relay.RELAY_URL + "/", "https://example.com/"):
            with self.subTest(endpoint=endpoint), self.assertRaisesRegex(relay.InstallDenied, "RELAY_EXACT_URL_DENIED"):
                self.part(self.response(), asset={**self.asset, "url": endpoint})
            with self.subTest(final=endpoint), self.assertRaisesRegex(relay.InstallDenied, "RELAY_EXACT_FINAL_URL_DENIED"):
                self.part(self.response(url=endpoint))
            self.assertFalse((self.root / "part-00.bin").exists())

    def test_missing_invalid_token_denied_before_network(self):
        for token in ("", "a"*31, "a"*129, "a"*32 + "\n", "secret value"):
            with self.subTest(token_length=len(token)), \
                 patch.object(relay.urllib.request,"build_opener",side_effect=AssertionError("network")), \
                 patch.object(relay,"RELAY_TOKEN",token), \
                 self.assertRaisesRegex(relay.InstallDenied,"RELAY_TOKEN_REQUIRED"):
                relay.download_part(self.asset,(0,2,5),self.root/"part-00.bin",time.monotonic()+100,
                                    threading.Event(),queue.Queue())

    def test_range_status_and_content_range_are_strict(self):
        for kwargs, reason in (({"status":200},"PARALLEL_RANGE_UNSUPPORTED"),
                               ({"content_range":"bytes 0-3/10"},"PARALLEL_CONTENT_RANGE_MISMATCH"),
                               ({"content_range":"bytes 2-5/11"},"PARALLEL_CONTENT_RANGE_MISMATCH")):
            with self.subTest(reason=reason),self.assertRaisesRegex(relay.InstallDenied,reason):
                self.part(self.response(**kwargs))
            self.assertFalse((self.root/"part-00.bin").exists())

    def test_declared_package_sha_if_present_must_match(self):
        response=self.response()
        response.headers["X-Gold2-Package-Sha256"]="0"*64
        with self.assertRaisesRegex(relay.InstallDenied,"RELAY_DECLARED_DIGEST_MISMATCH"):
            self.part(response)
        self.assertFalse((self.root/"part-00.bin").exists())
        response=self.response()
        response.headers["X-Gold2-Package-Sha256"]=self.asset["sha256"]
        result,_=self.part(response)
        self.assertEqual(result["bytes"],4)

    def test_final_full_sha_is_required_before_unpack(self):
        seed=self.root/"seed";seed.write_bytes(b"ab")
        (self.root/"part-00.bin").write_bytes(b"cdefghix")
        with self.assertRaisesRegex(relay.InstallDenied,"PARALLEL_FINAL_SIZE_OR_SHA256_MISMATCH"):
            relay.merge_verify({"asset":self.asset},seed,self.root,{"parts":[{"index":0}]})

    def test_default_dry_run_has_no_token_and_no_network_or_write(self):
        self.assertEqual(relay.RELAY_TOKEN, "")
        self.assertEqual(relay.PARALLEL_MODE,"DRY_RUN")
        plan={"asset":self.asset,"recovery_target":str(self.root/"new")}
        with patch.object(relay,"parallel_plan",return_value=plan), \
             patch.object(relay,"copy_retained_partial",side_effect=AssertionError("write")), \
             patch.object(relay,"download_parts",side_effect=AssertionError("network")):
            result=relay.parallel_recover()
        self.assertNotIn(self.token,repr(result))
        self.assertFalse(result["network_access_performed"])
        self.assertFalse(result["file_write_performed"])

    def test_execute_missing_token_stops_before_mkdir(self):
        target=self.root/"new"
        with patch.object(relay,"parallel_plan",return_value={"recovery_target":str(target)}), \
             self.assertRaisesRegex(relay.InstallDenied,"RELAY_TOKEN_REQUIRED"):
            relay.parallel_recover(execute=True)
        self.assertFalse(target.exists())


if __name__=="__main__":unittest.main()
