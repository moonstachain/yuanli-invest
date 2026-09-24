#!/usr/bin/env python3
"""Publish existing research receipts via the scoped machine Edge only."""

import argparse
import json
from pathlib import Path

from yuanli_invest.receipts import receipt_envelope

if __package__:
    from .research_worker import MachineGateway
else:
    from research_worker import MachineGateway


def publish_receipt(gateway, receipt, *, learning=None, runner_commit="LOCAL", config_version="gold2_live_shadow.activation.v0.1"):
    payload = receipt_envelope(receipt)
    payload.update({"runner_commit": runner_commit, "config_version": config_version})
    if learning is not None:
        encoded = receipt_envelope(learning)
        payload.update({"learning_json": encoded["receipt_json"], "learning_sha256": encoded["receipt_sha256"]})
    return gateway("ingest_receipt", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--learning", type=Path)
    parser.add_argument("--runner-commit", default="LOCAL")
    parser.add_argument("--config-version", default="gold2_live_shadow.activation.v0.1")
    args = parser.parse_args()
    try:
        data = publish_receipt(
            MachineGateway.from_environment(), json.loads(args.receipt.read_text(encoding="utf-8")),
            learning=json.loads(args.learning.read_text(encoding="utf-8")) if args.learning else None,
            runner_commit=args.runner_commit, config_version=args.config_version,
        )
        print(json.dumps({"status": "MACHINE_REALITY_SINK_PASS", "authority": "SHADOW_ONLY", "data": data}, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(json.dumps({"status": "PRODUCT_SINK_FAIL_CLOSED", "authority": "SHADOW_ONLY", "error_type": type(exc).__name__}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
