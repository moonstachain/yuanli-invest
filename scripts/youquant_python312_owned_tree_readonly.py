#!python3
"""Read metadata at five fixed owned paths; no directory scan or mutation."""
import hashlib
import json
import os
import stat
BASE="/opt/yuanli-gold2-runtime"
ROOT=BASE+"/cpython-3.12.14-20260924-x86_64-recovery-20260926-r3"
EXE=ROOT+"/python/bin/python3.12"


def main():
    result={"schema_version":"gold2-python312-owned-tree-metadata.v1","directories":[],
            "file_write_performed":False,"account_access_performed":False,"production_started":False}
    try:
        safe=True
        for path in ("/opt",BASE,ROOT,ROOT+"/python",ROOT+"/python/bin"):
            info=os.lstat(path)
            isdir=stat.S_ISDIR(info.st_mode)
            result["directories"].append({"path":path,"type":"DIRECTORY" if isdir else "OTHER",
                                          "mode":oct(stat.S_IMODE(info.st_mode)),"uid":info.st_uid})
            if not isdir or info.st_uid!=0:safe=False
            if path in (BASE,ROOT) and stat.S_IMODE(info.st_mode)!=0o700:safe=False
        info=os.lstat(EXE)
        regular=stat.S_ISREG(info.st_mode)
        result["binary"]={"type":"REGULAR" if regular else "OTHER","mode":oct(stat.S_IMODE(info.st_mode)),
                          "uid":info.st_uid,"nlink":info.st_nlink,"bytes":info.st_size}
        if not safe or not regular or info.st_uid!=0 or info.st_nlink!=1 or info.st_size!=30964240:
            raise ValueError("OWN_TREE_READ_DENIED")
        fd=os.open(EXE,os.O_RDONLY|os.O_NOFOLLOW)
        digest=hashlib.sha256()
        with os.fdopen(fd,"rb") as raw:
            remaining=30964240
            while remaining:
                block=raw.read(min(65536,remaining))
                if not block:raise ValueError("OWN_BINARY_TRUNCATED")
                digest.update(block);remaining-=len(block)
            if raw.read(1):raise ValueError("OWN_BINARY_OVERSIZE")
        result["binary"]["sha256"]=digest.hexdigest();result["status"]="READ_BACK"
    except Exception as exc:result.update(status="BLOCKED",reason=type(exc).__name__)
    Log("GOLD2_PYTHON312_OWNED_TREE_METADATA",json.dumps(result,sort_keys=True))
