#!/usr/bin/env bash
set -euo pipefail
TAG="${1:-latest}"
ssh usuario@staging-host <<EOF
  export TAG=$TAG
  cd /srv/n8n-platform/infra
  docker login registry.local:5000
  docker compose -f docker-compose.staging.yml pull
  docker compose -f docker-compose.staging.yml up -d --remove-orphans
EOF
