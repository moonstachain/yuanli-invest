#!python3
"""Only inspect the exact new, failed GOLD2 runtime download tree; no writes."""
import json
import os
import stat

BASE = "/opt/yuanli-gold2-runtime"
TARGET = BASE + "/cpython-3.12.14-20260924-x86_64"
ARCHIVE_NAME = "cpython-3.12.14+20260924-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"


def partial_facts():
    result = {"schema_version": "gold-au-python-partial-readonly.v1", "target": TARGET,
              "status": "BLOCKED", "network_access_performed": False,
              "file_write_performed": False, "account_access_performed": False,
              "broker_action_authorized": False, "production_started": False}
    if os.geteuid() != 0:
        result["reason"] = "HOST_UID_CHANGED"; return result
    for path in ("/opt", BASE, TARGET):
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid != 0:
            result["reason"] = "UNSAFE_OWN_DIRECTORY"; return result
        if path != "/opt" and stat.S_IMODE(info.st_mode) != 0o700:
            result["reason"] = "UNSAFE_OWN_DIRECTORY_MODE"; return result
    names = []
    # This is our newly created, fixed target only; at most two entries are
    # needed to reject anything except the one known partial package.
    with os.scandir(TARGET) as entries:
        for entry in entries:
            names.append(entry.name)
            if len(names) > 1:
                result["reason"] = "UNEXPECTED_OWN_TARGET_CONTENTS"; return result
    if names != [ARCHIVE_NAME]:
        result["reason"] = "PARTIAL_ARCHIVE_NOT_ALONE"; return result
    info = os.lstat(TARGET + "/" + ARCHIVE_NAME)
    result.update({"partial_bytes": info.st_size, "expected_bytes": 34270188,
                   "partial_mode": oct(stat.S_IMODE(info.st_mode)), "owner_uid": info.st_uid,
                   "partial_nlink": info.st_nlink,
                   "partial_type": "REGULAR" if stat.S_ISREG(info.st_mode) else "SYMLINK" if stat.S_ISLNK(info.st_mode) else "OTHER",
                   "receipt_present": False, "unpacked_tree_present": False})
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
            or stat.S_IMODE(info.st_mode) not in (0o600, 0o644) or not 0 <= info.st_size <= 34270188):
        result["reason"] = "UNSAFE_PARTIAL_ARCHIVE"; return result
    result.update({"status": "OWN_PARTIAL_METADATA_READ_BACK", "reason": "NONE"})
    return result


def main():
    try:
        result = partial_facts()
    except OSError as exc:
        result = {"status": "BLOCKED", "reason": type(exc).__name__, "production_started": False}
    Log("GOLD2_PYTHON_PARTIAL_READONLY", json.dumps(result, sort_keys=True))
