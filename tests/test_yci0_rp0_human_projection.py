import unittest
from dataclasses import replace

from runtime.yci0_rp0.human_projection import (
    HumanProjectionError,
    build_human_projection,
)
from runtime.yci0_rp0.projection_compiler import ResearchProjection
from runtime.yci0_rp0.narrative_transmission import NarrativeTransmissionCard
from runtime.yci0_rp0.price_payoff import PricePayoffCard


def projection():
    narrative = NarrativeTransmissionCard(
        narrative_stage="D2", dominant_story="x", narrative_gap_hypothesis="y",
        primary_chain=("a", "b"), current_bottleneck="a", next_bottleneck_hypothesis="b",
        common_shock_branch="c", hard_negative_branch="d", evidence_refs=("e1",),
    )
    payoff = PricePayoffCard(
        implied_belief="i", scenarios={"BULL":"b","BASE":"base","BEAR":"bear","HARD_NEGATIVE":"h"},
        defeat_condition="capex decelerates", survival_cost="preserve optionality",
        book_mapping={"S":"s","C":"c","R":"r","X":"x"}, evidence_refs=("p1",),
    )
    return ResearchProjection(
        projection_id="proj-1", question_id="YCI0-RP0-CQ-001", as_of="2026-09-17T00:00:00Z",
        reality_as_of="2026-09-17T00:00:00Z", context_pack_id="ctx-1",
        narrative=narrative, price_payoff=payoff, defeat_condition="capex decelerates",
        confidence="MEDIUM", evidence_refs=("e1","p1"), audit_eligible=True,
    )


def current(stage="04 TRANSMISSION", known="2026-09-16T00:00:00Z"):
    return {
        "Question ID": "YCI0-RP0-CQ-001",
        "Journey Stage": stage,
        "Machine Known As Of": known,
        "Thesis": "human thesis must not change",
        "Prior Belief": "human prior must not change",
    }


def event(status="PASS", gate="PASS", known="2026-09-17T00:00:00Z", authority="RESEARCH"):
    return {
        "event_id": "evt-1",
        "source_id": "supabase://runtime/research_projections/proj-1",
        "known_as_of": known,
        "evidence_status": status,
        "gate_status": gate,
        "authority": authority,
    }


class HumanProjectionTests(unittest.TestCase):
    def test_unknown_or_blocked_regresses_to_evidence(self):
        for status in ("UNKNOWN", "BLOCKED"):
            result = build_human_projection(current("05 AUDIT"), event(status=status), projection())
            self.assertEqual(result.patch["Journey Stage"], "02 EVIDENCE")
            self.assertEqual(result.patch["Machine Evidence Status"], status)
            self.assertEqual(result.receipt.status, "APPLIED")

    def test_forward_movement_is_at_most_one_stage_and_only_to_audit(self):
        result = build_human_projection(current("04 TRANSMISSION"), event(), projection())
        self.assertEqual(result.patch["Journey Stage"], "05 AUDIT")
        from_earlier = build_human_projection(current("03 NARRATIVE"), event(), projection())
        self.assertNotIn("Journey Stage", from_earlier.patch)

    def test_no_machine_path_grants_shadow_capital_or_execution(self):
        shadow = build_human_projection(current("05 AUDIT"), event(), projection())
        self.assertNotEqual(shadow.patch.get("Journey Stage"), "06 SHADOW")
        for authority in ("CAPITAL", "EXECUTION"):
            with self.subTest(authority=authority):
                with self.assertRaises(HumanProjectionError):
                    build_human_projection(current(), event(authority=authority), projection())

    def test_stale_event_is_noop(self):
        result = build_human_projection(
            current("04 TRANSMISSION", "2026-09-17T00:00:00Z"),
            event(known="2026-09-16T00:00:00Z"),
            projection(),
        )
        self.assertEqual(result.patch, {})
        self.assertEqual(result.receipt.status, "STALE_IGNORED")

    def test_patch_is_whitelisted_and_never_overwrites_human_thesis(self):
        result = build_human_projection(current(), event(), projection())
        forbidden = {"Thesis", "Prior Belief", "Body", "Research Conclusion"}
        self.assertTrue(forbidden.isdisjoint(result.patch))
        allowed = {
            "Journey Stage", "Gate Status", "Machine Evidence Status", "Machine Gate Status",
            "Machine Known As Of", "Machine Event ID", "Machine Source ID", "Machine Sync Status",
            "Transition Suggestion", "Transition Reason", "Runtime Projection ID",
        }
        self.assertTrue(set(result.patch).issubset(allowed))

    def test_receipt_is_deterministic_for_same_input(self):
        a = build_human_projection(current(), event(), projection())
        b = build_human_projection(current(), event(), projection())
        self.assertEqual(a.receipt.receipt_id, b.receipt.receipt_id)
        self.assertEqual(a.receipt.request_hash, b.receipt.request_hash)


if __name__ == "__main__":
    unittest.main()
