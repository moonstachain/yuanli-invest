import json
import sys
import unittest
from copy import deepcopy
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from yuanli_invest.gold_paper import (  # noqa: E402
    PaperDenied,
    PaperGrant,
    PaperLedger,
    SIMNOW_FIRST,
    PROGRAM,
    admit_command,
    close_direction,
    contingent_exit_reason,
    reconcile_four_way,
    sign_command,
    trend_exit_reason,
)


KEY = b"paper-only-test-key-32-bytes-minimum"
NOW = datetime.fromisoformat("2026-09-29T09:01:00+08:00")
EVENT_AT = "2026-09-29T09:01:00+08:00"


def payload(**changes):
    result = {
        "schema_version": "1.0.0",
        "program": PROGRAM,
        "command_id": "CMD-GOLD2-000001",
        "action_contract_id": "AC-GOLD2-000001",
        "execution_intent_id": "EI-GOLD2-000001",
        "capital_admission_id": "CA-GOLD2-000001",
        "human_approval_ref": "HUMAN-PAPER-001",
        "program_approval_ref": "PROGRAM-PAPER-001",
        "decision_at": "2026-09-29T08:30:00+08:00",
        "issued_at": "2026-09-29T09:00:00+08:00",
        "not_before_at": "2026-09-29T09:00:00+08:00",
        "expires_at": "2026-09-29T09:05:00+08:00",
        "environment": SIMNOW_FIRST,
        "account_id": "SIMNOW-TEST-ACCOUNT",
        "robot_id": 12345,
        "contract": "au2612",
        "action": "OPEN_LONG",
        "reason": "ENTRY",
        "quantity": 1,
        "reference_price": "1000.00",
        "limit_price": "1000.02",
        "stop_price": "990.00",
        "exit_not_after_at": "2026-10-30T15:00:00+08:00",
        "roll_not_after_at": "2026-11-02T15:00:00+08:00",
        "credit_multiplier": "1",
        "volatility_multiplier": "1",
        "max_slippage_bps": "20",
        "evidence_hash": "sha256:" + "a" * 64,
        "live_execution_authorized": False,
        "real_capital_movement_authorized": False,
    }
    result.update(changes)
    return result


def grant(**changes):
    fields = {
        "program_approval_ref": "PROGRAM-PAPER-001",
        "human_approval_ref": "HUMAN-PAPER-001",
        "account_id": "SIMNOW-TEST-ACCOUNT",
        "robot_id": 12345,
        "starts_at": "2026-09-28T00:00:00+08:00",
        "expires_at": "2026-11-30T00:00:00+08:00",
        "enabled": True,
    }
    fields.update(changes)
    return PaperGrant(**fields)


def snapshot(**changes):
    value = {
        "source": "provider_readback",
        "identity_verified": True,
        "environment": SIMNOW_FIRST,
        "account_id": "SIMNOW-TEST-ACCOUNT",
        "robot_id": 12345,
        "connected": True,
        "reconciled": True,
        "observed_at": "2026-09-29T09:00:58+08:00",
        "contract_meta": {
            "InstrumentID": "au2612",
            "ExchangeID": "SHFE",
            "VolumeMultiple": 1000,
            "PriceTick": 0.02,
            "DeliveryYear": 2026,
            "DeliveryMonth": 12,
            "IsTrading": 1,
        },
        "positions": [],
        "open_order_ids": [],
        "margin_for_one_lot": "200000",
        "round_trip_fee_upper_cny": "80",
        "margin_in_use": "0",
        "available": "4000000",
        "broker_equity": "5000000",
    }
    value.update(changes)
    return value


def equity_mark(*, equity="5000000", broker_equity="5000000", **changes):
    value = {
        "source": "independent_strategy_accounting", "reconciled": True,
        "allocation_scope": "DEDICATED_STRATEGY_PAPER_ACCOUNT",
        "environment": SIMNOW_FIRST, "account_id": "SIMNOW-TEST-ACCOUNT",
        "observed_at": EVENT_AT, "equity": equity,
        "broker_equity": broker_equity, "raw_sha256": "sha256:" + "e" * 64,
    }
    value.update(changes)
    return value


