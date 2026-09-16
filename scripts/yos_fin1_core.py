#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "yos_fin1" / "fin1_source_contract.v0.1.json"


def load_contract(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or CONTRACT).read_text(encoding="utf-8"))


def validate_contract(c: Mapping[str, Any]) -> None:
    providers = c.get("providers")
    if not isinstance(providers, Mapping):
        raise ValueError("providers missing")
    expected = {
        "WIND": "EVIDENCE_ONLY",
        "MIAOXIANG_DATA": "EVIDENCE_ONLY",
        "WENCAI_SCREEN": "NO_EVIDENCE_AUTHORITY",
    }
    for provider, ceiling in expected.items():
        if providers.get(provider, {}).get("authority_ceiling") != ceiling:
            raise ValueError(f"provider authority drift: {provider}")
    anti = c.get("anti_echo", {})
    if anti.get("distinct_provider_roots_required") is not True:
        raise ValueError("independent provider roots must be required")
    if anti.get("same_provider_requery_counts_as_corroboration") is not False:
        raise ValueError("same-provider requery cannot count as corroboration")
    authority = c.get("authority", {})
    for field in (
        "capital_authorized", "sizing_authorized", "execution_authorized",
        "broker_action", "veighna_authorized", "canon_promotion_authorized",
        "production_scheduler_authorized",
    ):
        if authority.get(field) is not False:
            raise ValueError(f"forbidden authority enabled: {field}")
    security = c.get("security", {})
    if security.get("raw_authenticated_body_git_persistence") is not False:
        raise ValueError("raw authenticated body persistence forbidden")
    if security.get("secret_echo_authorized") is not False:
        raise ValueError("secret echo forbidden")


if __name__ == "__main__":
    contract = load_contract()
    validate_contract(contract)
    print("YOS-FIN1-G0 source contract: PASS")

import hashlib


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalize_receipt(*, provider: str, provider_class: str, request_kind: str, query: str,
                      observed_at: str, effective_at: str | None, instrument_or_series: str,
                      normalized_fields: Mapping[str, Any], provenance: Mapping[str, Any],
                      authority_ceiling: str, evidence_root_id: str, response_hash: str) -> dict[str, Any]:
    if not provider or not request_kind or not observed_at or not evidence_root_id:
        raise ValueError('incomplete provider receipt')
    if authority_ceiling not in {
        'EVIDENCE_ONLY','KNOWLEDGE_CANDIDATE_INPUT','PENDING_PIT_VALIDATION',
        'NO_EVIDENCE_AUTHORITY','NO_CANON_AUTHORITY'
    }:
        raise ValueError('unsupported authority ceiling')
    return {
        'provider': provider,
        'provider_class': provider_class,
        'request_kind': request_kind,
        'query_fingerprint': _fingerprint(query),
        'observed_at': observed_at,
        'effective_at': effective_at,
        'instrument_or_series': instrument_or_series,
        'normalized_fields': dict(normalized_fields),
        'provenance': dict(provenance),
        'authority_ceiling': authority_ceiling,
        'evidence_root_id': evidence_root_id,
        'response_hash': response_hash,
        'raw_body_persisted': False,
    }


def compare_provider_receipts(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, Any]:
    if a.get('provider') == b.get('provider'):
        return {'status': 'SAME_PROVIDER_NOT_CORROBORATION', 'independent_root_count': 1}
    sa = a.get('normalized_fields', {}).get('semantic_id')
    sb = b.get('normalized_fields', {}).get('semantic_id')
    if sa != sb:
        return {'status': 'SEMANTIC_MISMATCH', 'independent_root_count': 2}
    if not a.get('effective_at') or not b.get('effective_at'):
        return {'status': 'PIT_MISSING', 'independent_root_count': 2}
    if a.get('effective_at') != b.get('effective_at'):
        return {'status': 'PIT_MISMATCH', 'independent_root_count': 2}
    return {'status': 'INDEPENDENT_CORROBORATION_CANDIDATE', 'independent_root_count': 2}


def route_request(request_kind: str) -> dict[str, Any]:
    routes = {
        'macro_fact': {'primary': 'WIND', 'corroborate_with': ['MIAOXIANG_DATA']},
        'listed_company_fact': {'primary': 'WIND', 'corroborate_with': ['MIAOXIANG_DATA']},
        'natural_language_screen': {'primary': 'WENCAI_SCREEN', 'verify_with': ['WIND', 'MIAOXIANG_DATA']},
    }
    if request_kind not in routes:
        raise ValueError(f'unsupported request kind: {request_kind}')
    return routes[request_kind]
