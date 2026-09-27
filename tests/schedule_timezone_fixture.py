"""Explicit timezone-link fixtures; never changes the host or production gate."""
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch


@contextmanager
def host_timezone_link(zone="Asia/Shanghai"):
    original_resolve = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == Path("/etc/localtime"):
            return Path("/usr/share/zoneinfo") / zone
        return original_resolve(path, *args, **kwargs)

    with patch.object(Path, "resolve", new=resolve):
        yield
