---
description: Reglas universales para archivos Python
paths: ["**/*.py"]
---

# Python Rules

- Aplicar PEP 8. Usar `ruff` como referencia.
- Type hints en todas las funciones públicas.
- Docstrings Google Style en todas las funciones/clases públicas.
- Excepciones específicas, nunca bare `except:` ni `except Exception: pass`.
- Imports explícitos, nunca `import *`.
- Funciones ≤ 20 líneas. Si es más larga, extraer método.
- Nombres descriptivos: no usar `tmp`, `data`, `result`, `info` como nombres finales.
- Sin magic numbers/strings: usar constantes con nombre.
- DRY: si copias un bloque, necesitas una abstracción.
- No hardcodear credenciales, tokens ni API keys.
- Ejecutar `ruff check` y `ruff format` después de cada cambio.
- Verificar dependencias nuevas con `pip-audit` antes de agregar.
