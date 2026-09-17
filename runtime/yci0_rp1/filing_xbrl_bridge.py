from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import xml.etree.ElementTree as ET
from typing import Iterable

from runtime.yci0_rp1.capital_efficiency_reconstruction import FilingFact


@dataclass(frozen=True)
class FilingXbrlFact:
    concept: str
    value: Decimal
    context_ref: str
    start: str | None
    end: str | None
    instant: str | None
    dimensions: tuple[tuple[str, str], ...]


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def parse_xbrl_instance(raw: bytes) -> tuple[FilingXbrlFact, ...]:
    root = ET.fromstring(raw)
    contexts: dict[str, dict[str, object]] = {}
    for node in root.iter():
        if _local(node.tag) != "context":
            continue
        ctx = {"start": None, "end": None, "instant": None, "dimensions": []}
        for child in node.iter():
            name = _local(child.tag)
            if name == "startDate":
                ctx["start"] = (child.text or "").strip() or None
            elif name == "endDate":
                ctx["end"] = (child.text or "").strip() or None
            elif name == "instant":
                ctx["instant"] = (child.text or "").strip() or None
            elif name in {"explicitMember", "typedMember"}:
                ctx["dimensions"].append((str(child.attrib.get("dimension") or ""), (child.text or "").strip()))
        contexts[str(node.attrib.get("id") or "")] = ctx

    facts: list[FilingXbrlFact] = []
    for node in root.iter():
        cref = node.attrib.get("contextRef")
        if not cref or cref not in contexts:
            continue
        text = (node.text or "").strip().replace(",", "")
        if not text:
            continue
        try:
            value = Decimal(text)
        except InvalidOperation:
            continue
        ctx = contexts[cref]
        facts.append(FilingXbrlFact(
            concept=_local(node.tag), value=value, context_ref=cref,
            start=ctx["start"], end=ctx["end"], instant=ctx["instant"],
            dimensions=tuple(ctx["dimensions"]),
        ))
    return tuple(facts)


def _unique_zero_dim(
    facts: Iterable[FilingXbrlFact], concept: str, *, instant: str | None = None,
    start: str | None = None, end: str | None = None,
) -> FilingXbrlFact | None:
    rows = [f for f in facts if f.concept == concept and not f.dimensions]
    if instant is not None:
        rows = [f for f in rows if f.instant == instant]
    if start is not None:
        rows = [f for f in rows if f.start == start]
    if end is not None:
        rows = [f for f in rows if f.end == end]
    if len(rows) != 1:
        return None
    return rows[0]


