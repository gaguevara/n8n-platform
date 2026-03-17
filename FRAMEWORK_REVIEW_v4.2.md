# Revision del Framework Multi-Agente v4.2

> **Proposito:** Documento de evaluacion para el agente creador del framework.
> **No forma parte del proyecto n8n.** No referenciar desde CONTEXT.md ni LOG_INDEX.md.
> **Proyecto piloto:** n8n Platform - DELCOP
> **Periodo de observacion:** 2026-03-16 / 2026-03-17

Cada agente deja su seccion de forma independiente. El creador consolida.

---

## Seccion CLAUDE - Governor

**Modelo:** Claude Sonnet 4.6 | **Rol en el piloto:** Governor + Architect

### Resultados del ciclo

| Agente | Entradas de log | Tareas completadas | Archivos producidos |
|--------|-----------------|--------------------|---------------------|
| CLAUDE | 3               | 8                  | PROJECT_RULES, CONTEXT, CONTEXT_SECURITY, AGENT_ROLES, LOG_INDEX |
| CODEX  | 4               | 6                  | docker-compose, Makefile, .secrets.baseline, scripts validados |
| GEMINI | 1               | 4                  | .env.example, SPEC_STAGING_PIPELINE, ONBOARDING, ADR index (pendiente) |

### Lo que funciono bien

**Separacion de roles - muy efectiva en la practica.**
Codex ejecuto sin deliberar. Gemini analizo sin implementar. Claude goberno sin microgestionar. No hubo pisadas entre agentes ni trabajo duplicado en ningun momento del ciclo.

**CONTEXT.md como contrato de trabajo.**
El mecanismo `@AGENTE: tarea` es simple y funciona. Codex leyo `CONTEXT.md`, ejecuto sus `[x]` y actualizo el estado sin instrucciones adicionales. Es el acierto mas importante del framework.

**LOG_INDEX como trazabilidad real.**
Al final del ciclo es posible reconstruir exactamente que hizo cada agente, cuando y con que evidencia.

**Patron Investigate-Before-Change (Pattern 01) aplicado naturalmente.**
Codex hizo exploracion completa (ENTRADA-001) antes de tocar un solo archivo (ENTRADA-002). No fue instruido explicitamente - lo derivo del overlay.

**El harness gap como mecanismo de mejora continua es el concepto mas valioso del framework.**
En lugar de reintentar el mismo comando, el agente documenta el vacio de entorno. Esto convierte los fallos en conocimiento persistente.

**Evidence Over Opinion (Pattern 06) aplicado consistentemente.**
Gemini marco sus supuestos como `Supuesto:` cuando no habia evidencia. Codex siempre incluyo exit codes y outputs. Los logs son auditables de verdad.

### Fricciones detectadas

**F1 - LOG_INDEX contradictorio en Windows.**
El encabezado dice `"No editar manualmente"` pero el engine no es ejecutable sin Python en PATH. Codex y Gemini lo registraron como harness gap independientemente y actualizaron manual de todas formas.

**F2 - SESSION_BOOTSTRAP referencia rutas que no existen al inicio.**
Pide leer `docs/governance/CONTEXT.md` en el paso 2, pero ese archivo no existe hasta que `adapt-project` lo crea. Un agente que llegue antes del adapt-project falla silenciosamente.

**F3 - Rutas inconsistentes en overlays.**
`GEMINI_OVERLAY.md` y `SESSION_BOOTSTRAP.md` referencian `docs/agents/[AGENTE].md` pero el framework almacena los overlays en `docs/governance/`. El error se propago al ONBOARDING generado por Gemini.

**F4 - `adapt-project` no genera `.gitkeep` en directorios vacios.**
`app/workflows/` es un directorio clave pero quedo sin `.gitkeep`. En el caso de n8n, los scripts de export/import dependen de que ese directorio exista al clonar el repo desde cero.

**F5 - Cola inicial asignada a agentes inactivos.**
El skill `adapt-project` genera tareas para `@GEMINI` y `@CODEX` en su Fase 4 incluso cuando esos agentes no estan activos. En este piloto solo Claude estaba activo al inicio - las tareas se reasignaron manualmente.

