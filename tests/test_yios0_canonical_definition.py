from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validate_yios0_canonical_definition import validate_yios0

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "config" / "yios0" / "yios0_architecture.v1.json"
CURRENT = ROOT / "config" / "yios0" / "yios0_current.json"
CANON = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-CANONICAL-ARCHITECTURE-v1.0.md"
HUMAN_CURRENT = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-CURRENT.md"
STATUS = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-STATUS-MATRIX.md"
PROJECTION = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-NOTION-PROJECTION-CONTRACT-v1.0.md"


class TestYIOS0CanonicalDefinition(unittest.TestCase):
    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_validator_passes(self):
        validate_yios0()

    def test_current_pointer_integrity(self):
        current = self.load_json(CURRENT)
        self.assertEqual(current["system_id"], "YIOS0")
        self.assertEqual(current["current_architecture_version"], "1.0.0")
        self.assertEqual(current["canonical_architecture_path"], str(CANON.relative_to(ROOT)))
        self.assertEqual(current["machine_contract_path"], str(ARCH.relative_to(ROOT)))
        self.assertEqual(current["status_projection_path"], str(STATUS.relative_to(ROOT)))
        self.assertTrue(current["runtime_status_is_separate"])
        self.assertNotIn("human_accepted_merged", json.dumps(current))
        self.assertIn("1.0.0", HUMAN_CURRENT.read_text(encoding="utf-8"))

    def test_machine_contract_semantics(self):
        arch = self.load_json(ARCH)
        required = {
            "identity", "versioning", "strategic_positioning", "mother_loop", "mother_laws",
            "authority_topology", "knowledge_spine", "action_spine", "buses", "human_layers",
            "machine_services", "experience_plane", "deployment_domains", "status_semantics",
            "projection_contract", "bootstrap_contract", "non_authorizations",
        }
        self.assertTrue(required.issubset(arch))
        self.assertEqual(
            arch["mother_loop"],
            ["Reality", "Knowledge", "Trial", "Settlement", "Capital", "Execution", "Reality", "Learning"],
        )
        laws = arch["mother_laws"]
        for law in (
            "Reality > Belief",
            "Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition",
            "ResearchPass != CapitalPass",
            "ResearchAuthority != CapitalAuthority != ExecutionAuthority",
        ):
            self.assertIn(law, laws)
        self.assertEqual(len(arch["human_layers"]), 13)
        self.assertEqual(len(arch["machine_services"]), 8)

    def test_authority_and_credential_separation(self):
        arch = self.load_json(ARCH)
        authority = arch["authority_topology"]
        self.assertTrue(authority["research_capital_execution_separate"])
        self.assertEqual(
            authority["credential_separation"],
            "ResearchCredential != CapitalCredential != ExecutionCredential != BrokerCredential",
        )
        self.assertFalse(authority["research_production_has_broker_write_authority"])
        for value in arch["non_authorizations"].values():
            self.assertFalse(value)

    def test_status_three_axis_and_negative_evidence(self):
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("STATUS_MATRIX_IS_PROJECTION = true", text)
        self.assertIn("authority_state", text)
        self.assertIn("reality_state", text)
        self.assertIn("runtime_state", text)
        self.assertIn("status_known_as_of", text)
        self.assertIn("evidence_ref", text)
        self.assertIn("open_authority_gap", text)
        self.assertIn("YMQ4-B3", text)
        self.assertIn("SCIENTIFIC_NO_GO", text)
        self.assertIn("PR #72", text)
        for component in ("YGR0", "YRP1", "State Compiler", "YAU1", "YVN1-A1", "VeighNa Adapter", "Broker Paper", "Live Execution"):
            self.assertIn(component, text)
        self.assertNotIn("| PASS |", text)

    def test_projection_is_one_way_and_non_authoritative(self):
        text = PROJECTION.read_text(encoding="utf-8")
        self.assertIn("GitHub Canon → Projection Contract → Notion Human Projection", text)
        self.assertIn("Notion Edit → Direct Canon Mutation", text)
        self.assertIn("FORBIDDEN", text)
        self.assertIn("NotionVerification != ResearchSettlement", text)

    def test_canonical_file_preserves_non_authorizations(self):
        text = CANON.read_text(encoding="utf-8")
        self.assertIn("YIP0 remains philosophy authority", text)
        self.assertIn("YVN1-A1", text)
        self.assertIn("VeighNa", text)
        self.assertIn("Broker Paper", text)
        self.assertIn("Live Execution", text)
        self.assertIn("NOT_AUTHORIZED", text)


if __name__ == "__main__":
    unittest.main()
