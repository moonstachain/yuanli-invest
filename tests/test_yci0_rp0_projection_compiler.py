import json
import unittest
from dataclasses import replace

from runtime.yci0_rp0.context_adapter import ContextPack
from runtime.yci0_rp0.narrative_transmission import (
    NarrativeTransmissionError,
    compile_narrative_transmission,
)
from runtime.yci0_rp0.price_payoff import compile_price_payoff
from runtime.yci0_rp0.projection_compiler import ProjectionError, compile_projection
from runtime.yci0_rp0.state_compiler import RealityStateCard


def context_pack():
    return ContextPack(
        context_pack_id="ctx-1",
        question_id="YCI0-RP0-CQ-001",
        compiled_at="2026-09-17T00:00:00Z",
        as_of="2026-09-17T00:00:00Z",
        brain_snapshot_ref="brain://snap/1",
        historical_analogues=(), yuanli_patterns=(), prior_judgments=(),
        bottleneck_migration_patterns=(), hard_negatives=(), prior_learning_deltas=(),
        recommended_capabilities=(), freshness_summary={}, provenance_summary={},
        context_hash="ctxhash", authority="RESEARCH",
    )


def reality_card():
    return RealityStateCard(as_of="2026-09-17T00:00:00Z", dimensions={}, authority="RESEARCH")


def narrative(stage="D2"):
    return compile_narrative_transmission(
        narrative_stage=stage,
        dominant_story="AI infrastructure demand remains strong",
        narrative_gap_hypothesis="Narrative may be ahead of realized power constraints",
        primary_chain=("AI demand", "GPU", "networking", "power/grid"),
        current_bottleneck="GPU/networking",
        next_bottleneck_hypothesis="power/grid",
        common_shock_branch="higher real yields compress all long-duration AI assets",
        hard_negative_branch="hyperscaler capex discipline breaks transmission",
        evidence_refs=("e1", "e2"),
    )


def payoff(defeat_condition="Hyperscaler capex decelerates for two consecutive releases"):
    return compile_price_payoff(
        implied_belief="market prices continued high AI infrastructure growth",
        bull="capex accelerates and new bottlenecks expand profit pools",
        base="capex stays high but returns normalize",
        bear="capex slows and valuation compresses",
        hard_negative="AI monetization fails and hyperscalers cut capex",
        defeat_condition=defeat_condition,
        survival_cost="wrong thesis must not impair next-cycle participation",
        book_mapping={"S": "protect optionality", "C": "compound only with evidence", "R": "watch regime shift", "X": "right-tail candidates only"},
        evidence_refs=("p1",),
    )


class ProjectionCompilerTests(unittest.TestCase):
    def test_narrative_stage_closed_set_and_limited_status(self):
        for stage in ("D0", "D1", "D2", "D3", "D4", "UNKNOWN"):
            card = narrative(stage)
            self.assertEqual(card.narrative_stage, stage)
            self.assertEqual(card.scientific_status, "LIMITED")
            self.assertEqual(card.authority, "RESEARCH")
        with self.assertRaises(NarrativeTransmissionError):
            narrative("D5")

    def test_transmission_requires_chain_bottlenecks_common_shock_and_hard_negative(self):
        required = {
            "primary_chain": (),
            "current_bottleneck": "",
            "next_bottleneck_hypothesis": "",
            "common_shock_branch": "",
            "hard_negative_branch": "",
        }
        for field, bad in required.items():
            kwargs = dict(
                narrative_stage="D2", dominant_story="x", narrative_gap_hypothesis="y",
                primary_chain=("a", "b"), current_bottleneck="a", next_bottleneck_hypothesis="b",
                common_shock_branch="c", hard_negative_branch="d", evidence_refs=(),
            )
            kwargs[field] = bad
            with self.subTest(field=field):
                with self.assertRaises(NarrativeTransmissionError):
                    compile_narrative_transmission(**kwargs)

    def test_price_payoff_is_research_only_and_complete(self):
        card = payoff()
        self.assertEqual(card.scientific_status, "RESEARCH")
        self.assertEqual(card.authority, "RESEARCH")
        self.assertEqual(set(card.scenarios), {"BULL", "BASE", "BEAR", "HARD_NEGATIVE"})
        self.assertTrue(card.defeat_condition)
        self.assertTrue(card.survival_cost)
        self.assertEqual(set(card.book_mapping), {"S", "C", "R", "X"})
        serialized = json.dumps(card.to_dict(), ensure_ascii=False).lower()
        for forbidden in ("buy_authorization", "sell_authorization", "capital_authorization", "execution_authorization"):
            self.assertNotIn(forbidden, serialized)

    def test_empty_defeat_condition_blocks_audit_eligible_projection(self):
        p = payoff()
        p = replace(p, defeat_condition="")
        question = {"question_id": "YCI0-RP0-CQ-001", "as_of": "2026-09-17T00:00:00Z", "authority": "RESEARCH"}
        with self.assertRaises(ProjectionError):
            compile_projection(question, reality_card(), context_pack(), narrative(), p)

    def test_projection_denies_non_research_question_authority(self):
        for authority in ("CAPITAL", "EXECUTION", "NONE"):
            question = {"question_id": "YCI0-RP0-CQ-001", "as_of": "2026-09-17T00:00:00Z", "authority": authority}
            with self.subTest(authority=authority):
                with self.assertRaises(ProjectionError):
                    compile_projection(question, reality_card(), context_pack(), narrative(), payoff())

    def test_projection_is_research_only_and_preserves_lineage(self):
        question = {"question_id": "YCI0-RP0-CQ-001", "as_of": "2026-09-17T00:00:00Z", "authority": "RESEARCH"}
        projection = compile_projection(question, reality_card(), context_pack(), narrative(), payoff())
        self.assertTrue(projection.audit_eligible)
        self.assertEqual(projection.authority, "RESEARCH")
        self.assertEqual(projection.context_pack_id, "ctx-1")
        self.assertEqual(projection.evidence_refs, ("e1", "e2", "p1"))
        serialized = json.dumps(projection.to_dict(), ensure_ascii=False).lower()
        for forbidden in ("buy_authorization", "sell_authorization", "capital_authorization", "execution_authorization", "broker_order"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