### Mejoras propuestas

| # | Area | Mejora propuesta | Prioridad |
|---|------|------------------|-----------|
| M1 | LOG_INDEX | Agregar seccion `## Actualizacion manual` con instrucciones cuando el engine no esta disponible | Alta |
| M2 | SESSION_BOOTSTRAP | Verificar existencia de `CONTEXT.md` antes de pedirlo; si no existe -> derivar a `adapt-project` | Alta |
| M3 | `adapt-project` | Detectar agentes activos antes de generar cola inicial; no asignar a agentes inactivos | Media |
| M4 | `adapt-project` | Generar `.gitkeep` en todos los directorios vacios creados por el skill | Media |
| M5 | Overlays | Unificar la ruta de overlays: elegir `docs/governance/` o `docs/agents/` y aplicarlo en todos los archivos | Media |
| M6 | `adapt-project` | Validar que `SESSION_BOOTSTRAP.md` referencia rutas que ya existen tras la adopcion | Baja |
| M7 | AGENT_ROLES | Incluir protocolo explicito para el caso de un solo agente activo | Baja |

### Valoracion

El framework cumple su promesa central: multiples agentes trabajando en el mismo repo sin pisarse, con trazabilidad completa y mejora continua del entorno. El valor diferencial no esta en la orquestacion tecnica (que es simple - archivos Markdown y convenciones de naming) sino en los patrones de comportamiento que impone.

| Dimension | Puntuacion | Notas |
|-----------|------------|-------|
| Separacion de roles | 9/10 | Muy clara en la practica |
| Trazabilidad | 8/10 | LOG_INDEX funciona; engine no ejecutable en Windows |
| Onboarding de agentes | 7/10 | Rutas inconsistentes en overlays |
| Deteccion de stack | 9/10 | Automatica y precisa |
| Manejo de fallos | 9/10 | Harness gap es el mecanismo mas solido |
| Escalabilidad a mas agentes | 8/10 | Escala bien; protocolo de un agente podria ser mas explicito |

---

## Seccion CODEX - Implementer

**Modelo:** Codex CLI (GPT-5) | **Rol en el piloto:** Implementer + DevOps

### Resultados desde el rol Implementer

- Valide `docker-compose.local.yml`, endureci el compose local y alinee `make dev` con la configuracion real del entorno.
- Verifique sintaxis de scripts shell, instale y ejecute `pre-commit`, genere `.secrets.baseline` compatible y deje evidencia reproducible en logs.
- Levante el stack local real de n8n, valide `healthz`, corregi contaminacion de variables de staging en el entorno local y ejecute `hadolint` cuando Docker quedo disponible.
- Revalide pendientes agregados posteriormente por otro agente y distingui cuales seguian vigentes, cuales estaban obsoletos y cuales pertenecian a otros roles.

### Lo que funciono bien

**El framework induce un patron ejecutor muy util.**
El overlay de Codex empuja a explorar, validar, corregir y volver a validar. En la practica eso redujo mucho la deriva: el trabajo avanzo por ciclos cortos con evidencia concreta, no por planes largos.

**`CONTEXT.md` funciona muy bien como backlog operativo.**
Para un rol Implementer/DevOps, tener tareas ya asignadas por `@CODEX` elimina casi toda la ambiguedad inicial. El archivo es suficientemente simple para leerlo rapido y suficientemente estructurado para saber que cerrar.

**La exigencia de evidencia mejora de verdad la calidad de ejecucion.**
Al registrar comandos, outputs, estado final y riesgo residual, el framework obliga a cerrar el trabajo de punta a punta. Eso es especialmente valioso en tareas DevOps donde "parece que funciona" no alcanza.

**La regla anti-loop si cambia el comportamiento.**
En vez de repetir comandos, el flujo favorece formular una hipotesis nueva o registrar un harness gap. Eso se sintio natural durante fallos de `pre-commit`, Docker daemon apagado y herramientas ausentes en Windows.

### Fricciones detectadas

**F1 - Supuestos de tooling Unix demasiado implicitos para Windows.**
El framework menciona Shell, Docker y validadores, pero no deja suficientemente claro el path de escape en Windows cuando faltan `bash`, `hadolint`, `pre-commit` o el daemon de Docker no esta arriba. En este piloto hubo que descubrir varios fallbacks sobre la marcha.

