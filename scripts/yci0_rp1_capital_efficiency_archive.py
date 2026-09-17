#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.yci0_rp1.capital_efficiency_reconstruction import FilingFact, reconstruct_entity_observations

ENTITY_REGISTRY = ROOT / "config/yci0_rp1/capital_efficiency_entities.v0.1.json"
PROJECT_REF = "tbmoimbdhsrltvospwpu"
REGION = "us-east-2"
BUCKET = os.getenv("YMQ4_RAW_BUCKET", "ymq4-raw-evidence")
USER_AGENT = "YuanliResearchEvidenceBot/1.0 research@example.com"
MANDATORY_NORMALIZED = (
    "REVENUE", "OPERATING_INCOME", "PRETAX_INCOME", "INCOME_TAX_EXPENSE",
    "OPERATING_CASH_FLOW", "CAPEX", "TOTAL_ASSETS", "CASH",
    "CURRENT_MARKETABLE_SECURITIES", "TOTAL_CURRENT_LIABILITIES",
)
OPTIONAL_NORMALIZED = (
    "SHORT_TERM_BORROWINGS", "CURRENT_MATURITIES_LONG_TERM_DEBT", "CURRENT_FINANCE_LEASE_LIABILITIES",
)
DIRECT_QUARTER_FLOWS = {"REVENUE", "OPERATING_INCOME", "PRETAX_INCOME", "INCOME_TAX_EXPENSE"}
CUMULATIVE_FLOWS = {"OPERATING_CASH_FLOW", "CAPEX"}
STOCKS = {"TOTAL_ASSETS", "CASH", "CURRENT_MARKETABLE_SECURITIES", "TOTAL_CURRENT_LIABILITIES"} | set(OPTIONAL_NORMALIZED)
PERIOD_TYPES = {"Q1", "Q2", "Q3", "FY"}


def _load_registry() -> dict[str, Any]:
    return json.loads(ENTITY_REGISTRY.read_text(encoding="utf-8"))


def manifest_entities() -> tuple[str, ...]:
    return tuple(_load_registry()["entities"].keys())


