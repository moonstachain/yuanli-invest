"""Read-only host compatibility probe for the GOLD2 SimNow source bundle.

This module never calls exchange, GetCommand, _G, CommandRobot, or order APIs.
Presence and importability are observations only, not account attestation or
authority to start the strategy.  Use it as a separate preflight strategy.
"""

from collections.abc import Mapping
from importlib.machinery import PathFinder
import json
import sys


REQUIRED_CALLABLES = ("GetCommand", "_G", "Sleep", "Log")
REQUIRED_MODULES = ("zoneinfo", "yuanli_invest.gold_paper",
                    "youquant_gold_simnow_strategy")


def _module_spec_located(name):
    """Walk package specs without executing a parent package initializer."""
    try:
        parts = name.split(".")
        search_path = None
        for index in range(len(parts)):
            fullname = ".".join(parts[:index + 1])
            spec = PathFinder.find_spec(fullname, search_path)
            if spec is None:
                return False
            if index < len(parts) - 1:
                search_path = spec.submodule_search_locations
                if search_path is None:
                    return False
        return True
    except (ImportError, ValueError, AttributeError):
        return False


def inspect_host(host_globals):
    """Inspect names and imports only; do not touch their underlying objects."""
    if not isinstance(host_globals, Mapping):
        raise TypeError("host_globals must be a mapping")
    python_supported = sys.version_info >= (3, 12)
    modules = {name: _module_spec_located(name) for name in REQUIRED_MODULES}
    symbols = {name: callable(host_globals.get(name)) for name in REQUIRED_CALLABLES}
    exchange = host_globals.get("exchange")
    symbols["exchange"] = exchange is not None and exchange is not False
    unexpected_runtime = host_globals.get("GOLD2_SIMNOW_RUNTIME") is not None
    compatible = (python_supported and all(modules.values())
                  and all(symbols.values()) and not unexpected_runtime)
    return {
        "schema_version": "gold2-au-simnow-host-preflight.v1",
        "status": "HOST_SYMBOLS_PRESENT_UNVERIFIED" if compatible else "HOST_PREFLIGHT_BLOCKED",
        "python_version": "%s.%s.%s" % tuple(sys.version_info[:3]),
        "python_minimum": "3.12",
        "python_supported": python_supported,
        "module_spec_located": modules,
        "host_symbol_present": symbols,
        "unexpected_runtime_present": unexpected_runtime,
        "broker_api_calls": 0,
        "broker_api_calls_scope": "THIS_PREFLIGHT_SCRIPT_ONLY",
        "broker_identity_verified": False,
        "simnow_connection_verified": False,
        "module_upload_capability_verified": False,
        "paper_authority_enabled": False,
    }


def main():
    report = inspect_host(globals())
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
    logger = globals().get("Log")
    if callable(logger):
        logger("GOLD2_SIMNOW_READ_ONLY_PREFLIGHT", rendered)
    else:
        print(rendered)
    return report
