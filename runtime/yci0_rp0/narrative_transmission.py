from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

ALLOWED_NARRATIVE_STAGES = {"D0", "D1", "D2", "D3", "D4", "UNKNOWN"}


class NarrativeTransmissionError(ValueError):
    pass


@dataclass(frozen=True)
class NarrativeTransmissionCard:
    narrative_stage: str
    dominant_story: str
    narrative_gap_hypothesis: str
    primary_chain: tuple[str, ...]
    current_bottleneck: str
    next_bottleneck_hypothesis: str
    common_shock_branch: str
    hard_negative_branch: str
    evidence_refs: tuple[str, ...]
    scientific_status: str = "LIMITED"
    authority: str = "RESEARCH"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(name: str, value: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise NarrativeTransmissionError(f"{name.upper()}_REQUIRED")
    return text


def compile_narrative_transmission(
    *,
    narrative_stage: str,
    dominant_story: str,
    narrative_gap_hypothesis: str,
    primary_chain: tuple[str, ...],
    current_bottleneck: str,
    next_bottleneck_hypothesis: str,
    common_shock_branch: str,
    hard_negative_branch: str,
    evidence_refs: tuple[str, ...] = (),
) -> NarrativeTransmissionCard:
    if narrative_stage not in ALLOWED_NARRATIVE_STAGES:
        raise NarrativeTransmissionError("NARRATIVE_STAGE_INVALID")
    chain = tuple(str(node).strip() for node in primary_chain if str(node).strip())
    if len(chain) < 2:
        raise NarrativeTransmissionError("PRIMARY_CHAIN_REQUIRED")
    return NarrativeTransmissionCard(
        narrative_stage=narrative_stage,
        dominant_story=_required_text("dominant_story", dominant_story),
        narrative_gap_hypothesis=_required_text("narrative_gap_hypothesis", narrative_gap_hypothesis),
        primary_chain=chain,
        current_bottleneck=_required_text("current_bottleneck", current_bottleneck),
        next_bottleneck_hypothesis=_required_text("next_bottleneck_hypothesis", next_bottleneck_hypothesis),
        common_shock_branch=_required_text("common_shock_branch", common_shock_branch),
        hard_negative_branch=_required_text("hard_negative_branch", hard_negative_branch),
        evidence_refs=tuple(dict.fromkeys(evidence_refs)),
    )
