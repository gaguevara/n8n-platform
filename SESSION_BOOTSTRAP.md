# SESSION_BOOTSTRAP.md

## Propósito

Protocolo común de arranque para cualquier agente o desarrollador que inicie una sesión de trabajo en este repositorio. No iniciar cambios relevantes sin completar la secuencia de inicio.

---

## Secuencia obligatoria de inicio

```
1. Leer docs/governance/PROJECT_RULES.md
2. Leer docs/governance/CONTEXT.md
3. Leer overlay correspondiente en docs/agents/[AGENTE].md
4. Leer docs/governance/LOG_INDEX.md
5. Revisar últimas entradas relevantes en docs/logs/ de los otros agentes
6. Si la tarea involucra código → leer docs/knowledge/DESIGN_PRINCIPLES.md
7. Si hay dudas sobre habilidades esperadas → leer docs/skills/SKILLS.md
8. Si la tarea tiene spec → leer docs/sdlc/SPEC_[NOMBRE].md
9. Determinar tipo de tarea → actuar según nivel
```

## Principio de Harness Engineering

> Cuando un agente falla, el problema es el entorno, no el agente.

Cada fallo repetido debe resultar en una mejora al harness (documentación, herramienta,
spec, constraint mecánica), no en repetir el prompt. Ver `docs/harness/HARNESS.md`.

---

## Arranque adaptativo

### Caso A — Tarea puntual y clara
Ejecutar directamente. Validar de inmediato. Registrar resultado en el log del agente.

### Caso B — Proyecto existente con contexto suficiente
No repetir cuestionarios. Leer estructura, reglas, decisiones activas y logs recientes. Continuar sobre la base existente.

### Caso C — Proyecto greenfield o contexto insuficiente
Solicitar o construir primero: objetivo, stack, restricciones, alcance. No proponer arquitectura cerrada sin ese mínimo contexto.

### Caso D — Cambio de alto riesgo
Se considera alto riesgo si afecta: arquitectura, autenticación/autorización, secretos, cifrado, esquema de datos, CI/CD de producción, integraciones críticas, o controles de auditoría.

En este caso:
- Elaborar plan breve antes de ejecutar
- Identificar archivos e impacto
- Registrar plan en el log del agente
- Requerir validación cruzada obligatoria

---

## Regla anti-loop

- Mismo error 2 veces consecutivas sin nueva evidencia → **STOP**. Reportar: error exacto, log, comando, hipótesis de causa raíz.
- Error distinto con hipótesis nueva → máximo 1 intento adicional con la hipótesis documentada.
- No repetir comandos equivalentes a ciegas.
- Registrar siempre: error, hipótesis, evidencia, siguiente acción recomendada.

---

## Cierre de sesión

Antes de dar una tarea por terminada:

1. Registrar en `docs/logs/[AGENTE]_LOG.md`
2. Actualizar `docs/governance/LOG_INDEX.md` con el último LOG-ID
3. Actualizar `docs/governance/CONTEXT.md` si cambió el estado del proyecto
4. Actualizar `docs/governance/PROJECT_RULES.md` si cambió una regla o decisión estable
5. Escalar a revisión cruzada si el cambio afecta áreas críticas (ver sección 8 de PROJECT_RULES.md)
