# AI Agent Protocol & Best Practices

## 1.0 Introduction

This document outlines the architecture and best practices for using multiple AI agents (like Google's Gemini, GitHub Copilot, etc.) on this project. Following this protocol ensures that all agents work efficiently, consistently, and without conflict.

## 2.0 Core Architecture

The key to successful multi-agent collaboration is a clear separation between shared project knowledge and agent-specific configurations.

### 2.1 Shared Knowledge Base: `/docs`

The `/docs` directory is the **single source of truth** for all project-wide documentation. All agents should be instructed to consult the files within this directory before making any changes.

Key files include:
- `CONVENTIONS.md`: The rules for coding style, naming, and patterns.
- `CODE_MAP.md`: A high-level overview of the repository structure and the purpose of key files/directories.
- `SESSION_LOG.md`: A log of significant changes and tasks completed.

### 2.2 Agent-Specific Configuration

Each agent is configured in its own conventional location. The primary instruction file for each agent **must** include a directive to use the shared `/docs` directory.

- **Google Gemini:**
    - **Primary Config:** The root `GEMINI.md` file. This is loaded first and acts as a master index.
    - **Detailed Config:** The `.gemini/` directory can be used for more detailed or specialized instructions.

- **GitHub Copilot:**
    - **Primary Config:** The `.github/copilot-instructions.md` file.

## 3.0 Onboarding a New AI Agent

To add a new agent to this project, follow these steps:

1.  **Identify Configuration:** Determine where the new agent looks for its repository-specific instructions.
2.  **Create Instruction File:** Create the necessary instruction file in its conventional location (e.g., `.some-agent/instructions.md`).
3.  **Point to Shared Docs:** Add a clear, explicit instruction at the top of the agent's configuration file, directing it to use the `/docs` directory as the source of truth for project context, conventions, and history.
4.  **Verify:** Create a test prompt that requires the agent to read its configuration and then access information from the `/docs` directory to answer a question. This verifies that the agent can follow the new architecture. (See the prompt used for the initial Copilot verification for an example).

## 4.0 Conclusion

This federated architecture allows each agent to use its native configuration while ensuring all agents operate from the same shared understanding of the project. This prevents conflicting work and improves the quality and consistency of AI-assisted development.
