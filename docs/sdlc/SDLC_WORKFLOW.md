# SDLC_WORKFLOW.md — Ciclo de Vida del Desarrollo

> **Propósito:** Define el flujo completo desde la idea hasta el cierre de una feature/cambio.
> Todo agente y desarrollador sigue este ciclo. Integra Spec-Driven Development y Harness Engineering.

---

## Flujo completo

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  SPEC   │───►│  PLAN   │───►│  BUILD  │───►│  TEST   │───►│ REVIEW  │───►│ DEPLOY  │
│         │    │         │    │         │    │         │    │         │    │         │
│ Intent  │    │ Diseño  │    │ Código  │    │ Validar │    │ Cruzada │    │ Release │
│ + Spec  │    │ + ADR   │    │ + Lint  │    │ + Scan  │    │ + Log   │    │ + Close │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
    HUMAN         AGENT          AGENT          HARNESS        AGENT          HUMAN
  + AGENT       + HUMAN                       (mecánico)     + AGENT       + AGENT
```

---

## Fase 1: SPEC (Especificación)

**Responsable:** Humano (con apoyo de agente)
**Entrada:** Necesidad de negocio, bug report, mejora técnica
**Salida:** `docs/sdlc/SPEC_[NOMBRE].md` completada

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 1.1 | Identificar objetivo funcional | Sección "Objetivo" de la spec |
| 1.2 | Definir alcance (dentro y fuera) | Sección "Alcance" |
| 1.3 | Escribir criterios de aceptación | Sección "Criterios de aceptación" |
| 1.4 | Identificar riesgos | Sección "Riesgos" + entrada en RISK_REGISTER |
| 1.5 | Revisar spec con equipo/agente | Estado de spec = "Aprobada" |

**Gate:** La spec debe estar "Aprobada" antes de avanzar a Plan.

---

## Fase 2: PLAN (Diseño técnico)

**Responsable:** Agente (Claude: arquitectura) + Humano (validación)
**Entrada:** Spec aprobada
**Salida:** Plan de implementación documentado

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 2.1 | Leer spec completa + PROJECT_RULES + CONTEXT | Agente confirma lectura |
| 2.2 | Leer DESIGN_PRINCIPLES + knowledge relevante | Agente confirma principios aplicables |
| 2.3 | Proponer plan de implementación (archivos, orden, patrón) | Sección "Plan" en la spec |
| 2.4 | Identificar si necesita ADR nuevo | ADR creado o "no aplica" |
| 2.5 | Estimar impacto en áreas críticas | Lista de áreas afectadas |
| 2.6 | Humano valida plan | Plan aprobado |

**Gate:** Plan aprobado por humano antes de avanzar a Build.

---

## Fase 3: BUILD (Implementación)

**Responsable:** Agente ejecutor (Codex: código, Claude: infra, Gemini: optimización)
**Entrada:** Plan aprobado
**Salida:** Código + tests + documentación

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 3.1 | Implementar según plan | Archivos creados/modificados |
| 3.2 | Aplicar estándares de DESIGN_PRINCIPLES | Código limpio, patrones correctos |
| 3.3 | Escribir tests unitarios | Tests pasan localmente |
| 3.4 | Ejecutar linter/formatter | Sin errores de linting |
| 3.5 | Ejecutar scan de secrets | Sin secrets detectados |
| 3.6 | Registrar en log del agente | Entrada de log creada |

**Gate:** Linter + tests + secret scan pasan antes de avanzar.

---

## Fase 4: TEST (Validación por harness)

**Responsable:** Harness (mecánico) + Agente revisor
**Entrada:** Código con tests pasando
**Salida:** Validación completa

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 4.1 | Pre-commit hooks ejecutan | Todos los hooks pasan |
| 4.2 | Tests de integración (si aplica) | Suite de tests pasa |
| 4.3 | Scan de dependencias | pip-audit / npm audit limpio |
| 4.4 | Scan de imagen Docker (si aplica) | trivy sin vulnerabilidades críticas |
| 4.5 | Verificar criterios de aceptación de la spec | Cada CA marcado como verificado |

**Gate:** Todos los checks automáticos pasan + CAs verificados.

---

## Fase 5: REVIEW (Revisión cruzada)

**Responsable:** Agente revisor (distinto al ejecutor) + Humano
**Entrada:** Código validado por harness
**Salida:** Revisión aprobada

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 5.1 | Agente revisor lee cambios contra spec y principios | Review comments |
| 5.2 | Verificar que no hay violaciones de DESIGN_PRINCIPLES | Confirmación |
| 5.3 | Verificar aislamiento multi-company (si aplica) | Record rules validadas |
| 5.4 | Humano revisa hallazgos y aprueba | Aprobación documentada |
| 5.5 | Actualizar CONTEXT.md si el estado cambió | CONTEXT.md actualizado |
| 5.6 | Actualizar RISK_REGISTER si se detectaron riesgos | RISK_REGISTER actualizado |
| 5.7 | Registrar en LOG_INDEX | Índice actualizado |

**Gate:** Revisión aprobada por humano.

---

## Fase 6: DEPLOY (Despliegue)

**Responsable:** Humano + Agente (según entorno)
**Entrada:** Revisión aprobada
**Salida:** Cambio desplegado + spec cerrada

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 6.1 | Merge a rama correspondiente | Commit en git |
| 6.2 | Deploy a entorno (local → staging → producción) | Deploy exitoso |
| 6.3 | Validación post-deploy (smoke test) | Funcionalidad verificada |
| 6.4 | Completar DEPLOYMENT_VALIDATION si aplica | Checklist completo |
| 6.5 | Marcar spec como "Completada" | Estado actualizado |
| 6.6 | Cerrar riesgos resueltos en RISK_REGISTER | Riesgos cerrados |
| 6.7 | Log final del agente | Entrada de cierre |

**Regla:** Deploy a producción requiere aprobación humana documentada. Siempre.

---

## Flujo rápido (cambios menores)

Para cambios de bajo impacto en entorno local:

```
SPEC (mental, no formal) → BUILD → TEST (harness) → LOG
```

No requiere: spec formal, plan documentado, review cruzada, deployment checklist.
Sí requiere: linter pasa, tests pasan, log registrado.

---

## Flujo de emergencia (hotfix)

```
HUMANO autoriza → AGENTE implementa fix mínimo →
AGENTE REVISOR valida → DEPLOY con monitoreo →
POST-MORTEM (spec retroactiva + RISK_REGISTER)
```

Todo hotfix genera una revisión completa posterior.

---

## Versionamiento

| Elemento | Convención |
|----------|-----------|
| Código | Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `security:` |
| Módulos (Odoo) | `[odoo_version].[major].[minor].[patch]` ej: `19.0.1.0.0` |
| Framework | Semantic Versioning en `docs/CHANGELOG.md` |
| Specs | ID incremental: `SPEC-001`, `SPEC-002` |
| ADRs | ID incremental: `ADR-001`, `ADR-002` |
| Riesgos | ID con prefijo: `RISK-T01` (técnico), `RISK-O01` (operacional) |
| Logs | ID por agente: `LOG-C001` (Claude), `LOG-G001` (Gemini), `LOG-X001` (Codex) |

---

*Este flujo integra Spec-Driven Development (GitHub Spec Kit), Harness Engineering (OpenAI/Fowler), y cumplimiento ISO 27001:2022.*
