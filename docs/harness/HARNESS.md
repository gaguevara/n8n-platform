# HARNESS.md — Ingeniería de Arnés (Harness Engineering)

> **Propósito:** Define las restricciones mecánicas, loops de feedback y procesos de mantenimiento
> que mantienen a los agentes IA productivos y confiables. Basado en el modelo de OpenAI/Fowler (feb 2026).
>
> **Principio fundamental:** Cuando un agente falla, el problema es el harness, no el agente.
> Cada fallo repetido debe resultar en una mejora al entorno, no en repetir el prompt.

---

## 1. Modelo conceptual

```
┌─────────────────────────────────────────────────────┐
│                    HARNESS                           │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  CONTEXT     │  │ CONSTRAINTS  │  │ GARBAGE   │  │
│  │ ENGINEERING  │  │ MECÁNICAS    │  │ COLLECTION│  │
│  │             │  │              │  │           │  │
│  │ CLAUDE.md   │  │ Linters      │  │ Doc audit │  │
│  │ Rules files │  │ Tests estruct│  │ Dead code │  │
│  │ Specs       │  │ Pre-commit   │  │ Stale docs│  │
│  │ Knowledge   │  │ CI gates     │  │ Drift     │  │
│  │ Skills      │  │ Type checks  │  │ detection │  │
│  └─────────────┘  └──────────────┘  └───────────┘  │
│                                                     │
│              ┌──────────────┐                       │
│              │    AGENTE    │                        │
│              │   (modelo)   │                        │
│              └──────────────┘                        │
└─────────────────────────────────────────────────────┘
```

---

## 2. Context Engineering (lo que el agente ve)

### 2.1 Contexto estático (siempre cargado)

| Archivo | Propósito | Cuándo se carga |
|---------|-----------|-----------------|
| `CLAUDE.md` (raíz) | Puente al framework, reglas esenciales | Automático al iniciar Claude Code |
| `SESSION_BOOTSTRAP.md` | Protocolo de arranque | Primer paso de toda sesión |
| `docs/governance/PROJECT_RULES.md` | SSOT del proyecto | Arranque obligatorio |

### 2.2 Contexto bajo demanda (just-in-time)

| Archivo | Se carga cuando... |
|---------|-------------------|
| `docs/governance/CONTEXT.md` | El agente necesita estado actual del proyecto |
| `docs/knowledge/DESIGN_PRINCIPLES.md` | El agente va a generar o revisar código |
| `docs/skills/AGENT_SKILLS_MATRIX.md` | Se evalúa capacidad del agente o se asigna tarea |
| `docs/sdlc/SPEC_*.md` | El agente va a implementar una feature específica |
| `docs/security/RISK_REGISTER*.md` | Cambio en área crítica |

### 2.3 Reglas por ruta (path-scoped)

Cuando el agente trabaja en archivos específicos, las reglas se activan por extensión o directorio:

```
# Ejemplo para Claude Code (.claude/rules/)
*.py          → Aplicar PEP 8, type hints, Google docstrings
*.yml         → Validar YAML syntax, no hardcodear secrets
Dockerfile*   → Usuario no-root, multi-stage, no secrets en layers
*.xml         → Indentación 4 espacios (Odoo views)
addons/*/     → Verificar __manifest__.py completo, tests en tests/
```

---

## 3. Constraints Mecánicas (lo que el agente NO puede hacer)

### 3.1 Principio

Las restricciones textuales ("no hagas X") son sugerencias. Las restricciones mecánicas son bloqueos reales. Un linter que falla es más confiable que una instrucción en un prompt.

### 3.2 Herramientas de enforcement

| Herramienta | Qué valida | Cuándo ejecutar | Bloquea? |
|-------------|-----------|-----------------|----------|
| **ruff** (Python) | PEP 8, imports, code smells | Pre-commit + post-cambio | Sí |
| **mypy** (Python) | Type hints correctos | Pre-commit | Sí (modo strict) |
| **hadolint** | Dockerfile best practices | Pre-commit | Sí |
| **shellcheck** | Scripts bash | Pre-commit | Sí |
| **pip-audit** | CVEs en dependencias Python | Pre-merge | Sí |
| **trivy** | Vulnerabilidades en imágenes Docker | Pre-deploy | Sí |
| **detect-secrets** | Credenciales hardcodeadas | Pre-commit | Sí (bloqueante) |
| **eslint** (JS/OWL) | JavaScript standards | Pre-commit | Sí |

### 3.3 Tests estructurales

Además de tests funcionales, el proyecto debe tener tests que validen la estructura:

- **Test de dependencias:** Verificar que las dependencias fluyan en la dirección correcta (inner ← outer).
- **Test de imports:** Ningún módulo de negocio importa directamente un framework.
- **Test de secrets:** Ningún archivo versionado contiene patterns de credenciales.
- **Test de configuración:** Cada docker-compose tiene los campos requeridos (non-root user, resource limits, health checks).

### 3.4 Regla post-cambio para agentes

Después de cada cambio, el agente debe ejecutar (en este orden):

```
1. Linter/formatter      → ruff check + ruff format (Python)
2. Type check            → mypy (si habilitado)
3. Tests unitarios       → pytest (archivos afectados)
4. Secret scan           → detect-secrets scan
5. Docker lint           → hadolint (si Dockerfile afectado)
```

