import json
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from scripts import ymq_gold2_live_shadow as shadow
from scripts import ymq_gold2_learning_live as learning


ROOT = Path(__file__).resolve().parents[1]
MACHINE_WRAPPER = ROOT / "scripts/run_ymq_gold2_live_shadow_machine.sh"
MACHINE_INSTALLER = ROOT / "scripts/install_ymq_gold2_live_shadow_machine_launchd.sh"
LAUNCHD_INSTALLER = ROOT / "scripts/install_ymq_gold2_live_shadow_launchd.sh"


class ActivationContractTests(unittest.TestCase):
    def test_activation_authorizes_scheduler_only(self):
        cfg = shadow.load_activation()
        shadow.validate_activation(cfg)
        self.assertTrue(cfg["authority"]["live_scheduler_authorized"])
        for field in (
            "capital_authorized",
            "sizing_authorized",
            "execution_authorized",
            "broker_action",
            "veighna_authorized",
            "canon_promotion_authorized",
        ):
            self.assertFalse(cfg["authority"][field])

    def test_activation_rejects_execution_authority(self):
        cfg = shadow.load_activation()
        cfg["authority"]["execution_authorized"] = True
        with self.assertRaises(ValueError):
            shadow.validate_activation(cfg)

    def test_pilot_window_is_bounded(self):
        cfg = shadow.load_activation()
        self.assertEqual(cfg["pilot_days"], 30)
        self.assertEqual(cfg["start_date"], "2026-09-16")
        self.assertEqual(cfg["end_date_exclusive"], "2026-10-16")
        self.assertEqual(shadow.pilot_state(date(2026, 9, 16), cfg), "ACTIVE")
        self.assertEqual(shadow.pilot_state(date(2026, 10, 15), cfg), "ACTIVE")
        self.assertEqual(shadow.pilot_state(date(2026, 10, 16), cfg), "EXPIRED")


class WindAdapterTests(unittest.TestCase):
    def test_parse_wind_cli_response_requires_exact_metric_code(self):
        payload = {
            "content": [{"type": "text", "text": json.dumps({
                "metrics": [{
                    "meta": {"code": "G1147404", "name": "real yield", "endDate": "20260915"},
                    "date": ["20260915"],
                    "value": [3.05],
                }]
            })}],
            "isError": False,
        }
        metric = shadow.parse_wind_cli_response(json.dumps(payload), expected_code="G1147404")
        self.assertEqual(metric["meta"]["code"], "G1147404")
        self.assertEqual(metric["latest_value"], 3.05)
        self.assertEqual(metric["latest_date"], "20260915")

    def test_parse_wind_cli_response_rejects_wrong_metric(self):
        payload = {
            "content": [{"type": "text", "text": json.dumps({
                "metrics": [{"meta": {"code": "WRONG"}, "date": [], "value": []}]
            })}],
            "isError": False,
        }
        with self.assertRaises(ValueError):
            shadow.parse_wind_cli_response(json.dumps(payload), expected_code="G1147404")

    @mock.patch("scripts.ymq_gold2_live_shadow.subprocess.run")
    def test_query_uses_backend_compatible_string_observation(self, run):
        run.return_value = mock.Mock(
            returncode=0,
            stdout=json.dumps({
                "content": [{"type": "text", "text": json.dumps({
                    "metrics": [{
                        "meta": {"code": "M0000271", "name": "DXY", "endDate": "20260915"},
                        "date": ["20260915"],
                        "value": [97.5],
                    }]
                })}],
                "isError": False,
            }),
            stderr="",
        )
        out = shadow.query_wind_metric(Path("/tmp/cli.mjs"), "M0000271", observation="5")
        self.assertEqual(out["latest_value"], 97.5)
        argv = run.call_args.args[0]
        request_json = json.loads(argv[-1])
        self.assertEqual(request_json["observation"], "5")


