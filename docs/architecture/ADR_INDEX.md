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

---

*Última actualización: 2026-03-20 — Claude (Governor)*
