#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.yuanli.ymq-gold2-live-shadow"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
WRAPPER="$REPO_ROOT/scripts/run_ymq_gold2_live_shadow_machine.sh"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
NODE_BIN="${NODE_BIN:-$(command -v node)}"
WIND_MCP_CLI="${WIND_MCP_CLI:-$HOME/.agents/skills/wind-mcp-skill/scripts/cli.mjs}"
RUNTIME_DIR="${YMQ_GOLD2_SHADOW_DIR:-$HOME/.yuanli/runtime/ymq_gold2_live_shadow}"
SINK_CLIENT="${YIOS_TG1_SINK_CLIENT:-$HOME/YuanliRemoteReadGateway/YOS-OBS2-v1/runtime/yios-tg1-g1-runtime-code/scripts/yios_tg1_gold2_machine_sink.py}"
INGEST_ENDPOINT="${YIOS_TG1_INGEST_ENDPOINT:-https://tbmoimbdhsrltvospwpu.supabase.co/functions/v1/yios-tg1-g1-ingest}"
CLIENT_ID="${YIOS_TG1_MACHINE_CLIENT_ID:-YIOS-TG1-G1R-M4}"
KEYCHAIN_SERVICE="${YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE:-yuanli.yios-tg1.machine-ingest-token}"

[[ -x "$PYTHON_BIN" ]] || { echo "python3 not found" >&2; exit 2; }
[[ -x "$NODE_BIN" ]] || { echo "node not found" >&2; exit 2; }
[[ -f "$WIND_MCP_CLI" ]] || { echo "Wind MCP CLI not found" >&2; exit 2; }
[[ -f "$WRAPPER" ]] || { echo "machine wrapper missing" >&2; exit 2; }
[[ -f "$SINK_CLIENT" ]] || { echo "machine sink client missing" >&2; exit 2; }

/usr/bin/security find-generic-password   -a "$USER" -s "$KEYCHAIN_SERVICE" >/dev/null 2>&1 || {
  echo "machine ingest token Keychain projection missing" >&2
  exit 3
}

mkdir -p "$HOME/Library/LaunchAgents" "$RUNTIME_DIR/logs"
NODE_DIR="$(dirname "$NODE_BIN")"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key><array>
    <string>${WRAPPER}</string>
  </array>
  <key>WorkingDirectory</key><string>${REPO_ROOT}</string>
  <key>EnvironmentVariables</key><dict>
    <key>WIND_MCP_CLI</key><string>${WIND_MCP_CLI}</string>
    <key>YMQ_GOLD2_SHADOW_DIR</key><string>${RUNTIME_DIR}</string>
    <key>YIOS_TG1_SINK_CLIENT</key><string>${SINK_CLIENT}</string>
    <key>YIOS_TG1_INGEST_ENDPOINT</key><string>${INGEST_ENDPOINT}</string>
    <key>YIOS_TG1_MACHINE_CLIENT_ID</key><string>${CLIENT_ID}</string>
    <key>YIOS_TG1_MACHINE_TOKEN_KEYCHAIN_SERVICE</key><string>${KEYCHAIN_SERVICE}</string>
    <key>PATH</key><string>${NODE_DIR}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key><dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>10</integer>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${RUNTIME_DIR}/logs/stdout.log</string>
  <key>StandardErrorPath</key><string>${RUNTIME_DIR}/logs/stderr.log</string>
</dict></plist>
EOF

plutil -lint "$PLIST" >/dev/null
launchctl bootout "gui/$UID/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$UID" "$PLIST"
launchctl kickstart -k "gui/$UID/$LABEL"

echo "INSTALLED ${LABEL}"
echo "MODE YIOS-TG1-G1R_MACHINE_GATEWAY"
echo "AUTHORITY SHADOW_ONLY"
echo "SECRET_IN_PLIST NO"
