# Failure-to-Rule Conversion Template

> **Purpose:** When an agent hits the same failure twice without new evidence, the
> anti-loop protocol (HARNESS.md S3.2) triggers STOP. This template converts the
> failure into a permanent harness rule so it never recurs.
>
> **Process:** Fill one entry per failure. Once APPROVED, append the Rule Text to
> the Target File and set Status to DEPLOYED.

---

## Template

```
### FTR-NNN

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| Failure ID     | FTR-NNN                                                      |
| Date detected  | YYYY-MM-DD                                                   |
| Agent          | AGENT-01-CLAUDE | AGENT-02-CODEX | AGENT-03-GEMINI           |
| Trigger        | <What failed 2+ times — specific error message or pattern>   |
| Root cause     | <Why the environment allowed it — missing rule, wrong doc>   |
| Evidence       | <Links to log entries, commit hashes, test output>           |
| Security review| <No / Yes - explain if auth, secrets, ACL, network, or destructive ops are touched> |
| Rule text      | <Imperative, verifiable, 1-2 sentences>                      |
| Layer          | SYSTEM (core/) | PROJECT (project/)                          |
| Target file    | <Relative path under .claude/rules/, e.g. project/odoo-ve.md>|
| Verification   | <How to confirm the rule prevents the failure>               |
| Status         | DRAFT | APPROVED | DEPLOYED                                 |
```

### Field definitions

- **Failure ID:** Sequential identifier FTR-001, FTR-002, etc.
- **Date detected:** Date the second occurrence was observed.
- **Agent:** Which agent encountered the repeated failure.
- **Trigger:** The exact error, assertion, or pattern that recurred. Must be specific enough to grep for.
- **Root cause:** The structural gap — missing rule, stale documentation, absent constraint — that permitted the failure.
- **Evidence:** Commit hashes, log entry IDs (e.g., CLAUDE_LOG ENTRADA-043), CI output links.
- **Security review:** Mandatory if the future rule touches authentication, secrets, ACLs, external exposure, cryptography, or destructive operations.
- **Rule text:** The new rule to deploy. Must be imperative ("Use X", "Do not Y") and verifiable by linter, test, or code review.
- **Layer:** SYSTEM if the rule applies to any project using the framework. PROJECT if it is specific to this codebase.
- **Target file:** The rule file where the text will be appended. One rule, one file.
- **Verification:** Concrete check — a test command, a grep pattern, or a review step — that proves the rule is enforced.
- **Status:** DRAFT on creation. APPROVED after human or lead-agent review. DEPLOYED after the rule text is committed to the target file.

---

## Example entry

### FTR-000 (example)

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| Failure ID     | FTR-000                                                      |
| Date detected  | 2026-01-15                                                   |
| Agent          | AGENT-01                                                     |
| Trigger        | Agent used deprecated API method `auth.login_v1()` twice; both calls returned 404. |
| Root cause     | No rule documented that `auth.login_v1()` was removed in v3.0. The agent relied on cached knowledge. |
| Evidence       | Agent log ENTRADA-012, CI output showing 404 on `/api/v1/login` |
| Security review| Yes - authentication flow must not fall back to insecure endpoints. |
| Rule text      | Use `auth.login_v2()` for all authentication. The v1 endpoint was removed in v3.0. |
| Layer          | PROJECT (project/)                                           |
| Target file    | project/auth-rules.md                                        |
| Verification   | `grep -rn 'login_v1' src/` returns zero matches.            |
| Status         | DEPLOYED                                                     |

---

