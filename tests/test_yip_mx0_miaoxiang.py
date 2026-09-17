import json
import unittest
from datetime import date

from scripts import yip_mx0_miaoxiang as mx


class MiaoxiangParserTests(unittest.TestCase):
    def test_parse_macro_payload_selects_latest_daily_london_gold(self):
        text = json.dumps({"data": [
            {"columns": ["宏观数据（周）", "数据来源", "2026-09-04"],
             "items": [["国际现货价格:黄金(英)(美元/金衡盎司)", "商务部", "4422"]]},
            {"columns": ["宏观数据（日）", "数据来源", "2026-09-16", "2026-09-15"],
             "items": [["伦敦金现(美元/盎司)", "Choice数据", "4263", "4293"]]}
        ]}, ensure_ascii=False)
        metric = mx.parse_macro_text(text, series_contains="伦敦金现")
        self.assertEqual(metric["series_label"], "伦敦金现(美元/盎司)")
        self.assertEqual(metric["source"], "Choice数据")
        self.assertEqual(metric["latest_date"], "2026-09-16")
        self.assertEqual(metric["latest_value"], 4263.0)
        self.assertEqual(metric["frequency"], "daily")
        self.assertEqual(metric["unit"], "美元/盎司")

    def test_parse_macro_payload_rejects_ambiguous_match(self):
        text = json.dumps({"data": [{
            "columns": ["宏观数据（日）", "数据来源", "2026-09-16"],
            "items": [["伦敦金现A(美元/盎司)", "A", "1"], ["伦敦金现B(美元/盎司)", "B", "2"]]
        }]}, ensure_ascii=False)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            mx.parse_macro_text(text, series_contains="伦敦金现")


class MiaoxiangReceiptTests(unittest.TestCase):
    def test_build_receipt_is_evidence_only_and_no_execution_authority(self):
        metric = {
            "series_label": "伦敦金现(美元/盎司)", "source": "Choice数据",
            "latest_date": "2026-09-16", "latest_value": 4263.0,
            "frequency": "daily", "unit": "美元/盎司", "raw_sha256": "abc",
        }
        receipt = mx.build_receipt(metric, as_of=date(2026, 9, 17))
        self.assertEqual(receipt["provider"], "EASTMONEY_MIAOXIANG")
        self.assertEqual(receipt["authority"], "EVIDENCE_ONLY")
        self.assertFalse(receipt["capital_authorized"])
        self.assertFalse(receipt["execution_authorized"])
        self.assertFalse(receipt["canon_promotion_authorized"])
        self.assertEqual(receipt["known_as_of"], "2026-09-16")

    def test_compare_with_wind_flags_semantic_reconciliation_not_provider_failure(self):
        mx_metric = {"latest_date": "2026-09-16", "latest_value": 4263.0,
                     "series_label": "伦敦金现(美元/盎司)", "source": "Choice数据"}
        wind_metric = {"latest_date": "2026-09-16", "latest_value": 4328.2,
                       "metric_name": "现货价(伦敦市场):黄金:美元", "source": "根据新闻整理"}
        comparison = mx.compare_gold_sources(mx_metric, wind_metric, gap_threshold_pct=0.5)
        self.assertEqual(comparison["status"], "REQUIRES_SEMANTIC_RECONCILIATION")
        self.assertGreater(abs(comparison["gap_pct"]), 0.5)
        self.assertFalse(comparison["provider_failure_inferred"])


class MiaoxiangRuntimeContractTests(unittest.TestCase):
    def test_config_is_read_only_and_contains_no_secret(self):
        cfg = mx.load_config()
        self.assertEqual(cfg["provider"]["endpoint"], "https://mxapi.eastmoney.com/mxds/mcp")
        self.assertEqual(cfg["provider"]["auth_header"], "em_api_key")
        self.assertEqual(cfg["provider"]["authority"], "EVIDENCE_ONLY")
        self.assertFalse(cfg["authority"]["execution_authorized"])
        self.assertFalse(cfg["authority"]["capital_authorized"])
        import re
        self.assertIsNone(re.search(r"em_[A-Za-z0-9]{16,}", json.dumps(cfg)))

    def test_extract_tool_text_requires_single_text_payload(self):
        payload = {"content": [{"type": "text", "text": "{\"data\":[]}"}], "isError": False}
        self.assertEqual(mx.extract_tool_text(payload), '{"data":[]}')
        with self.assertRaisesRegex(ValueError, "exactly one text"):
            mx.extract_tool_text({"content": [], "isError": False})

    def test_runtime_dir_defaults_outside_repository(self):
        runtime = mx.default_runtime_dir()
        self.assertIn(".yuanli/runtime/yip_mx0", str(runtime))
        self.assertNotIn("superpowers/worktrees", str(runtime))

    def test_env_key_is_trimmed_without_mutating_config(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"EM_API_KEY": "  secret-value  "}, clear=False):
            self.assertEqual(mx.load_api_key(), "secret-value")



