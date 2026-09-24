import copy
from datetime import datetime, timezone
import hashlib
import json
import unittest

from yuanli_invest.context import compile_context
from yuanli_invest.first_capture import settle_daily_first_capture
from yuanli_invest.gold import classify_property_drift, classify_valuation
from yuanli_invest.receipts import canonical_hash, read_envelope, receipt_envelope


def daily_bundle():
    """Synthetic engineering records; no database, provider, repository or keys."""
    source = {"source_id": "synthetic_gold", "series_id": "S0031645", "target": "GOLD", "unit": "USD/OZ", "currency": "USD", "source_timezone": "Europe/London"}
    claim = {
        "schema_version": "gold-first-capture-claim.v1", "method": "daily_first_capture_v1",
        "claim_id": "synthetic-claim", "capability_version": "direction-v1", **source,
        "start_trade_date": "2026-09-02", "end_trade_date": "2026-09-09",
        "evidence_known_as_of": "2026-09-01T12:00:00Z", "model_direction": 1,
        "baseline_id": "FROZEN_NO_CHANGE", "baseline_direction": 0, "neutral_band_pct": "0.3",
        "data_mode": "SYNTHETIC_ENGINEERING_ONLY",
    }
    # Deliberately preserve unsorted browser-style JSON bytes.
    text = json.dumps(claim, ensure_ascii=False)
    registration = {"registered_at": "2026-09-01T13:00:00Z", "claim_json": text, "claim_sha256": hashlib.sha256(text.encode()).hexdigest()}
    captures = [
        {"capture_id": f"capture-{day}", "source_id": source["source_id"], "source_timezone": source["source_timezone"], "trade_date": f"2026-09-{day}", "value_decimal": value, "payload_sha256": day * 32, "first_captured_at": f"2026-09-{day}T16:10:00Z"}
        for day, value in (("02", "100"), ("09", "102"))
    ]
    return {"claim": claim, "registration": registration, "trusted_source": source, "observations": captures, "as_of": "2026-09-10T18:00:00Z"}


def refreeze(bundle):
    encoded = receipt_envelope(bundle["claim"])
    bundle["registration"].update(claim_json=encoded["receipt_json"], claim_sha256=encoded["receipt_sha256"])


