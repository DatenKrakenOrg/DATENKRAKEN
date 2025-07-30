#!/bin/bash
docker exec -it datenkraken_db psql -U ADMIN_USER -d datenkraken -c "SELECT COUNT(*) FROM bronze.noise;"
