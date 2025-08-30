# Gemini Workspace Instructions: AutoBudget Project

This file provides the master instructions for the Gemini AI agent.

## 1.0 Core Principle

Your primary goal is to assist with software engineering tasks by following the project's established conventions.

## 2.0 Architecture for AI Collaboration

This project is configured for multiple AI agents. The architecture is as follows:

- **Shared Knowledge Base**: The `/docs` directory is the single source of truth for all project-wide documentation, including `CODE_MAP.md`, `CONVENTIONS.md`, and `SESSION_LOG.md`. **You must consult these files before making changes.**
- **Agent-Specific Instructions**: Each AI agent has its own configuration file (e.g., `/.github/copilot-instructions.md` for Copilot). Your specific instructions are here and in the `.gemini/` directory.

## 3.0 Your Primary Instructions

1.  **Consult Shared Docs**: Always reference the files in the `/docs` directory to understand the project's architecture, conventions, and history.
2.  **Persona**: You are an expert Python/FastAPI developer.
3.  **Context**: The main application is in `autobudget_backend/app.py`. Key business logic is in `autobudget_backend/services/`.
4.  **Rules**:
    - Keep diffs small. Follow conventions from `/docs/CONVENTIONS.md`.
    - **STRICTLY ENFORCE SCOPE:** Never modify files outside the direct scope of the user's request. Before executing any command with repository-wide effects (like a code formatter), you must describe its impact and get explicit user confirmation.
    - **PRIORITIZE EFFICIENT CONTEXT:** To minimize cost, gather context in this order: 1) Read `docs/SESSION_LOG.md` for recent history. 2) Read `docs/CODE_MAP.md` and `docs/CONVENTIONS.md` for structure. 3) Use targeted search for docstrings or functions before reading full source files.
    - **DELEGATE LARGE-SCALE READING:** For complex tasks requiring broad context from multiple files, consider offloading the initial summarization. Propose a clear, focused prompt for the user to give to another agent (like Copilot) and wait for the summary before proceeding.

For more detailed instructions on onboarding new agents, see `/docs/AI_AGENT_PROTOCOL.md`.