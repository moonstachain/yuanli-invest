"""Finite equity cash-flow models for a candidate CAP-V-01 research profile.

Pure functions only. No targets, trading instructions, fitted probabilities or
claim that an inverse price problem uniquely identifies market expectations.
"""
from __future__ import annotations

import math
from itertools import product


class ModelInputError(ValueError):
    pass


def number(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelInputError(f"{name}: finite numeric input required")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ModelInputError(f"{name}: invalid numeric domain") from exc
    if not math.isfinite(value) or (positive and value <= 0):
        raise ModelInputError(f"{name}: invalid numeric domain")
    return value


def finite_calculation(calculate, name):
    """Reject nonfinite derived values as well as nonfinite source values."""
    try:
        value = calculate()
    except (OverflowError, ZeroDivisionError, ValueError) as exc:
        raise ModelInputError(f"{name}: calculation outside finite numeric domain") from exc
    return number(value, name)


def discount_parameters(discount_rate, terminal_growth):
    r = number(discount_rate, "discount_rate", positive=True)
    terminal = number(terminal_growth, "terminal_growth")
    if terminal <= -1 or terminal >= r:
        raise ModelInputError("terminal growth must be greater than -1 and below discount rate")
    return r, terminal


def growth_bounds(bounds):
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ModelInputError("growth bracket must contain exactly two bounds")
    low, high = [number(x, "growth_bound") for x in bounds]
    if low <= -1 or low >= high:
        raise ModelInputError("invalid growth bracket")
    return low, high


def years_count(years):
    if isinstance(years, bool) or not isinstance(years, int) or not 1 <= years <= 50:
        raise ModelInputError("years must be an integer between 1 and 50")
    return years


def cashflow_bridge(row):
    """Same-currency monetary units; cash tax and net borrowing are explicit.

EBIT - cash interest - cash taxes + D&A - capex - change in working capital
     + net borrowing. Cash taxes are supplied, not invented tax-loss credits.
Stock compensation/dilution and other adjustments need separate disclosed data.
"""
    revenue = number(row["revenue"], "revenue", positive=True)
    margin = number(row["operating_margin"], "operating_margin")
    if not -1 <= margin <= 1:
        raise ModelInputError("operating_margin outside declared model range")
    fields = ("cash_interest", "cash_taxes", "depreciation_amortization", "capex",
              "delta_working_capital", "net_borrowing")
    values = {k: number(row[k], k) for k in fields}
    for k in ("cash_interest", "cash_taxes", "depreciation_amortization", "capex"):
        if values[k] < 0:
            raise ModelInputError(f"{k} must be nonnegative in this bridge")
    operating_profit = number(revenue * margin, "operating_profit")
    fcfe = finite_calculation(lambda: math.fsum((operating_profit, -values["cash_interest"],
            -values["cash_taxes"], values["depreciation_amortization"], -values["capex"],
            -values["delta_working_capital"], values["net_borrowing"])), "equity_cash_flow")
    return {"operating_profit": operating_profit, "equity_cash_flow": fcfe,
            "definition": "explicit_cash_tax_levered_cashflow_bridge"}


def cashflow_pv(cashflows, discount_rate, terminal_growth=0.0):
    """Internal valuation identity; terminal growth starts AFTER the last year."""
    years_count(len(cashflows))
    r, terminal = discount_parameters(discount_rate, terminal_growth)
    cfs = [number(v, "cashflow") for v in cashflows]
    explicit = finite_calculation(lambda: math.fsum(
        v / (1 + r) ** t for t, v in enumerate(cfs, 1)), "explicit_cashflow_pv")
    residual = finite_calculation(lambda: cfs[-1] * (1 + terminal) / (r - terminal)
        / (1 + r) ** len(cfs), "terminal_cashflow_pv")
    return number(explicit + residual, "cashflow_pv")


def growing_cashflows(base_cashflow, growth, years):
    base = number(base_cashflow, "base_cashflow", positive=True)
    g = number(growth, "growth")
    if g <= -1:
        raise ModelInputError("cashflow growth must exceed -1")
    years_count(years)
    cashflows = [finite_calculation(lambda t=t: base * (1 + g) ** t, "grown_cashflow")
                 for t in range(1, years + 1)]
    if any(cf <= 0 for cf in cashflows):
        raise ModelInputError("positive cash flow path underflowed numerical precision")
    return cashflows


def implied_growth(observed_equity_value, base_cashflow, years, discount_rate,
                   terminal_growth=0.0, bounds=(-0.9, 2.0)):
    """Solve one conditional parameter with a disclosed bracket; no clipping."""
    observed = number(observed_equity_value, "observed_equity_value", positive=True)
    base = number(base_cashflow, "base_cashflow")
    years_count(years)
    r, terminal = discount_parameters(discount_rate, terminal_growth)
    low, high = growth_bounds(bounds)
    if base <= 0:
        return {"status": "unsupported", "reason": "nonpositive_base_cashflow_requires_explicit_turnaround_path"}
    def value(g):
        return cashflow_pv(growing_cashflows(base, g, years), r, terminal)
    low_pv, high_pv = value(low), value(high)
    if not low_pv <= observed <= high_pv:
        return {"status": "outside_search_domain", "reason": "no_bracketed_solution",
                "growth_bounds": [low, high]}
    for _ in range(110):
        mid = low / 2 + high / 2
        if value(mid) < observed:
            low = mid
        else:
            high = mid
    g = low / 2 + high / 2
    residual = number(abs(value(g) - observed) / observed, "relative_identity_residual")
    if residual > 1e-8:
        raise ModelInputError("conditional solution failed numerical identity tolerance")
    return {"status": "conditional_solution", "annual_cashflow_growth": g,
            "terminal_cashflow_multiple": finite_calculation(
                lambda: (1 + g) ** years, "terminal_cashflow_multiple"),
            "relative_identity_residual": residual}


def implied_region(observed_equity_value, base_cashflow, settings):
    """A grid of joint assumptions, not a statistical confidence interval."""
    observed = number(observed_equity_value, "observed_equity_value", positive=True)
    base = number(base_cashflow, "base_cashflow")
    dimensions = ("discount_rates", "horizons_years", "terminal_growth_rates", "cashflow_scales")
    if not isinstance(settings, dict) or any(
            not isinstance(settings.get(k), (list, tuple)) or not settings[k] for k in dimensions):
        raise ModelInputError("every joint-assumption grid dimension must be nonempty")
    bounds = growth_bounds(settings.get("growth_search_bounds"))
    records = []
    for r, n, terminal, scale in product(settings["discount_rates"], settings["horizons_years"],
                                          settings["terminal_growth_rates"], settings["cashflow_scales"]):
        scale = number(scale, "cashflow_scale", positive=True)
        scaled_base = number(base * scale, "scaled_base_cashflow")
        if base != 0 and scaled_base == 0:
            raise ModelInputError("scaled cash flow underflowed numerical precision")
        result = implied_growth(observed, scaled_base, n, r, terminal, bounds)
        records.append({"discount_rate": r, "horizon_years": n, "terminal_growth": terminal,
                        "cashflow_scale": scale, **result})
    valid = [x for x in records if x["status"] == "conditional_solution"]
    return {"state_type": "PriceImpliedExpectationState", "model_family": "finite_equity_cashflow_inversion",
            "identification_status": "underidentified" if valid else "unsupported",
            "uncertainty_semantics": "joint_assumption_grid_not_probability_or_confidence_interval",
            "assumption_regions": records, "solution_count": len(valid),
            "conditional_growth_range": [min(x["annual_cashflow_growth"] for x in valid),
                                         max(x["annual_cashflow_growth"] for x in valid)] if valid else None}


def scenario_implied_margins(observed_equity_value, historical_cashflow, revenue_scenarios):
    """Optional terminal cash-flow margin inversion with explicit interim CFs.

The supplied final-year revenue and interim cash-flow path form JOINT scenarios.
This does not estimate a universal terminal PE or equity market price target.
"""
    observed = number(observed_equity_value, "observed_equity_value", positive=True)
    historical_cashflow = number(historical_cashflow, "historical_cashflow")
    if not isinstance(revenue_scenarios, (list, tuple)) or not revenue_scenarios:
        raise ModelInputError("at least one explicit revenue scenario is required")
    output = []
    for s in revenue_scenarios:
        cfs = [number(x, "interim_cashflow") for x in s["interim_cashflows"]]
        n = years_count(len(cfs))
        r, g = discount_parameters(s["discount_rate"], s["terminal_growth"])
        revenue = number(s["terminal_revenue"], "terminal_revenue", positive=True)
        interim_pv = finite_calculation(lambda: math.fsum(
            x / (1 + r) ** t for t, x in enumerate(cfs, 1)), "interim_cashflow_pv")
        # Last explicit-year cash flow and next-year terminal cash flow are kept distinct.
        required_next_cf = finite_calculation(lambda: (observed - interim_pv)
            * (1 + r) ** n * (r - g), "required_next_cashflow")
        terminal_revenue = number(revenue * (1 + g), "next_year_revenue", positive=True)
        output.append({"scenario_id": s["scenario_id"], "required_terminal_cashflow_margin":
                       number(required_next_cf / terminal_revenue, "required_terminal_cashflow_margin"),
                       "discount_rate": r, "terminal_growth": g,
                       "horizon_years": n, "historical_cashflow_context": historical_cashflow})
    return output
