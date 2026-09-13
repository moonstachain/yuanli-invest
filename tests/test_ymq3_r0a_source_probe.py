from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ymq3_r0a_source_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ymq3_r0a_source_probe", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load source probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceProbeReceiptTest(unittest.TestCase):
    def test_probe_module_exists(self):
        self.assertTrue(SCRIPT.exists(), "source probe module must exist")

    def test_http_success_does_not_grant_rights(self):
        self.assertTrue(SCRIPT.exists(), "missing source probe module")
        m = load_module()
        source = {
            "source_id": "TEST",
            "processing_authority": "UNKNOWN",
            "raw_storage_authority": "UNKNOWN",
            "derived_feature_storage_authority": "UNKNOWN",
            "redistribution_authority": "UNKNOWN",
        }
        observed = {
            "run_id": "RUN-1",
            "probe_locator": "https://example.test/",
            "observed_at": "2026-09-13T12:00:00Z",
            "provider_status": "HTTP_200",
            "sample_historical_locator": "https://example.test/1999",
            "sample_publication_timestamp": "1999-01-01T00:00:00Z",
            "historical_range_observed": "1999-2002",
            "machine_access_observed": "PUBLIC_WEB",
            "terms_locator_observed": "https://example.test/terms",
            "content_or_metadata_hash": "sha256:" + "a" * 64,
            "notes": "fixture",
        }
        receipt = m.build_probe_receipt(source, observed)
        self.assertEqual(receipt["rights_verdict_observed"], "UNKNOWN_DENY")

    def test_receipt_keeps_publication_archive_and_retrieval_clocks_separate(self):
        self.assertTrue(SCRIPT.exists(), "missing source probe module")
        m = load_module()
        source = {
            "source_id": "TEST",
            "processing_authority": "ALLOW",
            "raw_storage_authority": "DENY",
            "derived_feature_storage_authority": "ALLOW",
            "redistribution_authority": "DENY",
        }
        observed = {
            "run_id": "RUN-2",
            "probe_locator": "https://example.test/",
            "observed_at": "2026-09-13T12:00:00Z",
            "provider_status": "HTTP_200",
            "sample_historical_locator": "https://example.test/2008",
            "sample_publication_timestamp": "2008-09-15T00:00:00Z",
            "sample_available_at": "2008-09-15T00:00:00Z",
            "sample_archive_capture_at": "2008-09-16T00:00:00Z",
            "sample_retrieved_at": "2026-09-13T12:00:00Z",
            "historical_range_observed": "2008-2009",
            "machine_access_observed": "PUBLIC_WEB",
            "terms_locator_observed": "https://example.test/terms",
            "content_or_metadata_hash": "sha256:" + "b" * 64,
            "notes": "fixture",
        }
        receipt = m.build_probe_receipt(source, observed)
        self.assertEqual(receipt["sample_publication_timestamp"], "2008-09-15T00:00:00Z")
        self.assertEqual(receipt["sample_archive_capture_at"], "2008-09-16T00:00:00Z")
        self.assertEqual(receipt["sample_retrieved_at"], "2026-09-13T12:00:00Z")
        m.validate_probe_receipt(receipt)

    def test_invalid_hash_fails_closed(self):
        self.assertTrue(SCRIPT.exists(), "missing source probe module")
        m = load_module()
        with self.assertRaises(ValueError):
            m.validate_probe_receipt({
                "run_id": "RUN-X",
                "source_id": "TEST",
                "probe_locator": "https://example.test/",
                "observed_at": "2026-09-13T12:00:00Z",
                "provider_status": "HTTP_200",
                "sample_historical_locator": None,
                "sample_publication_timestamp": None,
                "sample_available_at": None,
                "sample_archive_capture_at": None,
                "sample_retrieved_at": "2026-09-13T12:00:00Z",
                "historical_range_observed": None,
                "machine_access_observed": "PUBLIC_WEB",
                "terms_locator_observed": None,
                "rights_verdict_observed": "UNKNOWN_DENY",
                "content_or_metadata_hash": "bad-hash",
                "notes": "fixture",
            })


if __name__ == "__main__":
    unittest.main()
