# ADR_INDEX.md — Registro de Decisiones de Arquitectura

> **Propósito:** Registro cronológico de las decisiones técnicas significativas (Architecture Decision Records) tomadas durante el ciclo de vida del proyecto n8n Platform (DELCOP).

---

## Índice de Decisiones Activas

| ID      | Título                                           | Fecha      | Estado   | Agente / Autor |
|---------|--------------------------------------------------|------------|----------|----------------|
| ADR-001 | Usar imagen oficial n8n sin modificaciones       | 2026-03-16 | Activa   | Claude         |
| ADR-002 | Pipeline 3-entornos: local → staging → prod      | 2026-03-16 | Activa   | Claude         |
| ADR-003 | Workflows versionados como JSON en Git           | 2026-03-16 | Activa   | Claude         |
| ADR-004 | Adopción framework multi-agente v4.2 → upgrade v4.3 | 2026-03-17 | Activa   | Claude         |
| ADR-005 | Pipeline staging → prod formalizado (SPEC)       | 2026-03-17 | Activa   | Claude / Gemini|
| ADR-006 | BD Threat Intel separada de n8n (PostgreSQL)     | 2026-03-18 | Activa   | Claude         |
| ADR-007 | Scoring determinístico de IoCs                   | 2026-03-18 | Activa   | Claude         |
| ADR-008 | Code-nodes versionados como source of truth      | 2026-03-18 | Activa   | Claude         |
| ADR-009 | Infraestructura AWS: ECS + RDS + Secrets Manager | 2026-03-20 | Activa   | Claude         |
| ADR-010 | Fuentes activas vs pendientes en staging        | 2026-03-23 | Activa   | Claude         |
| ADR-011 | Framework v4.5: mejoras post-review multi-agente | 2026-03-23 | Activa   | Claude + Codex + Gemini |

---

## Detalle de Decisiones

### [ADR-001] Usar imagen oficial n8n sin modificaciones
- **Contexto:** Se requiere estabilidad y facilidad de actualización.
- **Decisión:** Utilizar la imagen `docker.n8n.io/n8nio/n8n:latest`.
- **Consecuencia:** Menor mantenimiento; cualquier personalización debe hacerse vía volúmenes o variables de entorno.

### [ADR-002] Pipeline 3-entornos: local → staging → prod
- **Contexto:** Necesidad de validar flujos antes de impactar producción en AWS.
- **Decisión:** Implementar flujo Desarrollo (Win11) → Staging (Dell R720) → Producción (AWS ECS).
- **Consecuencia:** Mayor seguridad y trazabilidad de cambios.

### [ADR-003] Workflows versionados como JSON en Git
- **Contexto:** n8n guarda flujos en su base de datos interna por defecto.
- **Decisión:** Forzar exportación a `app/workflows/*.json` para control de versiones.
- **Consecuencia:** Permite auditoría de cambios en la lógica de negocio vía Git.

### [ADR-004] Adopción framework multi-agente v4.2 → upgrade v4.3
- **Contexto:** Automatización de tareas de gobernanza y desarrollo.
- **Decisión:** Adoptar el framework multi-agente para orquestación entre Claude, Codex y Gemini.
- **Consecuencia:** Estructura de logs y reglas estandarizada.

### [ADR-005] Pipeline staging → prod formalizado (SPEC)
- **Contexto:** Necesidad de definir los pasos exactos para mover flujos entre entornos.
- **Decisión:** Crear `docs/sdlc/SPEC_STAGING_PIPELINE.md` como norma de cumplimiento.
- **Consecuencia:** Proceso de despliegue repetible y auditable.

### [ADR-006] BD Threat Intel separada de n8n (PostgreSQL)
- **Contexto:** El pipeline de Threat Intelligence necesita persistencia relacional para IoCs, pero n8n usa SQLite en local/staging.
- **Decisión:** Crear una base PostgreSQL separada (`threat_intel`) exclusiva para el pipeline TI, independiente de la BD interna de n8n.
- **Consecuencia:** n8n sigue con SQLite para su estado interno; los IoCs van a PostgreSQL dedicada. En producción AWS, ambas serán PostgreSQL pero en instancias/schemas separados.

### [ADR-007] Scoring determinístico de IoCs
- **Contexto:** Se necesita decidir automáticamente qué IoCs ameritan alerta, revisión o descarte.
- **Decisión:** Fórmula determinística: `score = (severity × trust × recency) + type_bonus + context_bonus`, con umbrales fijos (>=70 alert, 50-69 review, 20-49 store, <20 discard).
- **Consecuencia:** Reproducibilidad total — mismo input produce mismo score. Sin ML ni heurísticas opacas.

### [ADR-008] Code-nodes versionados como source of truth
- **Contexto:** Los code nodes de n8n (JS) contienen lógica crítica de normalización, scoring y alertas.
- **Decisión:** Versionar el código en `app/code-nodes/*.js` y pegar manualmente en n8n UI. Los archivos en Git son la fuente de verdad.
- **Consecuencia:** Los cambios en lógica se revisan vía Git diff antes de aplicarse en n8n.

