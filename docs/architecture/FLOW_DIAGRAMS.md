# FLOW_DIAGRAMS.md — Diagramas de Flujo del Framework

> **Versión:** 1.0
> **Fecha:** 2026-03-16
> **Autor:** Claude Opus 4.6 (Governor / Architect)
> **Formato:** Mermaid (renderizable en GitHub, GitLab, VS Code)
>
> Dos perspectivas: **Implementación** (instalar el framework en un proyecto)
> y **Uso** (operar con el framework ya instalado).

---

## PARTE A — IMPLEMENTACIÓN (Instalar el framework en un proyecto nuevo)

### A1. Flujo maestro de implementación

```mermaid
flowchart TD
    START([🚀 Proyecto nuevo o existente]) --> CHECK{¿Tiene archivos\npre-existentes?}

    CHECK -->|No - Greenfield| EXTRACT[Extraer framework\nmultiagent-framework-v4.1.zip]
    CHECK -->|Sí - Brownfield| PRESERVE[Inventariar archivos\nexistentes antes de tocar]

    PRESERVE --> ARCHIVE[Mover conflictos a\narchive/ si es necesario]
    ARCHIVE --> EXTRACT

    EXTRACT --> CLEAN[Limpiar rutas basura\ncon llaves literales]
    CLEAN --> ADAPTER[Crear adapter real\n.multiagent/adapters/proyecto.json]

    ADAPTER --> ADAPTER_CONFIG[Configurar en adapter:\n• project_name\n• agents con rutas de log\n• paths: log_index, context\n• validators por extensión\n• log_entry_pattern]

    ADAPTER_CONFIG --> VERIFY_ENGINE[Verificar engine\npython engine.py --config adapter.json status]
    VERIFY_ENGINE --> ENGINE_OK{¿Engine\nresponde?}

    ENGINE_OK -->|No| FIX_ADAPTER[Revisar rutas\nen adapter JSON]
    FIX_ADAPTER --> VERIFY_ENGINE

    ENGINE_OK -->|Sí| TESTS[Ejecutar tests\npytest .multiagent/tests/ -q]
    TESTS --> TESTS_OK{¿9/9 pass?}

    TESTS_OK -->|No| FIX_ENGINE[Revisar Python 3.12+\ny dependencias]
    FIX_ENGINE --> TESTS

    TESTS_OK -->|Sí| GIT{¿Git\ninicializado?}

    GIT -->|No| GIT_INIT[git init\ncrear .gitignore\nconfigurar identidad]
    GIT -->|Sí| GITIGNORE[Verificar .gitignore\nincluye zip, .env, __pycache__]

    GIT_INIT --> GOVERNANCE
    GITIGNORE --> GOVERNANCE

    GOVERNANCE[Activar gobernanza viva] --> GOV_STEPS[1. Completar PROJECT_RULES.md §2-§3\n2. Activar CONTEXT.md con estado real\n3. Crear logs iniciales por agente\n4. Actualizar LOG_INDEX.md]

    GOV_STEPS --> HOOKS{¿Activar\npre-commit?}

    HOOKS -->|Sí| PRECOMMIT[pip install pre-commit\npre-commit install\ngenerar .secrets.baseline]
    HOOKS -->|No / Después| SKIP_HOOKS[Documentar decisión\nen CONTEXT.md]

    PRECOMMIT --> COMMIT
    SKIP_HOOKS --> COMMIT

    COMMIT[Initial commit\nfeat: install multiagent framework] --> DONE([✅ Framework instalado\ny operativo])

    style START fill:#e1f5fe
    style DONE fill:#c8e6c9
    style PRESERVE fill:#fff3e0
    style ARCHIVE fill:#fff3e0
```

### A2. Estructura de archivos resultante

