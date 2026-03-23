# Framework Multi-Agente - Review de Recomendaciones para n8n-platform

**Proyecto:** n8n-platform - DELCOP
**Repositorio:** `C:/dev/Proyectos/n8n-platform`
**Documento base:** `FRAMEWORK_REVIEW_v4.4.md`
**Objetivo:** concentrar en un solo lugar el review multi-agente de recomendaciones para el framework, usando evidencia del proyecto `n8n-platform` y evitando confusion con otros repositorios.

---

## Importante

Este documento aplica **solo** al proyecto `n8n-platform`.

Si un agente lo reutiliza en otro repositorio, debe crear una copia con el nombre del proyecto correcto en el titulo y en el bloque de identidad.

---

## Como revisar

1. Leer `FRAMEWORK_REVIEW_v4.4.md`.
2. Validar cada recomendacion contra evidencia real de `n8n-platform`:
   - `docs/governance/PROJECT_RULES.md`
   - `docs/governance/CONTEXT.md`
   - `docs/governance/LOG_INDEX.md`
   - `docs/logs/*.md`
3. Escribir comentarios solo en la seccion del agente correspondiente.
4. No borrar comentarios anteriores; este documento debe crecer por append.
5. Si una recomendacion cambia de prioridad o se descarta, justificarlo con evidencia de este proyecto.

---

## Recomendaciones a revisar

| ID | Recomendacion | Fuente | Motivo en n8n-platform |
|----|---------------|--------|------------------------|
| M-001 | Regla append-only para logs de agentes | `FRAMEWORK_REVIEW_v4.4.md` | Evitar truncado o perdida de historial en `docs/logs/*.md` |
| M-002 | Regla anti-rewrite para `PROJECT_RULES.md` | `FRAMEWORK_REVIEW_v4.4.md` | Proteger reglas activas del proyecto frente a reescrituras parciales |
| M-003 | Verificacion de proyecto correcto en bootstrap | `FRAMEWORK_REVIEW_v4.4.md` | Ya hubo confusion de repo durante ejecucion real |
| M-004 | `adapt-project` debe generar rutas reales del proyecto | `FRAMEWORK_REVIEW_v4.4.md` | Hubo referencias incorrectas en onboarding/gobernanza |
| M-005 | Explicar tooling externo del framework en overlays/bootstrap | `FRAMEWORK_REVIEW_v4.4.md` | Context7 y skills.sh causaron dudas operativas |
| M-006 | Template de `CONTEXT.md` con anchors fijos por agente | `FRAMEWORK_REVIEW_v4.4.md` | El backlog por agente es critico para Codex/Gemini |
| M-007 | Verificacion explicita de remote antes de `git pull` | `FRAMEWORK_REVIEW_v4.4.md` | Reduce falsos bloqueos en repos sin tracking |
| M-008 | Comando `validate-log` en el engine | `FRAMEWORK_REVIEW_v4.4.md` | Deteccion automatica de truncados y drift documental |
| C-001 | Diferenciar remediaciones de runtime no versionadas vs cambios Git-trackeados | Comentario Codex en `FRAMEWORK_REVIEW_v4.4.md` | En staging hubo fixes efectivos que requirieron trazabilidad separada |
| C-002 | Definir una via estandar de dry-run para entornos n8n vivos | Comentario Codex en `FRAMEWORK_REVIEW_v4.4.md` | `n8n execute` no fue reutilizable en staging por colision con broker |
| G-001 | Herramienta o patron seguro de "insert after anchor" para Markdown | Comentario Gemini en `FRAMEWORK_REVIEW_v4.4.md` | Reducir riesgo de reemplazos grandes en logs y contexto |
| G-002 | Generar `FRAMEWORK_CAPABILITIES.md` al adaptar el proyecto | Comentario Gemini en `FRAMEWORK_REVIEW_v4.4.md` | Aclarar herramientas MCP, engine y skills disponibles |

---

## Criterios de decision sugeridos

- **Adoptar ahora:** la mejora corrige un fallo ya observado en `n8n-platform` y tiene bajo costo.
- **Adoptar luego:** la mejora es valida, pero depende de cambios mayores en engine/harness.
- **Descartar:** la mejora no aporta valor suficiente o ya esta cubierta por otra regla.

Cada agente deberia indicar para cada recomendacion:
- Estado sugerido: `Adoptar ahora`, `Adoptar luego`, o `Descartar`
- Riesgo que reduce
- Evidencia usada
- Si requiere cambio en framework base, adapter o solo documentacion local

---

## Review por agente

### Claude (Governor) - Proyecto n8n-platform

**Estado:** Completado

Comentarios:

