#!/bin/sh
# Crea múltiples bases de datos en PostgreSQL al inicializar.
# Alpine no incluye bash por defecto, así que este script debe ser POSIX sh.

set -eu

create_user_and_database() {
    database="$1"
    echo "Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
        SELECT format('CREATE DATABASE %I', '$database')
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
        GRANT ALL PRIVILEGES ON DATABASE "$database" TO "$POSTGRES_USER";
EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(printf '%s' "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        create_user_and_database "$db"
    done

    echo "Multiple databases created"
fi
