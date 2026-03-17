---
name: security-scan
description: Ejecuta escaneo de seguridad completo del proyecto. Usar después de cambios en dependencias, Dockerfiles, configuración sensible, o periódicamente como garbage collection.
---

# Security Scan

Ejecuta la siguiente secuencia de validaciones. Adapta los comandos al stack detectado en el proyecto.

## 1. Secret detection
```bash
detect-secrets scan --baseline .secrets.baseline 2>/dev/null || echo "detect-secrets not installed"
```
Si detect-secrets no esta disponible, hacer revision manual:
- Buscar patterns: `password`, `token`, `secret`, `api_key`, `credential` en archivos modificados
- Verificar que `.env*`, `*.pem`, `*.key` estan en `.gitignore`

Si detecta nuevos secretos: **BLOQUEANTE**.

## 2. Dependency audit
Detectar el stack y ejecutar lo que aplique:
- Python: `pip-audit --format json 2>/dev/null || echo "pip-audit not available"`
- Node: `npm audit --production 2>/dev/null`
- Go: `govulncheck ./... 2>/dev/null`

Si ninguna herramienta esta instalada, revisar manualmente las dependencias en `requirements.txt` / `pyproject.toml` / `package.json`.

## 3. Container scan (si hay Docker)
Solo ejecutar si existen Dockerfiles en el proyecto:
```bash
trivy image --severity HIGH,CRITICAL <image> 2>/dev/null || echo "trivy not available"
```

## 4. .gitignore audit
Confirmar que estos patterns existen:
- `.env*`, `*.pem`, `*.key`, `__pycache__/`, `*.pyc`, `node_modules/`
- Directorios de código propietario (enterprise/, vendor/ privado)

## 5. Resultado
Reportar hallazgos con severidad. Si hay CVEs HIGH/CRITICAL → registrar en `docs/security/RISK_REGISTER*.md` o equivalente del proyecto.