def _hash(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def build_filing_instant_bridge_fact(
    *, entity_id: str, fiscal_period: str, normalized_concept: str, concept: str,
    raw: bytes, raw_sha256: str, accession: str, known_as_of: str, instant: str,
    accounting_regime: str,
) -> tuple[FilingFact | None, dict[str, str]]:
    item = _unique_zero_dim(parse_xbrl_instance(raw), concept, instant=instant)
    if item is None:
        return None, {"status": "UNKNOWN", "reason": "UNIQUE_ZERO_DIMENSION_INSTANT_NOT_FOUND"}
    payload = {
        "proof_type": "FILING_INSTANT_XBRL", "entity_id": entity_id, "period": fiscal_period,
        "normalized_concept": normalized_concept, "concept": concept, "instant": instant,
        "value": str(item.value), "raw_sha256": raw_sha256, "accession": accession,
    }
    fact = FilingFact(
        entity_id=entity_id, fiscal_period=fiscal_period, known_as_of=known_as_of,
        source_locator=f"sec-filing-xbrl://{accession}#{concept}@{instant}",
        content_hash=_hash(payload), concept=normalized_concept, value=item.value,
        unit="USD", accounting_regime=accounting_regime,
    )
    return fact, {"status": "PASS", "reason": "PIT_FILING_XBRL", "proof_sha256": fact.content_hash}


def build_same_standard_q4_bridge_fact(
    *, entity_id: str, fiscal_period: str, normalized_concept: str, standard_tag: str,
    annual_raw: bytes, annual_raw_sha256: str, annual_accession: str, annual_known_as_of: str,
    annual_start: str, annual_end: str, q3_ytd_fact: FilingFact, accounting_regime: str,
) -> tuple[FilingFact | None, dict[str, str]]:
    if f"/us-gaap/{standard_tag}?" not in q3_ytd_fact.source_locator:
        return None, {"status": "UNKNOWN", "reason": "Q3_SOURCE_TAG_MISMATCH"}
    annual = _unique_zero_dim(parse_xbrl_instance(annual_raw), standard_tag, start=annual_start, end=annual_end)
    if annual is None:
        return None, {"status": "UNKNOWN", "reason": "ANNUAL_STANDARD_TAG_NOT_FOUND"}
    value = annual.value - q3_ytd_fact.value
    payload = {
        "proof_type": "SAME_STANDARD_TAG_Q4_FROM_FY_MINUS_Q3", "entity_id": entity_id,
        "period": fiscal_period, "normalized_concept": normalized_concept, "tag": standard_tag,
        "annual_value": str(annual.value), "q3_ytd_value": str(q3_ytd_fact.value), "value": str(value),
        "annual_raw_sha256": annual_raw_sha256, "annual_accession": annual_accession,
        "q3_content_hash": q3_ytd_fact.content_hash,
    }
    content_hash = _hash(payload)
    fact = FilingFact(
        entity_id=entity_id, fiscal_period=fiscal_period,
        known_as_of=max(annual_known_as_of, q3_ytd_fact.known_as_of),
        source_locator=f"sec-filing-xbrl://{annual_accession}#{standard_tag};q3={q3_ytd_fact.source_locator}",
        content_hash=content_hash, concept=normalized_concept, value=value,
        unit="USD", accounting_regime=accounting_regime,
    )
    return fact, {"status": "PASS", "reason": "SAME_STANDARD_TAG_RECONSTRUCTED_Q4", "proof_sha256": content_hash}


def build_disaggregation_bridge_fact(
    *, entity_id: str, fiscal_period: str, normalized_concept: str,
    component_concepts: tuple[str, ...], raw: bytes, raw_sha256: str, accession: str,
    known_as_of: str, instant: str, reconcile_instant: str, anchor_fact: FilingFact,
    accounting_regime: str,
) -> tuple[FilingFact | None, dict[str, str]]:
    facts = parse_xbrl_instance(raw)
    current = [_unique_zero_dim(facts, concept, instant=instant) for concept in component_concepts]
    prior = [_unique_zero_dim(facts, concept, instant=reconcile_instant) for concept in component_concepts]
    if any(item is None for item in current + prior):
        return None, {"status": "UNKNOWN", "reason": "DISAGGREGATION_COMPONENT_MISSING"}
    current_sum = sum((item.value for item in current if item is not None), Decimal("0"))
    prior_sum = sum((item.value for item in prior if item is not None), Decimal("0"))
    if prior_sum != anchor_fact.value:
        return None, {
            "status": "UNKNOWN", "reason": "DISAGGREGATION_RECONCILIATION_MISMATCH",
            "reconciled_prior_sum": str(prior_sum), "anchor_value": str(anchor_fact.value),
        }
    payload = {
        "proof_type": "DISAGGREGATION_RECONCILIATION", "entity_id": entity_id,
        "period": fiscal_period, "normalized_concept": normalized_concept,
        "components": list(component_concepts), "current_sum": str(current_sum),
        "reconcile_instant": reconcile_instant, "reconciled_prior_sum": str(prior_sum),
        "anchor_value": str(anchor_fact.value), "anchor_hash": anchor_fact.content_hash,
        "raw_sha256": raw_sha256, "accession": accession,
    }
    content_hash = _hash(payload)
    fact = FilingFact(
        entity_id=entity_id, fiscal_period=fiscal_period, known_as_of=known_as_of,
        source_locator=f"sec-filing-xbrl://{accession}#sum({','.join(component_concepts)})@{instant}",
        content_hash=content_hash, concept=normalized_concept, value=current_sum,
        unit="USD", accounting_regime=accounting_regime,
    )
    return fact, {
        "status": "PASS", "reason": "DISAGGREGATION_RECONCILED",
        "reconciled_prior_sum": str(prior_sum), "proof_sha256": content_hash,
    }


def apply_filing_bridge_rules(
    *, entity_id: str, accounting_regime: str,
    base_series: dict[str, list[FilingFact]], rules: list[dict[str, object]],
    filings: dict[str, dict[str, str]], raw_by_filing: dict[str, bytes],
    raw_sha_by_filing: dict[str, str], known_as_of_by_accession: dict[str, str],
) -> tuple[dict[str, list[FilingFact]], list[dict[str, str]], list[str]]:
    series = {concept: list(rows) for concept, rows in base_series.items()}
    emitted: dict[str, FilingFact] = {}
    proofs: list[dict[str, str]] = []
    blockers: list[str] = []

    for rule in rules:
        rule_id = str(rule["rule_id"])
        proof_type = str(rule["proof_type"])
        normalized = str(rule["normalized_concept"])
        filing_id = str(rule["filing_id"])
        filing = filings.get(filing_id) or {}
        accession = str(filing.get("accession") or "")
        raw = raw_by_filing.get(filing_id)
        raw_sha = raw_sha_by_filing.get(filing_id)
        known = known_as_of_by_accession.get(accession)
        if not accession or raw is None or raw_sha is None or known is None:
            blockers.append(f"BRIDGE_INPUT_MISSING:{rule_id}")
            proofs.append({"rule_id": rule_id, "status": "UNKNOWN", "reason": "BRIDGE_INPUT_MISSING"})
            continue

        fact: FilingFact | None
        proof: dict[str, str]
        if proof_type == "FILING_INSTANT_XBRL":
            fact, proof = build_filing_instant_bridge_fact(
                entity_id=entity_id, fiscal_period=str(rule["fiscal_period"]), normalized_concept=normalized,
                concept=str(rule["concept"]), raw=raw, raw_sha256=raw_sha, accession=accession,
                known_as_of=known, instant=str(rule["instant"]), accounting_regime=accounting_regime,
            )
        elif proof_type == "DISAGGREGATION_RECONCILIATION":
            anchor_id = str(rule["anchor_rule_id"])
            anchor = emitted.get(anchor_id)
            if anchor is None:
                fact, proof = None, {"status": "UNKNOWN", "reason": "ANCHOR_RULE_NOT_AVAILABLE"}
            else:
                fact, proof = build_disaggregation_bridge_fact(
                    entity_id=entity_id, fiscal_period=str(rule["fiscal_period"]), normalized_concept=normalized,
                    component_concepts=tuple(str(x) for x in rule["components"]), raw=raw, raw_sha256=raw_sha,
                    accession=accession, known_as_of=known, instant=str(rule["instant"]),
                    reconcile_instant=str(rule["reconcile_instant"]), anchor_fact=anchor,
                    accounting_regime=accounting_regime,
                )
        elif proof_type == "SAME_STANDARD_TAG_Q4_FROM_FY_MINUS_Q3":
            q3_period = str(rule["q3_period"])
            q3 = next((f for f in series.get(normalized, []) if f.fiscal_period == q3_period), None)
            if q3 is None:
                fact, proof = None, {"status": "UNKNOWN", "reason": "Q3_BASE_FACT_NOT_AVAILABLE"}
            else:
                fact, proof = build_same_standard_q4_bridge_fact(
                    entity_id=entity_id, fiscal_period=str(rule["fiscal_period"]), normalized_concept=normalized,
                    standard_tag=str(rule["standard_tag"]), annual_raw=raw, annual_raw_sha256=raw_sha,
                    annual_accession=accession, annual_known_as_of=known, annual_start=str(rule["annual_start"]),
                    annual_end=str(rule["annual_end"]), q3_ytd_fact=q3, accounting_regime=accounting_regime,
                )
        else:
            fact, proof = None, {"status": "UNKNOWN", "reason": "UNSUPPORTED_BRIDGE_PROOF_TYPE"}

        proof = {"rule_id": rule_id, **proof}
        proofs.append(proof)
        if fact is None or proof.get("status") != "PASS":
            blockers.append(f"BRIDGE_RULE_FAILED:{rule_id}:{proof.get('reason','UNKNOWN')}")
            continue

        rows = series.setdefault(normalized, [])
        existing = next((x for x in rows if x.fiscal_period == fact.fiscal_period), None)
        if existing is not None and existing.value != fact.value:
            blockers.append(f"BRIDGE_CONFLICT:{rule_id}:{fact.fiscal_period}")
            continue
        if existing is None:
            rows.append(fact)
            rows.sort(key=lambda x: (int(x.fiscal_period[:4]), int(x.fiscal_period[-1])))
        emitted[rule_id] = fact if existing is None else existing

    return series, proofs, blockers
