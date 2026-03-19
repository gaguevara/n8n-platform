#!/bin/bash
# Crea múltiples bases de datos en PostgreSQL al inicializar
# Usada por docker-compose via POSTGRES_MULTIPLE_DATABASES env var

set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        SELECT 'CREATE DATABASE $database'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done

    # Ejecutar schema en threat_intel
    if [ -f /docker-entrypoint-initdb.d/01-schema.sql ]; then
        echo "Applying threat_intel schema..."
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d threat_intel < /docker-entrypoint-initdb.d/01-schema.sql
    fi

    echo "Multiple databases created"
fi
