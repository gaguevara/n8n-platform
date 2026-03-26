# Checklist de Activación Pre-Cron (Threat Intel Pipeline)

Este documento define las verificaciones obligatorias que deben cumplirse **antes** de activar cualquier trigger de tipo cron para las fuentes del pipeline de Threat Intelligence en el entorno de producción o staging. El objetivo es evitar loops de error, alertas falsas masivas y bloqueos de cuenta por rate limits.

## 1. Verificaciones por cada fuente individual

Antes de habilitar el nodo cron que consulta una fuente específica (FortiGate, Wazuh, Zabbix, etc.), asegúrese de completar:

- [ ] **Conectividad a la API**: El entorno de ejecución (R720 o AWS ECS) puede alcanzar el endpoint de la API por la red sin restricciones de firewall (Security Groups, ACLs).
- [ ] **Validación de Credencial**: El token, API key, o usuario/contraseña está activo, no ha expirado y tiene los permisos mínimos necesarios (read-only recomendado).
- [ ] **Dry-Run OK**: Se ejecutó la consulta manualmente (vía interfaz UI de n8n o cURL simulado) devolviendo una respuesta JSON válida (HTTP 200).
- [x] **Wazuh Indexer (API)**: Desbloqueado vía Reverse Proxy (Nginx) en el servidor Wazuh (`192.168.206.10:9201`).
    - **Configuración**: Nginx actúa como terminador SSL y proxy hacia `127.0.0.1:9200`.
    - **Seguridad**: Whitelist de IP aplicada para permitir solo tráfico desde el Dell R720 (`192.168.0.70`).
    - **Validación**: Conectividad validada desde R720 con respuesta exitosa del clúster.

## 2. Verificaciones del Core y Persistencia

- [ ] **Conexión a Base de Datos**: El nodo PostgreSQL de n8n se conecta exitosamente a `threat-db`.
- [ ] **PG-Upsert OK**: La operación de inserción o actualización (upsert) en la tabla `iocs` fue exitosa usando un registro de prueba. (Recordar limpiar este dato de prueba luego).
- [ ] **Estrategia de Deduplicación**: Se validó que el pipeline no está generando entradas duplicadas por ejecuciones secuenciales con el mismo set de datos (comportamiento idempotente).

## 3. Verificaciones de Alertas y Salida (Alert Dispatcher)

- [ ] **Configuración de Canales**: Los Webhooks de Slack/Teams y la configuración SMTP de correo están definidos correctamente en las variables de entorno.
- [ ] **Fallo Controlado (Graceful Fail)**: Si un canal de notificación está inaccesible o la credencial de SMTP es incorrecta, se comprobó que el flujo no detiene el procesamiento general de IoCs.
- [ ] **Ruido de Alertas**: Se confirmó que los umbrales de puntuación (ej. mayor a 70 o 85) aplican bien sobre la muestra y el sistema no hará "spam" masivo a los canales.

---
> **Nota de Gobernanza**: Nunca modifique los intervalos del Cron a tiempos extremadamente cortos (ej. cada minuto) durante la fase inicial para evitar bloqueos por rate-limiting de las APIs OSINT (como AbuseIPDB u OTX).
