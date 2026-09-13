from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ymq3" / "r0a_evidence_gate.v0.1.json"
VALIDATOR = ROOT / "scripts" / "validate_ymq3_r0a.py"

EXPECTED_CASES = [
    ("C1_DOTCOM", "1999-01-01", "2002-12-31", "NARRATIVE_HEAVY"),
    ("C2_GFC", "2008-01-01", "2009-12-31", "ACUTE_SHOCK_HARD_NEGATIVE"),
    ("C3_CHINA_LEVERAGE", "2014-07-01", "2016-02-29", "NARRATIVE_HEAVY"),
    ("C4_COVID", "2020-01-01", "2020-12-31", "ACUTE_SHOCK_HARD_NEGATIVE"),
    ("C5_INFLATION", "2021-01-01", "2022-10-31", "MIXED_REALITY_NARRATIVE"),
    ("C6_AI", "2022-11-01", "2026-08-31", "NARRATIVE_HEAVY"),
]
EXPECTED_DOMAINS = [
    "MARKET",
    "MACRO_VINTAGE",
    "OFFICIAL_ANCHOR",
    "NARRATIVE_CORPUS",
    "LICENSE_RIGHTS",
    "PIT_PROVENANCE",
]
EXPECTED_SOURCE_VERDICTS = ["ADMIT", "ANNOTATION_ONLY", "UNKNOWN_DENY", "REJECT"]
EXPECTED_TIMESTAMP_CLASSES = [
    "TS1_SOURCE_NATIVE",
    "TS2_ARCHIVE_VERIFIED",
    "TS3_PROVIDER_INDEXED",
    "TS4_INFERRED_RETROSPECTIVE",
]
EXPECTED_RIGHT_VALUES = ["ALLOW", "DENY", "UNKNOWN"]
EXPECTED_CASE_VERDICTS = ["READY", "READY_WITH_LIMITATIONS", "BLOCKED", "INDETERMINATE"]
EXPECTED_PROGRAM_VERDICTS = [
    "FULL6_READY",
    "OPEN4_READY",
    "INSUFFICIENT_EVIDENCE_INDETERMINATE",
    "PHYSICAL_FAIL",
]


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


class EvidenceGateContractTest(unittest.TestCase):
    def test_machine_artifacts_exist(self):
        self.assertTrue(CONFIG.exists(), "Evidence gate config must exist before any source acquisition")
        self.assertTrue(VALIDATOR.exists(), "R0A validator must exist")

    def test_exact_cases_are_frozen_and_non_overlapping(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        actual = [(c["case_id"], c["start_date"], c["end_date"], c["role"]) for c in cfg["cases"]]
        self.assertEqual(actual, EXPECTED_CASES)
        for left, right in zip(cfg["cases"], cfg["cases"][1:]):
            self.assertLess(left["end_date"], right["start_date"])

    def test_evidence_domains_and_verdict_vocabularies_are_exact(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        self.assertEqual(cfg["mandatory_evidence_domains"], EXPECTED_DOMAINS)
        self.assertEqual(cfg["source_registry_verdicts"], EXPECTED_SOURCE_VERDICTS)
        self.assertEqual(cfg["timestamp_authority_classes"], EXPECTED_TIMESTAMP_CLASSES)
        self.assertEqual(cfg["rights_values"], EXPECTED_RIGHT_VALUES)
        self.assertEqual(cfg["case_verdicts"], EXPECTED_CASE_VERDICTS)
        self.assertEqual(cfg["program_verdicts"], EXPECTED_PROGRAM_VERDICTS)

    def test_rights_axes_are_separate_and_unknown_denies(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        self.assertEqual(
            cfg["rights_axes"],
            [
                "processing_authority",
                "raw_storage_authority",
                "derived_feature_storage_authority",
                "redistribution_authority",
            ],
        )
        self.assertEqual(cfg["unknown_rights_semantics"], "DENY")
        self.assertFalse(cfg["public_readability_implies_storage_rights"])

    def test_story_timestamp_and_revised_macro_rules_fail_closed(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        self.assertEqual(cfg["story_time_rule"], "publication_available_at <= canonical_week_end")
        self.assertEqual(cfg["retrospective_timestamp_class"], "TS4_INFERRED_RETROSPECTIVE")
        self.assertFalse(cfg["retrospective_allowed_as_story_feature"])
        self.assertFalse(cfg["current_revised_macro_can_substitute_historical_vintage"])

    def test_readiness_thresholds_are_frozen(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        t = cfg["readiness_thresholds"]
        self.assertEqual(t["pit_violation_count"], 0)
        self.assertEqual(t["unknown_processing_rights_count"], 0)
        self.assertEqual(t["unauthorized_raw_storage_count"], 0)
        self.assertEqual(t["timestamp_authority_rate_min"], 0.95)
        self.assertEqual(t["scored_week_presence_rate_min"], 0.80)
        self.assertEqual(t["median_eligible_documents_per_covered_week_min"], 10)
        self.assertEqual(t["multi_publisher_week_rate_min"], 0.70)
        self.assertEqual(t["distinct_publisher_groups_per_multi_publisher_week_min"], 2)
        self.assertTrue(t["narrative_heavy_requires_media_family"])

    def test_multimodal_minimum_and_non_authorizations_are_frozen(self):
        self.assertTrue(CONFIG.exists(), "missing evidence gate config")
        cfg = load_config()
        self.assertEqual(cfg["multimodal_minimum"]["ready_cases_min"], 4)
        self.assertEqual(cfg["multimodal_minimum"]["narrative_heavy_ready_min"], 2)
        self.assertEqual(cfg["multimodal_minimum"]["acute_shock_hard_negative_ready_min"], 1)
        self.assertEqual(
            cfg["non_authorizations"],
            [
                "SCIENTIFIC_PASS",
                "YMQ3_R1_FORWARD_SHADOW",
                "CAPITAL_ADMISSION",
                "PORTFOLIO_WEIGHTING",
                "POSITION_SIZING",
                "VEIGHNA_OR_BROKER_EXECUTION",
                "REAL_CAPITAL_MOVEMENT",
            ],
        )


if __name__ == "__main__":
    unittest.main()
