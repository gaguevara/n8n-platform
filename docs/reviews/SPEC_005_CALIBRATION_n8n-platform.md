# SPEC-005 Calibration Review - n8n-platform

**Fecha:** 2026-03-24
**Proyecto:** `n8n-platform`
**Agente:** `CODEX`
**Framework:** multi-agente v4.6

> Nota: no encontre un archivo `SPEC-005` versionado dentro de este repositorio (`rg -n "SPEC-005|SPEC_005" .` sin matches). La calibracion se hace sobre la ejecucion real pedida y el comportamiento observado del engine/watcher en este proyecto.

## Findings (Codex)

### 1. Critico - `watch --once` falla en Windows por encoding y no completa la ronda

El comando exacto pedido falla en esta estacion por `UnicodeEncodeError` al imprimir `CONTEXT.md → Pendientes inmediatos` bajo `cp1252`. Eso hace que el output exigido por SPEC-005 sea incompleto en Windows por defecto y deja la ronda a medio render.

### 2. Critico - El detector de `hallucination` esta severamente descalibrado para este proyecto

Con una re-ejecucion diagnostica usando `PYTHONIOENCODING=utf-8`, el watcher emitio `284` lineas de `hallucination detected` y `0` `ROLE_VIOLATION`. La evidencia observada indica que los `284/284` warnings de hallucination son falsos positivos para este repo: mezcla headings, endpoints HTTP, rutas temporales, comandos shell, variables, versiones y archivos reales existentes como si todos fueran archivos faltantes.

Peor aun, el engine corta la evaluacion del agente cuando encuentra hallucinations, asi que una tormenta de falsos positivos impide revisar `role_boundaries` y tambien bloquea cualquier auto-commit posterior de esa ronda.

### 3. Alto - `role_boundaries` de `CODEX` no reflejan el trabajo real del proyecto

La zona actual de `CODEX` solo cubre `.multiagent/core/`, `.multiagent/tests/`, `.claude/skills/`, `*.py` y `pyproject.toml`. En este proyecto yo modifico regularmente workflows, compose, Dockerfile, Makefile, env examples, bootstrap files y el adapter mismo. Hoy casi todo eso queda fuera de zona.

Ademas, `CLAUDE` tiene `*.md`, que en la practica le abre cualquier Markdown del repo y vuelve poco precisa la calibracion de ownership documental.

### 4. Medio - `auto_commit` no es seguro todavia para este repo

En el estado actual, no. El watcher hace `git add` de `affected_files` mas `LOG_INDEX` y el log del agente, sin whitelist especifica por proyecto. Con el parser actual, eso es demasiado amplio para un repositorio que mezcla gobernanza, docs, workflows n8n, scripts, compose, adapters y artefactos temporales.

---

# SPEC-005 Calibration Review — Governor (Claude)

**Fecha:** 2026-03-24
**Proyecto:** `n8n-platform`
**Agente:** `CLAUDE` (Governor + Architect)
**Framework:** multi-agente v4.6

---

## 1. Rondas de validación manual ejecutadas (Claude)

En este proyecto ejecuté **20 rondas de cross-review** (ENTRADA-001 a ENTRADA-019 + la presente) a lo largo de 8 días (2026-03-16 a 2026-03-24).

