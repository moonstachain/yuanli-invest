#!python3
"""Recover only the fixed failed GOLD2 download into a NEW dedicated tree.

Original partial evidence is retained unchanged. DRY_RUN is the default.
Cloud staging flattens the two audited tool sources; no production import.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import stat
import time
import urllib.request

from scripts.youquant_python_runtime_install import (
    InstallDenied, PINS, _host, _no_symlink_ancestors, _download_url_allowed,
    _PinnedRedirect, unpack_verified, smoke_interpreter,
)
from scripts.youquant_python_partial_readonly import partial_facts, BASE, TARGET, ARCHIVE_NAME


RESUME_MODE = "DRY_RUN"
RECOVERY_TARGET = TARGET + "-recovery-20260926-r1"
ASSET_URL = "https://github.com/astral-sh/python-build-standalone/releases/download/20260924/cpython-3.12.14%2B20260924-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"
DOWNLOAD_SECONDS = 600
MIB = 1024 * 1024


def recovery_plan():
    host = _host()
    if host != {"system": "Linux", "machine": "x86_64", "libc": "glibc 2.31", "uid": 0}:
        raise InstallDenied("RECOVERY_HOST_PIN_MISMATCH")
    metadata = partial_facts()
    if metadata.get("status") != "OWN_PARTIAL_METADATA_READ_BACK":
        raise InstallDenied(metadata.get("reason", "PARTIAL_TARGET_UNVERIFIED"))
    target = Path(RECOVERY_TARGET)
    _no_symlink_ancestors(target)
    if os.path.lexists(str(target)):
        raise InstallDenied("RECOVERY_TARGET_ALREADY_EXISTS")
    return {"schema_version": "gold-au-python-recovery-plan.v1", "original": metadata,
            "recovery_target": str(target), "interpreter": str(target / "python/bin/python3.12"),
            "asset": {**PINS["x86_64"], "url": ASSET_URL},
            "maximum_download_seconds": DOWNLOAD_SECONDS,
            "original_partial_will_be_modified": False, "production_started": False,
            "broker_action_authorized": False, "account_access_performed": False,
            "process_is_root": True, "system_python_modified": False}


def copy_retained_partial(plan, destination):
    source = Path(TARGET) / ARCHIVE_NAME
    descriptor = os.open(str(source), os.O_RDONLY | os.O_NOFOLLOW)
    digest, count = hashlib.sha256(), 0
    with os.fdopen(descriptor, "rb") as raw, destination.open("xb") as copied:
        before = os.fstat(raw.fileno())
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != 0
                or before.st_size != plan["original"]["partial_bytes"]):
            raise InstallDenied("ORIGINAL_PARTIAL_CHANGED")
        while True:
            block = raw.read(65536)
            if not block: break
            count += len(block)
            if count > before.st_size: raise InstallDenied("ORIGINAL_PARTIAL_CHANGED")
            digest.update(block); copied.write(block)
        after = os.fstat(raw.fileno())
        if count != before.st_size or after.st_size != before.st_size or after.st_mtime_ns != before.st_mtime_ns:
            raise InstallDenied("ORIGINAL_PARTIAL_CHANGED")
        copied.flush(); os.fsync(copied.fileno())
    destination.chmod(0o600)
    return {"retained_original_bytes": count, "retained_original_sha256": digest.hexdigest(),
            "retained_original_path": str(source)}


def _progress(stage, count, total):
    payload = json.dumps({"stage": stage, "bytes": count, "expected_bytes": total}, sort_keys=True)
    logger = globals().get("Log")
    if callable(logger): logger("GOLD2_PYTHON_RECOVERY_PROGRESS", payload)
    else: print(payload)


def resume_download(plan, seed, destination, *, progress=_progress):
    offset, total = plan["original"]["partial_bytes"], plan["asset"]["size"]
    digest, count = hashlib.sha256(), 0
    started = time.monotonic()
    mode = "VERIFIED_COMPLETE_RETAINED_COPY"
    if offset < total:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _PinnedRedirect(),
                                            urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        request = urllib.request.Request(plan["asset"]["url"], headers={
            "User-Agent": "yuanli-gold2-pinned-recovery/1", "Range": "bytes=" + str(offset) + "-"})
        response = opener.open(request, timeout=15)
    else:
        response = None
    try:
        if response is not None:
            if not _download_url_allowed(response.geturl()): raise InstallDenied("RECOVERY_FINAL_HOST_DENIED")
            status = response.status
            if status == 206:
                match = re.fullmatch(r"bytes ([0-9]+)-([0-9]+)/([0-9]+)", response.headers.get("Content-Range", ""))
                if not match or tuple(map(int, match.groups())) != (offset, total - 1, total):
                    raise InstallDenied("RECOVERY_CONTENT_RANGE_MISMATCH")
                mode = "HTTPS_RANGE_RETAINED_PREFIX"
                expected_body = total - offset
            elif status == 200:
                # Range unsupported: preserve original and seed; the response
                # goes into a separate new complete archive, starting at zero.
                mode = "HTTPS_FULL_DOWNLOAD_RANGE_UNSUPPORTED"
                expected_body = total
            else:
                raise InstallDenied("RECOVERY_HTTP_STATUS_DENIED")
            length = response.headers.get("Content-Length")
            if length is not None and (not length.isdigit() or int(length) != expected_body):
                raise InstallDenied("RECOVERY_CONTENT_LENGTH_MISMATCH")
        with destination.open("xb") as output:
            if response is None or mode == "HTTPS_RANGE_RETAINED_PREFIX":
                with seed.open("rb") as copied:
                    while True:
                        block = copied.read(65536)
                        if not block: break
                        count += len(block); digest.update(block); output.write(block)
                        if count > offset: raise InstallDenied("RECOVERY_SEED_SIZE_MISMATCH")
                if count != offset: raise InstallDenied("RECOVERY_SEED_SIZE_MISMATCH")
            progress("DOWNLOAD_STARTED", count, total)
            last_progress = count
            while response is not None:
                if time.monotonic() - started > DOWNLOAD_SECONDS:
                    raise InstallDenied("RECOVERY_DOWNLOAD_DEADLINE_EXCEEDED")
                block = response.read(65536)
                if not block: break
                count += len(block)
                if count > total: raise InstallDenied("RECOVERY_SIZE_EXCEEDED")
                digest.update(block); output.write(block)
                if count - last_progress >= MIB:
                    progress("DOWNLOAD_PROGRESS", count, total); last_progress = count
            output.flush(); os.fsync(output.fileno())
        destination.chmod(0o600)
    finally:
        if response is not None: response.close()
    if count != total or digest.hexdigest() != plan["asset"]["sha256"]:
        raise InstallDenied("RECOVERY_FINAL_SIZE_OR_SHA256_MISMATCH")
    progress("DOWNLOAD_VERIFIED", count, total)
    return {"mode": mode, "bytes": count, "sha256": digest.hexdigest()}


def recover_runtime(*, execute=False):
    plan = recovery_plan()
    if not execute:
        return {"status": "DRY_RUN", "network_access_performed": False,
                "file_write_performed": False, "plan": plan}
    target = Path(plan["recovery_target"])
    target.mkdir(mode=0o700)
    seed = target / "original-retained-prefix.partial"
    retained = copy_retained_partial(plan, seed)
    archive = target / ARCHIVE_NAME
    download = resume_download(plan, seed, archive)
    _progress("UNPACK_VERIFIED_ARCHIVE", download["bytes"], plan["asset"]["size"])
    extracted = unpack_verified(archive, target)
    interpreter = Path(plan["interpreter"])
    _no_symlink_ancestors(interpreter)
    smoke = smoke_interpreter(interpreter, target)
    receipt = {"schema_version": "gold-au-python-runtime-recovery.v1",
               "status": "RECOVERED_INSTALLED_NOT_PRODUCTION_ENABLED",
               "plan": plan, "retained_original": retained, "download": download,
               "extracted": extracted, "smoke": smoke, "installed_at_epoch": time.time(),
               "original_partial_modified": False, "broker_action_authorized": False,
               "account_access_performed": False, "production_started": False,
               "candidate_shebang": "#!" + str(interpreter)}
    with (target / "install-receipt.json").open("x") as raw:
        json.dump(receipt, raw, sort_keys=True, indent=2); raw.write("\n")
    (target / "install-receipt.json").chmod(0o600)
    return receipt


def main():
    if RESUME_MODE not in ("DRY_RUN", "EXECUTE"):
        raise InstallDenied("RECOVERY_MODE_INVALID")
    try:
        result = recover_runtime(execute=RESUME_MODE == "EXECUTE")
    except InstallDenied as exc:
        result = {"status": "BLOCKED", "reason": str(exc), "production_started": False}
    except Exception as exc:
        result = {"status": "FAILED", "reason": type(exc).__name__, "production_started": False}
    Log("GOLD2_PYTHON_RUNTIME_RECOVERY", json.dumps(result, sort_keys=True))
