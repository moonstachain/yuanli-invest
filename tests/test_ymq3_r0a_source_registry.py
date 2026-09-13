from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "ymq3" / "r0a_source_registry.v0.1.json"
AUDIT_DOC = ROOT / "docs" / "architecture" / "ymq3" / "YMQ3-R0A-SOURCE-AUTHORITY-AUDIT-v0.1.md"

REQUIRED_FIELDS = [
    "source_id",
    "publisher_group_id",
    "source_family",
    "source_class",
    "case_coverage",
    "historical_start",
    "historical_end",
    "timestamp_authority",
    "access_mode",
    "machine_access",
    "primary_locator",
    "terms_locator",
    "processing_authority",
    "raw_storage_authority",
    "derived_feature_storage_authority",
    "redistribution_authority",
    "attribution_required",
    "registry_verdict",
    "verified_at",
    "verification_evidence_refs",
    "notes",
]
REQUIRED_SOURCE_IDS = [
    "FRED_ALFRED",
    "SEC_EDGAR",
    "FED_OFFICIAL",
    "WHO_OFFICIAL",
    "OPENAI_PRIMARY",
    "GDELT_2_GKG_MENTIONS",
    "GDELT_1_EVENTS",
    "GOOGLE_TRENDS",
    "GOOGLE_BOOKS_NGRAM",
    "INTERNET_ARCHIVE_WAYBACK",
    "CSRC_OFFICIAL",
    "PBOC_OFFICIAL",
    "NBS_OFFICIAL",
    "SSE_OFFICIAL",
    "SZSE_OFFICIAL",
    "CNINFO_DISCLOSURES",
    "LICENSED_EN_NEWS_ARCHIVE",
    "LICENSED_CN_FIN_NEWS_ARCHIVE",
]


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


class SourceAuthorityRegistryTest(unittest.TestCase):
    def test_registry_and_human_audit_exist(self):
        self.assertTrue(REGISTRY.exists(), "source authority registry must exist")
        self.assertTrue(AUDIT_DOC.exists(), "source authority audit must exist")

    def test_required_sources_and_fields_are_frozen(self):
        self.assertTrue(REGISTRY.exists(), "missing source registry")
        sources = load_registry()["sources"]
        self.assertEqual([s["source_id"] for s in sources], REQUIRED_SOURCE_IDS)
        for source in sources:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, source, f"{source.get('source_id')} missing {field}")

    def test_rights_are_explicit_and_public_access_never_implies_storage(self):
        self.assertTrue(REGISTRY.exists(), "missing source registry")
        for source in load_registry()["sources"]:
            for axis in [
                "processing_authority",
                "raw_storage_authority",
                "derived_feature_storage_authority",
                "redistribution_authority",
            ]:
                self.assertIn(source[axis], ["ALLOW", "DENY", "UNKNOWN"])
            if source["access_mode"] in ["PUBLIC_WEB", "PUBLIC_API", "OPEN_DATA_DOWNLOAD"]:
                self.assertNotEqual(source.get("rights_inference"), "PUBLIC_MEANS_RAW_STORAGE_ALLOWED")

    def test_uncontracted_licensed_archive_capabilities_fail_closed(self):
        self.assertTrue(REGISTRY.exists(), "missing source registry")
        by_id = {s["source_id"]: s for s in load_registry()["sources"]}
        for sid in ["LICENSED_EN_NEWS_ARCHIVE", "LICENSED_CN_FIN_NEWS_ARCHIVE"]:
            s = by_id[sid]
            self.assertEqual(s["registry_verdict"], "UNKNOWN_DENY")
            self.assertEqual(s["processing_authority"], "UNKNOWN")
            self.assertEqual(s["raw_storage_authority"], "UNKNOWN")
            self.assertEqual(s["machine_access"], "UNVERIFIED")

    def test_gdelt_and_trends_are_not_silently_promoted_to_primary_story_truth(self):
        self.assertTrue(REGISTRY.exists(), "missing source registry")
        by_id = {s["source_id"]: s for s in load_registry()["sources"]}
        self.assertIn(by_id["GDELT_1_EVENTS"]["story_role"], ["EVENT_CONTEXT", "ANNOTATION_ONLY"])
        self.assertIn(by_id["GOOGLE_TRENDS"]["story_role"], ["ATTENTION_PROXY", "ANNOTATION_ONLY"])
        self.assertNotEqual(by_id["GDELT_1_EVENTS"]["story_role"], "PRIMARY_NARRATIVE_TRUTH")
        self.assertNotEqual(by_id["GOOGLE_TRENDS"]["story_role"], "PRIMARY_NARRATIVE_TRUTH")

    def test_gdelt_2_and_ngram_rights_are_supported_by_explicit_terms_refs(self):
        self.assertTrue(REGISTRY.exists(), "missing source registry")
        by_id = {s["source_id"]: s for s in load_registry()["sources"]}
        gdelt = by_id["GDELT_2_GKG_MENTIONS"]
        self.assertEqual(gdelt["processing_authority"], "ALLOW")
        self.assertEqual(gdelt["raw_storage_authority"], "ALLOW")
        self.assertEqual(gdelt["derived_feature_storage_authority"], "ALLOW")
        self.assertEqual(gdelt["redistribution_authority"], "ALLOW")
        self.assertTrue(gdelt["terms_locator"].startswith("https://gdeltproject.org/"))
        ngram = by_id["GOOGLE_BOOKS_NGRAM"]
        self.assertEqual(ngram["processing_authority"], "ALLOW")
        self.assertEqual(ngram["redistribution_authority"], "ALLOW")
        self.assertTrue(ngram["terms_locator"].startswith("https://books.google.com/"))


if __name__ == "__main__":
    unittest.main()
