#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.yuanli.ymq-gold2-live-shadow"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
NODE_BIN="${NODE_BIN:-$(command -v node)}"
WIND_MCP_CLI="${WIND_MCP_CLI:-$HOME/.agents/skills/wind-mcp-skill/scripts/cli.mjs}"
RUNTIME_DIR="${YMQ_GOLD2_SHADOW_DIR:-$HOME/.yuanli/runtime/ymq_gold2_live_shadow}"

[[ -x "$PYTHON_BIN" ]] || { echo "python3 not found" >&2; exit 2; }
[[ -x "$NODE_BIN" ]] || { echo "node not found" >&2; exit 2; }
[[ -f "$WIND_MCP_CLI" ]] || { echo "Wind MCP CLI not found: $WIND_MCP_CLI" >&2; exit 2; }
[[ -f "$REPO_ROOT/scripts/ymq_gold2_live_shadow.py" ]] || { echo "runner missing" >&2; exit 2; }

mkdir -p "$HOME/Library/LaunchAgents" "$RUNTIME_DIR/logs"
NODE_DIR="$(dirname "$NODE_BIN")"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key><array>
    <string>${PYTHON_BIN}</string>
    <string>${REPO_ROOT}/scripts/ymq_gold2_live_shadow.py</string>
  </array>
  <key>WorkingDirectory</key><string>${REPO_ROOT}</string>
  <key>EnvironmentVariables</key><dict>
    <key>WIND_MCP_CLI</key><string>${WIND_MCP_CLI}</string>
    <key>YMQ_GOLD2_SHADOW_DIR</key><string>${RUNTIME_DIR}</string>
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
echo "PLIST ${PLIST}"
echo "RUNTIME ${RUNTIME_DIR}"
echo "AUTHORITY research+scheduler only; capital/sizing/execution/broker remain DENY"
