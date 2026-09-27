"""Synthetic evidence tests; no network/account access."""
from datetime import datetime, time, timedelta
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.gold_au_research_diagnostic import accept_natural_morning, capture_current
from tests.test_gold_au_live_snapshot import fixture, TZ
from yuanli_invest.gold_au_research_diagnostic import observe_public_evidence
from yuanli_invest.gold_au_decision_log import LocalDecisionLog


def research_fixture(root):
    request, day, paths = fixture(root)
    research = {k:v for k,v in request.items() if k != 'cost_receipt_path'}
    research['schema_version'] = 'gold-au-research-observation-request.v1'
    return research, day, paths, request


class ResearchObservationTests(unittest.TestCase):
    def test_current_observation_never_emits_trading_contract(self):
        with TemporaryDirectory() as temporary:
            request, day, _, _ = research_fixture(Path(temporary))
            result = observe_public_evidence(request, as_of=datetime.combine(day, time(12), TZ))
            self.assertEqual(result['status'], 'READY_RESEARCH_OBSERVATION', result)
            self.assertEqual(result['price_observation']['official_prior_sessions'],273)
            self.assertFalse(result['decision_frozen'])
            self.assertFalse(result['actionable_entry'])
            self.assertFalse(result['broker_action_authorized'])
            self.assertEqual(result['risk_policy_observation']['wgc_multiplier'],0.5)
            self.assertEqual(result['risk_policy_observation']['indicative_frozen_policy_budget_cny'],12500)
            self.assertNotIn('signal', result)
            self.assertNotIn('signal_id', result)
            self.assertNotIn('decision_at', result)

    def test_current_known_history_does_not_backdate_original_captures(self):
        with TemporaryDirectory() as temporary:
            request, day, paths, _ = research_fixture(Path(temporary))
            manifest=json.loads(paths['shfe'].read_text())
            for row in manifest['reports']:
                row['captured_at']=datetime.combine(day,time(8,15),TZ).isoformat()
            paths['shfe'].write_text(json.dumps(manifest))
            result=observe_public_evidence(request,as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['status'],'READY_RESEARCH_OBSERVATION',result)
            self.assertFalse(result['price_observation']['intermediate_price_points_are_historical_signals'])
            self.assertTrue(all(datetime.fromisoformat(r['available_at'])==datetime.combine(day,time(8,15),TZ) for r in result['public_dataset']['bars']))
            self.assertIsNotNone(result['price_observation']['atr20_cny_per_gram'])

    def test_future_capture_is_rejected_at_actual_time(self):
        with TemporaryDirectory() as temporary:
            request, day, _, _=research_fixture(Path(temporary))
            result=observe_public_evidence(request,as_of=datetime.combine(day,time(8,19),TZ))
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(result['reason'],'SOURCE_NOT_YET_AVAILABLE_AT_ASSEMBLY')

    def test_raw_tamper_and_identity_mismatch_fail_closed(self):
        with TemporaryDirectory() as temporary:
            request, day, paths, _=research_fixture(Path(temporary))
            manifest=json.loads(paths['fred'].read_text())
            Path(manifest['captures'][0]['raw_file']).write_text('altered')
            result=observe_public_evidence(request,as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['reason'],'RAW_HASH_MISMATCH_FRED')
        with TemporaryDirectory() as temporary:
            request, day, paths, _=research_fixture(Path(temporary))
            mapping=json.loads(paths['mapping'].read_text());mapping['strategy_series']='WRONG'
            paths['mapping'].write_text(json.dumps(mapping))
            result=observe_public_evidence(request,as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['reason'],'H10_LIVE_MAPPING_NOT_WITNESSED')

    def test_trade_contract_or_cost_cannot_be_injected(self):
        with TemporaryDirectory() as temporary:
            request, day, _, live=research_fixture(Path(temporary))
            request['cost_receipt_path']=live['cost_receipt_path']
            result=observe_public_evidence(request,as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['reason'],'TRADING_CONTRACT_FIELDS_FORBIDDEN_IN_RESEARCH_OBSERVATION')

    def test_observation_source_change_detected(self):
        with TemporaryDirectory() as temporary:
            request, day, paths, _=research_fixture(Path(temporary))
            from yuanli_invest import gold_au_research_diagnostic as module
            original=module.macro_gate
            def mutate(*args,**kwargs):
                outcome=original(*args,**kwargs)
                paths['mapping'].write_text(paths['mapping'].read_text()+'\n')
                return outcome
            with patch.object(module,'macro_gate',side_effect=mutate):
                result=observe_public_evidence(request,as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['reason'],'SOURCE_CHANGED_DURING_RESEARCH_OBSERVATION')


