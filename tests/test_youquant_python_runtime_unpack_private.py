"""Regressions for implicit mkdir parents with an unrestricted host umask."""
import io
import os
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
from scripts.youquant_python_runtime_install import InstallDenied
from scripts.youquant_python_runtime_unpack_private import _private_dirs, unpack_verified_private


class PrivateUnpackTests(unittest.TestCase):
    def test_implicit_ancestors_are_all_private_with_umask_zero(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();destination=root/"owned";destination.mkdir(mode=0o700)
            archive=root/"fixed.tar.gz"
            with tarfile.open(archive,"w:gz") as output:
                member=tarfile.TarInfo("python/lib/deep/only-file");member.size=3;member.mode=0o644
                output.addfile(member,io.BytesIO(b"abc"))
            old=os.umask(0)
            try:result=unpack_verified_private(archive,destination)
            finally:os.umask(old)
            self.assertEqual(result["unpacked_bytes"],3)
            for relative in ("python","python/lib","python/lib/deep"):
                self.assertEqual(stat.S_IMODE((destination/relative).stat().st_mode),0o700)
            self.assertEqual(stat.S_IMODE((destination/"python/lib/deep/only-file").stat().st_mode),0o600)

    def test_existing_unsafe_parent_is_rejected_and_never_silently_repaired(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();root.chmod(0o700)
            parent=root/"unsafe";parent.mkdir(mode=0o700);parent.chmod(0o777)
            with self.assertRaisesRegex(InstallDenied,"ARCHIVE_DIRECTORY_NOT_PRIVATE"):
                _private_dirs(root,parent/"child")
            self.assertEqual(stat.S_IMODE(parent.stat().st_mode),0o777)
            self.assertFalse((parent/"child").exists())


if __name__=="__main__":unittest.main()
