#!/bin/bash
# gc-check.sh — Garbage collection helper
set -euo pipefail
echo "=== Garbage Collection Audit ==="
ISSUES=0

# Dead code (Python)
if command -v ruff &>/dev/null; then
  echo "[1] Dead code (Python)..."
  UNUSED=$(ruff check --select F401,F841 . 2>/dev/null | wc -l)
  [ "$UNUSED" -gt 0 ] && { echo "  ⚠ $UNUSED unused imports/variables"; ISSUES=$((ISSUES+UNUSED)); } || echo "  OK"
fi

# Stale TODOs
echo "[2] Stale TODOs..."
TODOS=$(grep -rn "TODO" --include="*.py" --include="*.js" --include="*.ts" --include="*.md" . 2>/dev/null | wc -l)
echo "  Found $TODOS TODO(s)"
[ "$TODOS" -gt 10 ] && ISSUES=$((ISSUES+1))

# Security (delegate to security-scan if available)
echo "[3] Security sweep..."
SCAN_SCRIPT="$(dirname "$0")/../security-scan/scripts/run-scan.sh"
if [ -x "$SCAN_SCRIPT" ]; then
  bash "$SCAN_SCRIPT" || ISSUES=$((ISSUES+1))
else
  echo "  security-scan script not found — skipping"
fi

echo ""
echo "=== GC Summary: $ISSUES issue(s) ==="
exit $ISSUES
