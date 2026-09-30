"""The supported production assembly: one Python 3.12+ cloud OMS process.

Missing adapters/receipts remain explicit failures. This module grants no paper
authority, creates no keys, purchases nothing, and never starts at import time.
Local research and the independently authenticated broker evidence reader are
separate trust boundaries, not alternate order hosts.
"""
from __future__ import annotations

from datetime import datetime, timezone
import sys
from typing import Any, Callable, Mapping

from scripts.youquant_gold_simnow_strategy import GoldSimNowRuntime, YouQuantBridge
from yuanli_invest.gold_au_account_coordinator import AccountCoordinator
from yuanli_invest.gold_au_broker_facts import BrokerFactsReader
from yuanli_invest.gold_au_receipt_client import ReceiptClient
from yuanli_invest.gold_au_strategy_accounting import SCOPE, KINDS, replay
from yuanli_invest.gold_paper import PaperDenied, PaperGrant, SIMNOW_FIRST
from decimal import Decimal


class ProductionGoldSimNowRuntime(GoldSimNowRuntime):
    """Canonical production type; legacy low-level runtimes cannot enter main."""
    def __init__(self, bridge, grant, signing_key, *, clock):
        super().__init__(bridge, grant, signing_key, clock=clock)
        self.production_entry_block_reason = "LINKED_PROTECTIVE_EXIT_REAL_ACCEPTANCE_REQUIRED"


def build_runtime(*, exchange: Any, get_command: Callable, kv_get: Callable, kv_set: Callable,
                  robot_id_get: Callable, facts: BrokerFactsReader, receipt_client: ReceiptClient,
                  independent_broker_evidence_reader: Callable[..., Mapping], grant: PaperGrant,
                  signing_key: bytes, pd_long_today: int, pd_long_yesterday: int,
                  clock: Callable[[], datetime] | None = None) -> GoldSimNowRuntime:
    if sys.version_info < (3, 12):
        raise PaperDenied("PYTHON_VERSION_UNSUPPORTED")
    if not isinstance(facts, BrokerFactsReader) or not isinstance(receipt_client, ReceiptClient):
        raise PaperDenied("UNSUPPORTED_PRODUCTION_ADAPTER")
    if (receipt_client.role != "runtime" or receipt_client.account_id != grant.account_id
            or receipt_client.robot_id != grant.robot_id or facts.robot_id != grant.robot_id
            or grant.environment != SIMNOW_FIRST or grant.strategy_initial_equity != "5000000"
            or grant.max_risk_fraction != "0.005" or grant.max_drawdown_fraction != "0.05"
            or grant.max_margin_fraction != "0.30" or not isinstance(signing_key, bytes) or len(signing_key) < 32):
        raise PaperDenied("PRODUCTION_BINDING_OR_FROZEN_LIMIT_MISMATCH")
    try:
        slippage = Decimal(grant.max_slippage_bps)
    except Exception:
        raise PaperDenied("PRODUCTION_SLIPPAGE_SCOPE_MISMATCH") from None
    if not slippage.is_finite() or not Decimal(0) <= slippage <= Decimal("20"):
        raise PaperDenied("PRODUCTION_SLIPPAGE_SCOPE_MISMATCH")
    if facts.exchange is not exchange:
        raise PaperDenied("PRODUCTION_EXCHANGE_BINDING_MISMATCH")
    if not all(callable(f) for f in (get_command, kv_get, kv_set, robot_id_get)):
        raise PaperDenied("PRODUCTION_HOST_CALLBACK_MISSING")
    # Official YouQuant position-direction enums: PD_LONG=0, PD_LONG_YD=2.
    if type(pd_long_today) is not int or type(pd_long_yesterday) is not int or (pd_long_today, pd_long_yesterday) != (0, 2):
        raise PaperDenied("POSITION_CONSTANTS_UNVERIFIED")
    clock = clock or (lambda: datetime.now(timezone.utc))
    coordinator = AccountCoordinator(receipt_client, independent_broker_evidence_reader,
                                     persist=lambda ledger: bridge.save_ledger(ledger))
    callbacks = facts.callbacks()
    callbacks["terminal_truth"] = facts.terminal_truth_with_four_way
    bridge = YouQuantBridge(exchange=exchange, get_command=get_command, kv_get=kv_get, kv_set=kv_set,
        robot_id_get=robot_id_get, ledger_anchor=receipt_client.append_ledger,
        atomic_claim=None, account_coordinator=coordinator, receipt_validation_clock=clock,
        required_equity_scope=SCOPE,
        pd_long_today=pd_long_today, pd_long_yesterday=pd_long_yesterday, **callbacks)
    # Startup is read only. Fresh installs need a real flat-account allocation
    # and externally anchored ledger before they can become an order runtime.
    ledger = bridge.load_ledger()
    if not ledger.events:
        raise PaperDenied("PRODUCTION_ALLOCATION_NOT_INITIALIZED")
    allocation = replay([e for e in ledger.events if e["kind"] in KINDS])["allocation"]
    if (allocation["account_id"] != grant.account_id or allocation["approval_ref"] != grant.human_approval_ref):
        raise PaperDenied("PRODUCTION_ALLOCATION_APPROVAL_MISMATCH")
    restart = coordinator.verify_restart(ledger, require_idle=False)
    attestation = facts.account_attestation()
    if attestation.get("account_id") != grant.account_id or robot_id_get() != grant.robot_id:
        raise PaperDenied("PRODUCTION_OBSERVED_ACCOUNT_MISMATCH")
    runtime = ProductionGoldSimNowRuntime(bridge, grant, signing_key, clock=clock)
    runtime.recovery_readonly = restart["status"] == "RESTART_VERIFIED_READONLY_RECOVERY"
    # Do not admit a new held lot until the linked protective-close protocol
    # for a native-confirmed fill / unavailable four-way settlement is built
    # and independently accepted. This is a source gate, not an operator flag.
    return runtime
