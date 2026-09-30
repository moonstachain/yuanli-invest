import copy
import unittest

from scripts.ymq4_b2_fixed_beta import frozen_panel, build_transformed_rows, fit_ols, split_rows
from tests.test_ymq4_b2 import synthetic_panel
from yuanli_invest.receipts import receipt_envelope


class B2FrozenInputTests(unittest.TestCase):
    def snapshot(self):
        rows = synthetic_panel()
        envelope = receipt_envelope({"schema_version": "b2-input.v1", "panel_id": "gold_core_monthly_v0.1", "rows": rows})
        return rows, {"snapshot_id": "synthetic-b2-v1", "payload_json": envelope["receipt_json"], "sha256": envelope["receipt_sha256"]}

    def test_later_panel_months_and_revisions_do_not_change_frozen_experiment(self):
        live, snapshot = self.snapshot()
        before = frozen_panel(snapshot)
        expected = fit_ols(split_rows(build_transformed_rows(before))[0])
        live[0]["value_numeric"] *= 2
        next_month = copy.deepcopy(live[-4:])
        for row in next_month:
            row["decision_date"] = row["known_as_of"] = "2026-09-30"
        live.extend(next_month)
        after = frozen_panel(snapshot)
        self.assertEqual(before, after)
        self.assertEqual(expected, fit_ols(split_rows(build_transformed_rows(after))[0]))

    def test_altered_bytes_or_unidentified_input_is_rejected(self):
        _, snapshot = self.snapshot()
        with self.assertRaises(ValueError):
            frozen_panel({**snapshot, "payload_json": snapshot["payload_json"] + " "})
        with self.assertRaises(ValueError):
            frozen_panel({**snapshot, "snapshot_id": ""})


if __name__ == "__main__":
    unittest.main()