class MiaoxiangProviderAdapterTests(unittest.TestCase):
    def test_provider_adapter_validates_against_contract(self):
        from jsonschema import validate
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        adapter = json.loads((root / "registry/providers/eastmoney-miaoxiang.v0.1.json").read_text())
        schema = json.loads((root / "packages/contracts/schemas/provider-adapter.schema.json").read_text())
        validate(adapter, schema)
        self.assertEqual(adapter["provider_adapter_id"], "PROVIDER-EASTMONEY-MIAOXIANG")
        self.assertTrue(adapter["canonical_semantics_may_not_be_redefined"])
        self.assertNotIn("api_key", json.dumps(adapter).lower())

    def test_provider_registry_admits_single_miaoxiang_pack(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        index = json.loads((root / "registry/providers/_index.json").read_text())
        self.assertEqual(index["entry_count"], 1)
        self.assertIn("eastmoney-miaoxiang.v0.1.json", index["pack_files"])


class MiaoxiangKeychainTests(unittest.TestCase):
    def test_keychain_fallback_is_used_when_env_missing(self):
        import os
        from unittest import mock
        fake = mock.Mock(returncode=0, stdout="  keychain-secret\n", stderr="")
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("scripts.yip_mx0_miaoxiang.subprocess.run", return_value=fake) as run:
            self.assertEqual(mx.load_api_key(), "keychain-secret")
        argv = run.call_args.args[0]
        self.assertEqual(argv[:2], ["security", "find-generic-password"])
        self.assertIn("yuanli.miaoxiang.api", argv)



class MiaoxiangTriangleTests(unittest.TestCase):
    def _triangle_text(self):
        return json.dumps({"data": [
            {"columns": ["利率（日）", "数据来源", "2026-09-16"],
             "items": [
                 ["美国:国债实际收益率(以通胀为标的):10年(%)", "美联储", "2.68"],
                 ["美国:国债实际收益率(以通胀为标的):20年(%)", "美联储", "2.93"],
                 ["美国:国债实际收益率(以通胀为标的):30年(%)", "美联储", "3.09"]
             ]},
            {"columns": ["宏观数据（日）", "数据来源", "2026-09-16"],
             "items": [
                 ["美元指数", "NYCE", "100.321"],
                 ["伦敦金现(美元/盎司)", "Choice数据", "4263"]
             ]}
        ]}, ensure_ascii=False)

    def test_extract_series_candidates_preserves_all_real_rate_tenors(self):
        rows = mx.extract_series_candidates(self._triangle_text(), series_contains="国债实际收益率")
        self.assertEqual(len(rows), 3)
        self.assertEqual([r["latest_value"] for r in rows], [2.68, 2.93, 3.09])

    def test_build_triangle_receipt_refuses_to_equate_tenor_points_with_wind_average(self):
        receipt = mx.build_triangle_receipt(self._triangle_text(), as_of=date(2026, 9, 17))
        self.assertEqual(receipt["metrics"]["gold_price"]["latest_value"], 4263.0)
        self.assertEqual(receipt["metrics"]["usd"]["latest_value"], 100.321)
        self.assertEqual(len(receipt["real_rate_candidates"]), 3)
        self.assertEqual(receipt["real_rate_semantic_state"], "NO_EXACT_WIND_GT10Y_AVG_EQUIVALENT")
        self.assertEqual(receipt["authority"], "EVIDENCE_ONLY")

    def test_write_private_artifacts_freezes_raw_and_normalized_receipt(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            raw_record = {"provider": "EASTMONEY_MIAOXIANG", "response": {"content": []}}
            receipt = {"status": "REALITY_PROOF_RECEIPT", "as_of": "2026-09-17"}
            paths = mx.write_private_artifacts(raw_record, receipt, Path(td))
            self.assertTrue(paths["raw"].exists())
            self.assertTrue(paths["receipt"].exists())
            self.assertIn("sha256", paths)
            self.assertNotEqual(paths["sha256"], "")



class MiaoxiangMcpClientTests(unittest.TestCase):
    def test_query_mcp_tool_uses_header_and_exact_tool(self):
        import asyncio
        seen = {}

        class TransportCtx:
            async def __aenter__(self):
                return ("read", "write", lambda: None)
            async def __aexit__(self, *args):
                return False

        def transport_factory(url, **kwargs):
            seen["url"] = url
            seen["headers"] = kwargs["headers"]
            return TransportCtx()

        class Result:
            def model_dump(self, mode="json"):
                return {"content": [{"type": "text", "text": '{"data":[]}'}], "isError": False}

        class Session:
            def __init__(self, read, write):
                seen["streams"] = (read, write)
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                return False
            async def initialize(self):
                seen["initialized"] = True
            async def call_tool(self, tool, arguments):
                seen["tool"] = tool
                seen["arguments"] = arguments
                return Result()

        payload = asyncio.run(mx.query_mcp_tool(
            endpoint="https://example.test/mcp", api_key="secret", tool="mx_macro_data", query="gold",
            transport_factory=transport_factory, session_factory=Session,
        ))
        self.assertFalse(payload["isError"])
        self.assertEqual(seen["headers"], {"em_api_key": "secret"})
        self.assertEqual(seen["tool"], "mx_macro_data")
        self.assertEqual(seen["arguments"], {"query": "gold"})
        self.assertTrue(seen["initialized"])


class MiaoxiangRegistryEvolutionTests(unittest.TestCase):
    def test_r2_validator_accepts_post_r2_provider_growth_without_rewriting_history(self):
        import subprocess, sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.run([sys.executable, str(root / "scripts/validate_r2_gold_pack.py")], cwd=root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        current = json.loads((root / "registry/registry-index.json").read_text())
        providers = next(item for item in current["registries"] if item["name"] == "providers")
        self.assertEqual(providers["entry_count"], 1)
        self.assertEqual(current["provider_adapter_count"], 1)
        self.assertEqual(current["entry_count_total"], 100)
        r2_state = json.loads((root / "docs/architecture/r2/R2-STATE.json").read_text())
        self.assertEqual(r2_state["provider_adapter_count"], 0)



if __name__ == "__main__":
    unittest.main()
