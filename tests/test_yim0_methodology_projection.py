from pathlib import Path
import copy
import json
import unittest

from scripts import validate_yim0_methodology_projection as yim0

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md"
README = ROOT / "docs/os-vnext/README.md"
STATUS = ROOT / "docs/architecture/CANON-STATUS.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class YIM0HumanProjectionTests(unittest.TestCase):
    def text(self):
        return MAP.read_text(encoding="utf-8")

    def test_map_exists_with_authority_notice_and_guards(self):
        text = self.text()
        self.assertIn("human navigation projection", text.lower())
        self.assertIn("It does not create ontology, schema, registry, portfolio, trading, execution, or program-stage authority", text)
        self.assertIn("Human Grammar != Machine Ontology", text)
        self.assertIn("Asset != Engine", text)
        self.assertIn("Target != Thesis != Position != Book", text)
        self.assertIn("Research pass != Capital pass", text)
        self.assertIn("ClaimAuthority <= EvidenceAuthority", text)

    def test_mother_map_and_engine_state_chain_are_present(self):
        text = self.text()
        for token in ("实在 · 可错 · 反身 · 演化 · 凸性 · 生存", "势 · 信 · 极｜真 · 价 · 生", "ENG-C", "ENG-R", "ENG-X", "ResearchTarget", "EngineThesis", "PositionPassport", "BookState@PIT", "No Silent Thesis Migration", "Survive → Capture → Compound"):
            self.assertIn(token, text)

    def test_frozen_section_order_is_preserved(self):
        text = self.text()
        headings = ["00｜这张地图是什么", "01｜哲学本源：我们如何认识投资世界", "02｜人类语法：势·信·极｜真·价·生", "03｜收益机制：C / R / X", "04｜机器对象：Target → Thesis → Passport → Book", "05｜研究学习环：PIT / Evidence / Falsifier / Settlement", "06｜五资产案例：同一语法，不同物理", "07｜ME0–ME5 演进路线", "08｜Authority Map：什么能定义什么", "09｜十分钟使用方法"]
        self.assertEqual([text.index(item) for item in headings], sorted(text.index(item) for item in headings))

    def test_five_cases_are_explanatory_only(self):
        text = self.text()
        for target in ("NVIDIA", "Gold", "UST30Y", "Copper", "USDJPY"):
            self.assertIn(target, text)
        self.assertIn("不构成当前投资结论、目标价、alpha claim、组合建议或交易指令", text)

    def test_roadmap_visibility_does_not_authorize_me2_to_me5(self):
        text = self.text()
        for stage in ("ME2", "ME3", "ME4", "ME5"):
            self.assertIn(stage, text)
        self.assertIn("roadmap visible / not authorized", text)
        self.assertIn("Roadmap visibility != Stage authorization", text)


class YIM0ReadmeBridgeTests(unittest.TestCase):
    def text(self):
        return README.read_text(encoding="utf-8")

    def test_successor_bridge_exists_without_rewriting_human_grammar(self):
        text = self.text()
        self.assertIn("## Successor Architecture Bridge", text)
        self.assertIn("势 · 信 · 极｜真 · 价 · 生", text)
        self.assertIn("ENG-C / ENG-R / ENG-X", text)
        self.assertIn("ResearchTarget → EngineThesis → PositionPassport → BookState@PIT", text)
        self.assertIn("Human Grammar is not Return Engine ontology", text)
        self.assertIn("Genesis Engine Set, not a proven exhaustive ontology", text)

    def test_upstream_os_semantics_remain_intact(self):
        text = self.text()
        for invariant in ("one_core_three_worlds_three_gates_one_loop", "X | 极 := (Xs, Xa, Xp)", "顺大势 · 乘共识 · 押极值｜凭真据 · 买好价 · 永不死", "R | Regime Causal Decomposition", "Asset form is not pricing model."):
            self.assertIn(invariant, text)


class YIM0CanonStatusTests(unittest.TestCase):
    def status(self):
        return load(STATUS)

    def test_layered_system_identity_and_successor_state_model(self):
        s = self.status()
        self.assertEqual(s["system_identity"], {"mission_center": "ResearchCapability", "return_reasoning_center": "EngineThesis", "capital_expression_center": "PositionPassport"})
        self.assertEqual(s["state_architecture"]["historical_canonical_state"], "ResearchStateVector")
        self.assertEqual(s["state_architecture"]["successor_state_model"], ["ResearchTarget", "EngineThesis", "PositionPassport", "BookState"])
        self.assertFalse(s["state_architecture"]["legacy_future_write_authority"])
        self.assertEqual(s["legacy_compatibility"]["authority"], "legacy_compatibility_only")

    def test_architecture_lineage_projects_accepted_states_without_authorizing_roadmap(self):
        s = self.status(); lineage = s["architecture_lineage"]
        self.assertEqual(lineage["YIP0"]["status"], "accepted_merged")
        self.assertEqual(lineage["ME0"]["completion_gate"], "ME0_COMPLETE")
        self.assertEqual(lineage["ME1"]["completion_gate"], "ME1_COMPLETE")
        for stage in ("ME2", "ME3", "ME4", "ME5"):
            self.assertFalse(lineage[stage]["authorized"])

    def test_multi_program_projection_uses_current_qxm_gate(self):
        s = self.status(); programs = s["parallel_programs"]
        self.assertEqual(s["latest_completed_architecture_stage"], "ME1_COMPLETE")
        self.assertEqual(s["roadmap_next_unapproved_stage"], "ME2")
        self.assertFalse(s["next_stage_authorized"])
        self.assertEqual(programs["research_capability_program"]["last_authoritative_stage"], "QXM2")
        self.assertEqual(programs["research_capability_program"]["next_gate"], "QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION")
        self.assertEqual(programs["multi_engine_program"]["next_stage"], "ME2")
        self.assertFalse(programs["multi_engine_program"]["authorized"])

    def test_projection_values_align_with_state_sources(self):
        s = self.status()
        yim0.validate_state_source_alignment_data(
            s,
            load(ROOT / "docs/architecture/yip0/YIP0-STATE.json"),
            load(ROOT / "docs/architecture/me0/ME0-STATE.json"),
            load(ROOT / "docs/architecture/me1/ME1-STATE.json"),
            load(ROOT / "docs/architecture/qxm2/QXM2-STATE.json"),
        )


