#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
-- 1. Create schema for medaillon architectur
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- 2. Timezone
ALTER SYSTEM SET timezone = 'Europe/Berlin';
SELECT pg_reload_conf();
EOSQL