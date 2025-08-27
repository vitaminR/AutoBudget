# CODE_MAP

This compact map mirrors the current tree and flags planned folders so an agent can navigate fast.

## Backend — `autobudget_backend/` (app.py, routes/, services/, models/, db/)

- Entry: `autobudget_backend/main.py` (FastAPI app, endpoints, SQLAlchemy models, CSV ingest)
- Config: env vars (DATABASE_URL, CSV_FILE_PATH). Default DB: `autobudget.db` at repo root
- Data scripts:
  - `scripts/inspect_db.py` — list tables and row counts (SQLite)
  - `scripts/ingest_data.py` — seed from `data/5.Tidy_Bills_AugNov_with_PPs.csv`
- Planned (not present yet): `app.py`, `routes/`, `services/`, `models/`, `db/` (migrations)

## Frontend — `autobudget_frontend/` (src/pages, src/components, src/api)

- Current: CRA layout under `autobudget_frontend/src/` (App.js, index.js, tests, styles)
- Planned (extract as app grows): `src/pages`, `src/components`, `src/api` (axios client)

## Contracts & Docs — `3.api.json`, `docs/use_cases.md`, `tests/`, `AGENT_GUIDE.md`, `SESSION_LOG.md`, `docs/FullContext.md`

- API spec: `data/3.api.json` (OpenAPI draft)
- Core docs: `docs/1.systemInstructions.md`, `docs/2.AutoBudgetPilotPlan.md`, `docs/4.ports_logic.md`, `docs/6.gamification.md`
- Agent docs: `AGENT_GUIDE.md` (this repo), `CODE_MAP.md` (this file)
- To add:
  - `docs/use_cases.md` — UC-001..UC-006 user stories + acceptance
  - `tests/test_use_cases.py` — pytest per UC
  - `SESSION_LOG.md` — append agent loops (decisions, diffs, test results)
  - `docs/FullContext.md` — optional long-form aggregation

## Tools — `scripts/agent_loop.sh`, `scripts/embed_index.py`, `.gemini/settings.json`

- Existing: `scripts/inspect_db.py`, `scripts/ingest_data.py`, `scripts/generate_snapshot.py`
- Gemini: `.gemini/ignore` present; project-local `.gemini/settings.json` not checked in (user-level exists)
- To add if needed: `scripts/agent_loop.sh` (loop driver), `scripts/embed_index.py` (RAG index), `.gemini/settings.json`

- Backend: `autobudget_backend/main.py` • DB: `autobudget.db` • Data: `data/5.Tidy_Bills_AugNov_with_PPs.csv`
- Frontend: `autobudget_frontend/src/App.js` • API: `data/3.api.json`
