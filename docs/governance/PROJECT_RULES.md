# PROJECT_RULES.md — Single Source of Truth (SSOT)

## 1. Propósito

Este documento es la fuente única de verdad para reglas de proyecto, criterios de implementación y decisiones técnicas vigentes. Todo agente y todo desarrollador debe leerlo antes de realizar cambios relevantes.

---

## 2. Identidad del proyecto

| Campo                    | Valor                                                   |
|--------------------------|---------------------------------------------------------|
| Nombre                   | n8n Platform — DELCOP                                   |
| Repositorio              | https://github.com/gaguevara/n8n-platform               |
| Tipo                     | Brownfield                                              |
| Objetivo funcional       | Plataforma de automatización de workflows empresariales |
| Alcance actual           | Pipeline dev → staging (Dell R720) → producción (AWS)   |
| Restricciones conocidas  | Ejecución en Windows 11, Docker Desktop requerido       |
| Entorno objetivo         | AWS ECS Fargate (prod), Docker local/staging            |
| Nivel de Harness         | Level 3 (Harness Engineering — Multi-Agent Adoptado)    |

---

## 3. Stack técnico

| Componente           | Tecnología / Versión              |
|----------------------|-----------------------------------|
| Motor principal      | n8n (latest — docker.n8n.io)      |
| Workflows            | JSON (versionados en Git)         |
| Contenedores         | Docker / Docker Compose           |
| CI/CD                | Makefile + pre-commit hooks       |
| Base de datos (local)| SQLite (volumen Docker)           |
| Base de datos (prod) | PostgreSQL RDS (AWS)              |
| Cloud                | AWS ECS Fargate                   |
| Observabilidad       | Logs estructurados (Markdown)     |
| Entorno OS           | Windows 11 + Docker Desktop       |

---

## 4. Arquitectura y patrones

- **Estilo:** Pipeline de entornos (local → staging → producción).
- **Estructura:** `app/workflows/` (JSONs exportados), `infra/` (Docker), `ops/` (Makefile), `scripts/` (utilidades).
- **Patrones permitidos:** Workflows n8n exportados como JSON, IaC con Docker Compose, scripts shell para operaciones.
- **Patrones prohibidos:** Credenciales hardcodeadas en JSON de workflows, modificar imagen base sin justificación técnica.
- **Gestión de secretos:** Variables de entorno en `.env` (no versionado), `N8N_ENCRYPTION_KEY` generada con `openssl rand -hex 32`.
- **Pipeline de entornos:** Local (SQLite) → Staging Dell R720 (SQLite/Volume) → Producción AWS ECS (PostgreSQL RDS).

---

## 5. Estándares de código

- **Workflows n8n:** Exportar siempre desde UI antes de commit (`scripts/export-workflows.sh`).
- **Nombres de workflows:** kebab-case descriptivo (e.g., `sync-contacts-crm.json`).
- **Docker Compose:** Definir `healthcheck` en cada servicio con estado de producción.
- **Variables de entorno:** Documentar en `.env.example` toda variable nueva.
- **Commits:** formato `[tipo]: descripción breve` — tipos: `feat`, `fix`, `docs`, `refactor`, `chore`, `security`, `ops`.
- **Shell scripts:** Incluir `set -euo pipefail` al inicio de cada script.

---

## 6. Reglas de implementación

- Todo cambio en workflows debe exportarse a JSON antes de commitear.
- No modificar `docker-compose.prod.yml` sin plan documentado y validación cruzada.
- Cambios en `infra/Dockerfile` requieren rebuild y test de imagen antes de push.
- No introducir dependencias npm o paquetes custom en la imagen sin justificación.
- Actualizar `.env.example` ante toda variable nueva o eliminada.
- Cambios que afecten autenticación (`N8N_ENCRYPTION_KEY`, `N8N_BASIC_AUTH_*`) son alto riesgo: requieren plan documentado.

---

## 7. Reglas de validación

Todo cambio relevante debe dejar evidencia mínima:
- Archivos afectados
- Motivo del cambio
- Validación ejecutada (lint JSON, build Docker, test de arranque)
- Resultado observado
- Riesgo residual

---

## 8. Escalation y revisión cruzada

Cambios de **alto riesgo** que requieren documentación previa en `CLAUDE_LOG.md`:
- Modificación de variables de autenticación o cifrado
- Cambios en `docker-compose.prod.yml` o configuración AWS
- Migración de base de datos (SQLite → PostgreSQL o esquema)
- Modificación de scripts de backup/restore
- Actualización de imagen base de n8n

---

## 9. Estructura de directorios

```
n8n-platform/
├── app/workflows/          # JSON exportados de n8n (versionados)
├── infra/                  # Dockerfile + docker-compose por entorno
├── ops/                    # Makefile de operaciones
├── scripts/                # export/import/backup de workflows
├── docs/
│   ├── governance/         # PROJECT_RULES, CONTEXT, LOG_INDEX, AGENT_ROLES
│   ├── logs/               # Logs de actividad por agente
│   ├── architecture/       # Diagramas y ADRs
│   ├── sdlc/               # SPECs de features
│   └── knowledge/          # Principios de diseño
├── .claude/skills/         # Skills del framework multi-agente
├── .multiagent/            # Engine y adapters del framework
├── CLAUDE.md               # Bootstrap protocol para Claude Code
└── SESSION_BOOTSTRAP.md    # Protocolo de inicio de sesión
```

---

## 10. Decisiones técnicas activas (ADRs)

| ID     | Decisión                                        | Fecha      | Estado   |
|--------|-------------------------------------------------|------------|----------|
| ADR-001| Usar imagen oficial n8n sin modificaciones      | 2026-03-16 | Activa   |
| ADR-002| Pipeline 3-entornos: local→staging→prod         | 2026-03-16 | Activa   |
| ADR-003| Workflows versionados como JSON en Git          | 2026-03-16 | Activa   |
| ADR-004| Adopción framework multi-agente v4.2            | 2026-03-16 | Activa   |

---

## 11. Perfiles de stack — herramientas de validación

### Docker
- Lint de Dockerfile: `hadolint` (si disponible)
- Lint de Compose: `docker compose config`
- Build: `docker build -f infra/Dockerfile .`

### JSON (Workflows n8n)
- Validación: `python -m json.tool <archivo>`
- Schema n8n: estructura `nodes`, `connections`, `settings`

### Shell Scripts
- Lint: `bash -n <script>`
- Estilo: `shellcheck` (si disponible)

---

> **Última actualización:** 2026-03-16 — Governor Claude (adapt-project)
> **Próxima revisión:** cuando se agregue nuevo entorno o cambio de stack
