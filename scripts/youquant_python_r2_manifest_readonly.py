#!python3
"""Read only one exact private r2 result, return bounded whitelisted fields."""
import json
import os
import stat

ROOT = "/opt/yuanli-gold2-runtime/cpython-3.12.14-20260924-x86_64-recovery-20260926-r2"
FILE = ROOT + "/download-parts-manifest.json"
REASONS = frozenset(("PARALLEL_URL_DENIED", "PARALLEL_FINAL_HOST_DENIED", "PARALLEL_RANGE_UNSUPPORTED",
                    "PARALLEL_CONTENT_RANGE_MISMATCH", "PARALLEL_CONTENT_LENGTH_MISMATCH", "PARALLEL_CANCELLED",
                    "PARALLEL_DEADLINE_EXCEEDED", "PARALLEL_PART_SIZE_EXCEEDED", "PARALLEL_PART_TRUNCATED",
                    "TimeoutError", "timeout", "HTTPError", "URLError", "OSError", "SSLError", "ConnectionResetError"))


def read_result():
    if os.geteuid() != 0: raise ValueError("HOST_UID_CHANGED")
    for path in ("/opt", "/opt/yuanli-gold2-runtime", ROOT):
        info = os.lstat(path)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0:
            raise ValueError("PRIVATE_DIRECTORY_INVALID")
        if path != "/opt" and stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError("PRIVATE_DIRECTORY_MODE_INVALID")
    fd = os.open(FILE, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as raw:
        info = os.fstat(raw.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_nlink != 1
                or stat.S_IMODE(info.st_mode) != 0o600 or not 0 < info.st_size <= 16384):
            raise ValueError("PRIVATE_MANIFEST_METADATA_INVALID")
        data = raw.read(16385)
    if len(data) > 16384: raise ValueError("MANIFEST_TOO_LARGE")
    value = json.loads(data)
    if value.get("schema_version") != "gold-au-python-range-parts.v1":
        raise ValueError("MANIFEST_SCHEMA_INVALID")
    errors, parts, received = [], [], {}
    if len(value.get("errors", [])) > 8 or len(value.get("parts", [])) > 8:
        raise ValueError("MANIFEST_COUNT_INVALID")
    for item in value.get("errors", []):
        index = item.get("index")
        if type(index) is not int or not 0 <= index < 8: raise ValueError("MANIFEST_INDEX_INVALID")
        reason = item.get("reason")
        errors.append({"index":index,"reason":reason if reason in REASONS else "UNKNOWN_SANITIZED_REASON"})
    for item in value.get("parts", []):
        row = {key:item.get(key) for key in ("index", "start", "end", "bytes")}
        if any(type(number) is not int or not 0 <= number <= 34270188 for number in row.values()) or row["index"] >= 8:
            raise ValueError("MANIFEST_PART_INVALID")
        parts.append(row)
    for key, count in value.get("received_byte_counts", {}).items():
        if key not in tuple(str(index) for index in range(8)) or type(count) is not int or not 0 <= count <= 34270188:
            raise ValueError("MANIFEST_RECEIVED_INVALID")
        received[key] = count
    return {"schema_version":"gold-au-python-r2-manifest-readonly.v1", "status":"READ_BACK",
            "manifest_bytes":len(data), "errors":errors, "parts":parts, "received_byte_counts":received,
            "network_access_performed":False, "file_write_performed":False,
            "account_access_performed":False, "production_started":False}


def main():
    try: result = read_result()
    except ValueError as exc:
        known = {"HOST_UID_CHANGED", "PRIVATE_DIRECTORY_INVALID", "PRIVATE_DIRECTORY_MODE_INVALID",
                 "PRIVATE_MANIFEST_METADATA_INVALID", "MANIFEST_TOO_LARGE", "MANIFEST_SCHEMA_INVALID",
                 "MANIFEST_COUNT_INVALID", "MANIFEST_INDEX_INVALID", "MANIFEST_PART_INVALID", "MANIFEST_RECEIVED_INVALID"}
        result = {"status":"BLOCKED", "reason":str(exc) if str(exc) in known else "MANIFEST_INVALID"}
    except Exception as exc: result = {"status":"BLOCKED", "reason":type(exc).__name__}
    Log("GOLD2_PYTHON_R2_MANIFEST_READONLY", json.dumps(result, sort_keys=True))
