from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import unittest

from yuanli_invest.gold_paper import PaperDenied, PaperLedger, _digest, validate_strategy_equity_mark
from yuanli_invest.gold_au_strategy_accounting import build_strategy_equity_mark, validate_strategy_subledger_mark, initialize_allocation
from tests.test_gold_paper import grant

NOW = datetime(2026, 9, 28, 1, 15, tzinfo=timezone.utc)
ACCOUNT = "SIMNOW-TEST-ACCOUNT"


def baseline():
    ledger = PaperLedger()
    ledger.append("StrategyAllocationInitialized", "CMD-ALLOCATION-0001", NOW.isoformat(), {
        "initial_equity": "5000000", "broker_equity": "10000000", "environment": "SIMNOW_FIRST_NORMAL",
        "account_id": ACCOUNT, "position_quantity": 0, "pending_order_count": 0,
        "approval_ref": "USER-PAPER-GRANT-0001", "raw_sha256": _digest({"baseline": 1}),
    })
    return ledger


def fill(ledger, ident, action, price, fee="20"):
    ledger.append("StrategyFillBooked", "CMD-TRADE-" + ident, NOW.isoformat(), {
        "trade_id": ident, "account_id": ACCOUNT, "environment": "SIMNOW_FIRST_NORMAL", "contract": "au2612",
        "action": action, "price": price, "fee_cny": fee, "quantity": 1,
        "raw_sha256": _digest({"native_trade": ident}),
    })


def snapshot(ledger=None, **fields):
    result = {"source": "simnow_strategy_accounting_readback", "account_id": ACCOUNT,
              "environment": "SIMNOW_FIRST_NORMAL", "history_complete": True,
              "external_cashflows_cny": "0", "pending_order_count": 0, "observed_at": NOW.isoformat(),
              "broker_equity": "10000000", "position_quantity": 0, "trade_ids": [], "settlement_ids": [],
              "trade_facts": [], "settlement_facts": []}
    for scope in ("account", "trades", "settlements", "positions"):
        result[scope + "_raw_sha256"] = _digest({"native_scope": scope})
    if ledger is not None:
        for kind, field, ident in (("StrategyFillBooked", "trade_facts", "trade_id"), ("StrategySettlementBooked", "settlement_facts", "settlement_id")):
            result[field] = list({e["data"][ident]: e["data"] for e in ledger.events if e["kind"] == kind}.values())
    result.update(fields)
    return result


