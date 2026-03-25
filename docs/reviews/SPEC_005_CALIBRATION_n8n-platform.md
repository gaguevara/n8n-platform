# SPEC-005 Calibration Review - n8n-platform

**Fecha:** 2026-03-24
**Proyecto:** `n8n-platform`
**Agente:** `CODEX`
**Framework:** multi-agente v4.6

> Nota: no encontre un archivo `SPEC-005` versionado dentro de este repositorio (`rg -n "SPEC-005|SPEC_005" .` sin matches). La calibracion se hace sobre la ejecucion real pedida y el comportamiento observado del engine/watcher en este proyecto.

## Findings

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

## Evidencia

### 1. Output real de `watch --once` (comando exacto solicitado)

Comando:

```powershell
python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . watch --once
```

Output observado:

```text
RONDA-001: state=ACTIVE
Baseline: CLAUDE=0, CODEX=0, GEMINI=0
Current: CLAUDE=19, CODEX=30, GEMINI=19
Pending: CLAUDE=19, CODEX=30, GEMINI=19
  CLAUDE: hallucination detected -> ### @CODEX - Implementer/DevOps
  CLAUDE: hallucination detected -> $env.ALERT_EMAIL_FROM
  CLAUDE: hallucination detected -> $env.ALERT_EMAIL_TO
  CLAUDE: hallucination detected -> $input.first(
  CLAUDE: hallucination detected -> .agent/
  CLAUDE: hallucination detected -> .claude/skills/*
  CLAUDE: hallucination detected -> .multiagent/core/*
  CLAUDE: hallucination detected -> /alerts
  CLAUDE: hallucination detected -> /api/v2/log/event/system
  CLAUDE: hallucination detected -> /api/v2/log/memory/event/system
  CLAUDE: hallucination detected -> /delcop*/odoo/db
  CLAUDE: hallucination detected -> /healthz
  CLAUDE: hallucination detected -> /sca
  CLAUDE: hallucination detected -> /syscheck
  CLAUDE: hallucination detected -> /vulnerability
  CLAUDE: hallucination detected -> 192.168.0.70:5678
  CLAUDE: hallucination detected -> AGENT_ROLES.md
  CLAUDE: hallucination detected -> API_KEY=\S+
  CLAUDE: hallucination detected -> CONTEXT.md
Traceback (most recent call last):
  File "C:\dev\Proyectos\n8n-platform\.multiagent\core\engine.py", line 1437, in <module>
    sys.exit(main())
             ^^^^^^
  File "C:\dev\Proyectos\n8n-platform\.multiagent\core\engine.py", line 1412, in main
    return cmd_watch(config_path, base, cmd_args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\dev\Proyectos\n8n-platform\.multiagent\core\engine.py", line 1173, in cmd_watch
    execute_watch_cycle(config_path, base)
  File "C:\dev\Proyectos\n8n-platform\.multiagent\core\engine.py", line 1009, in execute_watch_cycle
    print(f"  {warning}")
  File "C:\Users\gaguevara.AWS\AppData\Local\Programs\Python\Python312\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 47: character maps to <undefined>
```

### 2. Output real de `status`

Comando:

```powershell
python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . status
```

Output observado:

```text
=== n8n-platform - Agent Status ===

  CLAUDE: #19
    Header: ## ENTRADA-019 | 2026-03-23 | cross-review Wazuh fix — cierre de sesión
    > **Tipo:** Cross-review final de sesión
    > **Tarea:** Validar corrección Wazuh (Codex ENTRADA-026 + Gemini ENTRADA-017).

  CODEX: #30
    Header: ## ENTRADA-030 | 2026-03-24 | framework-v46-closeout
    > **Tipo:** Validacion final de trazabilidad
    > **Tarea:** Cerrar la aplicacion del framework v4.6 con verificacion final de contexto/logs/indice y 

  GEMINI: #19
    Header: ## ENTRADA-019 | 2026-03-24 | research + validation
    > **Tipo:** Validación y actualización de gobernanza
    > **Tarea:** Ejecución de tareas @GEMINI de Ronda 4 (Fase 1.8): validación matriz de skills, framework
```

### 3. Conteo de falsas detecciones

