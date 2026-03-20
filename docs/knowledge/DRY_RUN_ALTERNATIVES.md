# Investigación: Alternativas a `n8n execute` para Dry-Runs

## 1. Problema Actual
En el entorno de staging (Dell R720), el comando `n8n execute --id <ID>` falla porque intenta levantar una instancia parcial de n8n que colisiona con el puerto `5679` (Task Broker) ya utilizado por el contenedor principal.

## 2. Hallazgos de la API REST (v1)
Según la documentación oficial de la [Public API v1 de n8n](https://docs.n8n.io/api/remote-api/), **no existe un endpoint directo** para ejecutar un workflow por su ID (ej. `POST /workflows/{id}/run`).

La API v1 solo permite:
- Listar, obtener, activar y desactivar workflows.
- Consultar el estado de ejecuciones pasadas.
- Re-intentar ejecuciones fallidas.

## 3. Alternativas Identificadas

### 3.1 Nodo Webhook (Recomendado)
Agregar un nodo `Webhook` al inicio del workflow.
- **Ventaja:** Permite ejecución remota vía `curl` o Postman.
- **Desventaja:** Requiere modificar el workflow y activarlo en producción.

### 3.2 Uso de la UI (Manual)
Ejecutar manualmente presionando el botón "Execute Workflow" en la UI.
- **Ventaja:** No requiere configuración adicional.
- **Desventaja:** Difícil de automatizar en scripts de validación (Codex).

### 3.3 API Interna (No soportada)
La UI de n8n utiliza un endpoint interno `POST /rest/workflows/{id}/run`.
- **Riesgo:** Requiere autenticación de sesión (cookie/token de login) y puede cambiar sin previo aviso ya que no es una API pública. **No se recomienda para automatización.**

## 4. Recomendación Técnica
Para automatizar validaciones sin colisiones de puertos:
1. **Habilitar el nodo Webhook** solo en entornos de Staging con un path genérico (ej. `/trigger-dry-run`).
2. **Usar `curl`** desde los scripts de validación de Codex para disparar el evento.
3. **Validar la respuesta** o consultar el estado vía API v1 en `/executions`.
