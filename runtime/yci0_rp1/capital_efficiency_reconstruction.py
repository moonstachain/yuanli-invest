from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import re
from typing import Any, Iterable


FLOW_CONCEPTS = {
    "REVENUE", "OPERATING_INCOME", "PRETAX_INCOME", "INCOME_TAX_EXPENSE",
    "OPERATING_CASH_FLOW", "CAPEX",
}
OIC_MANDATORY_CONCEPTS = {
    "TOTAL_ASSETS", "CASH", "CURRENT_MARKETABLE_SECURITIES", "TOTAL_CURRENT_LIABILITIES",
}
OIC_OPTIONAL_INTEREST_BEARING_CONCEPTS = {
    "SHORT_TERM_BORROWINGS", "CURRENT_MATURITIES_LONG_TERM_DEBT", "CURRENT_FINANCE_LEASE_LIABILITIES",
}


@dataclass(frozen=True)
class FilingFact:
    entity_id: str
    fiscal_period: str
    known_as_of: str
    source_locator: str
    content_hash: str
    concept: str
    value: Decimal
    unit: str
    accounting_regime: str


@dataclass(frozen=True)
class DerivedCapitalEfficiencyObservation:
    entity_id: str
    fiscal_period: str
    component: str
    status: str
    reason: str
    value: Decimal | None
    formula_inputs: dict[str, Decimal]
    known_as_of: str | None
    calculation_receipt_sha256: str
    source_hashes: tuple[str, ...]
    source_known_as_of: tuple[str, ...]
    source_fact_count: int


def _period_key(period: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})Q([1-4])", period)
    if not match:
        raise ValueError(f"invalid fiscal_period: {period}")
    return int(match.group(1)), int(match.group(2))


def _decimal(spec: dict[str, Any], key: str) -> Decimal:
    return Decimal(str(spec[key]))


def _dedupe_facts(facts: Iterable[FilingFact]) -> dict[tuple[str, str], FilingFact]:
    index: dict[tuple[str, str], FilingFact] = {}
    for fact in facts:
        key = (fact.fiscal_period, fact.concept)
        previous = index.get(key)
        if previous and previous != fact:
            raise ValueError(f"ambiguous filing fact for {key}")
        index[key] = fact
    return index


def _fact(index: dict[tuple[str, str], FilingFact], period: str, concept: str) -> FilingFact | None:
    return index.get((period, concept))


def _collect(index: dict[tuple[str, str], FilingFact], periods: list[str], concepts: Iterable[str]) -> tuple[list[FilingFact], str | None]:
    rows: list[FilingFact] = []
    for period in periods:
        for concept in concepts:
            item = _fact(index, period, concept)
            if item is None:
                return rows, f"MISSING_FACT:{period}:{concept}"
            rows.append(item)
    return rows, None


def _regime_reason(rows: Iterable[FilingFact], expected: str) -> str | None:
    if any(row.accounting_regime != expected for row in rows):
        return "ACCOUNTING_REGIME_BREAK"
    return None


def _ttm_nopat(index: dict[tuple[str, str], FilingFact], periods: list[str], spec: dict[str, Any]) -> tuple[Decimal | None, str | None, list[FilingFact], dict[str, Decimal]]:
    rows, missing = _collect(index, periods, ("OPERATING_INCOME", "PRETAX_INCOME", "INCOME_TAX_EXPENSE"))
    if missing:
        return None, missing, rows, {}
    regime = _regime_reason(rows, str(spec["accounting_regime"]))
    if regime:
        return None, regime, rows, {}
    by = {c: sum((r.value for r in rows if r.concept == c), Decimal("0")) for c in ("OPERATING_INCOME", "PRETAX_INCOME", "INCOME_TAX_EXPENSE")}
    pretax = by["PRETAX_INCOME"]
    if pretax <= 0:
        return None, "PRETAX_NOT_POSITIVE", rows, by
    tax_rate = by["INCOME_TAX_EXPENSE"] / pretax
    if tax_rate < _decimal(spec, "tax_rate_min") or tax_rate > _decimal(spec, "tax_rate_max"):
        by["effective_tax_rate"] = tax_rate
        return None, "TAX_RATE_OUT_OF_RANGE", rows, by
    by["effective_tax_rate"] = tax_rate
    nopat = by["OPERATING_INCOME"] * (Decimal("1") - tax_rate)
    by["nopat"] = nopat
    return nopat, None, rows, by