```mermaid
graph LR
    subgraph "Capa 1 — Entry Point"
        CLAUDE[CLAUDE.md]
        BOOTSTRAP[SESSION_BOOTSTRAP.md]
        AGENTS[AGENTS.md]
    end

    subgraph "Capa 2 — Core Engine"
        ENGINE[engine.py]
        ROUTER[validation_router.py]
        PATTERNS[patterns/ x8]
        RULES[rules/ x7]
        ADAPTERS[adapters/*.json]
        SCHEMAS[schemas/]
        TEMPLATES[templates/]
        HOOKS_DIR[hooks/]
        TESTS_DIR[tests/]
    end

    subgraph "Capa 3 — Gobernanza"
        PROJ_RULES[PROJECT_RULES.md]
        CONTEXT[CONTEXT.md]
        ROLES[AGENT_ROLES.md]
        OVERLAYS[*_OVERLAY.md x3]
        LOG_IDX[LOG_INDEX.md]
        AI_GOV[AI_GOVERNANCE.md]
    end

    subgraph "Capa 4 — Knowledge & Ops"
        FW_DESIGN[FRAMEWORK_DESIGN.md]
        DESIGN_P[DESIGN_PRINCIPLES.md]
        HARNESS[HARNESS.md]
        SDLC[SDLC_WORKFLOW.md]
        SKILLS_DOC[SKILLS.md]
        LOGS[logs/ x3 agentes]
    end

    subgraph "Capa 5 — Agent Interface"
        CL_SKILLS[.claude/skills/ x7]
        CL_RULES[.claude/rules/]
        GEMINI_MD[GEMINI.md]
        CODEX_MD[codex.md]
    end

    subgraph "Capa 6 — Preservación"
        ARCHIVE[archive/]
    end

    CLAUDE --> BOOTSTRAP
    BOOTSTRAP --> PROJ_RULES
    ENGINE --> ADAPTERS
    ROUTER --> ENGINE
```

---

## PARTE B — USO (Operar con el framework ya instalado)

### B1. Ciclo de vida de una sesión de agente

```mermaid
flowchart TD
    AGENT_START([Agente inicia sesión]) --> READ_ENTRY[Leer CLAUDE.md / AGENTS.md\n→ Redirige a SESSION_BOOTSTRAP.md]

    READ_ENTRY --> BOOTSTRAP_SEQ[Secuencia de Bootstrap]

    subgraph BOOTSTRAP["📋 Bootstrap obligatorio"]
        direction TB
        B1[1. Leer PROJECT_RULES.md — SSOT]
        B2[2. Leer CONTEXT.md — estado vivo]
        B3[3. Leer OVERLAY propio — instrucciones específicas]
        B4[4. Leer LOG_INDEX.md — trazabilidad]
        B5[5. Revisar logs recientes de otros agentes]
        B6[6. Si toca código → DESIGN_PRINCIPLES.md]
        B7[7. Si hay spec → SPEC_nombre.md]

        B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7
    end

    BOOTSTRAP_SEQ --> BOOTSTRAP
    BOOTSTRAP --> EVAL_TASK{Evaluar tipo\nde tarea}

    EVAL_TASK -->|A: Puntual y clara| EXEC_DIRECT[Ejecutar directamente]
    EVAL_TASK -->|B: Con contexto| CONTINUE[Continuar sobre base existente]
    EVAL_TASK -->|C: Greenfield| BUILD_CTX[Construir contexto primero]
    EVAL_TASK -->|D: Alto riesgo| PLAN[Plan + review cruzado\nobligatorio]

    EXEC_DIRECT --> WORK
    CONTINUE --> WORK
    BUILD_CTX --> WORK
    PLAN --> WORK

    WORK[Ejecutar tarea] --> POST_CHANGE{¿Cambió\ncódigo?}

    POST_CHANGE -->|Sí| VALIDATE[Skill: validate-change\nlint → test → scan]
    POST_CHANGE -->|No| CLOSE

    VALIDATE --> VAL_OK{¿Pasa\nvalidación?}
    VAL_OK -->|Sí| CLOSE
    VAL_OK -->|No, 1er intento| FIX[Corregir y reintentar]
    FIX --> VALIDATE
    VAL_OK -->|No, 2do intento| ANTILOOP[⛔ STOP — Anti-loop\nSkill: failure-to-rule]

    ANTILOOP --> FTR[Generar FTR-NNN\nNueva regla para el harness]
    FTR --> CLOSE

    subgraph CLOSE["📝 Cierre de sesión"]
        direction TB
        C1[1. Registrar en docs/logs/AGENTE_LOG.md]
        C2[2. Actualizar LOG_INDEX.md]
        C3[3. ¿Cambió estado? → Actualizar CONTEXT.md]
        C4[4. ¿Cambió regla? → Actualizar PROJECT_RULES.md]
        C5[5. ¿Área crítica? → Solicitar cross-review]

        C1 --> C2 --> C3 --> C4 --> C5
    end

    CLOSE --> SESSION_END([Sesión cerrada])

    style AGENT_START fill:#e1f5fe
    style SESSION_END fill:#c8e6c9
    style ANTILOOP fill:#ffcdd2
```

