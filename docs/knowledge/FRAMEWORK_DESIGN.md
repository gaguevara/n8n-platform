# FRAMEWORK_DESIGN.md — Documento Base de Diseño

> **Versión:** 1.0
> **Fecha:** 2026-03-14
> **Autor:** Claude Opus 4.6 (Governor / Architect)
> **Estado:** Foundational — Este documento define QUÉ es el framework,
> PARA QUÉ sirve, y CÓMO opera. Es la referencia raíz de diseño.

---

## Parte I — QUÉ ES

### 1. Definición

El **Framework Base de Colaboración Multi-Agente** es una infraestructura
de archivos, protocolos y un motor ejecutable que permite a múltiples agentes
de IA trabajar dentro de un mismo repositorio de forma coordinada, trazable
y no destructiva.

No es una librería. No es una aplicación. Es un **sistema operativo de
colaboración** que se instala sobre cualquier proyecto de software y establece
las reglas de juego para que agentes y humanos produzcan cambios seguros.

### 2. Qué NO es

| El framework NO es... | Porque... |
|------------------------|-----------|
| Un proyecto de software con lógica de negocio | Es agnóstico al dominio — no contiene código de aplicación |
| Un wrapper de un modelo específico | Funciona con cualquier combinación de agentes (Claude, Codex, Gemini, otros) |
| Un sistema de automatización sin supervisión | El humano siempre tiene override; la autonomía es gradual |
| Un reemplazo del control de versiones | Opera sobre git, no lo sustituye |
| Un framework de ML/AI | No entrena modelos — orquesta agentes existentes |

### 3. Para qué sirve

**Problema:** Cuando múltiples agentes de IA trabajan en un mismo repositorio:
- No comparten contexto entre sesiones
- Cada uno toma decisiones sin saber qué hicieron los demás
- No hay trazabilidad de quién cambió qué y por qué
- Los errores se repiten en loops sin resolución
- La documentación diverge del código
- Los cambios destructivos ocurren sin advertencia

**Solución:** El framework establece:
1. **Contexto compartido** — archivos que todos los agentes leen al iniciar
2. **Roles claros** — cada agente sabe qué le toca y qué delegar
3. **Trazabilidad extrema** — todo cambio queda registrado con autoría y evidencia
4. **Preservación por defecto** — nada se borra sin aprobación explícita
5. **Anti-loop** — los errores repetidos se escalan, no se repiten
6. **Validación cruzada** — cambios críticos requieren review de otro agente

### 4. Resultados esperados

| Métrica | Sin framework | Con framework |
|---------|--------------|---------------|
| Contexto entre sesiones | Perdido — depende del chat | Persistido en archivos del repo |
| Conflictos entre agentes | Silenciosos, destructivos | Detectados, documentados, resueltos |
| Tasa de éxito primer intento | ~40-50% (estimado industria) | >70% (objetivo con harness maduro) |
| Trazabilidad | Cero — todo en historial de chat | Completa — logs por agente, LOG_INDEX, CONTEXT.md |
| Deuda técnica invisible | Acumulativa | Detectada por garbage collection |
| Documentación | Diverge del código en días | Sincronizada por protocolo |

---

## Parte II — PRINCIPIOS FUNDACIONALES

Estos principios son **invariantes** — no se negocian, no se relajan, no se
"adaptan al contexto". Todo lo demás del framework se deriva de ellos.

### P1. Universalidad
```
El framework no contiene nada específico de un proyecto, stack o dominio.
```
- Sin imports de librerías concretas en el core
- Sin ejemplos con datos reales de un cliente
- Los adapters son la capa de personalización — nunca el core
- Test: si borras todos los adapters, el core sigue siendo válido

### P2. Context Before Action
```
Ningún agente actúa sin leer el contexto vigente.
```
- Secuencia de bootstrap obligatoria (SESSION_BOOTSTRAP.md)
- Archivos de contexto con precedencia definida
- El agente que actúa sin contexto produce output inválido por definición
- No es una sugerencia — es una precondición mecánica