def _operating_invested_capital(index: dict[tuple[str, str], FilingFact], period: str, spec: dict[str, Any]) -> tuple[Decimal | None, str | None, list[FilingFact], dict[str, Decimal]]:
    rows, missing = _collect(index, [period], sorted(OIC_MANDATORY_CONCEPTS))
    if missing:
        return None, missing, rows, {}
    optional_rows: list[FilingFact] = []
    values = {r.concept: r.value for r in rows}
    for concept in sorted(OIC_OPTIONAL_INTEREST_BEARING_CONCEPTS):
        item = _fact(index, period, concept)
        if item is None:
            values[concept] = Decimal("0")
        else:
            optional_rows.append(item)
            values[concept] = item.value
    rows = rows + optional_rows
    regime = _regime_reason(rows, str(spec["accounting_regime"]))
    if regime:
        return None, regime, rows, {}
    nibcl = (
        values["TOTAL_CURRENT_LIABILITIES"]
        - values["SHORT_TERM_BORROWINGS"]
        - values["CURRENT_MATURITIES_LONG_TERM_DEBT"]
        - values["CURRENT_FINANCE_LEASE_LIABILITIES"]
    )
    oic = values["TOTAL_ASSETS"] - values["CASH"] - values["CURRENT_MARKETABLE_SECURITIES"] - nibcl
    values["non_interest_bearing_current_liabilities"] = nibcl
    values["operating_invested_capital"] = oic
    return oic, None, rows, values