### B2. Pipeline Tri-Agente (cambios significativos)

```mermaid
flowchart TD
    REQUEST([📩 Petición del usuario\no tarea identificada]) --> CLASSIFY{¿Nivel\nde cambio?}

    CLASSIFY -->|Menor: typo, lint,\ndoc update| FAST_TRACK

    subgraph FAST_TRACK["⚡ Flujo rápido"]
        FT1[Cualquier agente ejecuta]
        FT2[validate-change]
        FT3[Registrar en log]
        FT1 --> FT2 --> FT3
    end

    CLASSIFY -->|Significativo: feature,\nrefactor, arquitectura| PHASE1

    subgraph PHASE1["🔍 FASE 1 — Investigación (Gemini)"]
        direction TB
        G1[Escanear repo completo]
        G2[Analizar contexto y dependencias]
        G3[Identificar archivos afectados]
        G4[Evaluar riesgos sistémicos]
        G5[/"📄 Entregable:\nCONTEXT_SNAPSHOT.md"/]
        G1 --> G2 --> G3 --> G4 --> G5
    end

    PHASE1 --> PHASE2

    subgraph PHASE2["⚙️ FASE 2 — Ingeniería (Codex)"]
        direction TB
        X1[Leer CONTEXT_SNAPSHOT.md]
        X2[Implementar cambio]
        X3[Escribir / actualizar tests]
        X4[Ejecutar validate-change\nlint → test → scan]
        X5{¿Pasa?}
        X6[/"📄 Entregable:\nCódigo + Test Report"/]
        X1 --> X2 --> X3 --> X4 --> X5
        X5 -->|Sí| X6
        X5 -->|No| X7[Corregir]
        X7 --> X4
    end

    PHASE2 --> PHASE3

    subgraph PHASE3["🏛️ FASE 3 — Gobernanza (Claude)"]
        direction TB
        CL1[Review contra PROJECT_RULES]
        CL2[Auditoría de seguridad]
        CL3[Verificar intención del usuario]
        CL4[Skill: cross-review]
        CL5{¿Aprobado?}
        CL6[/"📄 Entregable:\nVALIDATION_CERTIFICATE.md"/]
        CL1 --> CL2 --> CL3 --> CL4 --> CL5
        CL5 -->|Sí| CL6
        CL5 -->|No| REJECT[Devolver a Fase 2\ncon observaciones]
    end

    REJECT --> PHASE2
    PHASE3 --> MERGE

    MERGE[Commit / Merge\nActualizar CONTEXT.md\nActualizar LOG_INDEX.md] --> DONE([✅ Cambio integrado])

    CLASSIFY -->|Emergencia:\nhotfix| HOTFIX

    subgraph HOTFIX["🚨 Flujo de emergencia"]
        H1[Autorización humana]
        H2[Implementar fix mínimo]
        H3[Validar + deploy]
        H4[Post-mortem obligatorio]
        H1 --> H2 --> H3 --> H4
    end

    style REQUEST fill:#e1f5fe
    style DONE fill:#c8e6c9
    style REJECT fill:#ffcdd2
    style HOTFIX fill:#fff3e0
```

### B3. Flujo de manejo de errores y anti-loop

