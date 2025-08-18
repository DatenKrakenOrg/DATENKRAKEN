psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
--- Temperature Gold View
CREATE VIEW gold.temperature (bucket_time, arduino_id, avg_value_in_bucket)
AS SELECT time_15m, arduino_id, avg_temperature_at_15m FROM silver.temperature;


--- Humidity Gold View
CREATE VIEW gold.humidity (bucket_time, arduino_id, avg_value_in_bucket)
AS SELECT time_15m, arduino_id, avg_humidity_at_15m FROM silver.humidity;

--- Voc Gold View
CREATE VIEW gold.voc (bucket_time, arduino_id, avg_value_in_bucket)
AS SELECT time_5m, arduino_id, avg_voc_at_5m FROM silver.voc;

--- Noise Gold View
CREATE VIEW gold.noise (bucket_time, arduino_id, avg_value_in_bucket)
AS SELECT time_30s, arduino_id, avg_noise_at_30s FROM silver.noise;

EOSQL