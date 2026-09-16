#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

RUNTIME = Path.home()/'YuanliRemoteReadGateway/YOS-OBS2-v1/runtime/yos-fin1-g0'


def compile_qualification(*, wind: Mapping[str,Any], mx: Mapping[str,Any], wc: Mapping[str,Any]) -> dict[str,Any]:
    missing=[]
    if mx.get('status')=='HUMAN_GATE': missing.append(mx.get('error_code','MIAOXIANG_HUMAN_GATE'))
    if wc.get('status')=='HUMAN_GATE': missing.append(wc.get('error_code','IWENCAI_HUMAN_GATE'))
    if missing:
        state='AWAITING_PROVIDER_CREDENTIALS'
    elif all(x.get('status')=='PASS' for x in (wind,mx,wc)):
        state='THREE_SOURCE_RUNTIME_READY_FOR_PROBE'
    else:
        state='RUNTIME_PARTIAL_FAIL_CLOSED'
    if mx.get('status')=='HUMAN_GATE':
        probe_a='PARTIAL_WIND_FAIL_CLOSED_MIAOXIANG_HUMAN_GATE' if wind.get('status')!='PASS' else 'PARTIAL_WIND_PASS_MIAOXIANG_HUMAN_GATE'
        probe_b='MIAOXIANG_HUMAN_GATE'
    else:
        probe_a='READY_FOR_COMPARISON' if wind.get('status')=='PASS' and mx.get('status')=='PASS' else 'FAIL_CLOSED'
        probe_b='READY_FOR_COMPARISON' if mx.get('status')=='PASS' else 'FAIL_CLOSED'
    probe_c='IWENCAI_HUMAN_GATE' if wc.get('status')=='HUMAN_GATE' else ('READY_FOR_SCREEN' if wc.get('status')=='PASS' else 'FAIL_CLOSED')
    return {
        'program':'YOS-FIN1-G0',
        'state':state,
        'probe_a_macro':probe_a,
        'probe_b_equity':probe_b,
        'probe_c_screen':probe_c,
        'blockers':missing + ([wind.get('error_code')] if wind.get('status')=='FAIL_CLOSED' and wind.get('error_code') else []),
        'authority':{
            'research_authorized':True,
            'capital_authorized':False,
            'sizing_authorized':False,
            'execution_authorized':False,
            'broker_action':False,
            'canon_promotion_authorized':False,
            'production_scheduler_authorized':False,
        }
    }


def _load(name:str)->dict[str,Any]:
    p=RUNTIME/name
    return json.loads(p.read_text()) if p.exists() else {'status':'NOT_RUN'}


def main()->int:
    out=compile_qualification(wind=_load('wind-probe.json'),mx=_load('miaoxiang-probe.json'),wc=_load('wencai-probe.json'))
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
