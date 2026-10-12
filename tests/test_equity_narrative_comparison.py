"""Meaningful arithmetic, point-in-time, accounting and authority regressions."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "research/equity-narrative-comparison"


def load(name, filename, dependencies=None):
    spec = importlib.util.spec_from_file_location(name, PACK / filename)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, dependencies or {}):
        spec.loader.exec_module(module)
    return module


model = load("equity_narrative_model_test", "model.py")
validator = load("equity_narrative_validator_test", "validator.py")
runner = load("equity_narrative_runner_test", "runner.py", {"model": model, "validator": validator})


class CashflowModelTests(unittest.TestCase):
    def test_constant_cashflow_has_perpetuity_identity_at_every_duration(self):
        for n in (1, 5, 10, 15):
            with self.subTest(years=n):
                self.assertAlmostEqual(model.cashflow_pv([10] * n, .10, 0), 100.0, places=10)

    def test_huayuan_conditional_example_keeps_duration_and_forward_pe(self):
        # Published illustrative table: profit reaches 2x in 5 years, r=7%.
        q = 2 ** (1 / 5)
        value = model.cashflow_pv([q ** t for t in range(1, 6)], .07, 0)
        self.assertAlmostEqual(value / q, 23.1467, places=3)
        q10 = 2 ** (1 / 10)
        slower = model.cashflow_pv([q10 ** t for t in range(1, 11)], .07, 0)
        self.assertNotAlmostEqual(slower, value, places=2)

    def test_terminal_growth_starts_after_explicit_final_cashflow(self):
        # One explicit year of 110 then 2% forever; manual value in time-zero units.
        self.assertAlmostEqual(model.cashflow_pv([110], .10, .02),
                               100 + 112.2 / .08 / 1.10, places=9)

    def test_cashflow_bridge_uses_explicit_cash_tax_interest_and_financing(self):
        row = {"revenue": 1000, "operating_margin": .20, "cash_interest": 10,
               "cash_taxes": 40, "depreciation_amortization": 30, "capex": 50,
               "delta_working_capital": 20, "net_borrowing": 5}
        self.assertEqual(model.cashflow_bridge(row)["equity_cash_flow"], 115)
        row["operating_margin"], row["cash_taxes"] = -.10, 0
        self.assertEqual(model.cashflow_bridge(row)["equity_cash_flow"], -145)

    def test_inverse_is_invariant_to_consistent_share_unit_rescaling(self):
        original = model.implied_growth(500, 10, 10, .10, .02)
        split = model.implied_growth(50, 1, 10, .10, .02)
        self.assertEqual(original["status"], "conditional_solution")
        self.assertAlmostEqual(original["annual_cashflow_growth"], split["annual_cashflow_growth"], places=12)
        self.assertLess(original["relative_identity_residual"], 1e-10)

    def test_negative_start_and_unbracketed_price_do_not_create_a_point_estimate(self):
        self.assertEqual(model.implied_growth(50, -10, 10, .10)["status"], "unsupported")
        absent = model.implied_growth(1e10, 1, 1, .10, bounds=(0, .01))
        self.assertEqual(absent["status"], "outside_search_domain")
        self.assertNotIn("annual_cashflow_growth", absent)

    def test_invalid_economic_domains_and_numerical_overflow_fail_closed(self):
        calls = [
            lambda: model.cashflow_pv([1], .05, .05),
            lambda: model.cashflow_pv([math.nan], .10),
            lambda: model.cashflow_pv([1e308], .10),
            lambda: model.implied_growth(50, True, 10, .10),
            lambda: model.implied_growth(50, 1, True, .10),
            lambda: model.growing_cashflows(1, -1, 10),
        ]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises(ValueError):
                    call()

    def test_sensitivity_retains_joint_assumptions_without_probabilities(self):
        settings = validator.read(PACK / "settings.json")
        state = model.implied_region(500, 10, settings)
        self.assertEqual(len(state["assumption_regions"]), 54)
        joint = {(r["discount_rate"], r["horizon_years"], r["terminal_growth"], r["cashflow_scale"])
                 for r in state["assumption_regions"]}
        self.assertEqual(len(joint), 54)
        self.assertEqual(state["identification_status"], "underidentified")
        self.assertNotIn("probability", state)
        with self.assertRaises(ValueError):
            model.implied_region(50, True, settings)


class ResearchReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = validator.read(PACK / "benchmark/financial-inputs.json")
        cls.market = validator.read(PACK / "benchmark/market-inputs.json")
        cls.protocol = validator.read(PACK / "benchmark/protocol.json")
        cls.settings = validator.read(PACK / "settings.json")
        cls.profile = validator.read(PACK / "profile.json")
        cls.sources = validator.read(PACK / "benchmark/sources.json")
        cls.outcomes = validator.read(PACK / "benchmark/financial-outcomes.json")
        cls.market_outcomes = validator.read(PACK / "benchmark/market-outcomes.json")

    def prepare(self):
        return runner.prepare(self.inputs, self.market, self.protocol, self.settings, self.profile, self.sources)

    def settle(self, predictions):
        return runner.settle(predictions, self.outcomes, self.market_outcomes,
                             self.inputs, self.market, self.protocol, self.sources)

    def validate_outcomes(self, outcomes=None, market_outcomes=None):
        validator.validate_outcomes(outcomes or self.outcomes, market_outcomes or self.market_outcomes,
                                    self.inputs, self.protocol, self.sources, self.market)

    def test_same_cutoff_and_source_availability_are_enforced(self):
        mutated = deepcopy(self.inputs)
        mutated["t0"] = "2024-02-24T21:00:00Z"
        with self.assertRaises(validator.ValidationError):
            validator.validate_inputs(mutated, self.market, self.protocol, self.sources)
        mutated = deepcopy(self.inputs)
        mutated["records"][0]["known_available_at"] = "2024-02-24T00:00:00Z"
        with self.assertRaises(validator.ValidationError):
            validator.validate_inputs(mutated, self.market, self.protocol, self.sources)

    def test_future_source_metadata_cannot_be_hidden_by_record_timestamp(self):
        sources = deepcopy(self.sources)
        source = next(x for x in sources["sources"] if x["source_id"] == "nvda_t0")
        source["known_available_at"] = "2024-03-01T00:00:00Z"
        with self.assertRaises(validator.ValidationError):
            validator.validate_inputs(self.inputs, self.market, self.protocol, sources)

    def test_share_cashflow_arithmetic_cannot_be_silently_changed(self):
        mutated = deepcopy(self.inputs)
        mutated["records"][0]["fiscal_year"]["diluted_weighted_average_shares_million"] *= 10
        with self.assertRaises(validator.ValidationError):
            validator.validate_inputs(mutated, self.market, self.protocol, self.sources)

    def test_AMD_nonGAAP_is_never_substituted_for_missing_GAAP(self):
        predictions, _ = self.prepare()
        amd = next(r for r in predictions["rows"] if r["ticker"] == "AMD")
        self.assertIsNone(amd["versions"]["C"]["gaap_gross_margin_ratio"])
        self.assertEqual(amd["versions"]["A"]["gaap_gross_margin_ratio"], .47)
        result = self.settle(predictions)
        self.assertEqual(result["financial_metrics"]["C"]["gaap_margin_common_sample"], ["NVDA", "INTC"])
        self.assertAlmostEqual(result["financial_metrics"]["A"]["gaap_gross_margin_mae_pp_common_sample"], 3.55)
        self.assertAlmostEqual(result["financial_metrics"]["C"]["gaap_gross_margin_mae_pp_common_sample"], 1.20)

    def test_operating_scores_match_independent_official_data_replay(self):
        predictions, _ = self.prepare()
        result = self.settle(predictions)
        self.assertAlmostEqual(result["financial_metrics"]["A"]["revenue_mape_percent"], 16.3030213863, places=8)
        self.assertAlmostEqual(result["financial_metrics"]["C"]["revenue_mape_percent"], 3.1235657669, places=8)
        self.assertEqual(result["guidance_interval_hits"], 2)
        self.assertEqual(result["guidance_interval_n"], 3)

    def test_strong_control_prevents_guidance_improvement_being_called_narrative_gain(self):
        predictions, _ = self.prepare()
        for row in predictions["rows"]:
            self.assertEqual(row["versions"]["A"], row["versions"]["B"])
            self.assertEqual(row["versions"]["C"], row["versions"]["D"])
            self.assertEqual(row["versions"]["C"], row["issuer_guidance_only_control"])
        result = self.settle(predictions)
        self.assertEqual(result["financial_metrics"]["C"], result["issuer_guidance_only_control"])
        self.assertEqual(result["incremental_numeric_operating_gain_over_issuer_guidance"], 0)

    def test_late_NVIDIA_release_cannot_confirm_earlier_market_window(self):
        predictions, _ = self.prepare()
        result = self.settle(predictions)
        nvda = next(r for r in result["engine_settlements"] if r["ticker"] == "NVDA" and r["primary_engine"] == "ENG-R")
        self.assertEqual(nvda["expiry_date"], "2024-05-20")
        self.assertFalse(nvda["issuer_outcome_available_by_expiry"])
        self.assertIsNone(nvda["issuer_realization_by_expiry"])
        intel = next(r for r in result["engine_settlements"] if r["ticker"] == "INTC" and r["primary_engine"] == "ENG-R")
        self.assertTrue(intel["issuer_outcome_available_by_expiry"])

    def test_one_sided_momentum_rule_reports_abstention_and_signal_coverage(self):
        predictions, _ = self.prepare()
        result = self.settle(predictions)
        forecasts = {r["ticker"]: r["momentum"]["forecast"] for r in predictions["rows"]}
        self.assertEqual(forecasts, {"NVDA": "positive_excess", "AMD": "abstain", "INTC": "abstain"})
        for summary in result["momentum_signal_summary"].values():
            self.assertEqual((summary["issued_n"], summary["eligible_universe_n"]), (1, 3))
        self.assertTrue(all(r["momentum_direction_hit"] is None for r in result["market_rows"] if r["ticker"] != "NVDA"))

    def test_outcome_period_provenance_and_duplicate_prices_are_rejected(self):
        outcome = deepcopy(self.outcomes)
        outcome["records"][0]["target_period_label"] = "FY2026_Q1"
        with self.assertRaises(validator.ValidationError):
            self.validate_outcomes(outcomes=outcome)
        for mutate in (
            lambda packet: packet["observations"].append(deepcopy(packet["observations"][0])),
            lambda packet: packet["observations"][0]["horizons"][0].update(close=math.nan),
            lambda packet: packet["observations"][0].update(price_basis="unadjusted_mixed_units"),
        ):
            market = deepcopy(self.market_outcomes)
            mutate(market)
            with self.assertRaises(validator.ValidationError):
                self.validate_outcomes(market_outcomes=market)

    def test_objects_use_existing_schemas_and_no_engine_is_automatically_qualified(self):
        _, objects = self.prepare()
        validator.validate_generated(objects)
        self.assertEqual(len(objects["targets"]), 3)
        self.assertEqual(len(objects["engine_theses"]), 9)
        self.assertTrue(all(t["lifecycle"]["status"] == "draft" for t in objects["engine_theses"]))
        states = {x["target_id"]: x for x in objects["capability_results"]}
        self.assertEqual(states["RT-EN-INTC"]["status"], "unknown")
        self.assertEqual(states["RT-EN-INTC"]["state"]["identification_status"], "unsupported")
        self.assertEqual(states["RT-EN-NVDA"]["status"], "partial")

    def test_empty_or_miswired_objects_and_forged_canon_hash_do_not_pass(self):
        _, objects = self.prepare()
        empty = {key: [] for key in objects}
        with self.assertRaises(validator.ValidationError):
            validator.validate_generated(empty)
        for mutate in (
            lambda x: x["capability_results"][0].update(target_id="RT-EN-AMD"),
            lambda x: x["research_receipts"][0]["invocation_envelope"].update(canon_hash="sha256:" + "0" * 64),
            lambda x: x["input_bundles"][0].update(pit_status="qualified"),
            lambda x: x["capability_results"][0].update(status="success"),
        ):
            modified = deepcopy(objects)
            mutate(modified)
            with self.assertRaises(validator.ValidationError):
                validator.validate_generated(modified)

    def test_prohibited_action_fields_are_rejected_even_when_nested(self):
        with self.assertRaises(validator.ValidationError):
            validator.validate_no_action_fields({"state": {"unexpected": [{"position_size": .2}]}})

    def temporary_pack(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        pack = Path(temp.name) / "candidate"
        shutil.copytree(PACK, pack, ignore=shutil.ignore_patterns("__pycache__"))
        return pack

    def test_prepare_runs_with_both_outcome_packets_physically_absent(self):
        pack = self.temporary_pack()
        for name in ("financial-outcomes.json", "market-outcomes.json"):
            (pack / "benchmark" / name).unlink()
        prepared, _ = runner.prepare_phase(pack)
        expected, _ = self.prepare()
        self.assertEqual(prepared["rows"], expected["rows"])

    def test_freezes_detect_changed_rules_and_saved_predictions(self):
        pack = self.temporary_pack()
        runner.prepare_phase(pack)
        saved = validator.read(pack / "benchmark/predictions.json")
        saved["rows"][0]["versions"]["C"]["revenue_usd_million"] = 26044
        runner.write_json(pack / "benchmark/predictions.json", saved)
        with self.assertRaises(validator.ValidationError):
            runner.settle_phase(pack)
        settings = validator.read(pack / "settings.json")
        settings["discount_rates"] = [.07]
        runner.write_json(pack / "settings.json", settings)
        with self.assertRaises(validator.ValidationError):
            runner.prepare_phase(pack)

    def test_full_replay_reconciles_hashes_and_carries_research_only_receipt(self):
        pack = self.temporary_pack()
        runner.prepare_phase(pack)
        runner.settle_phase(pack)
        receipt = validator.read(pack / "receipts/run-receipt.json")
        self.assertEqual(receipt["results_sha256"], validator.digest(pack / "benchmark/results.json"))
        self.assertFalse(receipt["canon_or_registry_promotion"])
        self.assertFalse(receipt["original_hypotheses_empirically_qualified"])


if __name__ == "__main__":
    unittest.main()
