#!/usr/bin/env python3
"""Multiagent Framework V4 — Core Engine.

Agnostic CLI that reads project configuration from an adapter JSON file
and provides status/sync commands for multi-agent governance.

No project-specific references allowed in this module.
All project knowledge comes from the adapter configuration.

Usage:
    python engine.py --config <adapter.json> status
    python engine.py --config <adapter.json> sync-index
    python engine.py --config <adapter.json> sync-index --write
    python engine.py --config <adapter.json> validate <file>
"""

import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

SYNC_START = "<!-- sync_start -->"
SYNC_END = "<!-- sync_end -->"


# ---------------------------------------------------------------------------
# Configuration loader
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_config(config_path: str) -> dict:
    """Load and validate an adapter JSON file."""
    path = Path(config_path)
    if not path.is_file():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    required_keys = ("project_name", "agents", "paths")
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(
            f"Error: adapter missing required keys: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return data


def resolve_path(config: dict, key: str, base: Path) -> Path:
    """Resolve a path from config['paths'][key] relative to project root."""
    raw = config["paths"].get(key, "")
    if not raw:
        return Path("")
    return resolve_repo_path(base, raw)


@lru_cache(maxsize=32)
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


# ---------------------------------------------------------------------------
# Log parser (generic)
# ---------------------------------------------------------------------------


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


def parse_last_entry(log_path: Path, pattern: str) -> dict | None:
    """Extract the highest-numbered entry from a markdown log file."""
    if not log_path.is_file():
        return None

    regex = _get_entry_regex(pattern)

    with open(log_path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    last_match = None
    last_number = -1
    last_line_idx = -1

    for idx in range(len(lines) - 1, -1, -1):
        line = lines[idx]
        m = regex.search(line)
        if m:
            num = int(m.group(1))
            if num > last_number:
                last_number = num
                last_match = line.strip()
                last_line_idx = idx

    if last_match is None:
        return None

    preview_lines = []
    for i in range(last_line_idx + 1, min(last_line_idx + 20, len(lines))):
        stripped = lines[i].strip()
        if stripped and not regex.search(stripped):
            preview_lines.append(stripped)
        if len(preview_lines) >= 3:
            break

    date = ""
    for pl in preview_lines:
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", pl)
        if date_match:
            date = date_match.group(0)
            break

    return {
        "number": last_number,
        "date": date,
        "raw_header": last_match,
        "first_lines": preview_lines,
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
        # Remove "ENTRADA-NNN: " prefix if present to avoid redundancy
        header_cleaned = re.sub(
            r"^ENTRADA-\d+[:\s]*", "", header_cleaned, flags=re.IGNORECASE
        )
        if not header_cleaned:
            header_cleaned = row["header"].lstrip("#").strip()

        row_line = (
            f"| {row['agent']} | {row['last_entry']} | "
            f"{row['date']} | {header_cleaned} |"
        )
        lines.append(row_line)
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


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_status(config: dict, base: Path) -> int:
    """Show last log entry per agent."""
    pattern = config.get("log_entry_pattern", "## ENTRADA-{number}")
    project = config["project_name"]

    print(f"=== {project} — Agent Status ===\n")

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
        print(
            warning,
        )
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
    if matched_cmd:
        resolved = matched_cmd.replace("{file}", filepath)
        if json_output:
            print(
                json.dumps(
                    {
                        "configured": True,
                        "file": filepath,
                        "template": matched_cmd,
                        "command": resolved,
                    },
                ),
            )
        else:
            print(f"  Suggested: {resolved}")
        return 0
    else:
        if json_output:
            print(
                json.dumps(
                    {
                        "configured": False,
                        "file": filepath,
                        "template": None,
                        "command": None,
                    },
                ),
            )
        else:
            print(f"  No validator configured for: {filepath}")
        return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def print_usage() -> None:
    """Print CLI usage."""
    print("Usage: engine.py --config <adapter.json> <command> [args]")
    print()
    print("Commands:")
    print("  status       Show last log entry per agent")
    print("  sync-index   Generate LOG_INDEX update proposal")
    print("  validate <f> Suggest validator for a file")
    print()
    print("Options:")
    print("  --config     Path to adapter JSON file")
    print("  --base       Project root (default: cwd)")
    print("  --write      Allow sync-index to update LOG_INDEX between anchors")
    print("  --json       Emit machine-readable JSON output where supported")
    print("  --router     Run validation_router.py as part of validate")


def main() -> int:
    """Entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print_usage()
        return 0

    config_path = None
    base_dir = None
    command = None
    cmd_args = []
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

    config = load_config(config_path)
    base = Path(base_dir) if base_dir else Path.cwd()

    if command == "status":
        return cmd_status(config, base)
    elif command == "sync-index":
        return cmd_sync_index(config, base, write=write_mode)
    elif command == "validate":
        filepath = cmd_args[0] if cmd_args else None
        return cmd_validate(
            config,
            base,
            filepath,
            json_output=json_mode,
            run_router=router_mode,
            config_path=config_path,
        )
    else:
        print(f"Error: unknown command '{command}'", file=sys.stderr)
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
