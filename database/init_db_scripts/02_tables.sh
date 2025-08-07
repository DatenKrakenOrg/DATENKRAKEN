#!/bin/bash
# \set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
CREATE TABLE bronze.temperature (
   id          BIGSERIAL         NOT NULL,
   time        TIMESTAMPTZ       NOT NULL,
   deleted_at  TIMESTAMPTZ,
   arduino_id  TEXT              NOT NULL,
   temperature FLOAT4            NOT NULL,
   PRIMARY KEY (id, time)
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.temperature (time, arduino_id, deleted_at);

CREATE TABLE bronze.humidity (
   id          BIGSERIAL         NOT NULL,
   time        TIMESTAMPTZ       NOT NULL,
   deleted_at  TIMESTAMPTZ,
   arduino_id  TEXT              NOT NULL,
   humidity    SMALLINT          NOT NULL,
   PRIMARY KEY (id, time)
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.humidity (time, arduino_id, deleted_at);


CREATE TABLE bronze.voc (
   id          BIGSERIAL         NOT NULL,
   time        TIMESTAMPTZ       NOT NULL,
   deleted_at  TIMESTAMPTZ,
   arduino_id  TEXT              NOT NULL,
   voc         SMALLINT          NOT NULL,
   PRIMARY KEY (id, time)
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.voc (time, arduino_id, deleted_at);

CREATE TABLE bronze.noise (
   id          BIGSERIAL         NOT NULL,
   time        TIMESTAMPTZ       NOT NULL,
   deleted_at  TIMESTAMPTZ,
   arduino_id  TEXT              NOT NULL,
   noise       SMALLINT          NOT NULL,
   PRIMARY KEY (id, time)
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.noise (time, arduino_id, deleted_at);
EOSQL