# n8n Platform - DELCOP

Plataforma de automatización de workflows con pipeline completo: desarrollo local → staging (R720) → producción (AWS).

## Arquitectura de Entornos

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LOCAL (Dev)   │    │    STAGING      │    │   PRODUCTION    │
│  Docker Desktop │───▶│   Dell R720     │───▶│    AWS ECS      │
│  Win11/Home Lab │    │   VMware/Docker │    │   Fargate       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      SQLite              SQLite/Volume         PostgreSQL RDS
```

## Quick Start (Desarrollo Local)

```bash
# 1. Clonar
git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/n8n-platform
cd n8n-platform

# 2. Configurar
cp .env.example .env
# Editar .env: generar N8N_ENCRYPTION_KEY con: openssl rand -hex 32

# 3. Levantar
make -C ops dev

# 4. Acceder
# http://localhost:5678
```

## Estructura del Proyecto

```
n8n-platform/
├── app/
│   └── workflows/          # JSON exportados (versionados en Git)
├── infra/
│   ├── Dockerfile          # Imagen custom con timezone
│   ├── docker-compose.local.yml
│   ├── docker-compose.staging.yml
│   └── docker-compose.prod.yml    # Referencia para ECS
├── ops/
│   └── Makefile            # Comandos de operación
├── scripts/
│   ├── export-workflows.sh
│   ├── import-workflows.sh
│   └── backup.sh
├── docs/
│   ├── SECURITY.md
│   ├── QUALITY.md
│   └── AWS_DEPLOYMENT.md
├── .vscode/
│   └── tasks.json          # Tareas para VS Code
├── data/                   # Persistencia local (gitignore)
├── shared-files/           # Archivos para nodos I/O
├── .env.example
├── .gitignore
└── README.md
```

## Comandos Disponibles

```bash
# Ver todos los comandos
make -C ops help

# DESARROLLO LOCAL
make -C ops dev              # Iniciar n8n
make -C ops dev-down         # Detener
make -C ops dev-logs         # Ver logs
make -C ops dev-shell        # Shell en container

# WORKFLOWS
make -C ops export           # Exportar a app/workflows/
make -C ops import           # Importar desde app/workflows/
make -C ops backup           # Backup completo

# DEPLOY
make -C ops build            # Construir imagen
make -C ops push-ecr         # Push a AWS ECR
make -C ops deploy-staging   # Deploy a R720
make -C ops deploy-prod      # Deploy a AWS ECS
```

## Workflow de Desarrollo

### 1. Desarrollo Local
```bash
make -C ops dev
# Crear/modificar workflows en http://localhost:5678
# Probar hasta que funcionen
```

### 2. Versionar Workflows
```bash
make -C ops export
git add app/workflows/
git commit -m "feat: nuevo workflow de notificaciones"
git push
```

### 3. Deploy a Staging
```bash
make -C ops build
make -C ops deploy-staging TAG=dev-20250126
# Probar en staging
```

### 4. Deploy a Producción
```bash
make -C ops deploy-prod TAG=v1.0.0
```

## Gestión de Credenciales

Las credenciales se almacenan **encriptadas** usando `N8N_ENCRYPTION_KEY`.

**IMPORTANTE:**
- Misma key = credenciales portables entre entornos
- Key diferente = reconfigurar credenciales manualmente
- **NUNCA** versionar la key en Git

### Migrar credenciales entre entornos:
1. Usar la misma `N8N_ENCRYPTION_KEY` en `.env`
2. O exportar/importar manualmente desde n8n UI

## VS Code

Abrir el proyecto en VS Code y usar `Ctrl+Shift+P` → "Tasks: Run Task" para ver las tareas disponibles.

## Troubleshooting

### Container no inicia
```bash
make -C ops dev-logs
# Verificar permisos de data/
```

### Puerto ocupado
Editar `.env`: `N8N_PORT=5679`

### Credenciales inválidas
La `N8N_ENCRYPTION_KEY` cambió. Reconfigurar credenciales en UI.

### Webhook no funciona en local
Los webhooks requieren URL pública. Opciones:
- Usar n8n tunnel (desarrollo): `N8N_TUNNEL_ENABLED=true`
- ngrok / cloudflared para testing
