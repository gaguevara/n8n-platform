---
description: Reglas universales para scripts bash/shell
paths: ["**/*.sh", "**/*.bash"]
---

# Shell Script Rules

- Empezar con `#!/bin/bash` y `set -euo pipefail`.
- Variables entre llaves: `${var}` no `$var`.
- Strings siempre entre comillas dobles para evitar word splitting.
- No usar `eval` salvo justificación documentada.
- Validar inputs y existencia de archivos antes de operar.
- Ejecutar `shellcheck` después de cada cambio.
- Comentar bloques funcionales.
- Exit codes significativos (no solo 0 y 1).
