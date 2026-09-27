#!python3
"""One bounded 8-range recovery from the SAME fixed official asset; inert default."""
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import ssl
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

from scripts.youquant_python_runtime_install import (
    InstallDenied, PINS, _host, _no_symlink_ancestors, _download_url_allowed,
    _PinnedRedirect, unpack_verified, smoke_interpreter,
)
from scripts.youquant_python_partial_readonly import partial_facts, TARGET, ARCHIVE_NAME
from scripts.youquant_python_runtime_resume import copy_retained_partial, _progress, ASSET_URL

PARALLEL_MODE = "DRY_RUN"
PARALLEL_TARGET = TARGET + "-recovery-20260926-r2"
PARALLEL_SECONDS = 600
PARALLEL_WORKERS = 8
KNOWN_PREFIX_BYTES = 2490368
MIB = 1024 * 1024


def parallel_plan():
    if _host() != {"system":"Linux","machine":"x86_64","libc":"glibc 2.31","uid":0}:
        raise InstallDenied("PARALLEL_HOST_PIN_MISMATCH")
    facts = partial_facts()
    expected = {"status":"BLOCKED","reason":"UNSAFE_PARTIAL_ARCHIVE","partial_type":"REGULAR",
                "partial_bytes":KNOWN_PREFIX_BYTES,"partial_mode":"0o666","owner_uid":0,"partial_nlink":1,
                "receipt_present":False,"unpacked_tree_present":False}
    if any(facts.get(key) != value for key,value in expected.items()):
        raise InstallDenied("REVIEWED_PARTIAL_FACTS_CHANGED")
    target = Path(PARALLEL_TARGET)
    _no_symlink_ancestors(target)
    if os.path.lexists(str(target)):
        raise InstallDenied("PARALLEL_RECOVERY_TARGET_ALREADY_EXISTS")
    return {"schema_version":"gold-au-python-parallel-plan.v1","original":facts,
            "recovery_target":str(target),"interpreter":str(target / "python/bin/python3.12"),
            "asset":{**PINS["x86_64"],"url":ASSET_URL},"workers":PARALLEL_WORKERS,
            "deadline_seconds":PARALLEL_SECONDS,"process_is_root":True,
            "original_partial_modified":False,"system_python_modified":False,
            "account_access_performed":False,"production_started":False}


def byte_ranges(offset, total, workers):
    if type(offset) is not int or type(total) is not int or not 0 < offset < total or not 1 <= workers <= 8:
        raise InstallDenied("PARALLEL_RANGE_INPUT_INVALID")
    width = (total - offset + workers - 1) // workers
    return [(index, start, min(start + width - 1, total - 1))
            for index,start in enumerate(range(offset,total,width))]


def download_part(asset, part, target, deadline, stop, messages):
    index,start,end = part
    expected = end - start + 1
    if not _download_url_allowed(asset["url"]): raise InstallDenied("PARALLEL_URL_DENIED")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _PinnedRedirect(),
                                        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request = urllib.request.Request(asset["url"],headers={"User-Agent":"yuanli-gold2-fixed-range/2",
                                                        "Range":"bytes=%d-%d" % (start,end)})
    response = opener.open(request,timeout=15)
    digest,count = hashlib.sha256(),0
    try:
        if not _download_url_allowed(response.geturl()): raise InstallDenied("PARALLEL_FINAL_HOST_DENIED")
        if response.status != 206: raise InstallDenied("PARALLEL_RANGE_UNSUPPORTED")
        match = re.fullmatch(r"bytes ([0-9]+)-([0-9]+)/([0-9]+)",response.headers.get("Content-Range",""))
        if not match or tuple(map(int,match.groups())) != (start,end,asset["size"]):
            raise InstallDenied("PARALLEL_CONTENT_RANGE_MISMATCH")
        length = response.headers.get("Content-Length")
        if length is not None and (not length.isdigit() or int(length) != expected):
            raise InstallDenied("PARALLEL_CONTENT_LENGTH_MISMATCH")
        fd = os.open(str(target),os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,"wb") as output:
            while True:
                if stop.is_set(): raise InstallDenied("PARALLEL_CANCELLED")
                if time.monotonic() >= deadline: raise InstallDenied("PARALLEL_DEADLINE_EXCEEDED")
                block = response.read(65536)
                if time.monotonic() >= deadline: raise InstallDenied("PARALLEL_DEADLINE_EXCEEDED")
                if not block: break
                count += len(block)
                if count > expected: raise InstallDenied("PARALLEL_PART_SIZE_EXCEEDED")
                digest.update(block);output.write(block)
                messages.put((index,count))
            output.flush();os.fsync(output.fileno())
        if count != expected: raise InstallDenied("PARALLEL_PART_TRUNCATED")
        return {"index":index,"start":start,"end":end,"bytes":count,"sha256":digest.hexdigest()}
    finally:
        response.close()


