#!/usr/bin/env python3
"""Proto-watcher: lightweight simulation of SPEC-004 auto-validate.

Runs engine status, compares against baseline, detects new entries,
verifies mentioned files exist, and optionally auto-commits.

Usage:
    python .multiagent/core/proto_watch.py --once          # single check
    python .multiagent/core/proto_watch.py --loop 3        # every 3 min
    python .multiagent/core/proto_watch.py --status        # show state
    python .multiagent/core/proto_watch.py --ack           # acknowledge deadman

No external dependencies. Python 3.10+ stdlib only.
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent
ADAPTER = ROOT / ".multiagent" / "adapters" / "framework-multiagent.json"
STATE_FILE = ROOT / ".multiagent" / ".watch.state.json"
ACK_FILE = ROOT / ".multiagent" / ".watch.ack"
LOG_DIR = ROOT / "docs" / "logs"

AGENTS = {
    "CLAUDE": LOG_DIR / "CLAUDE_LOG.md",
    "CODEX": LOG_DIR / "CODEX_LOG.md",
    "GEMINI": LOG_DIR / "GEMINI_LOG.md",
}

DEADMAN_INTERVAL = 5  # rounds before asking for ack


def load_state() -> dict:
    """Load persistent state or create default."""
    if STATE_FILE.is_file():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "check": 0,
        "baseline": {},
        "last_check": None,
        "deadman_counter": 0,
        "paused": False,
    }


def save_state(state: dict) -> None:
    """Persist state to JSON."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def count_entries(log_path: Path) -> int:
    """Count ## ENTRADA-N headers in a log file."""
    if not log_path.is_file():
        return 0
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^## ENTRADA-\d+", text, re.MULTILINE))


def get_current_counts() -> dict:
    """Get entry count per agent."""
    return {agent: count_entries(path) for agent, path in AGENTS.items()}


def extract_files_from_entry(log_path: Path, entry_num: int) -> list[str]:
    """Extract file paths mentioned in a specific ENTRADA."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    # Find the specific entry
    pattern = rf"## ENTRADA-{entry_num}\b(.*?)(?=## ENTRADA-|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    # Look for backtick-wrapped file paths
    files = re.findall(r"`([^`]+\.[a-zA-Z]{1,5})`", block)
    # Filter to likely file paths
    return [f for f in files if "/" in f or "\\" in f]


def verify_files(files: list[str]) -> tuple[list[str], list[str]]:
    """Check which mentioned files exist and which don't."""
    found = []
    missing = []
    for f in files:
        p = ROOT / f.replace("\\", "/")
        if p.is_file():
            found.append(f)
        else:
            missing.append(f)
    return found, missing


def check_role_boundaries(agent: str, files: list[str]) -> list[str]:
    """Check if agent modified files outside their zone."""
    zones = {
        "CLAUDE": ["docs/governance/", "docs/sdlc/", "docs/reviews/"],
        "CODEX": [".multiagent/core/", ".multiagent/tests/", ".claude/skills/"],
        "GEMINI": [
            "docs/knowledge/", "docs/architecture/",
            "docs/templates/", "docs/reviews/",
        ],
    }
    shared = [
        "docs/logs/",
        "docs/governance/CONTEXT.md",
        "docs/governance/LOG_INDEX.md",
    ]

    violations = []
    agent_zones = zones.get(agent, [])
    for f in files:
        f_norm = f.replace("\\", "/")
        # Skip shared zones
        if any(f_norm.startswith(s) or f_norm == s for s in shared):
            continue
        # Check if in agent's zone
        in_zone = any(f_norm.startswith(z) for z in agent_zones)
        if not in_zone and f_norm.endswith((".py", ".md", ".json", ".yaml", ".toml")):
            violations.append(f)
    return violations


def _check_deadman(state: dict) -> dict:
    """Increment deadman counter and pause if threshold reached."""
    state["deadman_counter"] = state.get("deadman_counter", 0) + 1
    if state["deadman_counter"] >= DEADMAN_INTERVAL:
        if ACK_FILE.is_file():
            ACK_FILE.unlink()
            state["deadman_counter"] = 0
            print("\n  Human ACK received. Deadman reset.")
        else:
            state["paused"] = True
            print(
                f"\n  DEADMAN SWITCH: {DEADMAN_INTERVAL}"
                " rounds without human ACK."
            )
            print(
                "  Watcher PAUSED. Resume: "
                "python proto_watch.py --ack"
            )
    return state


