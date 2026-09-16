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
