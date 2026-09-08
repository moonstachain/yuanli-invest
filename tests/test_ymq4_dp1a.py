import importlib.util
import contextlib
import io
import json
import pathlib
import unittest
import urllib.error
import urllib.parse
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dp1a", ROOT / "scripts/ymq4_dp1a_reality_proof.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TestDP1A(unittest.TestCase):
    def test_initial_request_searches_history_and_asof_overrides_both_bounds(self):
        historical = urllib.parse.parse_qs(urllib.parse.urlsplit(MOD.fred_url("fixture")).query)
        self.assertEqual(historical["realtime_start"], [MOD.OBS_START])
        self.assertGreater(historical["realtime_end"][0], "2020-03-11")
        asof = urllib.parse.parse_qs(urllib.parse.urlsplit(MOD.fred_url(
            "fixture", output_type=1, realtime_start="2020-03-11", realtime_end="2020-03-11")).query)
        self.assertEqual(asof["realtime_start"], ["2020-03-11"])
        self.assertEqual(asof["realtime_end"], ["2020-03-11"])

    def test_future_release_is_rejected(self):
        raw = json.dumps({"observations": [{"date": MOD.OBS_START,
            "realtime_start": "9999-12-31", "value": "259.050"}]}).encode()
        with self.assertRaisesRegex(RuntimeError, "future"):
            MOD.parse_initial(raw)

    def test_same_value_from_wrong_observation_is_rejected(self):
        initial = {"known_as_of": "2020-03-11", "observation_date": MOD.OBS_START, "value": 259.05}
        body = json.dumps({"observations": [{"date": "2020-01-01", "value": "259.050"}]}).encode()
        with patch.object(MOD, "request_bytes", return_value=(200, {}, body)):
            with self.assertRaisesRegex(RuntimeError, "date mismatch"):
                MOD.crosscheck_asof("fixture", initial)

    def test_http_failure_omits_key_and_provider_body(self):
        url = "https://x.test/path?api_key=synthetic-key"
        error = urllib.error.HTTPError(url, 403, "denied", {}, io.BytesIO(b"private-response"))
        with patch.object(MOD.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(RuntimeError) as got:
                MOD.request_bytes(url)
        self.assertIn("HTTP 403", str(got.exception))
        self.assertNotIn("synthetic-key", str(got.exception))
        self.assertNotIn("private-response", str(got.exception))
        self.assertTrue(got.exception.__suppress_context__)

    def test_http_failure_keeps_only_non_secret_provider_error(self):
        url = "https://x.test/path?api_key=synthetic-key"
        body = json.dumps({"error_code": 400, "error_message": "api_key is invalid"}).encode()
        error = urllib.error.HTTPError(url, 400, "denied", {}, io.BytesIO(body))
        with patch.object(MOD.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(RuntimeError) as got:
                MOD.request_bytes(url)
        self.assertIn("provider_code=400", str(got.exception))
        self.assertIn("api_key is invalid", str(got.exception))
        self.assertNotIn("synthetic-key", str(got.exception))

    def test_failure_receipt_redacts_all_credentials_without_traceback(self):
        names = ("FRED_API_KEY", "YMQ4_SUPABASE_SECRET_KEY",
                 "YMQ4_SUPABASE_S3_ACCESS_KEY_ID", "YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")
        secrets = {name: f"synthetic/{i}+value" for i, name in enumerate(names)}
        message = " ".join(part for value in secrets.values()
                           for part in (value, urllib.parse.quote(value, safe="")))
        output = io.StringIO()
        with patch.dict(MOD.os.environ, secrets), patch.object(MOD, "main", side_effect=RuntimeError(message)):
            with contextlib.redirect_stdout(output):
                self.assertEqual(MOD.run(), 1)
        receipt = json.loads(output.getvalue())
        self.assertEqual(receipt["status"], "FAIL_CLOSED")
        for value in secrets.values():
            self.assertNotIn(value, output.getvalue())
            self.assertNotIn(urllib.parse.quote(value, safe=""), output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())

    def test_redacts_api_key(self):
        url = "https://x.test/path?series_id=CPIAUCSL&api_key=SECRET123&output_type=4"
        out = MOD.redact_api_key(url)
        self.assertNotIn("SECRET123", out)
        self.assertIn("REDACTED", out)

    def test_parse_initial_four_clocks(self):
        raw = json.dumps({"observations": [{
            "realtime_start": "2020-03-11",
            "realtime_end": "2020-03-11",
            "date": "2020-02-01",
            "value": "259.050"
        }]}).encode()
        got = MOD.parse_initial(raw)
        self.assertEqual(got["observation_date"], "2020-02-01")
        self.assertEqual(got["release_date"], "2020-03-11")
        self.assertEqual(got["vintage_date"], "2020-03-11")
        self.assertEqual(got["known_as_of"], "2020-03-11")

    def test_parse_initial_fails_without_realtime_start(self):
        raw = json.dumps({"observations": [{"date": "2020-02-01", "value": "259.050"}]}).encode()
        with self.assertRaises(RuntimeError):
            MOD.parse_initial(raw)

    def test_modern_secret_is_apikey_only(self):
        headers = MOD.rpc_headers("sb_secret_example_key")
        self.assertEqual(headers["apikey"], "sb_secret_example_key")
        self.assertNotIn("Authorization", headers)

    def test_legacy_service_role_is_rejected(self):
        with self.assertRaises(RuntimeError):
            MOD.rpc_headers("eyJhbGciOiJIUzI1NiJ9.legacy.service_role")


if __name__ == "__main__":
    unittest.main()
