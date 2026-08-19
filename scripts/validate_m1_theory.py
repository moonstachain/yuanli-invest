#!/usr/bin/env python3
"""Validate M1.1 PNX-S theory hardening invariants.

This is a documentation/theory gate only. It must not infer research admission,
contract migration, production authorization or trading authority.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "methodology"

REQUIRED = [
    M / "force-investing-system-v0.2.md",
    M / "theory-lineage-pnxs-v0.1.md",
    M / "extreme-engine-v0.1.md",
    M / "survival-constitution-v0.1.md",
    M / "valuation-as-strike-v0.1.md",
    M / "falsifiable-hypotheses-v0.1.md",
    M / "epistemic-boundaries-force-system-v0.2.md",
    M / "M1-1-HUMAN-REVIEW-CARD-v0.2.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
    assert not missing, f"missing M1.1 theory files: {missing}"

    system = read(M / "force-investing-system-v0.2.md")
    extreme = read(M / "extreme-engine-v0.1.md")
    survival = read(M / "survival-constitution-v0.1.md")
    valuation = read(M / "valuation-as-strike-v0.1.md")
    hypotheses = read(M / "falsifiable-hypotheses-v0.1.md")
    boundaries = read(M / "epistemic-boundaries-force-system-v0.2.md")

    for token in [
        "P｜Paradigm",
        "N｜Narrative",
        "X｜Extreme Convexity",
        "S｜Survival",
        "E｜Evidence",
        "V｜Valuation",
    ]:
        assert token in system, f"missing core PNX-S token: {token}"

    for token in ["Xs｜Structural Right Tail", "Xa｜Tail Activation", "Xp｜Payoff Convexity"]:
        assert token in extreme, f"missing Extreme Engine split: {token}"

    assert "Never Risk the Right to Compound" in survival
    assert "Issuer Durability" in survival
    assert "Portfolio Survival" in survival
    assert "full Kelly" in survival

    assert "Strike Price" in valuation
    assert "不是黄金三角的第四个顶点" in valuation

    for hypothesis in ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"]:
        assert hypothesis in hypotheses, f"missing falsifiable hypothesis {hypothesis}"
    assert "WTCR" in hypotheses
    assert "ablation" in hypotheses.lower()

    for prohibited_shortcut in [
        "predictive",
        "causal_candidate",
        "identified",
        "full Kelly",
        "point-in-time",
    ]:
        assert prohibited_shortcut in boundaries, f"missing epistemic boundary: {prohibited_shortcut}"

    # M1.1 is theory-only; these explicit boundaries must remain visible.
    assert "不修改 Q0 已冻结的生产合同" in system
    assert "不修改 Q1 Data Qualification" in system
    assert "不授权仓位、交易、目标价或 live execution" in system

    print("M1.1 PNX-S theory validation: PASS")


if __name__ == "__main__":
    main()
