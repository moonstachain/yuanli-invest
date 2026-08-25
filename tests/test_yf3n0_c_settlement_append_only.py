import json
import unittest

from scripts import yf3n0_prospective as yf3
from tests.test_yf3n0_c_prospective import make_synthetic_preregistration_bundle


class YF3N0CSettlementAppendOnlyTests(unittest.TestCase):
    def test_settlement_record_cannot_rewrite_preregistered_prediction(self):
        bundle = make_synthetic_preregistration_bundle()
        resolution_output = {
            "settlement_record_id": "SYN-SET-APPEND-ONLY",
            "horizon": "T180",
            "binary_resolutions": [
                {"outcome_definition_id": "OUT-FORCE", "resolution": "YES"}
            ],
            "causal_settlements": [],
            "new_evidence_refs": ["SYN-FUTURE-APPEND-ONLY"],
        }
        record = yf3.build_settlement_record(
            bundle,
            resolution_output,
            "2027-02-20T00:11:00Z",
        )
        serialized = json.dumps(record, sort_keys=True)
        for forbidden in (
            "replacement_prediction_contract",
            "revised_probability",
            "revised_resolution_rule",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertNotIn("prediction_contract", record)
        self.assertEqual(record["preregistration_bundle_id"], bundle["preregistration_bundle_id"])


if __name__ == "__main__":
    unittest.main()
