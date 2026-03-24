# SPEC: Gestión de Errores y Observabilidad en n8n

## 1. Objetivo
Garantizar que cualquier fallo en el pipeline de Threat Intelligence sea detectado, notificado y persistido para su posterior análisis, minimizando el tiempo de inactividad del sistema de seguridad.

## 2. Arquitectura del Manejador de Errores

El sistema utilizará un **Error Workflow** centralizado en n8n, configurado en los "Settings" de cada flujo de trabajo (`errorWorkflow`).

### 2.1 Flujo de Datos
1. **Trigger:** Nodo `Error Trigger` recibe el payload de error de n8n.
2. **Normalización:** Un nodo `Code` extrae:
    - `workflow_name`: Nombre del flujo que falló.
    - `node_name`: Nodo exacto donde ocurrió el error.
    - `error_message`: Descripción corta del error.
    - `error_stack`: Stack trace completo (para persistencia).
    - `execution_id`: ID de ejecución en n8n para debugging directo.
3. **Persistencia:** Se inserta un registro en la tabla `audit_log` con `entity_type='workflow'` y `action='error'`.
4. **Notificación:**
    - Errores de fuentes OSINT o timeouts individuales: Alerta **Warning** en Slack/Teams.
    - Errores de Base de Datos, Autenticación o Fallo Crítico: Alerta **Critical** en Slack/Teams + Email.

## 3. Clasificación de Errores

| Tipo de Error | Severidad | Acción |
|---|---|---|
| **Conectividad DB** | Critical | Notificación inmediata (Slack/Email) + Re-intento (3 veces) |
| **Auth Failure** | Critical | Notificación inmediata + Desactivar trigger (opcional) |
| **Rate Limit Exceeded** | Warning | Notificación (Slack) + Pausa de 1 hora |
| **Timeout (Single Source)** | Warning | Log en DB + Notificación si persiste > 3 ciclos |
| **Parse Error (IOC)** | Info/Low | Log en DB (metadata del evento) |

## 4. Implementación en n8n

### 4.1 Variables de Entorno Requeridas
- `ERROR_SLACK_WEBHOOK_URL`: Canal dedicado a logs de errores (`#n8n-errors`).
- `ERROR_EMAIL_RECIPIENT`: Correo del administrador de seguridad.

### 4.2 Esquema de Persistencia (PostgreSQL)
Se utilizará la tabla `audit_log` existente:
```sql
INSERT INTO audit_log (entity_type, entity_id, action, actor, details)
VALUES (
    'workflow',
    $execution_id,
    'error',
    $workflow_name,
    jsonb_build_object(
        'node', $node_name,
        'message', $error_message,
        'stack', $error_stack
    )
);
```

## 5. Mejores Prácticas
- **Evitar bucles de error:** El Error Workflow NO debe tener configurado un Error Workflow.
- **Deduplicación de alertas:** No enviar alertas repetidas por el mismo error en un intervalo de 5 minutos (usar `threat-cache` Redis para check de frecuencia).
- **Contexto:** Incluir siempre el enlace directo a la ejecución fallida: `https://n8n.delcop.com.co/execution/{{ $execution_id }}`.
