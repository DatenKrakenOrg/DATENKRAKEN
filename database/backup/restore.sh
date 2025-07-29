#!/bin/bash
gunzip -c full_backup_*.sql.gz | docker exec -i datenkraken_db psql -U ADMIN_USER -d datenkraken
