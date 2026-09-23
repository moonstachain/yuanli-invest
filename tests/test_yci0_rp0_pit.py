import unittest

from runtime.yci0_rp0.contracts import EvidenceStatus, PITAdmissionReason, SourceType
from runtime.yci0_rp0.evidence_adapter import normalize_observation, pit_eligible


BASE_SPEC = {
    "metric_id": "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY",
    "family": "HYPERSCALER_CAPEX",
    "source_type": "FIRST_PARTY_FILING_OR_STRUCTURED_SENSOR",
    "pit_policy": "REQUIRE_RELEASE_VINTAGE_AND_KNOWN_AS_OF",
    "required_timestamps": [
        "observed_at", "released_at", "known_as_of", "retrieved_at", "revised_at"
    ],
    "admission_rule": "PIT-qualified only with release, vintage, known_as_of and provenance.",
    "fallback": "UNKNOWN",
}

BASE_RAW = {
    "entity_id": "MSFT",
    "metric_name": "quarterly_capex",
    "value": 30.0,
    "unit": "USD_BN",
    "period": "2026Q2",
    "source_name": "Microsoft 10-Q",
    "source_locator": "https://example.test/msft/2026q2-10q",
    "observed_at": "2026-06-30T00:00:00Z",
    "released_at": "2026-07-29T20:05:00Z",
    "known_as_of": "2026-07-29T20:05:00Z",
    "retrieved_at": "2026-09-16T12:00:00Z",
    "revised_at": None,
    "vintage": "2026-07-29",
    "receipt_id": "rcpt-msft-q2",
    "authority": "RESEARCH",
}


class YCI0RP0PITTests(unittest.TestCase):
    def test_valid_first_party_row_is_pit_eligible(self):
        evidence = normalize_observation(BASE_RAW, BASE_SPEC)
        self.assertEqual(evidence.evidence_status, EvidenceStatus.PASS)
        self.assertEqual(evidence.pit_admission_reason, PITAdmissionReason.PIT_QUALIFIED)
        self.assertTrue(pit_eligible(evidence))

    def test_missing_known_as_of_is_never_pit_qualified(self):
        raw = dict(BASE_RAW)
        raw.pop("known_as_of")
        evidence = normalize_observation(raw, BASE_SPEC)
        self.assertEqual(evidence.evidence_status, EvidenceStatus.UNKNOWN)
        self.assertEqual(evidence.pit_admission_reason, PITAdmissionReason.MISSING_KNOWN_AS_OF)
        self.assertFalse(pit_eligible(evidence))

    def test_alice_authored_output_defaults_to_candidate_not_pass(self):
        raw = dict(BASE_RAW)
        raw["source_type"] = "WIND_ALICE_AUTHORED"
        raw["source_name"] = "Wind Alice"
        evidence = normalize_observation(raw, BASE_SPEC)
        self.assertEqual(evidence.source_type, SourceType.AUTHORED_KNOWLEDGE_CANDIDATE)
        self.assertEqual(evidence.evidence_status, EvidenceStatus.CURRENT_CONTEXT_ONLY)
        self.assertEqual(evidence.pit_admission_reason, PITAdmissionReason.AUTHORED_SOURCE_NOT_EVIDENCE)
        self.assertFalse(pit_eligible(evidence))

    def test_missing_release_or_vintage_semantics_is_current_context_only(self):
        raw = dict(BASE_RAW)
        raw["released_at"] = None
        raw["vintage"] = None
        evidence = normalize_observation(raw, BASE_SPEC)
        self.assertEqual(evidence.evidence_status, EvidenceStatus.CURRENT_CONTEXT_ONLY)
        self.assertEqual(evidence.pit_admission_reason, PITAdmissionReason.MISSING_RELEASE_OR_VINTAGE)
        self.assertFalse(pit_eligible(evidence))

    def test_content_hash_and_fallback_source_locator_are_deterministic(self):
        raw = dict(BASE_RAW)
        raw.pop("source_locator")
        first = normalize_observation(raw, BASE_SPEC)
        second = normalize_observation(dict(raw), dict(BASE_SPEC))
        self.assertEqual(first.source_locator, second.source_locator)
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertTrue(first.source_locator.startswith("source://"))
        self.assertEqual(len(first.content_hash), 64)

    def test_authority_escalation_fails_closed(self):
        raw = dict(BASE_RAW)
        raw["authority"] = "CAPITAL"
        evidence = normalize_observation(raw, BASE_SPEC)
        self.assertEqual(evidence.evidence_status, EvidenceStatus.BLOCKED)
        self.assertEqual(evidence.pit_admission_reason, PITAdmissionReason.AUTHORITY_VIOLATION)
        self.assertFalse(pit_eligible(evidence))


if __name__ == "__main__":
    unittest.main()
