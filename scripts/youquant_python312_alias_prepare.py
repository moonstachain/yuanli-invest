#!python3
"""Verify only our installed r3 tree; optionally create one private short alias."""
import hashlib
import json
import os
import stat
import subprocess
import sys

BASE = "/opt/yuanli-gold2-runtime"
ROOT = BASE + "/cpython-3.12.14-20260924-x86_64-recovery-20260926-r3"
EXE = ROOT + "/python/bin/python3.12"
RECEIPT = ROOT + "/install-receipt.json"
ALIAS = BASE + "/python312"
BINARY_SIZE = 30964240
BINARY_SHA = "edffa803e5c4d73a1357f7f2c6c9fd38e9693712b2c06793e6a5e5cc1090d03a"
PACKAGE_SHA = "269b2c99e4db15b242bf01832f4fea1e8f1a664f273cff519393f296e9820b41"
ALIAS_MODE = "DRY_RUN"


def verified_read(path, limit, *, executable=False):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd,"rb") as raw:
        info = os.fstat(raw.fileno())
        mode = 0o700 if executable else 0o600
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_nlink != 1
                or stat.S_IMODE(info.st_mode) != mode or not 0 < info.st_size <= limit):
            raise ValueError("OWN_FILE_METADATA_INVALID")
        data = raw.read(limit+1)
    if len(data)>limit: raise ValueError("OWN_FILE_OVERSIZE")
    return data


def prepare(*,execute=False):
    if os.geteuid()!=0: raise ValueError("HOST_UID_CHANGED")
    for path in ("/opt",BASE,ROOT,ROOT+"/python",ROOT+"/python/bin"):
        info=os.lstat(path)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0:
            raise ValueError("OWN_DIRECTORY_INVALID")
        if path!="/opt" and stat.S_IMODE(info.st_mode)!=0o700:
            raise ValueError("OWN_DIRECTORY_MODE_INVALID")
    receipt=json.loads(verified_read(RECEIPT,16384))
    if (receipt.get("schema_version")!="gold-au-python-relay-parallel-recovery.v1"
            or receipt.get("status")!="RECOVERED_INSTALLED_NOT_PRODUCTION_ENABLED"
            or receipt.get("download")!={"bytes":34270188,"sha256":PACKAGE_SHA}
            or receipt.get("smoke")!={"executable":EXE,"stdlib_smoke":"PASS","version":[3,12,14]}):
        raise ValueError("INSTALL_RECEIPT_INVALID")
    binary=verified_read(EXE,BINARY_SIZE,executable=True)
    if len(binary)!=BINARY_SIZE or hashlib.sha256(binary).hexdigest()!=BINARY_SHA:
        raise ValueError("INSTALLED_BINARY_HASH_INVALID")
    del binary
    code="import sys,json; print(json.dumps({'version':list(sys.version_info[:3]),'executable':sys.executable},sort_keys=True))"
    result=subprocess.run([EXE,"-I","-B","-c",code],capture_output=True,text=True,env={},timeout=15,check=False)
    if result.returncode!=0 or len(result.stdout)>1024: raise ValueError("INSTALLED_INTERPRETER_START_FAILED")
    probe=json.loads(result.stdout)
    if probe!={"version":[3,12,14],"executable":EXE}: raise ValueError("INSTALLED_INTERPRETER_PROBE_INVALID")
    existed=os.path.lexists(ALIAS)
    if existed:
        info=os.lstat(ALIAS)
        if not stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or os.readlink(ALIAS)!=EXE:
            raise ValueError("ALIAS_ALREADY_EXISTS_DIFFERENT")
    if execute and not existed: os.symlink(EXE,ALIAS)
    created=execute and not existed
    if execute and os.path.realpath(ALIAS)!=EXE: raise ValueError("ALIAS_REALPATH_INVALID")
    return {"schema_version":"gold2-python312-private-alias.v1",
            "status":"ALIAS_READY" if execute else "DRY_RUN_VERIFIED",
            "installed_interpreter":probe,"installed_binary_sha256":BINARY_SHA,
            "alias":ALIAS,"realpath":os.path.realpath(ALIAS) if execute or existed else None,
            "alias_created":created,"current_strategy_python":list(sys.version_info[:3]),
            "account_access_performed":False,"system_python_modified":False,
            "production_started":False}


def main():
    try:
        if ALIAS_MODE not in ("DRY_RUN","EXECUTE"):raise ValueError("ALIAS_MODE_INVALID")
        result=prepare(execute=ALIAS_MODE=="EXECUTE")
    except ValueError as exc:
        known={"HOST_UID_CHANGED","OWN_FILE_METADATA_INVALID","OWN_FILE_OVERSIZE","OWN_DIRECTORY_INVALID",
               "OWN_DIRECTORY_MODE_INVALID","INSTALL_RECEIPT_INVALID","INSTALLED_BINARY_HASH_INVALID",
               "INSTALLED_INTERPRETER_START_FAILED","INSTALLED_INTERPRETER_PROBE_INVALID",
               "ALIAS_ALREADY_EXISTS_DIFFERENT","ALIAS_REALPATH_INVALID","ALIAS_MODE_INVALID"}
        result={"status":"BLOCKED","reason":str(exc) if str(exc) in known else "ALIAS_VERIFICATION_INVALID"}
    except Exception as exc:result={"status":"BLOCKED","reason":type(exc).__name__}
    Log("GOLD2_PYTHON312_PRIVATE_ALIAS",json.dumps(result,sort_keys=True))
