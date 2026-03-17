---
description: Reglas universales para archivos YAML de configuración
paths: ["**/*.yml", "**/*.yaml"]
---

# YAML Rules

- Validar sintaxis YAML antes de commit.
- No hardcodear secretos ni credenciales. Usar variables de entorno: `${VAR_NAME}`.
- Indentación: 2 espacios (estándar YAML).
- Strings con caracteres especiales entre comillas.
- Comentar secciones no obvias.
- En CI/CD: cada step con `name:` descriptivo.
