# Session Log

- [init] seed created; tests scaffolded (2025-08-27)
- [2025-08-27] Created: docs/use_cases.md, tests/test_use_cases.py, autobudget_backend/app.py, autobudget_backend/services/snowball.py, autobudget_backend/services/unlocks.py, autobudget_backend/services/reconcile.py
- [2025-08-27] Added /api/\* COMPAT aliases in app.py; added **init**.py markers to fix imports; updated docs (CODE_MAP, GEMINI, README); deduped .gitignore
- [2025-08-27] Added /api/\* COMPAT aliases in app.py; added **init**.py to backend/services to fix imports; updated docs and guides
- [2025-08-27] Added SQLite database integration. Created `db.py` and `models.py`. Modified `app.py` to use the database for bill ingestion and retrieval.
- [2025-08-27] Updated /debts/snowball, /unlocks, and /reconcile endpoints to use the database.
- [2025-08-27] Fixed "mark as paid" persistence by connecting the /api/bills/{bill_id}/toggle-paid and /api/pay-periods/{pp}/bills endpoints to the database.
- [NEXT] Frontend integration: connect to /bills endpoint and display data.