### P3. Preserve-First
```
La acción por defecto es conservar. Destruir requiere aprobación explícita.
```
- No borrar archivos, logs ni documentación
- No truncar registros existentes
- Si algo queda obsoleto → archivar en `archive/`, no eliminar
- Toda acción destructiva requiere confirmación del humano
- En caso de duda, preservar siempre

### P4. Evidence Over Opinion
```
Las decisiones se basan en datos verificables, no en preferencia del modelo.
```
- Un agente que propone un cambio debe mostrar evidencia (test, log, benchmark)
- "Yo creo que es mejor" no es argumento — "los tests muestran que" sí lo es
- Las discrepancias se resuelven con evidencia reproducible
- Si no hay evidencia suficiente, el cambio no se adopta

### P5. Atomic Changes
```
Los cambios son pequeños, reversibles y con blast radius controlado.
```
- Un commit = una intención
- No mezclar refactor + feature en el mismo cambio
- Cada cambio debe poder revertirse sin efectos colaterales
- El blast radius máximo aceptable se define por proyecto (vía adapter)

### P6. Cross-Validation
```
Los cambios relevantes requieren revisión por una entidad distinta al autor.
```
- Agente A implementa → Agente B revisa → Agente C (o humano) aprueba
- Ningún agente se auto-aprueba en áreas críticas
- Las áreas críticas están definidas en PROJECT_RULES.md §8

### P7. Skills Post-Bootstrap
```
Las capacidades especializadas se activan después de adquirir contexto.
```
- Primero el agente lee el contexto
- Luego detecta el stack y la necesidad
- Solo entonces activa skills relevantes
- Previene la aplicación de skills incorrectas por falta de información

### P8. Governance Separation
```
Core, gobernanza, documentación y extensiones viven en capas separadas.
```
- El core engine no depende de los docs de gobernanza
- Los docs de gobernanza no dependen de las skills
- Las skills no dependen de los adapters de proyecto
- Cada capa puede evolucionar independientemente

---

## Parte III — ARQUITECTURA

### 5. Estructura de capas

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PROYECTO HOST                                │
│                   (cualquier repo de software)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CAPA 1 — PUNTO DE ENTRADA                                         │
│  ┌──────────┐ ┌───────────────────┐                                │
│  │ CLAUDE.md│ │SESSION_BOOTSTRAP.md│  ← Todo agente empieza aquí   │
│  │ AGENTS.md│ │                   │                                │
│  └──────────┘ └───────────────────┘                                │
│                                                                     │
│  CAPA 2 — CORE ENGINE                                              │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ .multiagent/                                             │       │
│  │  ├── core/engine.py          ← Motor ejecutable          │       │
│  │  ├── core/validation_router  ← Router de validación      │       │
│  │  ├── core/patterns/          ← 8 patrones operacionales  │       │
│  │  ├── core/rules/             ← Reglas base por tipo      │       │
│  │  ├── adapters/               ← Configuración por proyecto│       │
│  │  ├── schemas/                ← Esquemas de validación    │       │
│  │  ├── templates/              ← Plantillas reusables      │       │
│  │  ├── hooks/                  ← Pre/post acciones         │       │
│  │  └── tests/                  ← Tests del engine          │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  CAPA 3 — GOBERNANZA                                               │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ docs/governance/                                         │       │
│  │  ├── PROJECT_RULES.md   ← SSOT de reglas del proyecto    │       │
│  │  ├── CONTEXT.md         ← Estado vivo actual             │       │
│  │  ├── AGENT_ROLES.md     ← Roles y especialidades        │       │
│  │  ├── AI_GOVERNANCE.md   ← Políticas de uso de IA        │       │
│  │  ├── ONBOARDING.md      ← Guía de incorporación         │       │
│  │  ├── LOG_INDEX.md       ← Índice de trazabilidad        │       │
│  │  └── *_OVERLAY.md       ← Instrucciones por agente      │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  CAPA 4 — CONOCIMIENTO Y OPERACIONES                               │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ docs/knowledge/    ← Principios, guías, knowledge base   │       │
│  │ docs/harness/      ← Modelo de Harness Engineering       │       │
│  │ docs/sdlc/         ← Ciclo de vida, specs, workflows     │       │
│  │ docs/skills/       ← Catálogo de skills disponibles      │       │
│  │ docs/security/     ← Risk register, auditorías           │       │
│  │ docs/logs/         ← Logs operativos por agente          │       │
│  │ docs/architecture/ ← ADRs, diagramas                     │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  CAPA 5 — INTERFAZ DE AGENTE (host-specific)                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ .claude/skills/    ← Skills ejecutables por Claude Code   │       │
│  │ .claude/rules/     ← Reglas path-scoped                  │       │
│  │ GEMINI.md          ← Instrucciones para Gemini CLI       │       │
│  │ codex.md / .codex/ ← Instrucciones para Codex CLI        │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  CAPA 6 — PRESERVACIÓN                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ archive/           ← Reubicación no destructiva          │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6. Regla de dependencia entre capas