- En el output exacto del comando pedido antes del crash: `19` lineas de `hallucination detected`, `0` lineas de `ROLE_VIOLATION`.
- En la re-ejecucion diagnostica con UTF-8 para completar el render: `284` lineas de `hallucination detected`, `0` lineas de `ROLE_VIOLATION`.
- Juicio de calibracion:
  - `hallucination` falsos positivos: `284`
  - `role_violation` falsos positivos: `0`
  - Riesgo mayor detectado: `role_violation` tiene falsos negativos, no falsos positivos, porque no reporta nada aunque hay ediciones reales fuera de la zona configurada.

Razon del juicio: la muestra contiene strings como `GET /alerts`, `docker compose ...`, `/healthz`, `API_KEY=\S+`, `framework_version: 4.3`, `origin/main`, `Get-Content ...`, rutas temporales ya limpiadas y archivos reales existentes. Eso no es evidencia de alucinacion de archivos.

## 4. Archivos que modifico regularmente vs zona actual

Evidencia de recurrencia tomada de `docs/logs/CODEX_LOG.md` (conteo de menciones del path entre entradas previas):

| Archivo | Frecuencia observada | Dentro de `shared_zones` | Dentro de zona actual de `CODEX` |
|---------|----------------------|--------------------------|----------------------------------|
| `docs/governance/LOG_INDEX.md` | 31 | Si | No |
| `docs/governance/CONTEXT.md` | 28 | Si | No |
| `docs/logs/CODEX_LOG.md` | 21 | Si | No |
| `infra/docker-compose.local.yml` | 13 | No | No |
| `AGENTS.md` | 10 | No | No |
| `app/workflows/threat-intel-main.json` | 9 | No | No |
| `.env.example` | 9 | No | No |
| `ops/Makefile` | 9 | No | No |
| `infra/Dockerfile` | 9 | No | No |
| `GEMINI.md` | 4 | No | No |
| `.multiagent/adapters/n8n-platform.json` | 3 | No | No |

Otros archivos reales de trabajo de Codex que hoy tambien quedan fuera de zona:

- `app/code-nodes/ioc_normalizer.js`
- `scripts/import-workflows.sh`
- `docs/governance/FRAMEWORK_CAPABILITIES.md`

Conclusión: la zona actual de `CODEX` solo cubre bien trabajo sobre engine/tests Python, pero no cubre el rol operativo real de Implementer + DevOps en `n8n-platform`.

## 5. Cambios recomendados al adapter JSON para que `role_boundaries` sea preciso

### Ajustes necesarios

1. Quitar `*.md` de `CLAUDE`; es demasiado amplio y desvirtua ownership documental.
2. Ampliar `CODEX` para incluir las superficies que realmente opera:
   - `app/workflows/`
   - `app/code-nodes/`
   - `infra/`
   - `scripts/`
   - `ops/`
   - `.multiagent/adapters/`
   - `.env.example`
   - `.env.*.example`
   - `AGENTS.md`
   - `GEMINI.md`
   - `docs/governance/FRAMEWORK_CAPABILITIES.md`
3. Mover `docs/reviews/` a `shared_zones`, porque en este proyecto los reviews los puede escribir Claude, Gemini o Codex segun la tarea.
4. Mantener `docs/logs/`, `docs/governance/CONTEXT.md` y `docs/governance/LOG_INDEX.md` como compartidos.

### Propuesta concreta

```json
"role_boundaries": {
  "CLAUDE": [
    "docs/governance/",
    "docs/sdlc/",
    "SESSION_BOOTSTRAP.md",
    "CLAUDE.md"
  ],
  "CODEX": [
    ".multiagent/core/",
    ".multiagent/tests/",
    ".multiagent/adapters/",
    "app/workflows/",
    "app/code-nodes/",
    "infra/",
    "scripts/",
    "ops/",
    ".env.example",
    ".env.*.example",
    "AGENTS.md",
    "GEMINI.md",
    "docs/governance/FRAMEWORK_CAPABILITIES.md",
    "*.py",
    "pyproject.toml"
  ],
  "GEMINI": [
    "docs/knowledge/",
    "docs/architecture/",
    "docs/templates/",
    "docs/skills/",
    "docs/PHASE1_SUMMARY.md",
    "docs/EVIDENCIA_*.md",
    "docs/governance/ONBOARDING.md"
  ]
},
"shared_zones": [
  "docs/logs/",
  "docs/governance/CONTEXT.md",
  "docs/governance/LOG_INDEX.md",
  "docs/reviews/"
]
```

