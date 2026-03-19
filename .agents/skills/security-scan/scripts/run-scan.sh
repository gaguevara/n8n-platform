#!/bin/bash
# run-scan.sh — Helper for security-scan skill
# Detects stack and runs appropriate security tools
set -euo pipefail

echo "=== Security Scan ==="
ISSUES=0

# 1. Secrets
if command -v detect-secrets &>/dev/null; then
  echo "[1/4] Scanning for secrets..."
  detect-secrets scan --baseline .secrets.baseline 2>/dev/null && echo "  OK" || { echo "  ⚠ New secrets detected"; ISSUES=$((ISSUES+1)); }
else
  echo "[1/4] detect-secrets not installed — skipping"
fi

# 2. Dependencies
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  if command -v pip-audit &>/dev/null; then
    echo "[2/4] Auditing Python dependencies..."
    pip-audit 2>/dev/null && echo "  OK" || { echo "  ⚠ Vulnerabilities found"; ISSUES=$((ISSUES+1)); }
  fi
elif [ -f "package.json" ]; then
  echo "[2/4] Auditing Node dependencies..."
  npm audit --production 2>/dev/null && echo "  OK" || { echo "  ⚠ Vulnerabilities found"; ISSUES=$((ISSUES+1)); }
else
  echo "[2/4] No dependency file detected — skipping"
fi

# 3. Docker
if command -v trivy &>/dev/null && command -v docker &>/dev/null; then
  echo "[3/4] Scanning Docker images..."
  for img in $(docker images --format '{{.Repository}}:{{.Tag}}' | head -3); do
    trivy image --severity HIGH,CRITICAL --quiet "$img" 2>/dev/null || ISSUES=$((ISSUES+1))
  done
else
  echo "[3/4] trivy or docker not available — skipping"
fi

# 4. Gitignore check
echo "[4/4] Checking .gitignore..."
for pattern in ".env" "*.pem" "*.key" "__pycache__"; do
  grep -q "$pattern" .gitignore 2>/dev/null || { echo "  ⚠ Missing: $pattern in .gitignore"; ISSUES=$((ISSUES+1)); }
done

echo ""
if [ "$ISSUES" -gt 0 ]; then
  echo "⚠ $ISSUES issue(s) found. Review above."
  exit 1
else
  echo "✅ Security scan clean."
  exit 0
fi
