from __future__ import annotations

import copy
import re
from typing import Any

from .validation import assert_no_capital_outputs

PROHIBITED_BLIND_KEYS = {
    "case_type",
    "settlement",
    "outcome_class",
    "episode_id",
    "gold_qualified",
    "historical_gold_admitted",
}
ROLE_LEAK_TOKENS = ("GOLD", "NEAR", "WRONG_MECHANISM", "WRONG_STRIKE", "-WM-", "-WS-")
VALID_RESOLUTIONS = {
    "PRIMARY_LEADS",
    "ALTERNATIVE_LEADS",
    "NULL_LEADS",
    "TIE_UNRESOLVED",
    "INSUFFICIENT_EVIDENCE",
}


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys |= _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            keys |= _walk_keys(child)
    return keys


def build_blind_packet(
    blind_case_id: str,
    case: dict[str, Any],
    evidence_packet: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": "0.1.0",
        "blind_case_id": blind_case_id,
        "mechanism_family": case["mechanism_family"],
        "as_of": case["as_of"],
        "evidence_cutoff": case["evidence_cutoff"],
        "t0": copy.deepcopy(case["t0"]),
        "evidence": {
            "hydration_status": evidence_packet.get("hydration_status", "INSUFFICIENT_EVIDENCE"),
            "blindness_grade": evidence_packet.get("blindness_grade", "B_PIPELINE_BLIND"),
            "admitted_signals": copy.deepcopy(evidence_packet.get("admitted_signals", [])),
        },
    }
    assert_no_capital_outputs(packet)
    validate_blind_packet(packet)
    return packet


def validate_blind_packet(packet: dict[str, Any]) -> None:
    blind_id = str(packet.get("blind_case_id", ""))
    if not re.fullmatch(r"H41-B\d{2}", blind_id):
        raise ValueError("blind_case_id must be opaque and role-free")
    upper_id = blind_id.upper()
    if any(token in upper_id for token in ROLE_LEAK_TOKENS):
        raise ValueError("blind case id contains role leakage")
    leaked = _walk_keys(packet) & PROHIBITED_BLIND_KEYS
    if leaked:
        raise ValueError(f"blind packet contains outcome/role keys: {sorted(leaked)}")
    if "t0" not in packet or "evidence" not in packet:
        raise ValueError("blind packet requires t0 and evidence")
    assert_no_capital_outputs(packet)


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


def _signal_map(signals: list[dict[str, Any]]) -> dict[str, list[str]]:
    mapped: dict[str, list[str]] = {}
    for signal in signals:
        observable = _norm(signal.get("observable", signal.get("token", "")))
        if not observable:
            continue
        state = _norm(signal.get("state", "TRUE"))
        mapped.setdefault(observable, []).append(state)
        token = signal.get("token")
        if token:
            mapped.setdefault(_norm(token), []).append(state)
    return mapped


def _token_triggered(token: str, signals: dict[str, list[str]]) -> bool:
    key = _norm(token)
    if key in signals and any(state in {"TRUE", "TRIGGERED", "YES", "1"} for state in signals[key]):
        return True
    directional_suffixes = {"_UP": "UP", "_DOWN": "DOWN", "_HIGH": "HIGH", "_LOW": "LOW"}
    for suffix, state in directional_suffixes.items():
        if key.endswith(suffix):
            observable = key[: -len(suffix)]
            if state in signals.get(observable, []):
                return True
    return False


def _score_hypothesis(hypothesis: dict[str, Any], signals: dict[str, list[str]]) -> dict[str, Any]:
    support = 0
    contradiction = 0
    unknown = 0
    predicted = hypothesis.get("predicted_observables", {})
    for observable, expected in predicted.items():
        observed_states = signals.get(_norm(observable), [])
        if not observed_states:
            unknown += 1
        elif _norm(expected) in observed_states:
            support += 1
        else:
            contradiction += 1

    for condition in hypothesis.get("required_conditions", []):
        states = signals.get(_norm(condition), [])
        if not states:
            continue
        if any(state in {"TRUE", "PRESENT", "YES", "1"} for state in states):
            support += 1
        elif any(state in {"FALSE", "ABSENT", "NO", "0"} for state in states):
            contradiction += 1

    falsifier_triggered = any(_token_triggered(item, signals) for item in hypothesis.get("falsifiers", []))
    breaker = hypothesis.get("breaker")
    breaker_triggered = bool(breaker and _token_triggered(str(breaker), signals))
    decisive_count = len(predicted)
    observed_decisive = decisive_count - sum(1 for observable in predicted if not signals.get(_norm(observable)))
    coverage_ratio = (observed_decisive / decisive_count) if decisive_count else 0.0
    score = support - contradiction
    if falsifier_triggered:
        score -= 2
    if breaker_triggered:
        score -= 4
    return {
        "hypothesis_id": hypothesis.get("hypothesis_id"),
        "role": hypothesis.get("role"),
        "support_count": support,
        "contradiction_count": contradiction,
        "unknown_count": unknown,
        "falsifier_triggered": falsifier_triggered,
        "breaker_triggered": breaker_triggered,
        "coverage_ratio": round(coverage_ratio, 4),
        "score": score,
    }


def resolve_blind_packet(packet: dict[str, Any]) -> dict[str, Any]:
    validate_blind_packet(packet)
    evidence = packet["evidence"]
    signals_list = evidence.get("admitted_signals", [])
    if evidence.get("hydration_status") != "EVIDENCE_HYDRATED" or not signals_list:
        return {
            "blind_case_id": packet["blind_case_id"],
            "blindness_grade": evidence.get("blindness_grade", "B_PIPELINE_BLIND"),
            "resolution": "INSUFFICIENT_EVIDENCE",
            "hypothesis_scores": [],
        }

    signals = _signal_map(signals_list)
    hs = packet["t0"]["hypothesis_set"]
    hypotheses = [hs["primary"], *hs.get("alternatives", []), hs["null"]]
    scores = [_score_hypothesis(hypothesis, signals) for hypothesis in hypotheses]
    eligible = [score for score in scores if not score["breaker_triggered"] and score["coverage_ratio"] >= 0.5]
    if not eligible:
        resolution = "INSUFFICIENT_EVIDENCE"
    else:
        ranked = sorted(eligible, key=lambda item: (item["score"], item["support_count"]), reverse=True)
        best = ranked[0]
        second_score = ranked[1]["score"] if len(ranked) > 1 else best["score"] - 1
        if best["score"] <= 0 or best["score"] == second_score:
            resolution = "TIE_UNRESOLVED"
        elif best["role"] == "PRIMARY":
            resolution = "PRIMARY_LEADS"
        elif best["role"] == "ALTERNATIVE":
            resolution = "ALTERNATIVE_LEADS"
        elif best["role"] == "NULL":
            resolution = "NULL_LEADS"
        else:
            resolution = "TIE_UNRESOLVED"

    result = {
        "blind_case_id": packet["blind_case_id"],
        "blindness_grade": evidence.get("blindness_grade", "B_PIPELINE_BLIND"),
        "resolution": resolution,
        "hypothesis_scores": scores,
    }
    if result["resolution"] not in VALID_RESOLUTIONS:
        raise ValueError("invalid blind resolution")
    assert_no_capital_outputs(result)
    return result
