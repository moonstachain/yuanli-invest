#!python3
"""Only tighten the verified new r3 python root from 0777 to 0700."""
import hashlib
import json
import os
import stat
BASE="/opt/yuanli-gold2-runtime"
ROOT=BASE+"/cpython-3.12.14-20260924-x86_64-recovery-20260926-r3"
PYTHON=ROOT+"/python"
EXE=PYTHON+"/bin/python3.12"
BINARY_SHA="edffa803e5c4d73a1357f7f2c6c9fd38e9693712b2c06793e6a5e5cc1090d03a"
HARDEN_MODE="DRY_RUN"


def harden(*,execute=False):
    if os.geteuid()!=0:raise ValueError("HOST_UID_CHANGED")
    for path,mode in (("/opt",0o755),(BASE,0o700),(ROOT,0o700),(PYTHON,None),(PYTHON+"/bin",0o700)):
        info=os.lstat(path)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0:
            raise ValueError("OWN_DIRECTORY_INVALID")
        actual=stat.S_IMODE(info.st_mode)
        if (mode is not None and actual!=mode) or (mode is None and actual not in (0o777,0o700)):
            raise ValueError("REVIEWED_DIRECTORY_MODE_CHANGED")
    fd=os.open(EXE,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,"rb") as raw:
        info=os.fstat(raw.fileno())
        if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o700
                or info.st_uid!=0 or info.st_nlink!=1 or info.st_size!=30964240):
            raise ValueError("REVIEWED_BINARY_METADATA_CHANGED")
        digest=hashlib.sha256();count=0
        while True:
            block=raw.read(65536)
            if not block:break
            count+=len(block)
            if count>30964240:raise ValueError("REVIEWED_BINARY_SIZE_CHANGED")
            digest.update(block)
    if count!=30964240 or digest.hexdigest()!=BINARY_SHA:raise ValueError("REVIEWED_BINARY_HASH_CHANGED")
    fd=os.open(PYTHON,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd);before=stat.S_IMODE(info.st_mode)
        current=os.lstat(PYTHON)
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or before not in (0o777,0o700)
                or (info.st_dev,info.st_ino)!=(current.st_dev,current.st_ino)):
            raise ValueError("OWN_DIRECTORY_CHANGED")
        if execute and before==0o777:os.fchmod(fd,0o700)
        after=stat.S_IMODE(os.fstat(fd).st_mode)
        if execute and after!=0o700:raise ValueError("HARDEN_READBACK_FAILED")
    finally:os.close(fd)
    return {"schema_version":"gold2-python312-owned-root-harden.v1",
            "status":"HARDENED" if execute else "DRY_RUN", "directory":PYTHON,
            "mode_before":oct(before),"mode_after":oct(after),"changed":execute and before!=after,
            "installed_binary_sha256":BINARY_SHA,"directory_scan_performed":False,
            "system_python_modified":False,"account_access_performed":False,"production_started":False}


def main():
    try:
        if HARDEN_MODE not in ("DRY_RUN","EXECUTE"):raise ValueError("HARDEN_MODE_INVALID")
        result=harden(execute=HARDEN_MODE=="EXECUTE")
    except ValueError as exc:result={"status":"BLOCKED","reason":str(exc)}
    except Exception as exc:result={"status":"BLOCKED","reason":type(exc).__name__}
    Log("GOLD2_PYTHON312_OWNED_ROOT_HARDEN",json.dumps(result,sort_keys=True))
