# Guía de Configuración de Fuentes de Threat Intelligence

Este documento detalla los pasos para configurar los accesos de mínimo privilegio para cada fuente del pipeline de n8n DELCOP.

---

## 1. FortiGate (FortiOS)

Para obtener logs via REST API, se debe crear un perfil de acceso y un usuario de API.

### 1.1 Crear Perfil de Acceso (CLI)
```bash
config system accprofile
    edit "n8n_threat_read"
        set loggrp read          # Acceso solo lectura a logs
        set sysgrp read          # Necesario para visibilidad básica del sistema
    next
end
```

### 1.2 Crear Usuario de API y Token
1. Ir a **System** → **Administrators**.
2. Crear nuevo **REST API User**.
3. **Username:** `n8n_threat_intel`
4. **Profile:** `n8n_threat_read`
5. **Trusted Hosts:** Agregar la IP del servidor n8n (R720 / AWS ECS). **Obligatorio para seguridad.**
6. Al guardar, se generará el **API Key**. Copiarlo inmediatamente (no se vuelve a mostrar).

---

## 2. Wazuh (RBAC)

Wazuh requiere permisos tanto en el Indexer (OpenSearch) como en la API.

### 2.1 Rol en Wazuh Indexer (Datos)
Crear un rol (ej. `wazuh_readonly_alerts`) con:
- **Index Permissions:** `wazuh-alerts-*`, `wazuh-states-*`
- **Privileges:** `read`

### 2.2 Política en Wazuh API (Interface)
Crear una política con las siguientes acciones permitidas:
- `agent:read`
- `group:read`
- `rules:read`
- `decoders:read`
- `syscheck:read`
- `sca:read`

### 2.3 Mapeo de Usuario
1. Crear el usuario en **Server Management** → **Security** → **Users**.
2. Mapear el usuario al rol de Indexer y a la política de API.
3. Verificar en `/usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml` que `run_as: true` esté configurado si se accede via Dashboard.

---

## 3. Zabbix (API Tokens)

Zabbix 6.0+ permite el uso de tokens de larga duración con roles específicos.

### 3.1 Crear User Role
1. **Administration** → **User roles** → **Create user role**.
2. **User type:** `User`.
3. **API access:** `Enabled`.
4. **API methods:** `Allow list`.
5. Agregar: `host.get`, `trigger.get`, `item.get`, `history.get`.

### 3.2 Crear Usuario de Servicio
1. **Administration** → **Users** → **Create user**.
2. **Username:** `svc_n8n_threat`.
3. **Role:** El rol creado en el paso 3.1.
4. **Permissions:** Asegurar que el usuario pertenezca a un grupo con permisos de **Read** sobre los Host Groups que se desean monitorear.

### 3.3 Generar Token
1. **Administration** → **API tokens** → **Create API token**.
2. Seleccionar el usuario `svc_n8n_threat`.
3. Copiar el token generado.

---

## 4. AWS GuardDuty

### 4.1 Identificación del Detector
En la cuenta `043019737945` (us-east-1), el detector activo es:
- **Detector ID:** `68c960313fc4628bdf683f052e953cf5`

### 4.2 Política IAM de Mínimo Privilegio
Asignar esta política al usuario/rol que consumirá n8n:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GuardDutyReadFindings",
            "Effect": "Allow",
            "Action": [
                "guardduty:ListFindings",
                "guardduty:GetFindings"
            ],
            "Resource": "arn:aws:guardduty:us-east-1:043019737945:detector/68c960313fc4628bdf683f052e953cf5"
        }
    ]
}
```

---

## 5. Fuentes OSINT

### 5.1 AbuseIPDB
1. Registrarse en [abuseipdb.com](https://www.abuseipdb.com/).
2. Ir a **API** → **Create Key**.
3. El tier gratuito permite 1,000 checks por día. El cron de 15 min consume ~96 checks/día por IP.

### 5.2 AlienVault OTX
1. Registrarse en [otx.alienvault.com](https://otx.alienvault.com/).
2. Ir a **Settings** → **API Key**.
3. Suscribirse a pulses (ej. "Malware", "Botnet") para recibir datos en el feed de `subscribed`.

### 5.3 VirusTotal
1. Registrarse en [virustotal.com](https://www.virustotal.com/).
2. Ir a su perfil → **API Key**.
3. **Límites Tier Gratuito:** 4 peticiones por minuto, 500 peticiones por día. El pipeline debe usar un nodo `Wait` o `Throttle` si se procesan batches grandes.

---

## 6. Trellix (Email/IMAP)

Trellix ePO envía alertas en formato de texto plano que n8n debe parsear.

### 6.1 Configuración del Buzón (M365)
1. Crear un **Shared Mailbox** (ej. `trellix-alerts@delcop.com.co`).
2. Habilitar **IMAP** para el buzón si se usa el nodo IMAP, o crear una **App Registration** en Azure con permisos `Mail.Read` si se usa el nodo Microsoft Outlook.
3. Asegurar que ePO tiene configurado este buzón como destinatario en sus reglas de notificación.

### 6.2 Reglas de Notificación en ePO
1. **Automation** → **Automatic Responses**.
2. Crear/Editar respuesta para eventos críticos (ej. `ENDPATP_1070`).
3. En **Actions**, seleccionar **Send Email**.
4. **Formato:** Texto plano (es vital para el parser `trellix_email_parser.js`).

---

## 7. Resumen de Límites de API (OSINT)

| Fuente | Límite (Gratuito) | Estrategia en n8n |
|---|---|---|
| **AbuseIPDB** | 1,000 / día | Cron cada 15 min (batch de 100 IPs max) |
| **AlienVault OTX** | 10,000 / hora | Cron cada 15 min (pulses recientes) |
| **VirusTotal** | 4 / min \| 500 / día | Nodo `Wait` entre peticiones de enriquecimiento |