class ReceiptTests(unittest.TestCase):
    def test_build_receipt_is_research_only_and_fail_closed(self):
        cfg = shadow.load_activation()
        metrics = {
            "real_rate": {"meta": {"code": "G1147404"}, "latest_date": "20260915", "latest_value": 3.05, "raw_sha256": "a"},
            "usd": {"meta": {"code": "M0000271"}, "latest_date": "20260915", "latest_value": 97.5, "raw_sha256": "b"},
            "gold_price": {"meta": {"code": "S0031645"}, "latest_date": "20260915", "latest_value": 4400.0, "raw_sha256": "c"},
        }
        receipt = shadow.build_receipt(metrics, cfg, as_of=date(2026, 9, 16))
        self.assertEqual(receipt["research_state"], "WATCH")
        self.assertEqual(receipt["expectation_reality_state"], "INDETERMINATE")
        self.assertEqual(receipt["valuation_state"], "UNIDENTIFIABLE")
        self.assertFalse(receipt["authority"]["capital_authorized"])
        self.assertFalse(receipt["authority"]["execution_authorized"])
        self.assertIn("policy_path_expectations", receipt["unknowns"])

    def test_write_receipt_never_writes_to_repo_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            target = shadow.write_receipt({"status": "OK", "as_of": "2026-09-16"}, Path(td))
            self.assertTrue(target.exists())
            self.assertTrue(str(target).startswith(td))


class LearningIntegrationTests(unittest.TestCase):
    def _live_receipt(self, day, gold, real_rate, usd, known):
        return {
            "status": "LIVE_SHADOW_RECEIPT",
            "as_of": day,
            "known_as_of_min": known,
            "known_as_of_max": known,
            "provider_receipts": {
                "gold_price": {"metric_code": "S0031645", "latest_date": known, "latest_value": gold},
                "real_rate": {"metric_code": "G1147404", "latest_date": known, "latest_value": real_rate},
                "usd": {"metric_code": "M0000271", "latest_date": known, "latest_value": usd},
            },
            "property_drift_state": "DRIFT_CANDIDATE",
            "expectation_reality_state": "INDETERMINATE",
            "valuation_state": "UNIDENTIFIABLE",
            "research_state": "WATCH",
            "lifecycle_state": "未知",
            "unknowns": ["policy_path_expectations"],
        }

    def test_learning_hook_is_inert_without_separate_production_authorization(self):
        current = self._live_receipt("2026-09-17", 4328.2, 3.06, 100.3293, "2026-09-16")
        cfg = learning.load_contract()
        cfg["authority"]["production_scheduler_integration_authorized"] = False
        with tempfile.TemporaryDirectory() as td:
            result = shadow.emit_learning_live(current, Path(td), learning_cfg=cfg)
            self.assertEqual(result["status"], "LEARNING_INTEGRATION_NOT_AUTHORIZED")
            self.assertFalse(Path(td, "learning").exists())

    def test_learning_hook_runs_only_with_explicit_activation(self):
        prior = self._live_receipt("2026-09-16", 4296.15, 3.05, 99.6335, "2026-09-15")
        current = self._live_receipt("2026-09-17", 4328.2, 3.06, 100.3293, "2026-09-16")
        cfg = learning.load_contract()
        cfg["authority"]["production_scheduler_integration_authorized"] = True
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shadow.write_receipt(prior, root)
            shadow.write_receipt(current, root)
            result = shadow.emit_learning_live(current, root, learning_cfg=cfg)
            self.assertEqual(result["status"], "LEARNING_CANDIDATE_ONLY")
            self.assertTrue(Path(td, "learning", "latest-learning.json").exists())
            self.assertFalse(result["accepted_learning"])

    def test_learning_failure_does_not_mutate_successful_provider_receipt(self):
        current = self._live_receipt("2026-09-17", 4328.2, 3.06, 100.3293, "2026-09-16")
        original = json.loads(json.dumps(current, ensure_ascii=False))
        cfg = learning.load_contract()
        cfg["authority"]["production_scheduler_integration_authorized"] = True
        broken = dict(current)
        broken["known_as_of_max"] = "not-a-date"
        with tempfile.TemporaryDirectory() as td:
            result = shadow.emit_learning_live(broken, Path(td), learning_cfg=cfg)
            self.assertEqual(result["status"], "LEARNING_FAIL_CLOSED")
            self.assertEqual(current, original)
            self.assertNotIn("error", result)
            self.assertIn("error_type", result)


