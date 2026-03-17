# Pattern: Context Before Action

> Load all relevant context before acting on a task.

## When to use

- At the start of every session (bootstrap protocol)
- Before working on a task assigned by another agent
- When switching between different areas of the codebase

## Steps

1. **Read governance files** — PROJECT_RULES, CONTEXT.md, LOG_INDEX.
2. **Read cross-agent logs** — check what other agents did recently.
3. **Read task-specific context** — spec, related code, tests, knowledge base entries.
4. **Check for blockers** — review LOG_INDEX for active blocks or contradictions.
5. **Only then act** — with full context loaded, execute the task.

## Anti-pattern

- Starting to code immediately without reading the current project state.
- Ignoring other agents' recent work (causing conflicts or redundant effort).
- Working from stale context ("last time I checked, the status was...").

## Verification

The agent's log entry for a task explicitly references the context files read before starting work.