class NaturalAcceptanceTests(unittest.TestCase):
    def test_future_pending_and_missed_morning_never_create_log(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary);os.chmod(root,0o700)
            before=accept_natural_morning(root,decision_date='2026-09-28',as_of=datetime.fromisoformat('2026-09-26T12:00:00+08:00'))
            self.assertEqual(before['status'],'PENDING')
            after=accept_natural_morning(root,decision_date='2026-09-28',as_of=datetime.fromisoformat('2026-09-28T08:32:00+08:00'))
            self.assertEqual(after['status'],'MISSING_NATURAL_DECISION')
            self.assertEqual(list(root.iterdir()),[])
            self.assertFalse(after['replay_performed'])

    def test_failed_public_capture_stays_in_diagnostic_namespace(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); os.chmod(root,0o700)
            request, day, paths, live = research_fixture(root)
            (root/'daily_request_sources.json').write_text(json.dumps({
                'schema_version':'gold-au-daily-request-sources.v1', 'execution_mode':'RESEARCH_ONLY',
                'calendar_receipt_path':live['calendar_receipt_path'],
                'h10_mapping_receipt_path':live['h10_mapping_receipt_path']}))
            (root/'shfe_archive_sources.json').write_text(json.dumps({'seed_manifest_paths':live['shfe_manifest_paths']}))
            calls=[]
            def fake_macro(**kwargs):
                calls.append(('macro',kwargs['end_inclusive'].isoformat()))
                kwargs['output_dir'].mkdir()
                (kwargs['output_dir']/'manifest.json').write_text('{}')
                return {'status':'PARTIAL_FAILURE'}
            def failed_shfe(day):
                calls.append(('shfe',day));raise TimeoutError('synthetic timeout')
            result=capture_current(root,clock=lambda:datetime.combine(day,time(12),TZ),macro_capture=fake_macro,shfe_fetch=failed_shfe)
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(calls,[('macro','2026-09-28'),('shfe','2026-09-24')])
            self.assertTrue((Path(result['output_dir'])/'report.json').is_file())
            self.assertFalse((root/'requests').exists())
            self.assertFalse((root/'macro_captures').exists())
            self.assertFalse((root/'shfe_archives').exists())
            self.assertFalse((root/'gold_au_decisions.sqlite').exists())
            self.assertFalse(result['formal_daily_artifacts_written'])

    def test_natural_record_readback_is_verified_without_mutation(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary);os.chmod(root,0o700)
            request,day,_=fixture(root)
            log=LocalDecisionLog(root/'gold_au_decisions.sqlite',clock=lambda:datetime.combine(day,time(8,30),TZ))
            log.capture(request)
            before=(root/'gold_au_decisions.sqlite').read_bytes()
            early=accept_natural_morning(root,decision_date=day.isoformat(),as_of=datetime.combine(day,time(8,29),TZ))
            self.assertEqual(early['status'],'INVALID_DECISION_LOG')
            self.assertEqual(early['reason'],'RECORD_NOT_YET_AVAILABLE_AT_ACCEPTANCE')
            result=accept_natural_morning(root,decision_date=day.isoformat(),as_of=datetime.combine(day,time(12),TZ))
            self.assertEqual(result['status'],'ACCEPTED_RESEARCH_FREEZE',result)
            self.assertEqual((root/'gold_au_decisions.sqlite').read_bytes(),before)
            self.assertEqual(result['chain_record_count'],1)
            self.assertFalse(result['broker_action_authorized'])

if __name__=='__main__':unittest.main()
