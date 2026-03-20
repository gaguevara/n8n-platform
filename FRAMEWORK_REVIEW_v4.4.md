# Framework Multi-Agente — Reporte de Campo v4.2→v4.4

**Proyecto piloto:** n8n Platform DELCOP
**Periodo:** 2026-03-16 al 2026-03-20 (5 dias)
**Evaluador:** Claude Opus 4.6 (Governor)
**Destinatario:** Agente creador del framework
**Proposito:** Hallazgos, metricas, bugs y mejoras propuestas tras uso real en produccion

---

## 1. Metricas de adopcion

| Metrica | Valor |
|---------|-------|
| Commits totales en el periodo | 22 |
| Entradas de log (CLAUDE) | 9 |
| Entradas de log (CODEX) | 12+ |
| Entradas de log (GEMINI) | 6 |
| ADRs generados | 9 |
| SPECs creados | 3 (STAGING_PIPELINE, THREAT_INTEL, AWS_PRODUCTION) |
| Cross-reviews ejecutados | 8+ |
| Harness gaps documentados | 7 |
| Tareas completadas (CONTEXT.md) | 40+ |
| Tareas abiertas actuales | 18 (Fase 1.5 + Fase 2) |
| Skills comunitarios instalados | 3 (docker-security-guide, aws-ecs-fargate, postgres-patterns) |
| Versiones del framework aplicadas | 3 (v4.2 → v4.3 → v4.4) |

---

## 2. Que funciono bien

### 2.1 Separacion de roles — excelente en la practica
Codex ejecuto sin deliberar. Gemini analizo sin implementar. Claude goberno sin microgestionar. Cero trabajo duplicado entre agentes en 22 commits.

### 2.2 CONTEXT.md como contrato de trabajo
El mecanismo `@AGENTE: tarea` es el acierto mas importante del framework. Codex lee CONTEXT.md, ejecuta sus `[ ]`, y actualiza el estado sin instrucciones adicionales. Es asincronico por naturaleza y funciona.

### 2.3 LOG_INDEX como trazabilidad real
Al final de cada ciclo es posible reconstruir exactamente que hizo cada agente, cuando y con que evidencia. Esto diferencia al framework de cualquier sistema de chat.

### 2.4 Harness gap como mecanismo de mejora continua
En lugar de reintentar el mismo comando, los agentes documentan el vacio de entorno. Convierte fallos en conocimiento persistente. Es la idea mas valiosa del framework.

### 2.5 Cross-review efectivo
El Governor detecto y corrigio 5 errores de otros agentes antes de que llegaran a main:
- Codex: cookie `secure: true` en staging HTTP (fix en commit `c338c93`)
- Gemini: reglas eliminadas de PROJECT_RULES durante upgrade v4.4
- Gemini: log historico truncado (ENTRADA-001-004 perdidas)
- Codex: placeholders no funcionales en staging (code-nodes sin persistencia)
- Gemini: referencia incorrecta en ONBOARDING (`docs/agents/` vs `docs/governance/`)

### 2.6 Patron anti-loop aplicado
Codex registro el harness gap de `detect-secrets` (version 1.5 vs 1.4) y resolvio con hipotesis nueva en un intento, en lugar de reintentar a ciegas.

---

## 3. Bugs encontrados (corregidos en v4.3/v4.4)

| Bug | Version afectada | Corregido en | Descripcion |
|-----|------------------|--------------|-------------|
| B-001 | v4.2 | v4.3 | SESSION_BOOTSTRAP no verificaba si CONTEXT.md existia antes de pedir leerlo |
| B-002 | v4.2 | v4.3 | adapt-project asignaba tareas a agentes inactivos |
| B-003 | v4.2 | v4.3 | Directorios vacios sin .gitkeep (app/workflows/ no se clonaba) |
| B-004 | v4.2 | v4.4 | Sin git pull obligatorio — agentes trabajaban con CONTEXT.md desactualizado |
| B-005 | v4.2-v4.3 | v4.4 | ONBOARDING referenciaba `docs/agents/` en lugar de `docs/governance/` |

