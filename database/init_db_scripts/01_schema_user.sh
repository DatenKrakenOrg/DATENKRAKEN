#!/bin/bash
# \set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE ui WITH LOGIN PASSWORD '${UI_PASSWORD}';
    GRANT USAGE ON SCHEMA gold TO ui;
    ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT SELECT ON TABLES TO ui;
    GRANT SELECT ON ALL TABLES IN SCHEMA gold TO ui;

    CREATE ROLE dev with LOGIN PASSWORD '${DEV_PASSWORD}';
    GRANT USAGE ON SCHEMA bronze TO dev;
    GRANT USAGE ON SCHEMA silver TO dev;
    GRANT USAGE ON SCHEMA gold TO dev;
    ALTER DEFAULT PRIVILEGES IN SCHEMA bronze GRANT SELECT, INSERT, UPDATE ON TABLES TO dev;
    ALTER DEFAULT PRIVILEGES IN SCHEMA bronze GRANT USAGE ON SEQUENCES TO dev;
    -- Default privileges granted for update only on is_deleted column -> not easily done due to timescale compressing
    ALTER DEFAULT PRIVILEGES IN SCHEMA silver GRANT ALL ON TABLES TO dev;
    ALTER DEFAULT PRIVILEGES IN SCHEMA silver GRANT USAGE ON SEQUENCES TO dev;
    ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT ALL ON TABLES TO dev;
    ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT USAGE ON SEQUENCES TO dev;
    
    REVOKE DELETE ON ALL TABLES IN SCHEMA bronze FROM dev;

    ALTER ROLE ui SET search_path TO gold, public;
    ALTER ROLE dev SET search_path TO bronze, silver, gold, public;
    ALTER ROLE ${POSTGRES_USER} SET search_path TO bronze, silver, gold, public;
EOSQL