#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
KEYCHAIN_SERVICE="${YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE:-yuanli.yios-tg1.machine-ingest-token}"
SINK_CLIENT="${YIOS_TG1_SINK_CLIENT:-}"
INGEST_ENDPOINT="${YIOS_TG1_INGEST_ENDPOINT:-https://tbmoimbdhsrltvospwpu.supabase.co/functions/v1/yios-tg1-g1-ingest}"
CLIENT_ID="${YIOS_TG1_MACHINE_CLIENT_ID:-YIOS-TG1-G1R-M4}"

[[ -x "$PYTHON_BIN" ]] || { echo "python3 not found" >&2; exit 21; }
[[ -n "$SINK_CLIENT" && -f "$SINK_CLIENT" ]] || {
  echo "machine sink client missing" >&2
  exit 22
}

TOKEN="$(/usr/bin/security find-generic-password   -a "$USER"   -s "$KEYCHAIN_SERVICE"   -w 2>/dev/null || true)"

if [[ -z "$TOKEN" ]]; then
  echo "machine ingest token projection missing" >&2
  exit 24
fi

export YIOS_TG1_PRODUCT_SINK_ENABLED=true
export YIOS_TG1_MACHINE_INGEST_TOKEN="$TOKEN"
export YIOS_TG1_INGEST_ENDPOINT="$INGEST_ENDPOINT"
export YIOS_TG1_MACHINE_CLIENT_ID="$CLIENT_ID"
unset TOKEN

exec "$PYTHON_BIN" "$REPO_ROOT/scripts/ymq_gold2_live_shadow.py"
