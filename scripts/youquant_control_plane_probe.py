#!/usr/bin/env python3
"""Read-only, redacted YouQuant account-control-plane probe.

Dry-run is the default and does not inspect credentials or use the network.
Execute permits only four account read methods. No raw API response, profile,
account identifier, key, or signature is printed or written by this program.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import ssl
import time
from typing import Any, Callable, Mapping
from urllib.parse import urlencode
from urllib.request import (
    HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener,
)


API_URL = "https://www.youquant.com/api/v1"
API_VERSION = "1.0"
ALLOWED_METHODS = frozenset({
    "GetPlatformList", "GetRobotDetail", "GetRobotList", "GetNodeList",
})
MAX_RESPONSE_BYTES = 262_144
TIMEOUT_SECONDS = 10
ACCESS_KEY_ENV = "YOUQUANT_ACCESS_KEY"
SECRET_KEY_ENV = "YOUQUANT_SECRET_KEY"
FIRST_NORMAL_TD_FRONT = "182.254.243.31:30001"
FIRST_NORMAL_MD_FRONT = "182.254.243.31:30011"


class ProbeDenied(ValueError):
    """Fixed, non-secret refusal code safe for terminal output."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request: Request, fp: Any, code: int,
                         msg: str, headers: Any, newurl: str) -> None:
        return None


def _verified_opener() -> Any:
    """No environment proxy, verified HTTPS, or credential-bearing redirect."""
    return build_opener(ProxyHandler({}), _NoRedirect(),
                        HTTPSHandler(context=ssl.create_default_context()))


def _validate_credentials(env: Mapping[str, str]) -> tuple[str, str]:
    access_key = env.get(ACCESS_KEY_ENV)
    secret_key = env.get(SECRET_KEY_ENV)
    if (not isinstance(access_key, str) or not isinstance(secret_key, str)
            or not 8 <= len(access_key) <= 512 or not 8 <= len(secret_key) <= 512
            or any(ord(char) < 33 or ord(char) > 126 for char in access_key + secret_key)):
        raise ProbeDenied("READ_ONLY_KEY_MISSING_OR_INVALID")
    return access_key, secret_key


def _signed_form(method: str, args: list[Any], access_key: str,
                 secret_key: str, nonce: int) -> bytes:
    if method not in ALLOWED_METHODS or type(nonce) is not int or nonce <= 0:
        raise ProbeDenied("METHOD_OR_NONCE_NOT_ALLOWED")
    if method == "GetRobotDetail":
        if (len(args) != 1 or type(args[0]) is not int
                or not 0 < args[0] < 10**12):
            raise ProbeDenied("ROBOT_ID_REQUIRED")
    elif args:
        raise ProbeDenied("METHOD_ARGS_NOT_ALLOWED")
    args_json = json.dumps(args, ensure_ascii=True, separators=(",", ":"))
    signed = f"{API_VERSION}|{method}|{args_json}|{nonce}|{secret_key}"
    signature = hashlib.md5(signed.encode("utf-8")).hexdigest()  # nosec: vendor token protocol
    return urlencode({"version": API_VERSION, "access_key": access_key,
                      "method": method, "args": args_json, "nonce": nonce,
                      "sign": signature}).encode("ascii")


def _strict_json(raw: bytes) -> Any:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for name, value in pairs:
            if name in obj:
                raise ProbeDenied("API_JSON_DUPLICATE_KEY")
            obj[name] = value
        return obj

    def reject_constant(_: str) -> None:
        raise ProbeDenied("API_JSON_NONFINITE")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except ProbeDenied:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise ProbeDenied("API_JSON_INVALID") from None


def _read_response(opener: Any, request: Request) -> bytes:
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise ProbeDenied("API_HTTP_STATUS_REJECTED")
            headers = response.headers
            length = headers.get("Content-Length")
            if length is not None:
                if not str(length).isdigit() or int(length) > MAX_RESPONSE_BYTES:
                    raise ProbeDenied("API_RESPONSE_OVERSIZED")
            if headers.get("Content-Encoding", "identity").lower() != "identity":
                raise ProbeDenied("API_RESPONSE_ENCODING_REJECTED")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except ProbeDenied:
        raise
    except Exception as exc:
        # URL/HTTP exceptions may contain the signed form; never echo them.
        raise ProbeDenied("API_NETWORK_OR_HTTP_FAILURE") from None
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise ProbeDenied("API_RESPONSE_EMPTY_OR_OVERSIZED")
    return raw


