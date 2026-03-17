# AI_GOVERNANCE.md — Registro Interno de Gobernanza de IA

> ⚠️ **DOCUMENTO INTERNO — NO INCLUIR EN ENTREGABLES DE PROYECTO NI DOCUMENTACIÓN PÚBLICA.**
>
> **Propósito:** Registro del uso de herramientas de asistencia IA en el proyecto n8n Platform (DELCOP), conforme a requisitos de trazabilidad ISO 27001:2022 e ISO 9001:2015. Mantener actualizado para auditorías internas.

---

## 1. Principio

La IA se considera herramienta de asistencia de desarrollo y arquitectura, no mecanismo de aprobación final. Toda salida generada con asistencia automatizada (especialmente workflows de n8n y configuraciones de AWS) debe ser revisada, validada y trazable.

---

## 2. Inventario de herramientas

| Herramienta        | Proveedor | Uso principal                                    | Riesgo principal                          | Responsable de validación |
|--------------------|-----------|--------------------------------------------------|-------------------------------------------|---------------------------|
| Claude Code        | Anthropic | Gobernanza (Governor), Arquitectura, SDLC, AWS   | Supuestos incorrectos en AWS/Security     | Claude (Governor) / Usuario |
| Gemini Code Assist | Google    | Investigación (Researcher), Auditoría, Doc        | Alucinaciones en documentación técnica    | Gemini (Researcher) / Usuario |
| Codex CLI          | OpenAI    | Implementación (Implementer), Scripts, Docker    | Comandos destructivos o errores de shell  | Codex (Implementer) / Usuario |

### Controles aplicados

- [x] Código fuente compartido con agentes no contiene credenciales (`.env` excluido vía `.gitignore`).
- [x] No se comparten datos de clientes reales ni bases de datos de producción con los agentes.
- [x] Los agentes operan en entorno local (Windows 11 / Docker Desktop) sin acceso directo a AWS Producción (limitado a lectura de docs/config).
- [x] Validación cruzada obligatoria: Los cambios de Codex (Implementer) son auditados por Gemini (Researcher).

---

## 3. Mapeo de controles ISO → implementación

| Control                     | Implementación en n8n Platform                               |
|-----------------------------|---------------------------------------------------------------|
| ISO 27001 A.5.9             | Registro en este archivo (Sección 2).                         |
| ISO 27001 A.5.23            | Verificación de ToS de APIs (Sección 6).                      |
| ISO 27001 A.8.4             | Agentes solo acceden a archivos del repo; no a secretos .env. |
| ISO 27001 A.8.9             | Trazabilidad total en `LOG_INDEX.md` y logs por agente.       |
| ISO 27001 A.8.25            | Integración de pre-commit hooks para detección de secretos.   |
| ISO 27001 A.8.28            | Validación manual de workflows n8n (JSON) antes de commit.    |
| ISO 9001 Control documental | `PROJECT_RULES.md` como Fuente Única de Verdad (SSOT).        |

---

## 4. Evaluación de riesgos

| Riesgo                                          | Probabilidad | Impacto | Mitigación                                                       |
|-------------------------------------------------|-------------|---------|------------------------------------------------------------------|
| Alucinación: workflows n8n con lógica errónea    | Alta        | Medio   | Test de ejecución en Staging (Dell R720) antes de Prod.          |
| Exposición de N8N_ENCRYPTION_KEY a la IA         | Baja        | Crítico | Exclusión estricta de `.env` y revisión de logs.                |
| Comandos de Shell incompatibles con Windows 11   | Media       | Bajo    | Validación por Codex en entorno real antes de proponer script.   |
| Desincronización entre agentes (Pisado de logs)  | Baja        | Medio   | Uso obligatorio de `LOG_INDEX.md` y `CONTEXT.md`.                |

### Riesgo aceptado

> El uso de herramientas de IA para asistencia en desarrollo se acepta bajo las condiciones de control documentadas en este archivo. Se prioriza la agilidad en la arquitectura multi-entorno de n8n bajo supervisión humana constante.
>
> **Aprobado por:** Governor Claude (vía Protocolo Adopción)
> **Fecha:** 2026-03-17
> **Próxima revisión:** 2026-06-17 (Trimestral)

---

## 5. Términos de servicio — verificación inicial (2026-03-17)

| Proveedor | ¿Usa datos para entrenar? | Retención | Enlace ToS |
|-----------|---------------------------|-----------|------------|
| Anthropic | No (vía API/Tier Enterprise) | 30 días   | https://www.anthropic.com/policies |
| Google    | No (vía Cloud API/Vertex)   | No aplica | https://cloud.google.com/terms |
| OpenAI    | No (vía API / Enterprise)   | 30 días   | https://openai.com/policies |

> **Nota:** Se asume el uso de APIs comerciales/empresariales que garantizan privacidad de datos. No utilizar versiones gratuitas ("Consumer") para subir código del proyecto.

---

*Última actualización: 2026-03-17 — Revisado por: Gemini (Researcher)*
