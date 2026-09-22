#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, os, shutil, urllib.error, urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

OPENAPI_URL='https://openapi.iwencai.com/v1/query2data'

@dataclass(repr=False)
class CredentialRef:
    source: str
    value: str = field(repr=False)
    def __getitem__(self,key:str): return getattr(self,key)
    def __repr__(self): return f"CredentialRef(source={self.source!r}, value=<redacted>)"


def discover_api_key(env: Mapping[str,str] | None=None) -> CredentialRef:
    env=env or os.environ
    value=(env.get('IWENCAI_API_KEY') or '').strip()
    if not value:
        raise RuntimeError('AUTH_MISSING: IWENCAI_API_KEY not configured')
    return CredentialRef('IWENCAI_API_KEY', value)


def build_openapi_request(query: str, page: int=1, limit: int=20) -> dict[str,Any]:
    return {
        'url':OPENAPI_URL,
        'payload':{'query':query,'source':'yuanli-fin1','page':str(page),'limit':str(limit),'is_cache':'1'},
        'endpoint_authority':'COMMUNITY_DOCUMENTED_RUNTIME_VERIFICATION_REQUIRED'
    }


def normalize_screen_response(body: Mapping[str,Any], query: str) -> dict[str,Any]:
    if body.get('status_code') not in (0,'0'):
        code=body.get('status_code')
        msg=str(body.get('status_msg') or 'provider rejected query')
        if str(code) in {'401','403'}: raise RuntimeError(f'AUTH_REJECTED: {msg}')
        raise RuntimeError(f'PROVIDER_UNAVAILABLE: {msg}')
    rows=body.get('datas') or []
    candidates=[]
    for row in rows[:50]:
        if not isinstance(row,Mapping): continue
        code=row.get('股票代码') or row.get('code') or row.get('股票代码[最新]')
        name=row.get('股票简称') or row.get('name') or row.get('股票简称[最新]')
        if code or name:
            candidates.append({'code':str(code) if code is not None else None,'name':name})
    return {
        'provider':'IWENCAI',
        'role':'RESEARCH_CANDIDATE',
        'authority_ceiling':'NO_EVIDENCE_AUTHORITY',
        'request_kind':'natural_language_screen',
        'query_fingerprint':hashlib.sha256(query.encode()).hexdigest(),
        'observed_at':datetime.now(timezone.utc).isoformat(),
        'candidate_count':len(candidates),
        'candidates':candidates,
        'raw_body_persisted':False,
        'endpoint_authority':'COMMUNITY_DOCUMENTED_RUNTIME_VERIFICATION_REQUIRED'
    }


def browser_cli_descriptor(path: str | None=None) -> dict[str,Any]:
    resolved=path or shutil.which('iwencai-query')
    return {'available':bool(resolved),'path':resolved,'role':'DISCOVERY_ONLY','authority_ceiling':'NO_CANON_AUTHORITY'}


def query_openapi(query: str, *, timeout: int=30, limit: int=20) -> dict[str,Any]:
    cred=discover_api_key()
    spec=build_openapi_request(query, limit=limit)
    req=urllib.request.Request(spec['url'], data=json.dumps(spec['payload'],ensure_ascii=False).encode(), method='POST', headers={'Content-Type':'application/json','Authorization':f'Bearer {cred.value}'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body=json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        code='AUTH_REJECTED' if e.code in (401,403) else 'PROVIDER_UNAVAILABLE'
        raise RuntimeError(f'{code}: HTTP {e.code}') from None
    except Exception as e:
        raise RuntimeError(f'PROVIDER_UNAVAILABLE: {type(e).__name__}') from None
    return normalize_screen_response(body,query)
