#!/usr/bin/env bash
# Run the test suite, overwrite logs, and emit JUnit XML.
# Usage: bash scripts/run_tests.sh
set -euo pipefail

log() { printf "[tests] %s\n" "$*"; }
die() { printf "[tests][ERR] %s\n" "$*" >&2; exit 1; }

# Resolve repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -z "$ROOT" ] && ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || die "Cannot cd to repo root"

TEST_FILE="tests/test_use_cases.py"
[ -f "$TEST_FILE" ] || die "Missing $TEST_FILE"

mkdir -p "$ROOT/.devlogs"

# Choose venv: prefer root .venv, fall back to backend venv if present
VENV_ACTIVATE=""
if [ -f "$ROOT/.venv/bin/activate" ]; then
  VENV_ACTIVATE="$ROOT/.venv/bin/activate"
elif [ -f "$ROOT/autobudget_backend/.venv/bin/activate" ]; then
  VENV_ACTIVATE="$ROOT/autobudget_backend/.venv/bin/activate"
else
  log "Creating Python venv at .venv ..."
  python3 -m venv .venv || die "venv creation failed"
  VENV_ACTIVATE="$ROOT/.venv/bin/activate"
fi
# shellcheck disable=SC1090
source "$VENV_ACTIVATE"

python -m pip -q install -U pip >/dev/null || true
# Install requirements if present
if [ -f "$ROOT/autobudget_backend/requirements.txt" ]; then
  pip -q install -r "$ROOT/autobudget_backend/requirements.txt" >/dev/null || die "pip install failed"
fi
pip -q install pytest >/dev/null || true

export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

log "Running pytest verbose run (logged to .devlogs/tests.log) ..."
set +e
python -m pytest -vv -rA "$TEST_FILE" | tee "$ROOT/.devlogs/tests.log"
CODE=$?
set -e
log "Exit code: $CODE"

log "Tail of .devlogs/tests.log (last 80 lines):"
tail -n 80 "$ROOT/.devlogs/tests.log" || true

log "Emitting JUnit XML to .devlogs/pytest.xml ..."
python -m pytest -q --junitxml="$ROOT/.devlogs/pytest.xml" "$TEST_FILE" >/dev/null || true

exit "$CODE"
