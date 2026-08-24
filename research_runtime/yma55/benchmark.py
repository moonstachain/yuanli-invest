from __future__ import annotations

from typing import Any

from .blind import resolve_blind_packet, validate_blind_packet
from .validation import assert_no_capital_outputs

BENCHMARK_VARIANTS = (
    "B0_NAIVE_PRIMARY_PRIOR",
    "B1_EVIDENCE_GATED_PRIMARY",
    "B2_COMPETING_NO_BREAKER",
    "B3_H1_H2_FULL_RESOLVER",
    "B4_H1_H2_H3_HISTORICAL_ONLY",
)


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


def _signal_map(signals: list[dict[str, Any]]) -> dict[str, list[str]]:
    mapped: dict[str, list[str]] = {}
    for signal in signals:
        observable = _norm(signal.get("observable", signal.get("token", "")))
        if observable:
            mapped.setdefault(observable, []).append(_norm(signal.get("state", "TRUE")))
    return mapped


def _simple_score(hypothesis: dict[str, Any], signals: dict[str, list[str]]) -> tuple[int, int]:
    support = 0
    contradiction = 0
    for observable, expected in hypothesis.get("predicted_observables", {}).items():
        observed = signals.get(_norm(observable), [])
        if not observed:
            continue
        if _norm(expected) in observed:
            support += 1
        else:
            contradiction += 1
    for condition in hypothesis.get("required_conditions", []):
        observed = signals.get(_norm(condition), [])
        if any(state in {"TRUE", "PRESENT", "YES", "1"} for state in observed):
            support += 1
        elif any(state in {"FALSE", "ABSENT", "NO", "0"} for state in observed):
            contradiction += 1
    return support - contradiction, support


def _resolve_competing_no_breaker(packet: dict[str, Any]) -> str:
    evidence = packet["evidence"]
    if evidence.get("hydration_status") != "EVIDENCE_HYDRATED" or not evidence.get("admitted_signals"):
        return "INSUFFICIENT_EVIDENCE"
    signals = _signal_map(evidence["admitted_signals"])
    hs = packet["t0"]["hypothesis_set"]
    hypotheses = [hs["primary"], *hs.get("alternatives", []), hs["null"]]
    ranked = []
    for hypothesis in hypotheses:
        score, support = _simple_score(hypothesis, signals)
        ranked.append((score, support, hypothesis.get("role", "")))
    ranked.sort(reverse=True)
    best = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else best[0] - 1
    if best[0] <= 0 or best[0] == second_score:
        return "TIE_UNRESOLVED"
    if best[2] == "PRIMARY":
        return "PRIMARY_LEADS"
    if best[2] == "ALTERNATIVE":
        return "ALTERNATIVE_LEADS"
    if best[2] == "NULL":
        return "NULL_LEADS"
    return "TIE_UNRESOLVED"


def resolve_variant(packet: dict[str, Any], variant: str) -> dict[str, Any]:
    validate_blind_packet(packet)
    if variant not in BENCHMARK_VARIANTS:
        raise ValueError(f"unknown benchmark variant: {variant}")

    base = {
        "blind_case_id": packet["blind_case_id"],
        "variant": variant,
        "claims_old_framework_replication": False,
        "capital_authority": False,
    }
    if variant == "B0_NAIVE_PRIMARY_PRIOR":
        base.update({"resolution": "PRIMARY_LEADS", "baseline_semantics": "naive_primary_prior"})
    elif variant == "B1_EVIDENCE_GATED_PRIMARY":
        resolution = (
            "PRIMARY_LEADS"
            if packet["evidence"].get("hydration_status") == "EVIDENCE_HYDRATED"
            and packet["evidence"].get("admitted_signals")
            else "INSUFFICIENT_EVIDENCE"
        )
        base.update({"resolution": resolution, "baseline_semantics": "evidence_gated_primary_prior"})
    elif variant == "B2_COMPETING_NO_BREAKER":
        base.update({
            "resolution": _resolve_competing_no_breaker(packet),
            "baseline_semantics": "competing_mechanisms_without_falsifier_breaker_penalties",
        })
    elif variant == "B3_H1_H2_FULL_RESOLVER":
        resolution = resolve_blind_packet(packet)["resolution"]
        base.update({"resolution": resolution, "baseline_semantics": "h1_h2_full_blind_resolver"})
    else:
        resolution = resolve_blind_packet(packet)["resolution"]
        base.update({
            "resolution": resolution,
            "baseline_semantics": "h1_h2_resolver_with_h3_present_but_not_identifiable_in_historical_only_replay",
            "h3_incremental_status": "NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY",
        })
    assert_no_capital_outputs(base)
    return base


def score_variant(outputs: list[dict[str, Any]], settlements: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {row["blind_case_id"]: row for row in settlements}
    if set(expected) != {row["blind_case_id"] for row in outputs}:
        raise ValueError("benchmark outputs and settlement cases must match exactly")

    matches = 0
    mismatches = 0
    abstentions = 0
    fully_hydrated_cases = 0
    fully_hydrated_matches = 0
    fully_hydrated_mismatches = 0
    hard_negative_total = 0
    hard_negative_correct = 0
    partial_case_forced = False

    for output in outputs:
        truth = expected[output["blind_case_id"]]
        resolution = output["resolution"]
        target = truth["settlement_expected_resolution"]
        hydrated = truth["hydration_status"] == "EVIDENCE_HYDRATED"
        if hydrated:
            fully_hydrated_cases += 1
        if target in {"ALTERNATIVE_LEADS", "NULL_LEADS"}:
            hard_negative_total += 1
            if resolution == target:
                hard_negative_correct += 1

        if resolution in {"INSUFFICIENT_EVIDENCE", "TIE_UNRESOLVED"}:
            abstentions += 1
        elif resolution == target:
            matches += 1
            if hydrated:
                fully_hydrated_matches += 1
        else:
            mismatches += 1
            if hydrated:
                fully_hydrated_mismatches += 1

        if not hydrated and resolution not in {"INSUFFICIENT_EVIDENCE", "TIE_UNRESOLVED"}:
            partial_case_forced = True

    denominator = fully_hydrated_matches + fully_hydrated_mismatches
    accuracy = f"{fully_hydrated_matches}/{denominator}" if denominator else "0/0"
    result = {
        "total_cases": len(outputs),
        "fully_hydrated_cases": fully_hydrated_cases,
        "matches": matches,
        "mismatches": mismatches,
        "evidence_abstentions": abstentions,
        "fully_hydrated_matches": fully_hydrated_matches,
        "fully_hydrated_mismatches": fully_hydrated_mismatches,
        "fully_hydrated_mechanism_accuracy": accuracy,
        "hard_negative_discrimination": f"{hard_negative_correct}/{hard_negative_total}",
        "partial_case_forced_resolution": partial_case_forced,
    }
    assert_no_capital_outputs(result)
    return result