class PaperAuthorizationTests(unittest.TestCase):
    def admit(self, body=None, provider=None, program_grant=None, ledger=None, now=NOW, mark=True):
        ledger = ledger if ledger is not None else PaperLedger()
        if mark and ledger.latest_equity_mark() is None:
            ledger.append("EquityMarked", "CMD-GOLD2-MARK-01", EVENT_AT, equity_mark())
        return admit_command(
            sign_command(body or payload(), KEY),
            KEY,
            program_grant or grant(),
            provider or snapshot(),
            ledger,
            now,
        )

    def test_cloud_grant_cannot_relax_frozen_v1_capital_limits(self):
        for override in (
            {"strategy_initial_equity": "10000000"},
            {"max_risk_fraction": "0.02"},
            {"max_drawdown_fraction": "0.50"},
            {"max_margin_fraction": "0.80"},
            {"max_slippage_bps": "50"},
        ):
            with self.subTest(override=override), self.assertRaises(PaperDenied) as error:
                self.admit(program_grant=grant(**override))
            self.assertEqual(error.exception.code, "PAPER_GRANT_EXCEEDS_FROZEN_V1_LIMITS")

    def test_engineering_open_requires_exact_one_command_grant(self):
        test_body = payload(reason="ENGINEERING_TEST")
        with self.assertRaises(PaperDenied) as error:
            self.admit(body=test_body)
        self.assertEqual(error.exception.code, "ENGINEERING_TEST_NOT_EXACTLY_GRANTED")
        allowed = self.admit(body=test_body, program_grant=grant(engineering_test_command_id=test_body["command_id"]))
        self.assertEqual(allowed["decision"], "ALLOW")
        with self.assertRaises(PaperDenied) as wrong:
            self.admit(body=test_body, program_grant=grant(engineering_test_command_id="CMD-GOLD2-OTHER-1"))
        self.assertEqual(wrong.exception.code, "ENGINEERING_TEST_NOT_EXACTLY_GRANTED")

    def assert_denied(self, code, **kwargs):
        with self.assertRaises(PaperDenied) as error:
            self.admit(**kwargs)
        self.assertEqual(error.exception.code, code)

    def test_bounded_valid_entry(self):
        admitted = self.admit()
        self.assertEqual(admitted["decision"], "ALLOW")
        self.assertEqual(admitted["command"]["contract"], "au2612")
        self.assertIsNone(admitted["position_age"])

    def test_no_broker_paper_authority_inherited_from_constitution(self):
        self.assert_denied("PAPER_PROGRAM_DISABLED", program_grant=grant(enabled=False))
        self.assert_denied("APPROVAL_REFERENCE_MISMATCH", body=payload(program_approval_ref="UNAPPROVED-0001"))

    def test_tamper_and_content_hash_cannot_be_bypassed(self):
        signed = sign_command(payload(), KEY)
        signed["payload"]["quantity"] = 2
        with self.assertRaises(PaperDenied) as error:
            admit_command(signed, KEY, grant(), snapshot(), PaperLedger(), NOW)
        self.assertEqual(error.exception.code, "SIGNATURE_MISMATCH")
        signed = sign_command(payload(), KEY)
        signed["payload"]["contract_hash"] = "sha256:" + "0" * 64
        import hashlib
        import hmac
        canonical = json.dumps(signed["payload"], sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        signed["signature"] = "hmac-sha256:" + hmac.new(KEY, canonical, hashlib.sha256).hexdigest()
        with self.assertRaises(PaperDenied) as error:
            admit_command(signed, KEY, grant(), snapshot(), PaperLedger(), NOW)
        self.assertEqual(error.exception.code, "CONTRACT_HASH_MISMATCH")

    def test_only_simnow_one_dated_au_and_no_live_flags(self):
        self.assert_denied("NOT_A_DATED_AU_CONTRACT", body=payload(contract="au888"))
        self.assert_denied("ORDER_SCOPE_EXPANSION", body=payload(quantity=2))
        self.assert_denied("LIVE_OR_CAPITAL_FLAG", body=payload(live_execution_authorized=True))
        self.assert_denied("PAPER_IDENTITY_MISMATCH", body=payload(environment="CTP_LIVE"))
        self.assert_denied("UNVERIFIED_SIMNOW_IDENTITY", provider=snapshot(identity_verified=False))
        self.assert_denied("CONTRACT_IDENTITY_MISMATCH", provider=snapshot(contract_meta={**snapshot()["contract_meta"], "InstrumentID": "au2702"}))
        self.assert_denied("CONTRACT_DELIVERY_METADATA_MISMATCH", provider=snapshot(contract_meta={**snapshot()["contract_meta"], "DeliveryYear": 2027}))
        self.assert_denied("DELIVERY_TOO_NEAR", body=payload(contract="au2610"), provider=snapshot(contract_meta={**snapshot()["contract_meta"], "InstrumentID": "au2610", "DeliveryMonth": 10}))
        self.assert_denied("GRANT_EXPIRES_BEFORE_CONTINGENT_EXIT",
                           program_grant=grant(expires_at="2026-10-01T00:00:00+08:00"))

    def test_risk_window_and_external_state_fail_closed(self):
        self.assert_denied("PLANNED_LOSS_LIMIT", body=payload(stop_price="960.00"))
        self.assert_denied("PLANNED_LOSS_LIMIT", body=payload(stop_price="975.02"))
        self.assert_denied("INVALID_ROUND_TRIP_FEE_UPPER_CNY", provider=snapshot(round_trip_fee_upper_cny=None))
        self.assert_denied("PLANNED_LOSS_LIMIT", body=payload(stop_price="985.00", credit_multiplier="0.5"))
        self.assert_denied("MARGIN_LIMIT", provider=snapshot(margin_for_one_lot="1600000"))
        self.assert_denied("EXTERNAL_OPEN_ORDER", provider=snapshot(open_order_ids=["ORDER-EXTERNAL-1"]))
        self.assert_denied("PROVIDER_STATE_UNKNOWN", provider=snapshot(reconciled=False))
        self.assert_denied("ENTRY_EXECUTION_WINDOW", body=payload(issued_at="2026-09-29T09:04:00+08:00", not_before_at="2026-09-29T09:04:00+08:00", expires_at="2026-09-29T09:09:00+08:00"), now=datetime.fromisoformat("2026-09-29T09:06:00+08:00"))
        self.assert_denied("COMMAND_EXPIRED_OR_FUTURE", body=payload(expires_at="2026-09-29T09:00:30+08:00"))

    def test_drawdown_and_duplicate_delivery(self):
        ledger = PaperLedger()
        ledger.append("EquityMarked", "CMD-GOLD2-MARK-01", EVENT_AT,
                      equity_mark(equity="4749000", broker_equity="4749000"))
        self.assert_denied("DRAWDOWN_STOP", ledger=ledger, provider=snapshot(broker_equity="4749000"))
        ledger = PaperLedger()
        signed = sign_command(payload(), KEY)
        ledger.append("ActionAdmitted", payload()["command_id"], EVENT_AT, {"contract_hash": signed["payload"]["contract_hash"]})
        replay = admit_command(signed, KEY, grant(), snapshot(), ledger, NOW)
        self.assertEqual(replay["decision"], "DUPLICATE_NO_SUBMIT")
        ledger.append("OrderSubmitAttempted", payload()["command_id"], EVENT_AT, {})
        self.assert_denied("UNRESOLVED_ORDER_OR_DRIFT", ledger=ledger, body=payload(command_id="CMD-GOLD2-000002"))

    def test_fresh_independent_equity_mark_required_for_drawdown_gate(self):
        self.assert_denied("STRATEGY_EQUITY_MARK_MISSING", mark=False,
                           provider=snapshot(broker_equity="4700000"))
        ledger = PaperLedger()
        ledger.append("EquityMarked", "CMD-GOLD2-MARK-01", EVENT_AT, equity_mark())
        self.assert_denied("STRATEGY_EQUITY_BROKER_DELTA", ledger=ledger,
                           provider=snapshot(broker_equity="4700000"))

    def test_close_today_yesterday_and_unknown(self):
        self.assertEqual(close_direction("TODAY"), "closebuy_today")
        self.assertEqual(close_direction("YESTERDAY"), "closebuy")
        with self.assertRaises(PaperDenied):
            close_direction("UNKNOWN")
        body = payload(
            command_id="CMD-GOLD2-CLOSE01", action="CLOSE_LONG", reason="EXIT_STOP",
            stop_price=None,
        )
        provider = snapshot(positions=[{"contract": "au2612", "side": "LONG", "quantity": 1, "age": "TODAY"}])
        admitted = self.admit(body=body, provider=provider)
        self.assertEqual(admitted["position_age"], "TODAY")
        self.assert_denied("CLOSE_POSITION_MISMATCH", body=body)


class PaperTruthTests(unittest.TestCase):
    def test_hash_chain_detects_tamper(self):
        ledger = PaperLedger()
        ledger.append("ActionAdmitted", "CMD-GOLD2-000001", EVENT_AT, {"contract_hash": "sha256:" + "a" * 64})
        events = ledger.events
        events[0]["data"]["contract_hash"] = "sha256:" + "b" * 64
        with self.assertRaises(PaperDenied):
            PaperLedger(events)

    def test_contingent_stop_roll_and_time(self):
        position = {
            "contingent_exit_authorized": True,
            "origin_action_contract_id": "AC-GOLD2-000001",
            "stop_price": "990.00",
            "roll_not_after_at": "2026-10-25T15:00:00+08:00",
            "exit_not_after_at": "2026-10-30T15:00:00+08:00",
        }
        self.assertEqual(contingent_exit_reason(position, "989.98", NOW), "EXIT_STOP")
        self.assertEqual(contingent_exit_reason(position, "1000", datetime.fromisoformat("2026-10-26T09:00:00+08:00")), "EXIT_ROLL")
        later = deepcopy(position)
        later["roll_not_after_at"] = "2026-11-02T15:00:00+08:00"
        self.assertEqual(contingent_exit_reason(later, "1000", datetime.fromisoformat("2026-10-31T09:00:00+08:00")), "EXIT_TIME")
        with self.assertRaises(PaperDenied):
            contingent_exit_reason({**position, "contingent_exit_authorized": False}, "900", NOW)

    def test_roll_and_max_hold_begin_exit_before_close_deadline(self):
        base = {
            "contingent_exit_authorized": True,
            "origin_action_contract_id": "AC-GOLD2-000001",
            "stop_price": "990.00",
            "roll_not_after_at": "2026-05-29T15:00:00+08:00",
            "exit_not_after_at": "2026-06-18T15:00:00+08:00",
        }
        self.assertIsNone(contingent_exit_reason(base, "1000", datetime.fromisoformat("2026-05-29T14:44:59+08:00")))
        self.assertEqual(contingent_exit_reason(base, "1000", datetime.fromisoformat("2026-05-29T14:45:00+08:00")), "EXIT_ROLL")
        held = {**base, "roll_not_after_at": "2026-07-01T15:00:00+08:00"}
        self.assertEqual(contingent_exit_reason(held, "1000", datetime.fromisoformat("2026-06-18T14:45:00+08:00")), "EXIT_TIME")

    def test_five_session_prior_ten_close_trend_exit(self):
        from datetime import date, timedelta
        now = datetime.fromisoformat("2026-10-08T09:01:00+08:00")
        days = []
        day = date(2026, 9, 1)
        while day < now.date():
            if day.weekday() < 5:
                days.append(day)
            day += timedelta(days=1)
        history = {"source": "independent_shfe_dated_daily_close_readback", "contract": "au2612",
                   "verified_session_calendar": True, "observed_at": now.isoformat(),
                   "next_session_date": now.date().isoformat(),
                   "last_completed_session_date": days[-1].isoformat(),
                   "bars": [{"date": day.isoformat(), "close": "900" if day == days[-1] else "1000",
                             "raw_sha256": "sha256:" + "a" * 64} for day in days]}
        context = {"contingent_exit_authorized": True, "contract": "au2612",
                   "entry_session_date": "2026-09-29"}
        self.assertEqual(trend_exit_reason(context, history, now), "EXIT_TREND")
        self.assertIsNone(trend_exit_reason({**context, "entry_session_date": "2026-10-05"}, history, now))
        self.assertIsNone(trend_exit_reason(context, {**history, "bars": [*history["bars"][:-1],
                                                                  {**history["bars"][-1], "close": "1000"}]}, now))
        with self.assertRaises(PaperDenied):
            trend_exit_reason(context, {**history, "verified_session_calendar": False}, now)

    def test_four_way_reconciliation_requires_order_position_cash_agreement(self):
        base = {"account_id": "SIMNOW-TEST-ACCOUNT", "contract": "au2612"}
        shared = {**base, "filled_quantity": 1, "cash": "4800000.00", "available": "4500000.00",
                  "frozen_margin": "0", "order_ids": ["O-1"], "observed_at": EVENT_AT}
        capital = {**shared, "source": "capital_intent_ledger", "raw_sha256": "sha256:" + "a" * 64,
                   "target_quantity": 1}
        yuanli = {**shared, "source": "yuanli_execution_ledger", "raw_sha256": "sha256:" + "b" * 64,
                  "position_quantity": 1}
        oms = {**shared, "source": "execution_oms_readback", "raw_sha256": "sha256:" + "c" * 64,
               "position_quantity": 1}
        broker = {**shared, "source": "simnow_broker_custodian_readback", "raw_sha256": "sha256:" + "d" * 64,
                  "position_quantity": 1}
        self.assertEqual(reconcile_four_way(capital, yuanli, oms, broker, as_of=NOW)["status"], "MATCHED")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "position_quantity": 0}, broker, as_of=NOW)["reason"], "POSITION_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "cash": "4799999.00"}, broker, as_of=NOW)["reason"], "CASH_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "order_ids": ["O-2"]}, broker, as_of=NOW)["reason"], "ORDER_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "available": "4499999"}, broker, as_of=NOW)["reason"], "AVAILABLE_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "frozen_margin": "10"}, broker, as_of=NOW)["reason"], "FROZEN_MARGIN_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, {**oms, "filled_quantity": 0}, broker, as_of=NOW)["reason"], "FILL_DELTA")
        self.assertEqual(reconcile_four_way(capital, yuanli, oms, {**broker, "raw_sha256": oms["raw_sha256"]}, as_of=NOW)["reason"], "CLONED_LEDGER_EVIDENCE")
        self.assertEqual(reconcile_four_way(capital, yuanli, {}, broker, as_of=NOW)["status"], "DRIFTED")


if __name__ == "__main__":
    unittest.main()
