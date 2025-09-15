FROM timescale/timescaledb:latest-pg17
COPY ./init_db_scripts/ /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/*.sh

