"""Separately admitted one-shot SimNow engineering runtime; never formal ENTRY.

No import-time I/O, credentials, account allocation or order authority. The
factory reuses all production identity/accounting/isolation checks but retains
the production OPEN gate. A separately signed control receipt binds one exact
engineering ActionContract. Broker facts and the coordinator remain mandatory.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import sys
from typing import Mapping, Callable, Any

from scripts.gold_au_runtime_bootstrap import build_runtime
from scripts.youquant_gold_simnow_strategy import GoldSimNowRuntime, run_once
from yuanli_invest.gold_paper import PaperDenied, verify_command, _time, SHANGHAI
from yuanli_invest.gold_au_receipt_client import object_hash


def validate_engineering_body(body: Mapping[str, Any], *, fee_upper: Any,
                              strategy_budget: Any) -> None:
    """R2 bounds augment, and never replace, ordinary paper admission checks."""
    if (body.get("action") != "OPEN_LONG" or body.get("reason") != "ENGINEERING_TEST"
            or type(body.get("quantity")) is not int or body["quantity"] != 1):
        raise PaperDenied("ENGINEERING_EXACT_OPEN_REQUIRED")
    try:
        price, stop = Decimal(body["limit_price"]), Decimal(body["stop_price"])
        reference = Decimal(body["reference_price"])
        fee, budget = Decimal(str(fee_upper)), Decimal(str(strategy_budget))
        if not all(x.is_finite() for x in (price, stop, reference, fee, budget)):
            raise ValueError
        distance = price - stop
        if (not Decimal("0") < distance <= Decimal("4") or fee < 0 or budget <= 0
                or abs(price-reference) > Decimal("0.10")
                or distance*1000 + Decimal("200") + fee > min(Decimal("5000"), budget)):
            raise ValueError
        decision = _time(body["decision_at"], "engineering_decision")
        deadline = _time(body["exit_not_after_at"], "engineering_deadline")
        roll = _time(body["roll_not_after_at"], "engineering_roll")
        if (not 0 < (deadline-decision).total_seconds() <= 120 or roll > deadline
                or deadline.astimezone(SHANGHAI).date() != decision.astimezone(SHANGHAI).date()
                or _time(body["expires_at"], "engineering_expiry") > deadline):
            raise ValueError
    except (ValueError, TypeError, KeyError, ArithmeticError):
        raise PaperDenied("ENGINEERING_R2_LIMIT_DENIED") from None


def verified_preparation(receipt: Mapping[str, Any], verifier: Callable, body: Mapping,
                         now: datetime) -> dict:
    if not isinstance(receipt, Mapping) or not callable(verifier):
        raise PaperDenied("ENGINEERING_PREPARATION_REQUIRED")
    value = deepcopy(dict(receipt))
    material = {k:v for k,v in value.items() if k not in {"signature", "raw_sha256"}}
    proof = verifier(value)
    if (value.get("source") != "independent_gold2_engineering_preparation_v4"
            or value.get("status") != "ENGINEERING_PREPARED"
            or value.get("raw_sha256") != object_hash(material)
            or not isinstance(proof, Mapping)
            or proof.get("status") != "SIGNATURE_VERIFIED_WITH_PINNED_KEY"
            or proof.get("verified_receipt_sha256") != value["raw_sha256"]
            or proof.get("verified_signer_id") != "GOLD2_INDEPENDENT_CONTROL_V4"
            or proof.get("verified_signer_key_fingerprint") != value.get("signer_key_fingerprint")
            or value.get("command_id") != body.get("command_id")
            or value.get("contract_hash") != body.get("contract_hash")
            or value.get("account_id") != body.get("account_id")
            or value.get("robot_id") != body.get("robot_id")
            or value.get("environment") != body.get("environment")
            or value.get("instrument") != body.get("contract")
            or value.get("exit_on_first_verified_fill") is not True
            or value.get("counts_as_strategy_return_sample") is not False
            or value.get("starts_formal_30_day_clock") is not False):
        raise PaperDenied("ENGINEERING_PREPARATION_BINDING_DENIED")
    if not 0 <= (now - _time(value.get("observed_at"), "preparation_at")).total_seconds() <= 15:
        raise PaperDenied("ENGINEERING_PREPARATION_STALE")
    validate_engineering_body(body, fee_upper=value.get("round_trip_fee_upper_cny"),
                              strategy_budget=value.get("strategy_budget_cny"))
    return value


class EngineeringGoldSimNowRuntime(GoldSimNowRuntime):
    def __init__(self, bridge, grant, signing_key, *, body, preparation, clock):
        super().__init__(bridge, grant, signing_key, clock=clock)
        self.engineering_body = deepcopy(dict(body))
        self.preparation = deepcopy(dict(preparation))

    def validate_open_evidence(self, body, now):
        # Engineering has no investment thesis/trend dependency. Its independent
        # preparation and native flat/cost/session facts are checked instead.
        if body != self.engineering_body:
            raise PaperDenied("ENGINEERING_CONTRACT_MISMATCH")
        if now > _time(body["expires_at"], "engineering_expiry"):
            raise PaperDenied("ENGINEERING_CASE_EXPIRED")
        provider = self.bridge.snapshot(body["contract"], now)
        self.validate_additional_open_risk(body, provider, now)

    def validate_additional_open_risk(self, body, provider, now):
        validate_engineering_body(body, fee_upper=provider.get("round_trip_fee_upper_cny"),
                                  strategy_budget=self.preparation["strategy_budget_cny"])
        quote = self.bridge.quote(body["contract"], now)
        last = Decimal(str(quote["last"]))
        if (abs(Decimal(body["reference_price"])-last) > Decimal("0.10")
                or abs(Decimal(body["limit_price"])-last) > Decimal("0.10")):
            raise PaperDenied("ENGINEERING_FRESH_QUOTE_PRICE_DRIFT")

    def process_command(self, envelope, now=None):
        body = verify_command(envelope, self.signing_key)
        # Explicit close commands are not an alternative authorizing path.
        # Only the existing linked contingent close may reduce this exact lot.
        if body != self.engineering_body:
            raise PaperDenied("ENGINEERING_CONTRACT_MISMATCH")
        return super().process_command(envelope, now)

    def current_position_context(self):
        context = super().current_position_context()
        if context is not None:
            if context.get("origin_command_id") != self.engineering_body["command_id"]:
                raise PaperDenied("ENGINEERING_FOREIGN_POSITION")
            # The frozen engineering policy authorizes immediate reduction
            # after a verified fill, including a provisional broker-only fill.
            context["exit_not_after_at"] = min(
                _time(context["exit_not_after_at"], "engineering_deadline"), self.clock()).isoformat()
        return context

    def process_due_safety_exit(self, now=None):
        ledger = self.bridge.load_ledger()
        attempted_close = any(e["kind"] == "OrderSubmitAttempted"
            and e["data"].get("action") == "CLOSE_LONG" for e in ledger.events)
        if attempted_close:
            return {"status": "ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY"}
        return super().process_due_safety_exit(now)


def build_engineering_runtime(*, engineering_envelope, preparation_receipt,
                              preparation_verifier, **production_args):
    if sys.version_info < (3, 12):
        raise PaperDenied("PYTHON_VERSION_UNSUPPORTED")
    body = verify_command(engineering_envelope, production_args["signing_key"])
    clock = production_args.get("clock") or (lambda: datetime.now(timezone.utc))
    grant = production_args["grant"]
    if grant.engineering_test_command_id != body["command_id"]:
        raise PaperDenied("ENGINEERING_TEST_NOT_EXACTLY_GRANTED")
    preparation = verified_preparation(preparation_receipt, preparation_verifier, body, clock())
    production = build_runtime(**production_args)
    # No mutation to ProductionGoldSimNowRuntime or its permanent entry gate.
    runtime = EngineeringGoldSimNowRuntime(production.bridge, grant, production_args["signing_key"],
        body=body, preparation=preparation, clock=clock)
    runtime.recovery_readonly = production.recovery_readonly
    return runtime


def serve_engineering(runtime, sleep, log):
    if sys.version_info < (3, 12):
        raise PaperDenied("PYTHON_VERSION_UNSUPPORTED")
    if type(runtime) is not EngineeringGoldSimNowRuntime or not callable(sleep) or not callable(log):
        raise PaperDenied("ENGINEERING_FACTORY_REQUIRED")
    while True:
        if (runtime.clock() > _time(runtime.engineering_body["expires_at"], "engineering_expiry")
                and not any(e["kind"] == "OrderSubmitAttempted" for e in runtime.bridge.load_ledger().events)):
            log("GOLD2_ENGINEERING_ONLY", "ENGINEERING_CASE_EXPIRED_NO_SUBMIT")
            return
        result = run_once(runtime)
        log("GOLD2_ENGINEERING_ONLY", result["status"])
        if result["status"] in {"NO_ACTIVE_POSITION", "NO_COMMAND"}:
            ledger = runtime.bridge.load_ledger()
            if any(e["kind"] == "OrderSubmitAttempted" for e in ledger.events):
                return
        if result["status"] in {"ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY",
            "LINKED_PAIR_RECONCILED_ACCOUNT_FROZEN"} or "MANUAL" in result["status"] or "UNCERTAIN" in result["status"]:
            return
        sleep(1000)


def main():
    runtime = globals().get("GOLD2_ENGINEERING_RUNTIME")
    serve_engineering(runtime, globals().get("Sleep"), globals().get("Log"))
