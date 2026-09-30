#!python3
"""Pinned standalone Python installer for an exchange-free YouQuant tool.

Default DRY_RUN is read-only and offline. Host pins must be filled from the
separate read-only probe before EXECUTE can create its dedicated new tree.
Never imports a strategy, reads credentials, changes PATH, invokes a shell,
uses sudo/package managers, or replaces system Python. Supports bootstrap 3.9.
"""
import hashlib
import json
import os
import platform
import posixpath
import re
import ssl
import stat
import subprocess
import tarfile
import time
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath


INSTALL_MODE = "DRY_RUN"
# These pins match the separate 2026-09-26 cloud read-only host receipt.
# The managed host runs strategies as UID 0. This is explicitly not a nonroot
# process; installation confines all writes to the new dedicated tree instead
# of using sudo, changing users, installing system packages or replacing Python.
INSTALL_BASE = "/opt/yuanli-gold2-runtime"
EXPECTED_MACHINE = "x86_64"
EXPECTED_UID = 0
PYTHON_VERSION = "3.12.14"
RELEASE_TAG = "20260924"
RELEASE_URL = "https://github.com/astral-sh/python-build-standalone/releases/tag/20260924"
PINS = {
    "x86_64": {"sha256": "269b2c99e4db15b242bf01832f4fea1e8f1a664f273cff519393f296e9820b41",
               "size": 34270188, "asset_id": 586643551},
    "aarch64": {"sha256": "c8499b61252c433280f134df954464d19811527b31cb920c35fc6967c1222e35",
                "size": 29199580, "asset_id": 586643192},
}
MAX_MEMBERS = 30000
MAX_UNPACKED_BYTES = 512 * 1024 * 1024
MAX_MEMBER_BYTES = 128 * 1024 * 1024
ALLOWED_DOWNLOAD_HOSTS = frozenset(("github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"))


class InstallDenied(RuntimeError):
    pass


def deny(code):
    raise InstallDenied(code)


def _no_symlink_ancestors(path):
    for item in (path,) + tuple(path.parents):
        if item.is_symlink():
            deny("SYMLINK_INSTALL_PATH")


def _host():
    try:
        libc = os.confstr("CS_GNU_LIBC_VERSION")
    except (AttributeError, OSError, ValueError):
        libc = None
    return {"system": platform.system(), "machine": platform.machine(), "libc": libc,
            "uid": os.geteuid() if hasattr(os, "geteuid") else None}


