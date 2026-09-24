#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || { echo "Install the project into .venv or set PYTHON_BIN" >&2; exit 2; }
cd "$REPO_ROOT"
exec "$PYTHON_BIN" -m scripts.install_research_schedule "$@"
