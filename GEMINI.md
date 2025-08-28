# Gemini Workspace Instructions: AutoBudget Project

## 1.0 The GEMINI.md File: The Brain of Your Workspace

This file is prepended to your prompts as a system message. Put project-level instructions here.

## 1.1 Project-Level and Hierarchical Instructions

- Place a `GEMINI.md` in the project root for global instructions.
- You can place `GEMINI.md` in subdirectories to scope instructions for those folders (e.g., `tests/GEMINI.md`).

## 2.0 Crafting Effective Custom Instructions

Use markdown sections. Keep instructions concise and focused to save tokens.

Example project instructions (adapted to AutoBudget):

### Persona

You are an expert Python/FastAPI developer specializing in backend financial applications. You write clean, testable, and efficient code.

### Context

This project, "AutoBudget", provides a lightweight FastAPI MVP in `autobudget_backend/app.py` with deterministic services under `autobudget_backend/services/`. A legacy, DB-backed app remains in `autobudget_backend/main.py` for reference. Frontend experiments live under `autobudget_frontend/`.

Preferred routes: `/ingest/bills`, `/payperiods/{id}/summary`, `/debts/snowball`, `/unlocks`, `/reconcile`. Temporary compatibility aliases exist under `/api/*` to avoid churn.

### Rules

- Provide complete, runnable functions. Keep public behavior stable and add concise docstrings when adding utilities.
- Prefer pure functions in `services/`; inject I/O at edges.
- Follow repo docs in `docs/CONVENTIONS.md` (tags, placeholder shapes, COMPAT policy).
- Keep diffs small; avoid mass refactors. Output responses in Markdown.

### Context order (most to least important)

1. `autobudget_backend/app.py` and `autobudget_backend/services/*`
2. `AGENT_GUIDE.md`, `CODE_MAP.md`, `docs/CONVENTIONS.md`
3. `SESSION_LOG.md` (recent decisions), `README.md` (dev/run)
4. `3.api.json`, `docs/*`

## 3.0 Master the .gemini/ignore File

Create `.gemini/ignore` at project root to exclude noisy files and save tokens. Syntax matches `.gitignore`.

## 4.0 Structure Your Workspace Intelligently

Use a clear layout so prompts can reference single files or small sets of files.

## 5.0 Be Explicit with File Context in Prompts

Always include file paths for targeted reads.

## 6.0 Write Token-Efficient Code

Keep code modular, concise, and free of dead code.

## 7.0 Manage Chat History

Use `gemini --clear-history` to start fresh between unrelated tasks.

## 8.0 Use a "Context" Directory for Boilerplate

Create a `/context` directory for reusable schemas and boilerplate.

## 9.0 Leverage Project-Local Settings

You can create `./.gemini/settings.json` to override global settings for this project.

## 10.0 Review and Refine Periodically

Revisit these files to keep context current and token-efficient.
