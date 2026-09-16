#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from scripts.yos_fin1_core import normalize_receipt

DEFAULT_CLI = Path.home()/'.agents/skills/wind-mcp-skill/scripts/cli.mjs'
FALLBACK_CLI = Path.home()/'YuanliRemoteReadGateway/YOS-OBS2-v1/work/wind-skills-research/skills/wind-mcp-skill/scripts/cli.mjs'


def classify_failure(text: str) -> str:
    t = text.lower()
    if '积分余额不足' in text or '调用次数已达上限' in text or 'credit' in t or 'quota' in t:
        return 'QUOTA_OR_CREDIT_BLOCK'
    if '未配置' in text and ('api_key' in t or 'wind_api_key' in t):
        return 'AUTH_MISSING'
    if '401' in text or 'unauthorized' in t or '已失效' in text:
        return 'AUTH_REJECTED'
    if 'schema' in t or '字段' in text and '必须是' in text:
        return 'SCHEMA_DRIFT'
    if '未识别到有效的金融标的' in text:
        return 'ENTITY_UNRESOLVED'
    return 'PROVIDER_UNAVAILABLE'


def build_macro_request(question: str, observations: int = 3) -> dict[str, Any]:
    return {'question': question, 'observation': str(observations)}


def _date_iso(v: str) -> str:
    s = str(v).replace('-', '')
    if len(s) != 8 or not s.isdigit():
        raise ValueError('invalid provider date')
    return f'{s[:4]}-{s[4:6]}-{s[6:8]}'


def parse_metric_payload(payload: dict[str, Any], expected_code: str) -> dict[str, Any]:
    metrics = payload.get('metrics')
    if not isinstance(metrics, list):
        raise ValueError('SCHEMA_DRIFT: metrics missing')
    for metric in metrics:
        meta = metric.get('meta', {})
        if meta.get('code') != expected_code:
            continue
        dates, values = metric.get('date'), metric.get('value')
        if not dates or not values or len(dates) != len(values):
            raise ValueError('PIT_MISSING: date/value missing')
        return {
            'metric_code': expected_code,
            'metric_name': meta.get('name'),
            'source': meta.get('source'),
            'unit': meta.get('unit'),
            'effective_at': _date_iso(dates[-1]),
            'value': values[-1],
        }
    raise ValueError('ENTITY_UNRESOLVED: expected metric code not found')


def _cli_path() -> Path:
    env = os.getenv('WIND_MCP_CLI')
    if env and Path(env).is_file(): return Path(env)
    if DEFAULT_CLI.is_file(): return DEFAULT_CLI
    if FALLBACK_CLI.is_file(): return FALLBACK_CLI
    raise RuntimeError('AUTH_MISSING: Wind MCP CLI unavailable')


def query_macro_metric(question: str, expected_code: str, observations: int = 3) -> dict[str, Any]:
    params = build_macro_request(question, observations)
    cp = subprocess.run(['node', str(_cli_path()), 'call', 'economic_data', 'query_economic_indicator_data', json.dumps(params, ensure_ascii=False)], capture_output=True, text=True, timeout=45)
    text = (cp.stdout or '').strip()
    if cp.returncode != 0:
        try:
            err = json.loads(text)
            msg = str(err.get('message') or err)
        except Exception:
            msg = (cp.stderr or text or 'Wind CLI failure')[:500]
        raise RuntimeError(f'{classify_failure(msg)}: {msg}')
    outer = json.loads(text)
    content = outer.get('content') or []
    if not content:
        raise RuntimeError('SCHEMA_DRIFT: missing content')
    inner_text = content[0].get('text')
    inner = json.loads(inner_text)
    parsed = parse_metric_payload(inner, expected_code)
    raw_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return normalize_receipt(
        provider='WIND', provider_class='licensed_vendor', request_kind='macro_fact',
        query=question, observed_at=datetime.now(timezone.utc).isoformat(),
        effective_at=parsed['effective_at'], instrument_or_series=expected_code,
        normalized_fields={'value':parsed['value'],'unit':parsed['unit'],'semantic_id':'US_LONG_REAL_YIELD'},
        provenance={'provider_metric_code':expected_code,'source':parsed['source'],'metric_name':parsed['metric_name']},
        authority_ceiling='EVIDENCE_ONLY', evidence_root_id=f'wind:{expected_code}', response_hash=raw_hash,
    )
