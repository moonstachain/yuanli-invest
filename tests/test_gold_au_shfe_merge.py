"""Merging source manifests must preserve raw hashes and exact day coverage."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.gold_au_shfe_merge import merge
from tests.test_gold_au_dataset_assemble import AssemblyFixture
from yuanli_invest.gold_au_dataset_assemble import assemble_dataset


class SHFEMergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = AssemblyFixture(Path(self.temp.name))
        self.output = Path(self.temp.name) / "merged"

    def test_merged_private_source_remains_assembler_verifiable(self):
        dry = merge(provider_manifest=self.fixture.au_path,
                    shfe_manifests=[self.fixture.shfe_path], output_dir=self.output)
        self.assertEqual(dry["requested_days"], 2)
        self.assertEqual(dry["report_count"], 1)
        self.assertFalse(self.output.exists())
        merge(provider_manifest=self.fixture.au_path,
              shfe_manifests=[self.fixture.shfe_path], output_dir=self.output, execute=True)
        manifest = json.loads((self.output / "manifest.json").read_text())
        self.assertTrue(Path(manifest["reports"][0]["raw_file"]).is_file())
        dataset, report = assemble_dataset(
            au_manifest_path=self.fixture.au_path,
            macro_manifest_path=self.fixture.macro_path,
            shfe_manifest_path=self.output / "manifest.json",
            h10_mapping_path=self.fixture.mapping,
            audit_report_path=self.fixture.audit_path,
            assembled_at=datetime.fromisoformat(manifest["captured_at"]) + timedelta(seconds=1),
        )
        self.assertEqual(report["official_repair_days"], 1)
        self.assertEqual(len(dataset["bars"]), 1)

    def test_missing_report_is_not_hidden_by_merge(self):
        manifest = json.loads(self.fixture.shfe_path.read_text())
        manifest["errors"] = []
        manifest["status"] = "CAPTURED"
        self.fixture.shfe_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "do not cover provider dates"):
            merge(provider_manifest=self.fixture.au_path,
                  shfe_manifests=[self.fixture.shfe_path], output_dir=self.output)


if __name__ == "__main__":
    unittest.main()
