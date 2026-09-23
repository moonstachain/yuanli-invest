import unittest

from runtime.yci0_rp0.contracts import (
    EvidenceStatus,
    PITAdmissionReason,
    RealityEvidence,
    SourceType,
)
from runtime.yci0_rp0.state_compiler import RealityState, compile_reality_state


def ev(eid, metric_id, value, known_as_of, status=EvidenceStatus.PASS):
    reason = (
        PITAdmissionReason.PIT_QUALIFIED
        if status is EvidenceStatus.PASS
        else PITAdmissionReason.MISSING_KNOWN_AS_OF
    )
    return RealityEvidence(
        evidence_id=eid,
        metric_id=metric_id,
        entity_id="TEST",
        metric_name=metric_id,
        value=value,
        unit="index",
        period=known_as_of[:10],
        source_type=SourceType.STRUCTURED_SENSOR,
        source_name="TEST_SENSOR",
        source_locator=f"test://{eid}",
        observed_at=known_as_of,
        released_at=known_as_of,
        known_as_of=known_as_of,
        retrieved_at=known_as_of,
        revised_at=None,
        vintage="v1",
        evidence_status=status,
        pit_admission_reason=reason,
        receipt_id=f"r-{eid}",
        content_hash=f"h-{eid}",
        authority="RESEARCH",
    )


class RealityStateCompilerTests(unittest.TestCase):
    def test_three_period_series_produces_level_delta_delta2_and_accelerating(self):
        evidence = [
            ev("e1", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 100, "2026-06-01T00:00:00Z"),
            ev("e2", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 112, "2026-07-01T00:00:00Z"),
            ev("e3", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 130, "2026-08-01T00:00:00Z"),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        d = card.dimensions["hyperscaler_capex"]
        self.assertEqual(d.level, 130)
        self.assertEqual(d.delta, 18)
        self.assertEqual(d.delta2, 6)
        self.assertEqual(d.state, RealityState.ACCELERATING)
        self.assertEqual(d.evidence_refs, ("e1", "e2", "e3"))
        self.assertEqual(d.known_as_of, "2026-08-01T00:00:00Z")

    def test_less_than_three_points_keeps_delta_and_delta2_unknown(self):
        evidence = [
            ev("e1", "AIINFRA.NETWORKING.REVENUE_BACKLOG", 10, "2026-07-01T00:00:00Z"),
            ev("e2", "AIINFRA.NETWORKING.REVENUE_BACKLOG", 12, "2026-08-01T00:00:00Z"),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        d = card.dimensions["networking"]
        self.assertEqual(d.level, 12)
        self.assertEqual(d.delta, "UNKNOWN")
        self.assertEqual(d.delta2, "UNKNOWN")
        self.assertEqual(d.state, RealityState.UNKNOWN)

    def test_blocked_or_unknown_evidence_forces_dimension_unknown(self):
        evidence = [
            ev("e1", "AIINFRA.POWER.AVAILABILITY", 100, "2026-06-01T00:00:00Z"),
            ev("e2", "AIINFRA.POWER.AVAILABILITY", 110, "2026-07-01T00:00:00Z"),
            ev("e3", "AIINFRA.POWER.AVAILABILITY", 125, "2026-08-01T00:00:00Z"),
            ev("e4", "AIINFRA.POWER.EQUIPMENT_ORDERS_BACKLOG", None, "2026-08-01T00:00:00Z", EvidenceStatus.BLOCKED),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        d = card.dimensions["power_grid"]
        self.assertEqual(d.state, RealityState.UNKNOWN)
        self.assertEqual(d.delta, "UNKNOWN")
        self.assertEqual(d.delta2, "UNKNOWN")
        self.assertIn("e4", d.evidence_refs)

    def test_every_non_unknown_dimension_retains_lineage(self):
        evidence = [
            ev("e1", "AIINFRA.RATES.US10Y_NOMINAL", 4.5, "2026-06-01T00:00:00Z"),
            ev("e2", "AIINFRA.RATES.US10Y_NOMINAL", 4.3, "2026-07-01T00:00:00Z"),
            ev("e3", "AIINFRA.RATES.US10Y_NOMINAL", 4.0, "2026-08-01T00:00:00Z"),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        for d in card.dimensions.values():
            if d.state is not RealityState.UNKNOWN:
                self.assertTrue(d.evidence_refs)
                self.assertTrue(d.known_as_of)
                self.assertIn(d.confidence, {"LOW", "MEDIUM", "HIGH"})

    def test_multiple_metrics_in_one_dimension_are_not_cross_mixed(self):
        evidence = [
            ev("a1", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 100, "2026-06-01T00:00:00Z"),
            ev("a2", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 110, "2026-07-01T00:00:00Z"),
            ev("a3", "AIINFRA.CAPEX.HYPERSCALER_QUARTERLY", 125, "2026-08-01T00:00:00Z"),
            ev("g1", "AIINFRA.CAPEX.HYPERSCALER_GUIDANCE", 50, "2026-06-01T00:00:00Z"),
            ev("g2", "AIINFRA.CAPEX.HYPERSCALER_GUIDANCE", 45, "2026-07-01T00:00:00Z"),
            ev("g3", "AIINFRA.CAPEX.HYPERSCALER_GUIDANCE", 35, "2026-08-01T00:00:00Z"),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        d = card.dimensions["hyperscaler_capex"]
        self.assertEqual(d.state, RealityState.MIXED)
        self.assertEqual(d.delta["AIINFRA.CAPEX.HYPERSCALER_QUARTERLY"], 15)
        self.assertEqual(d.delta["AIINFRA.CAPEX.HYPERSCALER_GUIDANCE"], -10)
        self.assertEqual(d.delta2["AIINFRA.CAPEX.HYPERSCALER_QUARTERLY"], 5)
        self.assertEqual(d.delta2["AIINFRA.CAPEX.HYPERSCALER_GUIDANCE"], -5)

    def test_future_evidence_is_excluded_by_as_of(self):
        evidence = [
            ev("e1", "AIINFRA.COMPUTE.NVDA_DATA_CENTER_REVENUE", 10, "2026-06-01T00:00:00Z"),
            ev("e2", "AIINFRA.COMPUTE.NVDA_DATA_CENTER_REVENUE", 11, "2026-07-01T00:00:00Z"),
            ev("e3", "AIINFRA.COMPUTE.NVDA_DATA_CENTER_REVENUE", 13, "2026-08-01T00:00:00Z"),
            ev("future", "AIINFRA.COMPUTE.NVDA_DATA_CENTER_REVENUE", 99, "2026-09-01T00:00:00Z"),
        ]
        card = compile_reality_state(evidence, "2026-08-15T00:00:00Z")
        d = card.dimensions["compute"]
        self.assertEqual(d.level, 13)
        self.assertNotIn("future", d.evidence_refs)


if __name__ == "__main__":
    unittest.main()
