---
description: Template for creating project-specific adapter rules
paths: ["**/*"]
---

# Project Adapter Template (v4.1)

> Purpose: This file demonstrates how a new project should adopt and extend the
> universal Multi-Agent Framework rules. It acts as the "glue" between universal
> SYSTEM rules and specific project USER needs.

## 1. Framework Principles (Ref: RES-04)

- Context Curation (F-02): Adapters must only provide the minimum necessary
  context to avoid token bloat and cognitive load for the agents.
- Technology Independence (F-07): SYSTEM rules are agnostic. Adapters provide
  the project-specific technology mapping (e.g., Odoo, React, AWS).

## 2. Failure-to-Rule Mechanic (FTR)

When an agent encounters the same failure twice without new evidence, the
anti-loop protocol triggers a STOP. To resolve this structurally:

1. Fill the template: Use `.claude/templates/FAILURE_TO_RULE.md`.
2. Target: Create or update a rule file in `project/` (e.g., `project/odoo-ve.md`).
3. Rule text: Must be imperative, specific, and verifiable.
4. Deployment: Once approved, the rule becomes part of the permanent project harness.

## 3. Verification Criteria (ISC)

Every project rule must be verifiable. Following the Ideal State Criteria (ISC)
pattern from `Docs/sdlc/SPEC_TEMPLATE.md`:

- Criteria must be boolean statements of 8-12 words.
- Method must be explicitly defined: test (automated), inspection (code review),
  or demo (functional verification).

Example:
- Rule: "Use company_ids Many2many for account.account in Odoo 19."
- Verification (test): `grep -r "company_id = fields.Many2one('res.company')" addons/` returns zero matches for new accounts.

## 4. Pattern: Inheriting and Extending Core Rules

To extend a core rule (e.g., `python.md`), create a rule file in `project/` named
`python-[project-name].md`.

### Example: Specific Python Linter
If the CORE rule says "Run a linter", the ADAPTER should specify WHICH linter:
- "For this project, always run `ruff check` and `ruff format` after editing `.py` files."

## 5. Pattern: Overriding Core Rules

If a CORE rule is incompatible with project requirements, explicitly state the
override in the project-specific rule file.

### Example: Indentation
- CORE: "Use 4 spaces for all text files."
- ADAPTER Override: "For this project, use 2 spaces for all .yml and .yaml
  files to comply with external standards."

## 6. Pattern: Adding Project-Only Rules

Unique business logic or specific governance should live only in `project/`.

### Example: Naming Conventions
- "All database tables for this project must be prefixed with ext_."

## 7. Security and Anti-Patterns (What NOT to put here)

- Secrets: Never include API keys, passwords, or tokens. Use environment
  variables or secret managers.
- Credentials: No hardcoded usernames or sensitive identifiers.
- Absolute Local Paths: Avoid paths like C:\Users\.... Use relative
  repository paths.
- Temporary TODOs: Use logs for session-specific notes; rule files are
  for persistent governance.

---
Created by AGENT-03-GEMINI — 2026-03-12
