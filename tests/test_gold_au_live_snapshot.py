"""Local-only morning evidence fixtures; no source claim about real market data."""

from __future__ import annotations

from datetime import date, datetime, timedelta, time
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from yuanli_invest.gold_au_live_snapshot import prepare_live_snapshot
from yuanli_invest.gold_au_strategy import (
    GoldAuDataset, build_current_snapshot_path, evaluate_signal, evaluate_current_snapshot_signal, replay_frozen_signal,
)
from yuanli_invest.gold_macro_capture import MacroSpec, normalize_raw as normalize_fred
from yuanli_invest.gold_au_official_calendar import build_calendar_receipt, SOURCES
from tests.test_gold_au_official_calendar import notice_fixture

TZ = ZoneInfo("Asia/Shanghai")


def stamp(day: date, hour: int, minute: int = 0) -> str:
    return datetime.combine(day, time(hour, minute), TZ).isoformat()


def weekdays(start: date, count: int) -> list[date]:
    result = []
    day = start
    while len(result) < count:
        if day.weekday() < 5:
            result.append(day)
        day += timedelta(days=1)
    return result


def write_receipt(root: Path, name: str, payload: dict, raw: bytes) -> Path:
    folder = root / name
    (folder / "raw").mkdir(parents=True)
    raw_path = (folder / "raw" / "source.dat").resolve()
    raw_path.write_bytes(raw)
    payload = dict(payload)
    payload["raw_file"] = str(raw_path)
    payload["raw_sha256"] = hashlib.sha256(raw).hexdigest()
    path = folder / "receipt.json"
    path.write_text(json.dumps(payload))
    return path


def synthetic_calendar(root: Path, decision: date) -> tuple[Path, list[date]]:
    """Locally generated annual-notice shape; no real market evidence claim."""
    # macOS TemporaryDirectory may spell /private/var as /var. Canonicalize
    # controlled test roots before making receipts; production still denies
    # every original receipt/raw path that traverses a symlink.
    root = root.resolve()
    folder = root / "calendar"
    raw_dir = folder / "raw"
    raw_dir.mkdir(parents=True)
    documents = []
    for year in SOURCES:
        raw = notice_fixture(year)
        source = (raw_dir / f"annual-{year}.html").resolve()
        source.write_bytes(raw)
        documents.append({"year": year, "source_ref": SOURCES[year], "raw_file": str(source),
                          "raw_sha256": hashlib.sha256(raw).hexdigest(), "captured_at": stamp(decision, 8, 21)})
    receipt = build_calendar_receipt(documents, raw_dir)
    path = folder / "receipt.json"
    path.write_text(json.dumps(receipt))
    return path, [date.fromisoformat(day) for day in receipt["sessions"]]


