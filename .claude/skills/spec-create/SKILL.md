---
name: spec-create
description: Genera una especificación formal para una nueva feature o cambio significativo. Usar cuando el usuario describe una necesidad funcional y se requiere planificación antes de implementar.
---

# Spec Create

Genera una spec usando el template en `.multiagent/templates/SPEC_TEMPLATE.md`.

## Proceso

1. Lee `docs/governance/PROJECT_RULES.md` para entender contexto.
2. Lee `docs/governance/CONTEXT.md` para estado actual.
3. Solicita al usuario los requisitos si no están claros.
4. Genera la spec completa con:
   - Objetivo (qué, no cómo)
   - Alcance (dentro y fuera)
   - Criterios de aceptación verificables
   - Verification Criteria en formato ISC (booleano, 8-12 palabras)
   - Riesgos identificados
   - Plan de implementación de alto nivel
5. Asigna ID incremental (buscar último SPEC-NNN en `docs/sdlc/`).
6. Guarda en `docs/sdlc/SPEC_[NOMBRE].md`.

## Reglas
- NO implementar código hasta que el usuario apruebe la spec.
- Si la spec afecta áreas críticas → señalar explícitamente.
- Mínimo 3 Verification Criteria por spec.
- Todo criterio debe ser verificable (test, inspection, o demo).