def _call(method: str, args: list[Any], access_key: str, secret_key: str,
          nonce: int, opener: Any) -> tuple[Mapping[str, Any], str]:
    form = _signed_form(method, args, access_key, secret_key, nonce)
    request = Request(API_URL, data=form,
                      headers={"Content-Type": "application/x-www-form-urlencoded",
                               "Accept": "application/json", "Accept-Encoding": "identity"},
                      method="POST")
    raw = _read_response(opener, request)
    raw_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
    parsed = _strict_json(raw)
    if (not isinstance(parsed, Mapping) or type(parsed.get("code")) is not int
            or parsed.get("code") != 0 or not isinstance(parsed.get("data"), Mapping)):
        raise ProbeDenied("API_ENVELOPE_REJECTED")
    data = parsed["data"]
    if data.get("error") is not None or not isinstance(data.get("result"), Mapping):
        raise ProbeDenied("API_RESULT_REJECTED")
    return data["result"], raw_hash


def _counted_items(result: Mapping[str, Any], field: str) -> list[Mapping[str, Any]]:
    all_count = result.get("all")
    rows = result.get(field)
    if (type(all_count) is not int or all_count < 0 or not isinstance(rows, list)
            or all_count < len(rows) or not all(isinstance(row, Mapping) for row in rows)):
        raise ProbeDenied("API_LIST_SCHEMA_REJECTED")
    return rows


def _profile_shape_and_match(value: Any) -> tuple[bool, bool]:
    if isinstance(value, str):
        try:
            value = _strict_json(value.encode("utf-8"))
        except ProbeDenied:
            return False, False
    if not isinstance(value, Mapping):
        return False, False
    fields = (value.get("BrokerId"), value.get("TDFront"), value.get("MDFront"))
    if not all(isinstance(item, str) and item for item in fields):
        return False, False
    td = fields[1].removeprefix("tcp://")
    md = fields[2].removeprefix("tcp://")
    return True, (fields[0] == "9999" and td == FIRST_NORMAL_TD_FRONT
                  and md == FIRST_NORMAL_MD_FRONT)


def _platform_summary(result: Mapping[str, Any]) -> tuple[dict[str, Any], set[int]]:
    platforms = _counted_items(result, "platforms")
    ctp_ids: set[int] = set()
    direct_shapes = 0
    first_normal_configs = 0
    seen_ids: set[int] = set()
    for item in platforms:
        object_id = item.get("id")
        if (type(object_id) is not int or object_id <= 0 or object_id in seen_ids
                or not isinstance(item.get("eid"), str)):
            raise ProbeDenied("API_PLATFORM_SCHEMA_REJECTED")
        seen_ids.add(object_id)
        if item["eid"] == "Futures_CTP":
            ctp_ids.add(object_id)
            direct, match = _profile_shape_and_match(item.get("profiles"))
            direct_shapes += int(direct)
            first_normal_configs += int(match)
    return {"added_platform_count": result["all"],
            "list_complete": result["all"] == len(platforms),
            "added_ctp_count_in_response": len(ctp_ids),
            "ctp_profile_direct_shape_count": direct_shapes,
            "ctp_first_normal_config_match_count": first_normal_configs}, ctp_ids


def _robot_detail_summary(result: Mapping[str, Any], robot_id: int,
                          ctp_ids: set[int]) -> dict[str, Any]:
    robot = result.get("robot")
    if (not isinstance(robot, Mapping) or type(robot.get("id")) is not int
            or robot["id"] != robot_id or type(robot.get("status")) is not int):
        raise ProbeDenied("API_ROBOT_SCHEMA_REJECTED")
    raw_pairs = robot.get("strategy_exchange_pairs")
    if not isinstance(raw_pairs, str):
        raise ProbeDenied("API_ROBOT_BINDING_SCHEMA_REJECTED")
    pairs = _strict_json(raw_pairs.encode("utf-8"))
    if (not isinstance(pairs, list) or len(pairs) != 3
            or type(pairs[0]) is not int or pairs[0] <= 0
            or not isinstance(pairs[1], list) or not isinstance(pairs[2], list)
            or len(pairs[1]) != len(pairs[2])
            or not all(type(item) is int for item in pairs[1])
            or not all(isinstance(item, str) for item in pairs[2])):
        raise ProbeDenied("API_ROBOT_BINDING_SCHEMA_REJECTED")
    bound = (len(pairs[1]) == 1 and pairs[1][0] in ctp_ids
             and pairs[2][0] in {"FUTURES", "FUTURES_CTP"})
    return {"robot_running": robot["status"] == 1,
            "robot_status_code": robot["status"],
            "bound_to_added_ctp_object_in_response": bound}


