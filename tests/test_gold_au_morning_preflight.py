"""No scheduled worker, broker or public network is exercised by preflight."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import gold_au_morning_preflight as p

NOW=datetime(2026,9,26,13,20,tzinfo=timezone.utc)


class MorningPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.base=Path(self.tmp.name)
        self.repo=self.base/'repo'; self.runtime=self.base/'runtime'; self.launch=self.base/'launch'
        for d in (self.repo,self.runtime,self.launch):d.mkdir(mode=0o700)
        (self.repo/'.venv/bin').mkdir(parents=True);(self.repo/'scripts').mkdir()
        (self.repo/'.venv/bin/python').write_text('offline fixture')
        for label,(hour,minute,script) in p.EXPECTED.items():
            (self.repo/'scripts'/script).write_text('# fixture worker, never run')
            plist={'Label':label,'RunAtLoad':False,'WorkingDirectory':str(self.repo),
                   'ProgramArguments':[str(self.repo/'.venv/bin/python'),str(self.repo/'scripts'/script),'--runtime-dir',str(self.runtime),'--execute'],
                   'StartCalendarInterval':[{'Weekday':i,'Hour':hour,'Minute':minute} for i in range(1,6)]}
            (self.launch/(label+'.plist')).write_bytes(plistlib.dumps(plist))
        (self.repo/'scripts/youquant_gold_simnow_readonly_cost_probe.py').write_text('# no broker')
        self.probe_sha='sha256:'+hashlib.sha256((self.repo/'scripts/youquant_gold_simnow_readonly_cost_probe.py').read_bytes()).hexdigest()
        self.calendar=self.base/'calendar.json';self.calendar.write_text('{}')
        self.mapping=self.runtime/'mapping.json';self.mapping.write_text('{}')
        (self.runtime/'daily_request_sources.json').write_text(json.dumps({'execution_mode':'RESEARCH_ONLY','calendar_receipt_path':str(self.calendar),'h10_mapping_receipt_path':'mapping.json'}))
        (self.runtime/'shfe_archive_sources.json').write_text(json.dumps({'calendar_receipt_path':str(self.calendar),'seed_manifest_paths':['seed.json']}))
        self.automation=self.base/'automation.toml'
        self.prompt='--accept-day 2026-09-28 2026-09-28北京时间09:15–09:20 09:18:20 不把09:15成本回填08:30 保持正式交易权限DENY 外部90秒watchdog 禁止下单、撤单 失败不得清除标记或重试 未变化保持安静 '+self.probe_sha[7:]
        self.save_automation()
        self.loaded=True
        self.prepare_calls=[]

    def tearDown(self):self.tmp.cleanup()

    def save_automation(self,updated=0):
        self.automation.write_text('id="gold2-au-simnow"\nstatus="ACTIVE"\nkind="heartbeat"\nname="fixture"\nrrule="FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=15"\nupdated_at='+str(updated)+'\nprompt='+json.dumps(self.prompt,ensure_ascii=False)+'\n')

    def collect(self):
        def proposal(**kwargs):
            self.prepare_calls.append(kwargs)
            return {'retained_reports':273,'requested_days':273,'missing_official_sessions':[],
                    'interval':['2025-08-13','2026-09-24'],'source_manifests':[]}
        natural={'status':'PENDING','checked_at':NOW.isoformat(),'inputs':{k:{'status':'MISSING_OR_INVALID'} for k in ('shfe_archive','macro_capture','account_cost_margin','assembled_request')}}
        with patch.object(p,'load_calendar_receipt',return_value={'raw_sha256':'a'*64}),\
             patch.object(p,'session_window',return_value={'decision_date':'2026-09-28','prior_session':'2026-09-24','prior_sessions':[]}),\
             patch.object(p,'prepare_archive',side_effect=proposal),\
             patch.object(p,'_mapping',return_value=({'witnessed_at':NOW.isoformat()},'b'*64)),\
             patch.object(p,'accept_natural_morning',return_value=natural):
            return p.collect_preflight(self.runtime,decision_day='2026-09-28',as_of=NOW,launch_dir=self.launch,
                automation_path=self.automation,repo=self.repo,
                task_observer=lambda _: {'installation':'LOADED' if self.loaded else 'UNKNOWN','runs':0},
                version_reader=lambda _: {'status':'VERIFIED_LOCAL_PYTHON312'},
                power_reader=lambda: {'current_prevent_idle_sleep_assertion':True,'assertion_survives_until_monday':'UNKNOWN'})

    def test_future_static_readiness_never_promotes_natural_acceptance(self):
        r=self.collect()
        self.assertTrue(r['static_prerequisites_verified']);self.assertEqual(r['natural_acceptance']['status'],'PENDING')
        self.assertFalse(r['broker_action_authorized']);self.assertEqual(r['actual_acceptance_pass_count'],0)
        self.assertFalse(r['scheduled_workers_started']);self.assertEqual(r['network_requests'],0)
        self.assertEqual(r['natural_acceptance']['inputs']['macro_capture']['preflight_interpretation'],'EXPECTED_NOT_RUN_BEFORE_TARGET_DAY')
        self.assertEqual(r['natural_acceptance']['inputs']['account_cost_margin']['dependency_role'],'EXECUTION_ONLY_NOT_RESEARCH_INPUT')
        self.assertFalse(self.prepare_calls[0]['execute']);self.assertFalse(self.prepare_calls[0]['fetch_missing'])
        self.assertEqual(self.prepare_calls[0]['observed_at'],NOW)

    def test_unknown_launchd_or_wrong_repository_cannot_be_ready(self):
        self.loaded=False;self.assertFalse(self.collect()['static_prerequisites_verified'])
        self.loaded=True
        name=next(iter(p.EXPECTED));file=self.launch/(name+'.plist')
        plist=plistlib.loads(file.read_bytes());plist['WorkingDirectory']='/unreviewed/repo'
        file.write_bytes(plistlib.dumps(plist))
        self.assertFalse(self.collect()['static_prerequisites_verified'])

    def test_future_updated_automation_or_wrong_probe_hash_rejected(self):
        self.save_automation(int(NOW.timestamp()*1000)+1)
        self.assertEqual(p.inspect_automation(self.automation,as_of=NOW,probe_sha256=self.probe_sha)['status'],'UNKNOWN')
        self.save_automation()
        self.assertEqual(p.inspect_automation(self.automation,as_of=NOW,probe_sha256='sha256:'+'c'*64)['status'],'CONFIG_MISMATCH')

    def test_python_probe_isolated_and_bad_output_is_unknown(self):
        calls=[]
        def runner(args,**kwargs):
            calls.append(args);return SimpleNamespace(returncode=0,stdout='[3,12,14]')
        self.assertEqual(p.python_version(Path('/python'),runner)['status'],'VERIFIED_LOCAL_PYTHON312')
        self.assertEqual(calls[0][1],'-I')
        self.assertEqual(p.python_version(Path('/python'),lambda *a,**k:SimpleNamespace(returncode=0,stdout='[true,12,14]'))['status'],'UNKNOWN')

    def test_existing_sleep_assertion_not_promoted_to_future_awake(self):
        def runner(args,**kwargs):
            return SimpleNamespace(returncode=0,stdout='AC Power:\n sleep 1\n' if args[-1]=='custom' else 'PreventUserIdleSystemSleep 1\n')
        result=p.inspect_power(runner)
        self.assertTrue(result['current_prevent_idle_sleep_assertion'])
        self.assertEqual(result['assertion_survives_until_monday'],'UNKNOWN');self.assertFalse(result['changed'])

    def test_private_new_report_hashes_and_no_overwrite(self):
        r=self.collect();out=self.base/'out'
        p.write_report(out,r)
        manifest=json.loads((out/'manifest.json').read_bytes())
        for name,sha in manifest['files'].items():
            self.assertEqual(sha,'sha256:'+hashlib.sha256((out/name).read_bytes()).hexdigest())
            self.assertEqual((out/name).stat().st_mode&0o777,0o600)
        self.assertEqual(out.stat().st_mode&0o777,0o700)
        with self.assertRaises(ValueError):p.write_report(out,r)
        self.assertIn('07:55–09:20',(out/'周一晨间就绪清单.md').read_text())

if __name__=='__main__':unittest.main()
