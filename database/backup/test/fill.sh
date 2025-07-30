#!/bin/bash
docker exec -i datenkraken_db psql -U ADMIN_USER -d datenkraken < fill_dummy.sql
