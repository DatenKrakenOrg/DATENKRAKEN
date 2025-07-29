#!/bin/bash
TIMESTAMP=$(date +%F_%T)
docker exec datenkraken_db pg_dump -U ADMIN_USER datenkraken | gzip -9 > full_backup_${TIMESTAMP}.sql.gz