def _robot_list_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    rows = _counted_items(result, "robots")
    if any(type(row.get("id")) is not int or type(row.get("status")) is not int
           for row in rows):
        raise ProbeDenied("API_ROBOT_LIST_SCHEMA_REJECTED")
    return {"robot_count": result["all"], "list_complete": result["all"] == len(rows),
            "running_robots_in_response": sum(row["status"] == 1 for row in rows)}


def _node_list_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    rows = _counted_items(result, "nodes")
    return {"node_count": result["all"], "returned_node_count": len(rows),
            "list_complete": result["all"] == len(rows)}


def _methods(robot_id: int | None, include_robot_list: bool,
             include_node_list: bool) -> list[tuple[str, list[Any]]]:
    if robot_id is not None and (type(robot_id) is not int or not 0 < robot_id < 10**12):
        raise ProbeDenied("ROBOT_ID_INVALID")
    calls: list[tuple[str, list[Any]]] = [("GetPlatformList", [])]
    if robot_id is not None:
        calls.append(("GetRobotDetail", [robot_id]))
    if include_robot_list:
        calls.append(("GetRobotList", []))
    if include_node_list:
        calls.append(("GetNodeList", []))
    return calls


def run_probe(*, execute: bool = False, robot_id: int | None = None,
              include_robot_list: bool = False, include_node_list: bool = False,
              env: Mapping[str, str] | None = None, opener: Any = None,
              clock_ns: Callable[[], int] = time.time_ns) -> dict[str, Any]:
    """Query only explicit account read methods; return no raw account fields."""
    calls = _methods(robot_id, include_robot_list, include_node_list)
    if not execute:
        return {"status": "DRY_RUN_NO_NETWORK", "planned_methods": [m for m, _ in calls],
                "robot_detail_requires_id": robot_id is None,
                "network_attempted": False, "broker_connection_verified": False,
                "paper_authority_enabled": False}
    access_key, secret_key = _validate_credentials(os.environ if env is None else env)
    active_opener = _verified_opener() if opener is None else opener
    reports: list[dict[str, Any]] = []
    ctp_ids: set[int] = set()
    previous_nonce = 0
    for method, args in calls:
        current_ns = clock_ns()
        if type(current_ns) is not int or current_ns <= 0:
            raise ProbeDenied("LOCAL_CLOCK_INVALID")
        nonce = max(current_ns // 1_000_000, previous_nonce + 1)
        previous_nonce = nonce
        result, raw_hash = _call(method, args, access_key, secret_key, nonce, active_opener)
        if method == "GetPlatformList":
            summary, ctp_ids = _platform_summary(result)
        elif method == "GetRobotDetail":
            summary = _robot_detail_summary(result, robot_id, ctp_ids)
        elif method == "GetRobotList":
            summary = _robot_list_summary(result)
        else:
            summary = _node_list_summary(result)
        reports.append({"method": method, "observed_at": datetime.now(timezone.utc).isoformat(),
                        "raw_response_sha256": raw_hash, **summary})
    return {"status": "READ_ONLY_CONTROL_PLANE_OBSERVED", "reports": reports,
            "network_attempted": True, "broker_connection_verified": False,
            "paper_authority_enabled": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="send read-only account API requests")
    parser.add_argument("--robot-id", type=int, help="also read this robot's details")
    parser.add_argument("--include-robot-list", action="store_true")
    parser.add_argument("--include-node-list", action="store_true")
    args = parser.parse_args()
    try:
        result = run_probe(execute=args.execute, robot_id=args.robot_id,
                           include_robot_list=args.include_robot_list,
                           include_node_list=args.include_node_list)
    except ProbeDenied as exc:
        result = {"status": "CONTROL_PLANE_PROBE_BLOCKED", "reason": exc.code,
                  "broker_connection_verified": False, "paper_authority_enabled": False}
        print(json.dumps(result, sort_keys=True))
        return 1
    except Exception:
        # No traceback: transport/JSON exceptions can contain request details.
        print(json.dumps({"status": "CONTROL_PLANE_PROBE_BLOCKED",
                          "reason": "UNEXPECTED_PROBE_FAILURE",
                          "broker_connection_verified": False,
                          "paper_authority_enabled": False}, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
