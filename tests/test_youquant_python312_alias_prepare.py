"""Offline tests for one owned short interpreter alias, never system Python."""
import hashlib
import json
import stat
import types
import unittest
from unittest.mock import Mock,patch
from scripts import youquant_python312_alias_prepare as alias


class AliasTests(unittest.TestCase):
    def receipt(self):
        return {"schema_version":"gold-au-python-relay-parallel-recovery.v1",
                "status":"RECOVERED_INSTALLED_NOT_PRODUCTION_ENABLED",
                "download":{"bytes":34270188,"sha256":alias.PACKAGE_SHA},
                "smoke":{"executable":alias.EXE,"stdlib_smoke":"PASS","version":[3,12,14]}}

    def run_prepare(self, *, execute=False, existed=False, receipt=None, binary=b"x", realpath=None, link_target=None):
        directory=types.SimpleNamespace(st_mode=stat.S_IFDIR|0o700,st_uid=0)
        link=types.SimpleNamespace(st_mode=stat.S_IFLNK|0o777,st_uid=0)
        process=types.SimpleNamespace(returncode=0,stdout=json.dumps({"version":[3,12,14],"executable":alias.EXE}))
        with patch.object(alias.os,"geteuid",return_value=0), \
             patch.object(alias.os,"lstat",side_effect=lambda path:link if path==alias.ALIAS else directory), \
             patch.object(alias,"verified_read",side_effect=[json.dumps(receipt or self.receipt()).encode(),binary]), \
             patch.object(alias,"BINARY_SIZE",1), \
             patch.object(alias,"BINARY_SHA",hashlib.sha256(b"x").hexdigest()), \
             patch.object(alias.subprocess,"run",return_value=process) as start, \
             patch.object(alias.os.path,"lexists",return_value=existed), \
             patch.object(alias.os,"readlink",return_value=alias.EXE if link_target is None else link_target), \
             patch.object(alias.os.path,"realpath",return_value=alias.EXE if realpath is None else realpath), \
             patch.object(alias.os,"symlink") as write:
            result=alias.prepare(execute=execute)
        return result,start,write

    def test_default_dry_run_verifies_without_creating_alias(self):
        self.assertEqual(alias.ALIAS_MODE,"DRY_RUN")
        result,start,write=self.run_prepare()
        self.assertEqual(result["status"],"DRY_RUN_VERIFIED")
        write.assert_not_called()
        self.assertEqual(start.call_args.args[0][:3],[alias.EXE,"-I","-B"])
        self.assertEqual(start.call_args.kwargs["env"],{})
        self.assertEqual(start.call_args.kwargs["timeout"],15)

    def test_execute_creates_only_exact_private_symlink(self):
        result,_,write=self.run_prepare(execute=True)
        write.assert_called_once_with(alias.EXE,alias.ALIAS)
        self.assertEqual(result["status"],"ALIAS_READY")
        self.assertTrue(result["alias_created"])
        self.assertFalse(result["system_python_modified"])

    def test_exact_existing_alias_is_idempotent(self):
        result,_,write=self.run_prepare(execute=True,existed=True)
        write.assert_not_called();self.assertFalse(result["alias_created"])

    def test_conflicting_alias_rejected(self):
        with self.assertRaisesRegex(ValueError,"ALIAS_ALREADY_EXISTS_DIFFERENT"):
            self.run_prepare(execute=True,existed=True,link_target="/usr/bin/python3")

    def test_receipt_and_binary_changes_are_denied(self):
        bad=self.receipt();bad["smoke"]["version"]=[3,9,2]
        with self.assertRaisesRegex(ValueError,"INSTALL_RECEIPT_INVALID"):
            self.run_prepare(execute=True,receipt=bad)
        with self.assertRaisesRegex(ValueError,"INSTALLED_BINARY_HASH_INVALID"):
            self.run_prepare(execute=True,binary=b"y")

    def test_nonroot_stops_before_filesystem(self):
        with patch.object(alias.os,"geteuid",return_value=1000), \
             patch.object(alias.os,"lstat",side_effect=AssertionError("filesystem")), \
             self.assertRaisesRegex(ValueError,"HOST_UID_CHANGED"):
            alias.prepare(execute=True)


if __name__=="__main__":unittest.main()
