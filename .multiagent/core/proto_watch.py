#!/usr/bin/env python3
"""Standalone wrapper for the real engine watcher.

SPEC-005 turns the proto watcher into an OS-friendly launcher that delegates
validation to `engine.py` while reading the new state files in
`.multiagent/state/`.

Usage:
    python .multiagent/core/proto_watch.py --once
    python .multiagent/core/proto_watch.py --loop
    python .multiagent/core/proto_watch.py --loop 5
    python .multiagent/core/proto_watch.py --status
    python .multiagent/core/proto_watch.py --ack
    python .multiagent/core/proto_watch.py --template systemd
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENGINE = ROOT / ".multiagent" / "core" / "engine.py"
ADAPTER = ROOT / ".multiagent" / "adapters" / "framework-multiagent.json"
WATCH_STATE = ROOT / ".multiagent" / "state" / "watch_state.json"
VALIDATION_STATE = ROOT / ".multiagent" / "state" / "validation_state.json"
TEMPLATE_DIR = ROOT / ".multiagent" / "templates" / "proto_watch"


def _engine_base_command() -> list[str]:
    return [
        sys.executable,
        str(ENGINE),
        "--config",
        str(ADAPTER),
        "--base",
        str(ROOT),
        "watch",
    ]


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {}
    return data


def _run_engine(args: list[str]) -> int:
    command = _engine_base_command() + args
    result = subprocess.run(command, cwd=ROOT, check=False, input="")
    return result.returncode


def _effective_interval_minutes(default: int = 3) -> int:
    state = _read_json(WATCH_STATE)
    return int(state.get("effective_interval_minutes", default) or default)


def _print_template(name: str) -> int:
    mapping = {
        "systemd": TEMPLATE_DIR / "framework-watch.service",
        "schtasks": TEMPLATE_DIR / "install_watch_task.ps1",
        "post-commit": TEMPLATE_DIR / "post-commit.sample",
    }
    template_path = mapping.get(name.lower())
    if template_path is None or not template_path.is_file():
        print(f"Unknown or missing template: {name}", file=sys.stderr)
        return 1
    print(template_path.read_text(encoding="utf-8"))
    return 0


def _print_status() -> int:
    print(f"Adapter: {ADAPTER}")
    print(f"Watch state file: {WATCH_STATE}")
    print(f"Validation state file: {VALIDATION_STATE}")
    return _run_engine(["--status"])


def _loop(interval_override: int | None = None) -> int:
    print("Proto-watch standalone loop active. Ctrl+C to stop.")
    try:
        while True:
            rc = _run_engine(["--once"])
            if rc != 0:
                return rc

            watch_state = _read_json(WATCH_STATE)
            if watch_state.get("state") == "PAUSED":
                print("Watcher paused by deadman policy. Send --ack to resume.")
                return 0

            interval = interval_override or _effective_interval_minutes()
            time.sleep(max(1, interval) * 60)
    except KeyboardInterrupt:
        print("Proto-watch stopped.")
        return 0


def main() -> int:
    args = sys.argv[1:]

    if "--ack" in args:
        return _run_engine(["--ack"])
    if "--status" in args:
        return _print_status()
    if "--once" in args:
        return _run_engine(["--once"])
    if "--template" in args:
        index = args.index("--template")
        template_name = args[index + 1] if index + 1 < len(args) else ""
        return _print_template(template_name)
    if "--loop" in args:
        index = args.index("--loop")
        interval = int(args[index + 1]) if index + 1 < len(args) else None
        return _loop(interval)

    print("Usage:")
    print("  python .multiagent/core/proto_watch.py --once")
    print("  python .multiagent/core/proto_watch.py --loop [minutes]")
    print("  python .multiagent/core/proto_watch.py --status")
    print("  python .multiagent/core/proto_watch.py --ack")
    print(
        "  python .multiagent/core/proto_watch.py "
        "--template systemd|schtasks|post-commit"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