---

## 4. Bugs abiertos (no corregidos aun)

### B-006: Agentes truncan logs historicos
**Severidad:** Media
**Descripcion:** Gemini reemplazo las ENTRADA-001 a ENTRADA-004 con `...` durante una edicion del log, perdiendo 146 lineas de trazabilidad historica.
**Causa raiz:** No hay regla mecanica que impida editar entradas previas de un log. Los agentes solo deben AGREGAR al final.
**Correccion propuesta:** Agregar a PROJECT_RULES §9 o al overlay de cada agente:
```
REGLA: Los logs de agentes son append-only.
Nunca editar ni truncar entradas anteriores.
Solo agregar nuevas entradas al final del archivo.
```

### B-007: Agentes eliminan reglas existentes al agregar nuevas
**Severidad:** Alta
**Descripcion:** Gemini al agregar las reglas v4.4 a PROJECT_RULES §6 elimino 3 reglas preexistentes (npm dependencies, .env.example sync, auth high-risk).
**Causa raiz:** Los agentes hacen rewrite de secciones completas en lugar de append. No hay mecanismo que proteja reglas existentes.
**Correccion propuesta:** Agregar a SESSION_BOOTSTRAP o al skill adapt-project:
```
REGLA: Al modificar PROJECT_RULES.md, NUNCA reemplazar secciones completas.
Agregar nuevas reglas al final de la seccion existente.
Si una regla debe eliminarse, requiere aprobacion explicita del Governor.
```

### B-008: Agente en proyecto equivocado
**Severidad:** Media
**Descripcion:** Codex fue invocado en `C:/dev/projects/framework_multiagent/` en lugar de `C:/dev/projects/n8n-platform/`. Ejecuto su bootstrap completo en el repo equivocado, reportando "no tengo pendientes" porque el CONTEXT.md de ese repo no tenia tareas.
**Causa raiz:** El framework no tiene un mecanismo para verificar que el agente esta en el repo correcto. SESSION_BOOTSTRAP lee lo que encuentra.
**Correccion propuesta:** Agregar verificacion al Paso 0 del bootstrap:
```
0. Verificar que el directorio actual coincide con el proyecto esperado:
   - Comparar `project_name` del adapter con el directorio actual
   - Si no coincide, ALERTAR al usuario antes de continuar
```

### B-009: Agente sin remote configurado no puede sincronizar
**Severidad:** Baja
**Descripcion:** Codex en el repo del framework no tenia remote configurado. El `git pull` del Paso 0 fallo con "no tracking information". El agente lo registro como bloqueante pero no pudo resolverlo.
**Causa raiz:** El Paso 0 asume que existe un remote. El fallback "si no hay remote, omitir" existe en el texto pero no es suficientemente explicito.
**Correccion propuesta:** Ya corregido en v4.4 SESSION_BOOTSTRAP ("Si no hay remote configurado, omitir"). Verificar que los overlays lo reflejan.

---

## 5. Observaciones de campo sobre los agentes

### Claude Opus 4.6 (Governor)
- **Fortaleza real:** Cross-review. Detecto errores sutiles que los otros agentes no vieron (cookie secure, reglas eliminadas, log truncado).
- **Debilidad real:** Tiende a generar demasiada documentacion en una sola entrada de log. Entradas de 80+ lineas son dificiles de revisar.
- **Patron observado:** Cuando no tiene tareas explicitas, revisa proactivamente logs de otros agentes. Esto es valioso y deberia documentarse como comportamiento esperado del Governor.

### Codex CLI (Implementer)
- **Fortaleza real:** Ejecucion autonoma de larga duracion. Levanto staging completo (SSH, clone, .env, compose, import, schema) sin supervision.
- **Debilidad real:** Parseo literal de CONTEXT.md. Si las tareas no estan exactamente bajo `### @CODEX`, no las ve. Esto motivo la regla de estructura en v4.4.
- **Patron observado:** Ejecuta validaciones exhaustivas (ruff, pytest, engine status, sync-index) en cada sesion aunque no haya cambios de codigo. Es un buen habito pero consume tokens.

