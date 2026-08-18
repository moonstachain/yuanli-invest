import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ApiContractTests(unittest.TestCase):
    def test_envelope_requires_audit_fields(self):
        schema = json.loads(
            (ROOT / "packages" / "contracts" / "schemas" / "api-envelope.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(schema["required"]),
            {
                "data_as_of", "generated_at", "schema_version", "calculation_version",
                "source_revision", "coverage", "partial_reasons", "payload_hash", "payload",
            },
        )

    def test_openapi_freezes_required_routes(self):
        text = (ROOT / "api" / "openapi.yaml").read_text(encoding="utf-8")
        for route in (
            "/status:", "/narratives:", "/companies/{id}:", "/evidence/{id}:",
            "/theses:", "/replays/{id}:", "/copilot/query:",
        ):
            self.assertIn(route, text)


if __name__ == "__main__":
    unittest.main()
