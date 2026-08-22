#!/usr/bin/env python3
"""Fail-closed validation for YIM0 Human Projection and Canon-status convergence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
MAP_PATH = ROOT / "docs" / "human-projection" / "YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md"
README_PATH = ROOT / "docs" / "os-vnext" / "README.md"
STATUS_PATH = ARCH / "CANON-STATUS.json"
YIP0_STATE = ARCH / "yip0" / "YIP0-STATE.json"
ME0_STATE = ARCH / "me0" / "ME0-STATE.json"
ME1_STATE = ARCH / "me1" / "ME1-STATE.json"
QXM2_STATE = ARCH / "qxm2" / "QXM2-STATE.json"
YIM0_STATE = ARCH / "yim0" / "YIM0-STATE.json"
HUMAN_REVIEW_CARD = ARCH / "yim0" / "YIM0-HUMAN-REVIEW-CARD-v0.1.md"
BUILDER = ROOT / "scripts" / "build_canon_status.py"
BASE_SHA = "877c3bbc59fb6fc01b586b554930bdaca5db4c59"

GENESIS_ENGINES = {"ENG-C", "ENG-R", "ENG-X"}
SUCCESSOR_STATE_MODEL = ["ResearchTarget", "EngineThesis", "PositionPassport", "BookState"]
ALLOWED_EXACT = {
    "docs/os-vnext/README.md",
    "docs/architecture/CANON-STATUS.json",
    "docs/superpowers/specs/2026-08-22-yim0-yuanli-investment-methodology-map-projection-convergence-design.md",
    "docs/superpowers/plans/2026-08-22-yim0-yuanli-investment-methodology-map-projection-convergence.md",
    "scripts/build_canon_status.py",
    "scripts/validate_yim0_methodology_projection.py",
    "tests/test_yim0_methodology_projection.py",
    ".github/workflows/ci.yml",
}
ALLOWED_PREFIXES = (
    "docs/human-projection/",
    "docs/architecture/yim0/",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_human_projection_text(text: str) -> None:
    lower = text.lower()
    require("human navigation projection" in lower, "N1: Human Projection missing Authority Notice")
    require(
        "it does not create ontology, schema, registry, portfolio, trading, execution, or program-stage authority" in lower,
        "N1: Authority Notice missing zero-authority boundary",
    )
    for guard in (
        "Human Grammar != Machine Ontology",
        "Asset != Engine",
        "Target != Thesis != Position != Book",
        "Research pass != Capital pass",
        "ClaimAuthority <= EvidenceAuthority",
        "Roadmap visibility != Stage authorization",
    ):
        require(guard in text, f"Human Projection guard missing: {guard}")
    for phrase in (
        "yim0 authorizes trading",
        "yim0 authorizes portfolio",
        "yim0 authorizes me2",
        "this document creates ontology authority",
        "human grammar = machine ontology",
        "new machine object authority",
    ):
        require(phrase not in lower, f"N2/N10: prohibited authority claim: {phrase}")
    engines = set(re.findall(r"\bENG-[A-Z][A-Z0-9-]*\b", text))
    require(engines <= GENESIS_ENGINES, f"N10: Human Projection introduces unknown Engine authority {sorted(engines - GENESIS_ENGINES)}")
    for engine in GENESIS_ENGINES:
        require(engine in engines, f"missing Genesis Engine {engine}")
    require("Genesis Engine Set" in text and "open-world" in text, "C/R/X must remain an open-world Genesis Engine Set")
    require("No Silent Thesis Migration" in text, "No Silent Thesis Migration missing")
    require("roadmap visible / not authorized" in text, "ME2-ME5 roadmap authorization boundary missing")


def validate_readme_text(text: str) -> None:
    lower = text.lower()
    require("## Successor Architecture Bridge" in text, "README successor bridge missing")
    require("势 · 信 · 极｜真 · 价 · 生" in text, "N3: Human Grammar removed")
    require("one_core_three_worlds_three_gates_one_loop" in text, "Base OS identity regressed")
    require("X | 极 := (Xs, Xa, Xp)" in text, "historical X semantics regressed")
    require("Human Grammar is not Return Engine ontology" in text, "Human/Machine boundary missing")
    require("human grammar = c/r/x" not in lower, "N4: README equates Human Grammar with Machine Engines")
    require("researchstatevector is obsolete" not in lower, "README cannot erase historical RSV identity")
    require("Genesis Engine Set, not a proven exhaustive ontology" in text, "README must preserve open-world Engine semantics")


def validate_canon_status_data(status: dict) -> None:
    require(status.get("projection_semantics") == "deterministic_non_authoritative_projection", "CANON-STATUS projection semantics regressed")
    lineage = status.get("architecture_lineage", {})
    for stage in ("YIP0", "ME0", "ME1"):
        require(stage in lineage, f"N5: CANON-STATUS omits {stage}")
    state_arch = status.get("state_architecture", {})
    require(state_arch.get("historical_canonical_state") == "ResearchStateVector", "historical RSV identity missing")
    require(state_arch.get("successor_state_model") == SUCCESSOR_STATE_MODEL, "N6: successor state model missing or incorrect")
    require(state_arch.get("legacy_future_write_authority") is False, "N6: RSV cannot retain future write authority")
    require(status.get("legacy_compatibility", {}).get("authority") == "legacy_compatibility_only", "legacy singular fields must be compatibility-only")
    for stage in ("ME2", "ME3", "ME4", "ME5"):
        require(stage in lineage, f"roadmap stage missing: {stage}")
        require(lineage[stage].get("authorized") is False, f"N7: {stage} roadmap cannot be authorized")
    require(status.get("latest_completed_architecture_stage") == "ME1_COMPLETE", "latest architecture stage drift")
    require(status.get("roadmap_next_unapproved_stage") == "ME2", "roadmap next stage drift")
    require(status.get("next_stage_authorized") is False, "N7: ME2 cannot be authorized")
    programs = status.get("parallel_programs", {})
    require("research_capability_program" in programs, "N8: Research Capability / QXM program erased")
    require("multi_engine_program" in programs, "N8: Multi-Engine program erased")
    require(programs["multi_engine_program"].get("authorized") is False, "Multi-Engine successor authorization regression")
    require(status.get("gate_projection_semantics", "").startswith("legacy_"), "legacy single-gate compatibility must be explicit")


def validate_state_source_alignment_data(status: dict, yip0: dict, me0: dict, me1: dict, qxm2: dict) -> None:
    lineage = status["architecture_lineage"]
    require(lineage["YIP0"]["status"] == yip0["status"], "N9: YIP0 lifecycle projection not state-sourced")
    require(lineage["YIP0"]["completion_gate"] == yip0["next_gate"], "N9: YIP0 gate projection drift")
    require(lineage["ME0"]["status"] == me0["status"], "N9: ME0 lifecycle projection not state-sourced")
    require(lineage["ME0"]["completion_gate"] == me0["next_gate"], "N9: ME0 gate projection drift")
    require(lineage["ME1"]["status"] == me1["status"], "N9: ME1 lifecycle projection not state-sourced")
    require(lineage["ME1"]["completion_gate"] == me1["next_gate"], "N9: ME1 gate projection drift")
    capability = status["parallel_programs"]["research_capability_program"]
    require(capability["status"] == qxm2["status"], "QXM2 status projection drift")
    require(capability["next_gate"] == qxm2["next_gate"], "QXM2 current next gate projection drift")
    require(status["next_stage_authorized"] == me1["next_me_stage_authorized"], "ME1 successor authorization drift")


def validate_builder_source(source: str) -> None:
    for token in (
        '"qxm2" / "QXM2-STATE.json"',
        '"yip0" / "YIP0-STATE.json"',
        '"me0" / "ME0-STATE.json"',
        '"me1" / "ME1-STATE.json"',
        'yip0["status"]',
        'me0["status"]',
        'me1["status"]',
        'qxm2["next_gate"]',
    ):
        require(token in source, f"N9: builder missing state-source token {token}")


def validate_scope_paths(paths: list[str], *, enforce_yim0_scope: bool = True) -> None:
    """Protect YIM0 authority files without scope-locking the repository after YIM0 completion.

    During the YIM0 construction phase we fail closed unless every changed path is part of the
    approved YIM0 surface. After YIM0 is completed, unrelated future PRs are allowed, while the
    authority-bearing upstream artifacts remain protected.
    """
    require("README.md" not in paths, "N12: repository root README modification prohibited")
    require("docs/os-vnext/CONSTITUTION.md" not in paths, "N11: Constitution modification prohibited")
    require(not any(path.startswith("packages/contracts/schemas/") for path in paths), "N11: production schema modification prohibited")
    require(not any(path.startswith("docs/architecture/yip0/") for path in paths), "N11: accepted YIP0 artifacts modification prohibited")
    require(not any(path.startswith("docs/architecture/me0/") for path in paths), "N11: accepted ME0 artifacts modification prohibited")
    require(not any(path.startswith("docs/architecture/me1/") for path in paths), "N11: accepted ME1 artifacts modification prohibited")

    if not enforce_yim0_scope:
        return

    violations = []
    for path in paths:
        if path in ALLOWED_EXACT or any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        violations.append(path)
    require(not violations, f"N11/N12: YIM0 scope violation {violations}")


def changed_paths_from_git() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{BASE_SHA}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def validate_authority_boundaries(state: dict, review_card: str) -> None:
    authority = state.get("authority", {})
    require(authority.get("human_projection_only") is True, "YIM0 identity must remain Human Projection only")
    for key, value in authority.items():
        if key == "human_projection_only":
            continue
        require(value is False, f"YIM0 authority regression: {key}")
    gate = state.get("human_gate", {})
    require(gate.get("token") == "ACCEPT_YIM0_YUANLI_INVESTMENT_METHODOLOGY_MAP_PROJECTION_CONVERGENCE", "YIM0 Human Gate token mismatch")
    require(gate.get("acceptance_does_not_imply_merge") is True, "Human Acceptance cannot imply merge")
    require(gate.get("acceptance_does_not_authorize_ME2") is True, "Human Acceptance cannot authorize ME2")
    require(state.get("human_review_threshold") == "10/10 PASS", "Human Review threshold must be 10/10 PASS")
    for index in range(1, 11):
        require(f"## D{index}" in review_card, f"Human Review Card missing D{index}")


def main() -> int:
    human_projection = MAP_PATH.read_text(encoding="utf-8")
    readme = README_PATH.read_text(encoding="utf-8")
    status = load_json(STATUS_PATH)
    yip0 = load_json(YIP0_STATE)
    me0 = load_json(ME0_STATE)
    me1 = load_json(ME1_STATE)
    qxm2 = load_json(QXM2_STATE)
    yim0_state = load_json(YIM0_STATE)
    review_card = HUMAN_REVIEW_CARD.read_text(encoding="utf-8")
    builder_source = BUILDER.read_text(encoding="utf-8")

    validate_human_projection_text(human_projection)
    validate_readme_text(readme)
    validate_canon_status_data(status)
    validate_state_source_alignment_data(status, yip0, me0, me1, qxm2)
    validate_builder_source(builder_source)
    enforce_yim0_scope = not (
        yim0_state.get("status") == "human_accepted_merged"
        and yim0_state.get("next_gate") == "YIM0_COMPLETE"
    )
    validate_scope_paths(changed_paths_from_git(), enforce_yim0_scope=enforce_yim0_scope)
    validate_authority_boundaries(yim0_state, review_card)
    print("YIM0 methodology projection validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