| Ronda | Tipo | Agentes revisados | Duración estimada |
|---|---|---|---|
| ENTRADA-001 | Setup framework | Solo Claude | ~5 min |
| ENTRADA-002 | Distribución multi-agente | Solo Claude | ~3 min |
| ENTRADA-003 | Cross-review Codex+Gemini | Codex 001-002, Gemini 001 | ~8 min |
| ENTRADA-004 | Upgrade v4.3 | Solo Claude | ~3 min |
| ENTRADA-005 | Integración Threat Intel | Codex 007-008, Gemini 003 | ~12 min |
| ENTRADA-006 | Harness fix CONTEXT.md | Solo Claude | ~2 min |
| ENTRADA-007 | Aprobación SPEC AWS | Gemini 005 | ~4 min |
| ENTRADA-008 | Cross-review staging | Codex 012-014 | ~5 min |
| ENTRADA-009 | Cross-review Rondas 1-3 parcial | Codex 015-016, Gemini 007-008 | ~6 min |
| ENTRADA-010 | Cierre review framework | Codex 021-023, Gemini 015-016 | ~5 min |
| ENTRADA-011-015 | ADR-009/010/011 + review framework | Todos | ~15 min total |
| ENTRADA-016-017 | Cross-review normalizers + Codex 024-025 | Codex, Gemini | ~8 min |
| ENTRADA-018 | Hallazgo Wazuh + tareas últma ronda | Codex 026, Gemini 017 | ~10 min |
| ENTRADA-019 | Cierre sesión + Wazuh fix | Codex 026, Gemini 017 | ~5 min |
| ENTRADA-020 (esta) | SPEC-005 Calibración | Codex 029-030, Gemini 019 | ~10 min |

**Total:** ~101 minutos de validación manual en 8 días.
**Promedio:** ~5 min por ronda de cross-review.

## 2. ¿Es sostenible el flujo actual? (Claude)

**Parcialmente, pero con límites claros:**

- **Funciona bien para:** cambios de gobernanza, documentación, configuración. El Governor puede validar diffs en segundos y dar aprobación informada.
- **No escala para:** rondas de dry-run operativo donde Codex ejecuta 5-7 comandos SSH y el Governor solo revisa logs post-facto. En ese caso, el cross-review es más burocracia que valor.
- **Bottleneck real:** El humano dice "valida" → Claude valida → humano dice "continúa". Este ciclo de 3 pasos agrega ~2-3 minutos de latencia por ronda que no aportan cuando los cambios son de bajo riesgo.

**Propuesta:** Clasificar las tareas en dos carriles:
- **Carril rápido (auto-dispatch):** Tareas de documentación, logs, limpieza, framework sync. No necesitan aprobación del Governor ni del humano.
- **Carril supervisado:** Tareas que modifican código (code-nodes, workflows), infraestructura (compose, Dockerfile) o credenciales. Requieren cross-review del Governor + ACK del humano.

## 3. ¿Confiaría en auto-dispatch con validation_state.json? (Claude)

**Sí, bajo estas condiciones:**

| Condición | Justificación |
|---|---|
| `hallucination_count == 0` con parser calibrado | Si hay 284 FP como hoy, el sistema es inútil |
| `role_violations == 0` con zonas correctas | Las zonas actuales de Codex están mal — necesitan el ajuste que propuso Codex |
| `affected_files` limitados a whitelist del carril rápido | Logs, CONTEXT, LOG_INDEX, reviews — nunca workflows ni infra |
| Tests del engine pasan (`29/29`) | Garantía mínima de que el engine no regresionó |
| Deadman switch activo | Humano debe poder pausar en cualquier momento |
| `git diff --stat` muestra < 200 líneas | Cambios masivos requieren revisión humana |

## 4. Clasificación de tareas CONTEXT.md: auto-dispatch vs aprobación humana (Claude)

### Seguras para auto-dispatch (carril rápido)
- Registrar entradas en logs, `LOG_INDEX`, `CONTEXT.md`.
- Crear/actualizar docs en `docs/knowledge/` y `docs/reviews/`.
- Limpieza de temporales.

### Requieren aprobación del Governor (carril supervisado)
- Modificar `app/workflows/`, `app/code-nodes/`, `infra/`, `scripts/`, `ops/`.
- Crear/modificar ADRs.

### Requieren aprobación del humano (nunca auto-dispatch)
- Activar cron triggers en producción.
- Crear infraestructura real en AWS.
- Rotación de credenciales reales.

---

# SPEC-005 Calibration Review — Researcher/Reviewer (Gemini)

**Fecha:** 2026-03-24
**Proyecto:** `n8n-platform`
**Agente:** `GEMINI` (Researcher + Reviewer)
**Framework:** multi-agente v4.6

---

## 1. Métricas de Entrada (Datos Reales)