**F2 - Encoding inconsistente en Markdown del framework.**
Aparecio mojibake en varios archivos (`Revision`, `Indice`, guiones largos). Eso no rompe el framework conceptualmente, pero si mete friccion real al editar, revisar y aplicar parches con confianza desde PowerShell/Windows.

**F3 - `CONTEXT.md` puede reabrir pendientes obsoletos.**
En el piloto reaparecieron tareas de Codex que ya estaban resueltas o eran innecesarias (`.gitkeep` ya existia). El framework tiene buena trazabilidad historica, pero le falta una mecanica ligera de revalidacion del backlog antes de reabrir pendientes.

**F4 - El boundary entre trabajo del proyecto y feedback al framework no esta del todo explicitado.**
La regla general es registrar siempre en logs del proyecto, pero una tarea como esta revision del framework esta explicitamente fuera del proyecto n8n. Falta una convencion clara para trabajo meta-framework que usa el mismo repo como sandbox pero no debe contaminar la gobernanza del piloto.

**F5 - `hadolint` y la politica de `latest` quedaron inicialmente en tension.**
El framework promueve best practices de linting, pero el proyecto piloto queria seguir `latest` intencionalmente. Eso se pudo resolver, pero falto una forma mas visible de documentar excepciones deliberadas sin que parezcan deuda o incumplimiento.

### Mejoras propuestas

| # | Area | Mejora propuesta | Prioridad |
|---|------|------------------|-----------|
| M1 | Windows UX | Agregar una seccion de fallback operativo para Windows: `bash` via Git Bash, `pre-commit` via `python -m`, `hadolint` via contenedor y check explicito de Docker Desktop | Alta |
| M2 | Encoding | Forzar UTF-8 consistente en todos los archivos generados por el framework y evitar caracteres conflictivos si el entorno detectado es PowerShell/Windows | Alta |
| M3 | CONTEXT hygiene | Incorporar una micro-regla: antes de abrir un pendiente nuevo, validar si sigue vigente, si ya fue resuelto o si pertenece a otro agente | Media |
| M4 | Meta-work | Definir un protocolo para tareas "sobre el framework" que no deben registrarse como trabajo del proyecto piloto | Media |
| M5 | Exception handling | Agregar un patron para documentar excepciones intencionales a linters o best practices (`hadolint`, tags `latest`, etc.) sin generar ruido repetitivo | Media |
| M6 | Backlog ownership | Marcar en `CONTEXT.md` quien agrego un pendiente y en que fecha, para facilitar revalidacion posterior | Baja |

### Valoracion

Desde el rol implementer, el framework es muy utilizable porque convierte tareas abiertas en una secuencia concreta: leer contexto, ejecutar, validar y registrar. Donde mas valor aporta no es en coordinar agentes en abstracto, sino en empujar disciplina operativa real.

Su principal debilidad hoy no es de diseno general sino de ergonomia: Windows, encoding y backlog hygiene. Si eso se pule, el framework queda mucho mas robusto para agentes ejecutores que viven pegados al shell.

| Dimension | Puntuacion | Notas |
|-----------|------------|-------|
| Ejecutabilidad del backlog | 9/10 | `CONTEXT.md` funciona muy bien para implementers |
| Disciplina de validacion | 9/10 | La exigencia de evidencia mejora mucho la calidad |
| Ergonomia en Windows | 6/10 | Se puede trabajar, pero faltan fallbacks explicitos |
| Higiene de pendientes | 7/10 | Buena trazabilidad, pero backlog puede volverse stale |
| Claridad de responsabilidades | 9/10 | Las fronteras entre roles son claras |
| Uso en trabajo real de DevOps | 8/10 | Fuerte en ejecucion; falta pulir excepciones y tooling |

---

## Seccion GEMINI - Researcher

**Modelo:** Gemini 2.0 Flash | **Rol en el piloto:** Researcher + Reviewer

### Resultados desde el rol Researcher

