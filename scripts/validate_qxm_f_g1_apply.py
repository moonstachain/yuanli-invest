#!/usr/bin/env python3
"""Fail-closed validation for QXM-F G1 Human-accepted Registry apply."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator
from validate_qxm_f_closure import validate_qxm_f

ROOT = Path(__file__).resolve().parents[1]
G1 = ROOT / "docs" / "architecture" / "qxm-f" / "g1"
STATE = ROOT / "docs" / "architecture" / "qxm-f" / "QXM-F-STATE.json"
LEDGER = G1 / "QXM-F-G1-ADMISSION-LEDGER-v0.1.json"
REVIEW = G1 / "QXM-F-G1-HUMAN-REVIEW-CARD-v0.1.md"
ACCEPTANCE = G1 / "QXM-F-G1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
ADMISSION = G1 / "QXM-F-G1-ADMISSION-RECEIPT-v0.1.json"
THEORY_PACK = ROOT / "registry" / "theories" / "qxm-f-financial-mechanics-v0.1.json"
HYP_PACK = ROOT / "registry" / "hypotheses" / "qxm-f-financial-mechanics-v0.1.json"
SHADOW_THEORIES = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-SHADOW-THEORY-OBJECTS-v0.1.json"
SHADOW_HYPOTHESES = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json"
THEORY_SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "theory-object.schema.json"
HYP_SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "hypothesis-object.schema.json"

HUMAN_TOKEN = "ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION"
MERGE_TOKEN = "AUTHORIZE_QXM_F_G1_MERGE"
ACCEPTED_LEDGER_BLOB = "d6947465f1b19f3f22f2ebcddc65e3da9cf4d004"
ACCEPTED_REVIEW_BLOB = "57d23ed0489848c606febc1761d5d5b24db5bced"
KEEP_SHADOW_HYP = "HYP-V-202-OOS-DISCOUNT-RATE"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def changed_paths(root: Path):
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return []
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def assert_apply_scope(paths):
    prohibited_prefixes = ("registry/benchmarks/", "registry/capabilities/", "registry/providers/", "canon/")
    offenders = [p for p in paths if p.startswith(prohibited_prefixes)]
    assert not offenders, f"G1 apply authority exceeded: {offenders}"
    allowed_registry = {
        "registry/theories/qxm-f-financial-mechanics-v0.1.json",
        "registry/hypotheses/qxm-f-financial-mechanics-v0.1.json",
        "registry/theories/_index.json",
        "registry/hypotheses/_index.json",
        "registry/registry-index.json",
    }
    unexpected_registry = [p for p in paths if p.startswith("registry/") and p not in allowed_registry]
    assert not unexpected_registry, f"unexpected G1 Registry mutation: {unexpected_registry}"


def validate_core_phase_aware():
    """Run the full QXM-F core validator while delegating PR path authority to this G1 phase validator."""
    original_base_ref = os.environ.pop("GITHUB_BASE_REF", None)
    try:
        validate_qxm_f(ROOT)
    finally:
        if original_base_ref is not None:
            os.environ["GITHUB_BASE_REF"] = original_base_ref


def main():
    for path in (STATE, LEDGER, REVIEW, ACCEPTANCE, ADMISSION, THEORY_PACK, HYP_PACK, SHADOW_THEORIES, SHADOW_HYPOTHESES):
        assert path.exists(), f"missing G1 apply artifact: {path.relative_to(ROOT)}"

    validate_core_phase_aware()

    state = load_json(STATE)
    ledger = load_json(LEDGER)
    acceptance = load_json(ACCEPTANCE)
    admission = load_json(ADMISSION)
    theories = load_json(THEORY_PACK)
    hypotheses = load_json(HYP_PACK)

    assert git_blob_sha(LEDGER) == ACCEPTED_LEDGER_BLOB, "Human-reviewed G1 ledger drift"
    assert git_blob_sha(REVIEW) == ACCEPTED_REVIEW_BLOB, "Human-reviewed G1 review card drift"
    assert ledger["status"] == "candidate_ledger_human_pending"
    assert all(row["human_disposition"] is None for row in ledger["objects"]), "candidate ledger must remain immutable machine proposal"

    assert acceptance["decision"] == HUMAN_TOKEN
    assert acceptance["accepted_candidate"]["admission_ledger_blob_sha"] == ACCEPTED_LEDGER_BLOB
    assert acceptance["accepted_candidate"]["human_review_card_blob_sha"] == ACCEPTED_REVIEW_BLOB
    qual = acceptance["post_acceptance_reconciliation"]
    assert qual["qualified_head_sha"] == "6b23de9a0759f38da60fc4ebfcf05c7d3392e2df"
    assert qual["run_number"] == 256
    assert qual["run_id"] == 32470340324
    assert qual["conclusion"] == "success"
    for key in ("contracts", "governance", "qxm2", "qxm_f", "yip0", "unit_tests"):
        assert qual[key] == "success", (key, qual[key])
    assert acceptance["merge_authority"] == "not_implied_by_human_acceptance"
    assert acceptance["required_merge_token"] == MERGE_TOKEN
    assert all(value is False for value in acceptance["boundaries_preserved"].values())

    dispositions = acceptance["accepted_dispositions"]
    assert len(dispositions) == 30
    expected_theory_ids = {k for k, v in dispositions.items() if k.startswith("THEORY-") and v in {"ADMIT", "ADMIT_WITH_BOUNDARY"}}
    expected_hyp_ids = {k for k, v in dispositions.items() if k.startswith("HYP-") and v in {"ADMIT", "ADMIT_WITH_BOUNDARY"}}
    seed_ids = {k for k, v in dispositions.items() if k.startswith("QXM2-BSEED-") and v == "FORMALIZE"}
    assert len(expected_theory_ids) == 12
    assert len(expected_hyp_ids) == 11
    assert len(seed_ids) == 6
    assert dispositions[KEEP_SHADOW_HYP] == "KEEP_SHADOW"

    assert theories["entry_count"] == 12
    assert hypotheses["entry_count"] == 11
    assert {o["theory_id"] for o in theories["objects"]} == expected_theory_ids
    assert {o["hypothesis_id"] for o in hypotheses["objects"]} == expected_hyp_ids
    assert KEEP_SHADOW_HYP not in {o["hypothesis_id"] for o in hypotheses["objects"]}
    assert all(o["status"] == "proposed" for o in hypotheses["objects"])

    shadow_theory_map = {x["theory_object"]["theory_id"]: x["theory_object"] for x in load_json(SHADOW_THEORIES)["shadow_theories"]}
    shadow_hyp_map = {x["hypothesis_object"]["hypothesis_id"]: x["hypothesis_object"] for x in load_json(SHADOW_HYPOTHESES)["shadow_hypotheses"]}
    for obj in theories["objects"]:
        assert obj == shadow_theory_map[obj["theory_id"]], f"theory semantic mutation: {obj['theory_id']}"
    for obj in hypotheses["objects"]:
        assert obj == shadow_hyp_map[obj["hypothesis_id"]], f"hypothesis semantic mutation: {obj['hypothesis_id']}"

    theory_validator = Draft202012Validator(load_json(THEORY_SCHEMA))
    hyp_validator = Draft202012Validator(load_json(HYP_SCHEMA))
    for obj in theories["objects"]:
        theory_validator.validate(obj)
    for obj in hypotheses["objects"]:
        hyp_validator.validate(obj)

    tindex = load_json(ROOT / "registry" / "theories" / "_index.json")
    hindex = load_json(ROOT / "registry" / "hypotheses" / "_index.json")
    gindex = load_json(ROOT / "registry" / "registry-index.json")
    bindex = load_json(ROOT / "registry" / "benchmarks" / "_index.json")
    assert tindex["entry_count"] == 31 and "qxm-f-financial-mechanics-v0.1.json" in tindex["pack_files"]
    assert hindex["entry_count"] == 23 and "qxm-f-financial-mechanics-v0.1.json" in hindex["pack_files"]
    assert gindex["entry_count_total"] == 122
    assert gindex["entry_count_total"] == sum(x["entry_count"] for x in gindex["registries"])
    assert bindex["entry_count"] == 7
    assert all("qxm" not in name.lower() for name in bindex.get("pack_files", [])), "G1 must not create QXM BenchmarkObject pack"

    assert admission["human_acceptance"] == HUMAN_TOKEN
    assert admission["registry_delta"] == {
        "theories_before": 19, "theories_added": 12, "theories_after": 31,
        "hypotheses_before": 12, "hypotheses_added": 11, "hypotheses_after": 23,
        "registry_total_before": 99, "registry_total_added": 23, "registry_total_after": 122,
    }
    assert admission["formal_benchmark_objects_created"] == 0
    assert admission["hypotheses_preregistered"] == 0
    assert admission["capabilities_promoted"] == 0
    assert admission["production_runtime_activated"] is False
    assert admission["required_next_authority"] == MERGE_TOKEN
    assert all(value is False for value in admission["boundaries_preserved"].values())

    g1 = state["g1"]
    assert g1["human_decision"] == HUMAN_TOKEN
    assert g1["registry_apply_state"] == "human_accepted_ready_for_merge"
    assert g1["theory_registry_admissions_applied"] == 12
    assert g1["hypothesis_registry_admissions_applied"] == 11
    assert g1["hypothesis_kept_shadow"] == 1
    assert g1["benchmark_seed_formalize_dispositions"] == 6
    assert g1["hypothesis_preregistration_performed"] is False
    assert g1["formal_benchmark_creation_performed"] is False
    assert g1["benchmark_execution_performed"] is False
    assert g1["capability_promotion_performed"] is False
    assert g1["required_merge_token"] == MERGE_TOKEN
    for key in ("hypothesis_preregistration_authority", "formal_benchmark_creation_authority", "benchmark_execution_authority", "capability_promotion_authority", "production_runtime_authority", "trading_authority"):
        assert state[key] == "none", (key, state[key])

    assert_apply_scope(changed_paths(ROOT))
    print("QXM-F G1 Human-accepted Registry apply validation: PASS theories=12 hypotheses=11 keep_shadow=1 benchmarks_created=0")


if __name__ == "__main__":
    main()
