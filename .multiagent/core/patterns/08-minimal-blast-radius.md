# Pattern: Minimal Blast Radius

> Change only what is necessary. Do not over-engineer.

## When to use

- When fixing a bug (fix the bug, not the surrounding code)
- When adding a feature (add the feature, not "improvements")
- When refactoring (refactor only what was requested)

## Steps

1. **Scope the change** — identify exactly what needs to change and nothing more.
2. **Resist expansion** — do not add error handling for impossible scenarios, abstractions for one-time operations, or features nobody asked for.
3. **Count the files** — if your change touches more than 5 files, reassess scope.
4. **Review the diff** — before committing, verify every changed line is necessary for the stated goal.
5. **Delete the unnecessary** — remove any speculative additions.

## Anti-pattern

- "While I'm here, let me also refactor this function."
- Adding type annotations, docstrings, or comments to code you did not change.
- Creating helper utilities for a pattern used only once.
- Designing for hypothetical future requirements.

## Verification

The diff for a task contains only changes directly related to the task's stated objective. No unrelated cleanups, no speculative features.