## 6. ¿El watcher podria hacer auto-commit seguro aqui?

Hoy, no de forma general.

### Motivos

- El parser de archivos afectados esta descalibrado y marca prosa/comandos como paths.
- La ronda puede abortar por encoding antes de terminar el render.
- `auto_commit()` no usa whitelist por proyecto; hace `git add` de todo `affected_files` resoluble.
- Este repo mezcla gobernanza, docs, code-nodes JS, workflows JSON, infra Docker, scripts shell y operaciones remotas en staging. El blast radius es alto.

### Auto-commit que si consideraria seguro

Solo para cambios de baja criticidad y artefactos de trazabilidad/documentacion, por ejemplo:

- `docs/logs/CODEX_LOG.md`
- `docs/governance/LOG_INDEX.md`
- `docs/governance/CONTEXT.md`
- `docs/reviews/*.md`
- `docs/governance/FRAMEWORK_CAPABILITIES.md`
- `.multiagent/adapters/*.json` solo si pasaron validacion JSON + engine status

### Lo que no pondria en auto-commit

- `app/workflows/*.json`
- `app/code-nodes/*.js`
- `infra/*.yml`
- `infra/Dockerfile`
- `scripts/*.sh`
- `ops/Makefile`
- `.env*.example`

## Conclusión

Para `n8n-platform`, SPEC-005 necesita calibrarse con tres cambios prioritarios:

1. Hacer el watcher UTF-8 safe en Windows para que `watch --once` no crashee.
2. Reemplazar la heuristica actual de `hallucination` por una extraccion de paths mas estricta o por un allowlist de formatos aceptados.
3. Ajustar `role_boundaries` al trabajo real de cada agente y no habilitar auto-commit general hasta tener whitelist explicita por proyecto.

---

# SPEC-005 Calibration Review — Governor (Claude)

**Fecha:** 2026-03-24
**Proyecto:** `n8n-platform`
**Agente:** `CLAUDE` (Governor + Architect)
**Framework:** multi-agente v4.6

---

## 1. Rondas de validación manual ejecutadas

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

## 2. ¿Es sostenible el flujo actual?

**Parcialmente, pero con límites claros:**

- **Funciona bien para:** cambios de gobernanza, documentación, configuración. El Governor puede validar diffs en segundos y dar aprobación informada.
- **No escala para:** rondas de dry-run operativo donde Codex ejecuta 5-7 comandos SSH y el Governor solo revisa logs post-facto. En ese caso, el cross-review es más burocracia que valor.
- **Bottleneck real:** El humano dice "valida" → Claude valida → humano dice "continúa". Este ciclo de 3 pasos agrega ~2-3 minutos de latencia por ronda que no aportan cuando los cambios son de bajo riesgo.

**Propuesta:** Clasificar las tareas en dos carriles:
- **Carril rápido (auto-dispatch):** Tareas de documentación, logs, limpieza, framework sync. No necesitan aprobación del Governor ni del humano.
- **Carril supervisado:** Tareas que modifican código (code-nodes, workflows), infraestructura (compose, Dockerfile) o credenciales. Requieren cross-review del Governor + ACK del humano.

## 3. ¿Confiaría en auto-dispatch con validation_state.json?

**Sí, bajo estas condiciones:**

| Condición | Justificación |
|---|---|
| `hallucination_count == 0` con parser calibrado | Si hay 284 FP como hoy, el sistema es inútil |
| `role_violations == 0` con zonas correctas | Las zonas actuales de Codex están mal — necesitan el ajuste que propuso Codex |
| `affected_files` limitados a whitelist del carril rápido | Logs, CONTEXT, LOG_INDEX, reviews — nunca workflows ni infra |
| Tests del engine pasan (`29/29`) | Garantía mínima de que el engine no regresionó |
| Deadman switch activo | Humano debe poder pausar en cualquier momento |
| `git diff --stat` muestra < 200 líneas | Cambios masivos requieren revisión humana |