### Gemini 2.5 Pro (Researcher)
- **Fortaleza real:** Investigacion profunda. El SPEC_AWS_PRODUCTION.md es el documento mas completo del proyecto — cubre networking, secrets, IAM, storage en una sola entrega.
- **Debilidad real:** Tendencia a reescribir archivos completos en lugar de agregar al final. Esto causo B-006 y B-007.
- **Patron observado:** Cuando no entiende un tooling (Context7, skills.sh) lo documenta como "no ejecutable" en lugar de preguntar. El harness gap de ENTRADA-006 es un ejemplo — interpreto skills.sh como scripts fisicos cuando son paquetes npm.

---

## 6. Mejoras propuestas para el framework

| # | Area | Mejora | Prioridad | Justificacion |
|---|------|--------|-----------|---------------|
| M-001 | Logs | Regla append-only para logs de agentes | Alta | B-006: Gemini trunco historial |
| M-002 | PROJECT_RULES | Regla anti-rewrite: no reemplazar secciones, solo agregar | Alta | B-007: Gemini elimino reglas |
| M-003 | Bootstrap | Verificacion de proyecto correcto (adapter vs directorio) | Media | B-008: Codex en repo equivocado |
| M-004 | adapt-project | Generar ONBOARDING con rutas reales del proyecto, no genericas | Media | B-005: referencia incorrecta |
| M-005 | Overlays | Seccion explicita: "Tooling externo del framework (Context7, skills.sh)" | Media | Gemini no entendio que son capacidades MCP/npm |
| M-006 | CONTEXT.md | Template con anchors fijos (`### @AGENTE - Rol`) generados por adapt-project | Baja | Estandarizar estructura desde el inicio |
| M-007 | SESSION_BOOTSTRAP | Agregar paso de verificacion de remote antes del git pull | Baja | B-009: ya parcialmente corregido |
| M-008 | Engine | Comando `validate-log` que verifique que no se eliminaron entradas | Baja | Deteccion automatica de B-006 |

---

## 7. Valoracion general

El framework cumplio su promesa central en un proyecto real de produccion: **3 agentes trabajando en el mismo repo sin pisarse, con trazabilidad completa y mejora continua del entorno.**

En 5 dias de uso:
- Se adopto el framework (v4.2), se itero dos veces (v4.3, v4.4) y se corrigieron 5 bugs
- Se desplego un pipeline de Threat Intelligence completo (30 nodos, 7 tablas SQL, 5 code nodes)
- Se levanto staging en un Dell R720 con 3 servicios Docker healthy
- Se documento la arquitectura de produccion AWS completa (SPEC aprobado)
- Se generaron 9 ADRs, 3 SPECs y 40+ tareas completadas

**El valor diferencial no esta en la orquestacion tecnica (que es simple — archivos Markdown y convenciones) sino en los patrones de comportamiento: investigar antes de cambiar, documentar fallos como harness gaps, escalar a cross-review en cambios criticos.**

Los bugs encontrados (B-006 a B-009) son todos de la categoria "agente malinterpreta convenciones" — se corrigen con reglas mecanicas, no con mejor prompting. Esa es exactamente la filosofia del framework.

### Puntuacion por dimension

| Dimension | v4.2 | v4.4 | Tendencia |
|-----------|------|------|-----------|
| Separacion de roles | 9/10 | 9/10 | Estable |
| Trazabilidad | 8/10 | 8/10 | Estable (engine Windows sigue sin funcionar nativamente) |
| Onboarding de agentes | 7/10 | 8/10 | Mejoro con rutas corregidas y SKILLS.md |
| Deteccion de stack | 9/10 | 9/10 | Estable |
| Manejo de fallos | 9/10 | 9/10 | Estable (harness gap sigue siendo la mejor idea) |
| Sincronizacion multi-maquina | 5/10 | 8/10 | Mejoro significativamente con Paso 0 y estructura de CONTEXT |
| Proteccion contra errores de agentes | 4/10 | 6/10 | Mejoro con reglas de estructura, pero falta append-only |

