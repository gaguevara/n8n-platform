# Pattern: Test-First Validation

> Run tests before and after every change.

## When to use

- After every code modification (edit, write, refactor)
- Before declaring a task complete
- When verifying a fix for a reported issue

## Steps

1. **Run tests before the change** — establish a baseline. Record pass/fail count.
2. **Make the change** — keep it atomic and focused.
3. **Run tests after the change** — compare against the baseline.
4. **Evaluate delta** — new failures must be investigated before proceeding.
5. **If tests fail twice on the same assertion** — STOP. Apply Failure-to-Rule pattern.

## Anti-pattern

- Making multiple changes before running any tests.
- Declaring "done" without running the test suite.
- Ignoring pre-existing failures ("those were already broken").

## Verification

Agent log entries include test counts before and after the change (e.g., "132/140 before, 135/140 after").
