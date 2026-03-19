#!/usr/bin/env bash
# =============================================================================
# n8n Workflow Import Script
# Importa flujos desde archivos JSON al entorno n8n
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMPORT_DIR="${PROJECT_ROOT}/app/workflows"
CONTAINER_NAME="${1:-n8n_local}"
CONTAINER_TMP_DIR="/tmp/n8n-import-temp"

docker_exec_in_container() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' docker exec "$@"
            ;;
        *)
            docker exec "$@"
            ;;
    esac
}

docker_exec_root_in_container() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' docker exec -u 0 "$@"
            ;;
        *)
            docker exec -u 0 "$@"
            ;;
    esac
}

echo "=== n8n Workflow Import ==="
echo "Container: ${CONTAINER_NAME}"
echo "Import from: ${IMPORT_DIR}"
echo ""

# Verificar que el contenedor está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '${CONTAINER_NAME}' is not running"
    echo ""
    echo "Available containers:"
    docker ps --format '  - {{.Names}}'
    echo ""
    echo "Usage: $0 [container_name]"
    exit 1
fi

# Verificar que hay workflows para importar
if [ ! -d "${IMPORT_DIR}" ]; then
    echo "ERROR: Directory ${IMPORT_DIR} does not exist"
    exit 1
fi

WORKFLOW_FILES=$(find "${IMPORT_DIR}" -maxdepth 1 -name "*.json" -type f 2>/dev/null)
WORKFLOW_COUNT=$(echo "${WORKFLOW_FILES}" | grep -c . || echo 0)

if [ "${WORKFLOW_COUNT}" -eq 0 ]; then
    echo "No workflow files found in ${IMPORT_DIR}"
    exit 0
fi

echo "Found ${WORKFLOW_COUNT} workflow(s) to import"
echo ""

# Crear directorio temporal en container
docker_exec_root_in_container "${CONTAINER_NAME}" mkdir -p "${CONTAINER_TMP_DIR}"

# Importar cada workflow
echo "Importing workflows..."
IMPORTED=0
FAILED=0

for file in ${IMPORT_DIR}/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo -n "  - ${filename}: "
        docker cp "$file" "${CONTAINER_NAME}:${CONTAINER_TMP_DIR}/${filename}"

        if docker_exec_in_container "${CONTAINER_NAME}" n8n import:workflow \
            --input="${CONTAINER_TMP_DIR}/${filename}" 2>/dev/null; then
            echo "OK"
            IMPORTED=$((IMPORTED + 1))
        else
            echo "FAILED"
            FAILED=$((FAILED + 1))
        fi
    fi
done

# Limpiar directorio temporal
docker_exec_root_in_container "${CONTAINER_NAME}" rm -rf "${CONTAINER_TMP_DIR}"

echo ""
echo "=== Import Complete ==="
echo "Imported: ${IMPORTED}"
echo "Failed: ${FAILED}"
echo ""
echo "Refresh n8n UI to see imported workflows"