```
Capa 1 (Entrada) ──► referencia ──► Capa 3 (Gobernanza)
Capa 2 (Core)    ──► independiente de todo (solo necesita adapters)
Capa 3 (Govern.) ──► referencia ──► Capa 4 (Knowledge)
Capa 4 (Knowledge)── independiente (referencia estática)
Capa 5 (AgentUI) ──► referencia ──► Capa 1 + Capa 3
Capa 6 (Archive) ──► independiente (solo recibe)

NUNCA: Capa 2 depende de Capa 3
NUNCA: Capa 4 depende de Capa 5
NUNCA: Capa 5 modifica Capa 2
```

### 7. Core engine — Componentes

| Componente | Archivo | Función |
|-----------|---------|---------|
| **Engine** | `engine.py` | CLI principal: `status`, `sync-index`, `validate` |
| **Validation Router** | `validation_router.py` | Detecta tipo de archivo → ejecuta validador apropiado |
| **Patterns** | `patterns/01-08` | 8 patrones operacionales que todo agente debe seguir |
| **Rules** | `rules/*.md` | Reglas base por tipo de archivo (python, docker, yaml, etc.) |
| **Adapters** | `adapters/*.json` | Configuración por proyecto — mapea rutas, logs, validadores |
| **Schemas** | `schemas/*.md` | Definiciones de estructura para adapters y configs |
| **Templates** | `templates/*.md` | Plantillas para specs, failure-to-rule, etc. |
| **Hooks** | `hooks/` | Acciones pre/post cambio |
| **Tests** | `tests/test_engine.py` | Suite de validación del engine (9 tests, 100% pass) |

### 8. Patrones operacionales

Los 8 patrones son reglas de comportamiento que todo agente debe seguir.
No son sugerencias — son restricciones operacionales.

| # | Patrón | Regla |
|---|--------|-------|
| 01 | Investigate Before Change | Leer y entender antes de modificar |
| 02 | Test-First Validation | Verificar estado antes y después de cada cambio |
| 03 | Failure to Rule | Todo fallo repetido genera una nueva regla |
| 04 | Cross-Agent Review | Cambios relevantes validados por otro agente |
| 05 | Incremental Rollout | Desplegar en incrementos, no en big-bang |
| 06 | Evidence Over Opinion | Datos verificables, no preferencias |
| 07 | Context Before Action | Contexto primero, acción después |
| 08 | Minimal Blast Radius | Cambio mínimo necesario |

---

## Parte IV — FLUJOS OPERATIVOS

### 9. Flujo de arranque de sesión (Bootstrap)

