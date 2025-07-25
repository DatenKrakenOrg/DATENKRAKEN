#!/bin/bash
# \set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
CREATE TABLE bronze.temperature (
   time        TIMESTAMPTZ       NOT NULL,
   arduino_id  TEXT              NOT NULL,
   temperature FLOAT4            NOT NULL
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.temperature (time, arduino_id);

CREATE TABLE bronze.humidity (
   time        TIMESTAMPTZ       NOT NULL,
   arduino_id  TEXT              NOT NULL,
   humidity    SMALLINT          NOT NULL
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.humidity (time, arduino_id);


CREATE TABLE bronze.voc (
   time        TIMESTAMPTZ       NOT NULL,
   arduino_id  TEXT              NOT NULL,
   voc         SMALLINT          NOT NULL
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.voc (time, arduino_id);

CREATE TABLE bronze.noise (
   time        TIMESTAMPTZ       NOT NULL,
   arduino_id  TEXT              NOT NULL,
   noise       SMALLINT          NOT NULL
) WITH (
   tsdb.hypertable,
   tsdb.partition_column='time',
   tsdb.segmentby = 'arduino_id',
   tsdb.orderby = 'time DESC'
);

CREATE INDEX ON bronze.noise (time, arduino_id);
EOSQL