def fixture(root: Path, *, h10_lag_days: int = 0) -> tuple[dict, date, dict]:
    root = root.resolve()
    decision = date(2026, 9, 28)
    calendar, sessions = synthetic_calendar(root, decision)
    index = sessions.index(decision)
    prior = sessions[index - 273:index]
    shfe_folder = root / "shfe"
    (shfe_folder / "raw").mkdir(parents=True)
    reports = []
    for i, day in enumerate(prior):
        price = round(1000 + 0.3 * i, 2)
        raw = json.dumps({"report_date": day.strftime("%Y%m%d"), "o_curinstrument": [{"PRODUCTID": "au_f", "DELIVERYMONTH": "2712",
                                               "OPENPRICE": price, "HIGHESTPRICE": price + 1,
                                               "LOWESTPRICE": price - 1, "CLOSEPRICE": price,
                                               "VOLUME": 10000, "OPENINTEREST": 20000}]}).encode()
        digest = hashlib.sha256(raw).hexdigest()
        raw_path = (shfe_folder / "raw" / f"kx{day.strftime('%Y%m%d')}.dat").resolve()
        raw_path.write_bytes(raw)
        reports.append({"date": day.isoformat(), "captured_at": stamp(day, 18),
                        "raw_file": str(raw_path), "raw_sha256": digest,
                        "bars": [{"date": day.isoformat(), "contract": "au2712",
                                  "open": str(price), "high": str(price + 1), "low": str(price - 1),
                                  "close": str(price), "volume": "10000", "open_interest": "20000",
                                  "source_sha256": digest, "pit_grade": "LATEST_VINTAGE_ONLY"}]})
    shfe_manifest = shfe_folder / "manifest.json"
    shfe_manifest.write_text(json.dumps({"schema_version": "gold-au-shfe-daily-capture.v1",
                                         "mode": "EXECUTE", "status": "CAPTURED", "reports": reports}))

    fred_folder = root / "fred"
    (fred_folder / "raw").mkdir(parents=True)
    captures = []
    for series in ("DFII10", "DTWEXBGS"):
        source_days = prior[-60:]
        if series == "DTWEXBGS" and h10_lag_days:
            source_days = weekdays(prior[-60] - timedelta(days=h10_lag_days), 60)
        raw = ("observation_date," + series + "\n" + "\n".join(
            f"{day.isoformat()},{4.5 - i * 0.01 if series == 'DFII10' else 100 - i * 0.05}"
            for i, day in enumerate(source_days)) + "\n").encode()
        source_path = (fred_folder / "raw" / f"{series}.csv").resolve()
        source_path.write_bytes(raw)
        captured = datetime.combine(decision, time(8, 20), TZ)
        spec = MacroSpec(series, source_days[0], source_days[-1])
        capture = normalize_fred(raw, spec, captured_at=captured)
        capture["raw_file"] = str(source_path)
        capture["status"] = "CAPTURED"
        captures.append(capture)
    fred_manifest = fred_folder / "manifest.json"
    fred_manifest.write_text(json.dumps({"schema_version": "gold-macro-capture.v1", "status": "CAPTURED",
                                         "provider_id": "fred_graph_csv", "captures": captures}))

    mapping = write_receipt(root, "mapping", {
        "schema_version": "gold-h10-live-mapping.v1", "status": "WITNESSED_FOR_LIVE_PIT",
        "source_series": "FRED:DTWEXBGS",
        "source_measurement_regime": "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY",
        "strategy_series": "FED:H10:DTWEXBGS",
        "strategy_measurement_regime": "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY",
        "unit": "INDEX", "underlying_release": "FEDERAL_RESERVE_H10",
        "witnessed_by": "SYNTHETIC_TEST_WITNESS", "witnessed_at": stamp(decision, 8, 21),
    }, b"synthetic H10 source mapping document")
    cost = write_receipt(root, "cost", {
        "schema_version": "gold-au-live-cost-receipt.v1", "source_kind": "SHFE_AND_SIMNOW_CAPTURE",
        "captured_at": stamp(decision, 8, 22),
        "contract_terms": [{"contract": "au2712", "margin_per_lot_cny": 200000,
                            "fee_open_per_lot_cny": 20, "fee_close_today_per_lot_cny": 20,
                            "fee_close_yesterday_per_lot_cny": 20}],
    }, b"synthetic SHFE and SimNow fee margin evidence")
    request = {"schema_version": "gold-au-live-snapshot-request.v1",
               "decision_date": decision.isoformat(),
               "shfe_manifest_paths": [str(shfe_manifest)], "fred_manifest_path": str(fred_manifest),
               "h10_mapping_receipt_path": str(mapping), "calendar_receipt_path": str(calendar),
               "cost_receipt_path": str(cost)}
    paths = {"shfe": shfe_manifest, "fred": fred_manifest, "mapping": mapping,
             "calendar": calendar, "cost": cost}
    return request, decision, paths


