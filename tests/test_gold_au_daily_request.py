"""Synthetic local receipt fixtures, never claims about real source evidence."""

from __future__ import annotations

from datetime import datetime, time, timedelta
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.gold_au_daily_request import run
from tests.test_gold_au_live_snapshot import fixture, stamp, TZ
from yuanli_invest.gold_au_daily_request import assemble_daily_request, CATALOG_SCHEMA
from yuanli_invest.gold_au_live_snapshot import prepare_live_snapshot
from yuanli_invest.receipts import canonical_hash


def assembler_fixture(root: Path):
    request, day, paths = fixture(root)
    # Match the existing macro daily worker's actual archive layout.
    macro = root / "macro_captures" / day.isoformat()
    macro.parent.mkdir()
    paths["fred"].parent.rename(macro)
    manifest = json.loads((macro / "manifest.json").read_text())
    for capture in manifest["captures"]:
        capture["raw_file"] = str(macro / "raw" / (capture["provider_series"] + ".csv"))
    (macro / "manifest.json").write_text(json.dumps(manifest))
    catalog = {key: value for key, value in request.items() if key.endswith("_path") and key != "fred_manifest_path"}
    catalog.update({"schema_version": CATALOG_SCHEMA, "shfe_manifest_paths": request["shfe_manifest_paths"]})
    return catalog, day, {**paths, "fred": macro / "manifest.json"}


