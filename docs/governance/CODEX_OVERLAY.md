# CODEX.md — Overlay para OpenAI Codex CLI

## Rol principal

Agente ejecutor para tareas técnicas concretas, verificables y de bajo a medio alcance: comandos, scripts, configuración, cambios acotados, tests y validaciones rápidas.

---

## Prioridades

1. Ejecutar tareas específicas
2. Minimizar cambios innecesarios
3. Verificar inmediatamente
4. Dejar evidencia reproducible
5. Escalar rápido ante bloqueo real

---

## Lectura obligatoria al inicio de sesión

1. `docs/governance/PROJECT_RULES.md`
2. `docs/governance/CONTEXT.md`
3. `docs/governance/LOG_INDEX.md`
4. Últimas entradas relevantes de `docs/logs/CLAUDE_LOG.md` y `docs/logs/GEMINI_LOG.md`

---

## Forma de trabajo

- Si la tarea es clara → ejecutar, validar, registrar.
- No pedir planificación extensa salvo que la tarea sea ambigua, afecte arquitectura o implique riesgo alto.
- Un cambio por vez. Una hipótesis por intento.
- Mostrar resultado concreto: diff, output del test, siguiente acción.

---

## Reglas de ejecución

- No repetir el mismo intento sin nueva evidencia.
- No inventar rutas, comandos o herramientas no confirmadas.
- No asumir acceso a secretos o sistemas no verificados.
- Scripts bash deben incluir `set -euo pipefail` y manejo de errores explícito.
- Tests y herramientas según el perfil de stack definido en `PROJECT_RULES.md` sección 17.

---

## Validación mínima obligatoria

Después de cada cambio relevante, registrar:
- Archivos afectados
- Comando o acción ejecutada
- Evidencia (output, exit code)
- Estado final
- Riesgo residual

---

## Prohibido

- Rehacer grandes bloques sin justificación.
- Continuar tras un bloqueo repetido.
- Ocultar fallas parciales.
- Marcar completado sin validación mínima.
- Introducir complejidad por "mejora" no solicitada.

---

## Salida mínima esperada

- Acción ejecutada
- Evidencia observada
- Estado
- Siguiente paso recomendado
- Entrada en `docs/logs/CODEX_LOG.md`
- Actualización de `docs/governance/LOG_INDEX.md`
