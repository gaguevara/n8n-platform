# Validación técnica del proyecto

Fecha: 2026-03-19
Entorno: Windows PowerShell + Docker Desktop 29.2.1 + Git Bash

## Alcance
Se ejecutó una validación real de Compose, arranque local, inicialización de PostgreSQL, import/export/backup de workflows y compatibilidad de scripts shell en Windows.

## Resultados

### 1) Docker Compose
- `docker compose -f infra/docker-compose.local.yml config`: **OK**
- `docker compose -f infra/docker-compose.staging.yml config`: **OK** con warnings por variables no definidas (`REDIS_PASSWORD`, `THREAT_DB_PASSWORD`) cuando no existe `.env`
- `docker compose -f infra/docker-compose.prod.yml config`: **OK** como archivo de referencia, con warnings por variables no definidas (`AWS_ACCOUNT_ID`, `AWS_REGION`, `N8N_ENCRYPTION_KEY`, `RDS_*`)

### 2) Runtime local
- `docker compose -f infra/docker-compose.local.yml up -d`: **OK**
- `n8n_local`: **healthy**
- `n8n_threat_db`: **healthy**
- `n8n_threat_cache`: **healthy**
- Verificación en PostgreSQL `threat_intel`: **OK**
  - Tablas públicas: `7`
  - Registros en `data_sources`: `9`
- Verificación en n8n: **OK**
  - Workflows cargados: `1`
  - Nodos en el workflow principal: `30`

### 3) Scripts shell
- `bash -n scripts/backup.sh scripts/export-workflows.sh scripts/import-workflows.sh`: **OK**
- `scripts/import-workflows.sh n8n_local`: **OK**
- `scripts/export-workflows.sh n8n_local`: **OK**
- `scripts/backup.sh n8n_local`: **OK** (sin credenciales para exportar en esta instancia)

### 4) Hallazgos corregidos durante la validación
- `infra/init-db/00-create-dbs.sh` fallaba en `postgres:16-alpine` por usar `#!/bin/bash` y fin de línea Windows.
- `scripts/import-workflows.sh`, `scripts/export-workflows.sh` y `scripts/backup.sh` fallaban en Git Bash por conversión de rutas MSYS hacia `docker exec`.
- `scripts/import-workflows.sh` abortaba con `set -e` por `((IMPORTED++))`.
- `scripts/export-workflows.sh` y `scripts/backup.sh` usaban una sintaxis de `n8n export:*` no compatible con la CLI actual sin `--backup/--separate`.
- Los temporales en rutas bind-mounted causaban errores de permisos al limpiar archivos copiados con `docker cp`.

## Limitaciones del entorno
- `make` no está disponible en `PATH`, por lo que no se ejecutaron targets del `ops/Makefile`.
- `detect-secrets` no está disponible en `PATH`; se hizo revisión manual del diff aplicado y no se introdujeron secretos nuevos.

## Conclusión
- La validación local ya no está pendiente: el stack arranca, el schema y seed se aplican, y los scripts operativos principales funcionan en este entorno Windows.
- Quedan pendientes solo validaciones dependientes de infraestructura externa o variables reales de despliegue (`staging` y `prod`).

## Siguientes pasos recomendados
1. Instalar `make` y `detect-secrets` en la estación de trabajo para completar la cobertura operativa local.
2. Probar `deploy-staging` desde la máquina con acceso al Dell R720 y `.env` real.
3. Completar la especificación y provisión de AWS antes de considerar `deploy-prod`.
