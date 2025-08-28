# Use Cases (UC-001 .. UC-006)

Concise, human-readable acceptance criteria for core flows.

## UC-001 — Ingest Bills CSV

- Endpoint: POST /ingest/bills
- Accepts: CSV of bills
- Returns: { "ingested_rows": > 0 }
- Notes: Current backend also supports POST /api/ingest-csv using an env var CSV_FILE_PATH.

## UC-002 — Pay Period Summary

- Endpoint: GET /payperiods/{id}/summary
- Returns: { income, fixed, variable, surplus_or_deficit, pots }
- Where pots has keys: Needs, Wants, Savings, Debt.

## UC-003 — Pots Structure Present

- Endpoint: GET /payperiods/{id}/summary
- Returns: object containing `pots` with keys: Needs, Wants, Savings, Debt.

## UC-004 — Debt Snowball

- Endpoint: GET /debts/snowball
- Returns: list ordered by smallest balance, each with `payoff_eta_days`.

## UC-005 — Unlocks

- Endpoint: GET /unlocks
- Returns: array of { action, impact_score, prereqs }.

## UC-006 — Reconciliation

- Endpoint: POST /reconcile
- Accepts: { transactions: [ {date, amount, memo, ...}, ... ] }
- Returns: { matched: [...], unmatched: [...], matched_count: number, unmatched_count: number }

---

Implementation notes

- MVP endpoints implemented (DB-free) in `autobudget_backend/app.py`:
  - POST /ingest/bills, GET /payperiods/{id}/summary, GET /debts/snowball, GET /unlocks, POST /reconcile
  - COMPAT stubs: POST /api/ingest-csv, GET /api/pay-periods, GET /api/pay-periods/{n}/bills, POST /api/bills/{id}/toggle-paid
  - CORS is enabled for CRA (localhost:3000)
