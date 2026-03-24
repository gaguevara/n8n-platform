#!/usr/bin/env python3
"""Multiagent Framework V4 - Core Engine.

Agnostic CLI that reads project configuration from an adapter JSON file
and provides status/sync/validate/watch commands for multi-agent governance.

No project-specific references allowed in this module.
All project knowledge comes from the adapter configuration.

Usage:
    python engine.py --config <adapter.json> status
    python engine.py --config <adapter.json> sync-index
    python engine.py --config <adapter.json> sync-index --write
    python engine.py --config <adapter.json> validate <file>
    python engine.py --config <adapter.json> watch --once
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

SYNC_START = "<!-- sync_start -->"
SYNC_END = "<!-- sync_end -->"
WATCH_STATUS_REL = ".multiagent/.watch.status"
WATCH_PID_REL = ".multiagent/.watch.pid"
WATCH_ACK_REL = ".multiagent/.watch.ack"
WATCH_LOCK_REL = ".multiagent/.watch.lock"
SUBAGENT_HEADER_REGEX = re.compile(r"^\s*#+\s*SUB-([A-Z]+)-(\d+)\b")
AGENT_SECTION_REGEX = re.compile(r"^###\s+@([A-Z]+)\s+-")
MAIN_TASK_REGEX = re.compile(r"^\s*-\s+\[([ xX])\]\s+@([A-Z]+):\s*(.*)$")
DEPENDENCY_REGEXES = (
    re.compile(
        r"(?:esperar a(?: que)?|cuando)\s+@?(CLAUDE|CODEX|GEMINI)\b([^\n.]*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"depende de\s+@?(CLAUDE|CODEX|GEMINI)\b([^\n.]*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"tras completar\s+@?(CLAUDE|CODEX|GEMINI)\b([^\n.]*)",
        re.IGNORECASE,
    ),
)
ERROR_TOKENS = ("error", "failed", "failure", "falla", "bloqueado", "blocked")
DEFAULT_ROLE_BOUNDARIES = {
    "CLAUDE": [
        "docs/governance/",
        "docs/sdlc/",
        "docs/reviews/",
        "*.md",
        "SESSION_BOOTSTRAP.md",
    ],
    "CODEX": [
        ".multiagent/core/",
        ".multiagent/tests/",
        ".claude/skills/",
        "*.py",
        "pyproject.toml",
    ],
    "GEMINI": [
        "docs/knowledge/",
        "docs/architecture/",
        "docs/governance/ONBOARDING.md",
        "docs/templates/",
        "docs/reviews/",
    ],
}
DEFAULT_SHARED_ZONES = [
    "docs/logs/",
    "docs/governance/CONTEXT.md",
    "docs/governance/LOG_INDEX.md",
]
DEFAULT_ON_NEW_ENTRY = ["verify_files", "commit", "sync_index", "notify"]


@dataclass(frozen=True)
class WatchPaths:
    """Filesystem paths used by the watcher runtime."""

    status: Path
    pid: Path
    ack: Path
    lock: Path


@dataclass(frozen=True)
class LogEntry:
    """Structured representation of a markdown log entry."""

    number: int
    header: str
    body: tuple[str, ...]
    date: str = ""


@dataclass(frozen=True)
class DependencyState:
    """Dependency queue state for an agent."""

    status: str
    reason: str = ""


def utc_now_iso() -> str:
    """Return the current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    """Create parent directories if they do not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    """Read a JSON file and return an object payload."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in: {path}")
    return data


def with_auto_validate_defaults(config: dict) -> dict:
    """Return config with watcher defaults merged in."""
    merged = json.loads(json.dumps(config))
    auto_validate = merged.setdefault("auto_validate", {})
    auto_validate.setdefault("enabled", True)
    auto_validate.setdefault("interval_minutes", 3)
    auto_validate.setdefault("round_counter", 0)
    auto_validate.setdefault("baseline", {})
    auto_validate.setdefault("on_new_entry", list(DEFAULT_ON_NEW_ENTRY))
    auto_validate.setdefault("hallucination_check", True)
    auto_validate.setdefault("auto_commit", True)
    auto_validate.setdefault("notify", "stdout")
    auto_validate.setdefault("subagent_pattern", "SUB-{AGENT}-{N}")
    auto_validate.setdefault("deadman_interval", 5)
    auto_validate.setdefault("role_boundaries", {})
    auto_validate.setdefault("shared_zones", list(DEFAULT_SHARED_ZONES))

    role_boundaries = auto_validate["role_boundaries"]
    if not isinstance(role_boundaries, dict):
        role_boundaries = {}
        auto_validate["role_boundaries"] = role_boundaries

    for agent_id, zones in DEFAULT_ROLE_BOUNDARIES.items():
        role_boundaries.setdefault(agent_id, list(zones))

    baseline = auto_validate["baseline"]
    if not isinstance(baseline, dict):
        baseline = {}
        auto_validate["baseline"] = baseline

    for agent in merged["agents"]:
        baseline.setdefault(agent["id"], 0)

    return merged


