import unittest
import weakref
from datetime import datetime, timezone

from runtime.ymq_gateway.context_compiler import compile_context
from runtime.ymq_gateway.router import route_request


class YMQGatewayTests(unittest.TestCase):
    def test_context_excludes_future_and_unknown_evidence(self):
        as_of = datetime(2026, 1, 15, tzinfo=timezone.utc)
        rows = [
            {"evidence_ref": "e1", "known_as_of": "2026-01-10T00:00:00+00:00", "status": "PASS", "authority": "RESEARCH", "payload": {"x": 1}},
            {"evidence_ref": "e2", "known_as_of": "2026-01-20T00:00:00+00:00", "status": "PASS", "authority": "RESEARCH", "payload": {"x": 2}},
            {"evidence_ref": "e3", "known_as_of": "2026-01-05T00:00:00+00:00", "status": "UNKNOWN", "authority": "RESEARCH", "payload": {"x": 3}},
        ]
        context = compile_context(as_of=as_of, evidence_rows=rows, max_items=10)
        self.assertEqual(context.evidence_refs, ("e1",))
        self.assertEqual(context.denied_refs, ("e2", "e3"))

    def test_context_is_minimal_and_deterministic(self):
        as_of = datetime(2026, 1, 15, tzinfo=timezone.utc)
        rows = [
            {"evidence_ref": f"e{i}", "known_as_of": "2026-01-01T00:00:00+00:00", "status": "PASS", "authority": "RESEARCH", "payload": {"rank": i}}
            for i in range(5)
        ]
        context = compile_context(as_of=as_of, evidence_rows=rows, max_items=2)
        self.assertEqual(context.evidence_refs, ("e0", "e1"))
        self.assertEqual(len(context.items), 2)

    def test_stream_retains_only_limit_but_still_reports_later_denials(self):
        class Evidence(dict):
            pass

        references = []

        def rows():
            for index in range(100):
                if index > 2:
                    self.assertIsNone(references[index - 2]())
                row = Evidence(
                    evidence_ref=f"e{index}",
                    known_as_of="2026-01-01T00:00:00+00:00",
                    status="PASS",
                    authority="RESEARCH",
                )
                references.append(weakref.ref(row))
                yield row
            yield Evidence(
                evidence_ref="late-denial",
                known_as_of="2026-01-01T00:00:00+00:00",
                status="UNKNOWN",
                authority="RESEARCH",
            )

        context = compile_context(
            as_of=datetime(2026, 1, 15, tzinfo=timezone.utc),
            evidence_rows=rows(),
            max_items=1,
        )
        self.assertEqual(context.evidence_refs, ("e0",))
        self.assertEqual(context.denied_refs, ("late-denial",))

    def test_router_denies_capital_and_execution(self):
        for intent in ("position_sizing", "broker_order", "real_capital_move"):
            with self.subTest(intent=intent):
                result = route_request(intent=intent, requested_authority="CAPITAL", evidence_status="PASS", provider="any")
                self.assertFalse(result.allowed)
                self.assertEqual(result.reason, "AUTHORITY_DENY")

    def test_router_denies_unknown(self):
        result = route_request(intent="research", requested_authority="RESEARCH", evidence_status="UNKNOWN", provider="any")
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "UNKNOWN_DENY")

    def test_provider_cannot_upgrade_authority(self):
        result = route_request(intent="research", requested_authority="EXECUTION", evidence_status="PASS", provider="super-provider")
        self.assertFalse(result.allowed)
        self.assertEqual(result.granted_authority, "NONE")

    def test_research_request_is_allowed_as_research_only(self):
        result = route_request(intent="research", requested_authority="RESEARCH", evidence_status="PASS", provider="replaceable-provider")
        self.assertTrue(result.allowed)
        self.assertEqual(result.granted_authority, "RESEARCH")


if __name__ == "__main__":
    unittest.main()