| ID | Estado sugerido | Comentario Claude (Governor) |
|----|-----------------|------------------------------|
| M-001 | **Adoptar ahora** | Unanimidad 3/3. B-006 fue real: Gemini truncó 146 líneas de historial. Regla mecánica: logs son append-only, nunca editar entradas previas. **Cambio: PROJECT_RULES §9 + overlays.** |
| M-002 | **Adoptar ahora** | Unanimidad 3/3. B-007 fue real: Gemini eliminó 3 reglas de seguridad al agregar las de v4.4. **Cambio: PROJECT_RULES §6 — agregar al final, nunca reemplazar secciones.** |
| M-003 | **Adoptar ahora** | Unanimidad 3/3. B-008 fue real: Codex ejecutó bootstrap completo en repo equivocado. **Cambio: SESSION_BOOTSTRAP Paso 0 — verificar adapter.project_name vs directorio.** |
| M-004 | **Adoptar ahora** | 2/3 dicen ahora, 1 dice luego. Gemini tiene razón: el drift de rutas genera tokens desperdiciados. Bajo costo de implementación. **Cambio: adapt-project genera rutas reales.** |
| M-005 | **Adoptar ahora** | Unanimidad 3/3. Gemini interpretó Context7/skills.sh como archivos físicos faltantes. **Cambio: overlays + bootstrap deben listar tooling externo explícitamente.** |
| M-006 | **Adoptar ahora** | Unanimidad 3/3. Codex pierde tareas si no hay anchors fijos. **Cambio: adapt-project genera `### @AGENTE - Rol` en CONTEXT.md.** |
| M-007 | **Adoptar luego** | Unanimidad 3/3 en "luego". Ya parcialmente corregido en v4.4. Prioridad baja. |
| M-008 | **Adoptar luego** | Unanimidad 3/3 en "luego". Útil pero depende de trabajo de engine. Priorizar después de M-001/M-002. |
| C-001 | **Adoptar ahora** | Unanimidad 3/3. Staging generó remediaciones de runtime no versionadas que luego hubo que reconciliar. **Cambio: nueva sección en PROJECT_RULES para clasificar cambios runtime vs git.** |
| C-002 | **Adoptar ahora** | Unanimidad 3/3. El dry-run es el mayor gap operativo. `n8n execute` colisiona con el broker. **Cambio: documentar webhook dedicado como patrón estándar de dry-run.** |
| G-001 | **Adoptar ahora** | Unanimidad 3/3. El riesgo de truncado en archivos largos es real y recurrente. **Cambio: documentar patrón "insert after anchor" en patterns/.** |
| G-002 | **Adoptar ahora** | 2/3 dicen ahora. Gemini y yo coincidimos en que reduce tokens desperdiciados. **Cambio: adapt-project genera FRAMEWORK_CAPABILITIES.md.** |

**Decisión consolidada del Governor:**

| Prioridad | IDs | Acción |
|---|---|---|
| **Inmediata (v4.5)** | M-001, M-002, M-003, M-005, M-006, G-001 | Reglas mecánicas — bajo costo, alto impacto |
| **Corto plazo (v4.5)** | M-004, C-001, C-002, G-002 | Requieren cambios en adapt-project o documentación nueva |
| **Medio plazo (v4.6)** | M-007, M-008 | Dependen de trabajo en engine |

**Evidencia usada:** `FRAMEWORK_REVIEW_v4.4.md` (bugs B-006 a B-009), `CLAUDE_LOG.md` (ENTRADA-001 a 015), cross-reviews de Codex y Gemini en 22 commits, 50+ tareas completadas.

**Próximo paso:** Crear ADR-011 formalizando estas decisiones y un patch v4.5 con las mejoras inmediatas.

---

### Codex (Implementer/DevOps) - Proyecto n8n-platform

**Estado:** Completado

Comentarios:

| ID | Estado sugerido | Comentario Codex |
|----|-----------------|------------------|
| M-001 | Adoptar ahora | Alto valor y bajo costo. Los logs son append-only en la practica, pero falta una regla mecanica explicita para evitar truncados. |
| M-002 | Adoptar ahora | `PROJECT_RULES.md` es SSOT del repo; una reescritura parcial puede romper el trabajo de los 3 agentes. |
| M-003 | Adoptar ahora | Ya hubo ejecucion en repo equivocado. El bootstrap deberia alertar antes de seguir leyendo contexto. |
| M-004 | Adoptar luego | Conviene corregirlo en `adapt-project`, pero no bloquea la operacion diaria si el Governor detecta el drift rapido. |
| M-005 | Adoptar ahora | Context7 y skills.sh generan confusion operativa real si no se explican como tooling MCP/npm y no como archivos del repo. |
| M-006 | Adoptar ahora | Para Codex esto es critico: si el backlog no esta bajo anchors claros por agente, se pierden tareas. |
| M-007 | Adoptar luego | Ya hay mejora parcial en bootstrap; falta endurecer el caso de repos sin tracking o con remote no configurado. |
| M-008 | Adoptar luego | Seria util, pero depende de trabajo de engine. Lo priorizaria despues de reglas append-only y anti-rewrite. |
| C-001 | Adoptar ahora | En staging hubo remediaciones validas en runtime que luego hubo que reconciliar con Git. El framework debe distinguir ambas clases de cambio. |
| C-002 | Adoptar ahora | El mayor gap operativo actual para n8n vivo es el dry-run. La dependencia de UI/manual reduce repetibilidad y evidencias. |
| G-001 | Adoptar ahora | Un patron `insert after anchor` reduciria mucho el riesgo en logs, contexto y docs de governance. |
| G-002 | Adoptar luego | Aporta onboarding, pero no es tan urgente como proteger logs, reglas y backlog por agente. |

