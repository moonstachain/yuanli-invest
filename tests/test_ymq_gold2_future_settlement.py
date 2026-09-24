import copy
import unittest

from scripts import ymq_gold2_future_settlement as settlement


def synthetic_bundle():
    """Engineering fixture only; never a real preregistration or market record."""
    claim = {
        "schema_version": "gold-future-settlement.v1",
        "claim_id": "SYNTHETIC-GOLD-FIXTURE",
        "capability_version": "offline-fixture-v1",
        "target": "GOLD", "series_id": "SYNTHETIC_GOLD_USD_OZ",
        "unit": "USD_PER_TROY_OUNCE", "currency": "USD",
        "data_mode": "SYNTHETIC_ENGINEERING_ONLY",
        "t0": "2026-09-01T16:00:00Z", "horizon_end": "2026-09-08T16:00:00Z",
        "evidence_known_as_of": "2026-09-01T15:00:00Z",
        "model_direction": 1, "baseline_direction": 0,
        "baseline_id": "FROZEN_NO_CHANGE", "neutral_band_pct": 0.1,
    }
    registration = {
        "claim_sha256": settlement.canonical_hash(claim),
        "recorded_at": "2026-09-01T15:30:00Z",
        "registry_id": "SYNTHETIC_TEST_REGISTRY", "record_id": "SYNTHETIC_TEST_RECORD",
        "data_mode": claim["data_mode"], "verification": "EXTERNAL_READBACK_REQUIRED",
        "registry_kind": "SYNTHETIC_FIXTURE",
    }
    observations = []
    for day, value in (("01", 100.0), ("08", 102.0)):
        observations.append({
            **{k: claim[k] for k in settlement.IDENTITY_FIELDS},
            "data_mode": claim["data_mode"], "observation_id": "SYNTHETIC-" + day,
            "source_ref": "SYNTHETIC_ENGINEERING_FIXTURE", "raw_sha256": day * 32,
            "source_kind": "SYNTHETIC_FIXTURE",
            "observed_at": f"2026-09-{day}T16:00:00Z",
            "available_at": f"2026-09-{day}T16:05:00Z",
            "captured_at": f"2026-09-{day}T16:10:00Z",
            "vintage_kind": "FIRST_RELEASE", "value": value,
        })
    return {"claim": claim, "preregistration": registration, "observations": observations, "as_of": "2026-09-08T17:00:00Z"}


