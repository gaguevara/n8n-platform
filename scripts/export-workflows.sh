#!/usr/bin/env bash
# =============================================================================
# n8n Workflow Export Script
# Exporta todos los flujos a JSON para versionado en Git
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPORT_DIR="${PROJECT_ROOT}/app/workflows"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="${1:-n8n_local}"

echo "=== n8n Workflow Export ==="
echo "Container: ${CONTAINER_NAME}"
echo "Export to: ${EXPORT_DIR}"
echo ""

# Verificar que el contenedor está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '${CONTAINER_NAME}' is not running"
    echo ""
    echo "Available containers:"
    docker ps --format '  - {{.Names}}'
    echo ""
    echo "Usage: $0 [container_name]"
    echo "  Default: n8n_local"
    echo "  Staging: $0 n8n_staging"
    exit 1
fi

# Crear directorio de export si no existe
mkdir -p "${EXPORT_DIR}"

# Crear directorio temporal en container
docker exec "${CONTAINER_NAME}" mkdir -p /home/node/.n8n/export-temp/

# Exportar todos los workflows
echo "Exporting all workflows..."
docker exec "${CONTAINER_NAME}" n8n export:workflow --all --output=/home/node/.n8n/export-temp/ 2>/dev/null || {
    echo "Warning: n8n export command returned non-zero (may be empty)"
}

# Copiar archivos exportados al host
docker cp "${CONTAINER_NAME}:/home/node/.n8n/export-temp/." "${EXPORT_DIR}/" 2>/dev/null || true

# Limpiar directorio temporal en container
docker exec "${CONTAINER_NAME}" rm -rf /home/node/.n8n/export-temp/

# Contar workflows exportados
WORKFLOW_COUNT=$(find "${EXPORT_DIR}" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l)

echo ""
echo "=== Export Complete ==="
echo "Exported ${WORKFLOW_COUNT} workflow(s)"
echo ""

if [ "${WORKFLOW_COUNT}" -gt 0 ]; then
    echo "Workflows exported:"
    find "${EXPORT_DIR}" -maxdepth 1 -name "*.json" -type f -exec basename {} \; | sort
    echo ""
    echo "Next steps:"
    echo "  git add app/workflows/"
    echo "  git commit -m 'chore: export workflows ${TIMESTAMP}'"
    echo "  git push"
else
    echo "No workflows found to export."
    echo "Create some workflows in n8n UI first."
fi
