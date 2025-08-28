# Conventions

This doc standardizes how we mark placeholders, future work, and TODOs, and defines a minimal placeholder response shape for API stubs.

## Tags (use in code comments)

- TODO: actionable task we intend to complete soon.
- FIXME: known bug/defect that should be fixed.
- FUTURE: planned enhancement or refactor, not scheduled.
- PLACEHOLDER: temporary implementation to keep flows unblocked.
- COMPAT: compatibility shim/alias to avoid churn during migration.
- DEBT: technical debt we acknowledge and will address.

Example:

// TODO: validate input schema
// FUTURE: replace heuristic with ML scoring
// PLACEHOLDER: deterministic data for MVP
// COMPAT: keep /api/\* routes until frontend migrates

## Placeholder API response shape

When returning a placeholder stub, include at least these fields:

- ok: boolean — request succeeded
- placeholder: boolean — indicates stubbed behavior
- since: string (ISO date) — when this placeholder was introduced
- message: string — guidance or next step for clients
- data: optional — any payload returned

Example:

{
"ok": true,
"placeholder": true,
"since": "2025-08-27",
"message": "Use POST /ingest/bills with CSV UploadFile in MVP",
"data": {}
}

## Comment style

Prefer brief, high-signal comments above functions or blocks. Keep them current.

## Removal policy

- COMPAT shims: remove after two minor versions or once clients migrate.
- PLACEHOLDER logic: replace once persistence/real logic lands and is tested.
- TODO/FIXME: convert to tracked issues if not addressed within two sprints.
