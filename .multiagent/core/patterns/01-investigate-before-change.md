# Pattern: Investigate Before Change

> Read existing code before modifying it.

## When to use

- Before editing any file in the codebase
- Before proposing a refactor or migration
- Before claiming an API has changed

## Steps

1. **Read the target file** — understand current structure, conventions, dependencies.
2. **Check related files** — imports, tests, callers, inherited classes.
3. **Verify assumptions** — if claiming a framework change (e.g., "Odoo 19 removed X"), confirm against the actual source code or a hallucination registry.
4. **Document findings** — state what you found before proposing changes.

## Anti-pattern

- Editing a file based on memory or assumed structure without reading it first.
- Proposing a rewrite based on a claimed API change without evidence.
- "I think this function does X" instead of "Line 42 shows this function does X."

## Verification

An agent's change log should reference the file and line numbers read before the change was made.
