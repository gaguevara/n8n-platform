# Checklist de Monitoreo Post-Activación (24h)

Este documento define las métricas y verificaciones obligatorias a realizar durante las primeras 24 horas tras la activación de los triggers Cron en el pipeline de Threat Intelligence.

---

## 0. Estrategia de Activación Progresiva (Piloto)

Para minimizar el radio de impacto, no se deben activar todos los cron triggers simultáneamente. Seguir este orden:

1.  **T1 (Zabbix)**: Activar trigger de 5 min. Monitorear 15 min. Buscar `zabbix` en la tabla `iocs`.
2.  **T2 (FortiGate)**: Activar triggers (Events, IPS, Virus). Monitorear 15 min. Buscar `fortigate` en la tabla `iocs`.
3.  **T3 (Wazuh)**: Activar trigger de 10 min (según recomendación Gemini). Monitorear 30 min. Buscar `wazuh` en la tabla `iocs`.

---

## 1. Verificaciones de Salud del Workflow (n8n UI)

- [ ] **Ejecuciones Exitosas**: El workflow debe mostrar ejecuciones verdes para cada trigger.
    - FortiGate: Cada 5 min.
    - Wazuh: Cada 5-10 min (según configuración inicial).
    - GuardDuty: Cada 5 min.
    - Zabbix: Cada 5 min.
    - OSINT: Cada 15 min.
- [ ] **Latencia de Ejecución**: Confirmar que ninguna ejecución tome más de 60 segundos (riesgo de solapamiento si los nodos de enriquecimiento tardan demasiado).
- [ ] **Logs de Error**: Revisar la pestaña "Executions" filtrando por `Error`. Investigar cualquier `401 Unauthorized` o `403 Forbidden` inmediatamente.

---

## 2. Verificaciones de Datos (PostgreSQL)

Ejecutar las siguientes consultas en la base de datos `threat_intel` (Dell R720):

### 2.1 Conteo de IoCs generados
```sql
-- Verificar que se están insertando IoCs
SELECT source, count(*) 
FROM iocs 
WHERE observed_at > NOW() - INTERVAL '24 hours' 
GROUP BY source;
```

### 2.2 Registro de Auditoría
```sql
-- Verificar balance de ingesta vs creación
SELECT workflow_name, status, events_ingested, iocs_created, alerts_sent, finished_at 
FROM workflow_runs 
ORDER BY finished_at DESC 
LIMIT 20;
```

---

## 3. Verificaciones de Notificación

- [ ] **Canales Activos**: Confirmar la recepción de al menos una alerta de prueba (o real de severidad High/Critical) en:
    - [ ] Slack (`#security-alerts-test`)
    - [ ] Microsoft Teams
    - [ ] Email (seguridad@delcop.com.co)
- [ ] **Formato de Alerta**: Validar que el mensaje contiene el valor del IoC, la fuente, el score de amenaza y el enlace a la ejecución de n8n.

---

## 4. Recursos del Sistema (Infraestructura)

- [ ] **Uso de Disco**: `docker exec n8n_threat_db du -sh /var/lib/postgresql/data`. Asegurar que el crecimiento es lineal y manejable.
- [ ] **Uso de CPU/RAM**: `docker stats`. n8n no debe exceder de forma sostenida los 2GB de RAM ni el 50% de un core de CPU durante los picos de cron.

---

## 5. Umbrales de Alarma (Acción Inmediata)

| Escenario | Acción |
|---|---|
| > 5 fallos consecutivos de una fuente | Desactivar cron de esa fuente y revisar credenciales. |
| > 100 alertas en 15 minutos | Posible falso positivo masivo. Detener workflow y revisar `ioc_scorer.js`. |
| Error `database is locked` | Problema de concurrencia en PostgreSQL. Revisar pool de conexiones. |

---
*Generado por Gemini (Researcher + Reviewer) — 2026-03-25*