**No confiaría** si:
- Un agente modifica archivos fuera de su zona sin explicar por qué
- El parser de hallucinations sigue generando FP (prioridad de fix para v4.7)
- No hay mecanismo de rollback (hoy no existe `git revert` automatizado en el engine)

## 4. ¿Es adecuado el deadman gradual para este proyecto?

**El esquema 5 → 10 → 20 rondas es razonable pero necesita ajuste por intervalo:**

Con `proto_watch` corriendo cada 3 minutos:
- 5 rondas = **15 min** hasta primer ACK → adecuado para sesiones activas
- 10 rondas = **30 min** → aceptable para trabajo autónomo
- 20 rondas = **60 min** → demasiado para este proyecto. Si un agente lleva 1 hora sin supervisión en n8n-platform, ya pudo haber reimportado un workflow roto en staging.

**Propuesta para n8n-platform:**
- Sesión activa: `5 → 10 → 15` rondas (15 → 30 → 45 min)
- Sesión desatendida (overnight): `10 → 20 → 30` rondas con auto-commit solo del carril rápido

## 5. Clasificación de tareas CONTEXT.md: auto-dispatch vs aprobación humana

### Seguras para auto-dispatch (carril rápido)

| Tarea | Riesgo | Por qué es segura |
|---|---|---|
| Registrar entrada en `*_LOG.md` | Bajo | Append-only, no modifica lógica |
| Actualizar `LOG_INDEX.md` | Bajo | Mecánico, derivado de logs |
| Actualizar `CONTEXT.md` (marcar [x]) | Bajo | Solo cambia estado de tarea |
| Crear/actualizar docs en `docs/knowledge/` | Bajo | No afecta runtime |
| Crear/actualizar docs en `docs/reviews/` | Bajo | No afecta runtime |
| `git pull` en R720 | Bajo | Lectura, no modifica |
| `engine.py status` / `proto_watch --status` | Nulo | Solo lectura |
| Limpiar temporales (`/tmp/*.json`) | Bajo | Archivos efímeros |

### Requieren aprobación del Governor (carril supervisado)

| Tarea | Riesgo | Por qué necesita revisión |
|---|---|---|
| Modificar `app/workflows/*.json` | Alto | Afecta runtime de n8n en staging |
| Modificar `app/code-nodes/*.js` | Alto | Lógica de negocio del pipeline |
| Reimportar workflow en staging | Alto | Cambia el runtime inmediatamente |
| Modificar `infra/*.yml` / Dockerfile | Alto | Puede romper el stack |
| Cambiar `.env.example` / `.env.staging.example` | Medio | Afecta documentación de secretos |
| Crear/modificar ADRs | Medio | Decisiones de arquitectura formales |
| Activar/desactivar workflows en n8n | Crítico | Impacto directo en producción |

### Requieren aprobación del humano (nunca auto-dispatch)

| Tarea | Riesgo | Por qué |
|---|---|---|
| Activar triggers cron en producción | Crítico | Impacto real en seguridad DELCOP |
| Crear recursos AWS (ECR, ECS, RDS) | Crítico | Costos y seguridad |
| Rotación de credenciales | Crítico | Puede romper conectividad |
| `git push --force` | Destructivo | Pérdida de historial |
| Cambiar `PROJECT_RULES.md` | Alto | SSOT del proyecto |

## Conclusión del Governor

El framework v4.6 es operativamente sólido para n8n-platform, pero el watcher (`watch --once`) no está calibrado para proyectos reales:

1. **284 falsos positivos de hallucination** invalidan completamente esa señal hoy
2. **role_zones** necesitan el ajuste que Codex propuso — coincido 100% con su propuesta
3. **Auto-dispatch es viable** para el carril rápido (docs, logs, limpieza) con whitelist explícita
4. **El Governor no debe ser bottleneck** — las tareas de bajo riesgo deben fluir sin mi aprobación
5. **El deadman es adecuado** con ajuste a 5→10→15 para sesiones activas

**Prioridad para v4.7:** Fix del parser de hallucinations > role_zones calibradas > whitelist de auto-commit por proyecto.