def download_parts(plan,target,*,progress=_progress):
    parts = byte_ranges(plan["original"]["partial_bytes"],plan["asset"]["size"],plan["workers"])
    deadline = time.monotonic() + plan["deadline_seconds"]
    stop,messages = threading.Event(),queue.Queue(maxsize=1024)
    received,results,errors = {},[],[]
    last_progress = plan["original"]["partial_bytes"]
    progress("PARALLEL_DOWNLOAD_STARTED",last_progress,plan["asset"]["size"])
    with ThreadPoolExecutor(max_workers=plan["workers"]) as executor:
        jobs = {executor.submit(download_part,plan["asset"],part,target / ("part-%02d.bin" % part[0]),
                                deadline,stop,messages):part[0] for part in parts}
        pending = set(jobs)
        while pending:
            done,pending = wait(pending,timeout=1,return_when=FIRST_COMPLETED)
            while True:
                try: index,count = messages.get_nowait();received[index] = count
                except queue.Empty: break
            total_received = plan["original"]["partial_bytes"] + sum(received.values())
            if total_received - last_progress >= MIB:
                progress("PARALLEL_DOWNLOAD_PROGRESS",total_received,plan["asset"]["size"])
                last_progress = total_received
            if time.monotonic() >= deadline: stop.set()
            for job in done:
                try: results.append(job.result())
                except Exception as exc:
                    errors.append({"index":jobs[job],"reason":str(exc) if isinstance(exc,InstallDenied) else type(exc).__name__})
                    stop.set()
    manifest = {"schema_version":"gold-au-python-range-parts.v1","parts":sorted(results,key=lambda row:row["index"]),
                "errors":errors,"expected_ranges":parts,"received_byte_counts":received,
                "maximum_download_seconds":plan["deadline_seconds"],"original_partial_modified":False}
    with (target / "download-parts-manifest.json").open("x") as raw:
        json.dump(manifest,raw,sort_keys=True,indent=2);raw.write("\n")
    (target / "download-parts-manifest.json").chmod(0o600)
    if errors or len(results) != len(parts): raise InstallDenied("PARALLEL_INCOMPLETE_PARTS_RETAINED")
    return manifest


def merge_verify(plan,seed,target,manifest):
    archive = target / ARCHIVE_NAME
    digest,count = hashlib.sha256(),0
    ordered = [seed]+[target / ("part-%02d.bin" % row["index"]) for row in manifest["parts"]]
    with archive.open("xb") as output:
        for source in ordered:
            with source.open("rb") as raw:
                while True:
                    block = raw.read(65536)
                    if not block: break
                    count += len(block)
                    if count > plan["asset"]["size"]: raise InstallDenied("PARALLEL_MERGE_SIZE_EXCEEDED")
                    digest.update(block);output.write(block)
        output.flush();os.fsync(output.fileno())
    archive.chmod(0o600)
    if count != plan["asset"]["size"] or digest.hexdigest() != plan["asset"]["sha256"]:
        raise InstallDenied("PARALLEL_FINAL_SIZE_OR_SHA256_MISMATCH")
    return archive,{"bytes":count,"sha256":digest.hexdigest()}


def parallel_recover(*,execute=False):
    plan = parallel_plan()
    if not execute:
        return {"status":"DRY_RUN","network_access_performed":False,"file_write_performed":False,"plan":plan}
    target = Path(plan["recovery_target"]);target.mkdir(mode=0o700)
    seed = target / "original-retained-prefix.partial"
    retained = copy_retained_partial(plan,seed)
    manifest = download_parts(plan,target)
    archive,download = merge_verify(plan,seed,target,manifest)
    _progress("PARALLEL_ARCHIVE_VERIFIED",download["bytes"],plan["asset"]["size"])
    extracted = unpack_verified(archive,target)
    interpreter = Path(plan["interpreter"]);_no_symlink_ancestors(interpreter)
    smoke = smoke_interpreter(interpreter,target)
    receipt = {"schema_version":"gold-au-python-parallel-recovery.v1",
               "status":"RECOVERED_INSTALLED_NOT_PRODUCTION_ENABLED","plan":plan,
               "retained_original":retained,"download":download,"extracted":extracted,"smoke":smoke,
               "installed_at_epoch":time.time(),"original_partial_modified":False,
               "account_access_performed":False,"broker_action_authorized":False,"production_started":False,
               "candidate_shebang":"#!"+str(interpreter)}
    with (target / "install-receipt.json").open("x") as raw:
        json.dump(receipt,raw,sort_keys=True,indent=2);raw.write("\n")
    (target / "install-receipt.json").chmod(0o600)
    return receipt


def main():
    if PARALLEL_MODE not in ("DRY_RUN","EXECUTE"): raise InstallDenied("PARALLEL_MODE_INVALID")
    try: result = parallel_recover(execute=PARALLEL_MODE == "EXECUTE")
    except InstallDenied as exc: result = {"status":"BLOCKED","reason":str(exc),"production_started":False}
    except Exception as exc: result = {"status":"FAILED","reason":type(exc).__name__,"production_started":False}
    Log("GOLD2_PYTHON_PARALLEL_RECOVERY",json.dumps(result,sort_keys=True))
