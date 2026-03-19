# Threat Intelligence — Trellix Email Integration

**Fuente:** Trellix (ex-FireEye/McAfee) vía ePO email notifications
**Método:** IMAP / Outlook Trigger sobre buzón dedicado
**Workflow:** `threat-intel-trellix-email.json`

---

## 1. Formato del correo

### Headers

| Campo | Valor |
|---|---|
| From | `do-not-reply@manage.trellix.com` |
| To | `comite.seguridad@delcop.com.co`, `gabriel.guevara@delcop.com`, `informatica@xcol.co` |

### Body (texto plano, 6 líneas por evento)

```
L1: {fecha} {hora} {event_id}
L2: {event_code} {severity} {threat_type} {threat_name} {flag}
L3: {protection_module} {action}
L4: {domain}\{user} {IP} {hostname}
L5: {org_path}
L6: {process}
```

### Ejemplo real

```
9/29/25 3:00 PM ENDPATP_1070
35104 Critical Trojan JTI/Suspect.524610!2e5a8590cf68 True
Adaptive Threat Protection Blocked
AWS\osierra 192.168.1.68 H0LDTQ2
My Organization\AWS\XCOL\H0LDTQ2
mshta.exe
```

---

## 2. Reglas de parseo

### Línea 1: Fecha + Event ID

- Formato fecha: `M/D/YY H:MM AM/PM` (hora local, no UTC)
- Event ID: última palabra de la línea (e.g., `ENDPATP_1070`)
- `ENDPATP` = Endpoint Adaptive Threat Protection

### Línea 2: Código + Severidad + Amenaza

- Primer token numérico = event code
- Busca match exacto contra: `critical`, `high`, `medium`, `low`, `info`
- Threat type: palabra después de severidad (`Trojan`, `Exploit`, `Virus`, etc.)
- Threat name: token que contiene `/` o `!` (firma Trellix)
- El `!` separa familia de hash parcial: `JTI/Suspect.524610!2e5a8590cf68`

### Línea 3: Módulo + Acción

- Acciones conocidas: `blocked`, `detected`, `cleaned`, `deleted`, `quarantined`, `allowed`, `denied`, `would block`
- Todo antes de la acción = nombre del módulo de protección

### Línea 4: Usuario + IP + Hostname

- Formato usuario: `DOMAIN\username`
- IP: regex IPv4 estándar
- Hostname: último token que no es IP ni `DOMAIN\user`
- **La IP casi siempre es privada (192.168.x.x)**. Se guarda como metadata, no como IoC externo.

### Línea 5: Ruta organizacional

- Formato ePO: `My Organization\{grupo}\{subgrupo}\{hostname}`
- Útil para identificar qué sede/unidad de negocio

### Línea 6: Proceso

- Nombre del ejecutable que disparó la alerta
- Si es LOLBin (mshta.exe, wscript.exe, powershell.exe, etc.), se marca `lolbin: true`

---

## 3. IoCs generados

| Condición | IoC Type | Role |
|---|---|---|
| Threat name presente | `file_name` | `indicator` |
| Hash completo extraído del threat name | `hash_md5/sha1/sha256` | `indicator` |
| IP pública en L4 | `ip_v4` | `indicator` |
| IP privada en L4 | N/A | Se guarda en `asset_ip`, no como IoC |
| Hash parcial (< 32 chars) | N/A | Se guarda en `metadata.hash_partial` |
| CVE en body | `cve` | `indicator` |
| SHA256 en body | `hash_sha256` | `indicator` |

---

## 4. Limitaciones conocidas

1. **Hash parcial**: Trellix incluye un hash truncado después del `!` en el threat name. En el ejemplo, `2e5a8590cf68` tiene solo 12 chars. No es MD5 (32), SHA1 (40) ni SHA256 (64). Se registra pero no se crea IoC.

2. **IPs siempre internas**: En la infraestructura DELCOP, las alertas de Trellix reportan la IP privada del endpoint. Para obtener IPs externas maliciosas necesitarías correlacionar con logs de FortiGate o el proxy.

3. **Formato no estándar**: Trellix no manda JSON ni XML. El formato de texto plano puede variar entre tipos de alerta (ATP, Exploit Prevention, Access Protection, Firewall). El parser es tolerante pero puede fallar con formatos no vistos.

4. **Un email = un evento**: No se observaron emails batch con múltiples eventos. Si Trellix envía resúmenes, el parser necesitará ajuste.

5. **Timezone**: La hora en el email es local (Colombia, GMT-5). El parser la interpreta como local y convierte a ISO 8601.

---

## 5. Troubleshooting: no llegan correos

Verificar en este orden:

1. **Consola ePO/Trellix**: ¿La regla de notificación por email está habilitada y activa?
2. **Destinatario**: ¿El buzón dedicado (`trellix-alerts@delcop.com.co`) está en la lista de destinatarios?
3. **Relay SMTP**: ¿El servidor ePO puede alcanzar el relay SMTP? Verificar con telnet/nmap desde el servidor ePO.
4. **Exchange Online**: ¿Hay reglas de transporte que bloqueen o redirigan correos de `@manage.trellix.com`?
5. **Cuarentena**: ¿Defender for Office 365 está filtrando como spam? Verificar en `security.microsoft.com` → Email & collaboration → Review → Quarantine.
6. **Certificado TLS**: Si el relay usa STARTTLS, ¿el certificado está vigente?
7. **Licencia Trellix**: ¿El contrato de soporte/suscripción sigue activo?

---

## 6. Configuración del buzón

### Recomendado: buzón dedicado en M365

```
Buzón: trellix-alerts@delcop.com.co
Tipo: Shared Mailbox (sin licencia)
Acceso: IMAP habilitado O app registration con Graph API
```

### Variables en `.env`

```env
TRELLIX_IMAP_HOST=outlook.office365.com
TRELLIX_IMAP_PORT=993
TRELLIX_IMAP_USER=trellix-alerts@delcop.com.co
TRELLIX_IMAP_PASSWORD=
TRELLIX_IMAP_TLS=true
```

### Alternativa: Outlook Trigger

Si el buzón está en M365, usar el nodo `Microsoft Outlook Trigger` en lugar de IMAP. Requiere app registration con permisos `Mail.Read` en Microsoft Entra ID.