Al cierre de esta sesión de calibración, el conteo de entradas oficiales es:

| Agente | Entradas | Fuente |
|---|---|---|
| **CLAUDE** | 20 | `docs/logs/CLAUDE_LOG.md` |
| **CODEX** | 32 | `docs/logs/CODEX_LOG.md` |
| **GEMINI** | 20 | `docs/logs/GEMINI_LOG.md` |

**Observación:** El desbalance de Codex se debe a la alta frecuencia de tareas operativas (validación runtime, SSH a staging, re-import de workflows) que requieren registrar evidencia detallada paso a paso. Mi rol (Gemini) se concentra en bloques de investigación más extensos que resultan en menos entradas pero de mayor densidad documental.

## 2. Falsos Positivos del Watcher

- **Hallucinations:** Coincido con Codex en que el detector de alucinaciones está descalibrado. Confunde comandos shell, fragmentos de código n8n y endpoints de red con archivos faltantes. Esto genera ruido cognitivo innecesario.
- **Role Violations:** No he observado falsos positivos de `ROLE_VIOLATION`. Sin embargo, el riesgo real es el **falso negativo**: la zona actual de Gemini es tan restrictiva que si edito una SPEC en `docs/sdlc/` (que es mi tarea principal), el engine no me marca violación si esa zona no está configurada, o me marca violación legítima pero necesaria.

## 3. Zonas de Archivo Reales (Gemini)

Para este proyecto, mi superficie de trabajo efectiva abarca:
- `docs/logs/GEMINI_LOG.md`
- `docs/knowledge/` (Runbooks, checklists)
- `docs/sdlc/` (Especificaciones técnicas como `SPEC_AWS_PRODUCTION.md`)
- `docs/architecture/` (ADR Index)
- `docs/governance/GEMINI_OVERLAY.md`
- `docs/PHASE1_SUMMARY.md` y `docs/EVIDENCIA_*.md`
- `GEMINI.md`

**Desajuste detectado:** El adapter actual no me da ownership explícito sobre `docs/sdlc/`, lo cual es mi zona de mayor valor estratégico.

## 4. Evaluación del Deadman Switch (5 rondas)

**Veredicto:** **Adecuado.**

En tareas de investigación profunda (como mapear endpoints de FortiGate o Wazuh), 5 rondas permiten avanzar lo suficiente para tener una propuesta sólida sin perder el contacto con el Governor o el Humano. Para tareas más mecánicas, puede sentirse lento, pero en este proyecto "brownfield" con infraestructura real externa, la cautela de las 5 rondas es un salvavidas contra derivas de configuración.

## 5. Cuello de Botella Detectado

- **Validación de Infraestructura Inexistente:** Mi mayor cuello de botella es cuando se me asigna "validar secretos" o "revisar networking" de algo que aún no ha sido creado por Codex o el usuario. Esto me obliga a generar "Supuestos" que luego deben ser re-validados, duplicando el trabajo.
- **Sync de Documentación:** A veces Codex genera evidencia técnica en archivos que yo debería supervisar (como el Runbook), creando fricción sobre quién es el "dueño" del documento final.

## 6. ¿Funcionaría el Self-Dispatch? (Gemini)

**Sí, pero limitado a Investigación y Documentación.**

- **Viabilidad:** Gemini puede ejecutar proactivamente tareas de mapeo, redacción de specs y auditoría documental sin intervención humana constante.
- **Riesgos:** 
    1. **Desincronización:** Documentar una spec de AWS que Codex no puede implementar por limitaciones de permisos IAM.
    2. **Sobreescritura:** Si Codex y yo auto-despachamos ediciones en el mismo archivo de gobernanza (ej. `CONTEXT.md`), el riesgo de conflicto de merge es alto si no hay un Governor orquestando el turno.

**Conclusión:** El auto-dispatch debe estar vinculado al **Lock de Turno** del framework para evitar colisiones en archivos compartidos como `CONTEXT.md`.

---
*Generado por Gemini (Researcher + Reviewer) — 2026-03-24*
