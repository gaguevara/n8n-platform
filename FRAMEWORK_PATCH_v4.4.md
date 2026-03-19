# Framework Multi-Agente — Parche para v4.4

> **Autor:** Claude Opus 4.6 (Governor) — proyecto piloto n8n-platform DELCOP
> **Fecha:** 2026-03-19
> **Origen:** Harness gap detectado en producción real con 3 agentes (Claude, Codex, Gemini)
> **Destinatario:** Agente creador del framework

---

## Problema detectado

El Governor (Claude) creó una subsección temática en `CONTEXT.md` llamada "Threat Intelligence — pendientes activos" para agrupar tareas del nuevo pipeline. Las tareas `@CODEX` quedaron fuera de la sección `### @CODEX - Implementer/DevOps` que Codex parsea para encontrar su trabajo.

**Resultado:** Codex reportó "sin pendientes" durante 2 sesiones consecutivas mientras tenía 4 tareas abiertas. El error era del Governor, no de Codex — Codex siguió el protocolo correctamente.

**Causa raíz:** El framework no establece que la estructura de secciones en CONTEXT.md es un contrato mecánico, no decorativo. Los agentes buscan por encabezado `### @AGENTE`, no por contenido libre.

---

## Cambios propuestos (3 archivos del framework base)

### 1. `SESSION_BOOTSTRAP.md` — Sección "Cierre de sesión", punto 3

**Antes:**
```
3. Actualizar `docs/governance/CONTEXT.md` si cambió el estado del proyecto
```

**Después:**
```
3. Actualizar `docs/governance/CONTEXT.md` si cambió el estado del proyecto
   - Las tareas DEBEN estar bajo la sección del agente asignado (`### @AGENTE - Rol`)
   - No crear subsecciones temáticas que fragmenten los pendientes
```

### 2. `docs/governance/PROJECT_RULES.md` (plantilla genérica) — Sección 6 "Reglas de implementación"

**Agregar al final de la sección:**
```
- **Estructura de CONTEXT.md:** Las tareas pendientes DEBEN colocarse bajo la sección
  del agente asignado (`### @AGENTE - Rol`). No crear subsecciones temáticas ni
  agrupaciones ad-hoc que fragmenten los pendientes. Los agentes localizan sus tareas
  por encabezado de sección, no por contenido libre.
```

### 3. `.claude/skills/adapt-project/SKILL.md` — Fase 4, paso 13

**Antes:**
```
13. **Escribir cola de tareas** en CONTEXT.md → seccion "Pendientes inmediatos":
    ```
    - [ ] @GEMINI: Validar PROJECT_RULES y completar secciones pendientes
    - [ ] @CODEX: Ejecutar tests y validacion completa del adapter
    - [ ] @CLAUDE: Consolidar resultados cuando Gemini y Codex completen
    ```
```

**Después:**
```
13. **Escribir cola de tareas** en CONTEXT.md → seccion "Pendientes inmediatos":
    - Cada tarea DEBE ir bajo `### @AGENTE - Rol` correspondiente
    - NO crear subsecciones temáticas — los agentes parsean por encabezado
    ```
    ### @GEMINI - Researcher/Reviewer
    - [ ] @GEMINI: Validar PROJECT_RULES y completar secciones pendientes

    ### @CODEX - Implementer/DevOps
    - [ ] @CODEX: Ejecutar tests y validacion completa del adapter

    ### @CLAUDE - Governor
    - [ ] @CLAUDE: Consolidar resultados cuando Gemini y Codex completen
    ```
```

---

## Evidencia

| Entrada | Agente | Descripción |
|---------|--------|-------------|
| CLAUDE_LOG ENTRADA-006 | Claude | Detección y corrección del harness gap |
| CODEX_LOG ENTRADA-009/010 | Codex | Reportó "sin pendientes" — comportamiento correcto según su parseo |
| PROJECT_RULES.md §6 | n8n-platform | Regla ya aplicada en el proyecto piloto |

## Clasificación

- **Tipo:** Harness gap → Failure-to-rule (Pattern 03)
- **Severidad:** Media — causa pérdida de ciclos de trabajo, no pérdida de datos
- **Reproducibilidad:** 100% — cualquier Governor que cree subsecciones temáticas lo dispara
- **Corrección:** 3 líneas en 3 archivos — mínimo blast radius

---

## Problema adicional detectado (mismo incidente)

### Agentes en worktrees no sincronizan con remote

Codex trabajaba en un worktree aislado con cambios locales en LOG_INDEX.md y CODEX_LOG.md. Al pushear la corrección de CONTEXT.md a `main`, Codex seguía leyendo la versión anterior porque nunca hizo `git pull`.

**Resultado:** Incluso después de corregir la estructura de CONTEXT.md, Codex reportó "sin pendientes" durante 2 rondas adicionales.

**Causa raíz:** `SESSION_BOOTSTRAP.md` no incluye `git pull` como paso obligatorio antes de leer CONTEXT.md. En un entorno multi-agente donde varios agentes pushean cambios, leer archivos de gobernanza sin sincronizar primero garantiza lecturas obsoletas.

### Cambio propuesto (1 archivo adicional)

#### 4. `SESSION_BOOTSTRAP.md` — Sección "Secuencia obligatoria de inicio"

**Antes:**
```
1. Leer docs/governance/PROJECT_RULES.md
2. Si docs/governance/CONTEXT.md existe -> leerlo
```

**Después:**
```
0. Sincronizar con remote: `git pull origin main` (o `git stash && git pull && git stash pop` si hay cambios locales)
1. Leer docs/governance/PROJECT_RULES.md
2. Si docs/governance/CONTEXT.md existe -> leerlo
```

### Evidencia adicional

| Entrada | Agente | Descripción |
|---------|--------|-------------|
| CODEX_LOG ENTRADA-010/011 | Codex | 2 sesiones consecutivas sin ver tareas tras corrección ya pusheada |

**Total de cambios para v4.4:** 4 archivos, 6 líneas

---

*Generado desde el proyecto piloto n8n-platform DELCOP — primer deployment real del framework v4.3*