class DailyRequestTests(unittest.TestCase):
    def test_explicit_catalog_required_with_all_missing_inputs(self):
        result = assemble_daily_request(None, runtime_dir=Path("/nonexistent"),
                                        decision_date="2026-09-28", as_of=datetime.fromisoformat("2026-09-28T08:20:00+08:00"))
        self.assertEqual(result["reason"], "EXPLICIT_SOURCE_CATALOG_REQUIRED")
        self.assertEqual(len(result["missing_inputs"]), 5)
        self.assertNotIn("request", result)
        self.assertFalse(result["broker_action_authorized"])

    def test_all_missing_receipts_and_no_previous_day_macro_substitution(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "macro_captures" / "2026-09-25").mkdir(parents=True)
            (root / "macro_captures" / "2026-09-25" / "manifest.json").write_text("{}")
            result = assemble_daily_request({"schema_version": CATALOG_SCHEMA}, runtime_dir=root,
                                            decision_date="2026-09-28", as_of=datetime.fromisoformat("2026-09-28T08:20:00+08:00"))
            self.assertEqual(set(result["missing_inputs"]), {"calendar_receipt_path", "h10_mapping_receipt_path", "cost_receipt_path", "fred_manifest_path", "shfe_manifest_paths"})
            self.assertNotIn("request", result)
            self.assertIn("2026-09-28", result["source_inventory"]["fred_manifest_path"]["path"])

    def test_explicit_research_mode_omits_cost_and_its_pin(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            catalog["execution_mode"] = "RESEARCH_ONLY"
            paths["cost"].unlink()
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["status"], "READY_OFFLINE_CANDIDATE", result)
            self.assertEqual(result["request"]["execution_mode"], "RESEARCH_ONLY")
            self.assertNotIn("cost_receipt_path", result["request"])
            self.assertNotIn("cost_receipt_path", result["source_inventory"])
            self.assertEqual(len(result["request"]["assembly_source_receipts"]), 4)
            snapshot = prepare_live_snapshot(result["request"], as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(snapshot["status"], "READY_STRICT_RESEARCH_SIGNAL", snapshot)
            self.assertFalse(snapshot["signal"]["actionable_entry"])
            self.assertEqual(snapshot["signal"]["action_block"], "AWAITING_EXECUTION_COST_VERIFICATION")
            self.assertFalse(result["decision_frozen"])

    def test_missing_cost_remains_blocked_without_explicit_research_mode(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            paths["cost"].unlink()
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("cost_receipt_path", result["missing_inputs"])
            self.assertNotIn("request", result)

    def test_unknown_explicit_mode_fails_closed(self):
        result = assemble_daily_request({"schema_version": CATALOG_SCHEMA, "execution_mode": "TRADE_ANYWAY"},
                                        runtime_dir=Path("/nonexistent"), decision_date="2026-09-28",
                                        as_of=datetime.fromisoformat("2026-09-28T08:25:00+08:00"))
        self.assertEqual(result["reason"], "INVALID_EXPLICIT_EXECUTION_MODE")
        self.assertNotIn("request", result)

    def test_ready_candidate_is_worker_compatible_and_does_not_freeze_a_signal(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, _ = assembler_fixture(root)
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["status"], "READY_OFFLINE_CANDIDATE", result)
            self.assertEqual(result["request_sha256"], canonical_hash(result["request"]))
            self.assertEqual(result["wgc_status"], "UNKNOWN_RISK_BUDGET_HALVED")
            self.assertFalse(result["decision_frozen"])
            self.assertNotIn("signal", result)
            self.assertEqual(prepare_live_snapshot(result["request"], as_of=datetime.combine(day, time(8, 30), TZ))["status"], "READY_STRICT_RESEARCH_SIGNAL")

    def test_future_evidence_at_assembly_time_cannot_pass_hypothetical_0830(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            cost = json.loads(paths["cost"].read_text())
            cost["captured_at"] = stamp(day, 8, 29)
            paths["cost"].write_text(json.dumps(cost))
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["reason"], "MISSING_OR_INVALID_PROOF_INPUTS")
            self.assertEqual(result["source_inventory"]["cost_receipt_path"]["reason"], "SOURCE_NOT_YET_AVAILABLE_AT_ASSEMBLY")
            self.assertNotIn("request", result)

    def test_retrospective_identity_and_raw_hash_mismatch_are_not_candidates(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            mapping = json.loads(paths["mapping"].read_text())
            mapping["status"] = "EXPLICIT_RETROSPECTIVE_ALIAS_ONLY"
            paths["mapping"].write_text(json.dumps(mapping))
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["reason"], "H10_LIVE_MAPPING_NOT_WITNESSED")
            self.assertNotIn("request", result)
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            source = paths["cost"].parent / "raw" / "source.dat"
            source.write_bytes(b"altered source")
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["reason"], "RAW_HASH_MISMATCH_COST")

    def test_malformed_source_does_not_raise_or_emit_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            manifest = json.loads(paths["fred"].read_text())
            manifest["captures"][0] = None
            paths["fred"].write_text(json.dumps(manifest))
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertNotIn("request", result)

    def test_prior_day_cost_never_produces_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            cost = json.loads(paths["cost"].read_text())
            cost["captured_at"] = stamp(day - timedelta(days=1), 18)
            paths["cost"].write_text(json.dumps(cost))
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["reason"], "STALE_COST_MARGIN_RECEIPT")
            self.assertNotIn("request", result)

    def test_explicit_day_template_binds_exact_archive_without_fallback(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            archive = root / "shfe_archives" / day.isoformat()
            archive.parent.mkdir()
            paths["shfe"].parent.rename(archive)
            manifest = json.loads((archive / "manifest.json").read_text())
            for report in manifest["reports"]:
                report["raw_file"] = str(archive / "raw" / Path(report["raw_file"]).name)
            (archive / "manifest.json").write_text(json.dumps(manifest))
            catalog["shfe_manifest_paths"] = ["shfe_archives/{decision_date}/manifest.json"]
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["status"], "READY_OFFLINE_CANDIDATE")
            self.assertEqual(result["request"]["shfe_manifest_paths"], [str(archive / "manifest.json")])
            catalog["shfe_manifest_paths"] = ["shfe_archives/{latest}/manifest.json"]
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["source_inventory"]["shfe_manifest_0"]["reason"], "UNSUPPORTED_SOURCE_PATH_TEMPLATE")

    def test_receipt_changed_during_validation_is_rejected(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)

            def change_then_validate(request, *, as_of):
                result = prepare_live_snapshot(request, as_of=as_of)
                paths["cost"].write_text(paths["cost"].read_text() + " ")
                return result

            with patch("yuanli_invest.gold_au_daily_request.prepare_live_snapshot", side_effect=change_then_validate):
                result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                                as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["reason"], "SOURCE_CHANGED_DURING_ASSEMBLY")
            self.assertNotIn("request", result)

    def test_worker_rejects_tampered_receipt_and_incomplete_pin_inventory(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            request = result["request"]
            self.assertEqual(result["source_catalog_sha256"], canonical_hash(catalog))
            paths["cost"].write_text(paths["cost"].read_text() + " ")
            snapshot = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(snapshot["reason"], "PINNED_SOURCE_RECEIPT_HASH_MISMATCH")
            self.assertFalse(snapshot["broker_action_authorized"])
            request["assembly_source_receipts"].pop()
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "ASSEMBLY_SOURCE_PIN_INVENTORY_MISMATCH")

    def test_worker_rejects_extra_or_conflicting_pin(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, _ = assembler_fixture(root)
            request = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                             as_of=datetime.combine(day, time(8, 25), TZ))["request"]
            request["assembly_source_receipts"].append({"path": str(root / "unrequested.json"), "receipt_sha256": "0" * 64})
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "ASSEMBLY_SOURCE_PIN_INVENTORY_MISMATCH")
            request["assembly_source_receipts"].pop()
            request["assembly_source_receipts"].append({**request["assembly_source_receipts"][0], "receipt_sha256": "0" * 64})
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "CONFLICTING_ASSEMBLY_SOURCE_PIN")

    def test_worker_pin_inventory_includes_optional_wgc(self):
        from tests.test_gold_au_live_snapshot import write_receipt

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, _ = assembler_fixture(root)
            wgc = write_receipt(root, "wgc", {
                "schema_version": "gold-wgc-manual-witness.v1", "source_kind": "WGC_PRIMARY",
                "witnessed_at": stamp(day, 8, 22), "observations": [],
            }, b"Synthetic WGC source fixture; no market fact claimed")
            catalog["wgc_receipt_path"] = str(wgc)
            request = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                             as_of=datetime.combine(day, time(8, 25), TZ))["request"]
            request["assembly_source_receipts"] = [pin for pin in request["assembly_source_receipts"] if pin["path"] != str(wgc)]
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "ASSEMBLY_SOURCE_PIN_INVENTORY_MISMATCH")

    def test_symlink_and_duplicate_archive_rejected(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog, day, paths = assembler_fixture(root)
            link = root / "cost-link.json"
            link.symlink_to(paths["cost"])
            catalog["cost_receipt_path"] = str(link)
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["source_inventory"]["cost_receipt_path"]["reason"], "MISSING_OR_SYMLINK_RECEIPT")
            catalog["cost_receipt_path"] = str(paths["cost"])
            catalog["shfe_manifest_paths"] *= 2
            result = assemble_daily_request(catalog, runtime_dir=root, decision_date=day.isoformat(),
                                            as_of=datetime.combine(day, time(8, 25), TZ))
            self.assertEqual(result["source_inventory"]["shfe_manifest_1"]["reason"], "DUPLICATE_SHFE_MANIFEST")

    def test_cli_local_write_is_private_immutable_and_blocked_has_no_request(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            when = datetime.fromisoformat("2026-09-28T08:20:00+08:00")
            result = run(root, as_of=when, execute=True)
            self.assertEqual(result["status"], "BLOCKED")
            evidence = Path(result["evidence_path"])
            self.assertEqual(evidence.stat().st_mode & 0o777, 0o600)
            self.assertFalse((root / "requests").exists())
            replay = run(root, as_of=when, execute=True)
            self.assertEqual(replay["evidence_path"], result["evidence_path"])
            with self.assertRaises(ValueError):
                run(root, as_of=when, decision_date="../escape", execute=True)

    def test_successful_cli_write_is_consumable_and_not_replaceable(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            catalog, day, _ = assembler_fixture(root)
            (root / "daily_request_sources.json").write_text(json.dumps(catalog))
            result = run(root, as_of=datetime.combine(day, time(8, 25), TZ), execute=True)
            request_path = root / "requests" / (day.isoformat() + ".json")
            self.assertEqual(result["request"], json.loads(request_path.read_bytes()))
            self.assertEqual(request_path.stat().st_mode & 0o777, 0o600)
            replay = run(root, as_of=datetime.combine(day, time(8, 25), TZ), execute=True)
            self.assertEqual(replay["evidence_path"], result["evidence_path"])
            self.assertEqual(json.loads(request_path.read_bytes()), result["request"])

    def test_blocked_attempt_does_not_prevent_later_proven_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            catalog, day, paths = assembler_fixture(root)
            source_catalog = root / "daily_request_sources.json"
            partial = dict(catalog)
            del partial["cost_receipt_path"]
            source_catalog.write_text(json.dumps(partial))
            blocked = run(root, as_of=datetime.combine(day, time(8, 23), TZ), execute=True)
            self.assertNotIn("request", blocked)
            source_catalog.write_text(json.dumps(catalog))
            ready = run(root, as_of=datetime.combine(day, time(8, 25), TZ), execute=True)
            self.assertEqual(ready["status"], "READY_OFFLINE_CANDIDATE")
            self.assertNotEqual(ready["evidence_path"], blocked["evidence_path"])
            self.assertEqual(json.loads(Path(blocked["evidence_path"]).read_bytes())["status"], "BLOCKED")
            original = (root / "requests" / (day.isoformat() + ".json")).read_bytes()
            cost = json.loads(paths["cost"].read_text())
            cost["contract_terms"][0]["margin_per_lot_cny"] += 1
            paths["cost"].write_text(json.dumps(cost))
            with self.assertRaises(FileExistsError):
                run(root, as_of=datetime.combine(day, time(8, 26), TZ), execute=True)
            self.assertEqual((root / "requests" / (day.isoformat() + ".json")).read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
