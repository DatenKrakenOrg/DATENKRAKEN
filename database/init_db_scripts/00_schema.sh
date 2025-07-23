#!/bin/bash
# \set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
-- 1. Create schema for medaillon architectur
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

ALTER ROLE ${POSTGRES_USER} SET search_path TO bronze, silver, gold, public;
EOSQL