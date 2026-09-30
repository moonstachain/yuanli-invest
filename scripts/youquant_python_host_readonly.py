#!python3
"""Bounded, one-shot host facts for a separate, exchange-free tool strategy.

No network, file writes, environment access, credential lookup, directory
listing, production import or exchange callback. This tool may run on 3.9;
the production Python >=3.12 requirement remains unchanged.
"""
import json
import os
import platform
import subprocess
import sys


INTERPRETER_PATHS = tuple(
    prefix + "/python" + version
    for prefix in ("/usr/bin", "/usr/local/bin", "/opt/python/bin")
    for version in ("3.12", "3.13", "3.14")
)


def host_facts():
    try:
        libc = os.confstr("CS_GNU_LIBC_VERSION")
    except (AttributeError, OSError, ValueError):
        libc = None
    uid = os.geteuid() if hasattr(os, "geteuid") else None
    cwd = os.getcwd()
    roots = (os.path.join(cwd, ".yuanli-gold2-runtime"),
             "/tmp/yuanli-gold2-runtime-uid-" + str(uid))
    locations = []
    for root in dict.fromkeys(roots):
        exists = os.path.lexists(root)
        locations.append({
            "path": root, "exists": exists,
            "symlink": os.path.islink(root),
            "existing_directory": os.path.isdir(root) if exists else False,
            "parent_writable_by_process": os.access(os.path.dirname(root), os.W_OK | os.X_OK),
            "writable_check_only_no_file_created": True,
        })
    candidates = []
    for path in INTERPRETER_PATHS:
        item = {"path": path, "status": "NOT_PRESENT"}
        if os.path.isfile(path) and os.access(path, os.X_OK):
            try:
                run = subprocess.run(
                    [path, "-I", "-B", "-c", "import json,sys;print(json.dumps(list(sys.version_info[:3])))"],
                    env={}, capture_output=True, text=True, timeout=3, check=True)
                version = json.loads(run.stdout)
                if (not isinstance(version, list) or len(version) != 3
                        or any(type(value) is not int for value in version)):
                    raise ValueError("MALFORMED_VERSION")
                item.update({"status": "VERSION_READ_BACK", "version": version,
                             "meets_production_minimum": tuple(version) >= (3, 12, 0)})
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                item.update({"status": "PROBE_FAILED", "reason": type(exc).__name__})
        candidates.append(item)
    return {
        "schema_version": "gold-au-python-host-readonly.v1",
        "system": platform.system(), "machine": platform.machine(),
        "libc": libc, "effective_uid": uid, "nonroot_process": uid is not None and uid != 0,
        "default_version": list(sys.version_info[:3]), "default_executable": sys.executable,
        "allowed_interpreters": candidates, "dedicated_locations": locations,
        "network_access_performed": False, "file_write_performed": False,
        "environment_access_performed": False, "account_access_performed": False,
        "broker_action_authorized": False, "production_started": False,
    }


def main():
    Log("GOLD2_PYTHON_HOST_READONLY", json.dumps(host_facts(), sort_keys=True))