class YIM0GenesisNegativeTests(unittest.TestCase):
    def assert_rejected(self, fn, *args):
        with self.assertRaises((ValueError, TypeError)):
            fn(*args)

    def map_text(self):
        return MAP.read_text(encoding="utf-8")

    def readme_text(self):
        return README.read_text(encoding="utf-8")

    def status(self):
        return load(STATUS)

    def test_n1_missing_authority_notice_is_rejected(self):
        text = self.map_text().replace("human navigation projection", "navigation note")
        self.assert_rejected(yim0.validate_human_projection_text, text)

    def test_n2_positive_machine_or_trading_authority_claim_is_rejected(self):
        self.assert_rejected(yim0.validate_human_projection_text, self.map_text() + "\nYIM0 authorizes trading.\n")

    def test_n3_removed_human_grammar_is_rejected(self):
        text = self.readme_text().replace("势 · 信 · 极｜真 · 价 · 生", "C / R / X")
        self.assert_rejected(yim0.validate_readme_text, text)

    def test_n4_human_grammar_equals_engine_ontology_is_rejected(self):
        self.assert_rejected(yim0.validate_readme_text, self.readme_text() + "\nHuman Grammar = C/R/X\n")

    def test_n5_missing_accepted_lineage_stage_is_rejected(self):
        s = self.status(); del s["architecture_lineage"]["ME1"]
        self.assert_rejected(yim0.validate_canon_status_data, s)

    def test_n6_rsv_as_sole_future_state_is_rejected(self):
        s = self.status(); s["state_architecture"]["successor_state_model"] = ["ResearchStateVector"]
        self.assert_rejected(yim0.validate_canon_status_data, s)

    def test_n7_me2_authorization_is_rejected(self):
        s = self.status(); s["architecture_lineage"]["ME2"]["authorized"] = True
        self.assert_rejected(yim0.validate_canon_status_data, s)

    def test_n8_erased_parallel_qxm_program_is_rejected(self):
        s = self.status(); del s["parallel_programs"]["research_capability_program"]
        self.assert_rejected(yim0.validate_canon_status_data, s)

    def test_n9_state_source_misalignment_is_rejected(self):
        s = self.status()
        yip0 = load(ROOT / "docs/architecture/yip0/YIP0-STATE.json"); yip0["status"] = "candidate_started"
        self.assert_rejected(
            yim0.validate_state_source_alignment_data,
            s, yip0,
            load(ROOT / "docs/architecture/me0/ME0-STATE.json"),
            load(ROOT / "docs/architecture/me1/ME1-STATE.json"),
            load(ROOT / "docs/architecture/qxm2/QXM2-STATE.json"),
        )

    def test_n10_unknown_engine_or_machine_authority_is_rejected(self):
        self.assert_rejected(yim0.validate_human_projection_text, self.map_text() + "\nENG-Y\n")

    def test_n11_constitution_or_schema_scope_change_is_rejected(self):
        self.assert_rejected(yim0.validate_scope_paths, ["docs/os-vnext/CONSTITUTION.md"])
        self.assert_rejected(yim0.validate_scope_paths, ["packages/contracts/schemas/vnext/engine-thesis.schema.json"])

    def test_n12_root_readme_change_is_rejected(self):
        self.assert_rejected(yim0.validate_scope_paths, ["README.md"])


class YIM0PostCompletionScopeTests(unittest.TestCase):
    def test_completed_yim0_does_not_scope_lock_unrelated_future_prs(self):
        yim0.validate_scope_paths(
            ["docs/architecture/sdr0/SDR0-STATE.json"],
            enforce_yim0_scope=False,
        )

    def test_completed_yim0_still_rejects_protected_authority_paths(self):
        with self.assertRaises(ValueError):
            yim0.validate_scope_paths(
                ["docs/architecture/me0/ME0-STATE.json"],
                enforce_yim0_scope=False,
            )


class YIM0ValidatorTests(unittest.TestCase):
    def test_repository_yim0_projection_passes(self):
        yim0.main()

    def test_yim0_state_preserves_zero_authority(self):
        state = load(ROOT / "docs/architecture/yim0/YIM0-STATE.json")
        self.assertTrue(state["authority"]["human_projection_only"])
        self.assertTrue(all(value is False for key, value in state["authority"].items() if key != "human_projection_only"))
        self.assertEqual(state["human_review_threshold"], "10/10 PASS")
        self.assertTrue(state["human_gate"]["acceptance_does_not_imply_merge"])
        self.assertTrue(state["human_gate"]["acceptance_does_not_authorize_ME2"])


if __name__ == "__main__":
    unittest.main()
