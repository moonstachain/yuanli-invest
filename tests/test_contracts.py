import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import validate_repository

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_repository_validator(self):
        result = validate_repository(ROOT)
        self.assertGreater(result["objects"], 0)
        self.assertGreater(result["schemas"], 0)


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        shutil.copytree(ROOT / "packages/contracts/schemas", self.root / "packages/contracts/schemas")
        self.narrative = json.loads(next((ROOT / "canon/narratives").glob("*.json")).read_text())
        self.write("canon/narrative.json", self.narrative)

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_independent_repository_without_events_is_valid(self):
        self.assertEqual(validate_repository(self.root)["objects"], 1)

    def test_unknown_object_type_is_rejected(self):
        self.narrative["object_type"] = "NotAResearchObject"
        self.write("canon/narrative.json", self.narrative)
        with self.assertRaisesRegex(ValueError, "unknown object_type"):
            validate_repository(self.root)

    def test_invalid_datetime_is_rejected(self):
        self.narrative["as_of"] = "yesterday"
        self.write("canon/narrative.json", self.narrative)
        with self.assertRaisesRegex(ValueError, "date-time"):
            validate_repository(self.root)

    def test_duplicate_object_version_is_rejected(self):
        self.write("canon/duplicate.json", self.narrative)
        with self.assertRaisesRegex(ValueError, "duplicate object version"):
            validate_repository(self.root)

    def test_invalid_source_uri_is_rejected(self):
        source = json.loads(next((ROOT / "canon/source-records").glob("*.json")).read_text())
        source["source_url"] = "not a URI"
        self.write("canon/source.json", source)
        with self.assertRaisesRegex(ValueError, "uri"):
            validate_repository(self.root)

    def test_missing_event_subject_is_rejected(self):
        event = json.loads(next((ROOT / "events").rglob("*.json")).read_text())
        event["subject_id"] = "missing-subject"
        event["evidence_ids"] = []
        self.write("events/event.json", event)
        with self.assertRaisesRegex(ValueError, "missing event subject"):
            validate_repository(self.root)


if __name__ == "__main__":
    unittest.main()
