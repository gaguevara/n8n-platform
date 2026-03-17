from __future__ import annotations

import importlib.util
from pathlib import Path
from subprocess import CompletedProcess

ENGINE_PATH = Path(__file__).resolve().parents[1] / "core" / "engine.py"
SPEC = importlib.util.spec_from_file_location("multiagent_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(engine)


def build_config() -> dict:
    return {
        "project_name": "test-project",
        "agents": [
            {"id": "CLAUDE", "log": "logs/CLAUDE_LOG.md"},
            {"id": "CODEX", "log": "logs/CODEX_LOG.md"},
        ],
        "paths": {
            "log_index": "Docs/governance/LOG_INDEX.md",
        },
        "validators": {
            ".py": "ruff check {file}",
            ".md": None,
            ".sh": "shellcheck {file}",
            "Dockerfile*": "hadolint {file}",
        },
        "log_entry_pattern": "## ENTRADA-{number}",
    }


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_parse_last_entry_valid(tmp_path: Path) -> None:
    log_path = tmp_path / "CLAUDE_LOG.md"
    write_file(
        log_path,
        "\n".join(
            [
                "# ENTRADA-001",
                "## Fecha: 2026-03-10",
                "Primer evento",
                "",
                "## ENTRADA-004",
                "## Fecha: 2026-03-12",
                "Ultimo evento",
            ],
        ),
    )

    entry = engine.parse_last_entry(log_path, "## ENTRADA-{number}")

    assert entry is not None
    assert entry["number"] == 4
    assert entry["date"] == "2026-03-12"
    assert entry["raw_header"] == "## ENTRADA-004"


def test_parse_last_entry_empty(tmp_path: Path) -> None:
    log_path = tmp_path / "EMPTY.md"
    write_file(log_path, "")

    assert engine.parse_last_entry(log_path, "## ENTRADA-{number}") is None


def test_parse_last_entry_prefers_highest_number_when_log_is_out_of_order(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "CODEX_LOG.md"
    write_file(
        log_path,
        "\n".join(
            [
                "# ENTRADA-047",
                "## Fecha: 2026-03-12",
                "Nueva entrada",
                "",
                "# ENTRADA-043",
                "## Fecha: 2026-03-11",
                "Entrada vieja agregada despues",
            ],
        ),
    )

    entry = engine.parse_last_entry(log_path, "## ENTRADA-{number}")

    assert entry is not None
    assert entry["number"] == 47
    assert entry["date"] == "2026-03-12"


def test_sync_index_generates_table(tmp_path: Path, capsys) -> None:
    config = build_config()
    write_file(
        tmp_path / "logs" / "CLAUDE_LOG.md",
        "## ENTRADA-002\n## Fecha: 2026-03-12\nCambio Claude\n",
    )
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        "# ENTRADA-007\n## Fecha: 2026-03-11\nCambio Codex\n",
    )

    rc = engine.cmd_sync_index(config, tmp_path)
    output = capsys.readouterr().out

    assert rc == 0
    assert "| Agent | Last Entry | Date | Tema |" in output
    assert "| CLAUDE | 2 | 2026-03-12 | ENTRADA-002 |" in output
    assert "| CODEX | 7 | 2026-03-11 | ENTRADA-007 |" in output


def test_validate_python_file(capsys, tmp_path: Path) -> None:
    config = build_config()

    rc = engine.cmd_validate(config, tmp_path, "addons/test_module/models/demo.py")
    output = capsys.readouterr().out

    assert rc == 0
    assert "Suggested: ruff check addons/test_module/models/demo.py" in output


def test_validate_unknown_extension(capsys, tmp_path: Path) -> None:
    config = build_config()

    rc = engine.cmd_validate(config, tmp_path, "README.md")
    output = capsys.readouterr().out

    assert rc == 0
    assert "No validator configured for: README.md" in output


def test_validate_json_output(capsys, tmp_path: Path) -> None:
    config = build_config()

    rc = engine.cmd_validate(
        config,
        tmp_path,
        "addons/test_module/models/demo.py",
        json_output=True,
    )
    output = capsys.readouterr().out

    assert rc == 0
    assert '"configured": true' in output.lower()
    assert '"template": "ruff check {file}"' in output


def test_validate_router_invokes_validation_router(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    config = build_config()
    router_path = tmp_path / ".multiagent" / "core" / "validation_router.py"
    write_file(router_path, "# router stub\n")

    captured: dict[str, object] = {}

    def fake_run(argv, capture_output, text, cwd, check, **kwargs):
        captured["argv"] = argv
        captured["cwd"] = cwd
        return CompletedProcess(argv, 0, stdout="router ok\n", stderr="")

    monkeypatch.setattr(engine.subprocess, "run", fake_run)

    rc = engine.cmd_validate(
        config,
        tmp_path,
        None,
        run_router=True,
        config_path="adapter.json",
    )
    output = capsys.readouterr().out

    assert rc == 0
    assert "router ok" in output
    assert captured["cwd"] == tmp_path
    assert "--config" in captured["argv"]


def test_validate_requires_file_without_router(capsys, tmp_path: Path) -> None:
    config = build_config()

    rc = engine.cmd_validate(config, tmp_path, None)
    output = capsys.readouterr().err

    assert rc == 1
    assert "validate requires a file path" in output


def test_sync_index_write_with_anchors(tmp_path: Path, capsys) -> None:
    config = build_config()
    log_index = tmp_path / "Docs" / "governance" / "LOG_INDEX.md"
    write_file(
        log_index,
        "\n".join(
            [
                "# LOG_INDEX",
                engine.SYNC_START,
                "old table",
                engine.SYNC_END,
                "footer",
            ],
        ),
    )
    write_file(
        tmp_path / "logs" / "CLAUDE_LOG.md",
        "## ENTRADA-003\n## Fecha: 2026-03-12\nCambio Claude\n",
    )
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        "# ENTRADA-004\n## Fecha: 2026-03-12\nCambio Codex\n",
    )

    rc = engine.cmd_sync_index(config, tmp_path, write=True)
    output = capsys.readouterr().out
    content = log_index.read_text(encoding="utf-8")

    assert rc == 0
    assert "Wrote sync-index table to:" in output
    assert "# LOG_INDEX" in content
    assert "footer" in content
    assert "| CLAUDE | 3 | 2026-03-12 | ENTRADA-003 |" in content
    assert "| CODEX | 4 | 2026-03-12 | ENTRADA-004 |" in content


def test_sync_index_write_rejects_path_escape(tmp_path: Path, capsys) -> None:
    config = build_config()
    config["paths"]["log_index"] = "../outside.md"

    rc = engine.cmd_sync_index(config, tmp_path, write=True)
    output = capsys.readouterr().err

    assert rc == 1
    assert "path escapes project base" in output
