"""Synthetic contract mechanics; no real preregistration or SimNow evidence."""

from __future__ import annotations

import copy
import unittest
from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo

from yuanli_invest.gold_au_forward_settlement import assess_program, settle_forward
from yuanli_invest.receipts import canonical_hash

TZ = ZoneInfo("Asia/Shanghai")
SHA = "b" * 64


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


def bundle() -> dict:
    days = weekdays(date(2026, 9, 28), 25)
    d0, d5, d10, d20 = days[0], days[5], days[10], days[20]
    decision = {"schema_version": "gold-au-forward-decision.v2", "decision_id": "SYNTHETIC-DECISION-001",
                "signal_id": "SYNTHETIC-SIGNAL-001", "strategy_version": "gold-au-strategy.v1",
                "baseline_id": "CASH", "contract": "au2712", "action": "OPEN_LONG", "quantity": 1,
                "environment": "SIMNOW_FIRST_NORMAL", "data_mode": "SYNTHETIC_ENGINEERING_ONLY",
                "decision_at": stamp(d0, 8, 30), "evidence_known_as_of": stamp(d0, 8, 29),
                "evidence_sha256": SHA, "parameters_sha256": SHA,
                "horizons_trading_days": [5, 20], "engineering_test": False}
    registration = {"decision_sha256": canonical_hash(decision),
                    "recorded_at": datetime.combine(d0, time(8, 30, 20), TZ).isoformat(),
                    "registry_id": "SYNTHETIC_TEST_REGISTRY", "record_id": "SYNTHETIC_TEST_RECORD",
                    "source_ref": "SYNTHETIC_REGISTRY_READBACK", "raw_sha256": SHA,
                    "verification": "EXTERNAL_READBACK_REQUIRED", "registry_kind": "SYNTHETIC_FIXTURE",
                    "outcome_contracts": [
                        {"horizon_trading_days": horizon, "session_date": day.isoformat(),
                         "decision_id": decision["decision_id"],
                         "outcome_contract_id": f"SYNTHETIC-OUTCOME-D{horizon}"}
                        for horizon, day in ((5, d5), (20, d20))]}

    def fill(fill_id: str, action: str, day: date, minute: int, price: str, reference: str) -> dict:
        return {"fill_id": fill_id, "decision_id": decision["decision_id"],
                "broker_order_id": "ORDER-" + fill_id, "broker_trade_id": "TRADE-" + fill_id,
                "broker_source_ref": "SYNTHETIC_SIMNOW_LEDGER", "broker_ledger_ref": "SYNTHETIC_LEDGER_DAY",
                "broker_source_kind": "SYNTHETIC_FIXTURE", "reference_source_ref": "SYNTHETIC_QUOTE",
                "reference_raw_sha256": SHA, "contract": "au2712", "action": action, "quantity": 1,
                "environment": "SIMNOW_FIRST_NORMAL", "data_mode": decision["data_mode"],
                "fill_at": stamp(day, 9, minute), "retrieved_at": stamp(day, 9, minute + 1),
                "reconciled_at": stamp(day, 9, minute + 2), "reconciliation_state": "RECONCILED",
                "price_cny_per_gram": price, "reference_price_cny_per_gram": reference,
                "fee_cny": "20", "raw_sha256": SHA}

    def mark(horizon: int, day: date, ids: list[str], contract: str | None, price: str | None) -> dict:
        return {"snapshot_id": f"SYNTHETIC-MARK-{horizon}", "horizon_trading_days": horizon,
                "session_date": day.isoformat(), "decision_id": decision["decision_id"],
                "outcome_contract_id": f"SYNTHETIC-OUTCOME-D{horizon}",
                "data_mode": decision["data_mode"], "source_kind": "SYNTHETIC_FIXTURE",
                "source_ref": "SYNTHETIC_SIMNOW_AND_EXCHANGE_MARK", "broker_ledger_ref": "SYNTHETIC_LEDGER_DAY",
                "broker_fill_ids": ids, "broker_reconciled": True,
                "observed_at": stamp(day, 15), "published_at": stamp(day, 15, 5),
                "retrieved_at": stamp(day, 15, 6), "available_at": stamp(day, 15, 6),
                "vintage_kind": "FIRST_RELEASE", "raw_sha256": SHA,
                "mark_contract": contract, "mark_price_cny_per_gram": price,
                "mark_source_ref": "SYNTHETIC_EXCHANGE_CLOSE" if contract else None,
                "mark_raw_sha256": SHA if contract else None}

    return {"decision": decision, "registration": registration,
            "exchange_calendar": {"calendar_id": "SYNTHETIC_CALENDAR", "source_kind": "SYNTHETIC_FIXTURE",
                                  "source_ref": "SYNTHETIC_SHFE_SESSIONS", "raw_sha256": SHA,
                                  "sessions": [day.isoformat() for day in days]},
            "broker_fills": [fill("ENTRY-001", "OPEN_LONG", d0, 1, "1000", "999.98"),
                             fill("EXIT-001", "CLOSE_LONG", d10, 0, "1010", "1010.02")],
            "outcome_snapshots": [mark(5, d5, ["ENTRY-001"], "au2712", "1005"),
                                  mark(20, d20, ["ENTRY-001", "EXIT-001"], None, None)],
            "as_of": stamp(d20, 18)}


