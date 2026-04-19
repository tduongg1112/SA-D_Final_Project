#!/bin/bash
set -euo pipefail

if [[ -z "${POSTGRES_MULTIPLE_DATABASES:-}" ]]; then
  exit 0
fi

IFS=',' read -ra DATABASES <<< "${POSTGRES_MULTIPLE_DATABASES}"

for db in "${DATABASES[@]}"; do
  db="$(echo "$db" | xargs)"
  if [[ -z "$db" ]]; then
    continue
  fi

  echo "Creating database '$db' if it does not exist."
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE "$db" OWNER "$POSTGRES_USER"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
done
