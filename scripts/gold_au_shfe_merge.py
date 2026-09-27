#!/usr/bin/env python3
"""Merge bounded private SHFE daily captures without changing source bytes.

Dry-run is the default. The merged manifest is a convenience inventory for the
retrospective assembler; it does not certify historical publication times or
fill prices. All source files and the merged output stay outside Git.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def _private(path: Path) -> Path:
    path = path.expanduser().resolve()
    if any((parent / ".git").exists() for parent in (path, *path.parents)):
        raise ValueError("SHFE source and output must remain outside Git")
    return path


def _read(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON manifest must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def merge(*, provider_manifest: Path, shfe_manifests: list[Path], output_dir: Path,
          execute: bool = False) -> dict:
    if not shfe_manifests or len(shfe_manifests) > 8:
        raise ValueError("one to eight SHFE manifests required")
    provider, provider_sha = _read(_private(provider_manifest))
    if provider.get("schema_version") != "gold-au-history-capture.v1" or provider.get("status") != "CAPTURED":
        raise ValueError("complete dated AU provider manifest required")
    vendor_days = {
        bar["date"] for capture in provider.get("captures", []) for bar in capture.get("bars", [])
        if date.fromisoformat(bar["date"]).weekday() < 5
    }
    intervals: list[tuple[date, date]] = []
    parents = []
    reports = []
    errors = []
    observed_days: set[str] = set()
    for source_path in shfe_manifests:
        source_path = _private(source_path)
        source, source_sha = _read(source_path)
        if (source.get("schema_version") != "gold-au-shfe-daily-capture.v1"
                or source.get("mode") != "EXECUTE"
                or source.get("status") not in {"CAPTURED", "PARTIAL_FAILURE"}
                or source.get("historical_release_time_verified") is not False):
            raise ValueError("SHFE retrospective source manifest required")
        interval = source.get("interval")
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError("SHFE source interval missing")
        start, end = (date.fromisoformat(day) for day in interval)
        if start > end:
            raise ValueError("SHFE source interval invalid")
        intervals.append((start, end))
        expected = {day for day in vendor_days if start <= date.fromisoformat(day) <= end}
        if source.get("requested_days") != len(expected):
            raise ValueError("SHFE source request count mismatch")
        rows = source.get("reports")
        failures = source.get("errors")
        if not isinstance(rows, list) or not isinstance(failures, list):
            raise ValueError("SHFE source inventory missing")
        actual = [row["date"] for row in rows] + [row["date"] for row in failures]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            raise ValueError("SHFE source dates do not cover provider dates")
        if observed_days & set(actual):
            raise ValueError("duplicate SHFE source date")
        observed_days.update(actual)
        for row in rows:
            original = Path(row["raw_file"]).resolve()
            if original.parent != (source_path.parent / "raw").resolve():
                raise ValueError("SHFE raw source outside capture")
            raw = original.read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["raw_sha256"]:
                raise ValueError("SHFE raw source SHA mismatch")
            reports.append((dict(row), raw))
        errors.extend(failures)
        parents.append({"manifest_sha256": source_sha, "manifest_path": str(source_path),
                        "interval": interval, "reports": len(rows), "errors": len(failures)})
    ordered = sorted(intervals)
    if any(right[0] <= left[1] for left, right in zip(ordered, ordered[1:])):
        raise ValueError("SHFE source intervals overlap")
    if any(right[0] != left[1] + timedelta(days=1) for left, right in zip(ordered, ordered[1:])):
        raise ValueError("SHFE source intervals have a gap")
    span = [ordered[0][0].isoformat(), ordered[-1][1].isoformat()]
    expected_span = {day for day in vendor_days if span[0] <= day <= span[1]}
    if observed_days != expected_span:
        raise ValueError("SHFE merged dates do not cover provider span")
    destination = _private(output_dir)
    summary = {"schema_version": "gold-au-shfe-daily-capture.v1",
               "merge_schema_version": "gold-au-shfe-manifest-merge.v1",
               "mode": "EXECUTE" if execute else "DRY_RUN",
               "status": "PARTIAL_FAILURE" if errors else "CAPTURED",
               "historical_release_time_verified": False,
               "authority": "RETROSPECTIVE_RESEARCH_EVIDENCE_ONLY",
               "interval": span, "requested_days": len(expected_span),
               "report_count": len(reports), "error_count": len(errors),
               "source_manifests": parents, "provider_manifest_sha256": provider_sha}
    if not execute:
        return summary
    if destination.exists():
        raise FileExistsError("choose a new immutable merged output directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".gold-shfe-merge-", dir=destination.parent))
    try:
        (staging / "raw").mkdir(mode=0o700)
        output_rows = []
        for row, raw in sorted(reports, key=lambda pair: pair[0]["date"]):
            path = staging / "raw" / ("kx" + row["date"].replace("-", "") + ".dat")
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as target:
                target.write(raw)
            row["raw_file"] = str(destination / "raw" / path.name)
            output_rows.append(row)
        manifest = {key: value for key, value in summary.items()
                    if key not in {"report_count", "error_count", "provider_manifest_sha256"}}
        manifest.update({"captured_at": datetime.now(timezone.utc).isoformat(),
                         "reports": output_rows, "errors": sorted(errors, key=lambda row: row["date"]),
                         "source_manifest_sha256s": [row["manifest_sha256"] for row in parents]})
        target = staging / "manifest.json"
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider-manifest", type=Path, required=True)
    parser.add_argument("--shfe-manifest", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    result = merge(provider_manifest=args.provider_manifest,
                   shfe_manifests=args.shfe_manifest, output_dir=args.output_dir,
                   execute=args.execute)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
