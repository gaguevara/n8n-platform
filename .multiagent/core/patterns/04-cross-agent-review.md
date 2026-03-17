# Pattern: Cross-Agent Review

> Every significant change is reviewed by a different agent than the one who made it.

## When to use

- After completing a feature or fix (before merging/closing)
- For security-sensitive changes (ACLs, secrets, auth, external APIs)
- When a task involves multiple files or architectural decisions

## Steps

1. **Author agent** completes the change and registers it in their log.
2. **Reviewer agent** reads the change (diff, files, tests).
3. **Reviewer** checks against applicable rules (core/ + project/).
4. **Reviewer** issues a verdict: APPROVED, APPROVED WITH COMMENTS, or REJECTED.
5. **If REJECTED** — author agent addresses findings. Reviewer re-checks.
6. **Log** — both agents record the review in their respective logs.

## Anti-pattern

- Self-reviewing your own work ("I checked it, looks fine").
- Rubber-stamping without reading the actual changes.
- Reviewing only the description instead of the code diff.

## Verification

The reviewer's log entry contains specific file references and a verdict for each reviewed change.
