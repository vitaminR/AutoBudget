#!/usr/bin/env bash
set -euo pipefail

log() { printf "[dev] %s\n" "$*"; }
die() { printf "[dev][ERR] %s\n" "$*" >&2; exit 1; }

# Resolve repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -z "$ROOT" ] && ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || die "Cannot cd to repo root"

BACKEND_DIR="$ROOT/autobudget_backend"
FRONTEND_DIR="$ROOT/autobudget_frontend"
BACKEND_HEALTH="http://127.0.0.1:8000/openapi.json"
FRONTEND_HEALTH="http://127.0.0.1:3000"

# Backend module selection
# Defaults to MVP (DB-free). Set USE_DB=1 or BACKEND=legacy|db to use the DB-backed legacy app.
BACKEND_MODULE="${BACKEND_MODULE:-autobudget_backend.app:app}"
if [ "${USE_DB:-}" = "1" ] || [ "${BACKEND:-}" = "legacy" ] || [ "${BACKEND:-}" = "db" ]; then
  BACKEND_MODULE="autobudget_backend.main:app"
fi

# Optional: set DEV_SEED=1 to run a seed step before backend starts
DEV_SEED="${DEV_SEED:-}"

require() { command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"; }

wait_http() {
  local url="$1" tries="${2:-120}" delay="${3:-0.5}"
  for ((i=1;i<=tries;i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep "$delay"
  done
  return 1
}

start_backend() {
  [ -d "$BACKEND_DIR" ] || die "Backend directory not found: $BACKEND_DIR"
  log "Starting backend (uvicorn autobudget_backend.app:app) ..."
  cd "$BACKEND_DIR"
  if [ ! -d ".venv" ]; then
    log "Creating Python venv ..."
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip -q install --upgrade pip >/dev/null
  if [ -f requirements.txt ]; then
    pip -q install -r requirements.txt >/dev/null || die "pip install failed"
  fi

  if [ -n "$DEV_SEED" ]; then
    log "Seeding (DEV_SEED=1) ..."
    python "$ROOT/scripts/ingest_data.py" || log "Seed failed (continuing)"
  fi

  cd "$ROOT"
  mkdir -p "$ROOT/.devlogs"
  (
  . "$BACKEND_DIR/.venv/bin/activate" \
  && export PYTHONPATH="$ROOT:${PYTHONPATH:-}" \
  && PYTHONUNBUFFERED=1 python -m uvicorn "$BACKEND_MODULE" \
         --host 127.0.0.1 --port 8000 --reload --reload-dir "$BACKEND_DIR"
  ) >"$ROOT/.devlogs/backend.log" 2>&1 &
  echo $! > "$ROOT/.devlogs/backend.pid"

  log "Backend PID $(cat "$ROOT/.devlogs/backend.pid"); waiting for $BACKEND_HEALTH ..."
  wait_http "$BACKEND_HEALTH" 120 0.5 || {
    log "Backend logs (tail):"; tail -n 120 "$ROOT/.devlogs/backend.log" || true
    die "Backend did not become ready"
  }
  log "Backend is ready."
}

start_frontend() {
  if [ ! -d "$FRONTEND_DIR" ]; then
    log "Frontend directory not found ($FRONTEND_DIR); skipping frontend."
    return 0
  fi
  if ! command -v npm >/dev/null 2>&1; then
    log "npm not found; skipping frontend."
    return 0
  fi
  log "Starting frontend (npm start) ..."
  cd "$FRONTEND_DIR"
  npm install --silent
  mkdir -p "$ROOT/.devlogs"
  (
    PORT=3000 npm start
  ) >"$ROOT/.devlogs/frontend.log" 2>&1 &
  echo $! > "$ROOT/.devlogs/frontend.pid"

  log "Frontend PID $(cat "$ROOT/.devlogs/frontend.pid"); waiting for $FRONTEND_HEALTH ..."
  wait_http "$FRONTEND_HEALTH" 120 0.5 || {
    log "Frontend logs (tail):"; tail -n 120 "$ROOT/.devlogs/frontend.log" || true
    die "Frontend did not become ready"
  }
  log "Frontend is ready."
}

cleanup() {
  log "Stopping services ..."
  for name in frontend backend; do
    pidfile="$ROOT/.devlogs/$name.pid"
    if [ -f "$pidfile" ]; then
      pid="$(cat "$pidfile" || true)"
      if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
      fi
      rm -f "$pidfile"
    fi
  done
  log "Done."
}
trap cleanup EXIT INT TERM

# Pre-flight checks
require curl
require python3

start_backend
start_frontend

log "All services up:
- Backend:  http://127.0.0.1:8000
- Frontend: http://127.0.0.1:3000

Logs: .devlogs/{backend.log,frontend.log}
Press Ctrl+C to stop."

wait