class ProductSinkHookTests(unittest.TestCase):
    def test_product_sink_is_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(
            os.environ, {}, clear=True
        ):
            result = shadow.emit_product_sink(Path(td, "receipt.json"), Path(td))
            self.assertEqual(result["status"], "PRODUCT_SINK_DISABLED")
            self.assertEqual(result["authority"], "SHADOW_ONLY")

    def test_enabled_sink_requires_client(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(
            os.environ, {"YIOS_TG1_PRODUCT_SINK_ENABLED": "true"}, clear=True
        ):
            result = shadow.emit_product_sink(Path(td, "receipt.json"), Path(td))
            self.assertEqual(result["status"], "PRODUCT_SINK_CLIENT_MISSING")

    def test_enabled_sink_requires_machine_projected_credentials(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            client = root / "sink.py"
            client.write_text("print('unused')\n")
            env = {
                "YIOS_TG1_PRODUCT_SINK_ENABLED": "true",
                "YIOS_TG1_SINK_CLIENT": str(client),
            }
            with mock.patch.dict(os.environ, env, clear=True):
                result = shadow.emit_product_sink(root / "receipt.json", root)
            self.assertEqual(
                result["status"], "PRODUCT_SINK_CREDENTIALS_NOT_PROJECTED"
            )

    @mock.patch("scripts.ymq_gold2_live_shadow._source_commit", return_value="a" * 40)
    @mock.patch("scripts.ymq_gold2_live_shadow.subprocess.run")
    def test_enabled_sink_delegates_machine_token_via_environment_only(
        self, run, _commit
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = root / "receipt.json"
            receipt.write_text("{}\n")
            client = root / "sink.py"
            client.write_text("print('unused')\n")
            run.return_value = mock.Mock(
                returncode=0,
                stdout=json.dumps({
                    "status": "MACHINE_REALITY_SINK_PASS",
                    "authority": "SHADOW_ONLY",
                }),
                stderr="",
            )
            env = {
                "YIOS_TG1_PRODUCT_SINK_ENABLED": "true",
                "YIOS_TG1_SINK_CLIENT": str(client),
                "YIOS_TG1_MACHINE_INGEST_TOKEN": "MACHINE_TOKEN_TEST_ONLY",
                "YIOS_TG1_INGEST_ENDPOINT": "https://example.invalid/ingest",
                "YIOS_TG1_MACHINE_CLIENT_ID": "YIOS-TG1-G1R-M4",
            }
            with mock.patch.dict(os.environ, env, clear=True):
                result = shadow.emit_product_sink(receipt, root)
            self.assertEqual(result["status"], "MACHINE_REALITY_SINK_PASS")
            argv = run.call_args.args[0]
            self.assertIn(str(client), argv)
            self.assertNotIn("MACHINE_TOKEN_TEST_ONLY", argv)


class MachineProjectionCandidateTests(unittest.TestCase):
    def test_wrapper_reads_scoped_ingest_token_from_keychain(self):
        sh = MACHINE_WRAPPER.read_text()
        self.assertIn("security find-generic-password", sh)
        self.assertIn("YIOS_TG1_MACHINE_INGEST_TOKEN", sh)
        self.assertIn("yuanli.yios-tg1.machine-ingest-token", sh)
        self.assertNotIn("OP_SERVICE_ACCOUNT_TOKEN", sh)
        self.assertNotIn("op run", sh)

    def test_machine_installer_contains_only_nonsecret_projection_metadata(self):
        installer = MACHINE_INSTALLER.read_text()
        self.assertIn("run_ymq_gold2_live_shadow_machine.sh", installer)
        self.assertIn("YIOS_TG1_INGEST_ENDPOINT", installer)
        self.assertIn("YIOS_TG1_MACHINE_CLIENT_ID", installer)
        self.assertIn("YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE", installer)
        self.assertNotIn("sb_secret_", installer)
        self.assertNotIn("YIOS_TG1_MACHINE_INGEST_TOKEN</key>", installer)

    def test_legacy_installer_remains_separate(self):
        installer = LAUNCHD_INSTALLER.read_text()
        self.assertNotIn("run_ymq_gold2_live_shadow_machine.sh", installer)


if __name__ == "__main__":
    unittest.main()
