from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ymq3_r0a_evidence.py"
STATUS = ROOT / "config" / "ymq3" / "r0a_case_evidence_status.v0.1.json"
GATE = ROOT / "config" / "ymq3" / "r0a_evidence_gate.v0.1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("ymq3_r0a_evidence", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evidence module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvidenceCompilerTest(unittest.TestCase):
    def test_artifacts_exist(self):
        self.assertTrue(SCRIPT.exists(), "evidence compiler must exist")
        self.assertTrue(STATUS.exists(), "case evidence status must exist")

    def test_future_publication_is_rejected(self):
        self.assertTrue(SCRIPT.exists())
        m = load_module()
        row = {
            "case_id": "C6_AI", "document_id": "d1", "source_id": "GDELT_2_GKG_MENTIONS",
            "publisher_group_id": "P1", "week_end": "2023-01-06T23:59:59Z",
            "publication_available_at": "2023-01-07T00:00:00Z", "timestamp_authority": "TS3_PROVIDER_INDEXED",
            "processing_authority": "ALLOW", "raw_payload_stored": False, "raw_storage_authority": "ALLOW",
            "eligible_for_story": True,
        }
        with self.assertRaises(ValueError):
            m.validate_evidence_row(row)

    def test_ts4_unknown_processing_and_unauthorized_raw_storage_are_rejected(self):
        self.assertTrue(SCRIPT.exists())
        m = load_module()
        base = {
            "case_id": "C6_AI", "document_id": "d1", "source_id": "X", "publisher_group_id": "P1",
            "week_end": "2023-01-06T23:59:59Z", "publication_available_at": "2023-01-06T12:00:00Z",
            "timestamp_authority": "TS3_PROVIDER_INDEXED", "processing_authority": "ALLOW",
            "raw_payload_stored": False, "raw_storage_authority": "ALLOW", "eligible_for_story": True,
        }
        bad = dict(base, timestamp_authority="TS4_INFERRED_RETROSPECTIVE")
        with self.assertRaises(ValueError): m.validate_evidence_row(bad)
        bad = dict(base, processing_authority="UNKNOWN")
        with self.assertRaises(ValueError): m.validate_evidence_row(bad)
        bad = dict(base, raw_payload_stored=True, raw_storage_authority="DENY")
        with self.assertRaises(ValueError): m.validate_evidence_row(bad)

    def test_weekly_coverage_counts_publisher_groups_not_urls(self):
        self.assertTrue(SCRIPT.exists())
        m = load_module()
        rows = [
            {"case_id":"C6_AI","document_id":"d1","source_id":"S1","publisher_group_id":"GROUP_A","week_end":"2023-01-06T23:59:59Z","publication_available_at":"2023-01-06T10:00:00Z","timestamp_authority":"TS3_PROVIDER_INDEXED","processing_authority":"ALLOW","raw_payload_stored":False,"raw_storage_authority":"ALLOW","eligible_for_story":True},
            {"case_id":"C6_AI","document_id":"d2","source_id":"S1_MIRROR","publisher_group_id":"GROUP_A","week_end":"2023-01-06T23:59:59Z","publication_available_at":"2023-01-06T11:00:00Z","timestamp_authority":"TS3_PROVIDER_INDEXED","processing_authority":"ALLOW","raw_payload_stored":False,"raw_storage_authority":"ALLOW","eligible_for_story":True},
            {"case_id":"C6_AI","document_id":"d3","source_id":"S2","publisher_group_id":"GROUP_B","week_end":"2023-01-13T23:59:59Z","publication_available_at":"2023-01-13T11:00:00Z","timestamp_authority":"TS3_PROVIDER_INDEXED","processing_authority":"ALLOW","raw_payload_stored":False,"raw_storage_authority":"ALLOW","eligible_for_story":True},
        ]
        stats = m.weekly_coverage(rows, {"case_id":"C6_AI","start_date":"2023-01-01","end_date":"2023-01-15"})
        self.assertEqual(stats["covered_weeks"], 2)
        self.assertEqual(stats["multi_publisher_weeks"], 0, "same publisher group aliases must not create fake breadth")

    def test_case_ready_requires_domains_coverage_and_thresholds(self):
        self.assertTrue(SCRIPT.exists())
        m = load_module()
        stats = {
            "domain_statuses": {d: "PASS" for d in ["MARKET","MACRO_VINTAGE","OFFICIAL_ANCHOR","NARRATIVE_CORPUS","LICENSE_RIGHTS","PIT_PROVENANCE"]},
            "coverage_materialized": True,
            "pit_violation_count": 0, "unknown_processing_rights_count": 0, "unauthorized_raw_storage_count": 0,
            "timestamp_authority_rate": .96, "scored_week_presence_rate": .85,
            "median_eligible_documents_per_covered_week": 12, "multi_publisher_week_rate": .75,
            "narrative_media_family_present": True, "blocked_reasons": [],
        }
        self.assertEqual(m.case_evidence_verdict(stats), "READY")
        self.assertEqual(m.case_evidence_verdict(dict(stats, coverage_materialized=False)), "READY_WITH_LIMITATIONS")
        self.assertEqual(m.case_evidence_verdict(dict(stats, blocked_reasons=["no lawful corpus"])), "BLOCKED")

    def test_program_verdict_is_fail_closed(self):
        self.assertTrue(SCRIPT.exists())
        m = load_module()
        roles = {
            "C1_DOTCOM":"NARRATIVE_HEAVY", "C2_GFC":"ACUTE_SHOCK_HARD_NEGATIVE",
            "C3_CHINA_LEVERAGE":"NARRATIVE_HEAVY", "C4_COVID":"ACUTE_SHOCK_HARD_NEGATIVE",
            "C5_INFLATION":"MIXED_REALITY_NARRATIVE", "C6_AI":"NARRATIVE_HEAVY",
        }
        self.assertEqual(m.program_evidence_verdict({c:"READY" for c in roles}, roles), "FULL6_READY")
        open4 = {"C1_DOTCOM":"READY","C2_GFC":"READY","C3_CHINA_LEVERAGE":"READY","C4_COVID":"READY","C5_INFLATION":"INDETERMINATE","C6_AI":"INDETERMINATE"}
        self.assertEqual(m.program_evidence_verdict(open4, roles), "OPEN4_READY")
        insufficient = {c:"READY_WITH_LIMITATIONS" for c in roles}
        self.assertEqual(m.program_evidence_verdict(insufficient, roles), "INSUFFICIENT_EVIDENCE_INDETERMINATE")
        self.assertEqual(m.program_evidence_verdict(insufficient, roles, physical_fail=True), "PHYSICAL_FAIL")


if __name__ == "__main__":
    unittest.main()