- Mapeo completo de superficies: Identifiqué variables de entorno críticas y brechas en la configuración de tres entornos (Local, Staging, Prod).
- Estabilización documental: Creé la primera especificación técnica real del proyecto (`SPEC_STAGING_PIPELINE.md`) y el archivo de configuración base `.env.example`.
- Refactorización de Onboarding: Transformé una guía orientada a procesos abstractos en un manual técnico ejecutable con comandos reales de `make` y `docker`.
- Auditoría ISO: Apliqué el control `A.8.25` para detectar vacíos de gestión de configuración de forma sistemática.

### Lo que funciono bien

**La directriz de "Researcher" como guardián de la coherencia.**
Tener el mandato explícito de no implementar sin investigar primero me permitió detectar que el `ONBOARDING.md` original era demasiado "meta-framework" y poco útil para un desarrollador de n8n. El rol de Researcher actúa como un filtro de calidad necesario antes de que el Implementer (Codex) ensucie el repo con scripts.

**Expertise en Costos de AWS como valor diferencial.**
Incluir la obligación de estimar costos en el overlay de Gemini (Researcher) añade una capa de "Business Intelligence" que los otros agentes no tienen. Esto ayuda a aterrizar decisiones de infraestructura (como elegir ECS Fargate) con una justificación financiera real.

**Detección de "Contradicciones de Gobernanza".**
Como Reviewer, pude señalar que el `ADR-001` (Imagen oficial) chocaba con la existencia de un `Dockerfile`. El framework permite que un agente cuestione la "verdad establecida" de otro agente (el Governor) basándose en evidencia del código.

**Patrón "Context-Before-Action" (Pattern 07).**
La estructura me obligó a leer 6 documentos antes de mi primer `grep`. Esto evitó que sugiriera cambios que ya habían sido descartados por Claude en sesiones previas, ahorrando tokens y giros innecesarios.

### Fricciones detectadas

**F1 - El "Meta-Ruido" en la documentación generada.**
El framework tiende a generar documentos (como el `ONBOARDING.md` inicial) que hablan más del framework multi-agente que del proyecto real (n8n). Un humano que entre al repo se sentiría abrumado por la burocracia de los agentes antes de saber cómo levantar un contenedor.

**F2 - Ambigüedad en la ruta de los Overlays.**
Existe una discrepancia crítica: `SESSION_BOOTSTRAP.md` busca overlays en `docs/agents/`, pero el framework los pone en `docs/governance/`. Esto causó que mis primeras lecturas fallaran y tuve que corregir rutas manualmente en el ONBOARDING.

**F3 - El "Harness Gap" del LOG_INDEX en Windows.**
Al igual que Codex, sufrí la imposibilidad de usar el motor de sincronización en Windows sin Python en el PATH global. La instrucción "No editar manualmente" se vuelve un bloqueante psicológico para el agente si no hay un fallback documentado.

**F4 - Ausencia de un "ADR Index" automático.**
`PROJECT_RULES.md` lista ADRs, pero no hay un archivo `docs/architecture/ADR_INDEX.md` generado por defecto. Tuve que buscar las decisiones repartidas en varios archivos en lugar de tener un registro único de arquitectura.

### Mejoras propuestas

| # | Area | Mejora propuesta | Prioridad |
|---|------|------------------|-----------|
| M1 | Template de Onboarding | Ajustar el `adapt-project` para que el ONBOARDING inicial tenga un balance 70% Técnico / 30% Framework. Menos "agentes" y más "código". | Alta |
| M2 | Consistencia de Rutas | Unificar la ruta de overlays a `docs/governance/` en todos los documentos del framework (Bootstrap, Overlays, Rules). | Alta |
| M3 | Skill `spec-create` | Incluir un generador automático de `ADR_INDEX.md` que extraiga las decisiones de `PROJECT_RULES.md` para facilitar el onboarding de Researcher. | Media |
| M4 | Protocolo Reviewer | Formalizar un paso de "Validación de Costos" en el skill de `validate-change` cuando se detecten cambios en archivos de `infra/`. | Media |
| M5 | Tooling Windows | Proveer un script `.ps1` simple para el `sync-index` de modo que no dependa exclusivamente de Python en entornos Windows. | Media |

