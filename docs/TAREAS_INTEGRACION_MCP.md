# Tareas de Integración: Fuentes Threat Intel con MCP Servers

> **Fecha:** 2026-03-22
> **Origen:** Proyecto mcp-servers (Claude Governor)
> **Para:** Agentes del proyecto n8n-platform
> **Prioridad:** Alta

---

## Contexto

El proyecto mcp-servers validó conectividad y credenciales de 3 sistemas. Las APIs están confirmadas funcionales desde el R720 (192.168.0.70). Los agentes de n8n-platform deben integrar estas fuentes en el workflow `threat-intel-main.json`.

---

## 1. FortiGate — Corregir endpoint (CRÍTICO)

**Hallazgo:** ver `docs/HALLAZGO_FORTIGATE_ENDPOINT.md`

**En `app/workflows/threat-intel-main.json`, nodo `http-fortigate`:**

Cambiar:
```json
"url": "={{ $env.FORTIGATE_HOST }}/api/v2/log/event/system"
```
Por:
```json
"url": "={{ $env.FORTIGATE_HOST }}/api/v2/log/memory/event/system"
```

Agregar a query parameters:
```json
{ "name": "vdom", "value": "root" }
```

**Variables ya configuradas en R720 .env:**
- `FORTIGATE_HOST=https://192.168.0.14` ✓
- `FORTIGATE_API_KEY=***` ✓ (en .env del R720, no en repo)
- `FORTIGATE_POLL_INTERVAL=300` ✓

**Validación:** `curl -sk -H "Authorization: Bearer $FORTIGATE_API_KEY" "https://192.168.0.14/api/v2/log/memory/event/system?vdom=root&rows=5"` → 200 OK

---

## 2. Wazuh — Configurar fuente

**Agregar al `.env` de n8n en R720 (`/srv/n8n-platform/.env`):**
```env
WAZUH_API_URL=https://192.168.206.10:55000
WAZUH_API_USER=mcp_readonly
WAZUH_API_PASS=Delcop2026**
```

**Auth flow (JWT):** El workflow ya tiene el nodo correcto:
```
POST /security/user/authenticate → JWT token → GET /alerts
```

**Validado desde R720:**
- Auth: OK (JWT generado)
- Versión: v4.14.4
- Agentes: 12 activos

**Pendiente en workflow:**
- Verificar que el nodo `http-wazuh` usa `$env.WAZUH_API_URL`
- Verificar filtro `rule.level>7`
- Ejecutar dry-run del nodo

---

## 3. Zabbix — Configurar fuente

**Agregar al `.env` de n8n en R720:**
```env
ZABBIX_API_URL=http://192.168.206.12/zabbix/api_jsonrpc.php
ZABBIX_API_TOKEN=4d9bba4020832b25a85f11d0dd132e0d47899cbe1189ef78918031d475ad7852
```

**API:** JSON-RPC 2.0 con Bearer token en header Authorization.

**Validado desde R720:**
- Versión: 7.0.24
- Hosts: 5+ visibles
- Auth: Bearer token OK

**Pendiente en workflow:**
- Verificar que el nodo `http-zabbix` usa `$env.ZABBIX_API_URL` y `$env.ZABBIX_API_TOKEN`
- Método: `trigger.get` con `min_severity: 3`
- Ejecutar dry-run del nodo

---

## 4. Orden de ejecución recomendado

- [x] 1. @CODEX: Agregar variables Wazuh y Zabbix al .env de n8n en R720 — **pendiente del usuario**
- [x] 2. @CODEX: Corregir endpoint FortiGate en workflow JSON — commit `8a1aa78`
- [x] 3. @CODEX: Importar workflow corregido en n8n staging — Codex ENTRADA-019
- [ ] 4. @CODEX: Dry-run nodo FortiGate
- [ ] 5. @CODEX: Dry-run nodo Wazuh (bloqueado: .env pendiente)
- [ ] 6. @CODEX: Dry-run nodo Zabbix (bloqueado: .env pendiente)
- [ ] 7. @CLAUDE: Validar resultados de cada dry-run
- [x] 8. @GEMINI: Documentar evidencia para A.5.7 (Inteligencia de amenazas) — Ver `docs/EVIDENCIA_ISO_A57.md`

### Hallazgo adicional (validado 2026-03-22)
- Zabbix: el nodo usa `auth` en body JSON-RPC (legacy). Zabbix 7.0+ recomienda `Authorization: Bearer` en header. Funcional pero mejorable.
- Recomendación: @CODEX migrar auth a header en Fase 1.7 o posterior.

---

## 5. Notas de seguridad

- Los tokens/passwords están en `.env` del R720, NO en el repo
- `FORTIGATE_API_KEY` ya rotada — próxima rotación: 2026-06-17
- `mcp_readonly` en Wazuh tiene permisos de solo lectura
- Zabbix token creado por `gaguevara` con permisos de lectura

---

*Generado por Claude (Governor) desde proyecto mcp-servers — 2026-03-22*
