#!/usr/bin/env bash
set -euo pipefail

PORTS=(8000 3000 5173)
if [[ $# -gt 0 ]]; then PORTS=("$@"); fi

stop_port() {
  local port="$1"
  echo "Stopping processes on port ${port}..." >&2
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti:"${port}" -sTCP:LISTEN | xargs -r kill -9 || true
  else
    echo "No fuser/lsof; skipping ${port}" >&2
  fi
}

for p in "${PORTS[@]}"; do
  stop_port "$p"
done

echo "Done." >&2
