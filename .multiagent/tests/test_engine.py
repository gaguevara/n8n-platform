from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from subprocess import CompletedProcess

ENGINE_PATH = Path(__file__).resolve().parents[1] / "core" / "engine.py"
SPEC = importlib.util.spec_from_file_location("multiagent_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = engine
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


def build_watch_config() -> dict:
    config = build_config()
    config["agents"].append({"id": "GEMINI", "log": "logs/GEMINI_LOG.md"})
    config["paths"].update(
        {
            "context": "Docs/governance/CONTEXT.md",
            "project_rules": "Docs/governance/PROJECT_RULES.md",
            "agent_roles": "Docs/governance/AGENT_ROLES.md",
        }
    )
    config["auto_validate"] = {
        "enabled": True,
        "interval_minutes": 3,
        "round_counter": 0,
        "baseline": {"CLAUDE": 0, "CODEX": 0, "GEMINI": 0},
        "on_new_entry": ["verify_files", "sync_index", "notify"],
        "hallucination_check": True,
        "auto_commit": False,
        "notify": "stdout",
        "subagent_pattern": "SUB-{AGENT}-{N}",
        "deadman_interval": 5,
        "role_boundaries": {
            "CLAUDE": ["docs/governance/", "docs/sdlc/", "*.md"],
            "CODEX": [".multiagent/core/", ".multiagent/tests/", "*.py"],
            "GEMINI": ["docs/reviews/", "docs/architecture/"],
        },
        "shared_zones": [
            "docs/logs/",
            "docs/governance/CONTEXT.md",
            "docs/governance/LOG_INDEX.md",
        ],
    }
    return config


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(engine.json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def test_parse_subagent_entries_detects_headers(tmp_path: Path) -> None:
    log_path = tmp_path / "CLAUDE_LOG.md"
    write_file(
        log_path,
        "\n".join(
            [
                "## ENTRADA-001",
                "main entry",
                "## SUB-CLAUDE-1",
                "sub work",
                "## SUB-CLAUDE-2",
                "more sub work",
            ],
        ),
    )

    assert engine.parse_subagent_entries(log_path) == [("CLAUDE", 1), ("CLAUDE", 2)]


def test_verify_files_reports_missing_path(tmp_path: Path) -> None:
    entry = engine.LogEntry(
        number=1,
        header="## ENTRADA-001",
        body=("- **Archivos afectados:** `docs/missing.md`, `docs/existing.md`",),
    )
    write_file(tmp_path / "docs" / "existing.md", "ok")

    missing = engine.verify_files(tmp_path, [entry])

    assert missing == ["docs/missing.md"]


def test_detect_antiloop_when_same_error_repeats(tmp_path: Path) -> None:
    log_path = tmp_path / "CODEX_LOG.md"
    write_file(
        log_path,
        "\n".join(
            [
                "## ENTRADA-001",
                "Error: same failure on step 12",
                "## ENTRADA-002",
                "Error: same failure on step 42",
            ],
        ),
    )

    fingerprint = engine.detect_antiloop(log_path, "## ENTRADA-{number}")

    assert fingerprint is not None
    assert "same failure" in fingerprint


def test_check_role_boundaries_flags_violation_and_allows_shared_zone() -> None:
    config = build_watch_config()

    warnings = engine.check_role_boundaries(
        "CODEX",
        [
            ".multiagent/core/engine.py",
            "docs/governance/PROJECT_RULES.md",
            "docs/governance/CONTEXT.md",
        ],
        config,
    )

    assert warnings == [
        (
            "ROLE_VIOLATION: CODEX modified "
            "docs/governance/PROJECT_RULES.md outside assigned zone"
        )
    ]


def test_check_dependency_queue_returns_queued_until_blocker_checked() -> None:
    context_text = "\n".join(
        [
            "### @GEMINI - Researcher",
            "- [ ] @GEMINI: Fase A de SPEC-004",
            "### @CODEX - Implementer",
            "- [ ] @CODEX: Fase B de SPEC-004",
            "  Nota: Fase B inicia cuando Gemini complete Fase A",
        ],
    )

    queue = engine.check_dependency_queue(context_text)

    assert queue["CODEX"].status == "QUEUED"
    assert "GEMINI" in queue["CODEX"].reason


def test_check_dependency_queue_returns_ready_when_blocker_is_checked() -> None:
    context_text = "\n".join(
        [
            "### @GEMINI - Researcher",
            "- [x] @GEMINI: Fase A de SPEC-004",
            "### @CODEX - Implementer",
            "- [ ] @CODEX: Fase B de SPEC-004",
            "  Nota: Fase B inicia cuando Gemini complete Fase A",
        ],
    )

    queue = engine.check_dependency_queue(context_text)

    assert queue["CODEX"].status == "READY"


def test_parse_context_tasks_stops_before_non_agent_sections() -> None:
    context_text = "\n".join(
        [
            "### @CLAUDE - Governor",
            "- [ ] @CLAUDE: Fase C",
            "  Nota: cuando CODEX complete Fase B",
            "---",
            "## Riesgos tecnicos abiertos",
            "| Riesgo | Impacto |",
        ],
    )

    tasks = engine.parse_context_tasks(context_text)

    assert len(tasks) == 1
    assert "Riesgos tecnicos abiertos" not in tasks[0]["combined_text"]


def test_execute_watch_cycle_updates_round_and_baseline(
    tmp_path: Path,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        (
            "## ENTRADA-001\n"
            "## Fecha: 2026-03-24\n"
            "- **Archivos afectados:** `.multiagent/core/engine.py`\n"
        ),
    )
    write_file(tmp_path / ".multiagent" / "core" / "engine.py", "print('ok')\n")
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    state = engine.execute_watch_cycle(str(config_path), tmp_path)
    saved = engine.read_json(config_path)

    assert state["round_counter"] == 1
    assert saved["auto_validate"]["round_counter"] == 1
    assert saved["auto_validate"]["baseline"]["CODEX"] == 1


def test_execute_watch_cycle_detects_hallucination_and_keeps_baseline(
    tmp_path: Path,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        "## ENTRADA-001\n- **Archivos afectados:** `docs/missing.md`\n",
    )
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    state = engine.execute_watch_cycle(str(config_path), tmp_path)
    saved = engine.read_json(config_path)

    assert state["hallucinations"] == [
        "CODEX: hallucination detected -> docs/missing.md"
    ]
    assert saved["auto_validate"]["baseline"]["CODEX"] == 0


def test_execute_watch_cycle_deadman_awaits_then_pauses(tmp_path: Path) -> None:
    config = build_watch_config()
    config["auto_validate"]["deadman_interval"] = 1
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    first = engine.execute_watch_cycle(str(config_path), tmp_path)
    second = engine.execute_watch_cycle(str(config_path), tmp_path)

    assert first["state"] == "AWAITING_ACK"
    assert second["state"] == "PAUSED"


def test_watch_ack_clears_pause_on_next_cycle(tmp_path: Path) -> None:
    config = build_watch_config()
    config["auto_validate"]["deadman_interval"] = 2
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    engine.execute_watch_cycle(str(config_path), tmp_path)
    second = engine.execute_watch_cycle(str(config_path), tmp_path)
    rc = engine.cmd_watch(str(config_path), tmp_path, ["--ack"])
    third = engine.execute_watch_cycle(str(config_path), tmp_path)

    assert second["state"] == "AWAITING_ACK"
    assert rc == 0
    assert third["state"] == "ACTIVE"


def test_render_watch_status_includes_queue_and_round(tmp_path: Path) -> None:
    config = build_watch_config()
    config["auto_validate"]["round_counter"] = 3
    config["auto_validate"]["baseline"]["GEMINI"] = 0
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "\n".join(
            [
                "### @GEMINI - Researcher",
                "- [ ] @GEMINI: Fase A de SPEC-004",
                "### @CODEX - Implementer",
                "- [ ] @CODEX: Fase B de SPEC-004",
                "  Nota: Fase B inicia cuando Gemini complete Fase A",
            ],
        ),
    )

    output = engine.render_watch_status(str(config_path), tmp_path)

    assert "RONDA-003" in output
    assert "CODEX: QUEUED" in output


def test_auto_commit_invokes_git_with_safe_paths(tmp_path: Path, monkeypatch) -> None:
    config = build_watch_config()
    write_file(tmp_path / "logs" / "CODEX_LOG.md", "entry\n")
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(tmp_path / ".multiagent" / "core" / "engine.py", "print('ok')\n")

    calls: list[list[str]] = []

    def fake_run(argv, capture_output, text, cwd, check, **kwargs):
        calls.append(argv)
        if argv[:3] == ["git", "status", "--porcelain"]:
            return CompletedProcess(argv, 0, stdout="", stderr="")
        if argv[:4] == ["git", "diff", "--cached", "--name-only"]:
            return CompletedProcess(
                argv,
                0,
                stdout=".multiagent/core/engine.py\n",
                stderr="",
            )
        return CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(engine.subprocess, "run", fake_run)
    monkeypatch.setattr(engine, "cmd_sync_index", lambda config, base, write=False: 0)

    committed = engine.auto_commit(
        tmp_path,
        config,
        "CODEX",
        7,
        4,
        [".multiagent/core/engine.py"],
    )

    assert committed is True
    assert [
        "git",
        "commit",
        "-m",
        "chore(watch): RONDA-004 validate CODEX ENTRADA-007",
    ] in calls


def test_cmd_watch_daemon_spawns_subprocess(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)

    class DummyProcess:
        pid = 4321

    monkeypatch.setattr(
        engine.subprocess,
        "Popen",
        lambda *args, **kwargs: DummyProcess(),
    )

    rc = engine.cmd_watch(str(config_path), tmp_path, ["--daemon"])
    output = capsys.readouterr().out

    assert rc == 0
    assert "PID 4321" in output
