# AI_GOVERNANCE.md — Registro Interno de Gobernanza de IA

> ⚠️ **DOCUMENTO INTERNO — NO INCLUIR EN ENTREGABLES DE PROYECTO NI DOCUMENTACIÓN PÚBLICA.**
>
> **Propósito:** Registro del uso de herramientas de asistencia IA, conforme a requisitos de trazabilidad ISO 27001:2022 e ISO 9001:2015. Mantener actualizado para auditorías internas.

---

## 1. Principio

La IA se considera herramienta de asistencia de desarrollo, no mecanismo de aprobación final. Toda salida generada con asistencia automatizada debe ser revisada, validada y trazable.

---

## 2. Inventario de herramientas

| Herramienta        | Proveedor | Uso principal                                    | Riesgo principal                          | Responsable de validación |
|--------------------|-----------|--------------------------------------------------|-------------------------------------------|---------------------------|
| Claude Code        | Anthropic | Revisión de impacto, refactor, análisis técnico, SDLC | Supuestos incorrectos, cambios de alto alcance | `[Nombre]` |
| Gemini Code Assist | Google    | Síntesis, cobertura, documentación, mapeo         | Respuestas plausibles pero incorrectas    | `[Nombre]` |
| Codex CLI          | OpenAI    | Ejecución concreta, scripts, terminal, CI/CD      | Automatización errónea sin contexto       | `[Nombre]` |

### Controles aplicados

- [ ] Código fuente compartido con agentes no contiene credenciales (`.env` excluido vía `.gitignore`).
- [ ] No se comparten datos de clientes ni datos personales con los agentes.
- [ ] Revisión humana obligatoria antes de merge a rama principal.
- [ ] Los agentes operan sobre copia local del repositorio, no acceso directo a producción.

---

## 3. Mapeo de controles ISO → implementación

| Control                     | Implementación requerida                                      |
|-----------------------------|---------------------------------------------------------------|
| ISO 27001 A.5.9             | Inventariar herramientas IA y uso permitido (esta tabla).     |
| ISO 27001 A.5.23            | Evaluar términos de servicio de proveedores cloud/IA.         |
| ISO 27001 A.8.4             | Restringir acceso a información según necesidad.              |
| ISO 27001 A.8.9             | Gestionar configuración y cambios con trazabilidad.           |
| ISO 27001 A.8.24            | Aplicar criptografía si hay datos sensibles en tránsito.      |
| ISO 27001 A.8.25            | Integrar seguridad en el SDLC.                                |
| ISO 27001 A.8.28            | Asegurar codificación segura y validación de inputs.          |
| ISO 9001 Control documental | Mantener evidencia de revisión y consistencia.                |
| ISO 9001 Mejora continua    | Registrar hallazgos y ajustar proceso.                        |

---

## 4. Evaluación de riesgos

| Riesgo                                          | Probabilidad | Impacto | Mitigación                                                       |
|-------------------------------------------------|-------------|---------|------------------------------------------------------------------|
| Alucinación: código con bugs sutiles             | Alta        | Medio   | Revisión cruzada entre agentes + revisión humana + tests.        |
| Exposición de lógica propietaria a terceros       | Media       | Alto    | Verificar ToS de proveedores. No enviar IP crítica.              |
| Dependencia excesiva en agentes IA                | Media       | Medio   | Documentación y onboarding para desarrolladores sin contexto IA. |
| Código sin cumplimiento de estándares             | Media       | Medio   | `PROJECT_RULES.md` como SSOT + análisis estático en CI/CD.      |
| Pérdida de trazabilidad                           | Baja        | Alto    | Logs por agente + `LOG_INDEX.md` + ADRs.                        |

### Riesgo aceptado

> El uso de herramientas de IA para asistencia en desarrollo se acepta bajo las condiciones de control documentadas en este archivo. La decisión de no reflejar el uso de IA en documentación técnica del proyecto es una decisión consciente de gestión de riesgos.
>
> **Aprobado por:** `[NOMBRE - ROL]`
> **Fecha:** `[YYYY-MM-DD]`
> **Próxima revisión:** `[YYYY-MM-DD]`

---

## 5. Registro de revisiones humanas

| Fecha | PR/Commit | Agente origen | Revisor humano | Resultado | Observaciones |
|-------|-----------|---------------|----------------|-----------|---------------|
| `[FECHA]` | `[REF]` | `[Agente]` | `[Nombre]` | `[Aprobado/Rechazado]` | `[Notas]` |

---

## 6. Términos de servicio — verificación periódica

| Proveedor | ¿Usa datos para entrenar? | Retención | Última verificación | Enlace ToS |
|-----------|---------------------------|-----------|---------------------|------------|
| Anthropic | `[Verificar]` | `[Verificar]` | `[FECHA]` | https://www.anthropic.com/policies |
| Google    | `[Verificar]` | `[Verificar]` | `[FECHA]` | https://cloud.google.com/terms |
| OpenAI    | `[Verificar]` | `[Verificar]` | `[FECHA]` | https://openai.com/policies |

> **Acción:** Revisar trimestralmente. Verificar si datos enviados a APIs se usan para entrenamiento.

---

*Última actualización: [FECHA] — Revisado por: [NOMBRE]*