class DailyFirstCaptureTests(unittest.TestCase):
    def test_exact_dates_decimal_outcome_and_frozen_baseline(self):
        result = settle_daily_first_capture(daily_bundle())
        self.assertEqual(result["status"], "SETTLED_RESEARCH")
        self.assertEqual(result["outcome_return_pct_decimal"], "2")
        self.assertTrue(result["model_score"]["correct"])
        self.assertEqual(result["baseline_score"]["direction"], 0)
        self.assertFalse(result["baseline_score"]["correct"])
        self.assertNotIn("authority", result)
        self.assertNotIn("accepted_learning", result)

    def test_claim_original_bytes_are_verified_without_reserializing(self):
        bundle = daily_bundle()
        self.assertNotEqual(canonical_hash(bundle["claim"]), bundle["registration"]["claim_sha256"])
        self.assertEqual(settle_daily_first_capture(bundle)["status"], "SETTLED_RESEARCH")

    def test_claim_edit_or_bad_hash_cannot_change_registered_direction(self):
        for field in ("model_direction", "neutral_band_pct", "end_trade_date"):
            with self.subTest(field=field):
                bundle = daily_bundle()
                bundle["claim"][field] = {"model_direction": -1, "neutral_band_pct": "0.4", "end_trade_date": "2026-09-10"}[field]
                with self.assertRaisesRegex(ValueError, "immutable"):
                    settle_daily_first_capture(bundle)
        bundle = daily_bundle(); bundle["registration"]["claim_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "sha256"):
            settle_daily_first_capture(bundle)

    def test_frozen_no_change_baseline_is_mandatory(self):
        for value in (1, -1, False, "0"):
            bundle = daily_bundle(); bundle["claim"]["baseline_direction"] = value; refreeze(bundle)
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "baseline"):
                settle_daily_first_capture(bundle)

    def test_registration_local_day_must_precede_start(self):
        bundle = daily_bundle(); bundle["registration"]["registered_at"] = "2026-09-02T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "registration day"):
            settle_daily_first_capture(bundle)
        for row in (bundle["claim"], bundle["trusted_source"], *bundle["observations"]):
            row["source_timezone"] = "America/Los_Angeles"
        refreeze(bundle)
        self.assertEqual(settle_daily_first_capture(bundle)["status"], "SETTLED_RESEARCH")

    def test_registration_requires_evidence_already_known(self):
        bundle = daily_bundle(); bundle["claim"]["evidence_known_as_of"] = "2026-09-01T14:00:00Z"; refreeze(bundle)
        with self.assertRaisesRegex(ValueError, "after registration"):
            settle_daily_first_capture(bundle)

    def test_source_registry_identity_cannot_be_substituted(self):
        for field in ("source_id", "source_timezone", "series_id", "unit", "currency", "target"):
            bundle = daily_bundle(); bundle["trusted_source"][field] = "OTHER"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "trusted source"):
                settle_daily_first_capture(bundle)

    def test_later_revision_does_not_replace_first_capture(self):
        bundle = daily_bundle()
        revision = dict(bundle["observations"][1], capture_id="revision", value_decimal="50", first_captured_at="2026-09-09T17:00:00Z", payload_sha256="f" * 64)
        bundle["observations"].insert(0, revision)
        result = settle_daily_first_capture(bundle)
        self.assertEqual(result["selected_capture_ids"]["end"], "capture-09")
        self.assertEqual(result["realized_direction"], 1)

    def test_nearby_trade_dates_are_not_substituted(self):
        bundle = daily_bundle(); bundle["observations"][1]["trade_date"] = "2026-09-08"
        result = settle_daily_first_capture(bundle)
        self.assertEqual(result["status"], "INDETERMINATE_EVIDENCE")
        self.assertIsNone(result["model_score"])
        self.assertEqual(result["endpoint_status"]["end"], "MISSING_EXACT_TRADE_DATE")

    def test_precise_neutral_boundaries_and_both_sides(self):
        for value, expected in (("99.7", 0), ("100.3", 0), ("99.699999999999999999", -1), ("100.300000000000000001", 1)):
            bundle = daily_bundle(); bundle["observations"][1]["value_decimal"] = value
            with self.subTest(value=value):
                self.assertEqual(settle_daily_first_capture(bundle)["realized_direction"], expected)

    def test_not_due_or_not_captured_is_never_scored(self):
        bundle = daily_bundle(); bundle["as_of"] = "2026-09-08T12:00:00Z"
        self.assertEqual(settle_daily_first_capture(bundle)["status"], "NOT_DUE")
        bundle["as_of"] = "2026-09-09T16:00:00Z"
        self.assertEqual(settle_daily_first_capture(bundle)["status"], "NOT_DUE")
        bundle["as_of"] = "2026-09-10T18:00:00Z"
        bundle["observations"][1]["first_captured_at"] = "2026-09-11T18:00:00Z"
        result = settle_daily_first_capture(bundle)
        self.assertEqual(result["status"], "INDETERMINATE_EVIDENCE")
        self.assertEqual(result["endpoint_status"]["end"], "NOT_YET_CAPTURED")

    def test_invalid_price_or_conflicting_first_capture_is_error(self):
        for value in ("NaN", "Infinity", "-1", "0", True, 102.0):
            bundle = daily_bundle(); bundle["observations"][1]["value_decimal"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                settle_daily_first_capture(bundle)
        bundle = daily_bundle(); bundle["observations"].append(dict(bundle["observations"][1], capture_id="conflict", value_decimal="99"))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            settle_daily_first_capture(bundle)

    def test_naive_time_is_rejected_at_each_clock(self):
        for target, field in (("registration", "registered_at"), ("claim", "evidence_known_as_of")):
            bundle = daily_bundle(); bundle[target][field] = "2026-09-01T12:00:00"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "timezone"):
                settle_daily_first_capture(bundle)
        bundle = daily_bundle(); bundle["as_of"] = "2026-09-09T18:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            settle_daily_first_capture(bundle)

    def test_input_order_and_rerun_are_deterministic(self):
        original = daily_bundle(); reversed_rows = copy.deepcopy(original); reversed_rows["observations"].reverse()
        self.assertEqual(settle_daily_first_capture(original), settle_daily_first_capture(reversed_rows))


class CoreContractTests(unittest.TestCase):
    def test_receipt_envelope_binds_unicode_exact_bytes(self):
        receipt = {"state": "未知\n等待", "price": "100.300000000000000001"}
        envelope = receipt_envelope(receipt)
        self.assertEqual(hashlib.sha256(envelope["receipt_json"].encode()).hexdigest(), envelope["receipt_sha256"])
        self.assertEqual(read_envelope(envelope), receipt)
        envelope["receipt_json"] += " "
        with self.assertRaises(ValueError):
            read_envelope(envelope)

    def test_nonfinite_numbers_cannot_be_receipted(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                receipt_envelope({"value": value})

    def test_context_requires_timezone_and_normalizes_as_of_to_utc(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            compile_context(as_of=datetime(2026, 9, 1), evidence_rows=[])
        row = {"evidence_ref": "e1", "known_as_of": "2026-09-01T00:00:00", "status": "PASS", "authority": "RESEARCH"}
        with self.assertRaisesRegex(ValueError, "timezone"):
            compile_context(as_of=datetime(2026, 9, 2, tzinfo=timezone.utc), evidence_rows=[row])
        context = compile_context(as_of=datetime.fromisoformat("2026-09-01T08:00:00+08:00"), evidence_rows=[])
        self.assertEqual(context.as_of.isoformat(), "2026-09-01T00:00:00+00:00")

    def test_gold_labels_do_not_need_repository_config(self):
        self.assertEqual(classify_valuation({"MACRO_FAIR_VALUE_LENS": "FAIR", "MONETARY_REGIME_PREMIUM_LENS": "FAIR", "REFLEXIVITY_POSITIONING_LENS": "FAIR"}), "FAIR")
        with self.assertRaises(ValueError):
            classify_property_drift(coefficient_distance=float("nan"), dominant_factor_match_share=0.5, residual_bias_ratio=0.1, independent_evidence_count=3)
