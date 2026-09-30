"""Private durable publisher hints; broker truth remains the remote receipt.

The local append chain detects corruption and retains uncertain publication IDs.
It is not an independently anchored or tamper-proof source of trading truth.
"""
from __future__ import annotations
from collections.abc import Mapping
from contextlib import contextmanager
import fcntl
from datetime import datetime, timezone
import re
import json
import os
from pathlib import Path
import stat
from typing import Any
from .gold_au_receipt_client import canonical_bytes, object_hash
from .gold_paper import PaperDenied

MAX_BYTES=2_100_000


class ReaderPublicationJournal:
    def __init__(self, path: Path, binding: Mapping, *, initialize: bool=False,
                 clock=lambda:datetime.now(timezone.utc)):
        self.path=Path(path)
        self.binding=dict(binding);self.clock=clock
        if not self.path.is_absolute() or self.path.parent.resolve()!=self.path.parent:
            raise PaperDenied("READER_JOURNAL_PRIVATE_PATH_REQUIRED")
        info=self.path.parent.stat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid()
                or stat.S_IMODE(info.st_mode)!=0o700):
            raise PaperDenied("READER_JOURNAL_PRIVATE_DIRECTORY_REQUIRED")
        if initialize:
            descriptor=None
            try:
                descriptor=self._open_private(self.path,initialize=True)
            finally:
                if descriptor is not None:os.close(descriptor)
        self.read()

    def _open_directory(self) -> int:
        """Revalidate the named private directory on every open, then pin its fd."""
        if self.path.parent.resolve()!=self.path.parent:
            raise PaperDenied("READER_JOURNAL_PRIVATE_PATH_REQUIRED")
        descriptor=os.open(self.path.parent,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0))
        try:
            info=os.fstat(descriptor)
            named=os.stat(self.path.parent,follow_symlinks=False)
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid()
                    or stat.S_IMODE(info.st_mode)!=0o700
                    or (info.st_dev,info.st_ino)!=(named.st_dev,named.st_ino)):
                raise PaperDenied("READER_JOURNAL_PRIVATE_DIRECTORY_REQUIRED")
        except Exception:
            os.close(descriptor)
            raise
        return descriptor

    def _fsync_directory(self) -> None:
        descriptor=self._open_directory()
        try:os.fsync(descriptor)
        finally:os.close(descriptor)

    def _open_private(self,path: Path,*,initialize: bool=False,lock: bool=False) -> int:
        if path.parent!=self.path.parent:
            raise PaperDenied("READER_JOURNAL_PRIVATE_PATH_REQUIRED")
        created=False;directory=self._open_directory()
        try:
            if initialize or lock:
                try:
                    descriptor=os.open(path.name,os.O_RDWR|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600,dir_fd=directory)
                    created=True
                except FileExistsError:
                    if initialize:raise PaperDenied("READER_JOURNAL_ALREADY_INITIALIZED")
                    descriptor=os.open(path.name,os.O_RDWR|getattr(os,"O_NOFOLLOW",0),dir_fd=directory)
            else:
                descriptor=os.open(path.name,os.O_RDWR|getattr(os,"O_NOFOLLOW",0),dir_fd=directory)
        except FileNotFoundError as exc:
            raise PaperDenied("READER_JOURNAL_MISSING_RESUME_DENIED") from exc
        finally:
            os.close(directory)
        info=os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600
                or info.st_uid!=os.getuid() or info.st_nlink!=1 or info.st_size>MAX_BYTES):
            os.close(descriptor)
            raise PaperDenied("READER_JOURNAL_FILE_DENIED")
        if created:
            try:
                os.fsync(descriptor)
                self._fsync_directory()
            except Exception:
                os.close(descriptor)
                raise
        return descriptor

    def _open(self) -> int:
        return self._open_private(self.path)

    def _parse(self, descriptor: int) -> list[dict]:
        os.lseek(descriptor,0,os.SEEK_SET)
        raw=os.read(descriptor,MAX_BYTES+1)
        if len(raw)>MAX_BYTES or raw and not raw.endswith(b"\n"):
            raise PaperDenied("READER_JOURNAL_CORRUPT")
        previous="0"*64;events=[];previous_at=None;states={};pending=None;unknown_ever=False
        try:
            for sequence,line in enumerate(raw.splitlines(),1):
                event=json.loads(line)
                if (not isinstance(event,dict) or set(event)!={"sequence","previous_hash","binding","kind","at","data","event_hash"}
                        or type(event["sequence"]) is not int or event["sequence"]!=sequence
                        or event["previous_hash"]!=previous or event["binding"]!=self.binding
                        or event["kind"] not in {"PublicationPrepared","PublicationIngestAcknowledged","PublicationIngestUnknown","PublicationReadbackConfirmed"}
                        or not isinstance(event["data"],dict)
                        or object_hash({k:v for k,v in event.items() if k!="event_hash"})!=event["event_hash"]):
                    raise PaperDenied("READER_JOURNAL_CHAIN_OR_BINDING_MISMATCH")
                if canonical_bytes(event)!=line:
                    raise PaperDenied("READER_JOURNAL_NONCANONICAL_OR_DUPLICATE_KEYS")
                at=datetime.fromisoformat(event["at"].replace("Z","+00:00"))
                now=self.clock()
                if (at.tzinfo is None or at.utcoffset() is None or now.tzinfo is None or at>now
                        or previous_at is not None and at<previous_at):
                    raise PaperDenied("READER_JOURNAL_TIME_REVERSED_OR_FUTURE")
                data=event["data"];evidence_id=data.get("evidence_id")
                if not isinstance(evidence_id,str) or not re.fullmatch(r"EV3-[0-9a-f]{64}",evidence_id):
                    raise PaperDenied("READER_JOURNAL_EVIDENCE_ID_INVALID")
                kind=event["kind"]
                if kind=="PublicationPrepared":
                    if (set(data)!={"evidence_id","kind","facts_sha256","observed_at"}
                            or data["kind"] not in {"NATIVE_ORDER","PAIRED_TERMINAL"}
                            or not isinstance(data["facts_sha256"],str) or not re.fullmatch(r"sha256:[0-9a-f]{64}",data["facts_sha256"])
                            or evidence_id in states or pending is not None or unknown_ever):
                        raise PaperDenied("READER_JOURNAL_PREPARE_STATE_OR_DATA_DENIED")
                    observed=datetime.fromisoformat(data["observed_at"].replace("Z","+00:00"))
                    if observed.tzinfo is None or observed.utcoffset() is None or observed>at:
                        raise PaperDenied("READER_JOURNAL_OBSERVATION_TIME_DENIED")
                    expected="EV3-"+object_hash({k:data[k] for k in ("kind","observed_at","facts_sha256")})[7:]
                    if expected!=evidence_id:raise PaperDenied("READER_JOURNAL_OBSERVATION_BINDING_MISMATCH")
                    states[evidence_id]="PREPARED";pending=evidence_id
                else:
                    if set(data)!={"evidence_id"} or evidence_id!=pending:
                        raise PaperDenied("READER_JOURNAL_TRANSITION_SCOPE_DENIED")
                    if kind=="PublicationIngestAcknowledged":
                        if states[evidence_id]!="PREPARED":raise PaperDenied("READER_JOURNAL_ACK_STATE_DENIED")
                        states[evidence_id]="ACKNOWLEDGED"
                    elif kind=="PublicationIngestUnknown":
                        if states[evidence_id]!="PREPARED":raise PaperDenied("READER_JOURNAL_UNKNOWN_STATE_DENIED")
                        states[evidence_id]="UNKNOWN";unknown_ever=True
                    elif kind=="PublicationReadbackConfirmed":
                        if states[evidence_id] not in {"PREPARED","ACKNOWLEDGED","UNKNOWN"}:
                            raise PaperDenied("READER_JOURNAL_READBACK_STATE_DENIED")
                        states[evidence_id]="CONFIRMED";pending=None
                previous=event["event_hash"];previous_at=at;events.append(event)
        except (UnicodeError,ValueError,TypeError,KeyError,AttributeError) as exc:
            raise PaperDenied("READER_JOURNAL_CORRUPT") from exc
        return events

    def read(self) -> list[dict]:
        descriptor=None
        try:
            descriptor=self._open();fcntl.flock(descriptor,fcntl.LOCK_SH)
            return self._parse(descriptor)
        except OSError as exc:
            raise PaperDenied("READER_JOURNAL_UNAVAILABLE") from exc
        finally:
            if descriptor is not None:os.close(descriptor)

    def append(self, *, kind: str, at: str, data: Mapping[str,Any]) -> None:
        descriptor=None
        try:
            descriptor=self._open();fcntl.flock(descriptor,fcntl.LOCK_EX)
            events=self._parse(descriptor)
            event={"sequence":len(events)+1,"previous_hash":events[-1]["event_hash"] if events else "0"*64,
                "binding":self.binding,"kind":kind,"at":at,"data":dict(data)}
            event["event_hash"]=object_hash(event);raw=canonical_bytes(event)+b"\n"
            if os.lseek(descriptor,0,os.SEEK_END)+len(raw)>MAX_BYTES:
                raise PaperDenied("READER_JOURNAL_FULL")
            written=os.write(descriptor,raw)
            if written!=len(raw):raise PaperDenied("READER_JOURNAL_WRITE_UNCERTAIN")
            os.fsync(descriptor)
            self._fsync_directory()
        except OSError as exc:
            raise PaperDenied("READER_JOURNAL_WRITE_UNCERTAIN") from exc
        finally:
            if descriptor is not None:os.close(descriptor)


    @contextmanager
    def publisher_guard(self):
        """One publication pipeline per journal; held across network writes."""
        descriptor=None
        try:
            lock_path=Path(str(self.path)+".lock")
            descriptor=self._open_private(lock_path,lock=True)
            try:
                fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise PaperDenied("INDEPENDENT_READER_PUBLICATION_ALREADY_RUNNING") from exc
            yield
        except OSError as exc:
            raise PaperDenied("READER_JOURNAL_LOCK_UNAVAILABLE") from exc
        finally:
            if descriptor is not None:os.close(descriptor)
