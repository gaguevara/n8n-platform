# Runbook: Operación del Pipeline de Threat Intelligence

Este documento define los procedimientos operativos estándar (SOP) para el mantenimiento, resolución de problemas y respuesta ante incidentes del pipeline de n8n en DELCOP.

---

## 1. Monitoreo de Salud del Sistema

### 1.1 Verificación de Workflows
- **Acceso:** Ir a la UI de n8n (Staging: `http://192.168.0.70:5678`).
- **Vista de Ejecuciones:** Revisar la pestaña "Executions" para confirmar que los crons están disparándose según lo planeado.
- **Error Handler:** Si el workflow `DELCOP n8n Error Handler` se activa, llegará una notificación a Slack (#n8n-errors).

### 1.2 Logs de Auditoría (PostgreSQL)
Consultar la tabla de ejecuciones para estadísticas:
```sql
SELECT workflow_name, status, events_ingested, iocs_created, alerts_sent, finished_at 
FROM workflow_runs 
ORDER BY finished_at DESC LIMIT 10;
```

---

## 2. Procedimientos de Resolución de Fallos

### 2.1 Fuente de Datos Caída (HTTP Timeout/404)
- **Síntoma:** Notificación en Slack indicando error en un nodo `httpRequest` (ej. FortiGate o Wazuh).
- **Acción:**
    1. Verificar conectividad de red desde el host (R720/ECS) a la IP de la fuente.
    2. Confirmar que el servicio origen (Wazuh API, etc.) esté arriba.
    3. El pipeline es resiliente (`continueOnFail: true`), por lo que no detendrá otras fuentes. No se requiere acción inmediata a menos que la caída supere las 24 horas.

### 2.2 Error de Autenticación (401/403)
- **Síntoma:** Error crítico en Slack indicando "Authentication Failure".
- **Acción:**
    1. Revisar si la API Key o Token ha expirado.
    2. Seguir la [Guía de Configuración de Fuentes](./SOURCE_CONFIG_GUIDE.md) para generar una nueva credencial.
    3. Actualizar la variable correspondiente en el archivo `.env` del entorno y reiniciar el servicio:
       ```bash
       # En R720
       cd /srv/n8n-platform
       docker compose restart n8n
       ```

### 2.3 Base de Datos PostgreSQL Llena o Inaccesible
- **Síntoma:** Error crítico general. El Error Handler no podrá loguear en DB pero sí enviará Slack/Email.
- **Acción:**
    1. Verificar espacio en disco en el host.
    2. Revisar logs del contenedor `threat-db`.
    3. Ejecutar el script de limpieza manual si es necesario:
       ```sql
       SELECT cleanup_old_data(30); -- Retener solo 30 días
       ```

---

## 3. Mantenimiento y Gestión de Cambios

### 3.1 Rotación de API Keys
Se recomienda rotar claves cada 90 días o ante sospecha de compromiso.
1. Generar nueva clave en el sistema origen (AbuseIPDB, OTX, FortiGate).
2. Actualizar `.env`.
3. Reiniciar n8n.
4. Ejecutar dry-run manual desde la UI para validar la nueva clave.

### 3.2 Actualización de Workflows
**NUNCA editar el JSON directamente en producción.**
1. Exportar el workflow desde Staging.
2. Hacer commit en el repositorio git.
3. En el entorno destino, ejecutar `make import` o importar vía UI.

---

## 4. Escalación de Alertas

| Nivel de Alerta | Canal | Responsable | Tiempo de Respuesta |
|---|---|---|---|
| **Low / Medium** | PostgreSQL | Auditoría mensual | N/A |
| **High** | Slack / Teams | Equipo de Seguridad | 4 horas (horario laboral) |
| **Critical** | Slack + Email | Administrador de Plataforma | Inmediato |

---

## 5. Reinicio del Pipeline (Disaster Recovery)

Si el contenedor de n8n queda en estado zombie o no responde:
1. Matar procesos: `docker compose down`.
2. Limpiar volúmenes temporales (opcional): `docker volume rm n8n_data` (OJO: Esto borra la DB SQLite de n8n si no hay backup).
3. Levantar: `make dev` (local) o `docker compose up -d`.
4. Re-importar workflows si la DB SQLite se perdió.