def installation_plan(base=None, *, expected_machine=None, expected_uid=None):
    host = _host()
    if host["system"] != "Linux" or host["machine"] not in PINS:
        deny("UNSUPPORTED_SYSTEM_OR_ARCHITECTURE")
    match = re.fullmatch(r"glibc ([0-9]+)\.([0-9]+)", host["libc"] or "")
    if not match or tuple(map(int, match.groups())) < (2, 17):
        deny("GLIBC_2_17_REQUIRED")
    if type(host["uid"]) is not int or host["uid"] < 0:
        deny("PROCESS_UID_REQUIRED")
    if expected_machine is None or expected_uid is None:
        deny("REVIEWED_HOST_PINS_REQUIRED")
    if host["machine"] != expected_machine or host["uid"] != expected_uid:
        deny("HOST_PIN_MISMATCH")
    allowed_bases = (Path("/opt/yuanli-gold2-runtime"),
                     Path("/tmp/yuanli-gold2-runtime-uid-" + str(host["uid"])))
    # User-directory option remains available for an independently reviewed
    # nonroot host; UID0 never installs under the platform's ephemeral cwd.
    if host["uid"] != 0:
        allowed_bases += (Path(os.getcwd()) / ".yuanli-gold2-runtime",)
    selected = Path(base) if isinstance(base, str) else None
    if selected not in allowed_bases or not selected.is_absolute():
        deny("DEDICATED_INSTALL_BASE_REQUIRED")
    _no_symlink_ancestors(selected)
    if not selected.parent.is_dir() or not os.access(str(selected.parent), os.W_OK | os.X_OK):
        deny("INSTALL_PARENT_NOT_WRITABLE")
    if selected.exists():
        mode = selected.stat()
        if not selected.is_dir() or mode.st_uid != host["uid"] or stat.S_IMODE(mode.st_mode) != 0o700:
            deny("UNSAFE_EXISTING_DEDICATED_BASE")
    target = selected / ("cpython-" + PYTHON_VERSION + "-" + RELEASE_TAG + "-" + host["machine"])
    if os.path.lexists(str(target)):
        deny("INSTALL_TARGET_ALREADY_EXISTS")
    pin = dict(PINS[host["machine"]])
    name = "cpython-" + PYTHON_VERSION + "+" + RELEASE_TAG + "-" + host["machine"] + "-unknown-linux-gnu-install_only_stripped.tar.gz"
    url = "https://github.com/astral-sh/python-build-standalone/releases/download/" + RELEASE_TAG + "/" + urllib.parse.quote(name, safe="")
    return {"schema_version": "gold-au-python-install-plan.v1", "host": host,
            "base": str(selected), "target": str(target), "archive_name": name,
            "asset": {**pin, "url": url}, "release_url": RELEASE_URL,
            "python_version": PYTHON_VERSION, "production_minimum": "3.12",
            "process_is_root": host["uid"] == 0, "system_python_modified": False,
            "temporary_base_may_be_cleaned_on_host_restart": str(selected).startswith("/tmp/"),
            "interpreter": str(target / "python/bin/python3.12"),
            "maximum_unpack_bytes": MAX_UNPACKED_BYTES, "broker_action_authorized": False,
            "account_access_performed": False, "production_started": False}


def _download_url_allowed(url):
    value = urllib.parse.urlsplit(url)
    return (value.scheme == "https" and value.hostname in ALLOWED_DOWNLOAD_HOSTS
            and value.username is None and value.password is None and value.port in (None, 443))


class _PinnedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        if not _download_url_allowed(newurl):
            deny("DOWNLOAD_REDIRECT_DENIED")
        return super().redirect_request(request, response, code, message, headers, newurl)


def download_verified(asset, destination):
    if not _download_url_allowed(asset["url"]):
        deny("DOWNLOAD_URL_DENIED")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _PinnedRedirect(),
                                        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request = urllib.request.Request(asset["url"], headers={"User-Agent": "yuanli-gold2-pinned-runtime/1"})
    digest = hashlib.sha256()
    size = 0
    started = time.monotonic()
    with opener.open(request, timeout=15) as response, destination.open("xb") as output:
        if not _download_url_allowed(response.geturl()):
            deny("DOWNLOAD_FINAL_HOST_DENIED")
        while True:
            if time.monotonic() - started > 120:
                deny("DOWNLOAD_DEADLINE_EXCEEDED")
            chunk = response.read(65536)
            if not chunk:
                break
            size += len(chunk)
            if size > asset["size"]:
                deny("DOWNLOAD_SIZE_EXCEEDED")
            digest.update(chunk)
            output.write(chunk)
        output.flush()
        os.fsync(output.fileno())
    destination.chmod(0o600)
    if size != asset["size"] or digest.hexdigest() != asset["sha256"]:
        deny("ARCHIVE_SIZE_OR_SHA256_MISMATCH")
    return {"bytes": size, "sha256": digest.hexdigest()}