```
Agente inicia sesión
    │
    ▼
┌─ Lee SESSION_BOOTSTRAP.md ──────────────────────────────────────────┐
│                                                                      │
│  1. Lee PROJECT_RULES.md (SSOT)                                     │
│  2. Lee CONTEXT.md (estado actual)                                  │
│  3. Lee su overlay ([AGENTE]_OVERLAY.md)                            │
│  4. Lee LOG_INDEX.md                                                │
│  5. Revisa últimos logs de otros agentes                            │
│  6. (Si toca código) Lee DESIGN_PRINCIPLES.md                      │
│  7. (Si hay spec) Lee SPEC_[nombre].md                             │
│                                                                      │
│  Evalúa tipo de tarea:                                              │
│  ├── Caso A: Puntual y clara → ejecutar directo                    │
│  ├── Caso B: Proyecto con contexto → continuar sobre base          │
│  ├── Caso C: Greenfield → construir contexto primero               │
│  └── Caso D: Alto riesgo → plan + review cruzado obligatorio       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
  Agente está listo para operar
```

### 10. Flujo de cambio estándar (Pipeline Tri-Agente)

```
     Petición del usuario o tarea identificada
                    │
                    ▼
    ┌──────── ¿Qué nivel de cambio? ──────────┐
    │                                          │
    ▼                                          ▼
  MENOR                                     SIGNIFICATIVO
  (lint, typo,                              (feature, refactor,
   doc update)                               arquitectura, seguridad)
    │                                          │
    ▼                                          ▼
  Cualquier agente:               FASE 1 — INVESTIGACIÓN (Gemini)
  ejecuta → valida → log         ├── Escanear repo y contexto
    │                             ├── Generar mapa de impacto
    ▼                             ├── Identificar dependencias
  FIN                             ├── Entregable: CONTEXT_SNAPSHOT.md
                                  │
                                  ▼
                          FASE 2 — INGENIERÍA (Codex)
                          ├── Tomar snapshot como input
                          ├── Implementar cambio
                          ├── Escribir/actualizar tests
                          ├── Ejecutar validación post-cambio
                          ├── Entregable: Código + Test Report
                          │
                          ▼
                    FASE 3 — GOBERNANZA (Claude)
                    ├── Review contra reglas del proyecto
                    ├── Auditoría de seguridad
                    ├── Verificar que se cumpla intención del usuario
                    ├── Actualizar CONTEXT.md si aplica
                    ├── Entregable: VALIDATION_CERTIFICATE.md
                    │
                    ▼
                  COMMIT / MERGE
```

### 11. Flujo de manejo de errores

```
  Agente encuentra error
         │
         ▼
  ┌── ¿Es el primer intento? ──┐
  │                              │
  ▼                              ▼
  SÍ                            NO (segundo intento)
  │                              │
  ▼                              ▼
  Intentar con               ┌── ¿Hay hipótesis nueva? ──┐
  hipótesis                   │                            │
  documentada                 ▼                            ▼
  │                          SÍ                           NO
  │                          │                            │
  │                          ▼                            ▼
  │                        Intentar UNA vez             ██ STOP ██
  │                        más con hipótesis             │
  │                        documentada                   ▼
  │                          │                      Registrar:
  │                          │                      • Error exacto
  │                          ▼                      • Log/output
  │                   ┌── ¿Resolvió? ──┐            • Hipótesis
  │                   │                 │            • Gap del harness
  │                   ▼                 ▼
  │                  SÍ               NO ──────► ██ STOP ██
  │                   │                          │
  ▼                   ▼                          ▼
  ┌── ¿Resolvió? ──┐                       Activar skill:
  │                 │                       failure-to-rule
  ▼                 ▼                       │
  SÍ               NO ──► Segundo          ▼
  │                        intento         Generar nueva regla
  ▼                                        para evitar recurrencia
  Registrar éxito
  en log del agente
```

### 12. Flujo de cierre de sesión

