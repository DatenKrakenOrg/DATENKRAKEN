psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

--- Temperature MV
CREATE MATERIALIZED VIEW silver.temperature (time_15m, arduino_id, avg_temperature_at_15m, stddev_temperature_at_15m)
WITH (timescaledb.continuous, timescaledb.create_group_indexes)
AS SELECT time_bucket('15 minutes', time) as time_15m, arduino_id, AVG(temperature) as avg_temperature_at_15m, STDDEV_POP(temperature) AS stddev_temperature_at_15m
FROM bronze.temperature
WHERE time BETWEEN '2025-08-05 00:00:00+02' AND NOW() AND deleted_at IS NULL AND temperature > 10 AND temperature < 40
GROUP BY time_15m, arduino_id;

SELECT add_continuous_aggregate_policy(
  'silver.temperature',
  start_offset      => INTERVAL '30 days',
  end_offset        => INTERVAL '15 minutes',
  schedule_interval => INTERVAL '15 minutes'
);

--- Humidity MV
CREATE MATERIALIZED VIEW silver.humidity (time_15m, arduino_id, avg_humidity_at_15m, stddev_humidity_at_15m)
WITH (timescaledb.continuous, timescaledb.create_group_indexes)
AS SELECT time_bucket('15 minutes', time) as time_15m, arduino_id, AVG(humidity) as avg_humidity_at_15m, STDDEV_POP(humidity) AS stddev_humidity_at_15m
FROM bronze.humidity
WHERE time BETWEEN '2025-08-05 00:00:00+02' AND NOW() AND deleted_at IS NULL AND humidity >= 0 AND humidity <= 100
GROUP BY time_15m, arduino_id;

SELECT add_continuous_aggregate_policy(
  'silver.humidity',
  start_offset      => INTERVAL '30 days',
  end_offset        => INTERVAL '15 minutes',
  schedule_interval => INTERVAL '15 minutes'
);

--- Voc MV
CREATE MATERIALIZED VIEW silver.voc (time_5m, arduino_id, avg_voc_at_5m, stddev_voc_at_5m)
WITH (timescaledb.continuous, timescaledb.create_group_indexes)
AS SELECT time_bucket('5 minutes', time) as time_5m, arduino_id, AVG(voc) as avg_voc_at_5m, STDDEV_POP(voc) AS stddev_voc_at_5m
FROM bronze.voc
WHERE time BETWEEN '2025-08-05 00:00:00+02' AND NOW() AND deleted_at IS NULL AND voc >= 0 AND voc <= 500
GROUP BY time_5m, arduino_id;

SELECT add_continuous_aggregate_policy(
  'silver.voc',
  start_offset      => INTERVAL '30 days',
  end_offset        => INTERVAL '5 minutes',
  schedule_interval => INTERVAL '5 minutes'
);

--- Noise MV
CREATE MATERIALIZED VIEW silver.noise (time_30s, arduino_id, avg_noise_at_30s, stddev_noise_at_30s)
WITH (timescaledb.continuous, timescaledb.create_group_indexes)
AS SELECT time_bucket('30 seconds', time) as time_30s, arduino_id, AVG(noise) as avg_noise_at_30s, STDDEV_POP(noise) AS stddev_noise_at_30s
FROM bronze.noise
WHERE time BETWEEN '2025-08-05 00:00:00+02' AND NOW() AND deleted_at IS NULL AND noise >= 0 AND noise <= 1023
GROUP BY time_30s, arduino_id;

--- Update intervall higher in order to not trigger too many jobs -> realtime is on anyways

SELECT add_continuous_aggregate_policy(
  'silver.noise',
  start_offset      => INTERVAL '30 days',
  end_offset        => INTERVAL '30 seconds',
  schedule_interval => INTERVAL '5 minutes'
);

ALTER MATERIALIZED VIEW silver.temperature SET (timescaledb.materialized_only = false);
ALTER MATERIALIZED VIEW silver.humidity    SET (timescaledb.materialized_only = false);
ALTER MATERIALIZED VIEW silver.voc         SET (timescaledb.materialized_only = false);
ALTER MATERIALIZED VIEW silver.noise       SET (timescaledb.materialized_only = false);

EOSQL