#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OP_BIN="${OP_BIN:-$(command -v op)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
ENV_OP="${YIOS_TG1_MACHINE_ENV_OP:-$HOME/.config/yuanli/yios-tg1-g1r.env.op}"
KEYCHAIN_SERVICE="${YIOS_TG1_OP_SERVICE_ACCOUNT_KEYCHAIN_SERVICE:-yuanli.yios-tg1.op-service-account}"

[[ -x "$OP_BIN" ]] || { echo "1Password CLI not found" >&2; exit 21; }
[[ -x "$PYTHON_BIN" ]] || { echo "python3 not found" >&2; exit 21; }
[[ -f "$ENV_OP" ]] || { echo "machine env.op missing: $ENV_OP" >&2; exit 22; }

if grep -q 'sb_secret_' "$ENV_OP"; then
  echo "plaintext Supabase secret detected in env.op; refusing" >&2
  exit 23
fi
if ! grep -q 'op://' "$ENV_OP"; then
  echo "env.op contains no 1Password Secret Reference" >&2
  exit 23
fi

TOKEN="$(/usr/bin/security find-generic-password   -a "$USER"   -s "$KEYCHAIN_SERVICE"   -w 2>/dev/null || true)"

if [[ -z "$TOKEN" ]]; then
  echo "machine service-account token projection missing" >&2
  exit 24
fi

export OP_SERVICE_ACCOUNT_TOKEN="$TOKEN"
unset TOKEN

exec "$OP_BIN" run   --env-file "$ENV_OP"   -- "$PYTHON_BIN" "$REPO_ROOT/scripts/ymq_gold2_live_shadow.py"
