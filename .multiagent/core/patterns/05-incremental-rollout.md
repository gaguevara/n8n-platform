# Pattern: Incremental Rollout

> Make atomic changes and verify each step before proceeding.

## When to use

- When implementing a feature that touches multiple files
- During migrations (version upgrades, API changes)
- When the risk of cascading failures is high

## Steps

1. **Decompose** — break the task into the smallest independently verifiable steps.
2. **Execute one step** — make a single, focused change.
3. **Verify** — run the relevant tests or checks for that step.
4. **Record** — note the result (pass/fail, count delta) in the log.
5. **Proceed or rollback** — if verified, move to the next step. If failed, fix before continuing.
6. **Never batch** — do not accumulate multiple unverified changes.

## Anti-pattern

- "Let me change all 8 files first, then we'll test everything at the end."
- Skipping verification for "trivial" changes.
- Combining a refactor with a feature change in the same step.

## Verification

Each step in the agent's log has its own verification result. No step spans more than 3 files.
