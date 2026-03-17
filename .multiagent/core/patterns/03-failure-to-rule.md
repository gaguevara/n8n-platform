# Pattern: Failure-to-Rule (FTR)

> Convert repeated failures into permanent harness rules.

## When to use

- When the same error occurs twice without new evidence
- When the anti-loop protocol triggers a STOP
- When a class of mistakes keeps recurring across sessions

## Steps

1. **DETECT** — the same failure occurs for the second time.
2. **STOP** — do not attempt a third fix. The environment is the problem, not the prompt.
3. **ANALYZE** — identify the root cause: missing rule, stale doc, absent constraint.
4. **TEMPLATE** — fill in `templates/FAILURE_TO_RULE.md` with all fields.
5. **CLASSIFY** — SYSTEM (universal) or PROJECT (specific to this codebase).
6. **DEPLOY** — append the rule text to the target rule file.
7. **VERIFY** — confirm the rule would have prevented the original failure.
8. **LOG** — record the FTR entry in the agent's log.

## Anti-pattern

- Retrying the same approach a third time with minor variations.
- Blaming the agent instead of the environment (missing rule, bad doc).
- Creating a rule so vague it cannot be verified.

## Verification

The FTR template has Status = DEPLOYED and the target rule file contains the new rule text.