```
  Agente termina tarea
         │
         ▼
  1. Registrar en docs/logs/[AGENTE]_LOG.md
         │
         ▼
  2. Actualizar docs/governance/LOG_INDEX.md
         │
         ▼
  3. ¿Cambió el estado del proyecto?
     ├── SÍ → Actualizar CONTEXT.md
     └── NO → continuar
         │
         ▼
  4. ¿Cambió una regla o decisión estable?
     ├── SÍ → Actualizar PROJECT_RULES.md
     └── NO → continuar
         │
         ▼
  5. ¿El cambio afecta áreas críticas?
     ├── SÍ → Solicitar review cruzado
     └── NO → continuar
         │
         ▼
  6. ¿Hubo fallo repetido?
     ├── SÍ → Documentar gap del harness
     └── NO → continuar
         │
         ▼
  Sesión cerrada correctamente
```

---

## Parte V — MODELO DE ADAPTACIÓN

### 13. Cómo se adapta a un proyecto nuevo

El framework es universal. La personalización ocurre exclusivamente vía **adapters**.

```
Framework base (universal)
    │
    ▼
Adapter del proyecto (.multiagent/adapters/[proyecto].json)
    │
    ├── Define: stack, rutas, logs, validadores, reglas específicas
    ├── No modifica el core — solo lo configura
    └── Puede extenderse sin límite sin tocar el engine
```

**Estructura de un adapter:**
```json
{
  "project_name": "mi-proyecto",
  "stack": "python-fastapi",
  "paths": {
    "source": "src/",
    "tests": "tests/",
    "docs": "docs/"
  },
  "logs": {
    "claude": "docs/logs/CLAUDE_LOG.md",
    "codex": "docs/logs/CODEX_LOG.md",
    "gemini": "docs/logs/GEMINI_LOG.md"
  },
  "validators": {
    "*.py": ["ruff", "mypy", "pytest"],
    "Dockerfile": ["hadolint"],
    "*.sh": ["shellcheck"]
  },
  "rules": {
    "commit_format": "conventional",
    "max_blast_radius": 5
  }
}
```

### 14. Qué no se adapta (invariantes)

Independientemente del adapter, estos elementos nunca cambian:
- Los 8 principios fundacionales
- Los 8 patrones operacionales
- El protocolo de bootstrap
- La regla anti-loop
- La estructura de logs y trazabilidad
- El formato de handoff entre agentes
- El flujo de manejo de errores

---

## Parte VI — HARNESS ENGINEERING

### 15. Modelo operativo

> **Principio:** Cuando un agente falla, el problema es el harness, no el agente.

```
┌─────────────────────────────────────────────┐
│              HARNESS                         │
│                                             │
│  Context Engineering                        │
│  ├── Archivos que el agente lee             │
│  ├── Secuencia de carga                     │
│  └── Contexto just-in-time                  │
│                                             │
│  Constraints Mecánicas                      │
│  ├── Linters, formatters                    │
│  ├── Pre-commit hooks                       │
│  ├── Type checkers                          │
│  └── Tests estructurales                    │
│                                             │
│  Garbage Collection                         │
│  ├── Drift docs↔código                      │
│  ├── Dead code, stale TODOs                 │
│  ├── Dependency audits                      │
│  └── ADR reviews                            │
│                                             │
│  Feedback Loops                             │
│  ├── Inmediato: cambio → lint → test        │
│  ├── Sesión: tarea → log → context update   │
│  └── Mejora: fallo → gap → mejora harness   │
│                                             │
└─────────────────────────────────────────────┘
```

### 16. Ciclo de mejora continua del harness

```
Agente falla (2+ veces) en la misma tarea
    │
    ▼
  STOP + documentar error con evidencia
    │
    ▼
  Evaluar: ¿falta contexto, herramienta, spec, o constraint?
    │
    ├── Falta contexto → Mejorar docs/knowledge o CONTEXT.md
    ├── Falta herramienta → Agregar a pre-commit o CI
    ├── Falta spec → Crear spec antes de reintentar
    └── Falta constraint → Agregar regla mecánica (linter, test)
    │
    ▼
  Documentar mejora en log
    │
    ▼
  Reintentar tarea con harness mejorado
```

---

## Parte VII — ROADMAP DE CAPACIDADES

