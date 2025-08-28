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
- Smoke endpoints return HTTP 200:
  - GET /
  - GET /payperiods/{id}/summary
  - GET /debts/snowball
  - GET /unlocks
  - POST /reconcile
  - COMPAT only: /api/pay-periods, /api/pay-periods/{n}/bills

Note: Prefer the non-/api MVP routes; /api/\* aliases are temporary COMPAT stubs.

## Repo pointers

- Backend entrypoint (MVP, DB-free): `autobudget_backend/app.py`
- Legacy DB-backed app (kept for reference): `autobudget_backend/main.py`
- Data seed/inspect (legacy flow): `scripts/ingest_data.py`, `scripts/inspect_db.py`
- Keep `project_snapshot.md` lean (no binaries, no lockfile dumps)
