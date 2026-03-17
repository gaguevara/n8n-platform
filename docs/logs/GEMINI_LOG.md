# GEMINI_LOG.md — Researcher/Reviewer Log

> Agente: Gemini Code Assist (Researcher + Reviewer)
> Proyecto: n8n Platform — DELCOP
> Formato de entradas: `## ENTRADA-{número} | {fecha} | {tipo}`

---

## ENTRADA-001 | 2026-03-17 | audit

**Tipo:** Auditoría de contexto y documentación
**Tarea:** Analizar brechas documentales, mapear variables, crear especificación de pipeline y actualizar onboarding técnico

### Análisis de brechas (ISO A.8.25)

| Control ISO | Estado | Evidencia | Brecha | Recomendación |
|-------------|--------|-----------|--------|---------------|
| `A.8.25` (Conf. Management) | `⚠️` | `.gitignore` | Falta `.env.example` y `.secrets.baseline` | Crear archivos para estandarizar setup |
| `A.12.1.2` (Change Mgmt) | `❌` | `docs/sdlc/` | No hay definición formal del pipeline multi-entorno | Crear `SPEC_STAGING_PIPELINE.md` |
| `A.18.2.2` (Compliance) | `⚠️` | `ONBOARDING.md` | Guía orientada a agentes, no a setup técnico real | Incluir requisitos de Windows 11/Docker |

### Acciones ejecutadas

1. **Mapeo de Variables:** Identificadas variables para Local, Staging y Prod.
2. **Creación de `.env.example`:** Centralización de configuración necesaria para onboarding técnico.
3. **Creación de `docs/sdlc/SPEC_STAGING_PIPELINE.md`:** Formalización del flujo Local → Dell R720 (Staging) → AWS ECS (Prod).
4. **Actualización de `docs/governance/ONBOARDING.md`:** Integración de sección técnica (make, docker, workflow export).

### Hallazgos técnicos relevantes

- **Contradicción en Imagen Docker:** `ADR-001` pide imagen oficial, pero `infra/Dockerfile` existe y `docker-compose.prod.yml` usa imagen de ECR. Se asume que el `Dockerfile` es un wrapper mínimo para cumplimiento corporativo.
- **Entornos:** Se confirmó que Staging (Dell R720) usa SQLite mientras Prod (AWS) usa RDS PostgreSQL. Esta discrepancia es aceptable para n8n si los workflows se versionan como JSON.

### Riesgo residual

- Falta de `.secrets.baseline` (Tarea de Codex/Claude).
- Los scripts shell (`scripts/*.sh`) pueden requerir Git Bash o WSL en Windows 11 para ejecutarse según lo documentado en el nuevo ONBOARDING.

### Harness gap

- `LOG_INDEX.md` tiene instrucciones contradictorias (usar engine vs actualización manual). Se optó por actualización manual para mantener trazabilidad inmediata.
