from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
YIOS0 = ROOT / "docs" / "architecture" / "yios0"
ARCH = ROOT / "config" / "yios0" / "yios0_architecture.v1.json"
CURRENT = ROOT / "config" / "yios0" / "yios0_current.json"
CANON = YIOS0 / "YIOS0-CANONICAL-ARCHITECTURE-v1.0.md"
HUMAN_CURRENT = YIOS0 / "YIOS0-CURRENT.md"
STATUS = YIOS0 / "YIOS0-STATUS-MATRIX.md"
CHANGELOG = YIOS0 / "YIOS0-CHANGELOG.md"
PROJECTION = YIOS0 / "YIOS0-NOTION-PROJECTION-CONTRACT-v1.0.md"
ACCEPTANCE = YIOS0 / "YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json"

# Accepted child-authority sentinel blobs from protected main @
# e2f06e039dccca45d178ab017654005cdb135666.  YIOS0 is not allowed to
# silently rewrite these subordinate authorities while composing the system.
IMMUTABLE_CHILD_SENTINELS = {
    "docs/architecture/yip0/YIP0-MERGE-RECEIPT-v0.1.json": "f38b841d7fe446f44e83430a6e1daa5d0395203e",
    "docs/architecture/me0/ME0-MERGE-RECEIPT-v0.1.json": "1110907a5af27e69a9d944c4d34ca7badd63f799",
    "docs/architecture/me1/ME1-MERGE-RECEIPT-v0.1.json": "00fce1cd894a8670229263df45a65a37e6555d5b",
    "docs/architecture/yex0/YEX0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json": "9c0c60ac7cbd6b03663c9e48fe293303fa0355ff",
    "docs/architecture/yvn1/YVN1-A0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json": "00558f5bd39d0969fd02ff5c291dcb7d05139fa9",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity, not cryptographic security


def validate_required_files() -> None:
    for path in (ARCH, CURRENT, CANON, HUMAN_CURRENT, STATUS, CHANGELOG, PROJECTION):
        require(path.exists(), f"required YIOS0 artifact missing: {path.relative_to(ROOT)}")


def validate_current_pointer() -> None:
    current = load_json(CURRENT)
    require(current["system_id"] == "YIOS0", "current pointer system id drift")
    require(current["current_architecture_version"] == "1.0.0", "current architecture version drift")
    require(
        current["canonical_architecture_path"] == "docs/architecture/yios0/YIOS0-CANONICAL-ARCHITECTURE-v1.0.md",
        "canonical architecture pointer drift",
    )
    require(
        current["machine_contract_path"] == "config/yios0/yios0_architecture.v1.json",
        "machine contract pointer drift",
    )
    require(
        current["status_projection_path"] == "docs/architecture/yios0/YIOS0-STATUS-MATRIX.md",
        "status projection pointer drift",
    )
    require(current["runtime_status_is_separate"] is True, "runtime status collapsed into architecture version")
    require("human_accepted_merged" not in json.dumps(current), "current pointer is self-authorizing")
    require(
        current["authority_policy"] == "current_only_when_present_on_protected_main_with_valid_human_acceptance",
        "current pointer authority policy drift",
    )

    human = HUMAN_CURRENT.read_text(encoding="utf-8")
    for token in (
        "1.0.0",
        "YIOS0-CANONICAL-ARCHITECTURE-v1.0.md",
        "yios0_architecture.v1.json",
        "YIOS0-STATUS-MATRIX.md",
        "protected-main presence + valid Human Acceptance Receipt + post-merge Reality readback",
    ):
        require(token in human, f"human current pointer missing invariant: {token}")


def validate_machine_contract() -> None:
    arch = load_json(ARCH)
    required_blocks = {
        "identity",
        "versioning",
        "strategic_positioning",
        "mother_loop",
        "mother_laws",
        "authority_topology",
        "knowledge_spine",
        "action_spine",
        "buses",
        "human_layers",
        "machine_services",
        "experience_plane",
        "deployment_domains",
        "status_semantics",
        "projection_contract",
        "bootstrap_contract",
        "non_authorizations",
    }
    require(required_blocks.issubset(arch), "machine contract required block missing")

    identity = arch["identity"]
    require(identity["system_id"] == "YIOS0", "machine system id drift")
    require(identity["architecture_version"] == "1.0.0", "machine architecture version drift")
    require(identity["composition_canon"] is True, "YIOS0 must remain composition authority")
    require(identity["subordinate_canons_retain_domain_authority"] is True, "child Canon authority swallowed")

    require(
        arch["mother_loop"]
        == ["Reality", "Knowledge", "Trial", "Settlement", "Capital", "Execution", "Reality", "Learning"],
        "mother loop drift",
    )
    for law in (
        "Reality > Belief",
        "Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition",
        "ResearchPass != CapitalPass",
        "ResearchAuthority != CapitalAuthority != ExecutionAuthority",
    ):
        require(law in arch["mother_laws"], f"mother law missing: {law}")

    authority = arch["authority_topology"]
    require(authority["yios0_can_promote_child_authority"] is False, "YIOS0 escalated child authority")
    require(authority["claim_authority_lte_evidence_authority"] is True, "ClaimAuthority law drift")
    require(authority["research_pass_ne_capital_pass"] is True, "ResearchPass/CapitalPass separation drift")
    require(authority["research_capital_execution_separate"] is True, "authority separation drift")
    require(
        authority["credential_separation"]
        == "ResearchCredential != CapitalCredential != ExecutionCredential != BrokerCredential",
        "credential separation drift",
    )
    require(authority["research_production_has_broker_write_authority"] is False, "research gained broker write authority")

    require(
        arch["knowledge_spine"]
        == ["External Reality", "Evidence", "PIT", "State", "Research Capability", "Trial", "Research Settlement", "Learning"],
        "Knowledge Spine drift",
    )
    require(
        arch["action_spine"]
        == [
            "Research Settlement",
            "Capital Admission",
            "PositionPassport",
            "ExecutionIntent",
            "ActionContract",
            "Execution Runtime",
            "Broker Reality",
            "Reconciliation",
            "Execution Settlement",
        ],
        "Action Spine drift",
    )

    buses = arch["buses"]
    require(set(buses) >= {"reality_bus", "intelligence_bus", "action_bus"}, "three-bus topology incomplete")
    require(buses["reality_bus_ne_action_bus"] is True, "Reality Bus aliased to Action Bus")
    require(buses["read_side_credential_cannot_become_execution_authority"] is True, "read credential escalated")

    human_layers = arch["human_layers"]
    require(len(human_layers) == 13, "human architecture must remain L0-L12")
    require([layer["id"] for layer in human_layers] == [f"L{i}" for i in range(13)], "human layer identity drift")

    services = arch["machine_services"]
    require(len(services) == 8, "machine service boundary count drift")
    require([service["id"] for service in services] == [f"M{i}" for i in range(1, 9)], "machine service identity drift")

    experience = arch["experience_plane"]
    require(experience["notion"]["authoritative"] is False, "Notion promoted to authority")
    require(experience["notion"]["canon_write_authority"] is False, "Notion gained Canon write authority")
    require(experience["web"]["authoritative_state_source"] is False, "Web promoted to truth")

    semantics = arch["status_semantics"]
    require(semantics["axes"] == ["authority_state", "reality_state", "runtime_state"], "status axes drift")
    require(semantics["single_pass_label_sufficient"] is False, "single PASS collapsed three-axis state")
    require(semantics["status_matrix_is_projection"] is True, "status matrix promoted to truth")

    versioning = arch["versioning"]
    require(versioning["runtime_status_is_separate"] is True, "version/status separation drift")
    require(versioning["runtime_only_change_bumps_architecture_version"] is False, "runtime status now bumps architecture")

    projection = arch["projection_contract"]
    require(projection["direction"] == "GitHub Canon → Projection Contract → Notion Human Projection", "projection direction drift")
    require(projection["one_way"] is True, "projection is not one-way")
    require(projection["notion_can_directly_mutate_canon"] is False, "Notion direct Canon mutation enabled")

    require(arch["bootstrap_contract"]["architecture_context_ne_task_evidence"] is True, "architecture substituted for task evidence")
    for key, value in arch["non_authorizations"].items():
        require(value is False, f"YIOS0 escalated non-authorized capability: {key}")


def parse_status_rows(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.startswith("|")]
    require(len(lines) >= 3, "status table missing")
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def validate_status_projection() -> None:
    text = STATUS.read_text(encoding="utf-8")
    for token in (
        "STATUS_MATRIX_IS_PROJECTION = true",
        "status_known_as_of",
        "authority_state",
        "reality_state",
        "runtime_state",
        "evidence_ref",
        "open_authority_gap",
        "YMQ4-B3",
        "SCIENTIFIC_NO_GO",
        "PR #72",
        "DYNAMIC_BETA_DOES_NOT_BEAT_B2",
        "YGR0",
        "YRP1",
        "State Compiler",
        "YAU1",
        "YVN1-A1",
        "VeighNa Adapter",
        "Broker Paper",
        "Live Execution",
    ):
        require(token in text, f"status projection missing required signal: {token}")
    require("| PASS |" not in text, "status projection collapsed state to a single PASS")

    rows = parse_status_rows(text)
    by_component = {row["Component"]: row for row in rows}
    expected = {
        "YIP0": ("CANON_ACCEPTED_MERGED", "NOT_APPLICABLE", "MAIN_ACTIVE"),
        "ME0 / ME1": ("CANON_ACCEPTED_MERGED", "NOT_APPLICABLE", "MAIN_ACTIVE"),
        "Gold DP1-A / DP1-B / B2": ("CANON_ACCEPTED_MERGED", "REALITY_PROVEN", "MAIN_ACTIVE"),
        "YMQ4-B3": ("NONE", "SCIENTIFIC_NO_GO", "CANDIDATE_BRANCH"),
        "YGR0": ("DESIGN_CANDIDATE", "NOT_RUN", "DESIGN_ONLY"),
        "YRP1": ("ARCHITECTURE_ACCEPTED", "NOT_RUN", "NOT_IMPLEMENTED"),
        "State Compiler": ("NONE", "NOT_RUN", "NOT_IMPLEMENTED"),
        "YAU1 Notion Portal": ("DESIGN_CANDIDATE", "NOT_RUN", "DESIGN_ONLY"),
        "YEX0": ("CANON_ACCEPTED_MERGED", "NOT_APPLICABLE", "MAIN_ACTIVE"),
        "YVN1-A0": ("CANON_ACCEPTED_MERGED", "NOT_APPLICABLE", "MAIN_ACTIVE"),
        "YVN1-A1": ("NONE", "NOT_RUN", "NOT_AUTHORIZED"),
        "VeighNa Adapter": ("NONE", "NOT_RUN", "NOT_AUTHORIZED"),
        "Broker Paper": ("NONE", "NOT_RUN", "NOT_AUTHORIZED"),
        "Live Execution": ("NONE", "NOT_RUN", "NOT_AUTHORIZED"),
    }
    for component, states in expected.items():
        require(component in by_component, f"status row missing: {component}")
        row = by_component[component]
        require(
            (row["authority_state"], row["reality_state"], row["runtime_state"]) == states,
            f"status row drift: {component}",
        )
        require(row["status_known_as_of"], f"status row lacks known-as-of: {component}")
        require(row["evidence_ref"], f"status row lacks evidence reference: {component}")
        require(row["open_authority_gap"], f"status row lacks authority-gap field: {component}")
        if row["reality_state"] == "REALITY_PROVEN":
            require("Reality" in row["evidence_ref"] or "REALITY" in row["evidence_ref"], "REALITY_PROVEN without Reality evidence")

    b3 = by_component["YMQ4-B3"]
    require("Draft / Open / Not Merged" in b3["open_authority_gap"], "B3 not-merged gap lost")
    require("DYNAMIC_BETA_DOES_NOT_BEAT_B2" in b3["open_authority_gap"], "B3 scientific NO-GO lost")


def validate_projection_contract() -> None:
    text = PROJECTION.read_text(encoding="utf-8")
    for token in (
        "GitHub Canon → Projection Contract → Notion Human Projection",
        "原力投研 OS｜最新版定义",
        "NotionVerification != ResearchSettlement",
        "Notion Edit → Direct Canon Mutation",
        "FORBIDDEN",
        "ACCEPT_YIOS0_CANONICAL_DEFINITION",
        "AUTHORIZE_YIOS0_MERGE",
        "ACCEPT_YIOS0_NOTION_PROJECTION",
    ):
        require(token in text, f"projection contract missing invariant: {token}")


def validate_canonical_human_definition() -> None:
    text = CANON.read_text(encoding="utf-8")
    for token in (
        "YIP0 remains philosophy authority",
        "Reality → Knowledge → Trial → Settlement → Capital → Execution → Reality → Learning",
        "ResearchAuthority != CapitalAuthority != ExecutionAuthority",
        "Knowledge Spine",
        "Action Spine",
        "Reality Bus",
        "Intelligence Bus",
        "Action Bus",
        "YVN1-A1",
        "VeighNa",
        "Broker Paper",
        "Live Execution",
        "NOT_AUTHORIZED",
    ):
        require(token in text, f"canonical architecture missing invariant: {token}")


def validate_child_authority_sentinels() -> None:
    for rel_path, expected_sha in IMMUTABLE_CHILD_SENTINELS.items():
        path = ROOT / rel_path
        require(path.exists(), f"accepted child authority missing: {rel_path}")
        actual = git_blob_sha(path)
        require(actual == expected_sha, f"accepted child authority mutated by YIOS0: {rel_path}")

    yex0 = load_json(ROOT / "docs/architecture/yex0/YEX0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json")
    require(yex0["decision"] == "ACCEPT_YEX0_CAPITAL_EXECUTION_CONSTITUTION", "YEX0 acceptance drift")
    require(yex0["boundaries_preserved"]["live_execution_authorized"] is False, "YEX0 live boundary drift")
    require(yex0["boundaries_preserved"]["broker_paper_authorized"] is False, "YEX0 broker-paper boundary drift")

    yvn1 = load_json(ROOT / "docs/architecture/yvn1/YVN1-A0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json")
    require(yvn1["decision"] == "ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE", "YVN1-A0 acceptance drift")
    require(yvn1["boundaries_preserved"]["a1_runtime_authorized"] is False, "YVN1-A1 silently authorized")
    require(yvn1["boundaries_preserved"]["veighna_invocation_authorized"] is False, "VeighNa silently authorized")
    require(yvn1["boundaries_preserved"]["broker_paper_authorized"] is False, "broker paper silently authorized")
    require(yvn1["boundaries_preserved"]["live_execution_authorized"] is False, "live execution silently authorized")
    require(yvn1["boundaries_preserved"]["real_capital_movement_authorized"] is False, "real capital silently authorized")


def validate_human_acceptance_if_present() -> None:
    if not ACCEPTANCE.exists():
        return
    receipt = load_json(ACCEPTANCE)
    require(receipt["system_id"] == "YIOS0", "acceptance receipt system drift")
    require(receipt["architecture_version"] == "1.0.0", "acceptance receipt version drift")
    require(receipt["decision"] == "ACCEPT_YIOS0_CANONICAL_DEFINITION", "acceptance token drift")
    require(receipt["merge_authority"] == "not_implied_by_acceptance", "G2 silently authorized merge")
    require(receipt["required_merge_token"] == "AUTHORIZE_YIOS0_MERGE", "G3 token drift")
    require(receipt["next_gate"] == "YIOS0_POST_ACCEPTANCE_CI", "post-acceptance gate drift")
    for key, value in receipt["boundaries_preserved"].items():
        require(value is False, f"G2 escalated downstream authority: {key}")


def validate_yios0() -> None:
    validate_required_files()
    validate_current_pointer()
    validate_machine_contract()
    validate_status_projection()
    validate_projection_contract()
    validate_canonical_human_definition()
    validate_child_authority_sentinels()
    validate_human_acceptance_if_present()
    print("YIOS0_CANONICAL_DEFINITION_MACHINE_CONTRACT_VALID")


if __name__ == "__main__":
    validate_yios0()
