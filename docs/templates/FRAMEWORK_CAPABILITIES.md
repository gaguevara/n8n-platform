# FRAMEWORK_CAPABILITIES.md — Catálogo de Capacidades del Framework

## Propósito

Este documento sirve como referencia rápida para que agentes y humanos entiendan qué puede hacer el framework, qué herramientas tiene integradas y cuáles son sus límites operativos.

---

## 1. Núcleo (Engine)

| Capacidad | Descripción | Estado |
|-----------|-------------|--------|
| **Orquestación Multi-Agente** | Protocolo de colaboración entre Claude, Codex y Gemini | Operativo |
| **Validación de Adapters** | Validación de esquemas y estados vía archivos `.json` | Operativo |
| **Sincronización de Índices** | Automatización de `LOG_INDEX.md` a partir de logs individuales | Operativo |
| **Router de Validación** | Enrutamiento de tareas de validación según el stack detectado | Operativo |

---

## 2. Herramientas Integradas

### 2.1 Análisis Estático y Calidad
- **Ruff:** Linter y formatter rápido para Python.
- **Pytest:** Framework de pruebas para el core y adaptadores.
- **ast-grep:** Análisis estructural de código (orientado a gobernanza).
- **pre-commit:** Hooks de validación antes de cada commit.

### 2.2 Conocimiento Externo
- **Context7 (MCP):** Acceso a documentación de librerías en tiempo real.
- **skills.sh:** Catálogo comunitario de mejores prácticas y hardening.

---

## 3. Gobernanza y Contexto

- **Estado Vivo (`CONTEXT.md`):** Contrato mecánico para backlog por agente.
- **Single Source of Truth (`PROJECT_RULES.md`):** Reglas, decisiones y estándares.
- **Trazabilidad (`LOG_INDEX.md` + Logs):** Historial inmutable de acciones y decisiones.
- **Harness Engineering:** Mejora continua del entorno ante fallos de agentes.

---

## 4. Límites y Restricciones

- **Entorno:** Optimizado para Windows/PowerShell con fallbacks documentados.
- **Stack Core:** Python 3.12+.
- **Gobernanza:** Basada en Markdown para máxima interoperabilidad.
- **Seguridad:** No se permite el almacenamiento de secretos en el repositorio (`detect-secrets`).

---

## 5. Próximas Capacidades (Roadmap)

- [ ] Integración profunda con MCP para control de infraestructura.
- [ ] Automatización de SPEC-to-Code mediante agentes especializados.
- [ ] Dashboard de observabilidad de salud del framework.

---

*Última actualización: 2026-03-20 — Versión: v4.4*