def run_once(state: dict) -> dict:
    """Execute one validation cycle."""
    now = datetime.now().isoformat(timespec="seconds")
    state["check"] += 1
    state["last_check"] = now
    ronda = state["check"]

    print(f"\n{'='*60}")
    print(f"  CHECK-{ronda:03d}  |  {now}")
    print(f"{'='*60}")

    current = get_current_counts()
    baseline = state.get("baseline", {})

    # Detect new entries
    changes = {}
    for agent, count in current.items():
        prev = baseline.get(agent, 0)
        if count > prev:
            changes[agent] = {"prev": prev, "current": count, "new": count - prev}

    if not changes:
        print("  No new entries detected. All quiet.")
        state["baseline"] = current
        state = _check_deadman(state)
        save_state(state)
        return state

    # Process new entries
    for agent, info in changes.items():
        prev, cur, new = info["prev"], info["current"], info["new"]
        print(f"\n  [{agent}] +{new} entries ({prev} -> {cur})")

        # Verify files mentioned in new entries
        log_path = AGENTS[agent]
        for entry_num in range(info["prev"] + 1, info["current"] + 1):
            files = extract_files_from_entry(log_path, entry_num)
            if files:
                found, missing = verify_files(files)
                if found:
                    print(f"    ENTRADA-{entry_num}: {len(found)} files verified [OK]")
                if missing:
                    n = len(missing)
                    print(f"    ENTRADA-{entry_num}: HALLUCINATION? {n} missing:")
                    for m in missing:
                        print(f"      - {m}")

                # Check role boundaries
                violations = check_role_boundaries(agent, found)
                if violations:
                    print(f"    ROLE_VIOLATION: {agent} modified outside zone:")
                    for v in violations:
                        print(f"      - {v}")

    # Update baseline
    state["baseline"] = current

    # Deadman switch
    state = _check_deadman(state)

    save_state(state)
    return state


def show_status(state: dict) -> None:
    """Display current watcher state."""
    current = get_current_counts()
    baseline = state.get("baseline", {})
    ronda = state.get("check", 0)
    paused = state.get("paused", False)
    deadman = state.get("deadman_counter", 0)
    last = state.get("last_check", "never")

    print("\n  Proto-Watch Status")
    print(f"  {'-'*40}")
    print(f"  Round:    CHECK-{ronda:03d}")
    print(f"  Status:   {'PAUSED (deadman)' if paused else 'ACTIVE'}")
    print(f"  Last:     {last}")
    print(f"  Deadman:  {deadman}/{DEADMAN_INTERVAL} rounds until ACK required")
    print(f"  {'-'*40}")
    print("  Agent     Baseline  Current  Delta")
    for agent in AGENTS:
        b = baseline.get(agent, 0)
        c = current.get(agent, 0)
        delta = c - b
        marker = f" +{delta}" if delta > 0 else ""
        print(f"  {agent:<10} {b:>5}    {c:>5}   {marker}")
    print()


def main() -> int:
    args = sys.argv[1:]
    state = load_state()

    if "--ack" in args:
        ACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACK_FILE.write_text(datetime.now().isoformat(), encoding="utf-8")
        state["paused"] = False
        state["deadman_counter"] = 0
        save_state(state)
        print("  [OK] ACK sent. Watcher resumed.")
        return 0

    if "--status" in args:
        show_status(state)
        return 0

    if state.get("paused"):
        print("  [!] Watcher is PAUSED (deadman switch). Use --ack to resume.")
        return 1

    if "--once" in args:
        run_once(state)
        return 0

    if "--loop" in args:
        idx = args.index("--loop")
        interval = int(args[idx + 1]) if idx + 1 < len(args) else 3
        print(f"  Proto-watch starting. Interval: {interval} min. Ctrl+C to stop.")
        try:
            while True:
                state = load_state()
                if state.get("paused"):
                    print("  [!] PAUSED. Use --ack to resume.")
                    break
                state = run_once(state)
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            print("\n  Watcher stopped by user.")
        return 0

    # Default: show usage
    print("Usage:")
    print("  python proto_watch.py --once          # single check")
    print("  python proto_watch.py --loop 3        # every 3 min")
    print("  python proto_watch.py --status        # show state")
    print("  python proto_watch.py --ack           # acknowledge deadman")
    return 0


if __name__ == "__main__":
    sys.exit(main())
