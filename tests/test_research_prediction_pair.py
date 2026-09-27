"""Synthetic transport regression; no provider calls or production source claims."""

import copy
from datetime import datetime, timezone
import unittest

from scripts import research_worker as worker
from tests.test_daily_first_capture import daily_bundle, refreeze
from yuanli_invest.first_capture import settle_daily_first_capture
from yuanli_invest.receipts import read_envelope, receipt_envelope


NOW = datetime(2026, 9, 12, 18, tzinfo=timezone.utc)


class PairRuntime:
    """Returns frozen due views and fresh acknowledgement views like Runtime."""

    def __init__(self):
        self.bundles, self.settlements, self.learning, self.calls = {}, {}, {}, []
        self.pair_id, self.context_sha256 = "synthetic-pair", "e" * 64
        for role, direction in (("human", 1), ("momentum", -1)):
            bundle = daily_bundle()
            bundle["claim"].update(claim_id=f"synthetic-{role}", model_direction=direction, neutral_band_pct="0.5")
            refreeze(bundle)
            self.bundles[role] = bundle
        self.fail_learning_once = None

    def pair_view(self, role):
        members = {key: {"claim_id": value["claim"]["claim_id"], "claim": value["claim"],
            "registration": value["registration"], "settlement": self.settlements.get(value["claim"]["claim_id"])}
            for key, value in self.bundles.items()}
        receipts = [read_envelope(member["settlement"]) if member["settlement"] else None for member in members.values()]
        effective = all(receipts) and receipts[0]["selected_capture_ids"] == receipts[1]["selected_capture_ids"] and receipts[0]["direction"] == receipts[1]["direction"]
        return copy.deepcopy({"pair_id": self.pair_id, "role": role,
            "human_claim_id": self.bundles["human"]["claim"]["claim_id"],
            "momentum_claim_id": self.bundles["momentum"]["claim"]["claim_id"],
            "context_sha256": self.context_sha256, **members,
            "effective": bool(effective), "blocked_reason": None if effective else "PAIR_NOT_BOTH_SETTLED"})

    def __call__(self, operation, payload):
        self.calls.append((operation, copy.deepcopy(payload)))
        if operation == "list_due_claims":
            return {"items": [copy.deepcopy({**bundle,
                "settlement": self.settlements.get(bundle["claim"]["claim_id"]),
                "prediction_pair": self.pair_view(role)}) for role, bundle in self.bundles.items()
                if bundle["claim"]["claim_id"] not in self.learning]}
        if operation == "record_settlement":
            claim_id = payload["claim_id"]
            self.settlements[claim_id] = copy.deepcopy(payload)
            role = next(role for role, bundle in self.bundles.items() if bundle["claim"]["claim_id"] == claim_id)
            return {"settlement": copy.deepcopy(payload), "prediction_pair": self.pair_view(role)}
        if operation == "record_learning":
            receipt = read_envelope(payload)
            if self.fail_learning_once == receipt["claim_id"]:
                self.fail_learning_once = None
                raise OSError("synthetic interrupted learning")
            self.learning[receipt["claim_id"]] = receipt
        return {}

    def run(self):
        return worker.settle_due(gateway=self, source=self.bundles["human"]["trusted_source"], clock=lambda: NOW)


