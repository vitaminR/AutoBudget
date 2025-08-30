#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root relative to this script (scripts/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PY=${PYTHON_BIN:-python3}
if ! command -v "$PY" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PY=python
  fi
fi

"$PY" "$SCRIPT_DIR/generate_snapshot.py"
echo "Snapshot written to project_snapshot.md"
