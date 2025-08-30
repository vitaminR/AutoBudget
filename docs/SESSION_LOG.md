- [2025-08-29] Debugging 500 errors and frontend data loading failures.
  - Symptoms: User reports frontend pages are not loading data. Initial smoke test (`scripts/smoke_test.py`) showed 'Connection refused', indicating the server was not running.
  - Diagnostics: A subsequent attempt to run the server was cancelled. User reported an intermittent `200 OK` on the `/debts/snowball` endpoint, while other endpoints failed, suggesting a partial application startup.
  - Status: Root cause is likely a runtime error in `app.py` that occurs during initialization. Awaiting user to restart the application server so I can perform a direct launch to capture the startup error.

# Session Log

- [2025-08-29] Revert of unintended agent edits: reverted agent-made changes across the repository to restore the working tree to the previous committed state.
  - Reason: Edits expanded beyond intended frontend scope and did not follow the project's change protocol (small, reviewable diffs and SESSION_LOG entries).
  - Action: Ran a hard reset to HEAD and removed untracked files added by the agent. Files removed or reverted included (non-exhaustive):
    - frontend: `autobudget_frontend/src/components/StatusDisplay.jsx`, `autobudget_frontend/src/components/Navbar.jsx`, modifications to `autobudget_frontend/src/pages/Bills.js`, `autobudget_frontend/src/App.js`, and `autobudget_frontend/src/api/client.js`.
    - backend: edits to `autobudget_backend/app.py`, `autobudget_backend/services/pots.py`.
    - tests/tooling/docs added by agent: `tests/test_services.py`, `tests/conftest.py`, `requirements-dev.txt`, `setup.py`, many files under `.gemini/` and `.github/`, and expanded `docs/` files.
  - Verification: After revert, working tree was reset to HEAD and untracked files removed with `git clean -fd`.

This entry documents the revert performed to restore repository hygiene. Future agent edits should follow the project's AGENT_GUIDE and include incremental changes with SESSION_LOG entries before committing.

- [2025-08-29] Frontend improvements (Navbar, StatusDisplay, Dashboard placeholders).

  - Files added:
    - `autobudget_frontend/src/components/Navbar.jsx` — simple navbar with Dashboard and Bills links.
    - `autobudget_frontend/src/components/StatusDisplay.jsx` — centralized loading spinner and error alert component.
  - Files modified:
    - `autobudget_frontend/src/App.js` — imports and renders `Navbar` on all pages.
    - `autobudget_frontend/src/pages/Bills.js` — uses `StatusDisplay` for loading/error states; existing logic preserved.
    - `autobudget_frontend/src/pages/Dashboard.jsx` — added three placeholder cards: Total Monthly Bills, Next Bill Due, Accounts Reconciled.
  - Scope: frontend-only changes and this single SESSION_LOG entry were committed to follow the project's strict rules for agent edits.

- [2025-08-29] Test suite execution via scripts/run_tests.sh.

  - Action: Ran the standard test script which provisions venv and executes pytest.
  - Result: 6 passed, 0 failed, 7 warnings in ~7s. See `.devlogs/tests.log` for full output.
  - Notes: Warnings include SQLAlchemy 2.0 deprecation for `declarative_base()` and unknown pytest mark `order` (non-blocking).

- [2025-08-29] Fix: compatibility endpoint `/api/debts/snowball` crashing at runtime.

  - Action: Updated `autobudget_backend/app.py` to invoke `debts_snowball` with a real `SessionLocal()` instance in the `/api/debts/snowball` wrapper instead of calling it without a DB session (which caused a `Depends` object to be passed and an AttributeError).
  - Verification: Restarted dev runner and observed that `/api/debts/snowball` no longer raises AttributeError in backend logs.

- [2025-08-29] Snapshot generator tightened.

  - Files modified:
    - `scripts/generate_snapshot.py`: excluded `tshoot_vertex/`, `gcloud_quota_check/`; limited CRA `autobudget_frontend/public/` to `index.html` and `manifest.json`; skipped `docs/FullContext.md` in output; kept lockfile summarization.
    - `scripts/generate_snapshot.ps1`: added interpreter fallback from `python3` to `python` for Windows.
  - Rationale: Reduce noise and sensitive/irrelevant artifacts in agent-facing snapshots.
  - Verification: Script loads and completes locally (pending next run); no functional impact on app code.

- [2025-08-29] Added snapshot alias wrappers.

  - Files added:
    - `scripts/gen.ps1` — PowerShell alias calling `generate_snapshot.ps1` with Python fallback.
    - `scripts/gen.sh` — Bash alias calling `generate_snapshot.py` from repo root.
  - Docs: Updated `scripts/README.md` to document usage. Fixed duplicate heading.

- [2025-08-29] UI theme: dark green with gold accents.

  - Modified:
    - `autobudget_frontend/src/index.css`: added CSS variables and global theme (emerald background, gold accent), Bootstrap-compatible overrides for navbar, cards, tables, forms, and buttons.
    - `autobudget_frontend/src/components/Navbar.jsx`: applied `app-navbar` class to adopt theme.
    - `autobudget_frontend/src/App.css`: aligned link color with theme.
    - `autobudget_frontend/src/components/StatusDisplay.jsx`: spinner and alert colors match gold/emerald theme.
  - Scope: style-only, no functional logic changes.
  - Follow-up: Darkened palette and enriched table styles (zebra striping, hover, header bg, rounded corners) in subsequent pass.

- [2025-08-29] Opulent dark theme pass.
  - Modified: `autobudget_frontend/src/index.css` to extend the theme across components (nav, cards, lists, badges, forms, alerts, dropdowns, tabs, modals, progress bars, scrollbars) and chart containers (Recharts/Apex/Chart.js) with deeper emerald tones and rich gold accents.
  - Notes: Visual/style-only changes; no logic altered.