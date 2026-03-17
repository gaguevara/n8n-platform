---
name: validate-change
description: Ejecuta validación post-cambio completa. Claude debe usar este skill después de CADA modificación de código. Detecta el stack automáticamente y ejecuta lint, tests y scan.
---

# Validate Change

Secuencia obligatoria después de cada cambio de código. Ejecutar `scripts/post-change.sh` si existe, o seguir los pasos manualmente:

## 1. Detectar stack
Revisar archivos del proyecto para determinar herramientas:
- `pyproject.toml` / `requirements.txt` → Python (ruff, pytest, mypy)
- `package.json` → Node (eslint, jest/vitest, tsc)
- `go.mod` → Go (golangci-lint, go test)
- `Dockerfile` → Docker (hadolint)
- `*.sh` → Shell (shellcheck)

## 2. Lint y formato
Ejecutar el linter detectado. Corregir errores antes de continuar.

## 3. Tests afectados
Ejecutar tests relevantes al cambio. Comparar con baseline (pattern 02-test-first-validation).
Si fallan 2 veces el mismo test → STOP → usar skill `failure-to-rule`.

## 4. Engine validate
Si existe `.multiagent/adapters/`, usar el engine para validar el archivo modificado:
```bash
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json validate <archivo> --json
```

## 5. Secret scan
```bash
detect-secrets scan --baseline .secrets.baseline 2>/dev/null || echo "detect-secrets not available, skipping"
```
Si detect-secrets no esta instalado, verificar manualmente que no se introdujeron credenciales, tokens o claves.

## 6. Resultado
- Todo pasa → continuar
- Algo falla → corregir antes de continuar
- Falla 2 veces el mismo → STOP + registrar harness gap en log
