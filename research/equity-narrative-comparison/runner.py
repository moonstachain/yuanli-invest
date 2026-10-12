"""Reproducible, retrospective research diagnostics; no execution authority.

prepare reads T0 numerical packets and audit metadata, never outcome packets.
settle verifies the saved prediction freeze before reading outcomes.
The analyst already knew these historical outcomes: this is not a blind study.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics

from model import cashflow_bridge, cashflow_pv, implied_region
from validator import (BASE_REVISION, PACK, ROOT, ValidationError, canonical_hash,
                       digest, read, validate_generated, validate_inputs,
                       validate_no_action_fields, validate_numeric,
                       validate_outcomes, validate_profile, verify_data_freeze,
                       verify_rule_freeze)

CAP_SPEC = "docs/architecture/r2_3b1/CAP-V-01-SPEC-v0.1.json"
PREPARATION_FILES = (
    "benchmark/financial-inputs.json", "benchmark/market-inputs.json",
    "benchmark/protocol.json", "benchmark/sources.json", "settings.json",
    "profile.json", "model.py", "runner.py", "validator.py",
)
NAMES = {"NVDA": "NVIDIA Corporation", "AMD": "Advanced Micro Devices, Inc.",
         "INTC": "Intel Corporation"}
AUTHORITIES = {"capital_authority": False, "portfolio_weight_authority": False,
               "trading_authority": False, "live_execution_authority": False}
ENGINE_TEXT = {
    "C": {
        "return": "cash_flow_compounding_from_reinvestment_above_capital_cost",
        "statement": "若持续价值获取与增量资本回报得到验证，再投资可形成现金流复利。",
        "mechanism": "经营现金生成、必要再投资与单位股权现金流增长；本轮一季数据不证明长期复利。",
        "falsifiers": ["增量资本回报持续低于资本成本", "增长依赖不可持续融资或股权稀释",
                       "原定价值获取机制被可核实的竞争证据推翻"],
    },
    "R": {
        "return": "repricing_from_independently_evidenced_expectation_revision",
        "statement": "若有带时间戳的预期变化、独立扩散证据和相符的价格反应，可检验预期重估机制。",
        "mechanism": "经营信息改变市场预期，并通过独立可观测的传播或持仓渠道进入价格。",
        "falsifiers": ["60 个交易日内未补齐独立预期变化与扩散证据",
                       "价格变化可由共同市场因子或折现变化解释且无增量预期证据",
                       "经营兑现与原假说方向矛盾；缺失披露保留未知"],
    },
    "X": {
        "return": "instrument_specific_convex_payoff_under_declared_tail_condition",
        "statement": "只有确定工具、成本、到期日和非线性收益结构后，才能研究凸性来源。",
        "mechanism": "工具的收益几何与尾部情景共同决定凸性；普通股票上涨潜力不构成工具证据。",
        "falsifiers": ["成本或融资要求破坏原收益不对称", "到期前尾部条件未出现",
                       "实际工具收益结构不具备所声称的凸性"],
    },
}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def pct_change(end, start):
    return end / start - 1


def prepare(financial, market, protocol, settings, profile, sources):
    """Pure preparation: the signature deliberately has no outcomes argument."""
    validate_inputs(financial, market, protocol, sources)
    validate_profile(profile)
    cutoff = protocol["as_of"]
    # The thesis declaration happened in 2026; historical evidence cutoff is separate.
    declared_at = protocol["frozen_at"]
    market_index = {r["symbol"]: r for r in market["observations"]}
    source_index = {s["source_id"]: s for s in sources["sources"]}
    benchmark = market_index[protocol["market_benchmark"]]
    benchmark_momentum = pct_change(benchmark["t0"]["close"], benchmark["lookback"]["close"])
    bundle = {key: [] for key in ("targets", "engine_theses", "invocations",
                                  "input_bundles", "capability_results", "research_receipts")}
    bundle["falsifier_registry"] = []
    predictions = {
        "protocol_id": protocol["protocol_id"], "as_of": cutoff,
        "thesis_declared_at": declared_at, "study_type": protocol["study_type"],
        "historically_preregistered": False, "historical_outcomes_already_public": True,
        "source_vintage": "current_archive_reconstruction",
        "classification_rule": "positive_prior_excess_only; otherwise abstain",
        "classification_note": "The frozen one-sided momentum rule does not authorize a negative-return forecast.",
        "financial_prediction_origin": "lagged_actual_or_issuer_guidance_no_narrative_fitted_coefficient",
        "performance_claim_authority": "none", "rows": [],
    }
    for row in financial["records"]:
        symbol = row["ticker"]
        price = market_index[symbol]
        fy, quarter, guide = row["fiscal_year"], row["latest_quarter"], row["guidance"]
        source_url = source_index[row["input_source_id"]]["url"]
        target_id = "RT-EN-" + symbol
        request_id, result_id = "RUN-EN-V-" + symbol, "RESULT-EN-V-" + symbol
        bundle_id = "BUNDLE-EN-V-" + symbol
        observations = [{"observation_type": "issuer_financials", "record": deepcopy(row)},
                        {"observation_type": "historical_price", "record": deepcopy(price)}]
        input_hash = "sha256:" + canonical_hash(observations)
        per_share_cf = fy["ocf_minus_cash_capital_purchases_proxy_usd_per_annual_diluted_share"]
        converted_price = price["t0"]["close"] * price["reported_T0_price_unit_factor"]
        region = implied_region(converted_price, per_share_cf, settings)
        region.update({
            "as_of": cutoff, "research_only": True,
            "evidence_refs": [source_url, price["source_url"]],
            "cashflow_definition": settings["cashflow_proxy_caveat"],
            "share_basis": settings["share_basis_caveat"],
            "price_unit_conversion": price["unit_conversion_caveat"],
            "model_scope": "conditional_cashflow_growth_not_separately_identified_revenue_margin_or_duration",
            "reinvestment_assumption": "cashflow_growth_is_after_all_required_reinvestment; proxy_does_not_establish_this",
            "discount_semantics": "declared_equity_discount_sensitivity_not_estimated_cost_of_equity",
            "next_evidence_date": protocol["financial_settlement_deadline"],
        })
        for n in (5, 10, 15):
            if not any(r["horizon_years"] == n for r in region["assumption_regions"]):
                raise ValidationError("required duration sensitivity absent")
        legacy_eps = fy["gaap_diluted_eps_usd"]
        valuation = {
            "reported_unit_price": converted_price,
            "reported_annual_diluted_eps": legacy_eps,
            "trailing_reported_pe": converted_price / legacy_eps if legacy_eps > 0 else None,
            "annual_cashflow_proxy_per_annual_diluted_share": per_share_cf,
            "price_to_cashflow_proxy": converted_price / per_share_cf if per_share_cf > 0 else None,
            "ratio_authority": "descriptive_proxy_not_current_share_count_normalized_valuation",
        }
        momentum = pct_change(price["t0"]["close"], price["lookback"]["close"])
        excess = momentum - benchmark_momentum
        a = {"revenue_usd_million": quarter["revenue_usd_million"],
             "gaap_gross_margin_ratio": quarter["gaap_gross_margin_ratio"],
             "basis": "prior_reported_quarter_unchanged"}
        c = {"revenue_usd_million": guide["revenue_mid_usd_million"],
             "gaap_gross_margin_ratio": guide["gaap_gross_margin_mid_ratio"],
             "basis": "issuer_guidance_GAAP_only",
             "missing_margin_reason": ("issuer_only_provided_nonGAAP_guidance"
                                      if guide["gaap_gross_margin_mid_ratio"] is None else None)}
        operating_cases = []
        for label, part in zip(settings["three_scenario_labels"], ("low", "mid", "high")):
            operating_cases.append({
                "scenario_id": symbol + "-" + label,
                "joint_operating_assumptions": {
                    "quarterly_revenue_usd_million": guide[f"revenue_{part}_usd_million"],
                    "gaap_gross_margin_ratio": guide.get(f"gaap_gross_margin_{part}_ratio"),
                    "operating_margin": None, "reinvestment": None, "equity_cashflow": None,
                },
                "discount_assumptions": "separate_declared_sensitivity_grid_not_a_joint_forecast",
                "dependencies": ["issuer_guidance_context", "consistent_GAAP_basis",
                                 "full_cashflow_bridge_missing"],
                "required_conditions": ["must_complete_operating_and_financing_bridge_before_full_DCF"],
                "confirming_evidence_refs": [source_url],
                "contradicting_evidence_refs": [],
                "falsifiers": ["joint_assumptions_fail_to_reconcile_with_subsequent_original_disclosure"],
                "next_observation_at": protocol["financial_settlement_deadline"],
                "expiry_at": protocol["financial_settlement_deadline"],
                "status": "incomplete_scenario_card",
                "semantics": "guidance_endpoint_sensitivity_not_issuer_joint_probability_or_loss_floor",
            })
        engine_candidates = {
            "C": {"status": "draft", "positive_cashflow_proxy": per_share_cf > 0,
                  "missing": ["multi_period_ROIC_and_reinvestment", "durable_value_capture"],
                  "single_quarter_can_qualify": False},
            "R": {"status": "draft",
                  "missing": ["dated_expectation_change", "independent_diffusion_or_positioning"],
                  "price_alone_can_qualify": False},
            "X": {"status": "draft", "missing": list(protocol["engine_rules"]["X"]["required_evidence"]),
                  "ordinary_equity_upside_can_qualify": False},
        }
        predictions["rows"].append({
            "ticker": symbol, "target_id": target_id, "target_period_label": guide["target_period_label"],
            "source_refs": [source_url], "valuation_baseline": valuation,
            "versions": {"A": deepcopy(a), "B": deepcopy(a), "C": deepcopy(c), "D": deepcopy(c)},
            "issuer_guidance_only_control": deepcopy(c),
            "guidance_interval_usd_million": [guide["revenue_low_usd_million"], guide["revenue_high_usd_million"]],
            "momentum": {"lookback_sessions": protocol["momentum_lookback_sessions"],
                         "price_return": momentum, "benchmark_price_return": benchmark_momentum,
                         "excess_price_return": excess,
                         "forecast": "positive_excess" if excess > 0 else "abstain"},
            "valuation_state_ref": result_id, "valuation_identification_status": region["identification_status"],
            "conditional_cashflow_growth_range": region["conditional_growth_range"],
            "operating_scenarios": operating_cases, "engine_candidates": engine_candidates,
            "t0_risks_and_gaps": row["t0_risks_and_gaps"],
        })
        bundle["targets"].append({
            "target_id": target_id, "schema_version": "2.0.0", "target_type": "company",
            "canonical_name": NAMES[symbol], "asset_form": "listed_common_equity",
            "primary_market": "NASDAQ", "currency": "USD", "identifiers": {"ticker": symbol},
            "active_status": "candidate", "created_at": declared_at,
            "authority": {"thesis_authority": False, "capital_authority": False, "trading_authority": False},
        })
        bundle["invocations"].append({
            "request_id": request_id, "capability_id": "CAP-V-01", "capability_version": "0.1.0",
            "target_id": target_id, "as_of": cutoff, "runtime": "reference_quant",
            "input_mode": "provided", "strict_pit": True,
            "parameters": {"profile_id": profile["profile_id"], "input_vintage_mode": "reconstructed",
                           "diagnostics_only_when_PIT_provisional": True},
            "requested_output_schema": "PriceImpliedExpectationState",
        })
        bundle["input_bundles"].append({
            "bundle_id": bundle_id, "request_id": request_id, "capability_id": "CAP-V-01",
            "target_id": target_id, "as_of": cutoff, "observations": observations,
            "input_manifest_hash": input_hash, "pit_status": "provisional",
            "warnings": ["Current historical archives are not an original T0 vintage.",
                         "Price close publication latency and adjustment vintage are not historically attested."],
        })
        bundle["capability_results"].append({
            "result_id": result_id, "request_id": request_id, "capability_id": "CAP-V-01",
            "target_id": target_id, "as_of": cutoff,
            "status": "partial" if region["solution_count"] else "unknown",
            "metrics": {"conditional_grid_solutions": region["solution_count"]},
            "state": region,
            "uncertainty": {"pit_status": "provisional", "probabilities_calibrated": False,
                            "missing_normalized_cashflow_and_T0_share_count": True},
            "counterevidence": row["t0_risks_and_gaps"],
            "falsifiers": ["pricing_identity_does_not_reconcile",
                          "cashflow_proxy_cannot_be_reconciled_to_equity_cashflows",
                          "input_unavailable_at_as_of"],
            "warnings": ["Research diagnostics only; strict-PIT qualification has not been met."],
            "prohibited_action_fields_absent": True,
        })
        for engine in ("C", "R", "X"):
            spec = ENGINE_TEXT[engine]
            thesis_id = f"ET-EN-{symbol}-{engine}"
            falsifier_refs = []
            for index, condition in enumerate(spec["falsifiers"], 1):
                ref = f"EN-FALSIFIER-{symbol}-{engine}-{index:02d}"
                falsifier_refs.append(ref)
                bundle["falsifier_registry"].append({"falsifier_id": ref, "condition": condition})
            bundle["engine_theses"].append({
                "engine_thesis_id": thesis_id, "schema_version": "1.0.0", "target_id": target_id,
                "identity_core": {"primary_engine": "ENG-" + engine,
                                  "thesis_origin": "2026_retrospective_candidate_not_a_2024_opened_thesis",
                                  "opened_at": declared_at},
                "research_contract": {
                    "source_of_return": [spec["return"]],
                    "time_horizon": protocol["engine_rules"][engine]["horizon"],
                    "thesis_statement": symbol + "：" + spec["statement"],
                    "causal_mechanism": spec["mechanism"],
                    "price_semantics": "conditional_implied_region_and_separate_observed_price_evidence",
                },
                "evidence": {"supporting_refs": [source_url] if engine != "X" else [],
                             "counter_refs": [source_url],
                             "capability_output_refs": [result_id], "primitive_state_refs": [],
                             "recorded_at": financial["created_at"], "known_as_of": cutoff,
                             "knowledge_cutoff": cutoff, "replay_cutoff": cutoff},
                "falsification": {"falsifier_refs": falsifier_refs,
                                  "challenge_conditions": spec["falsifiers"]},
                "lifecycle": {"status": "draft", "revision": 1,
                              "as_of": declared_at, "valid_from": declared_at,
                              "revision_reason": "Initial retrospective evidence-gap candidate; no promotion."},
                "authority": deepcopy(AUTHORITIES),
            })
        bundle["research_receipts"].append({
            "request_id": request_id, "result_id": result_id,
            "invocation_envelope": {
                "canon_revision": BASE_REVISION, "canon_hash": "sha256:" + digest(ROOT / CAP_SPEC),
                "capability_id": "CAP-V-01", "capability_contract_version": "0.1.0",
                "research_target": target_id, "A0_asset_form": "listed_common_equity",
                "A1_pricing_archetype": "corporate_equity_cashflow_claim",
                "as_of": cutoff, "evidence_cutoff": cutoff, "provider_runtime": "reference_quant",
            },
            "canon_hash_basis": CAP_SPEC,
            "profile_id": profile["profile_id"], "profile_version": "0.1.0",
            "engine_thesis_id": f"ET-EN-{symbol}-C", "primary_engine": "ENG-C",
            "consumer_thesis_refs": [f"ET-EN-{symbol}-{e}" for e in ("C", "R", "X")],
            "model_version": "0.1.0", "assumption_set_id": protocol["protocol_id"],
            "price_snapshot_id": "RECONSTRUCTED-20240223-" + symbol,
            "algorithm_family": "finite_equity_cashflow_inversion",
            "evidence_refs": [source_url, price["source_url"]],
            "output_state_version": "0.1.0",
            "degrade_state": ["research_only", region["identification_status"], "insufficient_evidence"],
            "input_snapshot_hash": input_hash, "assumption_version": "settings.json",
            "identification_status": region["identification_status"],
            "parameter_region_ref": result_id + "#state.assumption_regions",
            "next_evidence_date": protocol["financial_settlement_deadline"],
            "original_thesis_settlement_status": "draft_reconstructed_not_historical",
        })
    validate_generated(bundle)
    validate_numeric(predictions)
    validate_no_action_fields(predictions)
    return predictions, bundle


def synthetic_operating_bridge():
    """Arithmetic demonstration only; these are invented inputs, not forecasts."""
    examples = []
    for label, growth, margin in (("conservative", .03, .15),
                                 ("base", .08, .20), ("optimistic", .13, .25)):
        previous_revenue, rows, cashflows = 1000.0, [], []
        for year in range(1, 6):
            revenue = previous_revenue * (1 + growth)
            inputs = {"revenue": revenue, "operating_margin": margin,
                      "cash_interest": 10.0, "cash_taxes": (revenue * margin - 10) * .25,
                      "depreciation_amortization": revenue * .03, "capex": revenue * .05,
                      "delta_working_capital": (revenue - previous_revenue) * .10,
                      "net_borrowing": 0.0}
            output = cashflow_bridge(inputs)
            rows.append({"year": year, "inputs": inputs, "output": output})
            cashflows.append(output["equity_cash_flow"])
            previous_revenue = revenue
        examples.append({
            "scenario_id": "SYNTHETIC-" + label, "invented_data": True,
            "joint_assumptions": {"annual_revenue_growth": growth, "operating_margin": margin,
                                  "cash_tax_rate_on_positive_post_interest_profit": .25,
                                  "depreciation_to_revenue": .03, "capex_to_revenue": .05,
                                  "incremental_working_capital_to_revenue_change": .10},
            "years": rows, "discount_rate": .10, "terminal_growth": 0.0,
            "internal_pv_identity_in_synthetic_money_units": cashflow_pv(cashflows, .10, 0),
            "evidence_status": "synthetic_arithmetic_check_not_empirical_validation",
        })
    return {"status": "synthetic_only", "scenarios": examples}


def settle(predictions, outcomes, market_outcomes, financial, market_inputs, protocol, sources):
    validate_outcomes(outcomes, market_outcomes, financial, protocol, sources, market_inputs)
    actuals = {x["ticker"]: x for x in outcomes["records"]}
    market_start = {x["symbol"]: x for x in market_inputs["observations"]}
    market_end = {x["symbol"]: x for x in market_outcomes["observations"]}
    common_margin = [r["ticker"] for r in predictions["rows"]
                     if all(r["versions"][v]["gaap_gross_margin_ratio"] is not None for v in "ABCD")]
    financial_rows, market_rows, engine_rows = [], [], []
    for prediction in predictions["rows"]:
        symbol = prediction["ticker"]
        actual = actuals[symbol]
        version_errors = {}
        for version in "ABCD":
            forecast = prediction["versions"][version]
            version_errors[version] = {
                "revenue_ape_percent": abs(forecast["revenue_usd_million"] - actual["revenue_usd_million"])
                                       / actual["revenue_usd_million"] * 100,
                "gaap_margin_error_pp": (abs(forecast["gaap_gross_margin_ratio"] - actual["gaap_gross_margin_ratio"]) * 100
                                          if forecast["gaap_gross_margin_ratio"] is not None else None),
            }
        low, high = prediction["guidance_interval_usd_million"]
        financial_rows.append({
            "ticker": symbol, "target_period_label": actual["target_period_label"],
            "actual_revenue_usd_million": actual["revenue_usd_million"],
            "actual_gaap_gross_margin_ratio": actual["gaap_gross_margin_ratio"],
            "outcome_published_date": actual["published_date"],
            "version_errors": version_errors,
            "guidance_interval_hit": low <= actual["revenue_usd_million"] <= high,
            "margin_common_sample": symbol in common_margin,
            "outcome_source_id": actual["source_id"],
        })
        market60 = None
        for horizon in market_end[symbol]["horizons"]:
            bench = next(h for h in market_end[protocol["market_benchmark"]]["horizons"]
                         if h["sessions"] == horizon["sessions"])
            stock_return = pct_change(horizon["close"], market_start[symbol]["t0"]["close"])
            benchmark_return = pct_change(bench["close"], market_start[protocol["market_benchmark"]]["t0"]["close"])
            excess = stock_return - benchmark_return
            issued = prediction["momentum"]["forecast"] == "positive_excess"
            observation = {
                "ticker": symbol, "sessions": horizon["sessions"], "settled_date": horizon["date"],
                "price_return_percent": stock_return * 100,
                "benchmark_price_return_percent": benchmark_return * 100,
                "excess_price_return_pp": excess * 100,
                "momentum_forecast": prediction["momentum"]["forecast"],
                "momentum_direction_hit": excess > 0 if issued else None,
                "issuer_outcome_available_by_market_settlement": actual["published_date"] < horizon["date"],
                "availability_rule": "day_precision_same_day_is_not_assumed_available_at_close",
                "return_basis": protocol["market_return_convention"],
            }
            market_rows.append(observation)
            if horizon["sessions"] == 60:
                market60 = observation
        engine_rows.extend([
            {"ticker": symbol, "primary_engine": "ENG-C",
             "status": "not_settled_long_horizon_and_evidence_gaps",
             "missing": prediction["engine_candidates"]["C"]["missing"],
             "positive_cashflow_proxy": prediction["engine_candidates"]["C"]["positive_cashflow_proxy"],
             "quarterly_revenue_outcome_is_long_term_confirmation": False},
            {"ticker": symbol, "primary_engine": "ENG-R",
             "status": "not_qualified_missing_independent_expectation_and_diffusion_evidence",
             "missing": prediction["engine_candidates"]["R"]["missing"],
             "expiry_date": market60["settled_date"],
             "expiry_receipt": "required_confirmation_not_completed",
             "issuer_outcome_available_by_expiry": market60["issuer_outcome_available_by_market_settlement"],
             "issuer_realization_by_expiry": actual["revenue_usd_million"]
                                             if market60["issuer_outcome_available_by_market_settlement"] else None,
             "positive_excess_price_observed": market60["excess_price_return_pp"] > 0,
             "price_alone_confirms_engine": False},
            {"ticker": symbol, "primary_engine": "ENG-X",
             "status": "unsupported_missing_instrument_and_payoff_inputs",
             "missing": prediction["engine_candidates"]["X"]["missing"]},
        ])
    metrics = {}
    for version in "ABCD":
        metrics[version] = {
            "revenue_mape_percent": statistics.mean(r["version_errors"][version]["revenue_ape_percent"] for r in financial_rows),
            "revenue_sample_n": len(financial_rows),
            "gaap_gross_margin_mae_pp_common_sample": statistics.mean(
                r["version_errors"][version]["gaap_margin_error_pp"] for r in financial_rows if r["margin_common_sample"]),
            "gaap_margin_common_sample": common_margin,
            "gaap_margin_available_n": sum(r["version_errors"][version]["gaap_margin_error_pp"] is not None for r in financial_rows),
        }
    hits = {}
    for horizon in protocol["market_horizons_sessions"]:
        signaled = [r for r in market_rows if r["sessions"] == horizon and r["momentum_direction_hit"] is not None]
        hits[str(horizon)] = {"issued_n": len(signaled), "eligible_universe_n": len(predictions["rows"]),
                             "hits": sum(r["momentum_direction_hit"] for r in signaled),
                             "interpretation": "descriptive_single_positive_signal_not_an_accuracy_estimate"}
    results = {
        "protocol_id": protocol["protocol_id"], "as_of": protocol["as_of"],
        "study_type": "retrospective_mechanism_replay", "performance_claim_authority": "none",
        "financial_metrics": metrics,
        "issuer_guidance_only_control": deepcopy(metrics["C"]),
        "incremental_numeric_operating_gain_over_issuer_guidance": 0.0,
        "guidance_interval_hits": sum(r["guidance_interval_hit"] for r in financial_rows),
        "guidance_interval_n": len(financial_rows),
        "operating_rows": financial_rows, "market_rows": market_rows,
        "momentum_signal_summary": hits, "engine_settlements": engine_rows,
        "local_hypothesis_status": {
            "EN-HYP-1": "not_empirically_qualified_synthetic_identity_only",
            "EN-HYP-2": "not_tested_no_multi_period_incremental_capital_return",
            "EN-HYP-3": "not_tested_no_independent_diffusion_series",
        },
        "interpretation": [
            "A/B and C/D have identical operating forecasts within their pair.",
            "The observed operating improvement is already achieved by issuer guidance alone.",
            "The valuation grid describes assumption sensitivity, not predictive increment.",
            "D adds auditable evidence gaps and expiry receipts, not a better fitted forecast.",
            "No out-of-sample, causal, statistical significance, total-return or executable strategy claim.",
        ],
    }
    validate_numeric(results)
    validate_no_action_fields(results)
    return results


def report_markdown(predictions, results):
    by_symbol = {x["ticker"]: x for x in predictions["rows"]}
    lines = [
        "# 首轮叙事经济学 × 原力投研研究回放",
        "",
        "本轮完成模板、C/R/X 独立候选假说和可复算的真实数据对照。研究状态为候选；没有样本外收益证明。",
        "",
        "## 信息边界",
        "",
        "- 统一 T0：2024-02-23 21:00 UTC（美东收盘）；财务结算截止：2024-05-31。",
        "- 研究与规则记录于 2026 年，使用当前档案重建；历史结果早已公开。",
        "- 20 / 60 交易日价格窗口分别截至 2024-03-22 / 2024-05-20。",
        "- NVIDIA 2024-05-22 财报晚于 60 日窗口，未进入该窗口的 R 经营确认。",
        "",
        "## 经营预测对照",
        "",
        "单位：百万美元。A/B 使用上一季度持平；C/D 使用发行人指引中值。",
        "",
        "| 公司 | A/B 预测 | C/D 与指引强基准 | 实际 | A/B 误差 | C/D 误差 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in results["operating_rows"]:
        p = by_symbol[row["ticker"]]
        lines.append(f'| {row["ticker"]} | {p["versions"]["A"]["revenue_usd_million"]:,} | '
                     f'{p["versions"]["C"]["revenue_usd_million"]:,} | {row["actual_revenue_usd_million"]:,} | '
                     f'{row["version_errors"]["A"]["revenue_ape_percent"]:.4f}% | '
                     f'{row["version_errors"]["C"]["revenue_ape_percent"]:.4f}% |')
    a, c = results["financial_metrics"]["A"], results["financial_metrics"]["C"]
    lines += [
        "",
        f'三家公司营收 MAPE：A/B 为 {a["revenue_mape_percent"]:.4f}%，C/D 为 {c["revenue_mape_percent"]:.4f}%。',
        f'GAAP 毛利率共同样本为 NVDA、INTC：误差从 {a["gaap_gross_margin_mae_pp_common_sample"]:.2f} '
        f'降至 {c["gaap_gross_margin_mae_pp_common_sample"]:.2f} 个百分点。AMD 仅披露非 GAAP 指引，GAAP 字段保留缺失。',
        "",
        "**发行人指引单独实现了同样的改善；叙事层相对该强基准的数值增量为零。** 这里没有证明叙事 alpha。",
        "",
        "## 价格与简单动量",
        "",
        "仅报告不含股息和费用的拆股调整收盘价收益；超额为股票价格收益减 SPY 价格收益，单位为百分点。",
        "",
        "| 公司 | 窗口 | 价格收益 | 相对 SPY | T0 动量规则 |",
        "|---|---:|---:|---:|---|",
    ]
    for row in results["market_rows"]:
        label = "正超额信号" if row["momentum_forecast"] == "positive_excess" else "未发出正超额预测"
        lines.append(f'| {row["ticker"]} | {row["sessions"]} 日 | {row["price_return_percent"]:.2f}% | '
                     f'{row["excess_price_return_pp"]:+.2f} | {label} |')
    lines += [
        "",
        "冻结规则只声明正动量的正超额预测；非正动量保持 abstain。正信号覆盖 1/3，两个窗口各为 1/1 命中，不能称为胜率或统计验证。",
        "",
        "## 价格隐含预期",
        "",
        "每家公司检查 54 组折现率、持续期、终值增长率与现金流尺度的联合条件。区间是敏感性范围，没有概率含义。",
        "",
        "| 公司 | 过去一年报表 PE 代理 | 隐含年现金流增长范围 | 状态 |",
        "|---|---:|---|---|",
    ]
    for p in predictions["rows"]:
        region = p["conditional_cashflow_growth_range"]
        display = f"{region[0] * 100:.2f}%—{region[1] * 100:.2f}%" if region else "不适用：起点现金流为负"
        pe = p["valuation_baseline"]["trailing_reported_pe"]
        pe_text = f"{pe:.2f}" if pe is not None else "缺失"
        lines.append(f'| {p["ticker"]} | {pe_text} | {display} | {p["valuation_identification_status"]} |')
    lines += [
        "",
        "现金流起点是经营现金流减现金资本购置的代理，未完成标准化 FCFE；股份采用年度加权平均稀释股数，不能当成 T0 精确股本。NVIDIA 的价格按原披露股份单位换算。",
        "",
        "## C / R / X 结算",
        "",
        "- C：三家公司均缺多期增量资本回报与持续价值获取证据，一季披露不能结算 3—5 年复利。",
        "- R：三家公司均缺独立的带时间戳预期变化与扩散/持仓证据，价格上涨不能单独补齐；保留到期未获必要确认的回执。",
        "- X：未提供具体工具、权利金、到期日和收益结构，全部 unsupported。",
        "",
        "D 的已实现作用是保存口径检查、未知状态和证伪期限。EN-HYP-1/2/3 没有获得经验验证或投研准入。",
        "",
        "## 证据与复算",
        "",
        "输入与结果分离；prepare 只读取 T0 数值包及来源审计元数据，写出预测与 hash 后，settle 才读取结果数值包。协议、参数、数据与代码 hash 均保留在回执中。",
        "这种流程隔离可以发现实现中的未来数据引用，但不能让已经知晓历史结果的研究者变成盲测。",
        "",
        "六份发行人官网来源、发布时间、原始字节 hash 和逐字段 locator 见 benchmark/sources.json 与 financial 输入/结果包；行情来源及重建日期见 market 输入/结果包。",
        "复算入口、契约关系和后续所需证据见同目录 README.md。所有数字均可由已提交的小型 JSON 数据包离线复算。",
        "",
    ]
    return "\n".join(lines)


def prepare_phase(pack=PACK):
    verify_rule_freeze(pack)
    verify_data_freeze(pack, include_outcomes=False)
    financial, market, protocol, settings, profile, sources = (
        read(pack / name) for name in ("benchmark/financial-inputs.json", "benchmark/market-inputs.json",
                                      "benchmark/protocol.json", "settings.json", "profile.json", "benchmark/sources.json"))
    predictions, objects = prepare(financial, market, protocol, settings, profile, sources)
    predictions["preparation_files"] = {name: digest(pack / name) for name in PREPARATION_FILES}
    write_json(pack / "benchmark/predictions.json", predictions)
    write_json(pack / "examples/generated-objects.json", objects)
    write_json(pack / "examples/synthetic-operating-bridge.json", synthetic_operating_bridge())
    freeze = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "predictions_sha256": digest(pack / "benchmark/predictions.json"),
        "generated_objects_sha256": digest(pack / "examples/generated-objects.json"),
        "prepare_reads_outcome_packets": False,
        "metadata_note": "Sources catalog contains provenance metadata for both phases, never outcome numerical facts.",
        "historical_researcher_blindness": False,
    }
    write_json(pack / "receipts/prediction-freeze.json", freeze)
    return predictions, objects


def settle_phase(pack=PACK):
    verify_rule_freeze(pack)
    freeze = read(pack / "receipts/prediction-freeze.json")
    for key, path in (("predictions_sha256", "benchmark/predictions.json"),
                      ("generated_objects_sha256", "examples/generated-objects.json")):
        if freeze[key] != digest(pack / path):
            raise ValidationError("saved predictions or objects changed after preparation")
    predictions = read(pack / "benchmark/predictions.json")
    for relative, expected in predictions["preparation_files"].items():
        if digest(pack / relative) != expected:
            raise ValidationError("preparation input or implementation changed; rerun prepare")
    objects = read(pack / "examples/generated-objects.json")
    validate_generated(objects)
    # Only after verifying prediction integrity do we read any outcome packet.
    verify_data_freeze(pack)
    results = settle(predictions, read(pack / "benchmark/financial-outcomes.json"),
                     read(pack / "benchmark/market-outcomes.json"),
                     read(pack / "benchmark/financial-inputs.json"),
                     read(pack / "benchmark/market-inputs.json"),
                     read(pack / "benchmark/protocol.json"), read(pack / "benchmark/sources.json"))
    results["predictions_sha256"] = freeze["predictions_sha256"]
    write_json(pack / "benchmark/results.json", results)
    (pack / "receipts/pilot-report.md").write_text(report_markdown(predictions, results), encoding="utf-8")
    receipt = {
        "settled_at": datetime.now(timezone.utc).isoformat(),
        "protocol_id": results["protocol_id"], "candidate_status": "implemented_research_only",
        "protocol_sha256": digest(pack / "benchmark/protocol.json"),
        "settings_sha256": digest(pack / "settings.json"),
        "data_freeze_sha256": digest(pack / "benchmark/data-freeze.json"),
        "predictions_sha256": freeze["predictions_sha256"],
        "results_sha256": digest(pack / "benchmark/results.json"),
        "generated_objects_sha256": freeze["generated_objects_sha256"],
        "rule_and_data_hashes_verified": True, "existing_contract_schemas_validated": True,
        "positive_historical_alpha_claim": False, "canon_or_registry_promotion": False,
        "original_hypotheses_empirically_qualified": False,
    }
    write_json(pack / "receipts/run-receipt.json", receipt)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "settle", "all"), default="all")
    args = parser.parse_args()
    if args.phase in ("prepare", "all"):
        predictions, objects = prepare_phase()
        print(json.dumps({"phase": "prepare", "targets": len(objects["targets"]),
                          "engine_theses": len(objects["engine_theses"]),
                          "prediction_sha256": digest(PACK / "benchmark/predictions.json")}))
    if args.phase in ("settle", "all"):
        results = settle_phase()
        print(json.dumps({"phase": "settle", "metrics": results["financial_metrics"],
                          "guidance_increment": results["incremental_numeric_operating_gain_over_issuer_guidance"],
                          "claim_authority": results["performance_claim_authority"]}))


if __name__ == "__main__":
    main()
