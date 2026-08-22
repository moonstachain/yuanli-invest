from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md"
README = ROOT / "docs/os-vnext/README.md"


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
        for token in (
            "实在 · 可错 · 反身 · 演化 · 凸性 · 生存",
            "势 · 信 · 极｜真 · 价 · 生",
            "ENG-C",
            "ENG-R",
            "ENG-X",
            "ResearchTarget",
            "EngineThesis",
            "PositionPassport",
            "BookState@PIT",
            "No Silent Thesis Migration",
            "Survive → Capture → Compound",
        ):
            self.assertIn(token, text)

    def test_frozen_section_order_is_preserved(self):
        text = self.text()
        headings = [
            "00｜这张地图是什么",
            "01｜哲学本源：我们如何认识投资世界",
            "02｜人类语法：势·信·极｜真·价·生",
            "03｜收益机制：C / R / X",
            "04｜机器对象：Target → Thesis → Passport → Book",
            "05｜研究学习环：PIT / Evidence / Falsifier / Settlement",
            "06｜五资产案例：同一语法，不同物理",
            "07｜ME0–ME5 演进路线",
            "08｜Authority Map：什么能定义什么",
            "09｜十分钟使用方法",
        ]
        positions = [text.index(item) for item in headings]
        self.assertEqual(positions, sorted(positions))

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

    def test_projection_does_not_assert_new_machine_or_trading_authority(self):
        text = self.text().lower()
        forbidden_affirmative_claims = (
            "yim0 authorizes trading",
            "yim0 authorizes portfolio",
            "yim0 authorizes me2",
            "this document creates ontology authority",
            "human grammar = machine ontology",
            "cash is the fourth return engine",
        )
        for phrase in forbidden_affirmative_claims:
            self.assertNotIn(phrase, text)


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
        for invariant in (
            "one_core_three_worlds_three_gates_one_loop",
            "X | 极 := (Xs, Xa, Xp)",
            "顺大势 · 乘共识 · 押极值｜凭真据 · 买好价 · 永不死",
            "R | Regime Causal Decomposition",
            "Asset form is not pricing model.",
        ):
            self.assertIn(invariant, text)

    def test_bridge_does_not_claim_downstream_authority(self):
        text = self.text().lower()
        self.assertIn("does not create schema, registry, portfolio, trading, execution, m3 cutover, or me2–me5 program authority", text)
        self.assertNotIn("human grammar = c/r/x", text)
        self.assertNotIn("researchstatevector is obsolete", text)


if __name__ == "__main__":
    unittest.main()
