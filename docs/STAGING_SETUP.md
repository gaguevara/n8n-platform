# STAGING_SETUP.md — Setup del Servidor Dell R720

> **Rol:** Guía de instalación inicial y deploy en el servidor de staging (Dell R720)
> **Ejecutar una sola vez.** Para deploys recurrentes usar `make deploy-staging`.

---

## Prerequisitos en el R720

- Docker y Docker Compose v2 instalados (`docker compose version`)
- Git instalado
- Acceso SSH desde tu máquina de desarrollo (clave pública autorizada)
- Puerto 5678 abierto en el firewall local (LAN)

---

## Paso 1 — Clonar el repo en el R720

```bash
# En el servidor R720 (via SSH o consola)
sudo mkdir -p /srv/n8n-platform
sudo chown $USER:$USER /srv/n8n-platform

git clone https://github.com/gaguevara/n8n-platform.git /srv/n8n-platform
cd /srv/n8n-platform
```

---

## Paso 2 — Configurar variables de entorno

```bash
cd /srv/n8n-platform

# Copiar la plantilla de staging
cp .env.staging.example .env

# Editar con los valores reales
nano .env
```

**Variables obligatorias a completar:**

| Variable | Descripción |
|----------|-------------|
| `N8N_ENCRYPTION_KEY` | Generar con `openssl rand -hex 32` |
| `N8N_EDITOR_BASE_URL` | `http://<IP_R720>:5678` |
| `WEBHOOK_URL` | `http://<IP_R720>:5678/` |

---

## Paso 3 — Primer deploy (desde tu máquina en la oficina)

Primero, configura las variables de conexión en tu `.env` local:

```bash
# En tu .env local (máquina de desarrollo)
STAGING_HOST=<IP_o_hostname_R720>
STAGING_USER=<tu_usuario_ssh>
STAGING_PATH=/srv/n8n-platform
```

Luego ejecuta desde `ops/`:

```bash
# Desde tu máquina local
make -C ops deploy-staging
```

El comando hace via SSH:
1. `git pull origin main` — actualiza el código
2. `docker compose pull` — descarga la imagen n8n
3. `docker compose up -d --remove-orphans` — levanta el servicio

---

## Paso 4 — Importar workflows

```bash
make -C ops staging-import
```

---

## Paso 5 — Verificar que staging está sano

```bash
make -C ops staging-status
```

Deberías ver el contenedor en estado `healthy` y el endpoint `/healthz` respondiendo.

---

## Paso 6 — Verificar desde el navegador

Abrir en el navegador de la oficina:
```
http://<IP_R720>:5678
```

---

## Deploy recurrente (después del setup inicial)

Para cada nuevo cambio:

```bash
# 1. Exportar workflows desde local
make -C ops export

# 2. Commit y push
git add app/workflows/
git commit -m "feat: actualizar workflows"
git push

# 3. Desplegar en staging
make -C ops deploy-staging

# 4. Importar workflows y validar
make -C ops staging-validate
```

---

## Troubleshooting

### El contenedor no levanta
```bash
# Ver logs en tiempo real
make -C ops staging-logs

# O directamente en el R720
cd /srv/n8n-platform
docker compose -f infra/docker-compose.staging.yml logs -f
```

### Error de permisos en volúmenes
```bash
# En el R720
docker volume ls | grep n8n_staging
docker volume inspect n8n_staging_data
```

### Actualizar solo la imagen sin cambios de código
```bash
# En el R720
cd /srv/n8n-platform
docker compose -f infra/docker-compose.staging.yml pull
docker compose -f infra/docker-compose.staging.yml up -d
```

---

## Pipeline completo (staging → producción)

Ver [SPEC_STAGING_PIPELINE.md](sdlc/SPEC_STAGING_PIPELINE.md) para el flujo completo hacia AWS ECS.

---

> **Referencia:** `docs/governance/PROJECT_RULES.md` §4 (arquitectura) · `ops/Makefile` (comandos)
> **Última actualización:** 2026-03-17 — Gemini (Researcher)
