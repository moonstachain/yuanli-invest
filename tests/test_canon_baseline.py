import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def objects(directory: str):
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "canon" / directory).glob("*.json"))
    ]


class CanonBaselineTests(unittest.TestCase):
    def test_required_counts(self):
        self.assertEqual(len(objects("narratives")), 8)
        self.assertEqual(len(objects("companies")), 57)
        self.assertEqual(len(objects("mappings")), 58)
        self.assertEqual(len(objects("replays")), 8)
        self.assertEqual(len(objects("evidence")), 40)
        self.assertEqual(len(objects("source-records")), 40)

    def test_research_and_identity_evidence_are_separate(self):
        methods = Counter(item["provenance"]["method"] for item in objects("evidence"))
        self.assertEqual(methods["evidence_ledger_clean_room_import"], 36)
        self.assertEqual(methods["identity_governance_addition"], 4)

    def test_company_identity_and_risk_dispositions(self):
        by_ticker = {item["ticker"]: item for item in objects("companies")}
        self.assertEqual(len(by_ticker), 57)
        self.assertEqual((by_ticker["301043"]["official_name"], by_ticker["301043"]["status"]), ("绿岛风", "rejected"))
        self.assertEqual((by_ticker["300446"]["official_name"], by_ticker["300446"]["status"]), ("航天智造", "rejected"))
        self.assertEqual((by_ticker["600636"]["listing_status"], by_ticker["600636"]["status"]), ("delisted", "expired"))
        self.assertEqual((by_ticker["600745"]["listing_status"], by_ticker["600745"]["status"]), ("risk_warning", "partial"))

    def test_duplicate_legacy_row_is_a_mapping_not_a_company(self):
        counts = Counter(item["company_id"] for item in objects("mappings"))
        self.assertEqual(counts["company-688008-sh"], 2)
        self.assertEqual(sum(counts.values()), 58)

    def test_failure_cases_and_admission_boundary(self):
        self.assertEqual(sum(1 for item in objects("replays") if item["failure_case"]), 4)
        all_items = []
        for directory in ("narratives", "companies", "mappings", "replays", "evidence", "source-records", "stages"):
            all_items.extend(objects(directory))
        self.assertFalse(any(item["status"] == "approved" for item in all_items))


if __name__ == "__main__":
    unittest.main()
