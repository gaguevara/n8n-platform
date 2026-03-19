---
name: gc-audit
description: Auditoría de consistencia del repositorio (garbage collection). Busca doc-code drift, dead code, stale TODOs, dependency vulnerabilities, y log inconsistencies. Usar periódicamente o bajo demanda.
---

# GC Audit (Garbage Collection)

Ejecuta `scripts/gc-check.sh` si existe, o sigue los pasos manualmente.

## 1. Doc-code drift
Verificar `docs/governance/CONTEXT.md` contra estado real del repo:
- ¿Los pendientes listados siguen pendientes?
- ¿Hay archivos nuevos no documentados?

## 2. Dead code
Detectar funciones, imports y variables no usados:
- Python: `ruff check --select F401,F841 . 2>/dev/null`
- Node: `npx eslint --rule 'no-unused-vars: error' . 2>/dev/null`

## 3. Stale TODOs
```bash
grep -rn "TODO" --include="*.py" --include="*.js" --include="*.ts" --include="*.md" . 2>/dev/null
```
Reportar TODOs sin fecha o con más de 30 días.

## 4. Log consistency
Verificar que `docs/governance/LOG_INDEX.md` coincide con entradas reales en `docs/logs/`.
Opcionalmente usar `.multiagent/core/engine.py sync-index`.

## 5. ADR review
Buscar ADRs con estado "Propuesta" que lleven más de 30 días.

## 6. Security sweep
Invocar skill `security-scan` como parte del GC.

## Resultado
Generar reporte con hallazgos y acciones. Registrar en log con tag [GC].
