# Database
## Bronze
The bronze table has to store roughly 172k messages in the 60 days of our project period as discussed here <a href=""></a>. As specified the sensor data must be stored in the following fields (with additional fields of the <a href="/DATENKRAKEN/arduino/mqtt/">messageformat</a>).

Since we collect sensordata using different sample rates in order to be more memory efficient, we propose 4 tables in the bronze layer. Each stores the raw data of each sensor.

Fields that are part of all tables:
1. time: TIMESTAMPTZ
2. arduino_id: text -> denormalized since timescaledb does a dictionary compression / + enums do not allow to delete individual values within enum <a href="https://www.postgresql.org/docs/current/datatype-enum.html">8.7. Enumerated Types</a>

Field per table:
1. temperature: float4 
2. humidity: smallint
3. voc: smallint
4. noise: smallint

This type of bronze layer definition is chosen due to the public recommendation by timescaledb. First we thought about storing all values for each 30 seconds intervall within an array. By that we can ensure to persist all data within one table. But we could not find any references that ensure, that this wouldn't lead to performance issues on data aggregation as it's common with the array type on relational databases.

Also if we would persist it within a single table (without arrays) we would introduce many null values. That would lead to a growth of memory space since timescaledb interprets a "Null" as actual value. <a href="https://www.tigerdata.com/blog/best-practices-for-picking-postgresql-data-types">Best Practices for Picking PostgreSQL Data Types</a>.

Therefore we chose a multiple table design as proposed in <a href="https://www.tigerdata.com/learn/best-practices-time-series-data-modeling-single-or-multiple-partitioned-tables-aka-hypertables">Best Practices for Time-Series Data Modeling: Single or Multiple Partitioned Table(s) a.k.a. Hypertables</a>

The tables are named in the following schema:
<b>SENSORTYPE_bronze</b>

## Bronze TimescaleDB specific settings
By free command we examined the ram size of the AI401 server. It showed around 405 gb ram. Assuming 6 groups this would mean each group should have around 64 gb ram free (~- MQTT Broker, Docker Containers, etc.). By default

