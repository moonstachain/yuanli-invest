import unittest
from pathlib import Path

from scripts import validate_yim0_methodology_projection as yim0


class YIM0ScopeWindowTests(unittest.TestCase):
    def test_scope_window_is_frozen_to_semantic_merge_commit(self):
        state = yim0.load_json(Path(yim0.YIM0_STATE))
        paths = yim0.changed_paths_from_yim0_merge(state)
        self.assertTrue(paths)
        self.assertNotIn(".github/workflows/ymq4-dp1b-historical-backfill.yml", paths)
        yim0.validate_scope_paths(paths)


if __name__ == "__main__":
    unittest.main()
