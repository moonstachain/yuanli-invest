"""Actual call orchestration with offline host fixture; no production acceptance."""
import unittest
from yuanli_invest.gold_au_broker_facts import BrokerFactsReader, digest
from yuanli_invest.gold_paper import PaperDenied
from scripts.youquant_gold_simnow_strategy import _verified_added_ctp_binding
from tests.test_gold_au_broker_facts import HostExchange, NOW, INVESTOR, CONTRACT, attestation, binding, signed, verified


class NativeV3ProducerTests(unittest.TestCase):
    def setUp(self):
        self.host=HostExchange(); self.platform=binding()
        self.command=signed({"source":"independent_command_native_order_binding","environment":"SIMNOW_FIRST_NORMAL",
            "account_id":INVESTOR,"contract":CONTRACT,"observed_at":NOW.isoformat(),"command_id":"CMD-OPEN",
            "claim_id":"CLM-OPEN","action":"OPEN_LONG","quantity":1,"order_id":"platform-111",
            "platform_binding_sha256":self.platform["raw_sha256"]})
        self.reader=BrokerFactsReader(exchange=self.host,robot_id=479509,clock=lambda:NOW,
            account_attestation_reader=attestation,account_attestation_verifier=_verified_added_ctp_binding,
            independent_receipt_verifier=verified,order_binding_reader=lambda _:self.platform,
            command_order_binding_reader=lambda *_:self.command)
    def produce(self,action="OPEN_LONG"):
        return self.reader.native_order_evidence_v3(command_id="CMD-OPEN",claim_id="CLM-OPEN",contract=CONTRACT,action=action)
    def test_native_v3_conversion_reads_real_order_trade_position_account_calls(self):
        result=self.produce();f=result["facts"]
        self.assertEqual(f["filled_quantity"],1);self.assertEqual(f["position_quantity"],1)
        self.assertIsNone(f["reconciliation"]);self.assertEqual(result["facts_sha256"],digest(f))
        methods=[c[2] for c in self.host.calls if len(c)>2 and c[:2]==("IO","api")]
        self.assertEqual(methods,["ReqQryTradingAccount","ReqQryOrder","ReqQryTrade","ReqQryInvestorPosition"])
        self.assertFalse(any(c[0] in {"Buy","Sell","CancelOrder"} for c in self.host.calls))
    def test_missing_and_unsigned_command_mapping_are_denied(self):
        self.reader.command_binding_reader=None
        with self.assertRaisesRegex(PaperDenied,"BINDING_UNWIRED"):self.produce()
        self.reader.command_binding_reader=lambda *_:dict(self.command,claim_id="FORGED")
        with self.assertRaisesRegex(PaperDenied,"AUTHENTICITY"):self.produce()
    def test_wrong_claim_and_platform_binding_hash_cannot_select_nearby_order(self):
        for patch in ({"claim_id":"WRONG"},{"platform_binding_sha256":"sha256:"+"0"*64}):
            self.command=signed({**{k:v for k,v in self.command.items() if k not in {"signature","raw_sha256"}},**patch})
            with self.assertRaises(PaperDenied):self.produce()
    def test_signed_action_still_must_match_native_direction_offset(self):
        self.command=signed({**{k:v for k,v in self.command.items() if k not in {"signature","raw_sha256"}},"action":"CLOSE_LONG"})
        with self.assertRaisesRegex(PaperDenied,"NATIVE_ACTION"):self.produce("CLOSE_LONG")
    def test_two_pending_orders_cannot_be_v3_one_order_evidence(self):
        self.host.rows["ReqQryOrder"][0].update(OrderStatus="3",OrderSubmitStatus="3",VolumeTraded=0,VolumeTotal=1)
        self.host.rows["ReqQryTrade"]=[]
        self.host.pending=[{"Id":"platform-111","Amount":1,"DealAmount":0},{"Id":"other","Amount":1,"DealAmount":0}]
        with self.assertRaisesRegex(ValueError,"QUANTITY_OR_STATUS"):self.produce()

if __name__=="__main__":unittest.main()
