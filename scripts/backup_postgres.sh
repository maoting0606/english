#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
STAMP=$(date +%Y%m%d%H%M%S)
docker exec word-postgres pg_dump -U "${POSTGRES_USER:-worduser}" "${POSTGRES_DB:-word_kb}" > "backups/postgres-${STAMP}.sql"
