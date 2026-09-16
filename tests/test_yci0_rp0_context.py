import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.ymq_gateway.router import route_request
from runtime.yci0_rp0.context_adapter import ContextPackError, build_context_pack


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "yci0_rp0" / "context_pack_policy.v0.1.json"


QUESTION = {
    "question_id": "YCI0-RP0-CQ-001",
    "intent": "research",
    "authority": "RESEARCH",
    "evidence_status": "PASS",
    "as_of": "2026-09-16T00:00:00Z",
    "brain_snapshot_ref": "brain://snapshot/rp0-001",
}


def item(item_id, category="historical_analogues", *, freshness_state="FRESH"):
    return {
        "item_id": item_id,
        "category": category,
        "content": {"summary": f"bounded context {item_id}"},
        "evidence_status": "PASS",
        "authority": "RESEARCH",
        "provenance": {
            "source_system": "Yuanli Brain",
            "source_id": f"brain-item-{item_id}",
            "source_locator": f"brain://items/{item_id}",
            "retrieved_at": "2026-09-16T00:00:00Z",
        },
        "freshness": {
            "state": freshness_state,
            "as_of": "2026-09-15T00:00:00Z",
            "checked_at": "2026-09-16T00:00:00Z",
        },
    }


def results(*items_):
    grouped = {}
    for context_item in items_:
        grouped.setdefault(context_item["category"], []).append(context_item)
    return grouped


class YCI0RP0ContextTests(unittest.TestCase):
    def test_policy_declares_per_category_and_total_retrieval_caps(self):
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertIn("max_items_per_category", policy)
        self.assertIn("max_total_items", policy)
        self.assertGreater(policy["max_total_items"], 0)
        self.assertTrue(policy["max_items_per_category"])

    def test_full_vault_or_unbounded_payload_is_rejected(self):
        unbounded = {
            "scope": "full_vault",
            "historical_analogues": [item("h1")],
        }
        with self.assertRaises(ContextPackError):
            build_context_pack(QUESTION, unbounded)

        too_many = results(*[item(f"h{i}") for i in range(20)])
        with self.assertRaises(ContextPackError):
            build_context_pack(QUESTION, too_many)

    def test_every_emitted_context_item_has_provenance_and_freshness(self):
        pack = build_context_pack(
            QUESTION,
            results(
                item("h1", "historical_analogues"),
                item("p1", "yuanli_patterns"),
                item("j1", "prior_judgments"),
                item("n1", "hard_negatives"),
                item("d1", "prior_learning_deltas"),
                item("c1", "recommended_capabilities"),
            ),
        )
        emitted = [
            context_item
            for category in (
                "historical_analogues",
                "yuanli_patterns",
                "prior_judgments",
                "hard_negatives",
                "prior_learning_deltas",
                "recommended_capabilities",
            )
            for context_item in getattr(pack, category)
        ]
        self.assertEqual(len(emitted), 6)
        for context_item in emitted:
            self.assertTrue(context_item["provenance"])
            self.assertTrue(context_item["freshness"]["state"])

    def test_missing_provenance_or_freshness_is_rejected(self):
        for field in ("provenance", "freshness"):
            malformed = item("malformed-1")
            malformed.pop(field)
            with self.subTest(field=field):
                with self.assertRaises(ContextPackError):
                    build_context_pack(QUESTION, results(malformed))

    def test_stale_or_unproven_context_cannot_upgrade_evidence_or_authority(self):
        stale = item("stale-1", freshness_state="STALE")
        unproven = item("unknown-1", freshness_state="NOT_PROVEN")
        pack = build_context_pack(QUESTION, results(stale, unproven))
        self.assertEqual(pack.authority, "RESEARCH")
        self.assertEqual(pack.freshness_summary["admitted_count"], 0)
        self.assertEqual(pack.freshness_summary["blocked_count"], 2)
        self.assertEqual(
            set(pack.freshness_summary["blocked_item_ids"]), {"stale-1", "unknown-1"}
        )
        for field in pack.to_dict():
            self.assertNotIn(field, {"buy", "sell", "capital_authorization", "execution_authorization"})

    def test_output_has_no_buy_sell_capital_or_execution_authorization_field(self):
        pack = build_context_pack(QUESTION, results(item("h1")))
        serialized = json.dumps(pack.to_dict(), ensure_ascii=False).lower()
        for forbidden in (
            "buy_authorization",
            "sell_authorization",
            "capital_authorization",
            "execution_authorization",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_nested_authorization_field_is_rejected_before_output(self):
        malformed = item("h1")
        malformed["content"] = {"capital_authorization": False}
        with self.assertRaises(ContextPackError):
            build_context_pack(QUESTION, results(malformed))

    def test_context_hash_is_deterministic_and_gateway_is_reused(self):
        first_results = results(item("h2"), item("h1", "hard_negatives"))
        second_results = {
            "hard_negatives": [item("h1", "hard_negatives")],
            "historical_analogues": [item("h2")],
        }
        with patch(
            "runtime.yci0_rp0.context_adapter.route_request",
            wraps=route_request,
        ) as routed:
            first = build_context_pack(QUESTION, first_results)
            second = build_context_pack(QUESTION, second_results)
        self.assertEqual(first.context_hash, second.context_hash)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(routed.call_count, 2)

    def test_capital_or_execution_question_is_denied_by_gateway(self):
        for authority in ("CAPITAL", "EXECUTION"):
            question = copy.deepcopy(QUESTION)
            question["authority"] = authority
            with self.subTest(authority=authority):
                with self.assertRaises(ContextPackError):
                    build_context_pack(question, results(item("h1")))


if __name__ == "__main__":
    unittest.main()
