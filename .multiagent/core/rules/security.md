---
description: Reglas universales de seguridad para archivos de configuración sensibles
paths: ["**/.env*", "**/secrets*", "**/*credential*", "**/*secret*", "**/config/*.conf"]
---

# Security Rules

- NUNCA versionar archivos que contengan credenciales reales.
- Verificar que .gitignore excluye archivos sensibles (.env, secrets, credentials).
- Credenciales de laboratorio solo válidas en entorno local de desarrollo.
- En staging/producción: usar un gestor de secretos (Secrets Manager o equivalente).
- Si un archivo con credenciales reales llega a git: INCIDENTE DE SEGURIDAD.
- Ejecutar `detect-secrets scan` para validar ausencia de secretos.
