# =============================================================================
# n8n Platform - Makefile
# =============================================================================

.PHONY: help dev build push deploy-staging deploy-prod logs export import backup

# Default values (override con: make deploy-staging TAG=v1.2.3)
TAG ?= dev-$(shell date +%Y%m%d-%H%M)
ENV_FILE ?= ../.env

# Load .env if exists
ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export
endif

# Defaults si no están en .env
AWS_REGION ?= us-east-1
AWS_ACCOUNT_ID ?= 123456789012
ECR_REGISTRY ?= $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/delcop/n8n
STAGING_HOST ?= staging-server
STAGING_USER ?= admin
STAGING_PATH ?= /srv/n8n-platform

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
help:
	@echo "n8n Platform - Comandos disponibles:"
	@echo ""
	@echo "  DESARROLLO LOCAL:"
	@echo "    make dev              - Levantar n8n en Docker Desktop"
	@echo "    make dev-down         - Detener n8n local"
	@echo "    make dev-logs         - Ver logs en tiempo real"
	@echo "    make dev-shell        - Shell dentro del container"
	@echo ""
	@echo "  WORKFLOWS:"
	@echo "    make export           - Exportar workflows a app/workflows/"
	@echo "    make import           - Importar workflows desde app/workflows/"
	@echo "    make backup           - Backup completo de datos"
	@echo ""
	@echo "  BUILD & DEPLOY:"
	@echo "    make build            - Construir imagen Docker"
	@echo "    make push-ecr         - Push a AWS ECR"
	@echo "    make deploy-staging   - Desplegar en R720 (staging)"
	@echo "    make deploy-prod      - Desplegar en AWS ECS (prod)"
	@echo ""
	@echo "  VARIABLES:"
	@echo "    TAG=dev-20250126      - Tag de imagen (default: dev-YYYYMMDD-HHMM)"
	@echo ""

# -----------------------------------------------------------------------------
# Desarrollo Local (Docker Desktop)
# -----------------------------------------------------------------------------
dev:
	@echo ">>> Iniciando n8n local..."
	docker compose -f infra/docker-compose.local.yml up --build -d
	@echo ">>> n8n disponible en http://localhost:$${N8N_PORT:-5678}"

dev-down:
	docker compose -f infra/docker-compose.local.yml down

dev-logs:
	docker compose -f infra/docker-compose.local.yml logs -f

dev-shell:
	docker exec -it n8n_local /bin/sh

dev-restart:
	docker compose -f infra/docker-compose.local.yml restart

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------
build:
	@echo ">>> Building image with tag: $(TAG)"
	docker build -t n8n-delcop:$(TAG) -f infra/Dockerfile .
	docker tag n8n-delcop:$(TAG) n8n-delcop:latest

# -----------------------------------------------------------------------------
# Push to AWS ECR
# -----------------------------------------------------------------------------
ecr-login:
	@echo ">>> Login to ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

push-ecr: build ecr-login
	@echo ">>> Pushing to ECR: $(ECR_REGISTRY):$(TAG)"
	docker tag n8n-delcop:$(TAG) $(ECR_REGISTRY):$(TAG)
	docker tag n8n-delcop:$(TAG) $(ECR_REGISTRY):latest
	docker push $(ECR_REGISTRY):$(TAG)
	docker push $(ECR_REGISTRY):latest

# -----------------------------------------------------------------------------
# Deploy Staging (Dell R720)
# -----------------------------------------------------------------------------
deploy-staging:
	@echo ">>> Deploying to staging: $(STAGING_HOST)"
	@echo ">>> Image tag: $(TAG)"
	ssh $(STAGING_USER)@$(STAGING_HOST) "\
		cd $(STAGING_PATH) && \
		git pull origin main && \
		export TAG=$(TAG) && \
		docker compose -f infra/docker-compose.staging.yml pull && \
		docker compose -f infra/docker-compose.staging.yml up -d --remove-orphans && \
		docker compose -f infra/docker-compose.staging.yml ps"

staging-logs:
	ssh $(STAGING_USER)@$(STAGING_HOST) "\
		cd $(STAGING_PATH)/infra && \
		docker compose -f docker-compose.staging.yml logs -f --tail=100"

staging-status:
	ssh $(STAGING_USER)@$(STAGING_HOST) "\
		cd $(STAGING_PATH)/infra && \
		docker compose -f docker-compose.staging.yml ps && \
		docker compose -f docker-compose.staging.yml exec n8n wget -qO- http://localhost:5678/healthz"

# -----------------------------------------------------------------------------
# Deploy Production (AWS ECS)
# -----------------------------------------------------------------------------
deploy-prod: push-ecr
	@echo ">>> Deploying to AWS ECS..."
	@echo ">>> Updating ECS service to use image: $(ECR_REGISTRY):$(TAG)"
	aws ecs update-service \
		--cluster n8n-cluster \
		--service n8n-service \
		--force-new-deployment \
		--region $(AWS_REGION)
	@echo ">>> Deployment initiated. Monitor in AWS Console."

# -----------------------------------------------------------------------------
# Workflow Management
# -----------------------------------------------------------------------------
export:
	@echo ">>> Exporting workflows..."
	@bash scripts/export-workflows.sh

import:
	@echo ">>> Importing workflows..."
	@bash scripts/import-workflows.sh

# -----------------------------------------------------------------------------
# Backup
# -----------------------------------------------------------------------------
backup:
	@echo ">>> Creating backup..."
	@bash scripts/backup.sh

backup-staging:
	@echo ">>> Creating staging backup..."
	ssh $(STAGING_USER)@$(STAGING_HOST) "\
		cd $(STAGING_PATH) && \
		bash scripts/backup.sh"
