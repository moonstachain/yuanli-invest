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
        self.assertIn("Human Grammar != Machine Ontology", text)
        self.assertIn("Asset != Engine", text)
        self.assertIn("Target != Thesis != Position != Book", text)


if __name__ == "__main__":
    unittest.main()
