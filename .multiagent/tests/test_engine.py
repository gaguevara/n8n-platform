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
        "deadman_intervals": {
            "security": 3,
            "implementation": 5,
            "documentation": 7,
        },
        "role_zones": {
            "CLAUDE": ["docs/governance/", "docs/sdlc/", "*.md"],
            "CODEX": [
                ".multiagent/core/",
                ".multiagent/tests/",
                ".multiagent/templates/",
                ".multiagent/hooks/",
                "*.py",
            ],
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


def test_extract_paths_from_text_ignores_commands_and_status_tokens() -> None:
    text = "\n".join(
        [
            "- Evidencia: `python -m ruff check .multiagent/core .multiagent/tests`",
            "- Estado: `READY/QUEUED`",
            "- Directorio: `.multiagent/`",
            "- Referencia: `@docs/reviews/report.md`",
        ]
    )

    assert engine.extract_paths_from_text(text) == ["docs/reviews/report.md"]


def test_extract_affected_paths_ignores_traceability_references() -> None:
    lines = (
        (
            "- **Archivos afectados:** `.multiagent/core/engine.py`, "
            "`docs/logs/CODEX_LOG.md`"
        ),
        "- **Relacionado con:** `SPEC_004_AUTO_VALIDATE_WATCH.md`, `LOG_INDEX.md`",
    )

    assert engine.extract_affected_paths(lines) == [
        ".multiagent/core/engine.py",
        "docs/logs/CODEX_LOG.md",
    ]


def test_verify_files_resolves_unique_basenames_without_false_positives(
    tmp_path: Path,
) -> None:
    entry = engine.LogEntry(
        number=1,
        header="## ENTRADA-001",
        body=(
            "- Se releyeron `CONTEXT.md`, `LOG_INDEX.md`, `engine.py`, `GEMINI_LOG.md`",
            "- Evidencia: `python -m ruff check .multiagent/core .multiagent/tests`",
            "- Estado watcher: `READY/QUEUED`",
        ),
    )
    write_file(tmp_path / "Docs" / "governance" / "CONTEXT.md", "ctx\n")
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "log\n")
    write_file(tmp_path / ".multiagent" / "core" / "engine.py", "print('ok')\n")
    write_file(tmp_path / "logs" / "GEMINI_LOG.md", "## ENTRADA-001\n")

    missing = engine.verify_files(tmp_path, [entry])

    assert missing == []


def test_verify_files_ignores_optional_runtime_watch_paths(tmp_path: Path) -> None:
    entry = engine.LogEntry(
        number=1,
        header="## ENTRADA-001",
        body=("- Runtime watcher: `.watch.pid`, `.multiagent/.watch.status`",),
    )

    missing = engine.verify_files(tmp_path, [entry])

    assert missing == []


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


def test_parse_context_tasks_extracts_dispatch_and_reservation_metadata() -> None:
    context_text = "\n".join(
        [
            "### @CODEX - Implementer",
            (
                "- [ ] @CODEX: Implementar watcher [dispatch:governor] "
                "[type:security] [RESERVED @CODEX 2026-03-25T01:00:00Z]"
            ),
        ]
    )

    tasks = engine.parse_context_tasks(context_text)

    assert tasks[0]["dispatch_level"] == "GOVERNOR"
    assert tasks[0]["task_type"] == "security"
    assert tasks[0]["reservation_agent"] == "CODEX"


def test_check_role_boundaries_supports_role_zones_config() -> None:
    config = build_watch_config()
    config["auto_validate"].pop("role_zones")
    config["auto_validate"]["role_boundaries"] = {
        "CODEX": [".multiagent/adapters/"],
    }

    warnings = engine.check_role_boundaries(
        "CODEX",
        [".multiagent/adapters/framework-multiagent.json"],
        config,
    )

    assert warnings == []


def test_check_role_boundaries_resolves_unique_basenames_in_shared_zone(
    tmp_path: Path,
) -> None:
    config = build_watch_config()
    write_file(tmp_path / "docs" / "logs" / "CODEX_LOG.md", "entry\n")

    warnings = engine.check_role_boundaries(
        "CODEX",
        ["CODEX_LOG.md"],
        config,
        base=tmp_path,
    )

    assert warnings == []


def test_compute_deadman_policy_uses_task_type_threshold() -> None:
    config = build_watch_config()
    validation_state = {
        "agents": {
            "CODEX": {
                "next_task": "Fix security issue",
                "claimed_task": None,
                "task_type": "security",
            }
        }
    }

    policy = engine.compute_deadman_policy(config, validation_state, 4)

    assert policy == ("AWAITING_ACK", 10)


def test_execute_watch_cycle_writes_validation_state_next_task_and_reservation(
    tmp_path: Path,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "\n".join(
            [
                "### @CODEX - Implementer",
                "- [ ] @CODEX: Implementar Fase B [dispatch:auto]",
            ]
        )
        + "\n",
    )

    engine.execute_watch_cycle(str(config_path), tmp_path)
    validation_state = engine.read_json(
        engine.get_watch_paths(tmp_path).validation_state
    )
    context_text = (
        tmp_path / "Docs" / "governance" / "CONTEXT.md"
    ).read_text(encoding="utf-8")

    assert validation_state["agents"]["CODEX"]["next_task"] is not None
    assert validation_state["agents"]["CODEX"]["claimed_task"] is not None
    assert "[RESERVED @CODEX" in context_text