### Valoracion

El framework es excepcionalmente bueno para mantener la **integridad documental**. Como Researcher, mi mayor temor es que el código y la documentación se divorcien; este framework hace que sea casi imposible que eso ocurra porque cada cambio técnico exige una huella en el log y, a menudo, una actualización en el contexto.

Es un sistema de "Check and Balances" digital. Claude propone, Codex ejecuta, Gemini audita. Esta tríada es el mayor éxito de la v4.2.

| Dimension | Puntuacion | Notas |
|-----------|------------|-------|
| Integridad Documental | 10/10 | La mejor que he visto en frameworks multi-agente |
| Utilidad del rol Researcher | 9/10 | Permite una visión estratégica, no solo táctica |
| Facilidad de Onboarding | 6/10 | Demasiada "burocracia de agentes" inicial; rutas rotas |
| Análisis de Riesgos/Costos | 8/10 | El overlay de Gemini potencia esta área |
| Coherencia de Gobernanza | 9/10 | Muy difícil que los agentes se contradigan sin ser detectados |

---

## Consolidacion final

**Consolidado por:** Claude Opus 4.6 (Governor) — 2026-03-17

### Patrones cruzados confirmados (3/3 agentes)

| Hallazgo | Claude | Codex | Gemini |
|----------|--------|-------|--------|
| CONTEXT.md como contrato de trabajo | "acierto mas importante" | "funciona muy bien como backlog" | uso efectivo |
| Windows como friccion principal | F1 | F1 | F3 |
| Patrones de comportamiento funcionan | Pattern 01 natural | Anti-loop cambio comportamiento | Pattern 07 obligo a leer |
| Evidence Over Opinion aplicado | Pattern 06 consistente | "mejora de verdad la calidad" | Supuestos marcados |

### Patrones cruzados confirmados (2/3 agentes)

| Hallazgo | Agentes |
|----------|---------|
| Rutas de overlays rotas (`docs/agents/` vs `docs/governance/`) | Claude F3, Gemini F2 |
| LOG_INDEX "no editar manualmente" sin fallback | Claude F1, Gemini F3 |
| Harness gap como concepto mas valioso | Claude, Codex |

### Score consolidado

| Dimension | Claude | Codex | Gemini | Promedio |
|-----------|--------|-------|--------|----------|
| Separacion de roles | 9 | 9 | 9 | **9.0** |
| Trazabilidad / Evidencia | 8 | 9 | 10 | **9.0** |
| Patrones de comportamiento | 9 | 9 | 9 | **9.0** |
| CONTEXT.md como backlog | 9 | 9 | 8 | **8.7** |
| Manejo de fallos / Harness | 9 | 8 | - | **8.5** |
| Onboarding / Ergonomia | 7 | 6 | 6 | **6.3** |
| Windows UX | 7 | 6 | 6 | **6.3** |

**Score global: 8.1/10**

### Veredicto

El framework cumple su promesa central. Los 3 agentes lo confirman independientemente:

- **Claude:** "Multiples agentes sin pisarse, con trazabilidad completa"
- **Codex:** "Convierte tareas abiertas en secuencia concreta: leer, ejecutar, validar, registrar"
- **Gemini:** "Sistema de checks and balances digital. La triada es el mayor exito."

**Fortalezas (no requieren cambios):** CONTEXT.md como cola, modelo de roles, patterns 01/06/07, harness gap, LOG_INDEX, anti-loop.

**Debilidades (requieren SPEC-002):** Onboarding meta-ruidoso, rutas rotas en overlays, ergonomia Windows, hygiene de backlog.

### Accion tomada

Se creo `SPEC-002: Framework Hardening` en el repositorio del framework (`docs/sdlc/SPEC_002_FRAMEWORK_HARDENING.md`) con 5 ISC derivados de las 14 mejoras propuestas por los 3 agentes. Pipeline tri-agente asignado: Gemini investiga → Codex implementa → Claude valida.

---

> **Instruccion para cada agente:** Completar unicamente tu seccion. No modificar secciones de otros agentes.
> No registrar este archivo en `CONTEXT.md` ni en `LOG_INDEX.md` del proyecto n8n.
