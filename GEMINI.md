# Gemini Workspace Instructions: AutoBudget Project

## 1.0 The GEMINI.md File: The Brain of Your Workspace

This file is prepended to your prompts as a system message. Put project-level instructions here.

## 1.1 Project-Level and Hierarchical Instructions

- Place a `GEMINI.md` in the project root for global instructions.
- You can place `GEMINI.md` in subdirectories to scope instructions for those folders (e.g., `tests/GEMINI.md`).

## 2.0 Crafting Effective Custom Instructions

Use markdown sections. Keep instructions concise and focused to save tokens.

Example project instructions (adapt to AutoBudget):

### Persona

You are an expert Go developer specializing in backend financial applications. You write clean, idiomatic, and highly efficient code.

### Context

This project, "AutoBudget", is a command-line tool written in Go that automatically categorizes financial transactions from CSV files. The main logic is in `main.go`, with utility functions in the `utils/` directory. The primary data structure is the `Transaction` struct defined in `types/transaction.go`.

### Rules

- All Go code must be formatted with `gofmt`.
- Provide complete, runnable functions. Do not use placeholders.
- Prefer the standard library over third-party dependencies unless necessary.
- Include brief, clear comments in generated code.
- Output responses in Markdown.

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