def _archive_members(archive):
    members = []
    seen, links = set(), set()
    by_path, link_targets = {}, {}
    unpacked = 0
    for item in archive:
        if len(members) >= MAX_MEMBERS:
            deny("ARCHIVE_MEMBER_LIMIT_EXCEEDED")
        members.append(item)
        path = PurePosixPath(item.name)
        if (path.is_absolute() or ".." in path.parts or "\\" in item.name
                or not path.parts or path.parts[0] != "python" or "\x00" in item.name):
            deny("ARCHIVE_PATH_DENIED")
        normalized = str(path)
        if normalized in seen:
            deny("ARCHIVE_DUPLICATE_PATH")
        seen.add(normalized)
        by_path[normalized] = item
        if item.isdir():
            continue
        if item.issym():
            if (not item.linkname or PurePosixPath(item.linkname).is_absolute()
                    or "\\" in item.linkname or "\x00" in item.linkname):
                deny("ARCHIVE_LINK_DENIED")
            target = posixpath.normpath(posixpath.join(str(path.parent), item.linkname))
            if target != "python" and not target.startswith("python/"):
                deny("ARCHIVE_LINK_ESCAPE")
            links.add(normalized)
            link_targets[normalized] = target
        elif not item.isfile() or getattr(item, "sparse", None):
            deny("ARCHIVE_SPECIAL_FILE_DENIED")
        else:
            if item.size < 0 or item.size > MAX_MEMBER_BYTES:
                deny("ARCHIVE_MEMBER_SIZE_EXCEEDED")
            unpacked += item.size
            if unpacked > MAX_UNPACKED_BYTES:
                deny("ARCHIVE_UNPACK_LIMIT_EXCEEDED")
    for item in members:
        parents = PurePosixPath(item.name).parents
        if any(str(parent) in links for parent in parents):
            deny("ARCHIVE_LINK_ANCESTOR_DENIED")
        if any(str(parent) in by_path and not by_path[str(parent)].isdir() for parent in parents):
            deny("ARCHIVE_NON_DIRECTORY_ANCESTOR_DENIED")
        if item.issym():
            # Checking only normpath is insufficient: b/../c can escape after
            # b resolves to a directory symlink. Allow legitimate ../ terminfo
            # aliases only when every traversed prefix is an ordinary directory.
            current = list(PurePosixPath(item.name).parent.parts)
            parts = PurePosixPath(item.linkname).parts
            for index, component in enumerate(parts):
                if component == "..":
                    if len(current) <= 1:
                        deny("ARCHIVE_LINK_ESCAPE")
                    current.pop()
                elif component != ".":
                    current.append(component)
                if index < len(parts) - 1 and "/".join(current) in links:
                    deny("ARCHIVE_LINK_TARGET_ANCESTOR_DENIED")
            target = "/".join(current)
            if target not in by_path:
                deny("ARCHIVE_LINK_TARGET_MISSING")
            visited = {str(PurePosixPath(item.name))}
            while target in links:
                if target in visited or len(visited) >= 64:
                    deny("ARCHIVE_LINK_CYCLE_OR_DEPTH_EXCEEDED")
                visited.add(target)
                target = link_targets[target]
            if target not in by_path:
                deny("ARCHIVE_LINK_TARGET_MISSING")
    return members


def unpack_verified(archive_path, destination):
    """Manual bounded extraction; never invokes tar/extractall or preserves owners."""
    _no_symlink_ancestors(destination)
    if os.path.lexists(str(destination / "python")):
        deny("ARCHIVE_DESTINATION_ALREADY_EXISTS")
    with tarfile.open(str(archive_path), "r:gz") as archive:
        members = _archive_members(archive)
        for item in members:
            path = destination.joinpath(*PurePosixPath(item.name).parts)
            if item.isdir():
                path.mkdir(parents=True, exist_ok=True, mode=0o700)
            elif item.isfile():
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o700 if item.mode & 0o111 else 0o600)
                with os.fdopen(fd, "wb") as output, archive.extractfile(item) as source:
                    remaining = item.size
                    while remaining:
                        block = source.read(min(65536, remaining))
                        if not block:
                            deny("ARCHIVE_TRUNCATED_MEMBER")
                        output.write(block)
                        remaining -= len(block)
        # Links are created last, after all ordinary writes; no link can be an
        # extraction parent. Interpreter smoke uses the dated binary directly.
        for item in members:
            if item.issym():
                path = destination.joinpath(*PurePosixPath(item.name).parts)
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                path.symlink_to(item.linkname)
        return {"members": len(members), "unpacked_bytes": sum(item.size for item in members if item.isfile())}


