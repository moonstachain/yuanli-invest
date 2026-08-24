import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H41 = ROOT / "fixtures" / "replay" / "yma55_h4_1"
UNBLIND = H41 / "post_resolution_unblinding.json"
FREEZE_COMMIT = "805a5c52f6918c0f4339128ef5e95883de5fbf89"
EXPECTED = {
    "H41-B01": "PRIMARY_LEADS",
    "H41-B02": "ALTERNATIVE_LEADS",
    "H41-B03": "ALTERNATIVE_LEADS",
    "H41-B04": "ALTERNATIVE_LEADS",
    "H41-B05": "PRIMARY_LEADS",
    "H41-B06": "ALTERNATIVE_LEADS",
    "H41-B07": "ALTERNATIVE_LEADS",
    "H41-B08": "PRIMARY_LEADS",
    "H41-B09": "PRIMARY_LEADS",
    "H41-B10": "ALTERNATIVE_LEADS",
    "H41-B11": "ALTERNATIVE_LEADS",
    "H41-B12": "ALTERNATIVE_LEADS",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class H41PostResolutionUnblindingTests(unittest.TestCase):
    def test_unblinding_is_bound_to_prior_freeze_commit(self):
        data = load(UNBLIND)
        self.assertEqual(data["blind_freeze_commit_sha"], FREEZE_COMMIT)
        self.assertEqual(data["status"], "POST_RESOLUTION_UNBLINDED")
        self.assertFalse(data["historical_gold_admission"])
        self.assertFalse(data["capital_authority"])

    def test_unblinding_matches_sealed_mapping_and_frozen_machine_outputs(self):
        data = load(UNBLIND)
        mapping = {x["blind_case_id"]: x for x in load(H41 / "sealed_mapping.json")["cases"]}
        freeze = {x["blind_case_id"]: x["resolution"] for x in load(H41 / "blind_resolution_freeze.json")["resolutions"]}
        rows = data["cases"]
        self.assertEqual(len(rows), 12)
        self.assertEqual({x["blind_case_id"] for x in rows}, set(EXPECTED))
        for row in rows:
            blind_id = row["blind_case_id"]
            self.assertEqual(row["episode_id"], mapping[blind_id]["episode_id"])
            self.assertEqual(row["case_type"], mapping[blind_id]["case_type"])
            self.assertEqual(row["mechanism_family"], mapping[blind_id]["mechanism_family"])
            self.assertEqual(row["machine_resolution"], freeze[blind_id])
            self.assertEqual(row["settlement_expected_resolution"], EXPECTED[blind_id])
            expected_match = (
                "EVIDENCE_ABSTENTION" if row["machine_resolution"] == "INSUFFICIENT_EVIDENCE"
                else "MATCH" if row["machine_resolution"] == EXPECTED[blind_id]
                else "MISMATCH"
            )
            self.assertEqual(row["adjudication"], expected_match)

    def test_qualification_counts_are_truthful(self):
        data = load(UNBLIND)
        summary = data["summary"]
        self.assertEqual(summary["total_cases"], 12)
        self.assertEqual(summary["matches"], 10)
        self.assertEqual(summary["mismatches"], 1)
        self.assertEqual(summary["evidence_abstentions"], 1)
        self.assertEqual(summary["fully_hydrated_cases"], 11)
        self.assertEqual(summary["fully_hydrated_matches"], 10)
        self.assertEqual(summary["fully_hydrated_mismatches"], 1)
        self.assertEqual(summary["fully_hydrated_mechanism_accuracy"], "10/11")
        self.assertEqual(summary["safe_or_correct_outcomes"], "11/12")

    def test_no_incremental_superiority_claim_without_baseline(self):
        data = load(UNBLIND)
        self.assertEqual(data["incremental_value_claim"], "NOT_YET_ESTABLISHED")
        self.assertIn("baseline", data["incremental_value_blocker"].lower())


if __name__ == "__main__":
    unittest.main()