class GoldFutureSettlementTests(unittest.TestCase):
    def test_scores_baseline_and_model_separately_and_denies_authority(self):
        result = settlement.settle(synthetic_bundle())
        self.assertEqual(result["status"], "SETTLED_RESEARCH_CANDIDATE")
        self.assertAlmostEqual(result["outcome_return_pct"], 2.0)
        self.assertTrue(result["model_score"]["correct"])
        self.assertFalse(result["baseline_score"]["correct"])
        self.assertFalse(any(result["authority"].values()))
        self.assertFalse(result["investment_effectiveness_proven"])

    def test_not_due_cannot_score_even_with_injected_future_outcome(self):
        payload = synthetic_bundle()
        payload["as_of"] = "2026-09-07T23:00:00Z"
        result = settlement.settle(payload)
        self.assertEqual(result["status"], "NOT_DUE")
        self.assertIsNone(result["model_score"])

    def test_late_registration_and_post_t0_evidence_fail_closed(self):
        for target, field in (("preregistration", "recorded_at"), ("claim", "evidence_known_as_of")):
            with self.subTest(field=field):
                payload = synthetic_bundle()
                payload[target][field] = "2026-09-01T17:00:00Z"
                payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
                with self.assertRaises(ValueError):
                    settlement.settle(payload)

    def test_evidence_must_exist_when_claim_is_registered(self):
        payload = synthetic_bundle()
        payload["claim"]["evidence_known_as_of"] = "2026-09-01T15:45:00Z"
        payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
        with self.assertRaisesRegex(ValueError, "after preregistration"):
            settlement.settle(payload)

    def test_editing_direction_horizon_or_series_breaks_frozen_hash(self):
        for field, value in (("model_direction", -1), ("horizon_end", "2026-09-09T16:00:00Z"), ("series_id", "OTHER_SERIES")):
            with self.subTest(field=field):
                payload = synthetic_bundle()
                payload["claim"][field] = value
                with self.assertRaisesRegex(ValueError, "preregistration hash"):
                    settlement.settle(payload)

    def test_each_endpoint_requires_exact_measurement_identity(self):
        for field, value in (("series_id", "DIFFERENT_GOLD_FIX"), ("unit", "CNY_PER_GRAM"), ("currency", "CNY"), ("target", "SILVER"), ("observed_at", "2026-09-08T15:59:59Z")):
            with self.subTest(field=field):
                payload = synthetic_bundle()
                payload["observations"][1][field] = value
                result = settlement.settle(payload)
                self.assertEqual(result["status"], "INDETERMINATE_EVIDENCE")
                self.assertEqual(result["endpoint_status"]["horizon_end"], "MISSING_EXACT_OBSERVATION")

    def test_release_and_capture_clocks_both_limit_replay(self):
        for clock in ("available_at", "captured_at"):
            with self.subTest(clock=clock):
                payload = synthetic_bundle()
                row = payload["observations"][1]
                row[clock] = "2026-09-09T00:00:00Z"
                if clock == "available_at":
                    row["captured_at"] = "2026-09-09T00:01:00Z"
                result = settlement.settle(payload)
                self.assertEqual(result["endpoint_status"]["horizon_end"], "NOT_YET_AVAILABLE_OR_CAPTURED")

    def test_revision_alone_cannot_replace_original(self):
        payload = synthetic_bundle()
        payload["observations"][1]["vintage_kind"] = "REVISION"
        result = settlement.settle(payload)
        self.assertEqual(result["status"], "INDETERMINATE_EVIDENCE")
        self.assertEqual(result["endpoint_status"]["horizon_end"], "REVISION_WITHOUT_FIRST_RELEASE")

    def test_added_revision_cannot_rewrite_original_outcome(self):
        payload = synthetic_bundle()
        original = settlement.settle(payload)
        revision = copy.deepcopy(payload["observations"][1])
        revision.update({"value": 50.0, "vintage_kind": "REVISION", "observation_id": "REVISION"})
        payload["observations"].append(revision)
        result = settlement.settle(payload)
        self.assertEqual(result["model_score"], original["model_score"])
        self.assertEqual(result["selected_observation_sha256"], original["selected_observation_sha256"])

    def test_conflicting_initial_releases_are_not_silently_selected(self):
        payload = synthetic_bundle()
        conflict = copy.deepcopy(payload["observations"][1])
        conflict["value"] = 50.0
        payload["observations"].append(conflict)
        with self.assertRaisesRegex(ValueError, "conflicting"):
            settlement.settle(payload)

    def test_invalid_price_and_clock_are_rejected(self):
        for value in (float("nan"), float("inf"), True, 0, -1):
            with self.subTest(value=value):
                payload = synthetic_bundle()
                payload["observations"][1]["value"] = value
                with self.assertRaises(ValueError):
                    settlement.settle(payload)
        payload = synthetic_bundle()
        payload["observations"][1]["available_at"] = "2026-09-07T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "clocks"):
            settlement.settle(payload)

    def test_missing_preregistration_never_creates_one(self):
        payload = synthetic_bundle()
        del payload["preregistration"]
        with self.assertRaisesRegex(ValueError, "preregistration"):
            settlement.settle(payload)

    def test_naive_timestamp_and_mixed_reality_modes_are_rejected(self):
        payload = synthetic_bundle()
        payload["as_of"] = "2026-09-08T17:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            settlement.settle(payload)
        payload = synthetic_bundle()
        payload["observations"][1]["data_mode"] = "REAL_OBSERVATIONS"
        with self.assertRaisesRegex(ValueError, "data mode"):
            settlement.settle(payload)

    def test_neutral_band_and_deterministic_rerun(self):
        payload = synthetic_bundle()
        payload["observations"][1]["value"] = 100.0
        first = settlement.settle(payload)
        self.assertEqual(first, settlement.settle(copy.deepcopy(payload)))
        self.assertEqual(first["realized_direction"], 0)
        self.assertTrue(first["baseline_score"]["correct"])

    def test_timezone_equivalent_endpoint_matches(self):
        payload = synthetic_bundle()
        payload["observations"][1]["observed_at"] = "2026-09-09T00:00:00+08:00"
        self.assertEqual(settlement.settle(payload)["status"], "SETTLED_RESEARCH_CANDIDATE")

    def test_exact_neutral_boundaries_and_both_sides(self):
        for value, direction in ((99.7, 0), (100.3, 0), (99.699999, -1), (99.700001, 0), (100.299999, 0), (100.300001, 1)):
            with self.subTest(value=value):
                payload = synthetic_bundle()
                payload["claim"]["neutral_band_pct"] = 0.3
                payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
                payload["observations"][1]["value"] = value
                self.assertEqual(settlement.settle(payload)["realized_direction"], direction)

    def test_real_mode_cannot_relabel_declared_synthetic_provenance(self):
        for synthetic_kind in ("registry", "source"):
            with self.subTest(synthetic_kind=synthetic_kind):
                payload = synthetic_bundle()
                for item in (payload["claim"], payload["preregistration"], *payload["observations"]):
                    item["data_mode"] = "REAL_OBSERVATIONS"
                if synthetic_kind == "source":
                    payload["preregistration"]["registry_kind"] = "EXTERNAL_RECORD"
                    payload["preregistration"]["registry_id"] = "EXTERNAL_TEST_REGISTRY"
                    payload["preregistration"]["record_id"] = "EXTERNAL_TEST_RECORD"
                payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
                with self.assertRaisesRegex(ValueError, "contradicts declared synthetic"):
                    settlement.settle(payload)

    def test_external_declarations_are_not_treated_as_authentication(self):
        payload = synthetic_bundle()
        for item in (payload["claim"], payload["preregistration"], *payload["observations"]):
            item["data_mode"] = "REAL_OBSERVATIONS"
        payload["preregistration"]["registry_kind"] = "EXTERNAL_RECORD"
        payload["preregistration"]["registry_id"] = "EXTERNAL_TEST_REGISTRY"
        payload["preregistration"]["record_id"] = "EXTERNAL_TEST_RECORD"
        for row in payload["observations"]:
            row["source_kind"] = "EXTERNAL_RECORD"
            row["source_ref"] = "UNVERIFIED_EXTERNAL_TEST_REFERENCE"
            row["observation_id"] = "UNVERIFIED_" + row["observation_id"]
        payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
        result = settlement.settle(payload)
        self.assertEqual(result["source_authenticity"], "UNVERIFIED")
        self.assertEqual(result["observation_verification"], "EXTERNAL_READBACK_REQUIRED")
        self.assertFalse(result["investment_effectiveness_proven"])

    def test_changing_kind_does_not_override_explicit_fixture_reference(self):
        payload = synthetic_bundle()
        for item in (payload["claim"], payload["preregistration"], *payload["observations"]):
            item["data_mode"] = "REAL_OBSERVATIONS"
        payload["preregistration"]["registry_kind"] = "EXTERNAL_RECORD"
        payload["preregistration"]["claim_sha256"] = settlement.canonical_hash(payload["claim"])
        with self.assertRaisesRegex(ValueError, "explicit SYNTHETIC"):
            settlement.settle(payload)


if __name__ == "__main__":
    unittest.main()
