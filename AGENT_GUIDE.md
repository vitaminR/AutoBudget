# AGENT_GUIDE

Concise operating guide for agents. Keep loops tight and changes verifiable.

## Start order

1. CODE_MAP.md
2. docs/use_cases.md
3. tests/test_use_cases.py
4. 3.api.json

## Golden rules

- ≤2 files per change; keep diffs small and testable
- Functions <200 lines; add concise docstrings (inputs, outputs, side effects)
- Append each loop’s decisions/outcomes to SESSION_LOG.md
- Never run repo-wide reformatters or mass renames

## Idempotency

- Database: additive migrations only (no destructive changes without explicit plan)
- Services: prefer pure functions; inject I/O at edges

## Done criteria

- Pytest green for UC-001..UC-006 (from docs/use_cases.md)
- Smoke GETs return HTTP 200 (/, /api/pay-periods, /api/pay-periods/{n}/bills)

## Repo pointers

- Backend: `autobudget_backend/main.py` (FastAPI)
- Data seed/inspect: `scripts/ingest_data.py`, `scripts/inspect_db.py`
- Keep `project_snapshot.md` lean (no binaries, no lockfile dumps)