---

## 8. Comentarios de otros agentes

*(Espacio reservado para que Codex y Gemini agreguen sus observaciones)*

### Codex (Implementer)

> Validado desde la perspectiva de ejecucion real. El framework v4.4 mejora de forma tangible respecto a v4.3 en dos puntos que para Codex son criticos: `git pull` obligatorio al inicio y backlog unificado por agente en `CONTEXT.md`. Ambos reducen mucho el riesgo de trabajar con contexto viejo o de "perder" tareas por estructura ambigua.
>
> En uso de campo, la separacion de roles si funciono como promete: pude ejecutar ciclos largos de staging sin duplicar trabajo con Gemini ni Claude, y los cross-reviews corrigieron fallos reales antes de consolidarlos. El patron de harness gap tambien aguanto bien en runtime: cuando `n8n execute` colisiono con el Task Broker, el framework favorecio documentar el bloqueo y no insistir a ciegas.
>
> Mi validacion deja dos comentarios practicos para la siguiente iteracion del framework:
> 1. Hace falta una regla explicita para distinguir cambios de **runtime no versionados** vs cambios **Git-trackeados**. En staging fue util remediar con archivos temporales, pero luego hay que reflejar o descartar esa divergencia de forma gobernada.
> 2. El framework necesita una via estandar de **dry-run en entornos n8n vivos**. `n8n execute` dentro del contenedor activo no fue reutilizable en este caso por colision con el broker en `5679`, asi que hoy el runbook depende demasiado de UI/manual.
>
> Con esas dos mejoras, mi evaluacion es positiva: v4.4 ya es suficientemente operativo para trabajo multi-maquina y multi-agente en un repo real, y los fallos observados son de mecanica del harness, no de colaboracion entre agentes.

### Gemini (Researcher)

> Desde la perspectiva de análisis y documentación, el framework v4.4 es un salto cualitativo en **coherencia técnica**. La cadena de valor `SPEC` -> `Código` -> `Validación` permite que el Researcher actúe como un control de calidad preventivo, detectando Gaps de diseño (como la falta de Redis en el compose de producción) antes de que el Implementador gaste tokens en un despliegue fallido.
>
> Mis observaciones para la evolución del framework son:
> 1. **Riesgo del Tooling de Edición:** Al no tener una herramienta nativa de `append` en archivos Markdown, el uso de `replace` en archivos grandes (Logs, CONTEXT.md) es propenso a errores de truncado (Bug B-006). El framework ganaría robustez con una regla o herramienta de "Insert after anchor" que no requiera reescribir bloques grandes.
> 2. **Visibilidad de Infraestructura Interna:** Como se observó en mi análisis inicial, hay una curva de aprendizaje sobre las capacidades del propio framework (skills, engine, etc.). Sugiero que `adapt-project` genere un `FRAMEWORK_CAPABILITIES.md` local que describa qué herramientas MCP o scripts están disponibles, para que el Researcher no intente "redescubrirlos".
> 3. **Validación Cruzada como SSOT:** La capacidad de auditar el trabajo de Codex en Staging desde el rol de Researcher asegura que la documentación (Runbooks, SPECs) no sea solo teórica, sino empírica. Este "cierre de ciclo" es lo que realmente previene la degradación del repositorio a largo plazo.
>
> En resumen, v4.4 permite un nivel de profundidad arquitectónica que sería imposible en un modelo de agente único, siempre que se mitiguen los riesgos de manipulación de archivos extensos.

---

*Generado por Claude Opus 4.6 — Governor | 2026-03-20*
*Proyecto: n8n Platform DELCOP | Commit: 2d63a25*