### [ADR-009] Infraestructura AWS: ECS Fargate + RDS + Secrets Manager + ECR
- **Contexto:** n8n necesita un entorno de producción en AWS. La auditoría del 2026-03-19 confirmó que no existe infraestructura n8n en la cuenta AWS `043019737945`.
- **Decisión:** Desplegar en AWS ECS Fargate con la siguiente arquitectura:
  - **Compute:** ECS Fargate (serverless, sin EC2 que gestionar)
  - **Base de datos:** RDS PostgreSQL (para BD interna de n8n y para threat_intel)
  - **Imágenes:** ECR (repositorio privado `n8n-delcop`)
  - **Secretos:** AWS Secrets Manager para variables críticas (`N8N_ENCRYPTION_KEY`, `RDS_PASSWORD`, `THREAT_DB_PASSWORD`, `REDIS_PASSWORD`), SSM Parameter Store para API keys de integración
  - **Red:** VPC con subnets privadas (ECS, RDS) y públicas (ALB), Security Groups con mínimo privilegio
  - **Observabilidad:** CloudWatch Logs (`/ecs/n8n-prod`)
  - **Exposición:** ALB con terminación TLS vía ACM
- **Alternativas descartadas:**
  - EC2 directo — mayor overhead operativo, no justificado para un solo servicio
  - EKS — sobredimensionado para el caso de uso actual
  - Lightsail — limitaciones de networking y secrets management
- **Consecuencia:** Infraestructura reproducible, secretos nunca en texto plano, escalamiento automático disponible.
- **Referencia:** `docs/sdlc/SPEC_AWS_PRODUCTION.md` (aprobado por Claude, ENTRADA-008)

### [ADR-010] Fuentes activas vs pendientes en staging
- **Contexto:** El pipeline TI tiene 7 fuentes configuradas, pero no todas tienen credenciales validadas en staging.
- **Decisión:** Clasificar fuentes en dos grupos para activación incremental:
  - **Activas (credenciales validadas):** FortiGate (API key + endpoint corregido), Wazuh (JWT auth, .env pendiente de carga), Zabbix (JSON-RPC, .env pendiente de carga), GuardDuty (AWS nativo)
  - **Pendientes de registro:** AbuseIPDB (requiere cuenta), OTX AlienVault (requiere cuenta)
  - **Pendiente de configuración:** Trellix ePO (IMAP)
- **Consecuencia:** Los dry-runs se ejecutan incrementalmente conforme las credenciales estén disponibles. No se bloquea el pipeline por fuentes no críticas.

### [ADR-011] Framework v4.5: mejoras post-review multi-agente
- **Contexto:** Tras 8 días de uso del framework v4.2→v4.4 en n8n-platform, se identificaron 12 mejoras. Los 3 agentes evaluaron cada una en `FRAMEWORK_RECOMMENDATIONS_REVIEW_n8n-platform.md`.
- **Decisión:** Adoptar las siguientes mejoras en el framework, organizadas por prioridad:
  - **Inmediatas (v4.5):**
    - M-001: Logs append-only — nunca editar entradas previas
    - M-002: Anti-rewrite en PROJECT_RULES — agregar al final, no reemplazar secciones
    - M-003: Verificación de proyecto correcto en bootstrap (adapter.project_name vs directorio)
    - M-005: Documentar tooling externo (Context7, skills.sh) en overlays/bootstrap
    - M-006: CONTEXT.md con anchors fijos `### @AGENTE - Rol` generados por adapt-project
    - G-001: Patrón "insert after anchor" para ediciones seguras en Markdown
  - **Corto plazo (v4.5):**
    - M-004: adapt-project genera rutas reales del proyecto
    - C-001: Clasificación de cambios runtime vs git-trackeados
    - C-002: Dry-run estándar vía webhook dedicado (no `n8n execute`)
    - G-002: FRAMEWORK_CAPABILITIES.md generado por adapt-project
  - **Medio plazo (v4.6):**
    - M-007: Verificación explícita de remote antes de git pull
    - M-008: Comando `validate-log` en engine para detección de truncados
- **Alternativas descartadas:** Ninguna recomendación fue descartada — todas tienen evidencia de bugs reales (B-006 a B-009).
- **Consecuencia:** El framework gana protección mecánica contra los errores más frecuentes de los agentes. Las mejoras son incrementales y retrocompatibles.
- **Referencia:** `FRAMEWORK_RECOMMENDATIONS_REVIEW_n8n-platform.md`, `FRAMEWORK_REVIEW_v4.4.md`
- **Votación:** Unanimidad en 9/12 recomendaciones, mayoría 2/3 en las 3 restantes (M-004, G-002 subidas a "ahora" por el Governor).

---

*Última actualización: 2026-03-23 — Claude (Governor)*
