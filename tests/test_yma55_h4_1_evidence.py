import unittest

from research_runtime.yma55.evidence import admit_evidence, assess_hydration


class H41EvidenceAdmissionTests(unittest.TestCase):
    def source(self, **overrides):
        base = {
            "source_id": "S1",
            "title": "source",
            "publisher": "Federal Reserve",
            "canonical_url": "https://example.invalid/source",
            "document_date": "1994-01-01",
            "published_at": "1994-01-01T12:00:00Z",
            "retrieved_at": "2026-08-24T00:00:00Z",
            "evidence_tier": "E0",
            "producer_class": "central_bank",
            "originating_source_id": "S1",
            "public_at_t0": True,
            "admissible_at_cutoff": True,
            "provenance_note": "test fixture",
            "claims": [],
            "signals": [],
        }
        base.update(overrides)
        return base

    def test_post_cutoff_primary_is_rejected(self):
        source = self.source(published_at="1994-02-04T00:00:00Z")
        admitted, rejected = admit_evidence([source], "1994-01-01T23:59:59Z")
        self.assertEqual(admitted, [])
        self.assertEqual(rejected[0]["reason"], "POST_CUTOFF")

    def test_not_public_at_t0_is_rejected(self):
        source = self.source(public_at_t0=False)
        admitted, rejected = admit_evidence([source], "1994-01-01T23:59:59Z")
        self.assertEqual(admitted, [])
        self.assertEqual(rejected[0]["reason"], "NOT_PUBLIC_AT_T0")

    def test_e3_and_e4_are_excluded_from_resolver(self):
        sources = [self.source(source_id="E3", evidence_tier="E3"), self.source(source_id="E4", evidence_tier="E4")]
        admitted, rejected = admit_evidence(sources, "1994-01-01T23:59:59Z")
        self.assertEqual(admitted, [])
        self.assertEqual({r["reason"] for r in rejected}, {"RETROSPECTIVE_TIER"})

    def test_true_e0_plus_independent_e1_can_fully_hydrate(self):
        e0 = self.source(source_id="E0", originating_source_id="E0", producer_class="central_bank", evidence_tier="E0")
        e1 = self.source(source_id="E1", originating_source_id="E1", producer_class="energy_agency", evidence_tier="E1")
        result = assess_hydration([e0, e1])
        self.assertEqual(result["status"], "EVIDENCE_HYDRATED")
        self.assertTrue(result["independent_e1"])

    def test_fake_e1_independence_does_not_fully_hydrate(self):
        e0 = self.source(source_id="E0", originating_source_id="ORIGIN", producer_class="central_bank", evidence_tier="E0")
        e1 = self.source(source_id="E1", originating_source_id="ORIGIN", producer_class="news_republication", evidence_tier="E1")
        result = assess_hydration([e0, e1])
        self.assertNotEqual(result["status"], "EVIDENCE_HYDRATED")
        self.assertFalse(result["independent_e1"])


if __name__ == "__main__":
    unittest.main()