def _receipt(entity_id: str, period: str, component: str, status: str, reason: str, value: Decimal | None, inputs: dict[str, Decimal], rows: Iterable[FilingFact]) -> tuple[str, tuple[str, ...], tuple[str, ...], int, str | None]:
    unique = {(r.fiscal_period, r.concept, r.content_hash, r.source_locator): r for r in rows}
    ordered = [unique[k] for k in sorted(unique)]
    hashes = tuple(r.content_hash for r in ordered)
    known = tuple(r.known_as_of for r in ordered)
    payload = {
        "entity_id": entity_id,
        "fiscal_period": period,
        "component": component,
        "status": status,
        "reason": reason,
        "value": None if value is None else str(value),
        "formula_inputs": {k: str(v) for k, v in sorted(inputs.items())},
        "sources": [
            {"period": r.fiscal_period, "concept": r.concept, "hash": r.content_hash, "locator": r.source_locator, "known_as_of": r.known_as_of}
            for r in ordered
        ],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest(), hashes, known, len(ordered), max(known, default=None)


def _observation(entity_id: str, period: str, component: str, value: Decimal | None, reason: str | None, inputs: dict[str, Decimal], rows: Iterable[FilingFact]) -> DerivedCapitalEfficiencyObservation:
    status = "PASS" if reason is None and value is not None else "UNKNOWN"
    final_reason = "PIT_QUALIFIED" if status == "PASS" else (reason or "UNKNOWN")
    receipt, hashes, known, count, known_as_of = _receipt(entity_id, period, component, status, final_reason, value, inputs, rows)
    return DerivedCapitalEfficiencyObservation(
        entity_id=entity_id,
        fiscal_period=period,
        component=component,
        status=status,
        reason=final_reason,
        value=value if status == "PASS" else None,
        formula_inputs=inputs,
        known_as_of=known_as_of,
        calculation_receipt_sha256=receipt,
        source_hashes=hashes,
        source_known_as_of=known,
        source_fact_count=count,
    )


def reconstruct_entity_observations(facts: Iterable[FilingFact], entity_spec: dict[str, Any]) -> list[DerivedCapitalEfficiencyObservation]:
    rows = list(facts)
    entity_id = str(entity_spec["entity_id"])
    if any(row.entity_id != entity_id for row in rows):
        raise ValueError("entity_id mismatch in filing facts")
    index = _dedupe_facts(rows)
    periods = sorted({row.fiscal_period for row in rows}, key=_period_key)
    out: list[DerivedCapitalEfficiencyObservation] = []

    for i, period in enumerate(periods):
        if i < 3:
            continue
        ttm_periods = periods[i - 3 : i + 1]
        nopat, nopat_reason, nopat_rows, nopat_inputs = _ttm_nopat(index, ttm_periods, entity_spec)

        cfo_rows, cfo_missing = _collect(index, ttm_periods, ("OPERATING_CASH_FLOW",))
        cash_rows = nopat_rows + cfo_rows
        cash_reason = nopat_reason or cfo_missing or _regime_reason(cfo_rows, str(entity_spec["accounting_regime"]))
        cash_inputs = dict(nopat_inputs)
        cash_value = None
        if cash_reason is None and nopat is not None:
            cash_inputs["ttm_operating_cash_flow"] = sum((r.value for r in cfo_rows), Decimal("0"))
            if abs(nopat) <= _decimal(entity_spec, "near_zero_nopat"):
                cash_reason = "NOPAT_NEAR_ZERO"
            else:
                cash_inputs["ttm_nopat"] = nopat
                cash_value = cash_inputs["ttm_operating_cash_flow"] / nopat
        out.append(_observation(entity_id, period, "CASH_CONVERSION", cash_value, cash_reason, cash_inputs, cash_rows))

        burden_rows, burden_missing = _collect(index, ttm_periods, ("CAPEX", "REVENUE"))
        burden_reason = burden_missing or _regime_reason(burden_rows, str(entity_spec["accounting_regime"]))
        burden_inputs: dict[str, Decimal] = {}
        burden_value = None
        if burden_reason is None:
            burden_inputs["ttm_capex"] = sum((r.value for r in burden_rows if r.concept == "CAPEX"), Decimal("0"))
            burden_inputs["ttm_revenue"] = sum((r.value for r in burden_rows if r.concept == "REVENUE"), Decimal("0"))
            if burden_inputs["ttm_revenue"] <= 0:
                burden_reason = "REVENUE_NOT_POSITIVE"
            else:
                burden_value = burden_inputs["ttm_capex"] / burden_inputs["ttm_revenue"]
        out.append(_observation(entity_id, period, "CAPITAL_INTENSITY", burden_value, burden_reason, burden_inputs, burden_rows))

        if i < 7:
            continue
        base_period = periods[i - 4]
        base_ttm_periods = periods[i - 7 : i - 3]
        base_nopat, base_nopat_reason, base_nopat_rows, base_nopat_inputs = _ttm_nopat(index, base_ttm_periods, entity_spec)
        oic_t, oic_t_reason, oic_t_rows, oic_t_inputs = _operating_invested_capital(index, period, entity_spec)
        oic_base, oic_base_reason, oic_base_rows, oic_base_inputs = _operating_invested_capital(index, base_period, entity_spec)
        roic_rows = nopat_rows + base_nopat_rows + oic_t_rows + oic_base_rows
        roic_reason = nopat_reason or base_nopat_reason or oic_t_reason or oic_base_reason or _regime_reason(roic_rows, str(entity_spec["accounting_regime"]))
        roic_inputs: dict[str, Decimal] = {}
        roic_value = None
        if nopat is not None:
            roic_inputs["ttm_nopat_t"] = nopat
        if base_nopat is not None:
            roic_inputs["ttm_nopat_t_minus_4"] = base_nopat
        if oic_t is not None:
            roic_inputs["operating_invested_capital_t"] = oic_t
        if oic_base is not None:
            roic_inputs["operating_invested_capital_t_minus_4"] = oic_base
        for concept, name in (("SHORT_TERM_BORROWINGS", "short_term_borrowings"), ("CURRENT_MATURITIES_LONG_TERM_DEBT", "current_maturities_long_term_debt"), ("CURRENT_FINANCE_LEASE_LIABILITIES", "current_finance_lease_liabilities")):
            if concept in oic_t_inputs:
                roic_inputs[f"{name}_t"] = oic_t_inputs[concept]
            if concept in oic_base_inputs:
                roic_inputs[f"{name}_t_minus_4"] = oic_base_inputs[concept]
        if roic_reason is None and None not in (nopat, base_nopat, oic_t, oic_base):
            delta_ic = oic_t - oic_base  # type: ignore[operator]
            roic_inputs["invested_capital_delta_yoy"] = delta_ic
            roic_inputs["nopat_delta_yoy"] = nopat - base_nopat  # type: ignore[operator]
            if delta_ic <= 0 or delta_ic < _decimal(entity_spec, "minimum_invested_capital_delta"):
                roic_reason = "INVESTED_CAPITAL_DELTA_NOT_MEANINGFUL"
            else:
                roic_value = roic_inputs["nopat_delta_yoy"] / delta_ic
        out.append(_observation(entity_id, period, "INCREMENTAL_ROIC", roic_value, roic_reason, roic_inputs, roic_rows))

    return out
