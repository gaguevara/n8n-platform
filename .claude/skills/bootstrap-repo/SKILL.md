---
name: bootstrap-repo
description: Analiza la estructura del repositorio y genera comprensión completa del proyecto. Usar al iniciar trabajo en un repo nuevo, al inicio de sesión, o cuando el agente necesita orientarse.
---

# Bootstrap Repo

## 1. Estructura de archivos
Lista el árbol de directorios (2 niveles). Identifica:
- Código fuente (lenguaje principal)
- Tests
- Configuración (Docker, CI/CD, env)
- Documentación del framework multi-agente

## 2. Detectar stack
Buscar archivos indicadores:
- `pyproject.toml` / `requirements.txt` / `setup.py` → Python
- `package.json` → Node/TypeScript
- `go.mod` → Go
- `Cargo.toml` → Rust
- `Dockerfile` / `docker-compose*.yml` → Docker
- `__manifest__.py` en `addons/` → Odoo
- `.terraform/` / `*.tf` → Terraform

## 3. Verificar framework multi-agente
¿Existen estos archivos?
- `CLAUDE.md` (raíz) → puente del framework
- `SESSION_BOOTSTRAP.md` → protocolo de arranque
- `.multiagent/` → core engine v4
- `docs/governance/PROJECT_RULES.md` → SSOT
- `docs/governance/CONTEXT.md` → estado del proyecto
- `docs/logs/*.md` → últimas entradas

## 4. Discrepancias
Comparar lo que dice `CONTEXT.md` contra lo que realmente existe.

## 5. Skills disponibles
Listar skills en `.claude/skills/` y evaluar cuáles son relevantes para este proyecto según el stack detectado.

## 6. Resultado
Generar resumen: stack, estado, archivos clave, discrepancias, skills relevantes.
Registrar en log como sesión de bootstrap.