def smoke_interpreter(interpreter, target):
    program = ("import sys,json,ssl,sqlite3,hashlib,hmac,zoneinfo,urllib.request,decimal,dataclasses;"
               "from zoneinfo import ZoneInfo;ZoneInfo('Asia/Shanghai');"
               "assert sys.version_info[:3]==(3,12,14);"
               "ssl.create_default_context();sqlite3.connect(':memory:').close();"
               "print(json.dumps({'version':list(sys.version_info[:3]),'stdlib_smoke':'PASS','executable':sys.executable}))")
    run = subprocess.run([str(interpreter), "-I", "-B", "-c", program], env={},
                         cwd=str(target), capture_output=True, text=True, timeout=30, check=True)
    result = json.loads(run.stdout)
    if result.get("version") != [3, 12, 14] or result.get("stdlib_smoke") != "PASS":
        deny("INTERPRETER_SMOKE_MISMATCH")
    return result


def install_runtime(base, *, expected_machine, expected_uid, execute=False):
    plan = installation_plan(base, expected_machine=expected_machine, expected_uid=expected_uid)
    if not execute:
        return {"status": "DRY_RUN", "network_access_performed": False, "file_write_performed": False, "plan": plan}
    base_path = Path(plan["base"])
    if not base_path.exists():
        base_path.mkdir(mode=0o700)
    # Repeat host/path validation immediately before the exclusive new tree.
    refreshed = installation_plan(base, expected_machine=expected_machine, expected_uid=expected_uid)
    if refreshed != plan:
        deny("INSTALL_PLAN_CHANGED")
    target = Path(plan["target"])
    target.mkdir(mode=0o700)
    archive = target / plan["archive_name"]
    download = download_verified(plan["asset"], archive)
    extracted = unpack_verified(archive, target)
    interpreter = Path(plan["interpreter"])
    _no_symlink_ancestors(interpreter)
    if not interpreter.is_file() or not os.access(str(interpreter), os.X_OK):
        deny("DATED_INTERPRETER_MISSING_OR_NOT_EXECUTABLE")
    smoke = smoke_interpreter(interpreter, target)
    receipt = {"schema_version": "gold-au-python-runtime-install.v1", "status": "INSTALLED_NOT_PRODUCTION_ENABLED",
               "plan": plan, "download": download, "extracted": extracted, "smoke": smoke,
               "installed_at_epoch": time.time(), "network_access_performed": True,
               "file_write_performed": True, "broker_action_authorized": False,
               "account_access_performed": False, "production_started": False,
               "candidate_shebang": "#!" + str(interpreter)}
    with (target / "install-receipt.json").open("x") as output:
        json.dump(receipt, output, sort_keys=True, indent=2)
        output.write("\n")
    (target / "install-receipt.json").chmod(0o600)
    return receipt


def main():
    if INSTALL_MODE not in ("DRY_RUN", "EXECUTE"):
        deny("INSTALL_MODE_INVALID")
    try:
        result = install_runtime(INSTALL_BASE, expected_machine=EXPECTED_MACHINE,
                                 expected_uid=EXPECTED_UID, execute=INSTALL_MODE == "EXECUTE")
    except InstallDenied as exc:
        result = {"status": "BLOCKED", "reason": str(exc), "production_started": False,
                  "broker_action_authorized": False, "account_access_performed": False}
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as exc:
        # Do not log request objects, inherited environment, subprocess output,
        # or CDN query strings on failure. A failed tree is kept for review.
        result = {"status": "FAILED", "reason": type(exc).__name__, "production_started": False,
                  "broker_action_authorized": False, "account_access_performed": False}
    Log("GOLD2_PYTHON_RUNTIME_INSTALL", json.dumps(result, sort_keys=True))
