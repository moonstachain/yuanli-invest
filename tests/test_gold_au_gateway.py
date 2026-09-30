"""Synthetic offline gateway checks; no account, key, or market authority."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from copy import deepcopy
import unittest
from zoneinfo import ZoneInfo

from tests.test_gold_au_strategy import fixture
from yuanli_invest.gold_au_gateway import _deadlines, _digest, build_entry_ticket
from yuanli_invest.gold_au_strategy import DEFAULT_CONFIG
from yuanli_invest.gold_au_strategy import evaluate_signal, evaluate_current_snapshot_signal
from yuanli_invest.gold_paper import (
    COMMAND_FIELDS, PaperDenied, PaperGrant, PaperLedger, SIMNOW_FIRST,
    verify_command,
)


SHANGHAI = ZoneInfo("Asia/Shanghai")
KEY = b"offline-gateway-test-key-minimum-32-bytes"
HASH = "a" * 64


def _future_weekdays(after: date, count: int) -> list[str]:
    days = []
    day = after + timedelta(days=1)
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day.isoformat())
        day += timedelta(days=1)
    return days


def case(*, current_snapshot: bool = False) -> dict:
    dataset = fixture(300)
    last_bar = date.fromisoformat(max(bar["date"] for bar in dataset["bars"]))
    today = last_bar + timedelta(days=1)
    while today.weekday() >= 5:
        today += timedelta(days=1)
    dataset["exchange_sessions"].append(today.isoformat())
    if current_snapshot:
        dataset["purpose"] = "STRICT_0830_LIVE_SNAPSHOT_ONLY_NOT_HISTORICAL_BACKTEST"
        dataset["execution_cost_status"] = "WITNESSED"
        dataset["price_quality"]["status"] = "LIVE_SOURCE_CHECKED"
        decision = datetime.combine(today, datetime.min.time(), SHANGHAI).replace(hour=8, minute=30)
        signal = evaluate_current_snapshot_signal(dataset, as_of=decision)
    else:
        signal = evaluate_signal(dataset, today.isoformat(), pit_mode="strict", variant="full")
    contract = signal["contract"]
    now = datetime.combine(today, datetime.min.time(), SHANGHAI).replace(hour=9, minute=1)
    grant = PaperGrant(
        program_approval_ref="PROGRAM-GOLD2-PAPER-001", human_approval_ref="HUMAN-GOLD2-PAPER-001",
        account_id="SIMNOW-TEST-ACCOUNT", robot_id=12345,
        starts_at=(now - timedelta(days=1)).isoformat(),
        expires_at=(now + timedelta(days=60)).isoformat(), enabled=True,
    )
    provider = {
        "source": "provider_readback", "identity_verified": True,
        "environment": SIMNOW_FIRST, "account_id": grant.account_id, "robot_id": grant.robot_id,
        "connected": True, "reconciled": True, "observed_at": (now - timedelta(seconds=1)).isoformat(),
        "contract_meta": {
            "InstrumentID": contract, "ExchangeID": "SHFE", "VolumeMultiple": 1000,
            "PriceTick": 0.02, "DeliveryYear": 2000 + int(contract[2:4]),
            "DeliveryMonth": int(contract[4:6]), "IsTrading": 1,
        },
        "positions": [], "open_order_ids": [], "margin_for_one_lot": "200000",
        "margin_in_use": "0", "available": "4000000", "broker_equity": "5000000",
        "round_trip_fee_upper_cny": "40",
    }
    quote = {
        "source": "broker_quote_readback", "identity_verified": True, "connected": True,
        "environment": SIMNOW_FIRST, "account_id": grant.account_id, "robot_id": grant.robot_id,
        "exchange": "SHFE", "contract": contract,
        "observed_at": (now - timedelta(seconds=1)).isoformat(),
        "best_bid": "1079.98", "best_ask": "1080.00", "raw_sha256": HASH,
    }
    costs = {
        "source": "broker_fee_margin_readback", "identity_verified": True,
        "environment": SIMNOW_FIRST, "account_id": grant.account_id, "contract": contract,
        "observed_at": (now - timedelta(seconds=20)).isoformat(),
        "fee_open_per_lot_cny": "20", "fee_close_today_per_lot_cny": "20",
        "fee_close_yesterday_per_lot_cny": "20", "margin_for_one_lot_cny": "200000",
        "raw_sha256": HASH,
    }
    calendar = {
        "source": "SHFE_OFFICIAL_CALENDAR", "verified": True, "exchange": "SHFE",
        "source_ref": signal["exchange_calendar_ref"], "raw_sha256": HASH,
        "published_at": (now - timedelta(days=1)).isoformat(),
        "retrieved_at": (now - timedelta(days=1)).isoformat(),
        "sessions": dataset["exchange_sessions"] + _future_weekdays(today, 40),
    }
    sessions = calendar["sessions"]
    base = sessions.index(today.isoformat())
    registration = {
        "schema_version": "gold-au-signal-registration.v1",
        "source": "independent_append_only_registry_readback",
        "registry_kind": "EXTERNAL_APPEND_ONLY", "append_only_verified": True,
        "independent_readback_verified": True,
        "registry_id": "SYNTHETIC-INDEPENDENT-REGISTER",
        "record_id": "SYNTHETIC-0830-RECORD", "source_ref": "SYNTHETIC-TEST-ONLY",
        "raw_sha256": HASH, "registry_root_sha256": HASH,
        "recorded_at": now.replace(hour=8, minute=30, second=20).isoformat(),
        "read_back_at": (now - timedelta(seconds=1)).isoformat(),
        "decision_at": signal["as_of"], "signal_id": signal["signal_id"],
        "signal_sha256": _digest(signal), "frozen_dataset_sha256": _digest(dataset),
        "parameters_sha256": _digest(DEFAULT_CONFIG),
        "forward_decision_id": "FWD-GOLD2-SYNTHETIC-001",
        "forward_decision_sha256": HASH,
        "outcome_contracts": [
            {"horizon_trading_days": horizon, "session_date": sessions[base + horizon],
             "decision_id": "FWD-GOLD2-SYNTHETIC-001",
             "outcome_contract_id": f"OUT-GOLD2-SYNTHETIC-D{horizon}"}
            for horizon in (5, 20)
        ],
    }
    registration["raw_sha256"] = _digest({key: registration[key] for key in (
        "registry_id", "record_id", "source_ref", "recorded_at",
        "decision_at", "signal_id", "signal_sha256", "frozen_dataset_sha256",
        "parameters_sha256", "forward_decision_id", "forward_decision_sha256",
        "outcome_contracts")})
    sealed = deepcopy(registration)

    def verifier(receipt: dict) -> dict:
        # Fixture analogue of an external anchored inclusion verifier. It
        # refuses any changed record identity or timestamp, including a
        # rehashed backdate supplied by the gateway caller.
        if receipt != sealed:
            raise ValueError("independent registry inclusion failed")
        return {"status": "VERIFIED_APPEND_ONLY_INCLUSION",
                "registry_id": sealed["registry_id"], "record_id": sealed["record_id"],
                "record_sha256": sealed["raw_sha256"],
                "registry_root_sha256": sealed["registry_root_sha256"],
                "recorded_at": sealed["recorded_at"], "read_back_at": sealed["read_back_at"],
                "verifier_identity": "SYNTHETIC-INDEPENDENT-REGISTRY-VERIFY",
                "proof_sha256": HASH, "verified_at": now.isoformat()}
    ledger = PaperLedger()
    ledger.append("EquityMarked", "STRATEGY-EQUITY-TEST-001", (now - timedelta(seconds=1)).isoformat(), {
        "source": "independent_strategy_accounting", "reconciled": True,
        "environment": SIMNOW_FIRST, "account_id": grant.account_id,
        "allocation_scope": "DEDICATED_STRATEGY_PAPER_ACCOUNT",
        "observed_at": (now - timedelta(seconds=1)).isoformat(),
        "equity": "5000000", "broker_equity": "5000000", "raw_sha256": "sha256:" + HASH,
    })
    return {
        "signal": signal, "frozen_dataset": dataset,
        "signal_registration_readback": registration,
        "registration_verifier": verifier, "grant": grant,
        "provider_snapshot": provider, "quote_readback": quote,
        "fee_margin_readback": costs, "exchange_calendar": calendar,
        "ledger": ledger, "issued_signal_ids": frozenset(),
        "execution_intent_id": "EI-GOLD2-TEST-001",
        "capital_admission_id": "CA-GOLD2-TEST-001",
        "now": now, "signing_key": KEY,
    }


class GoldAuGatewayTests(unittest.TestCase):
    def assert_denied(self, code: str, args: dict) -> None:
        with self.assertRaises(PaperDenied) as error:
            build_entry_ticket(**args)
        self.assertEqual(error.exception.code, code)

    def test_current_snapshot_replays_through_all_unchanged_admission_gates(self):
        args = case(current_snapshot=True)
        ticket = build_entry_ticket(**args)
        self.assertEqual(ticket["status"], "PREPARED_NOT_SENT")
        self.assertFalse(ticket["transport_attempted"])
        self.assertEqual(ticket["prior_signal_registration"]["record_id"], args["signal_registration_readback"]["record_id"])
        self.assertFalse(verify_command(ticket["envelope"], KEY)["live_execution_authorized"])

    def test_current_research_deferred_cost_cannot_be_promoted_by_grade(self):
        args = case(current_snapshot=True)
        args["frozen_dataset"]["execution_cost_status"] = "DEFERRED_TO_EXECUTION_GATE"
        # Structural grade labels cannot override the explicit deferred policy.
        args["signal"] = evaluate_current_snapshot_signal(args["frozen_dataset"],
            as_of=datetime.fromisoformat(args["signal"]["as_of"]))
        self.assertFalse(args["signal"]["actionable_entry"])
        self.assertNotIn("planned_one_lot_loss_cny", args["signal"])
        self.assert_denied("GATEWAY_SIGNAL_NOT_ACTIONABLE", args)

    def test_current_snapshot_future_inputs_or_changed_metadata_are_rejected(self):
        args = case(current_snapshot=True)
        decision = datetime.fromisoformat(args["signal"]["as_of"])
        future = (decision + timedelta(seconds=1)).isoformat()
        args["frozen_dataset"]["bars"][0].update(retrieved_at=future, available_at=future)
        self.assert_denied("GATEWAY_SIGNAL_REPLAY_FAILED", args)
        args = case(current_snapshot=True)
        args["frozen_dataset"]["purpose"] = "FORGED_CURRENT_SCOPE"
        self.assert_denied("GATEWAY_SIGNAL_REPLAY_MISMATCH", args)
        args = case(current_snapshot=True)
        args["signal"]["price_information_set"] = "FORGED_HISTORICAL_CLAIM"
        self.assert_denied("GATEWAY_SIGNAL_REPLAY_MISMATCH", args)
        args = case(current_snapshot=True)
        args["signal"]["as_of"] = (datetime.fromisoformat(args["signal"]["as_of"])-timedelta(days=1)).isoformat()
        self.assert_denied("GATEWAY_DECISION_TIME_MISMATCH", args)

    def test_valid_offline_ticket_is_exact_signed_single_lot(self):
        args = case()
        ticket = build_entry_ticket(**args)
        self.assertEqual(ticket["status"], "PREPARED_NOT_SENT")
        self.assertFalse(ticket["transport_attempted"])
        body = verify_command(ticket["envelope"], KEY)
        self.assertEqual(set(body), COMMAND_FIELDS)
        self.assertEqual(body["action"], "OPEN_LONG")
        self.assertEqual(body["quantity"], 1)
        self.assertEqual(body["environment"], SIMNOW_FIRST)
        self.assertEqual(body["reason"], "ENTRY")
        self.assertEqual(body["reference_price"], "1080.00")
        self.assertEqual(body["limit_price"], "1080.10")
        self.assertEqual(body["stop_price"], "1076.10")
        self.assertFalse(body["live_execution_authorized"])
        self.assertFalse(body["real_capital_movement_authorized"])
        self.assertEqual(Decimal(ticket["planned_one_lot_loss_cny"]), Decimal("4040.00"))
        self.assertLessEqual(Decimal(ticket["planned_one_lot_loss_cny"]),
                             Decimal(ticket["allowed_one_lot_loss_cny"]))
        self.assertEqual(body["decision_at"], args["signal"]["as_of"])
        expected_expiry = datetime.combine(args["now"].date(), datetime.min.time(), SHANGHAI)
        expected_expiry = expected_expiry.replace(hour=9, minute=5).astimezone(timezone.utc)
        self.assertEqual(body["expires_at"], expected_expiry.isoformat())
        self.assertFalse(ticket["roll_before_max_hold"])

    def test_near_delivery_roll_deadline_is_last_session_of_eligible_month(self):
        day = date(2026, 5, 15)
        sessions = [day] + [date.fromisoformat(item) for item in _future_weekdays(day, 40)]
        exit_at, roll_at, roll_first = _deadlines(sessions, day, "au2607")
        self.assertTrue(roll_first)
        self.assertEqual(roll_at, "2026-05-29T15:00:00+08:00")
        self.assertGreater(datetime.fromisoformat(exit_at), datetime.fromisoformat(roll_at))

    def test_reconstructed_and_single_factor_signals_cannot_be_signed(self):
        args = case()
        today = args["now"].date().isoformat()
        args["signal"] = evaluate_signal(args["frozen_dataset"], today, pit_mode="reconstructed", variant="full")
        self.assert_denied("GATEWAY_NON_STRICT_SIGNAL", args)
        args = case()
        args["signal"] = evaluate_signal(args["frozen_dataset"], today, pit_mode="strict", variant="real_rate_only")
        self.assert_denied("GATEWAY_SIGNAL_REPLAY_MISMATCH", args)

    def test_missing_current_readbacks_calendar_and_repeat_fail_closed(self):
        args = case()
        args["quote_readback"]["observed_at"] = (args["now"] - timedelta(seconds=6)).isoformat()
        self.assert_denied("GATEWAY_STALE_QUOTE", args)
        args = case()
        args["fee_margin_readback"]["fee_open_per_lot_cny"] = None
        self.assert_denied("GATEWAY_INVALID_FEE_OPEN", args)
        args = case()
        args["fee_margin_readback"]["margin_for_one_lot_cny"] = "300000"
        self.assert_denied("GATEWAY_MARGIN_READBACK_MISMATCH", args)
        args = case()
        args["provider_snapshot"]["identity_verified"] = False
        self.assert_denied("GATEWAY_UNVERIFIED_ACCOUNT_OR_STATE", args)
        args = case()
        args["provider_snapshot"]["reconciled"] = False
        self.assert_denied("GATEWAY_UNVERIFIED_ACCOUNT_OR_STATE", args)
        args = case()
        args["exchange_calendar"]["sessions"] = []
        self.assert_denied("GATEWAY_INVALID_EXCHANGE_SESSIONS", args)
        args = case()
        args["issued_signal_ids"] = frozenset({args["signal"]["signal_id"]})
        self.assert_denied("GATEWAY_REPEAT_SIGNAL", args)

    def test_fee_risk_cap_and_grant_boundaries(self):
        args = case()
        args["fee_margin_readback"]["fee_open_per_lot_cny"] = "15000"
        args["provider_snapshot"]["round_trip_fee_upper_cny"] = "15020"
        self.assert_denied("GATEWAY_PLANNED_LOSS_LIMIT", args)
        args = case()
        args["quote_readback"]["best_ask"] = "1080.01"
        self.assert_denied("GATEWAY_OFF_TICK_BEST_ASK", args)
        args = case()
        args["grant"] = PaperGrant(**{**args["grant"].__dict__, "enabled": False})
        self.assert_denied("GATEWAY_PAPER_GRANT_DISABLED", args)
        args = case()
        args["now"] = args["now"].replace(hour=9, minute=5)
        self.assert_denied("GATEWAY_OUTSIDE_ENTRY_WINDOW", args)

    def test_signal_must_have_independently_read_back_0830_registration(self):
        args = case()
        args["signal_registration_readback"] = None
        self.assert_denied("GATEWAY_MISSING_INDEPENDENT_SIGNAL_REGISTRATION", args)
        args = case()
        args["signal_registration_readback"]["recorded_at"] = args["now"].isoformat()
        self.assert_denied("GATEWAY_LATE_SIGNAL_REGISTRATION", args)
        args = case()
        args["signal_registration_readback"]["signal_sha256"] = "sha256:" + "b" * 64
        self.assert_denied("GATEWAY_FROZEN_SIGNAL_REGISTRATION_MISMATCH", args)
        args = case()
        args["signal_registration_readback"]["frozen_dataset_sha256"] = "sha256:" + "b" * 64
        self.assert_denied("GATEWAY_FROZEN_SIGNAL_REGISTRATION_MISMATCH", args)
        args = case()
        args["signal_registration_readback"]["outcome_contracts"][1]["session_date"] = "2099-01-01"
        self.assert_denied("GATEWAY_PROSPECTIVE_OUTCOME_CONTRACT_MISMATCH", args)
        args = case()
        args["signal_registration_readback"]["read_back_at"] = (args["now"] - timedelta(minutes=1)).isoformat()
        self.assert_denied("GATEWAY_STALE_SIGNAL_REGISTRATION_READBACK", args)
        args = case()
        args["registration_verifier"] = None
        self.assert_denied("GATEWAY_MISSING_EXTERNAL_REGISTRATION_VERIFIER", args)
        args = case()
        args["signal_registration_readback"]["recorded_at"] = args["now"].replace(
            hour=8, minute=30, second=10).isoformat()
        keys = ("registry_id", "record_id", "source_ref", "recorded_at",
                "decision_at", "signal_id", "signal_sha256", "frozen_dataset_sha256",
                "parameters_sha256", "forward_decision_id", "forward_decision_sha256",
                "outcome_contracts")
        args["signal_registration_readback"]["raw_sha256"] = _digest({
            key: args["signal_registration_readback"][key] for key in keys})
        self.assert_denied("GATEWAY_REGISTRATION_INCLUSION_NOT_VERIFIED", args)

    def test_official_calendar_and_pre_registration_inputs_cannot_be_rewritten(self):
        args = case()
        gap = args["frozen_dataset"]["exchange_sessions"][10]
        args["frozen_dataset"]["exchange_sessions"].remove(gap)
        args["frozen_dataset"]["bars"] = [row for row in args["frozen_dataset"]["bars"]
                                               if row["date"] != gap]
        args["signal"] = evaluate_signal(args["frozen_dataset"], args["now"].date().isoformat(),
                                         pit_mode="strict")
        self.assertTrue(args["signal"]["actionable_entry"])
        self.assert_denied("GATEWAY_DATASET_CALENDAR_MISMATCH", args)
        args = case()
        first = args["frozen_dataset"]["bars"][0]
        first["retrieved_at"] = first["available_at"] = args["now"].replace(
            hour=8, minute=30, second=30).isoformat()
        args["signal"] = evaluate_signal(args["frozen_dataset"], args["now"].date().isoformat(),
                                         pit_mode="strict")
        self.assertTrue(args["signal"]["actionable_entry"])
        self.assert_denied("GATEWAY_POSTREGISTRATION_DATA_IN_FROZEN_DATASET", args)

    def test_fresh_independent_strategy_equity_mark_and_drawdown_required(self):
        args = case()
        args["ledger"] = PaperLedger()
        self.assert_denied("STRATEGY_EQUITY_MARK_MISSING", args)
        args = case()
        args["provider_snapshot"]["broker_equity"] = "4700000"
        args["ledger"].append("EquityMarked", "STRATEGY-EQUITY-TEST-002",
                              args["now"].isoformat(), {
            "source": "independent_strategy_accounting", "reconciled": True,
            "environment": SIMNOW_FIRST, "account_id": args["grant"].account_id,
            "allocation_scope": "DEDICATED_STRATEGY_PAPER_ACCOUNT",
            "observed_at": args["now"].isoformat(), "equity": "4700000",
            "broker_equity": "4700000", "raw_sha256": "sha256:" + HASH,
        })
        self.assert_denied("GATEWAY_DRAWDOWN_STOP", args)


if __name__ == "__main__":
    unittest.main()