Resumen Codex:

- Prioridad inmediata: `M-001`, `M-002`, `M-003`, `M-005`, `M-006`, `C-001`, `C-002`, `G-001`.
- Mayor beneficio operativo para `n8n-platform`: proteger trazabilidad, evitar drift de contexto y estandarizar ejecucion en staging.
- Evidencia principal usada: `FRAMEWORK_REVIEW_v4.4.md`, `docs/governance/PROJECT_RULES.md`, `docs/governance/CONTEXT.md`, `docs/governance/LOG_INDEX.md` y `docs/logs/CODEX_LOG.md`.

---

### Gemini (Researcher/Reviewer) - Proyecto n8n-platform

**Estado:** Completado

Comentarios:

| ID | Estado sugerido | Comentario Gemini |
|----|-----------------|-------------------|
| M-001 | Adoptar ahora | Crítico. Durante la ENTRADA-005, el uso de `replace` truncó accidentalmente entradas previas. Una regla mecánica de "solo append" es vital para la trazabilidad del Researcher. |
| M-002 | Adoptar ahora | Observado en ENTRADA-005: la adición de reglas v4.4 borró reglas de seguridad preexistentes. El Researcher tiende a sobre-simplificar el `old_string` en archivos de reglas extensos. |
| M-003 | Adoptar ahora | Apoyo la visión de Codex. La integridad del análisis depende de validar el entorno correcto desde el Paso 0 (ENTRADA-001 de exploración). |
| M-004 | Adoptar ahora | ENTRADA-006 mostró drift en ONBOARDING referenciando carpetas inexistentes (`docs/agents/`). El Researcher gasta tokens y turnos corrigiendo inconsistencias de generación. |
| M-005 | Adoptar ahora | Vital. En ENTRADA-006 documenté un harness gap erróneo sobre Context7 porque interpreté que faltaban archivos físicos, ignorando que es tooling MCP/npm. |
| M-006 | Adoptar ahora | Los anchors fijos permiten al Researcher validar la cobertura de tareas y consistencia del backlog sin ambigüedad estructural (ENTRADA-011). |
| M-007 | Adoptar luego | Útil para la limpieza del bootstrap, pero secundario frente a la protección de logs y SSOT. |
| M-008 | Adoptar luego | Valioso para auditorías de cumplimiento ISO (ENTRADA-009/014), detectando drifts entre código y documentación de forma proactiva. |
| C-001 | Adoptar ahora | La distinción es clave para el Researcher al documentar Runbooks (ENTRADA-010) que deben reflejar fielmente la operación real vs la versión Git. |
| C-002 | Adoptar ahora | La investigación en ENTRADA-010 confirmed que el gap CLI en staging obliga a usar Webhooks; el framework debería estandarizar este "modo debug/test". |
| G-001 | Adoptar ahora | **Prioridad Máxima.** Como Researcher, manejo archivos de documentación extensos donde `replace` es una operación de alto riesgo. Un patrón o herramienta de `insert after` es urgente. |
| G-002 | Adoptar ahora | Reduciría la curva de aprendizaje en cada nuevo proyecto, evitando investigaciones redundantes sobre las capacidades del propio agente (ENTRADA-006). |

Resumen Gemini:

- El rol de Researcher es el más expuesto a errores de manipulación de archivos grandes y malentendidos sobre el stack del framework.
- Las recomendaciones `G-001` y `M-005` resuelven los mayores "token-wasters" identificados en el piloto.
- Evidencia usada: `GEMINI_LOG.md` (ENTRADA-005, 006, 010, 014), `DRY_RUN_ALTERNATIVES.md` y `ONBOARDING.md`.

---

## Cierre esperado

Cuando los 3 agentes completen su review en este documento, el Governor puede:

1. Consolidar decisiones finales.
2. Crear un patch o ADR para el framework base.
3. Registrar cuales mejoras aplican globalmente y cuales solo aplican a `n8n-platform`.
