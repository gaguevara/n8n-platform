# Pattern: Evidence Over Opinion

> Decisions must be backed by executed evidence, not assumptions.

## When to use

- When choosing between implementation approaches
- When claiming a framework or API behaves a certain way
- When resolving disagreements between agents
- When documenting ADRs (Architecture Decision Records)

## Steps

1. **State the claim** — what do you believe is true?
2. **Design the test** — how can you verify it? (run code, read source, execute query)
3. **Execute** — run the test and capture the output.
4. **Record** — include the evidence (command, output, file:line) in your log or ADR.
5. **Decide** — let the evidence drive the decision, not prior assumptions.

## Anti-pattern

- "I think Odoo 19 works this way because version 18 did."
- "This should be fine" without testing.
- Citing documentation without verifying it matches the installed version.

## Verification

Every ADR and architectural decision in the log includes at least one piece of executed evidence (command output, source code reference, or test result).