def build_concept_coverage_diagnostics(
    normalized: str,
    candidates: list[str],
    gaap: dict[str, Any],
    normalized_by_tag: dict[str, list[Any]],
    target_periods: set[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tag in candidates:
        tag_obj = gaap.get(tag)
        if tag_obj is None:
            continue
        normalized_periods = sorted(
            {str(f.fiscal_period) for f in normalized_by_tag.get(tag, [])},
            key=_period_ordinal,
        )
        raw = _original_facts(tag_obj)
        target_years = {int(period[:4]) for period in target_periods}
        raw_facts = []
        for item in sorted(raw, key=lambda x: (x.get("filed", ""), x.get("accn", ""), x.get("start") or "", x.get("end") or "")):
            end = str(item.get("end") or "")
            fy = item.get("fy")
            end_year = int(end[:4]) if len(end) >= 4 and end[:4].isdigit() else None
            if fy not in target_years and end_year not in target_years:
                continue
            raw_facts.append({
                key: (str(item.get(key)) if key == "val" and item.get(key) is not None else item.get(key))
                for key in ("fy", "fp", "start", "end", "filed", "accn", "form", "val", "frame")
            })
        rows.append({
            "normalized": normalized,
            "tag": tag,
            "label": tag_obj.get("label"),
            "description": tag_obj.get("description"),
            "covered_target_periods": [p for p in normalized_periods if p in target_periods],
            "all_normalized_periods": normalized_periods,
            "raw_accessions": sorted({str(x.get("accn")) for x in raw if x.get("accn")}),
            "raw_fiscal_period_types": sorted({str(x.get("fp")) for x in raw if x.get("fp")}),
            "raw_fact_count": len(raw),
            "raw_facts": raw_facts,
        })
    return rows


def synthetic_receipt() -> dict[str, Any]:
    return {
        "status": "PASS",
        "authority": {
            "evidence_promotion_authorized": False,
            "research_authorized": False,
            "capital_authorized": False,
            "execution_authorized": False,
        },
    }


def audit_tag_regime(
    available_tags: set[str],
    required_candidates: dict[str, list[str]],
    coverage: dict[str, set[str]] | None = None,
    required_period_types: set[str] | None = None,
) -> dict[str, Any]:
    selected: dict[str, str] = {}
    blockers: list[str] = []
    for normalized, candidates in required_candidates.items():
        present = [tag for tag in candidates if tag in available_tags]
        if not present:
            blockers.append(f"MISSING_TAG:{normalized}")
            continue
        if coverage is not None and required_period_types is not None:
            full = [tag for tag in present if required_period_types.issubset(coverage.get(tag, set()))]
            if not full:
                blockers.append(f"NO_SINGLE_TAG_COVERS:{normalized}")
                continue
            selected[normalized] = full[0]
        else:
            selected[normalized] = present[0]
    return {"status": "PASS" if not blockers else "UNKNOWN", "selected_tags": selected, "blockers": blockers}


def _curl_bytes(url: str) -> bytes:
    proc = subprocess.run(
        ["curl", "--http1.1", "-sS", "-L", "--retry", "3", "--connect-timeout", "10", "--max-time", "120", "-A", USER_AGENT, url],
        check=True,
        stdout=subprocess.PIPE,
    )
    if not proc.stdout:
        raise RuntimeError(f"empty SEC response: {url}")
    return proc.stdout


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _s3_client():
    import boto3
    from botocore.config import Config
    access = os.getenv("YMQ4_SUPABASE_S3_ACCESS_KEY_ID", "").strip()
    secret = os.getenv("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY", "").strip()
    if not access or not secret:
        raise RuntimeError("missing required Supabase S3 secret bindings")
    return boto3.client(
        "s3", region_name=REGION,
        endpoint_url=f"https://{PROJECT_REF}.storage.supabase.co/storage/v1/s3",
        aws_access_key_id=access, aws_secret_access_key=secret,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def _archive(s3, entity: str, kind: str, raw: bytes) -> dict[str, Any]:
    sha = _sha(raw)
    key = f"yci0-rp1/capital-efficiency/{entity.lower()}/{kind}/{sha}.json"
    s3.put_object(Bucket=BUCKET, Key=key, Body=raw, ContentType="application/json", Metadata={"sha256": sha, "proof-contract": "YCI0-RP1-G6-CAPITAL-EFFICIENCY"})
    reread = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
    reread_sha = _sha(reread)
    if reread_sha != sha:
        raise RuntimeError(f"S3 SHA mismatch for {entity}/{kind}: {reread_sha} != {sha}")
    return {"kind": kind, "bytes": len(raw), "sha256": sha, "storage_bucket": BUCKET, "storage_path": key, "storage_readback_sha256": reread_sha}


def _iso_acceptance(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if value.endswith("Z"):
        return value
    if len(value) == 14 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}T{value[8:10]}:{value[10:12]}:{value[12:14]}Z"
    return value + ("Z" if "T" in value and not value.endswith("Z") else "")


def _acceptance_map(submissions: dict[str, Any]) -> dict[str, str]:
    recent = submissions.get("filings", {}).get("recent", {})
    accns = recent.get("accessionNumber", [])
    accepted = recent.get("acceptanceDateTime", [])
    out = {}
    for accn, when in zip(accns, accepted):
        iso = _iso_acceptance(when)
        if accn and iso:
            out[accn] = iso
    return out


def _duration_days(item: dict[str, Any]) -> int:
    if not item.get("start") or not item.get("end"):
        return 0
    return (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days + 1


def _original_facts(tag_obj: dict[str, Any]) -> list[dict[str, Any]]:
    units = tag_obj.get("units", {}).get("USD", [])
    candidates = [x for x in units if x.get("form") in {"10-Q", "10-K"} and x.get("fp") in PERIOD_TYPES and x.get("filed") and x.get("accn")]
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        grouped[(item.get("start"), item.get("end"))].append(item)
    out = []
    for items in grouped.values():
        earliest = min(x["filed"] for x in items)
        same = [x for x in items if x["filed"] == earliest]
        values = {str(x.get("val")) for x in same}
        if len(values) > 1:
            continue
        out.append(sorted(same, key=lambda x: (x.get("accn", ""), x.get("frame") or ""))[0])
    return out


def _coverage_for_tag(tag_obj: dict[str, Any]) -> set[str]:
    return {x.get("fp") for x in _original_facts(tag_obj) if x.get("fp") in PERIOD_TYPES}


def _choose_entry(entries: Iterable[dict[str, Any]], fy: int, fp: str, mode: str) -> dict[str, Any] | None:
    rows = [x for x in entries if x.get("fy") == fy and x.get("fp") == fp]
    if not rows:
        return None
    if mode == "instant":
        instants = [x for x in rows if not x.get("start")]
        return sorted(instants, key=lambda x: (x.get("filed", ""), x.get("accn", "")))[0] if instants else None
    durations = [(x, _duration_days(x)) for x in rows if x.get("start")]
    if not durations:
        return None
    if mode == "direct":
        return min(durations, key=lambda pair: (pair[1], pair[0].get("filed", "")))[0]
    if mode == "cumulative":
        return max(durations, key=lambda pair: (pair[1], pair[0].get("filed", "")))[0]
    raise ValueError(mode)


def _lineage_hash(raw_sha: str, normalized: str, tag: str, period: str, sources: list[dict[str, Any]], value: Decimal) -> str:
    payload = {"raw_sha256": raw_sha, "normalized": normalized, "tag": tag, "period": period, "value": str(value), "sources": [{k: s.get(k) for k in ("accn", "start", "end", "val", "filed", "fy", "fp")} for s in sources]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _source_locator(cik: str, tag: str, sources: list[dict[str, Any]]) -> str:
    accns = ",".join(sorted({x.get("accn", "") for x in sources}))
    return f"sec-companyfacts://CIK{cik}/us-gaap/{tag}?accessions={accns}"


def _known_as_of(sources: list[dict[str, Any]], acceptance: dict[str, str]) -> str | None:
    values = [acceptance.get(x.get("accn", "")) for x in sources]
    if any(v is None for v in values):
        return None
    return max(v for v in values if v is not None)


def _make_fact(entity: str, cik: str, normalized: str, tag: str, period: str, value: Decimal, sources: list[dict[str, Any]], acceptance: dict[str, str], raw_sha: str, regime: str) -> FilingFact | None:
    known = _known_as_of(sources, acceptance)
    if known is None:
        return None
    return FilingFact(
        entity_id=entity, fiscal_period=period, known_as_of=known,
        source_locator=_source_locator(cik, tag, sources),
        content_hash=_lineage_hash(raw_sha, normalized, tag, period, sources, value),
        concept=normalized, value=value, unit="USD", accounting_regime=regime,
    )


def _normalize_tag(entity: str, cik: str, normalized: str, tag: str, tag_obj: dict[str, Any], acceptance: dict[str, str], raw_sha: str, regime: str) -> tuple[list[FilingFact], list[str]]:
    entries = _original_facts(tag_obj)
    fys = sorted({int(x["fy"]) for x in entries if isinstance(x.get("fy"), int)})
    output: list[FilingFact] = []
    blockers: list[str] = []
    for fy in fys:
        selected: dict[str, dict[str, Any]] = {}
        mode = "instant" if normalized in STOCKS else ("direct" if normalized in DIRECT_QUARTER_FLOWS else "cumulative")
        for fp in ("Q1", "Q2", "Q3", "FY"):
            item = _choose_entry(entries, fy, fp, mode)
            if item is not None:
                selected[fp] = item
        if normalized in STOCKS:
            for fp, q in (("Q1",1),("Q2",2),("Q3",3),("FY",4)):
                if fp not in selected:
                    continue
                item=selected[fp]; fact=_make_fact(entity,cik,normalized,tag,f"{fy}Q{q}",Decimal(str(item["val"])),[item],acceptance,raw_sha,regime)
                if fact: output.append(fact)
                else: blockers.append(f"MISSING_ACCEPTANCE:{normalized}:{fy}Q{q}")
            continue
        if normalized in DIRECT_QUARTER_FLOWS:
            quarter_values: dict[str, tuple[Decimal,list[dict[str,Any]]]] = {}
            for fp in ("Q1","Q2","Q3"):
                if fp in selected:
                    quarter_values[fp]=(Decimal(str(selected[fp]["val"])),[selected[fp]])
            if "FY" in selected and all(fp in quarter_values for fp in ("Q1","Q2","Q3")):
                annual=Decimal(str(selected["FY"]["val"])); first9=sum((quarter_values[fp][0] for fp in ("Q1","Q2","Q3")),Decimal("0")); quarter_values["Q4"]=(annual-first9,[selected["FY"]]+[selected[fp] for fp in ("Q1","Q2","Q3")])
            for fp,q in (("Q1",1),("Q2",2),("Q3",3),("Q4",4)):
                if fp not in quarter_values: continue
                value,sources=quarter_values[fp]; fact=_make_fact(entity,cik,normalized,tag,f"{fy}Q{q}",value,sources,acceptance,raw_sha,regime)
                if fact: output.append(fact)
                else: blockers.append(f"MISSING_ACCEPTANCE:{normalized}:{fy}Q{q}")
            continue
        if normalized in CUMULATIVE_FLOWS:
            if "Q1" in selected:
                values={"Q1":(Decimal(str(selected["Q1"]["val"])),[selected["Q1"]])}
                if "Q2" in selected: values["Q2"]=(Decimal(str(selected["Q2"]["val"]))-Decimal(str(selected["Q1"]["val"])),[selected["Q2"],selected["Q1"]])
                if "Q3" in selected and "Q2" in selected: values["Q3"]=(Decimal(str(selected["Q3"]["val"]))-Decimal(str(selected["Q2"]["val"])),[selected["Q3"],selected["Q2"]])
                if "FY" in selected and "Q3" in selected: values["Q4"]=(Decimal(str(selected["FY"]["val"]))-Decimal(str(selected["Q3"]["val"])),[selected["FY"],selected["Q3"]])
                for fp,q in (("Q1",1),("Q2",2),("Q3",3),("Q4",4)):
                    if fp not in values: continue
                    value,sources=values[fp]; fact=_make_fact(entity,cik,normalized,tag,f"{fy}Q{q}",value,sources,acceptance,raw_sha,regime)
                    if fact: output.append(fact)
                    else: blockers.append(f"MISSING_ACCEPTANCE:{normalized}:{fy}Q{q}")
    dedup={(f.fiscal_period,f.concept):f for f in output}
    return [dedup[k] for k in sorted(dedup)], blockers


def _period_ordinal(period: str) -> int:
    return int(period[:4]) * 4 + int(period[-1])


def latest_consecutive_window(periods: list[str], size: int) -> list[str]:
    ordered = sorted(set(periods), key=_period_ordinal)
    best: list[str] = []
    run: list[str] = []
    previous: int | None = None
    for period in ordered:
        current = _period_ordinal(period)
        if previous is None or current == previous + 1:
            run.append(period)
        else:
            run = [period]
        previous = current
        if len(run) >= size:
            best = run[-size:]
    return best


def select_tag_for_target_periods(candidates: list[str], periods_by_tag: dict[str, set[str]], target_periods: set[str]) -> str | None:
    for tag in candidates:
        if target_periods.issubset(periods_by_tag.get(tag, set())):
            return tag
    return None


def _consecutive_last_four(periods: list[str]) -> bool:
    if len(periods) < 4:
        return False
    vals = [_period_ordinal(p) for p in periods[-4:]]
    return vals == list(range(vals[0], vals[0] + 4))


def analyze_entity(entity: str, cfg: dict[str, Any], normalized_candidates: dict[str, list[str]], companyfacts: dict[str, Any], submissions: dict[str, Any], raw_sha: str) -> dict[str, Any]:
    gaap = companyfacts.get("facts", {}).get("us-gaap", {})
    acceptance = _acceptance_map(submissions)
    cache: dict[tuple[str, str], list[FilingFact]] = {}

    def normalized_for(normalized: str, tag: str) -> list[FilingFact]:
        key = (normalized, tag)
        if key not in cache:
            if tag not in gaap:
                cache[key] = []
            else:
                facts, _ = _normalize_tag(entity, cfg["sec_cik"], normalized, tag, gaap[tag], acceptance, raw_sha, cfg["accounting_regime"])
                cache[key] = facts
        return cache[key]

    anchor_periods: list[str] = []
    anchor_tag: str | None = None
    for tag in normalized_candidates["TOTAL_ASSETS"]:
        periods = [f.fiscal_period for f in normalized_for("TOTAL_ASSETS", tag)]
        window = latest_consecutive_window(periods, 11)
        if window:
            anchor_periods = window
            anchor_tag = tag
            break
    if not anchor_periods:
        return {
            "entity_id": entity, "cohort": cfg["cohort"], "qualification": "UNKNOWN",
            "selected_tags": {}, "blockers": ["NO_11_QUARTER_ASSET_ANCHOR"], "derived": {},
        }

    target = set(anchor_periods)
    selected: dict[str, str] = {"TOTAL_ASSETS": anchor_tag} if anchor_tag else {}
    blockers: list[str] = []
    coverage_diagnostics: dict[str, list[dict[str, Any]]] = {}

    for normalized in MANDATORY_NORMALIZED:
        if normalized == "TOTAL_ASSETS":
            continue
        candidates = normalized_candidates[normalized]
        periods_by_tag = {tag: {f.fiscal_period for f in normalized_for(normalized, tag)} for tag in candidates if tag in gaap}
        tag = select_tag_for_target_periods(candidates, periods_by_tag, target)
        if tag is None:
            blockers.append(f"NO_SINGLE_TAG_COVERS_LATEST_11:{normalized}")
            coverage_diagnostics[normalized] = build_concept_coverage_diagnostics(
                normalized, candidates, gaap,
                {candidate: normalized_for(normalized, candidate) for candidate in candidates if candidate in gaap},
                target,
            )
        else:
            selected[normalized] = tag

    for normalized in OPTIONAL_NORMALIZED:
        candidates = normalized_candidates[normalized]
        periods_by_tag = {tag: {f.fiscal_period for f in normalized_for(normalized, tag)} for tag in candidates if tag in gaap}
        tag = select_tag_for_target_periods(candidates, periods_by_tag, target)
        if tag is not None:
            selected[normalized] = tag
        elif any(periods & target for periods in periods_by_tag.values()):
            blockers.append(f"OPTIONAL_DISCLOSURE_REGIME_BREAK:{normalized}")

    if blockers:
        return {
            "entity_id": entity, "cohort": cfg["cohort"], "qualification": "UNKNOWN",
            "selected_tags": selected, "blockers": sorted(set(blockers)), "target_periods": anchor_periods,
            "coverage_diagnostics": coverage_diagnostics, "derived": {},
        }

    normalized_facts: list[FilingFact] = []
    for normalized, tag in selected.items():
        normalized_facts.extend(f for f in normalized_for(normalized, tag) if f.fiscal_period in target)

    spec = {"entity_id": entity, **cfg}
    derived = reconstruct_entity_observations(normalized_facts, spec)
    summary: dict[str, Any] = {}
    expected_latest_four = anchor_periods[-4:]
    for component in ("INCREMENTAL_ROIC", "CASH_CONVERSION", "CAPITAL_INTENSITY"):
        rows = [x for x in derived if x.component == component]
        passed = [x for x in rows if x.status == "PASS"]
        latest = passed[-4:] if len(passed) >= 4 else passed
        latest_periods = [x.fiscal_period for x in latest]
        qualified = len(latest) == 4 and latest_periods == expected_latest_four and _consecutive_last_four(latest_periods)
        if not qualified:
            blockers.append(f"INSUFFICIENT_CONSECUTIVE_PASS:{component}:{len(latest)}")
        summary[component] = {
            "pass_count": len(passed),
            "latest_four_periods": latest_periods,
            "latest_four_values": [str(x.value) for x in latest],
            "latest_four_receipts": [x.calculation_receipt_sha256 for x in latest],
            "qualified": qualified,
        }
    all_blockers = sorted(set(blockers))
    return {
        "entity_id": entity, "cohort": cfg["cohort"],
        "qualification": "QUALIFIED" if not all_blockers and all(x["qualified"] for x in summary.values()) else "UNKNOWN",
        "selected_tags": selected, "blockers": all_blockers, "target_periods": anchor_periods,
        "normalized_period_range": [anchor_periods[0], anchor_periods[-1]],
        "normalized_fact_count": len(normalized_facts), "derived": summary,
    }


def _read_or_fetch(entity: str, cfg: dict[str, Any], input_dir: Path | None) -> tuple[bytes, bytes]:
    if input_dir:
        cf=input_dir/f"{entity}_companyfacts.json"; sub=input_dir/f"{entity}_submissions.json"
        companyfacts_raw=cf.read_bytes() if cf.exists() else _curl_bytes(cfg["companyfacts_url"])
        submissions_raw=sub.read_bytes() if sub.exists() else _curl_bytes(cfg["submissions_url"])
        if not cf.exists(): cf.write_bytes(companyfacts_raw)
        if not sub.exists(): sub.write_bytes(submissions_raw)
        return companyfacts_raw,submissions_raw
    return _curl_bytes(cfg["companyfacts_url"]),_curl_bytes(cfg["submissions_url"])


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--no-s3", action="store_true")
    args=parser.parse_args()
    registry=_load_registry(); normalized=registry["normalized_concepts"]
    s3=None if args.no_s3 else _s3_client()
    if s3: s3.head_bucket(Bucket=BUCKET)
    entities=[]; archives=[]
    for entity,cfg in registry["entities"].items():
        cf_raw,sub_raw=_read_or_fetch(entity,cfg,args.input_dir)
        cf_sha,sub_sha=_sha(cf_raw),_sha(sub_raw)
        if s3:
            archives.extend([{**_archive(s3,entity,"companyfacts",cf_raw),"entity_id":entity},{**_archive(s3,entity,"submissions",sub_raw),"entity_id":entity}])
        companyfacts=json.loads(cf_raw); submissions=json.loads(sub_raw)
        result=analyze_entity(entity,cfg,normalized,companyfacts,submissions,cf_sha)
        result["raw_companyfacts_sha256"]=cf_sha; result["raw_submissions_sha256"]=sub_sha
        entities.append(result)
    qualified=[x["entity_id"] for x in entities if x["qualification"]=="QUALIFIED"]
    receipt={
        "program":"YCI0-RP1","gate":"G6_CAPITAL_EFFICIENCY_RAW_EVIDENCE",
        "status":"PASS","archive_mode":"LOCAL_AUDIT_ONLY" if args.no_s3 else "PRIVATE_S3_SHA_READBACK",
        "source_role":"SEC_OFFICIAL_COMPANYFACTS_PLUS_SUBMISSIONS_STRUCTURED_SENSOR",
        "semantic_boundary":"Current SEC aggregate XBRL reconstruction linked to original accessions; not a historical byte-for-byte snapshot of each filing at original acceptance time.",
        "qualified_entities":qualified,"g6_coverage_status":"FULL" if len(qualified)==4 else "PARTIAL",
        "entities":entities,"archives":archives,
        "authority":{"evidence_promotion_authorized":False,"research_authorized":False,"capital_authorized":False,"execution_authorized":False},
        "generated_at":datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
