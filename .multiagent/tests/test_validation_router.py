from __future__ import annotations

import importlib.util
from pathlib import Path

ROUTER_PATH = Path(__file__).resolve().parents[1] / "core" / "validation_router.py"
SPEC = importlib.util.spec_from_file_location("validation_router", ROUTER_PATH)
router = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(router)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_find_project_root_uses_router_location(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "repo"
    router_path = project_root / ".multiagent" / "core" / "validation_router.py"
    engine_path = project_root / ".multiagent" / "core" / "engine.py"
    write_file(router_path, "# router\n")
    write_file(engine_path, "# engine\n")

    resolved = router.find_project_root(router_path=router_path)

    assert resolved == project_root


def build_success_result(command: str) -> dict:
    return {
        "executed": True,
        "command": command,
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
    }


def test_collect_validation_results_runs_lint_and_tests(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[str] = []

    def fake_ruff(project_root: Path) -> dict:
        captured.append(f"ruff:{project_root}")
        return build_success_result("ruff")

    def fake_pytest(project_root: Path) -> dict:
        captured.append(f"pytest:{project_root}")
        return build_success_result("pytest")

    monkeypatch.setattr(router, "run_ruff_check", fake_ruff)
    monkeypatch.setattr(router, "run_pytest_suite", fake_pytest)

    results = router.collect_validation_results(tmp_path, tmp_path / "adapter.json")

    assert [result["name"] for result in results] == ["ruff", "pytest"]
    assert captured == [f"ruff:{tmp_path}", f"pytest:{tmp_path}"]


def test_collect_validation_results_runs_targeted_validator(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[str] = []

    def fake_ruff(project_root: Path) -> dict:
        captured.append("ruff")
        return build_success_result("ruff")

    def fake_validator(
        project_root: Path,
        config_path: Path,
        file_path: str,
    ) -> dict | None:
        captured.append(file_path)
        return {
            "executed": True,
            "command": "python -m py_compile demo.py",
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

    def fail_pytest(project_root: Path) -> dict:
        raise AssertionError("pytest should not run for targeted validation")

    monkeypatch.setattr(router, "run_ruff_check", fake_ruff)
    monkeypatch.setattr(router, "run_configured_validator", fake_validator)
    monkeypatch.setattr(router, "run_pytest_suite", fail_pytest)

    results = router.collect_validation_results(
        tmp_path,
        tmp_path / "adapter.json",
        file_path="demo.py",
    )

    assert [result["name"] for result in results] == ["ruff", "validator"]
    assert captured == ["ruff", "demo.py"]


def test_compute_exit_code_returns_first_failure() -> None:
    results = [
        {"name": "ruff", "executed": True, "exit_code": 0},
        {"name": "pytest", "executed": True, "exit_code": 1},
        {"name": "validator", "executed": True, "exit_code": 0},
    ]

    assert router.compute_exit_code(results) == 1
