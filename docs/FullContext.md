# FullContext

Update this file every ~12 edits in ≤150 words. Summarize the current state of the repo, key decisions, and next priorities.

- Current state: [brief summary]
- Key decisions: [list 2-3 recent choices]
- Next priorities: [list 2-3 upcoming tasks]

## vX — 2025-08-27

We shipped a DB‑free FastAPI prototype that satisfies UC‑001..UC‑006 with deterministic logic: CSV ingest counting, pay‑period summaries (pots), debt snowball (balance‑sorted with ETA days), unlock suggestions (impact‑sorted), and memo‑based reconciliation. We added agent docs (CODE_MAP.md, AGENT_GUIDE.md), acceptance docs/tests, SESSION_LOG, and simple indexing tooling. Decisions: favor small, pure service functions and stable heuristics to keep loops fast and tests reproducible; defer persistence and auth until after API shape stabilizes. Risks: placeholder math may diverge from real budgeting rules; no persistence, validation, or auth yet; endpoint drift between legacy (/api/ingest-csv) and new (/ingest/bills) could confuse clients; minimal tests may miss edge cases. Next: run pytest and align routes, wire frontend to these endpoints, add input validation, then introduce a DB with additive migrations and expand tests to cover boundary cases and unhappy paths.
