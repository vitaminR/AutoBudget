# AUTOBUDGET Project

This repo defines the **Auto-Budget Pilot Plan**, instructions, API contracts, and test data for building an ADHD-friendly budgeting + debt payoff app.

## 📂 Files

1. **systemInstructions.md**

   - Master Prompt for the AI Assistant (Enhanced).
   - Defines personas (PM, Engineer, Analyst) and response schema (Keep/Fix/Add/Risks/Confidence + backlog).

2. **2.AutoBudgetPilotPlan.md**

   - Core pilot plan (Enhanced for Retrieval).
   - Contains §1–§10 (principles, financial situation, pots, tech stack, data model, flows, user stories, cost, risks, next steps).
   - Includes **PP-Negative Rule**, bill pay fields, security/observability, gamification milestone story.

3. **data/3.api.json**

   - OpenAPI spec v0.1 for FastAPI backend.
   - Endpoints for ingesting bills, pay period summaries, marking bills paid, checklists, unlocks, snowball view, and reconciliation.

4. **4.ports_logic.md**

   - Pots & Onboarding brief.
   - Explains the 4-pot system, double-entry ledger, reconciliation, onboarding wizard, checklist/unlock flow, and risk safeguards.

5. **5.Tidy_Bills_AugNov_with_PPs.csv**

   - Sample input data for PP17–PP24 (Aug–Nov).
   - Used to simulate surplus/deficit, rent timing, snowball, unlock flow.

6. **6.gamification.md**

   - Gamification layer to enhance user engagement.
   - Includes features like debt countdown bar, streaks, mini achievements, challenges, spouse play, visualizations, surprise unlocks, narrative journey, and failure recovery.

## 🚀 How It Fits Together

- **Assistant**: Uses (1) + (2) for guidance.
- **File Search**: Ingests (2), (4), (5) for context and data.
- **API**: Built according to (data/3), backed by SQLite/Postgres.
- **Backend Repo** (later): Implements logic from (2) + (4) using models from (3).

## 🧩 Next

- Add DB backend repo when ready (SQLite → Postgres).

## 🛠️ Dev

Local one-command startup (backend + frontend with waits/logs):

- Windows PowerShell:
  - `./scripts/dev.ps1`
- WSL/Linux:
  - `bash scripts/dev.sh`

Notes:

- Backend starts on <http://127.0.0.1:8000> (FastAPI/uvicorn).
- Frontend starts on <http://127.0.0.1:3000> (if `autobudget_frontend/` exists and npm is available).
- Logs are in `.devlogs/{backend.log,frontend.log}`; Ctrl+C stops both services.

See also: `docs/CONVENTIONS.md` for tags (TODO/FIXME/FUTURE/PLACEHOLDER/COMPAT) and placeholder response shape.

## ⚡ Quickstart

Backend (MVP, DB-free): starts on <http://127.0.0.1:8000>

- Use the one-command startup above, or run the backend directly via the VS Code Python interpreter targeting `autobudget_backend/app.py` with uvicorn.
- Preferred routes: `/`, `/ingest/bills`, `/payperiods/{id}/summary`, `/debts/snowball`, `/unlocks`, `/reconcile`.
- Temporary compatibility: `/api/pay-periods`, `/api/pay-periods/{n}/bills`, `/api/ingest-csv`, `/api/bills/{id}/toggle-paid` (placeholders tagged COMPAT/PLACEHOLDER in the code). These will be removed once the frontend migrates.
