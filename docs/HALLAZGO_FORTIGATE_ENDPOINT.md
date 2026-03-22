# Hallazgo: Endpoint FortiGate incorrecto en workflow threat-intel-main

> **Fecha:** 2026-03-22
> **Detectado por:** Claude (Governor) — proyecto mcp-servers
> **Severidad:** Alta — el workflow no recolectará logs correctamente
> **Workflow:** `app/workflows/threat-intel-main.json`
> **Nodo:** `http-fortigate` (ID: `http-fortigate`, línea ~68)

---

## Problema

El nodo "GET FortiGate Logs" usa el endpoint:
```
{{ $env.FORTIGATE_HOST }}/api/v2/log/event/system
```

Este endpoint **devuelve 404** en FortiOS 7.4.11. El path correcto validado en equipo real es:
```
{{ $env.FORTIGATE_HOST }}/api/v2/log/memory/event/system
```

## Referencia

Documentado como **Error E-3** en `SPEC-001` del proyecto mcp-servers:
> `/api/v2/monitor/log/{type}` y `/api/v2/log/{type}` devuelven 404. Path correcto: `/api/v2/log/memory/{category}`

## Endpoints correctos (validados 2026-03-19 en equipo real)

| Endpoint | Uso |
|----------|-----|
| `/api/v2/log/memory/event/system?vdom=root&rows=N` | Eventos del sistema |
| `/api/v2/log/memory/ips?vdom=root&rows=N` | IPS |
| `/api/v2/log/memory/virus?vdom=root&rows=N` | Antivirus |
| `/api/v2/log/memory/webfilter?vdom=root&rows=N` | WebFilter |
| `/api/v2/log/memory/app-ctrl?vdom=root&rows=N` | App Control |
| `/api/v2/log/memory/traffic/forward?vdom=root&rows=N` | Tráfico forward |

## Corrección requerida

En `app/workflows/threat-intel-main.json`, nodo `http-fortigate`:

**Cambiar:**
```json
"url": "={{ $env.FORTIGATE_HOST }}/api/v2/log/event/system"
```

**Por:**
```json
"url": "={{ $env.FORTIGATE_HOST }}/api/v2/log/memory/event/system"
```

También agregar `vdom=root` a los query parameters:
```json
{ "name": "vdom", "value": "root" }
```

## Estado

- [x] Variables FORTIGATE_HOST y FORTIGATE_API_KEY configuradas en .env del R720
- [x] API accesible desde container n8n (verificado 2026-03-22)
- [x] Corregir endpoint en workflow JSON (commit pendiente)
- [ ] Importar workflow corregido en n8n staging
- [ ] Ejecutar dry-run del nodo FortiGate

---

*Hallazgo cruzado entre proyectos mcp-servers ↔ n8n-platform*
