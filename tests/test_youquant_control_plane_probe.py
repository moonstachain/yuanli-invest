"""Offline tests for the read-only YouQuant control-plane probe."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import hashlib
import json
import os
from pathlib import Path
import ssl
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.request import HTTPSHandler, ProxyHandler


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youquant_control_plane_probe as probe  # noqa: E402


ACCESS_KEY = "a" * 32
SECRET_KEY = "s" * 32
ENV = {probe.ACCESS_KEY_ENV: ACCESS_KEY, probe.SECRET_KEY_ENV: SECRET_KEY}


def envelope(result):
    return json.dumps({"code": 0, "data": {"result": result, "error": None}},
                      ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class FakeResponse:
    def __init__(self, body, *, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self.read_limits = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        self.read_limits.append(limit)
        return self.body[:limit]


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.forms = []

    def open(self, request, timeout):
        assert timeout == probe.TIMEOUT_SECONDS
        assert request.full_url == probe.API_URL
        assert request.get_method() == "POST"
        assert "?" not in request.full_url
        assert request.get_header("Content-type") == "application/x-www-form-urlencoded"
        self.forms.append(parse_qs(request.data.decode("ascii"), strict_parsing=True))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class ControlPlaneProbeTests(unittest.TestCase):
    def test_default_dry_run_does_not_read_env_or_open_network(self):
        class PoisonEnv(dict):
            def get(self, key):
                raise AssertionError("dry-run inspected environment")

        result = probe.run_probe(robot_id=123, include_robot_list=True,
                                 include_node_list=True, env=PoisonEnv(),
                                 opener=object())
        self.assertEqual(result["status"], "DRY_RUN_NO_NETWORK")
        self.assertEqual(result["planned_methods"], ["GetPlatformList", "GetRobotDetail",
                                                      "GetRobotList", "GetNodeList"])
        self.assertFalse(result["network_attempted"])
        self.assertFalse(result["broker_connection_verified"])

    def test_token_post_read_only_summary_hash_and_monotonic_nonce(self):
        platform_raw = envelope({"all": 1, "platforms": [{
            "id": 321, "eid": "Futures_CTP", "name": "private-account-name",
            "profiles": json.dumps({"BrokerId": "9999", "TDFront": "tcp://182.254.243.31:30001",
                                    "MDFront": "182.254.243.31:30011",
                                    "Password": "secret-broker-password"})}]})
        robot_raw = envelope({"robot": {"id": 123, "status": 1,
                               "strategy_exchange_pairs": '[60,[321],["FUTURES"]]',
                               "username": "private-account-name"}})
        robot_list_raw = envelope({"all": 3, "robots": [{"id": 123, "status": 1}]})
        node_raw = envelope({"all": 1, "nodes": [{"id": 1, "online": True,
                                                    "host": "private-host"}]})
        opener = FakeOpener([FakeResponse(value) for value in
                             [platform_raw, robot_raw, robot_list_raw, node_raw]])
        result = probe.run_probe(execute=True, robot_id=123, include_robot_list=True,
                                 include_node_list=True, env=ENV, opener=opener,
                                 clock_ns=lambda: 1_800_000_000_000_000_000)
        self.assertEqual(result["status"], "READ_ONLY_CONTROL_PLANE_OBSERVED")
        self.assertFalse(result["broker_connection_verified"])
        reports = result["reports"]
        self.assertEqual(reports[0]["ctp_first_normal_config_match_count"], 1)
        self.assertEqual(reports[1]["bound_to_added_ctp_object_in_response"], True)
        self.assertEqual(reports[2]["robot_count"], 3)
        self.assertFalse(reports[2]["list_complete"])
        self.assertEqual(reports[3]["node_count"], 1)
        self.assertEqual(reports[0]["raw_response_sha256"],
                         "sha256:" + hashlib.sha256(platform_raw).hexdigest())
        self.assertEqual([int(form["nonce"][0]) for form in opener.forms],
                         [1_800_000_000_000 + index for index in range(4)])
        for form, method in zip(opener.forms, result["reports"]):
            self.assertEqual(set(form), {"version", "access_key", "method", "args", "nonce", "sign"})
            self.assertEqual(form["method"], [method["method"]])
            self.assertEqual(form["access_key"], [ACCESS_KEY])
            signed = (f'1.0|{method["method"]}|{form["args"][0]}|'
                      f'{form["nonce"][0]}|{SECRET_KEY}')
            self.assertEqual(form["sign"], [hashlib.md5(signed.encode()).hexdigest()])
            self.assertNotIn("secret_key", form)
        safe_text = json.dumps(result)
        for forbidden in (ACCESS_KEY, SECRET_KEY, "secret-broker-password",
                          "private-account-name", "private-host"):
            self.assertNotIn(forbidden, safe_text)

    def test_method_allowlist_and_argument_shapes_block_writes(self):
        for method in ("CommandRobot", "NewRobot", "StopRobot", "GetExchangeList"):
            with self.subTest(method=method), self.assertRaisesRegex(
                    probe.ProbeDenied, "METHOD_OR_NONCE_NOT_ALLOWED"):
                probe._signed_form(method, [], ACCESS_KEY, SECRET_KEY, 100)
        with self.assertRaisesRegex(probe.ProbeDenied, "METHOD_ARGS_NOT_ALLOWED"):
            probe._signed_form("GetPlatformList", [123], ACCESS_KEY, SECRET_KEY, 100)
        with self.assertRaisesRegex(probe.ProbeDenied, "ROBOT_ID_REQUIRED"):
            probe._signed_form("GetRobotDetail", [], ACCESS_KEY, SECRET_KEY, 100)

    def test_verified_transport_does_not_use_proxy_or_redirect(self):
        with patch.object(probe, "build_opener", wraps=probe.build_opener) as builder:
            opener = probe._verified_opener()
        proxy = next(item for item in builder.call_args.args if isinstance(item, ProxyHandler))
        self.assertEqual(proxy.proxies, {})
        self.assertTrue(any(isinstance(item, probe._NoRedirect) for item in opener.handlers))
        https = next(item for item in opener.handlers if isinstance(item, HTTPSHandler))
        self.assertEqual(https._context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(https._context.check_hostname)

    def test_fail_closed_on_http_size_json_and_schema(self):
        cases = [
            (FakeResponse(b"{}", status=302), "API_HTTP_STATUS_REJECTED"),
            (FakeResponse(b"{}", headers={"Content-Length": str(probe.MAX_RESPONSE_BYTES + 1)}),
             "API_RESPONSE_OVERSIZED"),
            (FakeResponse(b"X" * (probe.MAX_RESPONSE_BYTES + 1)),
             "API_RESPONSE_EMPTY_OR_OVERSIZED"),
            (FakeResponse(b"\xff"), "API_JSON_INVALID"),
            (FakeResponse(b'{"code":0,"code":0,"data":{}}'), "API_JSON_DUPLICATE_KEY"),
            (FakeResponse(b'{"code":NaN,"data":{}}'), "API_JSON_NONFINITE"),
            (FakeResponse(b'{"code":4,"data":null}'), "API_ENVELOPE_REJECTED"),
            (FakeResponse(envelope({"all": 1, "platforms": "bad"})), "API_LIST_SCHEMA_REJECTED"),
        ]
        for response, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(probe.ProbeDenied) as raised:
                    probe.run_probe(execute=True, env=ENV, opener=FakeOpener([response]))
                self.assertEqual(raised.exception.code, code)

    def test_unknown_profile_shape_and_ephemeral_binding_do_not_verify(self):
        platform = envelope({"all": 1, "platforms": [{"id": 1, "eid": "Futures_CTP",
                                                     "profiles": "..."}]})
        robot = envelope({"robot": {"id": 123, "status": 1,
                                    "strategy_exchange_pairs": '[60,[-100],["FUTURES_CTP"]]'}})
        result = probe.run_probe(execute=True, robot_id=123, env=ENV,
                                 opener=FakeOpener([FakeResponse(platform), FakeResponse(robot)]))
        self.assertEqual(result["reports"][0]["ctp_profile_direct_shape_count"], 0)
        self.assertEqual(result["reports"][0]["ctp_first_normal_config_match_count"], 0)
        self.assertFalse(result["reports"][1]["bound_to_added_ctp_object_in_response"])
        self.assertFalse(result["broker_connection_verified"])

    def test_no_credentials_no_network_and_cli_errors_are_redacted(self):
        with self.assertRaisesRegex(probe.ProbeDenied, "READ_ONLY_KEY_MISSING_OR_INVALID"):
            probe.run_probe(execute=True, env={}, opener=FakeOpener([]))
        output = StringIO()
        with (patch.dict(os.environ, ENV, clear=True),
              patch.object(sys, "argv", ["probe", "--execute"]),
              patch.object(probe, "_verified_opener", return_value=FakeOpener([
                  RuntimeError(f"network failed with {SECRET_KEY} and {ACCESS_KEY}")])),
              redirect_stdout(output)):
            exit_code = probe.main()
        self.assertEqual(exit_code, 1)
        self.assertEqual(json.loads(output.getvalue())["reason"], "API_NETWORK_OR_HTTP_FAILURE")
        self.assertNotIn(ACCESS_KEY, output.getvalue())
        self.assertNotIn(SECRET_KEY, output.getvalue())


if __name__ == "__main__":
    unittest.main()
