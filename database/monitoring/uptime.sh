#!/bin/bash

CSV_FILE="postgres_start_times.csv"
DOCKER_CONTAINER="datenkraken_db"
DB_USER="ADMIN"
DB_NAME="datenkraken"

db_unix_uptime=$(docker exec -i "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -q -c "SELECT floor(extract(epoch from pg_postmaster_start_time()))::text;" 2>/dev/null | tr -d '[:space:]')

if [ -z "$db_unix_uptime" ]; then
    db_unix_uptime="0"
    echo "Warning: Failed to get PostgreSQL start time, defaulting to 0" >&2
fi

current_unix=$(date +%s)

if [ ! -f "$CSV_FILE" ]; then
    echo "postgres_start_time,recorded_time" > "$CSV_FILE"
fi

echo "$db_unix_uptime,$current_unix" >> "$CSV_FILE"

echo "Entry added to $CSV_FILE: $db_unix_uptime, $current_unix"
