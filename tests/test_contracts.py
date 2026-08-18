import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_repository_validator(self):
        subprocess.run([sys.executable, "scripts/validate_repository.py"], cwd=ROOT, check=True)

    def test_schema_ids_are_urns(self):
        for path in (ROOT / "packages" / "contracts" / "schemas").glob("*.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(schema["$id"].startswith("urn:yuanli-invest:schema:"), path)


if __name__ == "__main__":
    unittest.main()
