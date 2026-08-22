from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md"


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


if __name__ == "__main__":
    unittest.main()