Si cualquier paso falla → el agente corrige antes de continuar. Si falla 2 veces el mismo → STOP + registrar gap en el harness.

---

## 4. Garbage Collection (mantenimiento del entorno)

### 4.1 Concepto

Igual que un garbage collector libera memoria no usada, un proceso periódico debe limpiar inconsistencias del codebase que los agentes (y humanos) generan con el tiempo.

### 4.2 Tareas de garbage collection

| Tarea | Frecuencia | Ejecutor | Qué busca |
|-------|-----------|----------|-----------|
| Doc-code drift | Semanal | Agente Claude | CONTEXT.md desactualizado vs estado real del repo |
| Dead code detection | Quincenal | Agente Codex | Funciones, imports, variables no usadas |
| Dependency audit | Quincenal | Agente Codex | CVEs nuevas en dependencias |
| ADR review | Mensual | Agente Claude | ADRs obsoletas o con decisiones revertidas |
| Log consistency | Semanal | Cualquier agente | LOG_INDEX.md vs contenido real de logs |
| Stale TODOs | Quincenal | Cualquier agente | TODOs con más de 30 días sin resolución |

### 4.3 Protocolo

1. El agente ejecuta la tarea de garbage collection
2. Registra hallazgos en su log
3. Si hay inconsistencias → propone corrección al humano
4. Si la corrección es de bajo riesgo y evidente → ejecutar y registrar
5. Si es de alto riesgo → solo reportar, no ejecutar

---

## 5. Feedback Loops

### 5.1 Loop inmediato (durante la sesión)

```
Agente genera código
    → Linter ejecuta
        → Error detectado
            → Agente corrige
                → Linter pasa
                    → Tests ejecutan
                        → Resultado registrado
```

### 5.2 Loop de sesión (al cierre)

```
Agente termina tarea
    → Registra en log
        → Actualiza CONTEXT.md
            → Verifica LOG_INDEX.md
                → Evalúa si el harness necesita mejoras
                    → Registra gap si aplica
```

### 5.3 Loop de mejora del harness

```
Agente falla en una tarea (2+ veces)
    → STOP (anti-loop)
        → Registra: error, contexto, hipótesis
            → Humano evalúa: ¿es gap del harness?
                → Sí → Mejorar: agregar doc, tool, spec, constraint
                → No → Limitación del modelo, reasignar o hacer manual
```

---

## 6. MCP Integration — Fase 2

### 6.1 Concepto

Dar a los agentes acceso directo a las herramientas del proyecto via MCP (Model Context Protocol), en vez de depender de copy-paste del humano.

### 6.2 MCP Servers planificados

| MCP Server | Acceso a | Agentes | Fase |
|------------|---------|---------|------|
| Docker MCP | `docker compose`, logs, exec | Claude, Codex | 2a |
| Database MCP | Queries read-only contra DB dev/staging | Gemini, Codex | 2b |
| CI/CD MCP | Pipeline status, test results, build logs | Todos | 2c |
| Observability MCP | Application logs, métricas, health checks | Claude, Gemini | 2d |
| IDE MCP (JetBrains/VSCode) | File problems, inspections, run configs | Codex | 2e |

### 6.3 Reglas de seguridad MCP

- **Solo lectura por defecto.** Ningún MCP server permite write sin aprobación explícita.
- **Solo entornos dev/staging.** Producción nunca se expone via MCP.
- **Credenciales via Secrets Manager.** Las conexiones MCP no hardcodean credentials.
- **Audit trail.** Toda invocación MCP queda registrada.
- **Timeout.** Máximo 30 segundos por invocación MCP.

### 6.4 Roadmap de implementación

```
Fase 2a — Docker MCP (inmediato)
  └─► docker compose logs, docker exec, docker ps
  └─► Permite al agente diagnosticar sin que el humano copie logs

Fase 2b — Database MCP (después de multi-company configurado)
  └─► Queries read-only contra BD de desarrollo
  └─► Permite al agente verificar datos, esquema, índices

Fase 2c — CI/CD MCP (después de pipeline configurado)
  └─► Ver estado de builds, test results, artifacts
  └─► Permite al agente verificar si sus cambios pasan CI

Fase 2d — Observability MCP (después de deploy a staging)
  └─► Logs de aplicación, métricas de performance
  └─► Permite al agente diagnosticar problemas en staging

Fase 2e — IDE MCP (cuando se estandarice VSCode/JetBrains)
  └─► Inspections, file problems, run configs predefinidas
  └─► Permite feedback loop inmediato como el caso Skyscanner
```

---

## 7. Métricas del Harness

| Métrica | Qué mide | Meta |
|---------|----------|------|
| Tasa de éxito primer intento | % de tareas que el agente completa sin fallo | > 70% |
| Fallos por gap de harness | Fallos causados por falta de doc/tool/spec | 0 recurrentes |
| Tiempo de feedback loop | Segundos desde cambio hasta validación | < 60s (linter+tests) |
| Garbage collection coverage | % de tareas GC ejecutadas en el periodo | 100% |
| Drift doc-código | Inconsistencias detectadas por GC | Tendencia decreciente |

---

*Basado en: Harness Engineering (OpenAI, feb 2026), Context Engineering for Coding Agents (Böckeler/Fowler, feb 2026), Spec-Driven Development (GitHub Spec Kit), Skyscanner + JetBrains MCP integration.*
