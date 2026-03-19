#!/usr/bin/env bash
# =============================================================================
# n8n Backup Script
# Crea backup de datos, workflows y credenciales
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="${1:-n8n_local}"
BACKUP_NAME="n8n-backup-${TIMESTAMP}"
CONTAINER_TMP_DIR="/tmp/n8n-backup-temp"

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

echo "=== n8n Backup ==="
echo "Container: ${CONTAINER_NAME}"
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Crear directorio de backups
mkdir -p "${BACKUP_DIR}"

# Verificar que el contenedor está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '${CONTAINER_NAME}' is not running"
    exit 1
fi

# Crear directorio temporal para backup
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

echo "1. Exporting workflows..."
docker_exec_in_container "${CONTAINER_NAME}" mkdir -p "${CONTAINER_TMP_DIR}/workflows"
docker_exec_in_container "${CONTAINER_NAME}" n8n export:workflow --backup \
    --output="${CONTAINER_TMP_DIR}/workflows/" 2>/dev/null || true

echo "2. Exporting credentials (encrypted)..."
docker_exec_in_container "${CONTAINER_NAME}" mkdir -p "${CONTAINER_TMP_DIR}/credentials"
docker_exec_in_container "${CONTAINER_NAME}" n8n export:credentials --backup \
    --output="${CONTAINER_TMP_DIR}/credentials/" 2>/dev/null || true

echo "3. Copying data from container..."
docker cp "${CONTAINER_NAME}:${CONTAINER_TMP_DIR}/." "${TEMP_DIR}/"

# Copiar database si existe (SQLite)
if docker_exec_in_container "${CONTAINER_NAME}" test -f /home/node/.n8n/database.sqlite 2>/dev/null; then
    echo "4. Copying SQLite database..."
    docker cp "${CONTAINER_NAME}:/home/node/.n8n/database.sqlite" "${TEMP_DIR}/"
fi

# Limpiar en container
docker_exec_root_in_container "${CONTAINER_NAME}" rm -rf "${CONTAINER_TMP_DIR}"

echo "5. Creating archive..."
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
tar -czf "${BACKUP_FILE}" -C "${TEMP_DIR}" .

# Calcular tamaño
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)

echo ""
echo "=== Backup Complete ==="
echo "File: ${BACKUP_FILE}"
echo "Size: ${BACKUP_SIZE}"
echo ""
echo "IMPORTANT: This backup contains encrypted credentials."
echo "You need the same N8N_ENCRYPTION_KEY to restore them."
echo ""

# Cleanup old backups (keep last 10)
echo "Cleaning old backups (keeping last 10)..."
ls -t "${BACKUP_DIR}"/n8n-backup-*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f

echo "Done."
