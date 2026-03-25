#!/usr/bin/env python3
"""Validation router for hooks and standalone validation runs."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROUTER_PATH = Path(__file__).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    return parser.parse_args()


def load_hook_input() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def find_project_root(
    candidate: Path | None = None,
    router_path: Path | None = None,
) -> Path:
    """Find the repo root by walking up until the core engine is found."""
    router_file = (router_path or ROUTER_PATH).resolve()
    search_roots: list[Path] = []

    if candidate is not None:
        resolved_candidate = candidate.resolve()
        candidate_root = (
            resolved_candidate.parent
            if resolved_candidate.is_file()
            else resolved_candidate
        )
        search_roots.append(
            candidate_root,
        )

    search_roots.append(router_file.parent)
    search_roots.append(Path.cwd().resolve())

    for start in search_roots:
        for current in (start, *start.parents):
            if (current / ".multiagent" / "core" / "engine.py").is_file():
                return current

    return router_file.parents[2]


def resolve_project_root(payload: dict) -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        env_candidate = Path(env_root)
        env_candidate_resolved = env_candidate.resolve()
        resolved = find_project_root(env_candidate)
        if (
            resolved == env_candidate_resolved
            or env_candidate_resolved.is_relative_to(resolved)
        ):
            return resolved

    payload_cwd = payload.get("cwd")
    if payload_cwd:
        cwd_candidate = Path(payload_cwd)
        cwd_candidate_resolved = cwd_candidate.resolve()
        resolved = find_project_root(cwd_candidate)
        if (
            resolved == cwd_candidate_resolved
            or cwd_candidate_resolved.is_relative_to(resolved)
        ):
            return resolved

    return find_project_root()


def resolve_config_path(project_root: Path, raw_config: str) -> Path:
    if raw_config:
        config_path = Path(raw_config)
        if not config_path.is_absolute():
            return project_root / config_path
        return config_path

    # Auto-detect: use first .json adapter in standard location
    adapters_dir = project_root / ".multiagent" / "adapters"
    if adapters_dir.is_dir():
        for candidate in sorted(adapters_dir.iterdir()):
            if candidate.suffix == ".json" and candidate.is_file():
                return candidate
    return adapters_dir / "adapter.json"


def extract_file_path(payload: dict) -> str:
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("filePath") or ""
    return str(file_path)


def relativize_path(project_root: Path, file_path: str) -> str:
    try:
        return str(Path(file_path).resolve().relative_to(project_root.resolve()))
    except Exception:
        return file_path


def run_validate(project_root: Path, config_path: Path, file_path: str) -> dict:
    engine_path = project_root / ".multiagent" / "core" / "engine.py"
    if not engine_path.is_file() or not config_path.is_file():
        return {
            "configured": False,
            "file": file_path,
            "template": None,
            "command": None,
        }

    result = subprocess.run(
        [
            sys.executable,
            str(engine_path),
            "--config",
            str(config_path),
            "--base",
            str(project_root),
            "--json",
            "validate",
            file_path,
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
        check=False,
    )

    try:
        return json.loads((result.stdout or "").strip())
    except json.JSONDecodeError:
        return {
            "configured": False,
            "file": file_path,
            "template": None,
            "command": None,
        }


def build_validator_argv(template: str, file_path: str) -> list[str]:
    tokens = shlex.split(template, posix=True)
    return [token.replace("{file}", file_path) for token in tokens]


def run_subprocess(
    argv: list[str],
    cwd: Path,
) -> dict:
    """Execute a process and normalize the result for reporting."""
    command_display = " ".join(argv)

    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False,
            shell=False,
        )
    except FileNotFoundError as exc:
        return {
            "executed": False,
            "command": command_display,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
        }

    return {
        "executed": True,
        "command": command_display,
        "exit_code": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
    }


def execute_validator(
    project_root: Path,
    template: str,
    file_path: str,
) -> dict:
    argv = build_validator_argv(template, file_path)
    return run_subprocess(argv, cwd=project_root)


def run_ruff_check(project_root: Path) -> dict:
    """Run Ruff against the engine and router sources."""
    return run_subprocess(
        [sys.executable, "-m", "ruff", "check", ".multiagent/core"],
        cwd=project_root,
    )


def run_pytest_suite(project_root: Path) -> dict:
    """Run the framework test suite."""
    return run_subprocess(
        [sys.executable, "-m", "pytest", ".multiagent/tests", "-q"],
        cwd=project_root,
    )


def run_configured_validator(
    project_root: Path,
    config_path: Path,
    file_path: str,
) -> dict | None:
    """Resolve and execute the configured validator for a single file."""
    validate_result = run_validate(project_root, config_path, file_path)
    template = validate_result.get("template")
    if not template:
        return None
    return execute_validator(project_root, template, file_path)


def collect_validation_results(
    project_root: Path,
    config_path: Path,
    file_path: str = "",
    *,
    skip_lint: bool = False,
    skip_tests: bool = False,
) -> list[dict]:
    """Collect validation steps for standalone or targeted runs."""
    results: list[dict] = []

    if not skip_lint:
        lint_result = run_ruff_check(project_root)
        lint_result["name"] = "ruff"
        results.append(lint_result)

    if file_path:
        validator_result = run_configured_validator(
            project_root,
            config_path,
            file_path,
        )
        if validator_result is not None:
            validator_result["name"] = "validator"
            validator_result["target"] = file_path
            results.append(validator_result)
    elif not skip_tests:
        test_result = run_pytest_suite(project_root)
        test_result["name"] = "pytest"
        results.append(test_result)

    return results


def compute_exit_code(results: list[dict]) -> int:
    """Return the first failing exit code, or 0 if every step succeeded."""
    for result in results:
        exit_code = result.get("exit_code")
        if exit_code not in (None, 0):
            return int(exit_code)
        if result.get("executed") is False:
            return 1
    return 0


def format_results(label: str, results: list[dict]) -> str:
    """Render collected validation results for hook or CLI output."""
    lines = [f"Validation router: {label}"]
    for result in results:
        name = result.get("name", "step")
        lines.append(f"[{name}] executed={str(result.get('executed', False)).lower()}")
        if result.get("target"):
            lines.append(f"target: {result['target']}")
        if result.get("command"):
            lines.append(f"command: {result['command']}")
        if result.get("exit_code") is not None:
            lines.append(f"exit_code: {result['exit_code']}")
        if result.get("stdout"):
            lines.append("stdout:")
            lines.append(result["stdout"])
        if result.get("stderr"):
            lines.append("stderr:")
            lines.append(result["stderr"])
    return "\n".join(lines)


def emit_hook_output(message: str, executed: bool) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        },
        "executed": executed,
    }
    print(json.dumps(payload))


def main() -> int:
    args = parse_args()
    payload = load_hook_input()
    project_root = resolve_project_root(payload)
    config_path = resolve_config_path(project_root, args.config)
    raw_file_path = args.file or extract_file_path(payload)
    is_hook_payload = bool(payload)

    file_path = (
        relativize_path(project_root, raw_file_path) if raw_file_path else ""
    )
    results = collect_validation_results(
        project_root,
        config_path,
        file_path=file_path,
        skip_lint=args.skip_lint,
        skip_tests=args.skip_tests,
    )
    exit_code = compute_exit_code(results)

    if not results:
        return 0

    message = format_results(file_path or "full-suite", results)
    if is_hook_payload:
        emit_hook_output(
            message,
            executed=all(result.get("executed", False) for result in results),
        )
    else:
        print(message)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
