from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_runtime.yma55.blind import resolve_blind_packet, validate_blind_packet

H41 = ROOT / "fixtures" / "replay" / "yma55_h4_1"
H4 = ROOT / "fixtures" / "replay" / "yma55_h4"
FREEZE_COMMIT = "805a5c52f6918c0f4339128ef5e95883de5fbf89"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"YMA55-H4.1 qualification FAIL: {message}")


def git_ok(*args: str) -> bool:
    result = subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def validate_freeze_sequence() -> None:
    require(git_ok("merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"), "blind freeze commit must be an ancestor of HEAD")
    require(git_ok("cat-file", "-e", f"{FREEZE_COMMIT}:fixtures/replay/yma55_h4_1/blind_resolution_freeze.json"), "freeze artifact must exist at freeze commit")
    require(not git_ok("cat-file", "-e", f"{FREEZE_COMMIT}:fixtures/replay/yma55_h4_1/post_resolution_unblinding.json"), "unblinding artifact must not exist at blind freeze commit")
    frozen_then = git_text("show", f"{FREEZE_COMMIT}:fixtures/replay/yma55_h4_1/blind_resolution_freeze.json")
    frozen_now = (H41 / "blind_resolution_freeze.json").read_text(encoding="utf-8")
    require(json.loads(frozen_then) == json.loads(frozen_now), "blind freeze artifact must remain immutable after unblinding")


def validate_blind_freeze() -> dict:
    freeze = load(H41 / "blind_resolution_freeze.json")
    require(freeze["blindness_grade"] == "B_PIPELINE_BLIND", "freeze must retain pipeline blindness grade")
    require(freeze["historical_role_mapping_exposed"] is False, "historical role mapping must be hidden at freeze")
    require(freeze["capital_authority"] is False, "freeze cannot grant capital authority")
    text = json.dumps(freeze, ensure_ascii=False)
    for forbidden in ("sealed_mapping", "case_type", "episode_id", "settlement", "GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE", "YMA55-H4-"):
        require(forbidden not in text, f"role/outcome leakage in freeze: {forbidden}")

    manifest = load(H41 / "blind_manifest.json")
    recomputed = []
    for rel in manifest["case_files"]:
        packet = load(H41 / rel)
        validate_blind_packet(packet)
        result = resolve_blind_packet(packet)
        recomputed.append({"blind_case_id": result["blind_case_id"], "resolution": result["resolution"]})
    require(freeze["resolutions"] == recomputed, "frozen resolutions must recompute from blind packets only")
    require(len(recomputed) == 12, "exactly 12 blind resolutions required")
    return freeze


def validate_unblinding(freeze: dict) -> dict:
    mapping = {x["blind_case_id"]: x for x in load(H41 / "sealed_mapping.json")["cases"]}
    unblind = load(H41 / "post_resolution_unblinding.json")
    require(unblind["blind_freeze_commit_sha"] == FREEZE_COMMIT, "unblinding must bind exact blind freeze commit")
    require(unblind["status"] == "POST_RESOLUTION_UNBLINDED", "post-resolution status required")
    require(unblind["historical_gold_admission"] is False, "H4.1 cannot admit historical Gold")
    require(unblind["capital_authority"] is False, "H4.1 cannot grant capital authority")
    require(unblind["incremental_value_claim"] == "NOT_YET_ESTABLISHED", "incremental superiority must remain blocked without baseline")

    frozen = {x["blind_case_id"]: x["resolution"] for x in freeze["resolutions"]}
    rows = unblind["cases"]
    require(len(rows) == 12, "exactly 12 unblinded rows required")
    for row in rows:
        blind_id = row["blind_case_id"]
        require(blind_id in mapping, f"unknown blind id in unblinding: {blind_id}")
        require(row["episode_id"] == mapping[blind_id]["episode_id"], f"episode mapping mismatch: {blind_id}")
        require(row["case_type"] == mapping[blind_id]["case_type"], f"case role mismatch: {blind_id}")
        require(row["mechanism_family"] == mapping[blind_id]["mechanism_family"], f"mechanism family mismatch: {blind_id}")
        require(row["machine_resolution"] == frozen[blind_id], f"frozen machine resolution changed: {blind_id}")

    summary = unblind["summary"]
    expected = {
        "total_cases": 12,
        "matches": 10,
        "mismatches": 1,
        "evidence_abstentions": 1,
        "fully_hydrated_cases": 11,
        "fully_hydrated_matches": 10,
        "fully_hydrated_mismatches": 1,
        "fully_hydrated_mechanism_accuracy": "10/11",
        "safe_or_correct_outcomes": "11/12",
    }
    for key, value in expected.items():
        require(summary[key] == value, f"truthful summary mismatch for {key}")
    require(summary["critical_miss"] == "H41-B11 / 2020 Gold wrong-mechanism case", "critical mismatch must stay visible")
    require(summary["critical_abstention"] == "H41-B09 / 1971 Gold partial-hydration case", "evidence abstention must stay visible")
    return unblind


def validate_hydration_and_authority(unblind: dict) -> None:
    packets = sorted((H41 / "hydration").glob("*.json"))
    require(len(packets) == 12, "exactly 12 hydration packets required")
    statuses = [load(path)["hydration_status"] for path in packets]
    require(statuses.count("EVIDENCE_HYDRATED") == 11, "11 fully hydrated packets required")
    require(statuses.count("PARTIAL_HYDRATION") == 1, "one partial-hydration packet required")

    manifest = load(H4 / "manifest.json")
    for mechanism in manifest["mechanisms"].values():
        for entry in mechanism["cases"]:
            case = load(ROOT / entry["path"])
            require(case["gold_qualified"] is False, "original H4 cases must remain non-Gold")
            require(case["evidence_status"] == "needs_primary_hydration", "H4 candidate history must not be silently rewritten")

    require(unblind["historical_gold_admission"] is False, "historical Gold admission remains zero")
    require(unblind["capital_authority"] is False, "capital authority remains zero")


def main() -> None:
    validate_freeze_sequence()
    freeze = validate_blind_freeze()
    unblind = validate_unblinding(freeze)
    validate_hydration_and_authority(unblind)
    print(
        "YMA55-H4.1 qualification: PASS "
        "cases=12 hydrated=11 partial=1 matches=10 mismatch=1 abstention=1 "
        "fully_hydrated_accuracy=10/11 gold_admission=0 capital_authority=0 "
        "incremental_superiority=NOT_YET_ESTABLISHED"
    )


if __name__ == "__main__":
    main()
