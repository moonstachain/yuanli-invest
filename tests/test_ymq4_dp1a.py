import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dp1a", ROOT / "scripts/ymq4_dp1a_reality_proof.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TestDP1A(unittest.TestCase):
    def test_redacts_api_key(self):
        url = "https://x.test/path?series_id=CPIAUCSL&api_key=SECRET123&output_type=4"
        out = MOD.redact_api_key(url)
        self.assertNotIn("SECRET123", out)
        self.assertIn("REDACTED", out)

    def test_parse_initial_four_clocks(self):
        raw = json.dumps({"observations": [{
            "realtime_start": "2020-03-11",
            "realtime_end": "2020-03-11",
            "date": "2020-02-01",
            "value": "259.050"
        }]}).encode()
        got = MOD.parse_initial(raw)
        self.assertEqual(got["observation_date"], "2020-02-01")
        self.assertEqual(got["release_date"], "2020-03-11")
        self.assertEqual(got["known_as_of"], "2020-03-11")

    def test_parse_initial_fails_without_realtime_start(self):
        raw = json.dumps({"observations": [{"date": "2020-02-01", "value": "259.050"}]}).encode()
        with self.assertRaises(RuntimeError):
            MOD.parse_initial(raw)


if __name__ == "__main__":
    unittest.main()
