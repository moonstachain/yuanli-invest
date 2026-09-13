from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_ymq3_r0a.py"
RECEIPT = ROOT / "artifacts" / "ymq3" / "r0a" / "YMQ3-R0A-PROBE-20260913" / "evidence-sufficiency-receipt.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_ymq3_r0a", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R0A validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReceiptIntegrityTest(unittest.TestCase):
    def test_canonical_receipt_hash_is_recomputed(self):
        m = load_validator()
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        m.validate_receipt_artifact_hash(receipt)

    def test_receipt_mutation_without_hash_change_fails(self):
        m = load_validator()
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        receipt["program_verdict"] = "FULL6_READY"
        with self.assertRaises(ValueError):
            m.validate_receipt_artifact_hash(receipt)


if __name__ == "__main__":
    unittest.main()