```mermaid
flowchart TD
    ERROR([⚠️ Error detectado]) --> FIRST{¿Primer\nintento?}

    FIRST -->|Sí| HYPOTHESIZE[Formular hipótesis\ncon evidencia]
    HYPOTHESIZE --> ATTEMPT1[Intentar corrección\ndocumentando hipótesis]
    ATTEMPT1 --> RESOLVED1{¿Resuelto?}

    RESOLVED1 -->|Sí| LOG_SUCCESS[Registrar éxito\nen log del agente]
    LOG_SUCCESS --> CONTINUE([Continuar trabajo])

    RESOLVED1 -->|No| SECOND{¿Hay hipótesis\nNUEVA?}

    FIRST -->|No| SECOND

    SECOND -->|Sí| ATTEMPT2[UN intento más\ncon hipótesis nueva\ndocumentada]
    ATTEMPT2 --> RESOLVED2{¿Resuelto?}

    RESOLVED2 -->|Sí| LOG_SUCCESS
    RESOLVED2 -->|No| STOP

    SECOND -->|No| STOP

    STOP[⛔ STOP OBLIGATORIO] --> REGISTER[Registrar en log:\n• Error exacto\n• Comando/output\n• Hipótesis probadas\n• Gap del harness identificado]

    REGISTER --> FTR_SKILL[Skill: failure-to-rule]

    FTR_SKILL --> ANALYZE[Analizar causa raíz:\n¿Falta contexto?\n¿Falta herramienta?\n¿Falta spec?\n¿Falta constraint?]

    ANALYZE --> NEW_RULE[Generar FTR-NNN:\n• Trigger condition\n• Root cause\n• Rule text\n• Deployment target]

    NEW_RULE --> DEPLOY_RULE{¿Tipo de\nregla?}

    DEPLOY_RULE -->|SYSTEM| SYSTEM_RULE[Agregar a\n.multiagent/core/rules/*.md]
    DEPLOY_RULE -->|PROJECT| PROJECT_RULE[Agregar a\n.claude/rules/*.md\no PROJECT_RULES.md]

    SYSTEM_RULE --> VERIFY_RULE[Verificar que la regla\npreviene el error original]
    PROJECT_RULE --> VERIFY_RULE

    VERIFY_RULE --> LOG_FTR[Registrar en log\ncon tag FTR]
    LOG_FTR --> CONTINUE

    style ERROR fill:#ffcdd2
    style STOP fill:#ef5350,color:#fff
    style CONTINUE fill:#c8e6c9
    style NEW_RULE fill:#fff3e0
```

### B4. Flujo del SDLC completo

```mermaid
flowchart LR
    IDEA([💡 Idea o\nnecesidad]) --> SPEC

    subgraph SPEC["SPEC"]
        S1[Skill: spec-create]
        S2[Generar SPEC_nombre.md]
        S3[Criterios ISC\n8-12 palabras, boolean]
        S1 --> S2 --> S3
    end

    SPEC -->|Aprobada\npor humano| PLAN

    subgraph PLAN["PLAN"]
        P1[Claude: diseño arquitectónico]
        P2[Identificar archivos e impacto]
        P3[ADR si cambio arquitectónico]
        P1 --> P2 --> P3
    end

    PLAN -->|Aprobado| BUILD

    subgraph BUILD["BUILD"]
        B1[Codex: implementar]
        B2[Escribir tests]
        B3[validate-change]
        B1 --> B2 --> B3
    end

    BUILD -->|Tests pasan| TEST

    subgraph TEST["TEST"]
        T1[Harness automático]
        T2[Verificar criterios ISC]
        T1 --> T2
    end

    TEST -->|CAs verificados| REVIEW

    subgraph REVIEW["REVIEW"]
        R1[cross-review\npor agente diferente]
        R2[Verificar vs spec\ny principios]
        R1 --> R2
    end

    REVIEW -->|Aprobado| DEPLOY

    subgraph DEPLOY["DEPLOY"]
        D1[Merge / commit]
        D2[Smoke test]
        D3[Marcar spec Completed]
        D1 --> D2 --> D3
    end

    DEPLOY --> DONE([✅ Feature\nentregada])

    style IDEA fill:#e1f5fe
    style DONE fill:#c8e6c9
```

### B5. Flujo de validación post-cambio (validation_router.py)