### 17. Estado actual vs. objetivo

| Capacidad | Estado actual | Objetivo |
|-----------|:------------:|:--------:|
| Core engine (CLI) | ✅ Funcional (9/9 tests) | Mantener |
| Patrones operacionales (8) | ✅ Definidos | Integrar en engine |
| Skills (7) | ✅ Definidas | Validar en uso real |
| Adapters | ⚠️ Solo ejemplos | Crear adapter real del framework |
| Gobernanza | ⚠️ Plantillas | Activar estado vivo |
| Trazabilidad | ⚠️ Estructura sin datos | Poblar con primer ciclo real |
| Hooks pre-commit | ⚠️ Config existe | Activar tras git init |
| MCP Integration | ❌ Planificado | Fase 2 |
| Garbage collection | ❌ Definido | Implementar como skill |
| Pipeline tri-agente | ❌ Diseñado | Primer ciclo real |

### 18. Primer ciclo operativo (bootstrap del propio framework)

El primer proyecto que se opera con el framework es **el framework mismo**.
Esto valida la universalidad: si el framework puede gestionarse a sí mismo,
puede gestionar cualquier proyecto.

```
1. Extraer zip a directorio de trabajo
2. Limpiar rutas basura con llaves literales
3. Inicializar git
4. Crear adapter: .multiagent/adapters/framework-multiagent.json
5. Activar CONTEXT.md con estado real
6. Poblar logs con primer ciclo
7. Commit inicial
8. Ejecutar primer pipeline tri-agente sobre un cambio real
9. Evaluar harness y documentar gaps encontrados
```

---

## Apéndice A — Relación con otros documentos

| Documento | Relación con FRAMEWORK_DESIGN.md |
|-----------|----------------------------------|
| `PROJECT_INIT.md` | Genesis — los objetivos originales que este diseño implementa |
| `PROJECT_RULES.md` | Operacionalización — las reglas vivas que implementan estos principios |
| `AGENT_ROLES.md` | Complemento — quién ejecuta cada parte de estos flujos |
| `HARNESS.md` | Detalle — expandido del modelo descrito en Parte VI |
| `SDLC_WORKFLOW.md` | Proceso — el ciclo de vida que se ejecuta dentro de estos flujos |
| `DESIGN_PRINCIPLES.md` | Knowledge — principios de código que aplican en Fase 2 (Ingeniería) |
| `SESSION_BOOTSTRAP.md` | Implementación — el script del flujo de arranque (§9) |

## Apéndice B — Glosario

| Término | Definición en este framework |
|---------|------------------------------|
| **Adapter** | Archivo JSON que personaliza el framework para un proyecto específico |
| **Blast radius** | Número de archivos/módulos afectados por un cambio |
| **Bootstrap** | Secuencia de carga de contexto al iniciar sesión |
| **Constraint mecánica** | Validación automática que bloquea (no sugiere) — ej. linter en pre-commit |
| **Cross-validation** | Review de un cambio por un agente distinto al autor |
| **Drift** | Divergencia entre documentación y estado real del código |
| **Garbage collection** | Proceso periódico de limpieza de inconsistencias |
| **Handoff** | Transferencia formal de una tarea de un agente a otro |
| **Harness** | Conjunto de contexto, constraints y feedback que rodea al agente |
| **Overlay** | Instrucciones específicas para un agente particular |
| **Pattern** | Regla de comportamiento operacional (hay 8 definidos) |
| **Pipeline tri-agente** | Flujo: Investigación (Gemini) → Ingeniería (Codex) → Gobernanza (Claude) |
| **SSOT** | Single Source of Truth — fuente única de verdad |
| **Skill** | Capacidad especializada activable bajo demanda |

---

*Documento fundacional del Framework Multi-Agente v4.1*
*Creado: 2026-03-14 por Claude Opus 4.6 (Governor / Architect)*
*Este documento debe leerse junto con AGENT_ROLES.md y PROJECT_RULES.md*