class ForwardSettlementTests(unittest.TestCase):
    def test_two_prospective_horizons_replay_actual_fills_fees_and_slippage(self):
        result = settle_forward(bundle())
        self.assertEqual(result["status"], "SETTLED_BOTH_HORIZONS")
        self.assertEqual(result["horizons"]["5"]["net_pnl_cny"], "4980.00")
        self.assertEqual(result["horizons"]["20"]["net_pnl_cny"], "9960.00")
        self.assertEqual(result["horizons"]["20"]["fees_cny"], "40.00")
        self.assertEqual(result["horizons"]["20"]["slippage_vs_reference_cny"], "40.00")
        self.assertFalse(result["investment_effectiveness_proven"])
        self.assertFalse(result["broker_action_authorized"])

    def test_future_horizon_is_not_scored_before_due(self):
        payload = bundle()
        payload["as_of"] = stamp(date(2026, 9, 29), 10)
        result = settle_forward(payload)
        self.assertEqual(result["horizons"]["5"]["status"], "NOT_DUE")
        self.assertEqual(result["horizons"]["20"]["status"], "NOT_DUE")

    def test_missing_registration_fill_or_reconciliation_stays_pending(self):
        payload = bundle()
        del payload["registration"]
        self.assertEqual(settle_forward(payload)["status"], "PENDING_INDEPENDENT_REGISTRATION")
        payload = bundle()
        del payload["exchange_calendar"]
        self.assertEqual(settle_forward(payload)["status"], "PENDING_CALENDAR_COVERAGE")
        payload = bundle()
        payload["broker_fills"] = []
        self.assertEqual(settle_forward(payload)["status"], "PENDING_BROKER_FILL")
        payload = bundle()
        payload["broker_fills"][0]["reconciliation_state"] = "PENDING"
        payload["broker_fills"][0]["reconciled_at"] = None
        self.assertEqual(settle_forward(payload)["status"], "PENDING_BROKER_RECONCILIATION")

    def test_late_or_changed_registration_cannot_backfill_decision(self):
        payload = bundle()
        payload["registration"]["recorded_at"] = stamp(date(2026, 9, 28), 9, 1)
        with self.assertRaisesRegex(ValueError, "08:30:59"):
            settle_forward(payload)
        payload = bundle()
        payload["registration"]["recorded_at"] = datetime.combine(
            date(2026, 9, 28), time(8, 31), TZ).isoformat()
        with self.assertRaisesRegex(ValueError, "08:30:59"):
            settle_forward(payload)
        payload = bundle()
        payload["decision"]["evidence_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "registration does not bind"):
            settle_forward(payload)
        payload = bundle()
        payload["decision"]["evidence_known_as_of"] = stamp(date(2026, 9, 28), 8, 31)
        payload["registration"]["decision_sha256"] = canonical_hash(payload["decision"])
        with self.assertRaisesRegex(ValueError, "post-decision evidence"):
            settle_forward(payload)

    def test_outcome_ids_must_be_frozen_before_ticket_and_match_later_snapshot(self):
        payload = bundle()
        payload["registration"]["outcome_contracts"][0]["session_date"] = "2026-10-01"
        with self.assertRaisesRegex(ValueError, "preregistered outcome contract"):
            settle_forward(payload)
        payload = bundle()
        payload["outcome_snapshots"][0]["outcome_contract_id"] = "REPLACED-AFTER-ENTRY"
        with self.assertRaisesRegex(ValueError, "preregistered contract ID"):
            settle_forward(payload)

    def test_late_outcome_capture_and_incomplete_ledger_remain_pending(self):
        payload = bundle()
        day20 = date.fromisoformat(payload["outcome_snapshots"][1]["session_date"])
        late = stamp(day20 + timedelta(days=2), 11)
        payload["outcome_snapshots"][1]["retrieved_at"] = late
        payload["outcome_snapshots"][1]["available_at"] = late
        payload["as_of"] = stamp(day20 + timedelta(days=3), 12)
        self.assertEqual(settle_forward(payload)["horizons"]["20"]["status"], "PENDING_LATE_OUTCOME_CAPTURE")
        payload = bundle()
        payload["outcome_snapshots"][1]["broker_fill_ids"] = ["ENTRY-001"]
        self.assertEqual(settle_forward(payload)["horizons"]["20"]["status"], "PENDING_BROKER_RECONCILIATION")

    def test_duplicate_entry_and_duplicate_fill_id_fail_closed(self):
        payload = bundle()
        payload["broker_fills"].append(copy.deepcopy(payload["broker_fills"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate broker fill"):
            settle_forward(payload)
        payload = bundle()
        extra = copy.deepcopy(payload["broker_fills"][0])
        extra.update({"fill_id": "ENTRY-002", "broker_order_id": "ORDER-002", "broker_trade_id": "TRADE-002",
                      "fill_at": stamp(date(2026, 9, 28), 9, 2),
                      "retrieved_at": stamp(date(2026, 9, 28), 9, 3),
                      "reconciled_at": stamp(date(2026, 9, 28), 9, 4)})
        payload["broker_fills"].insert(1, extra)
        payload["outcome_snapshots"][0]["broker_fill_ids"].append("ENTRY-002")
        payload["outcome_snapshots"][1]["broker_fill_ids"].append("ENTRY-002")
        with self.assertRaisesRegex(ValueError, "duplicate overlapping long"):
            settle_forward(payload)

    def test_program_gate_requires_both_12_months_and_30_independent_entries(self):
        start = date(2026, 1, 5)
        receipts = []
        for i in range(30):
            entry = start + timedelta(days=i * 13)
            close = entry + timedelta(days=5)
            receipts.append({"schema_version": "gold-au-forward-settlement.v2", "decision_id": f"D-{i}",
                             "entry_fill_id": f"F-{i}", "data_mode": "REAL_PAPER_OBSERVATIONS",
                             "engineering_test": False, "status": "SETTLED_BOTH_HORIZONS",
                             "entry_at": stamp(entry, 9),
                             "horizons": {"20": {"status": "SETTLED_PROSPECTIVE_PAPER_OUTCOME",
                                                 "last_close_at": stamp(close, 9)}}})
        early = assess_program(receipts, as_of=stamp(date(2026, 12, 31), 12))
        self.assertFalse(early["prospective_sample_gate_met"])
        mature = assess_program(receipts, as_of=stamp(date(2027, 2, 1), 12))
        self.assertTrue(mature["prospective_sample_gate_met"])
        self.assertFalse(mature["eligible_for_investment_review"])
        self.assertFalse(mature["investment_effectiveness_proven"])
        receipts[0]["engineering_test"] = True
        self.assertFalse(assess_program(receipts, as_of=stamp(date(2027, 2, 1), 12))["prospective_sample_gate_met"])

    def test_overlapping_entries_do_not_count_as_independent(self):
        base = {"schema_version": "gold-au-forward-settlement.v2", "data_mode": "REAL_PAPER_OBSERVATIONS",
                "engineering_test": False, "status": "SETTLED_BOTH_HORIZONS",
                "horizons": {"20": {"status": "SETTLED_PROSPECTIVE_PAPER_OUTCOME"}}}
        receipts = []
        for i in range(30):
            row = copy.deepcopy(base)
            row.update({"decision_id": f"D-{i}", "entry_fill_id": f"F-{i}",
                        "entry_at": stamp(date(2026, 1, 5) + timedelta(days=i), 9)})
            row["horizons"]["20"]["last_close_at"] = stamp(date(2026, 3, 1), 9)
            receipts.append(row)
        result = assess_program(receipts, as_of=stamp(date(2027, 6, 1), 12))
        self.assertEqual(result["independent_entries"], 1)
        self.assertFalse(result["prospective_sample_gate_met"])


if __name__ == "__main__":
    unittest.main()
