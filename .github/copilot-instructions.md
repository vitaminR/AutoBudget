# GitHub Copilot Instructions

## Core Instructions

- **Use the Shared Knowledge Base**: This project uses a shared `/docs` directory for all project-wide documentation. Before answering questions or writing code, you **must** consult the relevant files in `/docs`, including:
    - `/docs/CONVENTIONS.md` for coding standards and style.
    - `/docs/CODE_MAP.md` for understanding the repository structure.
    - `/docs/SESSION_LOG.md` for recent project history.

---

## Strict Rules (‼️ FAILURE TO FOLLOW WILL RESULT IN REVERT ‼️)

1.  **Adhere Strictly to Scope:** You **must not** modify any files that are not directly related to the user's request. Your changes must be targeted and minimal.
2.  **No Unattended Global Tools:** You **must not** run code formatters (like Prettier, Black), linters with auto-fix, or other tools that modify files across the project without getting explicit permission from the user first.
3.  **Log All Actions:** You **must** add an entry to `docs/SESSION_LOG.md` for every task you complete. The entry must summarize what you did.

---

## Standard Commands

- **To run the test suite:** Use the command `bash scripts/run_tests.sh`. **Do not** run `pytest` directly.
- **To start the development server:** Use the command `bash scripts/dev.sh &`.

---

## General Agent Guidelines

This file documents minimal onboarding and hygiene for Copilot/Gemini agents.

### Mode selection

- Ask: human requests a single clarification or small change.
- Edit: propose small, reviewable edits (1-2 files); include tests/docs where appropriate.
- Agent: small series of idempotent changes limited in scope; include tests and SESSION_LOG updates.

### Ignore patterns

- Agents and local workflows should ignore local virtual environments and workspace caches.
- Recommended ignores (also present in .gitignore):
  - .venv\*
  - .venv
  - .venv_ci
  - .venv_test

### Token discipline & patch rules

- Keep diffs small and reversible.
- Prefer tests/docs updates over large refactors.
- Avoid secrets, large data blobs, or committing runtime DBs.

### Requirements for code changes

- Any functional change should include a test under `tests/` and a note in `SESSION_LOG.md`.

### Contact

- Add a note to the PR body explaining the purpose and listing verification steps.
