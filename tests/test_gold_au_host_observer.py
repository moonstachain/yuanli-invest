from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import gold_au_host_observer as o


class HostObserverTests(unittest.TestCase):
    def test_current_projection_only_known_fields(self):
        import plistlib
        from types import SimpleNamespace
        import os
        def runner(args, **kwargs):
            if args[0].endswith('pmset'):
                raw=b"Now drawing from 'AC Power'"
            elif args[-1]=='AppleClamshellState':
                raw=plistlib.dumps([{'AppleClamshellState': False}])
            elif args[-1]=='IOConsoleUsers':
                raw=plistlib.dumps([{'IOConsoleUsers':[{'kCGSSessionOnConsoleKey':True,'kCGSessionLoginDoneKey':True,'kCGSSessionUserIDKey':os.getuid(),'kCGSSessionUserNameKey':'private'}]}])
            else:
                raw=b'REACH : (Reachable) address 1.2.3.4'
            return SimpleNamespace(returncode=0,stdout=raw)
        result=o.observe_host(runner)
        self.assertTrue(all(result[k] for k in ('ac_power','lid_open','console_session','network_route_reachable')))
        self.assertNotIn('private',json.dumps(result))
        self.assertNotIn('1.2.3.4',json.dumps(result))

    def test_command_failure_remains_unknown(self):
        def runner(*a,**kw):raise OSError()
        result=o.observe_host(runner)
        self.assertIsNone(result['lid_open'])
        self.assertIsNone(result['ac_power'])

    def test_exact_natural_start_and_official_holiday(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)/'raw';raw.write_bytes(b'official fixture')
            path=Path(tmp)/'calendar.json'
            path.write_text(json.dumps({'raw_file':str(raw),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'coverage_start':'2026-01-01','coverage_end':'2026-12-31','sessions':['2026-09-30','2026-10-08']}))
            config={'schema_version':'gold2-host-observer-config.v1','expires_on_exclusive':'2026-10-16','calendar_receipt_path':str(path),'calendar_receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            def at(day,hour=7,minute=55):return datetime.fromisoformat(f'{day}T{hour:02}:{minute:02}:00+08:00')
            self.assertEqual(o.authorize_day(config,at('2026-09-30')),'ELIGIBLE_START')
            self.assertEqual(o.authorize_day(config,at('2026-10-01')),'OFFICIAL_NON_SESSION')
            self.assertEqual(o.authorize_day(config,at('2026-10-08',8,0)),'MISSED_START_MINUTE')
            self.assertEqual(o.authorize_day(config,at('2026-10-16')),'EXPIRED')
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'HASH_CHANGED'):o.authorize_day(config,at('2026-09-30'))

    def samples(self):
        start=datetime.fromisoformat('2026-09-30T07:55:00+08:00')
        samples=[{'observed_at':(start+timedelta(seconds=i*60)).isoformat(),'elapsed_monotonic_seconds':i*60,'host':{k:True for k in ('ac_power','lid_open','console_session','network_route_reachable')}} for i in range(86)]
        return samples,start,start+timedelta(minutes=85)

    def test_valid_sampling_never_claims_continuity_or_trade(self):
        samples,start,end=self.samples();result=o.assess(samples,start,end)
        self.assertEqual(result['status'],'SAMPLED_WINDOW_MET')
        self.assertFalse(result['continuous_availability_proven'])
        self.assertFalse(result['broker_action_authorized'])

    def test_sleep_gap_unknown_or_lid_close_rejects(self):
        for failure in ('gap','unknown','lid'):
            samples,start,end=self.samples()
            if failure=='gap':samples=samples[:3]+samples[5:]
            elif failure=='unknown':samples[4]['host']['network_route_reachable']=None
            else:samples[4]['host']['lid_open']=False
            self.assertEqual(o.assess(samples,start,end)['status'],'SAMPLED_WINDOW_NOT_MET')

    def test_clock_change_and_missing_endpoint_rejects(self):
        samples,start,end=self.samples()
        samples[3]['observed_at']=(start+timedelta(seconds=900)).isoformat()
        self.assertIn('WALL_MONOTONIC_DIVERGENCE',o.assess(samples,start,end)['failures'])
        samples,start,end=self.samples()
        self.assertIn('WINDOW_ENDPOINTS_MISSING',o.assess(samples[:-1],start,end)['failures'])

    def test_exclusive_receipt_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'receipt.json';o.exclusive_json(path,{'status':'REAL_FAILURE'})
            with self.assertRaises(FileExistsError):o.exclusive_json(path,{'status':'PASS'})
            self.assertEqual(json.loads(path.read_bytes())['status'],'REAL_FAILURE')


if __name__ == '__main__':unittest.main()
