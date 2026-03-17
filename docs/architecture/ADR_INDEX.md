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

---

*Última actualización: 2026-03-17 — Generado por: Gemini (Researcher)*
