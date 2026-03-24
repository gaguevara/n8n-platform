# AGENT_SKILLS_MATRIX.md — Catálogo de Habilidades de los Agentes

> **Propósito:** Define las habilidades que los agentes deben demostrar y las herramientas que deben saber usar. Los agentes consultan este archivo para saber qué se espera de ellos.

---

## 1. Habilidades de Código

### 1.1 Lectura y comprensión

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Leer y entender código existente | Navegar un codebase desconocido, identificar entry points, flujo de datos y dependencias | El agente puede explicar qué hace un módulo sin documentación previa |
| Identificar code smells | Detectar violaciones de SOLID, código muerto, duplicación, funciones largas | El agente señala problemas en code review sin que se lo pidan |
| Trazar dependencias | Seguir la cadena de imports/requires para entender impacto de un cambio | El agente lista archivos afectados antes de proponer un cambio |

### 1.2 Escritura

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Código limpio por defecto | Nombres claros, funciones pequeñas, un nivel de abstracción, sin magic numbers | El código pasa revisión sin comentarios sobre naming o estructura |
| Tests junto al código | Generar tests unitarios que cubran happy path + edge cases + error cases | Cobertura mínima del caso principal y al menos 2 edge cases |
| Error handling explícito | Capturar excepciones específicas con contexto, no bare except | El agente nunca genera `except Exception: pass` |
| Documentación inline | Docstrings para funciones públicas, type hints donde aplique | Funciones públicas tienen docstring con params y return |

### 1.3 Refactoring

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Extract Method | Identificar bloques extraíbles y refactorizar | Funciones resultantes ≤ 20 líneas |
| Rename para claridad | Proponer nombres más descriptivos | Sin variables de 1-2 letras fuera de loops |
| Simplificar condicionales | Reducir anidamiento con early returns o guard clauses | Máximo 2 niveles de indentación en condicionales |
| Eliminar duplicación | Identificar y consolidar código repetido | DRY aplicado sin sobre-abstracción |

---

## 2. Habilidades de Arquitectura

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Evaluar trade-offs | Comparar alternativas con pros/contras concretos | El agente presenta mínimo 2 opciones con criterios antes de recomendar |
| Aplicar patrones correctos | Elegir el patrón de diseño adecuado al problema, no el más complejo | Justificación explícita de por qué ese patrón y no otro |
| Respetar boundaries | No violar la separación de capas o módulos | Import graphs limpios, sin dependencias circulares |
| Documentar decisiones | Registrar ADRs cuando hay alternativas consideradas | ADR con: decisión, alternativas, justificación, riesgos |

---

## 3. Habilidades de Seguridad

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Detectar secrets en código | Identificar credenciales hardcodeadas, tokens, API keys | Scan de strings sospechosos antes de commit |
| Validar inputs | Todo input externo es hostil — sanitizar y validar | No hay `eval()`, SQL crudo con interpolación, ni deserialización sin validación |
| Revisar dependencias | Verificar CVEs en dependencias del proyecto | Ejecutar `pip-audit`, `npm audit`, o equivalente |
| Escanear contenedores | Verificar vulnerabilidades en imágenes Docker | Ejecutar `trivy image` o equivalente |
| Principio de mínimo privilegio | Permisos, roles y accesos al mínimo necesario | IAM policies y DB roles revisados |

---

## 4. Habilidades de DevOps / Infraestructura

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Docker fluido | Crear, modificar y depurar Dockerfiles y docker-compose | Imágenes funcionales con usuario no-root, multi-stage si aplica |
| Interpretar logs | Leer y diagnosticar errores desde container logs, app logs, DB logs | Diagnóstico correcto en ≤ 3 iteraciones |
| CI/CD básico | Entender pipelines, stages, artifacts, triggers | Puede proponer un pipeline para el proyecto |
| IaC lectura | Leer y entender Terraform/CloudFormation/scripts de infraestructura | Identifica recursos, dependencias y variables |

---

## 5. Habilidades de Comunicación Técnica

| Habilidad | Descripción | Verificación |
|-----------|-------------|--------------|
| Explicar decisiones | Justificar por qué, no solo qué | Toda recomendación incluye "porque..." |
| Documentar para terceros | Un desarrollador nuevo entiende el contexto sin preguntar | CONTEXT.md y logs son autoexplicativos |
| Escalar con evidencia | Si no puede resolver, reporta: error, hipótesis, evidencia, siguiente acción | No hay escalaciones vagas tipo "no funciona" |
| Registrar actividad | Dejar trazabilidad de lo que hizo, por qué y con qué resultado | Log completo con formato estándar |

---

## 6. Habilidades por Rol de Agente

### Claude Code — Arquitecto / Validador

Habilidades primarias: Arquitectura, Refactoring, Docker, ADRs, Revisión final
Habilidades de soporte: Security review, Documentación técnica

### Codex CLI — Código / Seguridad

Habilidades primarias: Escritura de código, Tests, Security scan, Dependencias
Habilidades de soporte: Refactoring, Code review

### Gemini Code Assist — Optimización / Performance

Habilidades primarias: Análisis de performance, Queries SQL, Costos cloud, Algoritmos
Habilidades de soporte: Refactoring, Documentación

### 6.4 Fuentes externas (Community Skills)

| Fuente | Descripción | Uso |
|--------|-------------|-----|
| `skills.sh` | Catálogo comunitario (+89K) de mejores prácticas y seguridad | `npx skills add -y <repo>` |
| `Context7 (MCP)` | Documentación de librerías en tiempo real | `query-docs` |
| `superpowers:systematic-debugging` | Fuerza investigación de causa raíz antes de corregir bugs o fallas de tests | Aplicar ante cualquier comportamiento inesperado o regresión |
| `superpowers:verification-before-completion` | Exige evidencia fresca antes de declarar éxito, fix o suite en verde | Ejecutar antes de cerrar tareas, validar PRs o afirmar que algo pasó |
| `superpowers:subagent-driven-development` | Estructura ejecución por tareas con revisión de spec y calidad en dos etapas | Usar en implementaciones con subtareas independientes en la misma sesión |

---

## 7. Skill Gaps — Proceso de Mejora

Cuando un agente no puede ejecutar una habilidad esperada:

1. Registrar en el log del agente: habilidad, contexto, resultado
2. Evaluar si es limitación del modelo o falta de contexto (harness gap)
3. Si es falta de contexto → mejorar el harness (docs, tools, specs)
4. Si es limitación del modelo → documentar y asignar a otro agente o al humano
5. Actualizar este archivo si se identifican habilidades nuevas necesarias

---

*Este archivo es parte del framework multi-agente. Se revisa al menos cada trimestre o cuando se identifiquen skill gaps nuevos.*