class PredictionPairTests(unittest.TestCase):
    def test_both_commit_before_one_human_comparison_and_internal_marker(self):
        runtime = PairRuntime()
        result = runtime.run()
        self.assertEqual(result["status"], "COMPLETE")
        ops = [operation for operation, _ in runtime.calls]
        self.assertEqual(ops, ["list_due_claims", "record_settlement", "record_settlement", "record_learning", "record_learning"])
        human, momentum = runtime.learning["synthetic-human"], runtime.learning["synthetic-momentum"]
        self.assertEqual(human["schema_version"], "gold-research-learning.v2")
        self.assertEqual(human["receipt_kind"], "comparison_receipt")
        self.assertEqual((human["human_score"], human["momentum_score"], human["nochange_score"]), (1, 0, 0))
        self.assertEqual(human["sample_count"], 1)
        self.assertFalse(human["accepted_learning"])
        self.assertEqual(momentum["receipt_kind"], "internal_completion")
        self.assertNotIn("sample_count", momentum)
        self.assertEqual(list(worker.due_claims(runtime)), [])

    def test_human_waits_for_missing_momentum_then_recovers_original_bytes(self):
        runtime = PairRuntime()
        original_rows = runtime.bundles["momentum"]["observations"]
        runtime.bundles["momentum"]["observations"] = []
        first = runtime.run()
        self.assertEqual(first["status"], "COMPLETE")
        self.assertFalse(runtime.learning)
        frozen = copy.deepcopy(runtime.settlements["synthetic-human"])
        runtime.bundles["momentum"]["observations"] = original_rows
        runtime.calls = []
        self.assertEqual(runtime.run()["status"], "COMPLETE")
        self.assertEqual(runtime.settlements["synthetic-human"], frozen)
        submitted = [payload["claim_id"] for op, payload in runtime.calls if op == "record_settlement"]
        self.assertEqual(submitted, ["synthetic-momentum"])
        self.assertEqual(runtime.learning["synthetic-human"]["human_settlement_receipt_sha256"], frozen["receipt_sha256"])

    def test_stale_due_view_cannot_replace_fresh_effective_acknowledgement(self):
        runtime = PairRuntime()
        momentum = runtime.bundles["momentum"]
        runtime.settlements["synthetic-momentum"] = receipt_envelope(settle_daily_first_capture(momentum))
        self.assertEqual(runtime.run()["status"], "COMPLETE")
        self.assertEqual(runtime.learning["synthetic-human"]["receipt_kind"], "comparison_receipt")

    def test_momentum_marker_does_not_strand_later_human_comparison(self):
        runtime = PairRuntime()
        human_rows = runtime.bundles["human"]["observations"]
        runtime.bundles["human"]["observations"] = []
        runtime.run()
        self.assertEqual(set(runtime.learning), {"synthetic-momentum"})
        runtime.bundles["human"]["observations"] = human_rows
        runtime.run()
        self.assertEqual(set(runtime.learning), {"synthetic-human", "synthetic-momentum"})
        self.assertEqual(runtime.learning["synthetic-human"]["sample_count"], 1)

    def test_learning_failure_reuses_committed_settlement_and_does_not_resettle(self):
        runtime = PairRuntime(); runtime.fail_learning_once = "synthetic-human"
        self.assertEqual(runtime.run()["status"], "SYSTEM_ERROR")
        frozen = copy.deepcopy(runtime.settlements)
        runtime.calls = []
        self.assertEqual(runtime.run()["status"], "COMPLETE")
        self.assertEqual(runtime.settlements, frozen)
        self.assertNotIn("record_settlement", [op for op, _ in runtime.calls])
        self.assertEqual(runtime.learning["synthetic-human"]["sample_count"], 1)

    def test_same_outcome_but_different_endpoint_is_not_effective(self):
        runtime = PairRuntime()
        runtime.bundles["momentum"]["observations"][1]["capture_id"] = "different-close"
        self.assertEqual(runtime.run()["status"], "COMPLETE")
        self.assertNotIn("synthetic-human", runtime.learning)
        self.assertIn("synthetic-momentum", runtime.learning)

    def test_pair_claim_window_mismatch_cannot_produce_comparison(self):
        runtime = PairRuntime()
        runtime.bundles["momentum"]["claim"]["neutral_band_pct"] = "0.3"
        refreeze(runtime.bundles["momentum"])
        self.assertEqual(runtime.run()["status"], "SYSTEM_ERROR")
        self.assertNotIn("synthetic-human", runtime.learning)

    def test_stored_nested_format_is_rejected_without_learning(self):
        runtime = PairRuntime()
        human = runtime.bundles["human"]
        receipt = settle_daily_first_capture(human)
        receipt["model_score"] = {"correct": True, "direction": 1}
        runtime.settlements["synthetic-human"] = receipt_envelope(receipt)
        self.assertEqual(runtime.run()["status"], "SYSTEM_ERROR")
        self.assertNotIn("synthetic-human", runtime.learning)


if __name__ == "__main__":
    unittest.main()