class AccountingTests(unittest.TestCase):
    def test_allocation_requires_actual_flat_baseline_and_keeps_uncertain_anchor(self):
        observed = {"source": "simnow_native_ctp_readonly_facts", "environment": "SIMNOW_FIRST_NORMAL",
            "account_id": ACCOUNT, "positions": [], "pending_orders": [], "pending_order_count": 0,
            "broker_equity": "10000000", "observed_at": "2026-09-29T01:01:00+00:00",
            "available_at": "2026-09-29T01:01:00+00:00"}
        for key in ("raw_account_sha256", "raw_positions_sha256", "raw_orders_sha256"):
            observed[key] = _digest({"native": key})
        observed["raw_sha256"] = _digest(observed)
        from tests.test_gold_paper import NOW as trading_now
        ledger = PaperLedger()
        result = initialize_allocation(ledger, observed, grant(), trading_now, lambda ledger: None)
        self.assertEqual(result["initial_equity"], "5000000")
        with self.assertRaisesRegex(PaperDenied, "ALREADY_STARTED"):
            initialize_allocation(ledger, observed, grant(), trading_now, lambda ledger: None)
        ledger = PaperLedger()
        def failed_anchor(ledger):
            raise TimeoutError()
        with self.assertRaisesRegex(PaperDenied, "ANCHOR_UNCERTAIN"):
            initialize_allocation(ledger, observed, grant(), trading_now, failed_anchor)
        self.assertEqual(len(ledger.events), 1)

    def test_future_bookkeeping_cannot_enter_an_earlier_mark(self):
        ledger = baseline()
        fill(ledger, "future-trade", "OPEN_LONG", "1000")
        ledger.events  # public accessor stays a copy
        events = ledger.events
        events[-1]["at"] = "2026-09-28T02:00:00+00:00"
        events[-1]["event_hash"] = _digest({k: v for k, v in events[-1].items() if k != "event_hash"})
        future = PaperLedger(events)
        with self.assertRaisesRegex(PaperDenied, "JOURNAL_AFTER_READBACK"):
            build_strategy_equity_mark(future, snapshot(future, position_quantity=1, contract="au2612", mark_price="1000",
                broker_equity="9999980", trade_ids=["future-trade"]), NOW)
    def test_five_million_allocation_is_distinct_from_ten_million_broker(self):
        ledger = baseline()
        mark = build_strategy_equity_mark(ledger, snapshot(), NOW)
        self.assertEqual(mark["equity"], "5000000")
        self.assertEqual(mark["unallocated_equity"], "5000000")
        self.assertEqual(validate_strategy_equity_mark(mark, {"account_id": ACCOUNT, "broker_equity": "10000000"}, NOW, ledger), Decimal("5000000"))

    def test_settlement_resets_basis_without_double_counting_and_stop_entry_stays(self):
        ledger = baseline()
        fill(ledger, "trade-open", "OPEN_LONG", "1000")
        ledger.append("StrategySettlementBooked", "CMD-SETTLEMENT-0001", NOW.isoformat(), {
            "settlement_id": "day-20260928", "account_id": ACCOUNT, "environment": "SIMNOW_FIRST_NORMAL",
            "contract": "au2612", "settlement_price": "1010", "variation_pnl_cny": "10000",
            "position_quantity": 1, "raw_sha256": _digest({"native_settlement": 1}),
        })
        mark = build_strategy_equity_mark(ledger, snapshot(ledger, position_quantity=1, contract="au2612", mark_price="1012",
            broker_equity="10011980", trade_ids=["trade-open"], settlement_ids=["day-20260928"]), NOW)
        self.assertEqual(mark["equity"], "5011980")
        self.assertEqual(mark["floating_pnl_cny"], "2000")
        fill(ledger, "trade-close", "CLOSE_LONG", "1012")
        mark = build_strategy_equity_mark(ledger, snapshot(ledger, broker_equity="10011960",
            trade_ids=["trade-close", "trade-open"], settlement_ids=["day-20260928"]), NOW)
        self.assertEqual(mark["equity"], "5011960")

    def test_duplicate_trade_does_not_double_book_but_conflict_denies(self):
        ledger = baseline()
        fill(ledger, "trade-open", "OPEN_LONG", "1000")
        fill(ledger, "trade-open", "OPEN_LONG", "1000")
        mark = build_strategy_equity_mark(ledger, snapshot(ledger, position_quantity=1, contract="au2612", mark_price="1000",
            broker_equity="9999980", trade_ids=["trade-open"]), NOW)
        self.assertEqual(mark["equity"], "4999980")
        fill(ledger, "trade-open", "OPEN_LONG", "1001")
        with self.assertRaisesRegex(PaperDenied, "TRADE_ID_CONFLICT"):
            build_strategy_equity_mark(ledger, snapshot(), NOW)

    def test_unknown_cross_day_history_and_unassigned_activity_block(self):
        for overrides in ({"history_complete": False}, {"trade_ids": ["outside-trade"]},
                          {"broker_equity": "10000001"}, {"external_cashflows_cny": "1"},
                          {"observed_at": "2026-09-28T01:14:00+00:00"}):
            with self.subTest(overrides=overrides), self.assertRaises(PaperDenied):
                build_strategy_equity_mark(baseline(), snapshot(**overrides), NOW)

    def test_tampered_equity_or_nonmatching_ledger_cannot_be_admitted(self):
        ledger = baseline()
        mark = build_strategy_equity_mark(ledger, snapshot(), NOW)
        tampered = deepcopy(mark)
        tampered["equity"] = "6000000"
        with self.assertRaisesRegex(PaperDenied, "REPLAY_MISMATCH"):
            validate_strategy_subledger_mark(tampered, NOW, ledger)
        other = baseline()
        fill(other, "unrelated", "OPEN_LONG", "1000")
        with self.assertRaisesRegex(PaperDenied, "PREFIX_MISMATCH"):
            validate_strategy_subledger_mark(mark, NOW, other)

    def test_marks_do_not_embed_previous_marks_recursively(self):
        ledger = baseline()
        for index in range(10):
            mark = build_strategy_equity_mark(ledger, snapshot(), NOW)
            self.assertEqual(len(mark["proof"]["journal"]), 1)
            ledger.append("EquityMarked", "CMD-EQUITY-" + str(index).zfill(8), NOW.isoformat(), mark)
            validate_strategy_subledger_mark(mark, NOW, ledger)

    def test_bad_settlement_is_not_credited_as_profit(self):
        ledger = baseline()
        fill(ledger, "trade-open", "OPEN_LONG", "1000")
        ledger.append("StrategySettlementBooked", "CMD-SETTLEMENT-0001", NOW.isoformat(), {
            "settlement_id": "day-20260928", "account_id": ACCOUNT, "environment": "SIMNOW_FIRST_NORMAL",
            "contract": "au2612", "settlement_price": "1010", "variation_pnl_cny": "20000",
            "position_quantity": 1, "raw_sha256": _digest({"native_settlement": 1}),
        })
        with self.assertRaisesRegex(PaperDenied, "SETTLEMENT_PNL_MISMATCH"):
            build_strategy_equity_mark(ledger, snapshot(), NOW)
