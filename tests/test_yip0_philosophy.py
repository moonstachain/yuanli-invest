import unittest

from scripts import validate_yip0_philosophy


class YIP0PhilosophyTests(unittest.TestCase):
    def test_repository_yip0_contract_passes(self):
        validate_yip0_philosophy.main()


if __name__ == "__main__":
    unittest.main()