```mermaid
flowchart TD
    TOOL_USE([Agente usa Write/Edit\nen un archivo]) --> HOOK[PostToolUse hook\nvalidation_router.py]

    HOOK --> EXTRACT[Extraer file_path\ndel payload del hook]

    EXTRACT --> FIND_CONFIG[Auto-detectar adapter\nen .multiagent/adapters/]

    FIND_CONFIG --> CALL_ENGINE[Llamar engine.py validate\ncon --json]

    CALL_ENGINE --> MATCH{¿Hay validator\nconfigurado?}

    MATCH -->|No| SKIP[Sin validación\npara este tipo]
    SKIP --> END_HOOK([Hook termina])

    MATCH -->|Sí| RESOLVE[Resolver template:\n.py → python -m py_compile\n.json → python -m json.tool\n.sh → bash -n\n.md → test -s]

    RESOLVE --> EXECUTE[Ejecutar validator\nen subprocess]

    EXECUTE --> RESULT{¿Exit code?}

    RESULT -->|0 = OK| EMIT_OK[Emitir hook output:\nvalidation passed]
    RESULT -->|≠ 0 = FAIL| EMIT_FAIL[Emitir hook output:\nvalidation failed + stderr]

    EMIT_OK --> END_HOOK
    EMIT_FAIL --> END_HOOK

    style TOOL_USE fill:#e1f5fe
    style END_HOOK fill:#c8e6c9
    style EMIT_FAIL fill:#ffcdd2
```

### B6. Flujo de activación de skills

```mermaid
flowchart TD
    TRIGGER([Evento o necesidad\ndetectada]) --> WHICH{¿Qué skill\nse necesita?}

    WHICH -->|Inicio de sesión| BOOTSTRAP_SKILL[bootstrap-repo\nAnalizar repo + generar\ncomprensión del proyecto]

    WHICH -->|Código modificado| VALIDATE_SKILL[validate-change\nlint → test → scan]

    WHICH -->|Cambio significativo\ncompletado| REVIEW_SKILL[cross-review\nRevisión por agente\ndiferente al autor]

    WHICH -->|Cambio en deps,\nDocker, config| SECURITY_SKILL[security-scan\nCVEs + secrets +\ncontainer scan]

    WHICH -->|Anti-loop activado\n2 errores iguales| FTR_SKILL[failure-to-rule\nConvertir fallo en\nregla permanente]

    WHICH -->|Feature nueva\nrequiere planning| SPEC_SKILL[spec-create\nGenerar SPEC_nombre.md\ncon criterios ISC]

    WHICH -->|Auditoría periódica\no bajo demanda| GC_SKILL[gc-audit\nDrift, dead code,\nstale TODOs, logs]

    BOOTSTRAP_SKILL --> LOG
    VALIDATE_SKILL --> LOG
    REVIEW_SKILL --> LOG
    SECURITY_SKILL --> LOG
    FTR_SKILL --> LOG
    SPEC_SKILL --> LOG
    GC_SKILL --> LOG

    LOG[Registrar resultado\nen log del agente] --> DONE([Skill completado])

    style TRIGGER fill:#e1f5fe
    style DONE fill:#c8e6c9
    style FTR_SKILL fill:#ffcdd2
```

### B7. Flujo de garbage collection

```mermaid
flowchart TD
    TRIGGER([⏰ Periódico o\nbajo demanda]) --> GC_SKILL[Skill: gc-audit]

    GC_SKILL --> CHECKS

    subgraph CHECKS["Verificaciones de GC"]
        direction TB
        CHECK1[Doc-code drift\nCONTEXT.md vs estado real]
        CHECK2[Dead code\nFunciones, imports sin usar]
        CHECK3[Stale TODOs\n>30 días sin resolución]
        CHECK4[Log consistency\nLOG_INDEX vs logs reales]
        CHECK5[ADR review\nDecisiones obsoletas]
        CHECK6[Dependency audit\nCVEs nuevas]

        CHECK1 --> CHECK2 --> CHECK3 --> CHECK4 --> CHECK5 --> CHECK6
    end

    CHECKS --> FINDINGS{¿Hallazgos?}

    FINDINGS -->|Sin issues| LOG_CLEAN[Registrar: GC clean\nen log del agente]
    FINDINGS -->|Con issues| CLASSIFY

    CLASSIFY{¿Riesgo?}
    CLASSIFY -->|Bajo, evidente| AUTO_FIX[Corregir y registrar]
    CLASSIFY -->|Alto, ambiguo| REPORT[Solo reportar\nal humano]

    AUTO_FIX --> LOG_FIXED[Registrar correcciones\ncon tag GC]
    REPORT --> LOG_REPORTED[Registrar hallazgos\npendientes de decisión]

    LOG_CLEAN --> DONE([GC completado])
    LOG_FIXED --> DONE
    LOG_REPORTED --> DONE

    style TRIGGER fill:#e1f5fe
    style DONE fill:#c8e6c9
```