def test_execute_watch_cycle_auto_completes_auto_task_after_validation(
    tmp_path: Path,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    context_path = tmp_path / "Docs" / "governance" / "CONTEXT.md"
    write_file(
        context_path,
        "\n".join(
            [
                "### @CODEX - Implementer",
                "- [ ] @CODEX: Implementar Fase B [dispatch:auto]",
            ]
        )
        + "\n",
    )

    engine.execute_watch_cycle(str(config_path), tmp_path)
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        (
            "## ENTRADA-001\n"
            "- **Archivos afectados:** `.multiagent/core/engine.py`\n"
        ),
    )
    write_file(tmp_path / ".multiagent" / "core" / "engine.py", "print('ok')\n")

    engine.execute_watch_cycle(str(config_path), tmp_path)
    validation_state = engine.read_json(
        engine.get_watch_paths(tmp_path).validation_state
    )

    assert "- [x] @CODEX: Implementar Fase B [dispatch:auto]" in context_path.read_text(
        encoding="utf-8"
    )
    assert validation_state["agents"]["CODEX"]["last_validated"] == 1


def test_execute_watch_cycle_governor_task_waits_for_review(tmp_path: Path) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "\n".join(
            [
                "### @CODEX - Implementer",
                "- [ ] @CODEX: Cambiar motor [dispatch:governor]",
            ]
        )
        + "\n",
    )

    engine.execute_watch_cycle(str(config_path), tmp_path)
    write_file(
        tmp_path / "logs" / "CODEX_LOG.md",
        (
            "## ENTRADA-001\n"
            "- **Archivos afectados:** `.multiagent/core/engine.py`\n"
        ),
    )
    write_file(tmp_path / ".multiagent" / "core" / "engine.py", "print('ok')\n")

    engine.execute_watch_cycle(str(config_path), tmp_path)
    validation_state = engine.read_json(
        engine.get_watch_paths(tmp_path).validation_state
    )

    assert (
        validation_state["agents"]["CODEX"]["status"]
        == "awaiting_governor_dispatch"
    )


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
    watch_state = engine.read_json(engine.get_watch_paths(tmp_path).watch_state)
    validation_state = engine.read_json(
        engine.get_watch_paths(tmp_path).validation_state
    )

    assert state["round_counter"] == 1
    assert saved["auto_validate"]["round_counter"] == 0
    assert saved["auto_validate"]["baseline"]["CODEX"] == 0
    assert watch_state["round_counter"] == 1
    assert watch_state["baseline"]["CODEX"] == 1
    assert validation_state["agents"]["CODEX"]["last_validated"] == 1


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
    watch_state = engine.read_json(engine.get_watch_paths(tmp_path).watch_state)

    assert state["hallucinations"] == [
        "CODEX: hallucination detected -> docs/missing.md"
    ]
    assert saved["auto_validate"]["baseline"]["CODEX"] == 0
    assert watch_state["baseline"]["CODEX"] == 0


def test_execute_watch_cycle_deadman_awaits_then_pauses(tmp_path: Path) -> None:
    config = build_watch_config()
    config["auto_validate"]["deadman_interval"] = 1
    config["auto_validate"]["deadman_intervals"]["implementation"] = 1
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    first = engine.execute_watch_cycle(str(config_path), tmp_path)
    second = engine.execute_watch_cycle(str(config_path), tmp_path)
    third = engine.execute_watch_cycle(str(config_path), tmp_path)
    fourth = engine.execute_watch_cycle(str(config_path), tmp_path)

    assert first["state"] == "ACTIVE"
    assert second["state"] == "AWAITING_ACK"
    assert third["state"] == "DEGRADED"
    assert fourth["state"] == "PAUSED"


def test_watch_ack_clears_pause_on_next_cycle(tmp_path: Path) -> None:
    config = build_watch_config()
    config["auto_validate"]["deadman_interval"] = 2
    config["auto_validate"]["deadman_intervals"]["implementation"] = 2
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(tmp_path / "Docs" / "governance" / "LOG_INDEX.md", "# LOG\n")
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )

    engine.execute_watch_cycle(str(config_path), tmp_path)
    second = engine.execute_watch_cycle(str(config_path), tmp_path)
    third = engine.execute_watch_cycle(str(config_path), tmp_path)
    rc = engine.cmd_watch(str(config_path), tmp_path, ["--ack"])
    fourth = engine.execute_watch_cycle(str(config_path), tmp_path)

    assert second["state"] == "ACTIVE"
    assert third["state"] == "AWAITING_ACK"
    assert rc == 0
    assert fourth["state"] == "ACTIVE"


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


def test_render_watch_status_ignores_stale_pid_without_live_process(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config = build_watch_config()
    config_path = tmp_path / "adapter.json"
    write_json(config_path, config)
    write_file(
        tmp_path / "Docs" / "governance" / "CONTEXT.md",
        "### @CODEX - Implementer\n- [ ] @CODEX: Fase B\n",
    )
    write_file(tmp_path / ".multiagent" / ".watch.pid", "9876\n")
    engine.write_watch_state(
        engine.get_watch_paths(tmp_path),
        {
            "state": "ACTIVE",
            "pid": 9876,
            "last_check": "2026-03-24T18:20:08+00:00",
        },
    )
    monkeypatch.setattr(engine, "is_process_running", lambda pid: False)

    output = engine.render_watch_status(str(config_path), tmp_path)

    assert "Watch state: INACTIVE" in output
    assert "PID:" not in output


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
