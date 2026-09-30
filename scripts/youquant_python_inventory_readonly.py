#!python3
"""One-shot interpreter inventory; no exchange binding, credentials or orders.

This diagnostic deliberately loads on Python 3.9. It cannot activate the
production strategy or relax its Python >=3.12 requirement.
"""
import json
import shutil
import subprocess
import sys


def inventory():
    result = {
        "schema_version": "gold-au-python-inventory.v1",
        "default_version": list(sys.version_info[:3]),
        "default_executable": sys.executable,
        "candidates": [],
        "broker_action_authorized": False,
        "account_access_performed": False,
        "production_started": False,
    }
    # Only fixed interpreter names on PATH; no directory or environment dump.
    for name in ("python3.12", "python3.13", "python3.14"):
        path = shutil.which(name)
        row = {"name": name, "path": path, "status": "NOT_FOUND_ON_PATH"}
        if path:
            try:
                probe = subprocess.run(
                    [path, "-I", "-c", "import json,sys; print(json.dumps(list(sys.version_info[:3])))"],
                    capture_output=True, text=True, timeout=5, check=True,
                )
                version = json.loads(probe.stdout)
                if (not isinstance(version, list) or len(version) != 3
                        or any(type(v) is not int for v in version)):
                    raise ValueError("INVALID_INTERPRETER_VERSION")
                row.update({"version": version, "status": "VERSION_READ_BACK",
                            "meets_production_version": tuple(version) >= (3, 12, 0)})
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                row.update({"status": "PROBE_FAILED", "reason": type(exc).__name__})
        result["candidates"].append(row)
    return result


def main():
    Log("GOLD2_PYTHON_INVENTORY_READONLY", json.dumps(inventory(), sort_keys=True))

