"""Offline proof for same-asset bounded parallel range recovery."""
import hashlib
import io
from pathlib import Path
import queue
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch

from scripts import youquant_python_runtime_recover_parallel as parallel


class ParallelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.asset={"url":parallel.ASSET_URL,"size":10,"sha256":hashlib.sha256(b"abcdefghij").hexdigest()}

    def tearDown(self):self.temp.cleanup()

    def response(self, data=b"cdef",status=206,content_range="bytes 2-5/10"):
        value=io.BytesIO(data);value.status=status;value.headers={"Content-Range":content_range,"Content-Length":str(len(data))}
        value.geturl=lambda:"https://release-assets.githubusercontent.com/fixed";return value

    def download(self,response):
        opener=Mock();opener.open.return_value=response
        with patch.object(parallel.urllib.request,"build_opener",return_value=opener):
            result=parallel.download_part(self.asset,(0,2,5),self.root/"part-00.bin",time.monotonic()+100,
                                          threading.Event(),queue.Queue(maxsize=1024))
        self.opener=opener;return result

    def test_ranges_exact_cover_no_overlap(self):
        parts=parallel.byte_ranges(2490368,34270188,8)
        self.assertEqual(len(parts),8);self.assertEqual(parts[0][1],2490368);self.assertEqual(parts[-1][2],34270187)
        self.assertTrue(all(parts[i][2]+1==parts[i+1][1] for i in range(7)))
        self.assertEqual(sum(end-start+1 for _,start,end in parts),34270188-2490368)

    def test_exact_range_and_digest_for_one_part(self):
        result=self.download(self.response())
        self.assertEqual(result["bytes"],4);self.assertEqual(result["sha256"],hashlib.sha256(b"cdef").hexdigest())
        self.assertEqual(self.opener.open.call_args.args[0].get_header("Range"),"bytes=2-5")

    def test_unsupported_range_and_wrong_headers_denied_before_write(self):
        for response,reason in ((self.response(status=200),"PARALLEL_RANGE_UNSUPPORTED"),
                                (self.response(content_range="bytes 0-3/10"),"PARALLEL_CONTENT_RANGE_MISMATCH"),
                                (self.response(content_range="bytes 2-5/11"),"PARALLEL_CONTENT_RANGE_MISMATCH"),
                                (self.response(b"cde"),"PARALLEL_CONTENT_LENGTH_MISMATCH")):
            with self.subTest(reason=reason),self.assertRaisesRegex(parallel.InstallDenied,reason):self.download(response)
            self.assertFalse((self.root/"part-00.bin").exists())

    def test_deadline_cancel_short_read_and_oversize_denied(self):
        for data,reason in ((b"cde","PARALLEL_PART_TRUNCATED"),(b"cdefg","PARALLEL_PART_SIZE_EXCEEDED")):
            response=self.response(data);response.headers.pop("Content-Length")
            with self.subTest(reason=reason),self.assertRaisesRegex(parallel.InstallDenied,reason):self.download(response)
            (self.root/"part-00.bin").unlink()
        with patch.object(parallel.time,"monotonic",side_effect=[0,101]),self.assertRaisesRegex(parallel.InstallDenied,"PARALLEL_DEADLINE_EXCEEDED"):
            self.download(self.response())

    def test_final_merge_digest_required_and_ordered(self):
        seed=self.root/"seed";seed.write_bytes(b"ab")
        (self.root/"part-00.bin").write_bytes(b"cdef");(self.root/"part-01.bin").write_bytes(b"ghij")
        plan={"asset":self.asset};manifest={"parts":[{"index":0},{"index":1}]}
        archive,result=parallel.merge_verify(plan,seed,self.root,manifest)
        self.assertEqual(archive.read_bytes(),b"abcdefghij");self.assertEqual(result["sha256"],self.asset["sha256"])
        archive.unlink();(self.root/"part-01.bin").write_bytes(b"xxxx")
        with self.assertRaisesRegex(parallel.InstallDenied,"PARALLEL_FINAL_SIZE_OR_SHA256_MISMATCH"):
            parallel.merge_verify(plan,seed,self.root,manifest)

    def test_parallel_failure_retains_manifest_and_stops_before_merge(self):
        plan={"original":{"partial_bytes":2},"asset":self.asset,"workers":2,"deadline_seconds":3}
        def fake(asset,part,target,deadline,stop,messages):
            if part[0]==0:raise parallel.InstallDenied("TEST_RANGE_FAILURE")
            target.write_bytes(b"partial")
            raise parallel.InstallDenied("PARALLEL_CANCELLED")
        with patch.object(parallel,"download_part",side_effect=fake),self.assertRaisesRegex(parallel.InstallDenied,"PARALLEL_INCOMPLETE_PARTS_RETAINED"):
            parallel.download_parts(plan,self.root,progress=lambda *args:None)
        self.assertTrue((self.root/"download-parts-manifest.json").exists())
        self.assertTrue((self.root/"part-01.bin").exists())

    def test_known_prefix_metadata_must_match_exactly(self):
        facts={"status":"BLOCKED","reason":"UNSAFE_PARTIAL_ARCHIVE","partial_type":"REGULAR",
               "partial_bytes":2490368,"partial_mode":"0o666","owner_uid":0,"partial_nlink":1,
               "receipt_present":False,"unpacked_tree_present":False}
        host={"system":"Linux","machine":"x86_64","libc":"glibc 2.31","uid":0}
        with patch.object(parallel,"_host",return_value=host),patch.object(parallel,"partial_facts",return_value=facts):
            result=parallel.parallel_plan()
            self.assertFalse(Path(result["recovery_target"]).exists())
            for key,value in (("partial_bytes",2490369),("partial_mode","0o664"),("partial_nlink",2),("owner_uid",1)):
                original=facts[key];facts[key]=value
                with self.subTest(key=key),self.assertRaisesRegex(parallel.InstallDenied,"REVIEWED_PARTIAL_FACTS_CHANGED"):
                    parallel.parallel_plan()
                facts[key]=original

    def test_default_dry_run_and_failed_hash_never_reaches_binary(self):
        plan={"recovery_target":str(self.root/"new-tree"),"asset":self.asset}
        with patch.object(parallel,"parallel_plan",return_value=plan),patch.object(parallel,"copy_retained_partial",side_effect=AssertionError("write")):
            self.assertEqual(parallel.parallel_recover()["status"],"DRY_RUN")
        with patch.object(parallel,"parallel_plan",return_value=plan),patch.object(parallel,"copy_retained_partial",return_value={}), \
                patch.object(parallel,"download_parts",side_effect=parallel.InstallDenied("PARALLEL_INCOMPLETE_PARTS_RETAINED")), \
                patch.object(parallel,"unpack_verified",side_effect=AssertionError("unpack")), \
                patch.object(parallel,"smoke_interpreter",side_effect=AssertionError("binary")), \
                self.assertRaisesRegex(parallel.InstallDenied,"PARALLEL_INCOMPLETE_PARTS_RETAINED"):
            parallel.parallel_recover(execute=True)


if __name__=="__main__":unittest.main()