def read_config_data(config_path: str) -> dict:
    """Load adapter data without cache so watch cycles can persist state."""
    path = Path(config_path)
    if not path.is_file():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    data = read_json(path)
    required_keys = ("project_name", "agents", "paths")
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(
            f"Error: adapter missing required keys: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return with_auto_validate_defaults(data)


@lru_cache(maxsize=1)
def load_config(config_path: str) -> dict:
    """Load and validate an adapter JSON file."""
    return read_config_data(config_path)


def write_config_data(config_path: str, data: dict) -> None:
    """Persist adapter data and clear config/path caches."""
    path = Path(config_path)
    ensure_parent(path)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    load_config.cache_clear()
    resolve_repo_path.cache_clear()


def resolve_path(config: dict, key: str, base: Path) -> Path:
    """Resolve a path from config['paths'][key] relative to project root."""
    raw = config["paths"].get(key, "")
    if not raw:
        return Path("")
    return resolve_repo_path(base, raw)


@lru_cache(maxsize=64)
def resolve_repo_path(base: Path, raw_path: str) -> Path:
    """Resolve a config path and keep it inside the project base."""
    path = Path(raw_path)
    candidate = path.resolve() if path.is_absolute() else (base / path).resolve()
    base_resolved = base.resolve()

    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError(
            f"path escapes project base: {raw_path}",
        ) from exc

    return candidate


def get_watch_paths(base: Path) -> WatchPaths:
    """Return runtime file paths used by the watcher."""
    return WatchPaths(
        status=resolve_repo_path(base, WATCH_STATUS_REL),
        pid=resolve_repo_path(base, WATCH_PID_REL),
        ack=resolve_repo_path(base, WATCH_ACK_REL),
        lock=resolve_repo_path(base, WATCH_LOCK_REL),
    )


@lru_cache(maxsize=16)
def _get_entry_regex(pattern: str) -> re.Pattern:
    r"""Build and cache regex from pattern: ## ENTRADA-{number}."""
    normalized = pattern.lstrip("#").strip()
    if pattern.lstrip().startswith("#"):
        regex_str = r"^\s*#+\s*" + re.escape(normalized).replace(
            r"\{number\}", r"(\d+)"
        )
    else:
        regex_str = re.escape(pattern).replace(r"\{number\}", r"(\d+)")
    return re.compile(regex_str)


def _extract_date(lines: list[str]) -> str:
    """Extract the first YYYY-MM-DD date found in the body lines."""
    for line in lines:
        match = re.search(r"\d{4}-\d{2}-\d{2}", line)
        if match:
            return match.group(0)
    return ""


def parse_log_entries(log_path: Path, pattern: str) -> list[LogEntry]:
    """Parse numbered markdown log entries from a file."""
    if not log_path.is_file():
        return []

    regex = _get_entry_regex(pattern)
    entries: list[LogEntry] = []
    current_number: int | None = None
    current_header = ""
    current_body: list[str] = []

    with open(log_path, encoding="utf-8", errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            match = regex.search(line)
            if match:
                if current_number is not None:
                    entries.append(
                        LogEntry(
                            number=current_number,
                            header=current_header,
                            body=tuple(current_body),
                            date=_extract_date(current_body),
                        )
                    )
                current_number = int(match.group(1))
                current_header = line.strip()
                current_body = []
                continue

            if current_number is not None:
                current_body.append(line)

    if current_number is not None:
        entries.append(
            LogEntry(
                number=current_number,
                header=current_header,
                body=tuple(current_body),
                date=_extract_date(current_body),
            )
        )

    return entries


def parse_subagent_entries(log_path: Path) -> list[tuple[str, int]]:
    """Return sub-agent entry headers found in a log file."""
    if not log_path.is_file():
        return []

    subagents: list[tuple[str, int]] = []
    with open(log_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            match = SUBAGENT_HEADER_REGEX.search(line)
            if match:
                subagents.append((match.group(1), int(match.group(2))))
    return subagents


def parse_last_entry(log_path: Path, pattern: str) -> dict | None:
    """Extract the highest-numbered entry from a markdown log file."""
    entries = parse_log_entries(log_path, pattern)
    if not entries:
        return None

    entry = max(entries, key=lambda item: item.number)
    first_lines = [line.strip() for line in entry.body if line.strip()][:3]
    return {
        "number": entry.number,
        "date": entry.date,
        "raw_header": entry.header,
        "first_lines": first_lines,
    }


def collect_sync_rows(config: dict, base: Path, pattern: str) -> list[dict]:
    """Collect last-entry metadata for every configured agent."""
    rows = []

    for agent in config["agents"]:
        agent_id = agent["id"]
        log_rel = agent.get("log", "")

        try:
            log_path = resolve_repo_path(base, log_rel) if log_rel else Path("")
        except ValueError:
            rows.append(
                {
                    "agent": agent_id,
                    "last_entry": "!",
                    "date": "invalid-path",
                    "header": f"(invalid log path: {log_rel})",
                }
            )
            continue

        entry = parse_last_entry(log_path, pattern) if log_path.is_file() else None

        if entry:
            rows.append(
                {
                    "agent": agent_id,
                    "last_entry": entry["number"],
                    "date": entry["date"] or "unknown",
                    "header": entry["raw_header"],
                }
            )
        else:
            rows.append(
                {
                    "agent": agent_id,
                    "last_entry": "?",
                    "date": "?",
                    "header": "(no entries found)",
                }
            )

    return rows


def render_sync_table(rows: list[dict]) -> str:
    """Render sync-index rows as a markdown table."""
    lines = [
        "| Agent | Last Entry | Date | Tema |",
        "|-------|-----------|------|------|",
    ]
    for row in rows:
        header_cleaned = row["header"].lstrip("#").strip()
        header_cleaned = re.sub(
            r"^ENTRADA-\d+[:\s]*", "", header_cleaned, flags=re.IGNORECASE
        )
        if not header_cleaned:
            header_cleaned = row["header"].lstrip("#").strip()

        lines.append(
            f"| {row['agent']} | {row['last_entry']} | "
            f"{row['date']} | {header_cleaned} |"
        )
    return "\n".join(lines)


def resolve_validator_template(config: dict, filepath: str) -> str | None:
    """Return the configured validator template for a given file path."""
    validators = config.get("validators", {})
    fname = os.path.basename(filepath)

    for ext_pattern, cmd in validators.items():
        if cmd is None:
            continue
        if ext_pattern.startswith(".") and filepath.endswith(ext_pattern):
            return cmd

    for ext_pattern, cmd in validators.items():
        if cmd is None:
            continue
        if ext_pattern.endswith("*"):
            prefix = ext_pattern.replace("*", "")
            if fname.startswith(prefix):
                return cmd

    return None


def inject_between_anchors(content: str, new_block: str) -> str | None:
    """Replace content between sync anchors while preserving the rest."""
    pattern = re.compile(
        rf"({re.escape(SYNC_START)}\r?\n)(.*?)(\r?\n{re.escape(SYNC_END)})",
        re.DOTALL,
    )
    if not pattern.search(content):
        return None
    return pattern.sub(rf"\1{new_block}\3", content, count=1)


def get_agent_log_path(config: dict, base: Path, agent_id: str) -> Path:
    """Resolve the log path for a configured agent."""
    for agent in config["agents"]:
        if agent["id"] == agent_id:
            return resolve_repo_path(base, agent.get("log", ""))
    raise KeyError(f"unknown agent id: {agent_id}")


def get_current_counts(config: dict, base: Path, pattern: str) -> dict[str, int]:
    """Return the latest entry number for each agent."""
    counts: dict[str, int] = {}
    for agent in config["agents"]:
        log_path = get_agent_log_path(config, base, agent["id"])
        entry = parse_last_entry(log_path, pattern)
        counts[agent["id"]] = entry["number"] if entry else 0
    return counts


def get_subagent_counts(config: dict, base: Path) -> dict[str, int]:
    """Count sub-agent headers per parent agent log."""
    counts: dict[str, int] = {}
    for agent in config["agents"]:
        log_path = get_agent_log_path(config, base, agent["id"])
        counts[agent["id"]] = len(parse_subagent_entries(log_path))
    return counts


def _looks_like_repo_path(candidate: str) -> bool:
    """Return True when a string is likely a local repository path."""
    if "://" in candidate:
        return False

    cleaned = candidate.strip().rstrip(".,:;)")
    if not cleaned or cleaned.startswith("LOG-ID"):
        return False

    if "/" in cleaned or "\\" in cleaned:
        return True

    if cleaned.startswith("."):
        return True

    if cleaned in {"SESSION_BOOTSTRAP.md", "pyproject.toml"}:
        return True

    return bool(Path(cleaned).suffix)


def extract_paths_from_text(text: str) -> list[str]:
    """Extract likely repo paths from markdown-like text."""
    candidates = re.findall(r"`([^`\n]+)`", text)
    candidates.extend(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))
    paths = {
        candidate.strip().rstrip(".,:;)")
        for candidate in candidates
        if _looks_like_repo_path(candidate)
    }
    return sorted(paths)


def resolve_candidate_path(base: Path, candidate: str) -> Path | None:
    """Resolve a candidate file path and keep it inside the repo."""
    try:
        return resolve_repo_path(base, candidate)
    except ValueError:
        return None


def verify_files(base: Path, entries: list[LogEntry]) -> list[str]:
    """Return missing repo files mentioned in the provided entries."""
    missing: set[str] = set()
    for entry in entries:
        body_text = "\n".join(entry.body)
        for candidate in extract_paths_from_text(body_text):
            resolved = resolve_candidate_path(base, candidate)
            if resolved is None:
                missing.add(candidate)
                continue
            if not resolved.exists():
                missing.add(candidate)
    return sorted(missing)


def build_error_fingerprint(entry: LogEntry) -> str | None:
    """Build a normalized error fingerprint from the entry body."""
    relevant_lines = []
    for line in entry.body:
        lower = line.lower()
        if any(token in lower for token in ERROR_TOKENS):
            normalized = re.sub(r"\d+", "#", lower)
            normalized = re.sub(r"\s+", " ", normalized).strip()
            relevant_lines.append(normalized)
    if not relevant_lines:
        return None
    return "|".join(relevant_lines[:3])


def detect_antiloop(log_path: Path, pattern: str) -> str | None:
    """Return the repeated error fingerprint when the last two errors match."""
    entries = sorted(parse_log_entries(log_path, pattern), key=lambda item: item.number)
    if len(entries) < 2:
        return None

    latest = build_error_fingerprint(entries[-1])
    previous = build_error_fingerprint(entries[-2])
    if latest and previous and latest == previous:
        return latest
    return None


def parse_context_tasks(context_text: str) -> list[dict]:
    """Parse task blocks under the per-agent sections in CONTEXT.md."""
    tasks: list[dict] = []
    current_agent: str | None = None
    current_task: dict | None = None

    for raw_line in context_text.splitlines():
        section_match = AGENT_SECTION_REGEX.match(raw_line)
        if section_match:
            if current_task is not None:
                tasks.append(current_task)
            current_task = None
            current_agent = section_match.group(1).upper()
            continue

        if current_task is not None and (
            raw_line.startswith("## ") or raw_line.strip() == "---"
        ):
            tasks.append(current_task)
            current_task = None
            current_agent = None
            continue

        task_match = MAIN_TASK_REGEX.match(raw_line)
        if current_agent and task_match:
            if current_task is not None:
                tasks.append(current_task)
            current_task = {
                "agent": current_agent,
                "completed": task_match.group(1).lower() == "x",
                "text": [task_match.group(3).strip()],
            }
            continue

        if current_task is not None and raw_line.strip():
            current_task["text"].append(raw_line.strip())

    if current_task is not None:
        tasks.append(current_task)

    for task in tasks:
        task["combined_text"] = " ".join(task["text"]).strip()

    return tasks


def _normalize_dependency_subject(subject: str) -> str:
    """Normalize a dependency clause for fuzzy matching."""
    normalized = subject.lower()
    for token in ("complete", "completa", "completar", "tras", "que"):
        normalized = normalized.replace(token, " ")
    normalized = re.sub(r"[^a-z0-9 ]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_dependency(task_text: str) -> tuple[str, str] | None:
    """Extract a blocker agent and topic from a task block."""
    for regex in DEPENDENCY_REGEXES:
        match = regex.search(task_text)
        if match:
            return match.group(1).upper(), _normalize_dependency_subject(match.group(2))
    return None


def _task_matches_dependency(task_text: str, subject: str) -> bool:
    """Return True when the completed task text satisfies the dependency topic."""
    if not subject:
        return True

    tokens = [token for token in subject.split() if len(token) >= 3]
    if not tokens:
        return True

    haystack = _normalize_dependency_subject(task_text)
    return all(token in haystack for token in tokens)


def check_dependency_queue(
    context_text: str,
    blocked_agents: set[str] | None = None,
) -> dict[str, DependencyState]:
    """Compute READY/QUEUED/BLOCKED state per agent from CONTEXT.md."""
    blocked_agents = blocked_agents or set()
    tasks = parse_context_tasks(context_text)
    by_agent: dict[str, list[dict]] = {}
    for task in tasks:
        by_agent.setdefault(task["agent"], []).append(task)

    queue: dict[str, DependencyState] = {}
    for agent, agent_tasks in by_agent.items():
        if agent in blocked_agents:
            queue[agent] = DependencyState(status="BLOCKED", reason="anti-loop")
            continue

        pending_tasks = [task for task in agent_tasks if not task["completed"]]
        queue[agent] = DependencyState(status="READY")
        for task in pending_tasks:
            dependency = extract_dependency(task["combined_text"])
            if not dependency:
                continue

            blocker, subject = dependency
            blocker_tasks = by_agent.get(blocker, [])
            completed = any(
                item["completed"]
                and _task_matches_dependency(item["combined_text"], subject)
                for item in blocker_tasks
            )
            if not completed:
                queue[agent] = DependencyState(
                    status="QUEUED",
                    reason=f"waiting {blocker} {subject or 'dependency'}".strip(),
                )
                break

    return queue


def matches_zone(rel_path: str, zone: str) -> bool:
    """Return True when a repo-relative path matches a role zone rule."""
    rel_posix = rel_path.replace("\\", "/")
    zone_posix = zone.replace("\\", "/")

    if zone_posix.endswith("/"):
        return rel_posix.startswith(zone_posix)

    if "*" in zone_posix or "?" in zone_posix:
        if "/" not in zone_posix and fnmatch.fnmatch(Path(rel_posix).name, zone_posix):
            return True
        return fnmatch.fnmatch(rel_posix, zone_posix)

    return rel_posix == zone_posix


def check_role_boundaries(agent_id: str, files: list[str], config: dict) -> list[str]:
    """Return role violation warnings for files outside the allowed zones."""
    auto_validate = config.get("auto_validate", {})
    role_boundaries = auto_validate.get("role_boundaries", {})
    shared_zones = auto_validate.get("shared_zones", [])
    zones = role_boundaries.get(agent_id, [])

    warnings: list[str] = []
    for rel_path in sorted(set(path.replace("\\", "/") for path in files)):
        if any(matches_zone(rel_path, zone) for zone in shared_zones):
            continue
        if any(matches_zone(rel_path, zone) for zone in zones):
            continue
        warnings.append(
            f"ROLE_VIOLATION: {agent_id} modified {rel_path} outside assigned zone"
        )
    return warnings


def read_watch_state(paths: WatchPaths) -> dict:
    """Load persisted watcher state from disk."""
    if not paths.status.is_file():
        return {}
    return read_json(paths.status)


def write_watch_state(paths: WatchPaths, state: dict) -> None:
    """Persist watcher state to disk."""
    ensure_parent(paths.status)
    paths.status.write_text(
        json.dumps(state, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_pid_file(paths: WatchPaths, pid: int) -> None:
    """Persist the running watcher PID."""
    ensure_parent(paths.pid)
    paths.pid.write_text(str(pid), encoding="utf-8")


def clear_file(path: Path) -> None:
    """Delete a file if it exists."""
    if path.exists():
        path.unlink()


def has_merge_conflicts(base: Path) -> bool:
    """Return True when the git worktree contains merge conflicts."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=base,
        check=False,
        input="",
    )
    conflict_prefixes = ("UU", "AA", "DD", "AU", "UA", "DU", "UD")
    return any(
        line.startswith(conflict_prefixes) for line in result.stdout.splitlines()
    )


def auto_commit(
    base: Path,
    config: dict,
    agent_id: str,
    entry_number: int,
    round_number: int,
    files: list[str],
) -> bool:
    """Commit the validated files for a watcher round."""
    if has_merge_conflicts(base):
        print("  Watch: merge conflicts detected, auto-commit skipped")
        return False

    cmd_sync_index(config, base, write=True)

    tracked: set[str] = set()
    tracked.update(path for path in files if resolve_candidate_path(base, path))
    tracked.add(config["paths"].get("log_index", ""))

    for agent in config["agents"]:
        if agent["id"] == agent_id:
            tracked.add(agent.get("log", ""))
            break

    tracked_paths = [
        path
        for path in sorted(tracked)
        if path
        and resolve_candidate_path(base, path)
        and resolve_candidate_path(base, path).exists()
    ]
    if not tracked_paths:
        return False

    subprocess.run(
        ["git", "add", "--", *tracked_paths],
        capture_output=True,
        text=True,
        cwd=base,
        check=False,
        input="",
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=base,
        check=False,
        input="",
    )
    if not (staged.stdout or "").strip():
        print("  Watch: no staged changes after git add, auto-commit skipped")
        return False

    message = (
        f"chore(watch): RONDA-{round_number:03d} "
        f"validate {agent_id} ENTRADA-{entry_number:03d}"
    )
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
        cwd=base,
        check=False,
        input="",
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or "git commit failed"
        print(f"  Watch: auto-commit skipped ({detail})")
        return False

    print(f"  Watch: committed round {round_number:03d} for {agent_id}")
    return True


def _write_lock(paths: WatchPaths) -> bool:
    """Create a simple lock file and return False when already locked."""
    if paths.lock.exists():
        return False
    ensure_parent(paths.lock)
    paths.lock.write_text(str(os.getpid()), encoding="utf-8")
    return True


def _read_context_text(config: dict, base: Path) -> str:
    """Read CONTEXT.md when configured."""
    try:
        context_path = resolve_path(config, "context", base)
    except ValueError:
        return ""
    if not context_path.is_file():
        return ""
    return context_path.read_text(encoding="utf-8", errors="replace")


def _format_counts(prefix: str, values: dict[str, int]) -> str:
    """Render a compact KEY=value list."""
    pairs = ", ".join(f"{key}={value}" for key, value in values.items())
    return f"{prefix}: {pairs}"


def execute_watch_cycle(config_path: str, base: Path) -> dict:
    """Execute one validation round and persist watcher state."""
    config = read_config_data(config_path)
    auto_validate = config["auto_validate"]
    pattern = config.get("log_entry_pattern", "## ENTRADA-{number}")
    paths = get_watch_paths(base)

    if not _write_lock(paths):
        return {"state": "LOCKED", "message": "watch lock exists"}

    try:
        previous_state = read_watch_state(paths)
        current_counts = get_current_counts(config, base, pattern)
        baseline = {
            agent["id"]: int(auto_validate["baseline"].get(agent["id"], 0))
            for agent in config["agents"]
        }
        pending = {
            agent_id: max(
                0,
                current_counts.get(agent_id, 0) - baseline.get(agent_id, 0),
            )
            for agent_id in current_counts
        }
        round_number = int(auto_validate.get("round_counter", 0)) + 1
        context_text = _read_context_text(config, base)

        awaiting_ack_round = previous_state.get("awaiting_ack_round")
        ack_present = paths.ack.exists()
        if ack_present:
            clear_file(paths.ack)
            awaiting_ack_round = None

        result_state = "ACTIVE"
        message = ""
        deadman_interval = int(auto_validate.get("deadman_interval", 5) or 0)

        if awaiting_ack_round is not None and round_number > int(awaiting_ack_round):
            result_state = "PAUSED"
            message = f"paused waiting for ack requested at round {awaiting_ack_round}"

        blocked_agents: set[str] = set()
        hallucinations: list[str] = []
        role_violations: list[str] = []
        dependency_queue = check_dependency_queue(context_text, blocked_agents)
        committed = False

        if result_state != "PAUSED":
            for agent_id, count in pending.items():
                if count <= 0:
                    continue

                agent_state = dependency_queue.get(
                    agent_id,
                    DependencyState(status="READY"),
                )
                if agent_state.status != "READY":
                    continue

                log_path = get_agent_log_path(config, base, agent_id)
                new_entries = [
                    entry
                    for entry in parse_log_entries(log_path, pattern)
                    if entry.number > baseline.get(agent_id, 0)
                ]
                if not new_entries:
                    baseline[agent_id] = current_counts.get(agent_id, 0)
                    continue

                fingerprint = detect_antiloop(log_path, pattern)
                if fingerprint:
                    blocked_agents.add(agent_id)
                    dependency_queue[agent_id] = DependencyState(
                        status="BLOCKED",
                        reason="anti-loop",
                    )
                    continue

                if auto_validate.get("hallucination_check", True):
                    missing = verify_files(base, new_entries)
                    if missing:
                        hallucinations.extend(
                            f"{agent_id}: hallucination detected -> {path}"
                            for path in missing
                        )
                        continue

                affected_files = sorted(
                    {
                        path
                        for entry in new_entries
                        for path in extract_paths_from_text("\n".join(entry.body))
                        if resolve_candidate_path(base, path)
                    }
                )
                role_violations.extend(
                    check_role_boundaries(agent_id, affected_files, config)
                )

                should_commit = (
                    auto_validate.get("auto_commit", True)
                    and "commit" in auto_validate.get("on_new_entry", [])
                )
                if should_commit:
                    committed = auto_commit(
                        base,
                        config,
                        agent_id,
                        new_entries[-1].number,
                        round_number,
                        affected_files,
                    ) or committed

                baseline[agent_id] = current_counts.get(agent_id, 0)

            dependency_queue = check_dependency_queue(context_text, blocked_agents)

            if deadman_interval > 0 and awaiting_ack_round is None:
                if round_number % deadman_interval == 0:
                    awaiting_ack_round = round_number
                    result_state = "AWAITING_ACK"
                    message = f"awaiting ack after round {round_number}"

        auto_validate["round_counter"] = round_number
        auto_validate["baseline"] = baseline
        write_config_data(config_path, config)

        state = {
            "state": result_state,
            "project": config["project_name"],
            "round_counter": round_number,
            "interval_minutes": int(auto_validate.get("interval_minutes", 3)),
            "baseline": baseline,
            "current": current_counts,
            "pending": pending,
            "subagents": get_subagent_counts(config, base),
            "dependency_queue": {
                agent: {"status": queue.status, "reason": queue.reason}
                for agent, queue in dependency_queue.items()
            },
            "blocked_agents": sorted(blocked_agents),
            "role_violations": role_violations,
            "hallucinations": hallucinations,
            "awaiting_ack_round": awaiting_ack_round,
            "committed": committed,
            "message": message,
            "last_check": utc_now_iso(),
            "pid": os.getpid(),
        }
        write_watch_state(paths, state)

        print(f"RONDA-{round_number:03d}: state={result_state}")
        print(_format_counts("Baseline", baseline))
        print(_format_counts("Current", current_counts))
        if any(count > 0 for count in pending.values()):
            print(_format_counts("Pending", pending))
        for warning in role_violations:
            print(f"  {warning}")
        for warning in hallucinations:
            print(f"  {warning}")
        for agent, queue in state["dependency_queue"].items():
            reason = f" ({queue['reason']})" if queue["reason"] else ""
            print(f"  {agent}: {queue['status']}{reason}")
        if message:
            print(f"  Watch: {message}")

        return state
    finally:
        clear_file(paths.lock)


def render_watch_status(config_path: str, base: Path) -> str:
    """Return a human-readable watcher status summary."""
    config = read_config_data(config_path)
    auto_validate = config["auto_validate"]
    pattern = config.get("log_entry_pattern", "## ENTRADA-{number}")
    paths = get_watch_paths(base)
    state = read_watch_state(paths)
    current = get_current_counts(config, base, pattern)
    baseline = {
        agent["id"]: int(auto_validate["baseline"].get(agent["id"], 0))
        for agent in config["agents"]
    }
    pending = {
        agent_id: max(0, current.get(agent_id, 0) - baseline.get(agent_id, 0))
        for agent_id in current
    }
    context_text = _read_context_text(config, base)
    blocked_agents = set(state.get("blocked_agents", []))
    queue = check_dependency_queue(context_text, blocked_agents)
    subagents = get_subagent_counts(config, base)

    lines = [
        f"Watch state: {state.get('state', 'INACTIVE')}",
        f"Round: RONDA-{int(auto_validate.get('round_counter', 0)):03d}",
        f"Interval: {int(auto_validate.get('interval_minutes', 3))} min",
    ]
    if state.get("pid"):
        lines.append(f"PID: {state['pid']}")
    if state.get("last_check"):
        lines.append(f"Last check: {state['last_check']}")
    if state.get("message"):
        lines.append(f"Message: {state['message']}")

    lines.append(_format_counts("Baseline", baseline))
    lines.append(_format_counts("Current", current))
    lines.append(_format_counts("Pending", pending))

    if any(subagents.values()):
        lines.append(_format_counts("Subagents", subagents))

    for agent, dep_state in queue.items():
        reason = f" ({dep_state.reason})" if dep_state.reason else ""
        lines.append(f"{agent}: {dep_state.status}{reason}")

    for warning in state.get("role_violations", []):
        lines.append(warning)
    for warning in state.get("hallucinations", []):
        lines.append(warning)

    return "\n".join(lines)


def terminate_process(pid: int, base: Path) -> int:
    """Terminate a background watcher process."""
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
            cwd=base,
            check=False,
            input="",
        )
        return result.returncode

    try:
        os.kill(pid, 15)
    except OSError:
        return 1
    return 0


def cmd_watch(config_path: str, base: Path, args: list[str]) -> int:
    """Handle the watcher command family."""
    config = read_config_data(config_path)
    paths = get_watch_paths(base)

    if "--ack" in args:
        ensure_parent(paths.ack)
        paths.ack.write_text("ACK\n", encoding="utf-8")
        print(f"Watch ack written: {paths.ack}")
        return 0

    if "--status" in args:
        print(render_watch_status(config_path, base))
        return 0

    if "--stop" in args:
        if not paths.pid.is_file():
            print("Watch is not running")
            return 0
        try:
            pid = int(paths.pid.read_text(encoding="utf-8").strip())
        except ValueError:
            print("Watch PID file is invalid", file=sys.stderr)
            return 1

        rc = terminate_process(pid, base)
        if rc == 0:
            clear_file(paths.pid)
            print(f"Watch stopped (PID {pid})")
            return 0

        print(f"Failed to stop watch process {pid}", file=sys.stderr)
        return 1

    if "--daemon" in args:
        engine_path = Path(__file__).resolve()
        command = [
            sys.executable,
            str(engine_path),
            "--config",
            str(Path(config_path).resolve()),
            "--base",
            str(base.resolve()),
            "watch",
        ]
        kwargs = {
            "cwd": base,
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }

        if os.name == "nt":
            kwargs["creationflags"] = (
                getattr(subprocess, "DETACHED_PROCESS", 0)
                | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                | getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        else:
            kwargs["start_new_session"] = True

        process = subprocess.Popen(command, **kwargs)
        write_pid_file(paths, process.pid)
        write_watch_state(
            paths,
            {
                "state": "ACTIVE",
                "pid": process.pid,
                "round_counter": int(config["auto_validate"].get("round_counter", 0)),
                "interval_minutes": int(
                    config["auto_validate"].get("interval_minutes", 3)
                ),
                "last_check": utc_now_iso(),
                "message": "daemon started",
            },
        )
        print(f"Watch daemon started (PID {process.pid})")
        return 0

    if "--once" in args:
        execute_watch_cycle(config_path, base)
        return 0

    interval_seconds = max(
        1,
        int(config["auto_validate"].get("interval_minutes", 3)) * 60,
    )
    write_pid_file(paths, os.getpid())

    try:
        while True:
            start = time.monotonic()
            execute_watch_cycle(config_path, base)
            elapsed = time.monotonic() - start
            current_config = read_config_data(config_path)
            interval_seconds = max(
                1,
                int(current_config["auto_validate"].get("interval_minutes", 3)) * 60,
            )
            time.sleep(max(0.0, interval_seconds - elapsed))
    except KeyboardInterrupt:
        print("Watch interrupted")
        return 0
    finally:
        clear_file(paths.pid)


def cmd_status(config: dict, base: Path) -> int:
    """Show last log entry per agent."""
    pattern = config.get("log_entry_pattern", "## ENTRADA-{number}")
    project = config["project_name"]

    print(f"=== {project} - Agent Status ===\n")

    for agent in config["agents"]:
        agent_id = agent["id"]
        log_rel = agent.get("log", "")
        try:
            log_path = resolve_repo_path(base, log_rel) if log_rel else Path("")
        except ValueError:
            print(f"  {agent_id}: invalid log path ({log_rel})")
            continue

        if not log_path.is_file():
            print(f"  {agent_id}: log not found ({log_rel})")
            continue

        entry = parse_last_entry(log_path, pattern)
        if entry is None:
            print(f"  {agent_id}: no entries found")
            continue

        date_str = f" ({entry['date']})" if entry["date"] else ""
        print(f"  {agent_id}: #{entry['number']}{date_str}")
        print(f"    Header: {entry['raw_header']}")
        for fl in entry["first_lines"][:2]:
            print(f"    > {fl[:100]}")
        print()

    return 0


def cmd_sync_index(config: dict, base: Path, write: bool = False) -> int:
    """Generate a proposed LOG_INDEX update from agent logs."""
    pattern = config.get("log_entry_pattern", "## ENTRADA-{number}")
    try:
        index_path = resolve_path(config, "log_index", base)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("=== Sync Index Proposal ===\n")

    rows = collect_sync_rows(config, base, pattern)
    table = render_sync_table(rows)
    print(table)
    print()

    if not write:
        return 0

    if not index_path.is_file():
        print(f"  Warning: LOG_INDEX not found, cannot write: {index_path}")
        return 0

    original = index_path.read_text(encoding="utf-8")
    updated = inject_between_anchors(original, table)
    if updated is None:
        warning = (
            f"  Warning: anchors {SYNC_START} / {SYNC_END} not found in "
            f"{index_path}; no changes written."
        )
        print(warning)
        return 0

    if updated == original:
        print(f"  LOG_INDEX already up to date: {index_path}")
        return 0

    index_path.write_text(updated, encoding="utf-8")
    print(f"  Wrote sync-index table to: {index_path}")
    return 0


def cmd_validate(
    config: dict,
    base: Path,
    filepath: str | None,
    json_output: bool = False,
    run_router: bool = False,
    config_path: str = "",
) -> int:
    """Suggest the validator command for a given file based on config."""
    if run_router:
        router_path = base / ".multiagent" / "core" / "validation_router.py"
        if not router_path.is_file():
            print(
                f"Error: validation router not found: {router_path}",
                file=sys.stderr,
            )
            return 1

        argv = [
            sys.executable,
            str(router_path),
            "--config",
            config_path,
        ]
        if filepath:
            argv.extend(["--file", filepath])

        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            cwd=base,
            check=False,
            input="",
        )
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        return result.returncode

    if not filepath:
        print("Error: validate requires a file path", file=sys.stderr)
        return 1

    matched_cmd = resolve_validator_template(config, filepath)
    payload = {
        "configured": bool(matched_cmd),
        "file": filepath,
        "template": matched_cmd,
        "command": matched_cmd.replace("{file}", filepath) if matched_cmd else None,
    }
    if matched_cmd:
        if json_output:
            print(json.dumps(payload))
        else:
            print(f"  Suggested: {payload['command']}")
        return 0

    if json_output:
        print(json.dumps(payload))
    else:
        print(f"  No validator configured for: {filepath}")
    return 0


def print_usage() -> None:
    """Print CLI usage."""
    print("Usage: engine.py --config <adapter.json> <command> [args]")
    print()
    print("Commands:")
    print("  status       Show last log entry per agent")
    print("  sync-index   Generate LOG_INDEX update proposal")
    print("  validate <f> Suggest validator for a file")
    print("  watch        Run the auto-validation watcher")
    print()
    print("Options:")
    print("  --config     Path to adapter JSON file")
    print("  --base       Project root (default: cwd)")
    print("  --write      Allow sync-index to update LOG_INDEX between anchors")
    print("  --json       Emit machine-readable JSON output where supported")
    print("  --router     Run validation_router.py as part of validate")
    print("  watch flags  --once --daemon --stop --status --ack")


def main() -> int:
    """Entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print_usage()
        return 0

    config_path = None
    base_dir = None
    command = None
    cmd_args: list[str] = []
    write_mode = False
    json_mode = False
    router_mode = False

    i = 0
    while i < len(args):
        if args[i] == "--config" and i + 1 < len(args):
            config_path = args[i + 1]
            i += 2
        elif args[i] == "--base" and i + 1 < len(args):
            base_dir = args[i + 1]
            i += 2
        elif args[i] == "--write":
            write_mode = True
            i += 1
        elif args[i] == "--json":
            json_mode = True
            i += 1
        elif args[i] == "--router":
            router_mode = True
            i += 1
        elif command is None and not args[i].startswith("-"):
            command = args[i]
            i += 1
        else:
            cmd_args.append(args[i])
            i += 1

    if config_path is None:
        print("Error: --config is required", file=sys.stderr)
        return 1

    base = Path(base_dir) if base_dir else Path.cwd()

    if command == "watch":
        return cmd_watch(config_path, base, cmd_args)

    config = load_config(config_path)

    if command == "status":
        return cmd_status(config, base)
    if command == "sync-index":
        return cmd_sync_index(config, base, write=write_mode)
    if command == "validate":
        filepath = cmd_args[0] if cmd_args else None
        return cmd_validate(
            config,
            base,
            filepath,
            json_output=json_mode,
            run_router=router_mode,
            config_path=config_path,
        )

    print(f"Error: unknown command '{command}'", file=sys.stderr)
    print_usage()
    return 1


if __name__ == "__main__":
    sys.exit(main())
