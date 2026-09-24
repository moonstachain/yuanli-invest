import io
import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from threading import Barrier
from unittest import mock

from scripts import receipt_store
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
    @staticmethod
    def _response(dates, values):
        return json.dumps({"content": [{"type": "text", "text": json.dumps({
            "metrics": [{"meta": {"code": "TEST"}, "date": dates, "value": values}]
        })}]})

    def test_parser_rejects_invalid_observation_at_provider_seam(self):
        cases = [
            (["20260915"], [value])
            for value in (None, True, "3.05", float("nan"), float("inf"))
        ] + [
            (["20260230"], [3.05]),
            (["2026-09-15"], [3.05]),
            ("20260915", "12345678"),
            (["20260915"], []),
        ]
        for dates, values in cases:
            with self.subTest(dates=dates, values=values), self.assertRaises(ValueError):
                shadow.parse_wind_cli_response(self._response(dates, values), expected_code="TEST")

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

    def test_metric_queries_overlap_and_preserve_names(self):
        started = Barrier(3)

        def query(cli, code):
            started.wait(timeout=5)
            return {"code": code}

        metric_cfg = shadow.load_activation()["provider"]["metrics"]
        with mock.patch.object(shadow, "query_wind_metric", side_effect=query):
            result = shadow.query_wind_metrics(Path("/tmp/cli.mjs"), metric_cfg)
        self.assertEqual(result, {name: {"code": spec["code"]} for name, spec in metric_cfg.items()})

    def test_metric_query_failure_does_not_return_partial_batch(self):
        def query(cli, code):
            if code == "BAD":
                raise ValueError("provider unavailable")
            return {"code": code}

        with mock.patch.object(shadow, "query_wind_metric", side_effect=query):
            with self.assertRaisesRegex(ValueError, "provider unavailable"):
                shadow.query_wind_metrics(Path("/tmp/cli.mjs"), {"first": {"code": "OK"}, "second": {"code": "BAD"}})


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

    def test_concurrent_runs_preserve_every_receipt_and_complete_latest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipts = [{"as_of": "2026-09-16", "run": run} for run in range(20)]
            with ThreadPoolExecutor(max_workers=4) as executor:
                paths = list(executor.map(lambda value: shadow.write_receipt(value, root), receipts))
            self.assertEqual(len(set(paths)), len(receipts))
            self.assertEqual([json.loads(path.read_text()) for path in paths], receipts)
            self.assertIn(json.loads((root / "latest.json").read_text()), receipts)
            self.assertEqual(list(root.rglob(".receipt-*")), [])

    def test_failed_latest_replacement_keeps_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = {"as_of": "2026-09-16", "run": 1}
            shadow.write_receipt(original, root)
            replace = os.replace

            def fail_latest(source, target):
                if target.name == "latest.json":
                    raise OSError("disk unavailable")
                replace(source, target)

            with mock.patch.object(receipt_store.os, "replace", side_effect=fail_latest):
                with self.assertRaisesRegex(OSError, "disk unavailable"):
                    shadow.write_receipt({**original, "run": 2}, root)
            self.assertEqual(json.loads((root / "latest.json").read_text()), original)
            self.assertEqual(len(list(root.glob("*/receipt-*.json"))), 2)
            self.assertEqual(list(root.rglob(".receipt-*")), [])

    def test_invalid_receipt_does_not_create_runtime_files(self):
        for receipt in ({"as_of": "../escape"}, {"as_of": "2026-09-16", "value": float("nan")}):
            with self.subTest(receipt=receipt), tempfile.TemporaryDirectory() as td:
                with self.assertRaises(ValueError):
                    shadow.write_receipt(receipt, Path(td))
                self.assertEqual(list(Path(td).iterdir()), [])


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
            stale_learning = root / "learning" / "latest-learning.json"
            stale_learning.parent.mkdir()
            stale_learning.write_text('{"as_of": "2026-09-01"}')
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
            self.assertNotIn("--learning", argv)

            current_learning = root / "learning" / "current.json"
            current_learning.write_text('{"as_of": "2026-09-16"}')
            with mock.patch.dict(os.environ, env, clear=True):
                shadow.emit_product_sink(receipt, root, learning_path=current_learning)
            argv = run.call_args.args[0]
            self.assertEqual(argv[argv.index("--learning") + 1], str(current_learning))


class RunnerTests(unittest.TestCase):
    def test_learning_failure_keeps_receipt_and_sink_but_fails_scheduler_run(self):
        cfg = shadow.load_activation()
        metrics = {
            name: {"meta": {"code": spec["code"]}, "latest_date": "20260923", "latest_value": 1.25}
            for name, spec in cfg["provider"]["metrics"].items()
        }
        learning_cfg = learning.load_contract()
        learning_cfg["authority"]["production_scheduler_integration_authorized"] = True
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cli = root / "cli.mjs"
            cli.touch()
            output = io.StringIO()
            with mock.patch.multiple(
                shadow,
                default_cli_path=mock.Mock(return_value=cli),
                default_runtime_dir=mock.Mock(return_value=root),
                query_wind_metrics=mock.Mock(return_value=metrics),
                emit_product_sink=mock.Mock(return_value={"status": "MACHINE_REALITY_SINK_PASS"}),
            ), mock.patch.multiple(
                learning,
                load_contract=mock.Mock(return_value=learning_cfg),
                process_current_receipt=mock.Mock(side_effect=OSError("learning storage unavailable")),
            ), mock.patch.object(shadow, "date", wraps=date) as clock, redirect_stdout(output):
                clock.today.return_value = date(2026, 9, 24)
                code = shadow.main()
                target = Path(json.loads(output.getvalue())["receipt"])
                shadow.emit_product_sink.assert_called_once_with(target, root, learning_path=None)
            result = json.loads(output.getvalue())
            self.assertEqual(code, 3)
            self.assertEqual(result["status"], "LIVE_SHADOW_RECEIPT")
            self.assertEqual(result["learning_status"], "LEARNING_FAIL_CLOSED")
            self.assertEqual(result["product_sink_status"], "MACHINE_REALITY_SINK_PASS")
            self.assertEqual(json.loads(target.read_text())["status"], "LIVE_SHADOW_RECEIPT")
            self.assertEqual(json.loads((root / "latest.json").read_text()), json.loads(target.read_text()))

    def test_missing_provider_cli_emits_persisted_failure_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = io.StringIO()
            with mock.patch.multiple(
                shadow,
                default_cli_path=mock.Mock(return_value=root / "missing.mjs"),
                default_runtime_dir=mock.Mock(return_value=root),
                emit_product_sink=mock.Mock(return_value={"status": "PRODUCT_SINK_DISABLED"}),
                emit_learning_live=mock.Mock(),
            ), mock.patch.object(shadow, "date", wraps=date) as clock, redirect_stdout(output):
                clock.today.return_value = date(2026, 9, 24)
                code = shadow.main()
                shadow.emit_learning_live.assert_not_called()
                self.assertIsNone(shadow.emit_product_sink.call_args.kwargs["learning_path"])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "PROVIDER_FAIL_CLOSED")
            self.assertEqual(result["error_type"], "FileNotFoundError")
            self.assertEqual(json.loads((root / "latest.json").read_text())["status"], "PROVIDER_FAIL_CLOSED")


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
        self.assertIn("<key>RunAtLoad</key><false/>", installer)
        self.assertNotIn("launchctl kickstart", installer)

    def test_legacy_installer_remains_separate(self):
        installer = LAUNCHD_INSTALLER.read_text()
        self.assertNotIn("run_ymq_gold2_live_shadow_machine.sh", installer)


if __name__ == "__main__":
    unittest.main()
