"""Future extraction helper: create every ancestor privately, never implicit parents.

The historical deployed installer stays unchanged. Future installers must select
this function explicitly; it keeps the original archive validation and writes.
"""
import os
from pathlib import PurePosixPath
import stat
import tarfile
from scripts.youquant_python_runtime_install import _archive_members, _no_symlink_ancestors, deny


def _private_dirs(root, directory):
    try:
        components=directory.relative_to(root).parts
    except ValueError:
        deny("ARCHIVE_DIRECTORY_OUTSIDE_ROOT")
    if any(component in ("", ".", "..") for component in components):
        deny("ARCHIVE_DIRECTORY_COMPONENT_INVALID")
    current=root
    for component in (None,)+components:
        if component is not None:
            current=current/component
            if not os.path.lexists(str(current)):
                current.mkdir(mode=0o700)
        info=current.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid()
                or stat.S_IMODE(info.st_mode)!=0o700):
            deny("ARCHIVE_DIRECTORY_NOT_PRIVATE")


def unpack_verified_private(archive_path, destination):
    """Same strong archive checks; all created and retained directories must be 0700."""
    _no_symlink_ancestors(destination)
    _private_dirs(destination,destination)
    if os.path.lexists(str(destination/"python")):
        deny("ARCHIVE_DESTINATION_ALREADY_EXISTS")
    with tarfile.open(str(archive_path),"r:gz") as archive:
        members=_archive_members(archive)
        for item in members:
            path=destination.joinpath(*PurePosixPath(item.name).parts)
            if item.isdir():
                _private_dirs(destination,path)
            elif item.isfile():
                _private_dirs(destination,path.parent)
                fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,
                           0o700 if item.mode&0o111 else 0o600)
                with os.fdopen(fd,"wb") as output,archive.extractfile(item) as source:
                    remaining=item.size
                    while remaining:
                        block=source.read(min(65536,remaining))
                        if not block:deny("ARCHIVE_TRUNCATED_MEMBER")
                        output.write(block);remaining-=len(block)
        for item in members:
            if item.issym():
                path=destination.joinpath(*PurePosixPath(item.name).parts)
                _private_dirs(destination,path.parent)
                path.symlink_to(item.linkname)
        return {"members":len(members),"unpacked_bytes":sum(item.size for item in members if item.isfile())}
