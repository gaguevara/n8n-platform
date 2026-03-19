#!/bin/bash
# post-change.sh — Auto-detect stack and run validation
set -euo pipefail
FILE="${1:-}"
echo "=== Post-Change Validation ==="

# Python
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  command -v ruff &>/dev/null && { echo "[lint] ruff check..."; ruff check ${FILE:+$FILE} --fix 2>/dev/null; ruff format ${FILE:+$FILE} 2>/dev/null; }
  command -v pytest &>/dev/null && { echo "[test] pytest..."; pytest --tb=short -q 2>/dev/null; }
fi

# Node
if [ -f "package.json" ]; then
  command -v eslint &>/dev/null && { echo "[lint] eslint..."; npx eslint ${FILE:+$FILE} 2>/dev/null; }
fi

# Docker
if [ -n "$FILE" ] && echo "$FILE" | grep -qi "dockerfile"; then
  command -v hadolint &>/dev/null && { echo "[lint] hadolint..."; hadolint "$FILE" 2>/dev/null; }
fi

# Shell
if [ -n "$FILE" ] && echo "$FILE" | grep -qi "\.sh$"; then
  command -v shellcheck &>/dev/null && { echo "[lint] shellcheck..."; shellcheck "$FILE" 2>/dev/null; }
fi

# Secrets
command -v detect-secrets &>/dev/null && { echo "[scan] secrets..."; detect-secrets scan --baseline .secrets.baseline 2>/dev/null; }

echo "✅ Validation complete."
