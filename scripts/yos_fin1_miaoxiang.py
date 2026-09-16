#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, os, urllib.error, urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from scripts.yos_fin1_core import normalize_receipt

DATA_URL='https://mkapi2.dfcfs.com/finskillshub/api/claw/query'

@dataclass(repr=False)
class CredentialRef:
    source: str
    value: str = field(repr=False)
    def __getitem__(self, key: str):
        return getattr(self, key)
    def __repr__(self) -> str:
        return f"CredentialRef(source={self.source!r}, value=<redacted>)"


def discover_api_key(env: Mapping[str,str] | None=None) -> CredentialRef:
    env = env or os.environ
    for name in ('MX_APIKEY','EASTMONEY_APIKEY'):
        value=(env.get(name) or '').strip()
        if value:
            return CredentialRef(name, value)
    raise RuntimeError('AUTH_MISSING: MX_APIKEY/EASTMONEY_APIKEY not configured')


def build_data_request(query: str) -> dict[str, Any]:
    return {'url':DATA_URL,'payload':{'toolQuery':query}}


def classify_error(code: Any, message: str) -> str:
    s=f'{code} {message}'.lower()
    if str(code)=='113' or '调用次数已达上限' in message or 'quota' in s or 'credit' in s:
        return 'QUOTA_OR_CREDIT_BLOCK'
    if str(code) in {'114','401'} or '密钥不存在' in message or 'unauthorized' in s:
        return 'AUTH_REJECTED'
    if 'schema' in s or '字段' in message:
        return 'SCHEMA_DRIFT'
    return 'PROVIDER_UNAVAILABLE'


def _find_effective_at(obj: Any) -> str | None:
    keys=('tradeDate','tradingDate','reportDate','endDate','date','time')
    if isinstance(obj, dict):
        for k in keys:
            v=obj.get(k)
            if isinstance(v,str):
                digits=v[:10].replace('/','-')
                if len(digits)>=8:
                    return digits
        for v in obj.values():
            found=_find_effective_at(v)
            if found: return found
    elif isinstance(obj, list):
        for v in reversed(obj[:50]):
            found=_find_effective_at(v)
            if found: return found
    return None


def normalize_data_response(body: Mapping[str,Any], query: str) -> dict[str,Any]:
    if body.get('status') not in (0,'0',None):
        raise RuntimeError(f"{classify_error(body.get('status'),str(body.get('message','')))}: provider rejected request")
    effective_at=_find_effective_at(body.get('data'))
    authority='EVIDENCE_ONLY' if effective_at else 'KNOWLEDGE_CANDIDATE_INPUT'
    raw_hash=hashlib.sha256(json.dumps(body,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    qid=(body.get('data') or {}).get('questionId') if isinstance(body.get('data'),dict) else None
    return normalize_receipt(
        provider='MIAOXIANG', provider_class='licensed_vendor', request_kind='listed_company_fact',
        query=query, observed_at=datetime.now(timezone.utc).isoformat(), effective_at=effective_at,
        instrument_or_series=str(qid or 'natural-language-query'),
        normalized_fields={'semantic_id':'PROVIDER_NATURAL_LANGUAGE_RESULT','question_id':qid},
        provenance={'endpoint':DATA_URL,'provider':'Eastmoney MiaoXiang'}, authority_ceiling=authority,
        evidence_root_id=f"miaoxiang:{qid or raw_hash[:16]}", response_hash=raw_hash,
    )


def query_data(query: str, *, timeout: int=30) -> dict[str,Any]:
    cred=discover_api_key()
    spec=build_data_request(query)
    data=json.dumps(spec['payload'],ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(spec['url'],data=data,method='POST',headers={'Content-Type':'application/json','apikey':cred.value})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body=json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{classify_error(e.code,e.reason or '')}: HTTP {e.code}") from None
    except Exception as e:
        raise RuntimeError(f"PROVIDER_UNAVAILABLE: {type(e).__name__}") from None
    return normalize_data_response(body, query)
