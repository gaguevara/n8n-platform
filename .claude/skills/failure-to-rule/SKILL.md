---
name: failure-to-rule
description: Guía el proceso de convertir un fallo repetido en una regla permanente del harness. Usar cuando el anti-loop se activa (mismo error 2 veces sin evidencia nueva).
---

# Failure-to-Rule (FTR)

Este skill guía el proceso del Pattern 03 y el template en `.multiagent/templates/FAILURE_TO_RULE.md`.

## Cuándo se activa
- Mismo error ocurre por segunda vez sin nueva evidencia
- El anti-loop protocol dispara STOP

## Proceso

### 1. STOP
No intentar una tercera vez. El problema es el entorno, no el prompt.

### 2. Analizar
- ¿Qué falló? (error exacto, output, file:line)
- ¿Por qué el entorno lo permitió? (regla faltante, doc obsoleto, constraint ausente)
- ¿Es SYSTEM (aplica a cualquier proyecto) o PROJECT (solo este)?

### 3. Documentar
Copiar el template de `.multiagent/templates/FAILURE_TO_RULE.md` y completar:
- FTR-NNN (siguiente ID)
- Trigger: error específico
- Root cause: gap del harness
- Rule text: imperativo, verificable, 1-2 frases
- Target file: dónde se deploya la regla

### 4. Clasificar
- **SYSTEM** → nueva regla en `.multiagent/core/rules/[stack].md`
- **PROJECT** → nueva regla en `.claude/rules/[project-specific].md`

### 5. Deployar
Agregar el rule text al target file. Marcar Status = DEPLOYED.

### 6. Verificar
Confirmar que la nueva regla habría prevenido el fallo original.

### 7. Registrar
Log entry con tag [FTR] y referencia al FTR-NNN.
