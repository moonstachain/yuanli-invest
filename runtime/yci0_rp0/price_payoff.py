from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


class PricePayoffError(ValueError):
    pass


@dataclass(frozen=True)
class PricePayoffCard:
    implied_belief: str
    scenarios: dict[str, str]
    defeat_condition: str
    survival_cost: str
    book_mapping: dict[str, str]
    evidence_refs: tuple[str, ...]
    scientific_status: str = "RESEARCH"
    authority: str = "RESEARCH"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(name: str, value: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise PricePayoffError(f"{name.upper()}_REQUIRED")
    return out


def compile_price_payoff(
    *,
    implied_belief: str,
    bull: str,
    base: str,
    bear: str,
    hard_negative: str,
    defeat_condition: str,
    survival_cost: str,
    book_mapping: Mapping[str, str],
    evidence_refs: tuple[str, ...] = (),
) -> PricePayoffCard:
    if set(book_mapping) != {"S", "C", "R", "X"}:
        raise PricePayoffError("SCRX_MAPPING_REQUIRED")
    normalized_mapping = {key: _text(f"book_{key}", book_mapping[key]) for key in ("S", "C", "R", "X")}
    scenarios = {
        "BULL": _text("bull", bull),
        "BASE": _text("base", base),
        "BEAR": _text("bear", bear),
        "HARD_NEGATIVE": _text("hard_negative", hard_negative),
    }
    return PricePayoffCard(
        implied_belief=_text("implied_belief", implied_belief),
        scenarios=scenarios,
        defeat_condition=_text("defeat_condition", defeat_condition),
        survival_cost=_text("survival_cost", survival_cost),
        book_mapping=normalized_mapping,
        evidence_refs=tuple(dict.fromkeys(evidence_refs)),
    )
