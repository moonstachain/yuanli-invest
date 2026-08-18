#!/usr/bin/env python3
"""Compile reviewed local baselines into versioned clean-room Canon objects."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
from datetime import date
from pathlib import Path


SCHEMA_VERSION = "1.0.0"
DECISION_ID = "YL-DEC-A9-20260818-0001"
TASK_ID = "yuanli-invest-mvp-bootstrap-20260818"
TRACE_ID = "TRACE-A9-YUANLI-INVEST-20260818-0001"
IMPORT_AT = "2026-08-18T16:20:00+08:00"

EXPECTED_HASHES = {
    "evidence_ledger": "5681e65e902c0f025d24021ba2d8608df872d51c158e5e347af6e06a6e517bb2",
    "historical_replay": "330459073123b4fe75369f52926e8edf38c39894939567a9dedb0b7f4f3622c1",
    "narratives": "ba6ccc718f2714c8cfe3695f0054c6a40241f2bb735f7f6c8cf9f287eaba4d07",
    "companies": "1c852ddfe4c6df37f62e8f134f4012cbde111565f6f37e2541c2b7c3c457fe7e",
    "mappings": "8b836a423d6ce1acce5e9058ac1a78003fc994fe7caba0f3d66db14fe3cd0cdf",
    "classic_evidence": "856c1c44d0ec213af782b57f5e38684954fd017f1d6843d961da8d253e330acf",
    "identity_additions": "d4011e4e8d0c7af02d83b6cd0310366d97f637edca2654a1db1a8a707f3b8264",
}

NARRATIVE_FOR_REPLAY = {
    "HR01": "narrative-app-agent",
    "HR02": "narrative-compute",
    "HR03": "narrative-compute",
    "HR04": "narrative-robotics",
    "HR05": "narrative-edge-device",
    "HR06": "narrative-ai-health",
    "HR07": "narrative-data-infra",
    "HR08": "narrative-edge-device",
}

IDENTITY_EVIDENCE = {
    "301043": "E037",
    "300446": "E038",
    "600636": "E039",
    "600745": "E040",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path, label: str) -> None:
    actual = sha256(path)
    expected = EXPECTED_HASHES[label]
    if actual != expected:
        raise SystemExit(f"source_revision_drift:{label}:{actual}")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def clear_generated(directory: Path) -> None:
    if directory.name not in {"canon", "baseline-import"}:
        raise SystemExit(f"refusing_generated_cleanup:{directory}")
    if directory.exists():
        for path in directory.rglob("*.json"):
            path.unlink()


def date_from(value: str, fallback: str = "2026-08-18") -> str:
    if match := re.match(r"^(\d{4})-(\d{2})-(\d{2})", value or ""):
        return "-".join(match.groups())
    if match := re.match(r"^(\d{4})-(\d{2})", value or ""):
        return f"{match.group(1)}-{match.group(2)}-01"
    if match := re.match(r"^(\d{4})", value or ""):
        return f"{match.group(1)}-01-01"
    return fallback


def as_datetime(value: str) -> str:
    if "T" in value:
        return value
    return f"{date_from(value)}T23:59:59+08:00"


def shift_months(value: str, months: int) -> str:
    current = date.fromisoformat(date_from(value))
    month_index = current.year * 12 + current.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    day = min(current.day, calendar.monthrange(year, month)[1])
    return date(year, month, day).isoformat()


def base(
    *, object_id: str, object_type: str, status: str, as_of: str,
    valid_from: str, source_hash: str, source_revision: str,
    method: str, source_group: str, review_state: str,
):
    return {
        "id": object_id,
        "object_type": object_type,
        "version": "1.0.0",
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "as_of": as_datetime(as_of),
        "valid_from": date_from(valid_from),
        "valid_to": None,
        "provenance": {
            "source_group": source_group,
            "method": method,
            "review_state": review_state,
        },
        "source_snapshot_hash": source_hash,
        "portfolio_id": "A9",
        "decision_id": DECISION_ID,
        "task_id": TASK_ID,
        "trace_id": TRACE_ID,
        "source_revision": source_revision,
    }


def media_type(url: str) -> str:
    lowered = url.lower()
    if lowered.endswith(".pdf"):
        return "application/pdf"
    if "youtube.com" in lowered:
        return "video/web"
    return "text/html"


def import_evidence(research_dir: Path, classic_dir: Path):
    ledger_path = research_dir / "evidence-ledger.json"
    classic_path = classic_dir / "public" / "snapshots" / "latest" / "evidence.json"
    additions_path = classic_dir / "data" / "classic" / "evidence-additions.json"
    ledger = read_json(ledger_path)
    classic = read_json(classic_path)["items"]
    additions = read_json(additions_path)[:4]
    classic_locators = {
        item["id"]: item["locator"]
        for item in classic
        if item["id"] <= "E034" and item.get("locator")
    }

    rows = []
    for item in ledger["evidence"]:
        locator = classic_locators.get(item["id"], "source landing page; exact locator pending independent review")
        rows.append((item, item["id"], locator, EXPECTED_HASHES["evidence_ledger"], "evidence_ledger_clean_room_import"))

    for new_id, item in zip(("E037", "E038", "E039", "E040"), additions, strict=True):
        rows.append((item, new_id, item["locator"], EXPECTED_HASHES["identity_additions"], "identity_governance_addition"))

    evidence = []
    source_records = []
    for item, evidence_id, locator, source_hash, method in rows:
        issuer = item.get("author_or_issuer") or item.get("issuer") or "unknown"
        published_at = item.get("published_at", "unknown")
        independent_group = item.get("independent_group", f"source-{evidence_id.lower()}")
        source_record_id = f"SR-{evidence_id}"
        source_revision = f"sha256:{source_hash}"
        source_record = base(
            object_id=source_record_id, object_type="SourceRecord", status="partial",
            as_of=item.get("as_of", "2026-08-18"), valid_from=published_at,
            source_hash=source_hash, source_revision=source_revision,
            method="logical_source_registry_import", source_group=independent_group,
            review_state="vault_snapshot_not_frozen",
        )
        source_record.update({
            "source_url": item["url"],
            "logical_locator": locator,
            "vault_hash": None,
            "vault_status": "not_frozen",
            "copyright_status": "public" if method == "identity_governance_addition" else "unknown",
            "acquired_at": as_datetime(item.get("as_of", "2026-08-18")),
            "media_type": media_type(item["url"]),
        })
        source_records.append(source_record)

        stance = item.get("stance")
        if not stance:
            stance = "method" if evidence_id in {f"E{i:03d}" for i in range(1, 14)} | {f"E{i:03d}" for i in range(30, 37)} else "support"
        evidence_item = base(
            object_id=evidence_id, object_type="Evidence", status="partial",
            as_of=item.get("as_of", "2026-08-18"), valid_from=published_at,
            source_hash=source_hash, source_revision=source_revision,
            method=method, source_group=independent_group,
            review_state="grade_imported_not_reapproved",
        )
        evidence_item.update({
            "title": item["title"],
            "issuer": issuer,
            "published_at": published_at,
            "grade": item["grade"],
            "source_type": item["source_type"],
            "url": item["url"],
            "logical_locator": locator,
            "independent_group": independent_group,
            "interest_position": item.get("interest_position", "unknown"),
            "stance": stance,
            "supports": item["supports"],
            "source_record_id": source_record_id,
        })
        evidence.append(evidence_item)
    return evidence, source_records


def import_narratives(classic_dir: Path):
    source = classic_dir / "public" / "snapshots" / "latest" / "narratives.json"
    rows = []
    for item in read_json(source)["items"]:
        counter = item.get("counter_narratives") or ["反向证据尚未冻结"]
        origin = item["origin"]
        row = base(
            object_id=item["id"], object_type="Narrative", status="partial",
            as_of=item["as_of"], valid_from=item["valid_from"],
            source_hash=EXPECTED_HASHES["narratives"],
            source_revision="local-invest-candidate@bf140ac2efa1ba3d532f1da5d1ec663be7e0ac3a",
            method="versioned_narrative_definition_clean_room",
            source_group="classic-research-ledger-20260818",
            review_state="candidate_not_human_approved",
        )
        row.update({
            "name": item["name"], "definition": item["definition"],
            "included": item["included"], "excluded": item["excluded"],
            "synonyms": item["synonyms"], "reverse_narrative": "；".join(counter),
            "origin": {"date": origin["t0"], "event": origin["event"]},
            "falsifiers": counter,
        })
        rows.append(row)
    return rows


def listing_status(value: str) -> str:
    return {
        "risk_warning": "risk_warning",
        "delisting": "delisted",
        "active": "active",
    }.get(value, "unknown")


def import_companies(classic_dir: Path):
    source = classic_dir / "public" / "snapshots" / "latest" / "companies.json"
    rows = []
    for item in read_json(source)["items"]:
        status = item["status"] if item["status"] in {"rejected", "expired"} else "partial"
        evidence_ids = [IDENTITY_EVIDENCE[item["ticker"]]] if item["ticker"] in IDENTITY_EVIDENCE else []
        next_validation = item.get("next_validation") or {}
        row = base(
            object_id=item["id"], object_type="CompanyMaster", status=status,
            as_of=item["as_of"], valid_from=item["valid_from"],
            source_hash=EXPECTED_HASHES["companies"],
            source_revision="local-invest-candidate@bf140ac2efa1ba3d532f1da5d1ec663be7e0ac3a",
            method="legacy_disposition_with_identity_gate_clean_room",
            source_group="classic-research-ledger-20260818",
            review_state="candidate_not_human_approved",
        )
        row.update({
            "exchange": item["exchange"], "ticker": item["ticker"],
            "official_name": item["official_name"], "market": item["market"],
            "listing_status": listing_status(item["listing_status"]),
            "aliases": item.get("aliases", []), "legacy_disposition": status,
            "disposition_reason": item["disposition_reason"],
            "identity_evidence_ids": evidence_ids,
            "legacy_record_ids": item.get("legacy_record_ids", []),
            "legacy_names": item.get("legacy_names", []),
            "risk_flags": item.get("risk_flags", []),
            "confidence": item.get("confidence", "unverified"),
            "next_validation_at": as_datetime(next_validation.get("date", "2026-08-21")),
            "next_validation_metric": next_validation.get("metric", "company identity and mapping review"),
        })
        rows.append(row)
    return rows


def import_mappings(classic_dir: Path, companies):
    source = classic_dir / "public" / "snapshots" / "latest" / "mappings.json"
    company_by_id = {item["id"]: item for item in companies}
    rows = []
    for item in read_json(source)["items"]:
        company = company_by_id[item["company_id"]]
        status = company["status"] if company["status"] in {"rejected", "expired"} else "partial"
        evidence_ids = company["identity_evidence_ids"]
        edge_id = f"{item['id']}-edge-1"
        row = base(
            object_id=item["id"], object_type="AssetMapping", status=status,
            as_of=item["as_of"], valid_from=item["valid_from"],
            source_hash=EXPECTED_HASHES["mappings"],
            source_revision="local-invest-candidate@bf140ac2efa1ba3d532f1da5d1ec663be7e0ac3a",
            method="legacy_mapping_disposition_clean_room",
            source_group="classic-research-ledger-20260818",
            review_state="candidate_not_human_approved",
        )
        row.update({
            "narrative_id": item["narrative_id"], "company_id": item["company_id"],
            "edges": [{
                "id": edge_id,
                "from": f"legacy_record:{item['id']}",
                "to": company["official_name"],
                "claim_class": "hypothesis",
                "claim": "旧记录仅保留为待审研究假说，尚未证明产品、订单、收入与利润的连续传导。",
                "evidence_ids": evidence_ids,
            }],
            "weakest_edge_id": edge_id,
            "evidence_ids": evidence_ids,
            "counter_evidence_ids": evidence_ids if company["status"] in {"rejected", "expired"} or company["listing_status"] == "risk_warning" else [],
            "failure_condition": item.get("failure_condition", "无法建立产品、客户或订单、收入利润的逐边证据链"),
            "next_validation_at": as_datetime((item.get("next_validation") or {}).get("date", "2026-08-21")),
        })
        rows.append(row)
    return rows


def import_stages(narratives):
    rows = []
    for narrative in narratives:
        row = base(
            object_id=f"stage-{narrative['id']}", object_type="StageSnapshot", status="partial",
            as_of=narrative["as_of"], valid_from=narrative["valid_from"],
            source_hash=EXPECTED_HASHES["narratives"], source_revision=narrative["source_revision"],
            method="deterministic_unknown_without_frozen_observations",
            source_group="classic-research-ledger-20260818",
            review_state="candidate_not_human_approved",
        )
        row.update({
            "narrative_id": narrative["id"], "stage": "unknown",
            "calculation_version": "narrative-stage-v1.0.0",
            "input_observation_ids": [], "coverage": 0,
            "partial_reasons": ["narrative_observations_not_frozen", "evidence_reviewer_unassigned"],
        })
        rows.append(row)
    return rows


def import_replays(research_dir: Path):
    source = research_dir / "historical-replay.json"
    document = read_json(source)
    failures = set(document["sample_level_counterexample_check"]["explicit_failure_or_decay_cases"])
    limits = document["method"]["point_in_time_limits"]
    rows = []
    for item in document["cases"]:
        row = base(
            object_id=item["id"], object_type="Replay", status="partial",
            as_of=document["as_of"], valid_from=item["t0"],
            source_hash=EXPECTED_HASHES["historical_replay"],
            source_revision=f"sha256:{EXPECTED_HASHES['historical_replay']}",
            method="historical_replay_clean_room_import",
            source_group="ai-narrative-invest-research-20260817",
            review_state="descriptive_not_causal_not_admitted",
        )
        row.update({
            "narrative_id": NARRATIVE_FOR_REPLAY[item["id"]],
            "case_name": item["name"], "t0": item["t0"],
            "window_start": shift_months(item["t0"], -6),
            "window_end": shift_months(item["t0"], 18),
            "point_in_time_rule": "T0 标的池、当时可得信息与估值必须冻结；当前导入因事后重建标的池而保持 partial。",
            "horizons": document["method"]["windows_trading_days"],
            "financial_periods": 2, "failure_case": item["id"] in failures,
            "lookahead_check": "partial", "evidence_ids": item["evidence_ids"],
            "measurements": item["basket"], "constituents": item["constituents"],
            "counterevidence": item["counterevidence"], "falsifier": item["falsifier"],
            "fundamental_validation": item["fundamental_validation"],
            "method_limits": limits,
            "notes": "仅用于描述性事件路径与反例发现；禁止解释为因果、准入、策略或预期收益。",
        })
        rows.append(row)
    return rows


def event_for(item):
    status_to_event = {"rejected": "rejected", "expired": "expired", "partial": "partial"}
    evidence_ids = item.get("evidence_ids") or item.get("identity_evidence_ids") or []
    row = base(
        object_id=f"event-import-{item['id'].lower()}", object_type="ResearchEvent", status="candidate",
        as_of=IMPORT_AT, valid_from="2026-08-18", source_hash=item["source_snapshot_hash"],
        source_revision=item["source_revision"], method="append_only_clean_room_import_event",
        source_group="yuanli-invest-repository-genesis",
        review_state="not_human_reviewed",
    )
    row.update({
        "subject_id": item["id"], "subject_version": item["version"],
        "event_type": status_to_event.get(item["status"], "candidate_created"),
        "actor": "codex_clean_room_import", "occurred_at": IMPORT_AT,
        "reason": "Clean-room import only; this event does not grant research admission.",
        "evidence_ids": evidence_ids,
    })
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-dir", type=Path, required=True)
    parser.add_argument("--classic-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--events-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    sources = {
        "evidence_ledger": args.research_dir / "evidence-ledger.json",
        "historical_replay": args.research_dir / "historical-replay.json",
        "narratives": args.classic_dir / "public" / "snapshots" / "latest" / "narratives.json",
        "companies": args.classic_dir / "public" / "snapshots" / "latest" / "companies.json",
        "mappings": args.classic_dir / "public" / "snapshots" / "latest" / "mappings.json",
        "classic_evidence": args.classic_dir / "public" / "snapshots" / "latest" / "evidence.json",
        "identity_additions": args.classic_dir / "data" / "classic" / "evidence-additions.json",
    }
    for label, path in sources.items():
        verify(path, label)

    clear_generated(args.output_root)
    clear_generated(args.events_root)

    evidence, source_records = import_evidence(args.research_dir, args.classic_dir)
    narratives = import_narratives(args.classic_dir)
    companies = import_companies(args.classic_dir)
    mappings = import_mappings(args.classic_dir, companies)
    stages = import_stages(narratives)
    replays = import_replays(args.research_dir)

    collections = {
        "narratives": narratives,
        "source-records": source_records,
        "evidence": evidence,
        "stages": stages,
        "companies": companies,
        "mappings": mappings,
        "replays": replays,
    }
    all_objects = []
    for directory, rows in collections.items():
        for item in rows:
            write_json(args.output_root / directory / f"{item['id'].lower()}.v1.0.0.json", item)
            all_objects.append(item)

    events = [event_for(item) for item in all_objects]
    for event in events:
        write_json(args.events_root / f"{event['id']}.v1.0.0.json", event)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": IMPORT_AT,
        "decision_id": DECISION_ID,
        "task_id": TASK_ID,
        "source_hashes": EXPECTED_HASHES,
        "counts": {name: len(rows) for name, rows in collections.items()},
        "research_evidence_count": 36,
        "identity_governance_evidence_count": 4,
        "explicit_failure_or_decay_replays": sum(1 for item in replays if item["failure_case"]),
        "events": len(events),
        "research_admission": "blocked_unassigned_evidence_reviewer",
    }
    write_json(args.manifest, manifest)
    print(json.dumps(manifest["counts"], ensure_ascii=False, sort_keys=True))
    print(f"events={len(events)} research_admission=blocked_unassigned_evidence_reviewer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