---

## PARTE C — MAPA DE INTERACCIÓN ENTRE COMPONENTES

### C1. Vista general del sistema

```mermaid
graph TB
    subgraph "HUMANO"
        USER[👤 Usuario]
    end

    subgraph "AGENTES"
        CLAUDE[Claude\nGovernor + Architect]
        CODEX[Codex\nImplementer + DevOps]
        GEMINI[Gemini\nResearcher + Sentinel]
    end

    subgraph "CORE ENGINE"
        ENGINE[engine.py]
        VALIDATOR[validation_router.py]
    end

    subgraph "CONFIGURACIÓN"
        ADAPTER[adapter.json]
        PRECOMMIT[.pre-commit-config.yaml]
        HOOKS[hooks.json]
    end

    subgraph "GOBERNANZA"
        RULES[PROJECT_RULES.md]
        CTX[CONTEXT.md]
        ROLES[AGENT_ROLES.md]
        LOGIDX[LOG_INDEX.md]
    end

    subgraph "LOGS"
        CL_LOG[CLAUDE_LOG.md]
        CX_LOG[CODEX_LOG.md]
        GM_LOG[GEMINI_LOG.md]
    end

    subgraph "SKILLS"
        SK[7 skills\nbootstrap, validate,\ncross-review, security,\nfailure-to-rule, spec,\ngc-audit]
    end

    USER -->|peticiones| CLAUDE
    USER -->|peticiones| CODEX
    USER -->|peticiones| GEMINI

    CLAUDE -->|lee/escribe| RULES
    CLAUDE -->|lee/escribe| CTX
    CLAUDE -->|escribe| CL_LOG
    CLAUDE -->|invoca| SK

    CODEX -->|lee| RULES
    CODEX -->|lee| CTX
    CODEX -->|escribe| CX_LOG
    CODEX -->|invoca| SK

    GEMINI -->|lee| RULES
    GEMINI -->|lee/escribe| CTX
    GEMINI -->|escribe| GM_LOG
    GEMINI -->|invoca| SK

    ENGINE -->|lee| ADAPTER
    ENGINE -->|parsea| CL_LOG
    ENGINE -->|parsea| CX_LOG
    ENGINE -->|parsea| GM_LOG
    ENGINE -->|actualiza| LOGIDX

    VALIDATOR -->|invoca| ENGINE
    HOOKS -->|activa| VALIDATOR

    SK -->|post-cambio| VALIDATOR

    style USER fill:#e1f5fe
    style CLAUDE fill:#e8eaf6
    style CODEX fill:#fce4ec
    style GEMINI fill:#e8f5e9
```

---

## Apéndice — Referencia rápida de comandos del engine

```bash
# Ver estado de todos los agentes
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json status

# Generar propuesta de actualización de LOG_INDEX
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json sync-index

# Escribir actualización directamente (requiere anchors en LOG_INDEX.md)
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json sync-index --write

# Sugerir validador para un archivo
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json validate path/to/file.py

# Mismo en formato JSON (para hooks)
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --json validate path/to/file.py
```

---

*Documento generado por Claude Opus 4.6 (Governor / Architect) — 2026-03-16*
*Basado en análisis de engine.py, validation_router.py, 7 skills, 8 patterns, SDLC workflow y hooks*