class LiveSnapshotTests(unittest.TestCase):
    def test_explicit_research_only_freezes_observation_without_cost_or_trade_authority(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            request["execution_mode"] = "RESEARCH_ONLY"
            del request["cost_receipt_path"]
            result = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(result["status"], "READY_STRICT_RESEARCH_SIGNAL", result)
            self.assertTrue(result["signal"]["entry"])
            self.assertFalse(result["signal"]["actionable_entry"])
            self.assertEqual(result["signal"]["action_block"], "AWAITING_EXECUTION_COST_VERIFICATION")
            self.assertNotIn("planned_one_lot_loss_cny", result["signal"])
            self.assertNotIn("prior_margin_per_lot_cny", result["signal"])
            self.assertGreater(result["signal"]["stop_only_one_lot_loss_cny"], 0)
            self.assertIsNone(result["source_receipts"]["cost"])
            self.assertFalse(result["broker_action_authorized"])
            self.assertTrue(all(row["execution_cost_grade"] == "ASSUMPTION" for row in result["dataset"]["bars"]))
            # Omitting the mode never silently turns missing costs into ready.
            request.pop("execution_mode")
            rejected = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(rejected["reason"], "MISSING_COST_RECEIPT_PATH")

    def test_research_only_cannot_smuggle_costs_or_use_unknown_mode(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            when = datetime.combine(day, time(8, 30), TZ)
            request["execution_mode"] = "RESEARCH_ONLY"
            self.assertEqual(prepare_live_snapshot(request, as_of=when)["reason"],
                             "RESEARCH_ONLY_CANNOT_ASSERT_EXECUTION_COST")
            request["execution_mode"] = "TRADE_ANYWAY"
            self.assertEqual(prepare_live_snapshot(request, as_of=when)["reason"], "INVALID_EXECUTION_MODE")

    def test_backfill_known_today_warms_current_signal_but_not_historical_decisions(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            manifest = json.loads(paths["shfe"].read_text())
            # Mirrors actual deployment: completed history was acquired only
            # recently, rather than fictitiously acquired on each past date.
            acquired = stamp(day, 8, 5)
            for report in manifest["reports"]:
                report["captured_at"] = acquired
            paths["shfe"].write_text(json.dumps(manifest))
            before = paths["shfe"].read_bytes()
            when = datetime.combine(day, time(8, 30), TZ)
            result = prepare_live_snapshot(request, as_of=when)
            self.assertEqual(result["status"], "READY_STRICT_RESEARCH_SIGNAL", result)
            self.assertTrue(result["signal"]["actionable_entry"])
            self.assertFalse(result["broker_action_authorized"])
            self.assertEqual(result["signal"]["price_information_set"],
                             "CURRENT_DECISION_LOOKBACK_NOT_HISTORICAL_SIGNALS")
            self.assertEqual(paths["shfe"].read_bytes(), before)
            self.assertTrue(all(datetime.fromisoformat(row["retrieved_at"]) == datetime.fromisoformat(acquired)
                                for row in result["dataset"]["bars"]))
            old_information_path = evaluate_signal(result["dataset"], day.isoformat(), pit_mode="strict")
            self.assertEqual(old_information_path["reason"], "INSUFFICIENT_PRICE_HISTORY")
            self.assertFalse(old_information_path["actionable_entry"])

    def test_current_snapshot_cannot_accept_future_acquisition_or_late_cutoff(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            when = datetime.combine(day, time(8, 30), TZ)
            valid = prepare_live_snapshot(request, as_of=when)
            dataset = GoldAuDataset(valid["dataset"])
            with self.assertRaisesRegex(ValueError, "exactly 08:30"):
                build_current_snapshot_path(dataset, as_of=when + timedelta(seconds=1))
            with self.assertRaisesRegex(ValueError, "current official session"):
                build_current_snapshot_path(dataset, as_of=when - timedelta(days=4))
            manifest = json.loads(paths["shfe"].read_text())
            manifest["reports"][0]["captured_at"] = stamp(day, 8, 31)
            paths["shfe"].write_text(json.dumps(manifest))
            rejected = prepare_live_snapshot(request, as_of=when)
            self.assertEqual(rejected["reason"], "FUTURE_SHFE_CAPTURE")
            self.assertNotIn("signal", rejected)

    def test_research_deferred_policy_is_hard_gate_in_legacy_and_current_replay(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            request["execution_mode"] = "RESEARCH_ONLY"
            del request["cost_receipt_path"]
            result = prepare_live_snapshot(request, as_of=datetime.combine(day,time(8,30),TZ))
            payload = result["dataset"]
            for bar in payload["bars"]:
                bar["execution_cost_grade"] = "CONSERVATIVE"
            for answer in (evaluate_signal(payload,day.isoformat(),pit_mode="strict"),
                           replay_frozen_signal(payload,day.isoformat())):
                self.assertTrue(answer["entry"])
                self.assertFalse(answer["actionable_entry"])
                self.assertEqual(answer["action_block"], "AWAITING_EXECUTION_COST_VERIFICATION")
                self.assertNotIn("planned_one_lot_loss_cny",answer)
                self.assertNotIn("prior_margin_per_lot_cny",answer)
                without_hash={k:v for k,v in answer.items() if k not in {"signal_id","evidence_sha256"}}
                from yuanli_invest.receipts import canonical_hash
                self.assertEqual(canonical_hash(without_hash),answer["evidence_sha256"])

    def test_current_replay_rejects_current_bar_missing_policy_and_future_macro(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            when=datetime.combine(day,time(8,30),TZ)
            result=prepare_live_snapshot(request,as_of=when)
            from copy import deepcopy
            payload=deepcopy(result["dataset"])
            payload["bars"][0]["date"]=day.isoformat()
            with self.assertRaises(ValueError):
                replay_frozen_signal(payload,day.isoformat())
            payload=deepcopy(result["dataset"]);payload.pop("execution_cost_status")
            with self.assertRaisesRegex(ValueError,"explicit execution cost policy"):
                replay_frozen_signal(payload,day.isoformat())
            payload=deepcopy(result["dataset"])
            future=(when+timedelta(seconds=1)).isoformat()
            payload["observations"][0].update(released_at=future,retrieved_at=future,available_at=future)
            with self.assertRaisesRegex(ValueError,"postdecision macro"):
                replay_frozen_signal(payload,day.isoformat())

    def test_official_raw_day_identity_and_malformed_execution_mode_fail_closed(self):
        with TemporaryDirectory() as temporary:
            request, day, paths=fixture(Path(temporary))
            when=datetime.combine(day,time(8,30),TZ)
            request["execution_mode"]=[]
            self.assertEqual(prepare_live_snapshot(request,as_of=when)["reason"],"INVALID_EXECUTION_MODE")
            request.pop("execution_mode")
            manifest=json.loads(paths["shfe"].read_text())
            report=manifest["reports"][-1];raw_path=Path(report["raw_file"])
            raw=json.loads(raw_path.read_text());raw["report_date"]=day.strftime("%Y%m%d")
            encoded=json.dumps(raw).encode();raw_path.write_bytes(encoded)
            digest=hashlib.sha256(encoded).hexdigest();report["raw_sha256"]=digest
            for bar in report["bars"]:bar["source_sha256"]=digest
            paths["shfe"].write_text(json.dumps(manifest))
            self.assertEqual(prepare_live_snapshot(request,as_of=when)["reason"],"SHFE_RAW_REPORT_DATE_MISMATCH")

    def test_ready_signal_has_no_current_bar_and_unknown_wgc_halves_budget(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            result = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(result["status"], "READY_STRICT_RESEARCH_SIGNAL", result)
            self.assertFalse(any(row["date"] == day.isoformat() for row in result["dataset"]["bars"]))
            self.assertEqual(result["signal"]["pit_mode"], "strict")
            self.assertTrue(result["signal"]["actionable_entry"])
            self.assertEqual(result["signal"]["risk"]["credit_multiplier"], 0.5)
            self.assertFalse(result["broker_action_authorized"])
            self.assertTrue(all(row["vintage_kind"] == "REVISION" for row in result["dataset"]["observations"]))

    def test_before_decision_collects_without_frozen_signal(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary))
            result = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 10), TZ))
            self.assertEqual(result["status"], "COLLECTING_BEFORE_DECISION")
            self.assertNotIn("signal", result)

    def test_future_fred_capture_fails_closed(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            manifest = json.loads(paths["fred"].read_text())
            manifest["captures"][1]["captured_at"] = stamp(day, 8, 31)
            paths["fred"].write_text(json.dumps(manifest))
            result = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(result["reason"], "FUTURE_FRED_CAPTURE")

    def test_h10_lag_is_precise_skip(self):
        with TemporaryDirectory() as temporary:
            request, day, _ = fixture(Path(temporary), h10_lag_days=25)
            result = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(result["reason"], "STALE_FED_H10_DTWEXBGS_OBSERVATION")

    def test_missing_calendar_cost_and_official_prior_session_skip(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            missing = dict(request)
            del missing["calendar_receipt_path"]
            self.assertEqual(prepare_live_snapshot(missing, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "MISSING_CALENDAR_RECEIPT_PATH")
            missing = dict(request)
            del missing["cost_receipt_path"]
            self.assertEqual(prepare_live_snapshot(missing, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "MISSING_COST_RECEIPT_PATH")
            manifest = json.loads(paths["shfe"].read_text())
            manifest["reports"].pop()
            paths["shfe"].write_text(json.dumps(manifest))
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "MISSING_REQUIRED_SHFE_SESSIONS")

    def test_exchange_holiday_and_retrospective_mapping_fail_closed(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            calendar = json.loads(paths["calendar"].read_text())
            calendar["sessions"].remove(day.isoformat())
            paths["calendar"].write_text(json.dumps(calendar))
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "CALENDAR_RECEIPT_RAW_DISAGREEMENT")
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            mapping = json.loads(paths["mapping"].read_text())
            mapping["status"] = "EXPLICIT_RETROSPECTIVE_ALIAS_ONLY"
            paths["mapping"].write_text(json.dumps(mapping))
            self.assertEqual(prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))["reason"],
                             "H10_LIVE_MAPPING_NOT_WITNESSED")

    def test_self_asserted_sessions_without_annual_notice_bundle_are_rejected(self):
        with TemporaryDirectory() as temporary:
            request, day, paths = fixture(Path(temporary))
            calendar = json.loads(paths["calendar"].read_text())
            raw_path = paths["calendar"].parent / "raw" / "unsupported.dat"
            raw_path.write_bytes(b"a self-asserted calendar is not official notice evidence")
            calendar["raw_file"] = str(raw_path.resolve())
            calendar["raw_sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
            paths["calendar"].write_text(json.dumps(calendar))
            snapshot = prepare_live_snapshot(request, as_of=datetime.combine(day, time(8, 30), TZ))
            self.assertEqual(snapshot["reason"], "MISSING_OR_INVALID_OFFICIAL_CALENDAR")
            self.assertNotIn("signal", snapshot)


if __name__ == "__main__":
    unittest.main()
