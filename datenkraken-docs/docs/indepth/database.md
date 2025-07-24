# Database
The following chapter describes our decision regarding our database. The database name used within the project is: datenkraken.
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

<b>bronze.SENSORTYPE</b>

### Bronze table size
In order to estimate the final size of the database we inserted 172k rows of realistic dummy data into the temperature table. By examining its relation and index size we wanted to make sure we dont run into future trouble. We found out that the biggest table within the 60 day period of our project would be the temperature table with 16kB of memory usage.

__On ~172k temperature entries => 60min*24h*60days__
```
datenkraken=# SELECT pg_size_pretty(hypertable_size('bronze.temperature'));
 pg_size_pretty 
----------------
 106 MB
(1 row)
```

__On ~5m noise entries => 60min*24h*60days*60 entries per minute__
```
datenkraken=# SELECT pg_size_pretty(hypertable_size('bronze.noise'));
 pg_size_pretty 
----------------
 341 MB
(1 row)
```

Although this table size isn't very high we decided to create a composite index on the columns time and arduino_id in order to speed up read processes. We only need a composite index out of three reasons:

1. Our use case primarily will only need two filters within the dashboard -> in general by time (to scale diagrams), by time and arduino_id (to view each room). Therefore a composite index should be created.
2. Even if we filter only for time (for development purposes) timescale has a index on time by default.
3. Even if we filter only for arduino_id, we defined segments (partitions) for arduino_id on our hypertable definition.

When we want to detect bugs later on this could therefore help a lot, since in the worst case we had to trace it from gold to bronze layer and vice versa.