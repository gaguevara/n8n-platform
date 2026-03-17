#!/bin/bash
# update-agent-context.sh
# Sincroniza el contexto del framework a todos los archivos de agentes.
# Ejecutar después de cambios en PROJECT_RULES, CONTEXT, o estructura del framework.
# Uso: ./update-agent-context.sh
set -euo pipefail

echo "═══════════════════════════════════════════════════════"
echo "  Sincronizando contexto a agentes"
echo "═══════════════════════════════════════════════════════"

ROOT="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

# Verificar que estamos en el root del repo
if [ ! -f "$ROOT/CLAUDE.md" ]; then
    echo "❌ No se encontró CLAUDE.md en la raíz. ¿Estás en el directorio correcto?"
    exit 1
fi

# === CLAUDE.md (raíz) ===
if [ -f "$ROOT/CLAUDE.md" ]; then
    echo "✅ CLAUDE.md presente en raíz"
else
    echo "⚠️  CLAUDE.md falta en raíz — creando placeholder"
    echo "# CLAUDE.md — Leer SESSION_BOOTSTRAP.md primero" > "$ROOT/CLAUDE.md"
fi

# === AGENTS.md (estándar multi-agente) ===
# Algunos agentes (Codex, Copilot) buscan AGENTS.md
if [ ! -f "$ROOT/AGENTS.md" ]; then
    echo "📄 Creando AGENTS.md (alias para agentes que no leen CLAUDE.md)..."
    cat > "$ROOT/AGENTS.md" << 'EOF'
# AGENTS.md — Instrucciones para agentes IA

Este proyecto usa un framework multi-agente. Lee los siguientes archivos en orden:

1. SESSION_BOOTSTRAP.md (protocolo de arranque)
2. docs/governance/PROJECT_RULES.md (SSOT)
3. docs/governance/CONTEXT.md (estado actual)
4. Tu overlay en docs/governance/[AGENTE]_OVERLAY.md
5. docs/governance/LOG_INDEX.md

Registra toda actividad en docs/logs/[AGENTE]_LOG.md.
Principio harness: fallo repetido = mejorar entorno, no repetir prompt.
EOF
fi

# === Copilot instructions (si usa GitHub Copilot) ===
if [ -d "$ROOT/.github" ] || [ -f "$ROOT/.github/copilot-instructions.md" ]; then
    echo "📄 Actualizando .github/copilot-instructions.md..."
    mkdir -p "$ROOT/.github"
    cat > "$ROOT/.github/copilot-instructions.md" << EOF
# Copilot Instructions — Synced ${TIMESTAMP}
# Lee SESSION_BOOTSTRAP.md y docs/governance/PROJECT_RULES.md antes de generar código.
# Aplica principios de docs/knowledge/DESIGN_PRINCIPLES.md.
# Post-cambio: lint → tests → secret scan.
EOF
fi

# === Gemini rules (si usa Gemini Code Assist) ===
if [ -f "$ROOT/GEMINI.md" ] || [ -f "$ROOT/.gemini/rules.md" ]; then
    echo "📄 Actualizando GEMINI.md en raíz..."
    cat > "$ROOT/GEMINI.md" << EOF
# GEMINI.md — Synced ${TIMESTAMP}
# Lee SESSION_BOOTSTRAP.md y docs/governance/PROJECT_RULES.md antes de actuar.
# Tu overlay: docs/governance/GEMINI_OVERLAY.md
# Registra en: docs/logs/GEMINI_LOG.md
EOF
fi

# === Windsurf rules (si usa Windsurf/Cascade) ===
if [ -d "$ROOT/.windsurf" ]; then
    echo "📄 Actualizando .windsurf/rules/specify-rules.md..."
    mkdir -p "$ROOT/.windsurf/rules"
    cat > "$ROOT/.windsurf/rules/specify-rules.md" << EOF
# Windsurf Rules — Synced ${TIMESTAMP}
# Lee SESSION_BOOTSTRAP.md y docs/governance/PROJECT_RULES.md.
EOF
fi

echo ""
echo "✅ Contexto sincronizado — ${TIMESTAMP}"
echo "   Archivos actualizados según agentes detectados."
echo ""
echo "💡 Ejecutar este script después de cambios en:"
echo "   - PROJECT_RULES.md"
echo "   - CONTEXT.md"
echo "   - SESSION_BOOTSTRAP.md"
echo "   - Estructura del framework"
