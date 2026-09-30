#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"
KEYCHAIN_SERVICE="${YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE:-yuanli.yios-tg1.machine-ingest-token}"
KEYCHAIN_ACCOUNT="${YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_ACCOUNT:-$(id -un)}"

[[ -x "$PYTHON_BIN" ]] || { echo "Install the project into .venv or set PYTHON_BIN" >&2; exit 21; }
[[ -n "${YUANLI_RESEARCH_MACHINE_URL:-}" && -n "${YUANLI_WORKSPACE_ID:-}" && -n "${YIOS_TG1_MACHINE_CLIENT_ID:-}" && -f "${YUANLI_RESEARCH_SOURCE_CONFIG:-}" ]] || {
  echo "machine endpoint, workspace, client and reviewed source config are required" >&2
  exit 22
}

TOKEN="$(/usr/bin/security find-generic-password -a "$KEYCHAIN_ACCOUNT" -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)" || {
  echo "machine ingest token Keychain projection missing" >&2
  exit 24
}
[[ -n "$TOKEN" ]] || { echo "empty machine ingest token" >&2; exit 24; }
export YIOS_TG1_MACHINE_INGEST_TOKEN="$TOKEN"
unset TOKEN

exec "$PYTHON_BIN" "$REPO_ROOT/scripts/research_daily.py"
