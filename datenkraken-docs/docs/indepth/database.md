# Database
The following chapter describes our decision regarding our database. The database name used within the project is: datenkraken.

There are three users within the database:
**ui** -> read-only on gold schema
**dev** -> all privileges on tables within bronze, silver, gold except for delte
**datenkraken_admin** -> all

Configuration via .env:
```bash
POSTGRES_USER=
POSTGRES_PASSWORD=
UI_PASSWORD=
DEV_PASSWORD=
```
## Bronze
The bronze table has to store roughly 172k messages in the 60 days of our project period as discussed here <a href=""></a>. As specified the sensor data must be stored in the following fields (with additional fields of the <a href="/DATENKRAKEN/arduino/mqtt/">messageformat</a>).

Since we collect sensordata using different sample rates in order to be more memory efficient, we propose 4 tables in the bronze layer. Each stores the raw data of each sensor.

Fields that are part of all tables:

1. id: BIGSERIAL => used for composite primary key with the time field. => Composite primary key since this is the proposed way of timescaledb without inheriting any bottlenocks due to the index. (See down below: Best practices)

2. time: TIMESTAMPTZ

3. arduino_id: text -> denormalized since timescaledb does a dictionary compression / + enums do not allow to delete individual values within enum <a href="https://www.postgresql.org/docs/current/datatype-enum.html">8.7. Enumerated Types</a>

4. deleted_at: TIMESTAMPZ -> soft delete

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
In order to estimate the final size of the database we inserted 172k rows of realistic dummy data into the temperature table. And 5m rows in the noise table. By examining its relation and index size we wanted to make sure we dont run into future trouble. We found out that the biggest table within the 60 day period of our project would be the noise table with 341mb of memory usage.

_On ~172k temperature entries => 60min x 24h x 60days_
```
datenkraken=# SELECT pg_size_pretty(hypertable_size('bronze.temperature'));
 pg_size_pretty 
----------------
 106 MB
(1 row)
```

_On ~5m noise entries => 60min x 24h x 60days x 60 entries per minute_
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

# Silver
The purpose of this layer is to create filtered and cleaned layer of data. We develop the layer definition by the typical data quality criterias:

1. **Accuracy** - How correct is the data values?
2. **Completeness** - Is all information present?
3. **Consistency** - Does the data match other trusted data sources?    
4. **Validity** - Does the data conform to the predetermined format & constraints?
5. **Timeliness** - How up-to-date is the data?
6. **Intergrity** - Is the data maintained & updates over time?
7. **Uniqueness** - How little duplication is there in the records?

## Accuracy & Validity
Since we don't have direct access to other data sources we check the datas accuracy and validity based on plausibility rule set. Therefore we examine the columns as following

1. values -> sorted by min, max  see if range is plausible + singular values -> see whether values are plausible
2. time -> sorted by min, max + singular values -> see whether formatting works right / if it needs to be cleaned / pruned

We used the following query to check those:

### Values Min, Max Check
```sql
SELECT * FROM bronze.table ORDER BY values DESC LIMIT 50;
```
-> Check for min max values. (via desc, asc)

On first sight we have seen, that we have extreme outliers for bronze.voc. Where the common voc should be around 50 according to research we found many points lying in the region of around 100 - 300. When examining the data points via interval nesting of the ids we've seen that the outliers aren't actually "outliers" but the voc index is just pretty high in the morning. Therefore we wrote the following query, which looks for the min and max in a one hour interval per day:

```sql
SELECT time::date as Voc_Date, time_bucket('1 hours', time) as bucket, min(voc) as Voc_Minimum, max(voc) as Voc_Maximum
FROM bronze.voc
WHERE time::date = '2025-08-06'
GROUP BY Voc_Date, bucket
ORDER BY bucket ASC;
```

This produces the following output:

```
  voc_date  |         bucket         | voc_minimum | voc_maximum 
------------+------------------------+-------------+-------------
 2025-08-06 | 2025-08-06 00:00:00+02 |         212 |         263
 2025-08-06 | 2025-08-06 01:00:00+02 |         261 |         281
 2025-08-06 | 2025-08-06 02:00:00+02 |         279 |         296
 2025-08-06 | 2025-08-06 03:00:00+02 |         296 |         313
 2025-08-06 | 2025-08-06 04:00:00+02 |         313 |         325
 2025-08-06 | 2025-08-06 05:00:00+02 |         325 |         335
 2025-08-06 | 2025-08-06 06:00:00+02 |         118 |         337
 2025-08-06 | 2025-08-06 07:00:00+02 |          51 |         118
 2025-08-06 | 2025-08-06 08:00:00+02 |          44 |         265
 2025-08-06 | 2025-08-06 09:00:00+02 |          15 |         162
 2025-08-06 | 2025-08-06 10:00:00+02 |          21 |         110
 2025-08-06 | 2025-08-06 11:00:00+02 |          14 |          21
 2025-08-06 | 2025-08-06 12:00:00+02 |           3 |          40
 2025-08-06 | 2025-08-06 13:00:00+02 |           4 |          34
 2025-08-06 | 2025-08-06 14:00:00+02 |          15 |          34
 2025-08-06 | 2025-08-06 15:00:00+02 |          20 |          23
 2025-08-06 | 2025-08-06 16:00:00+02 |          18 |          30
 2025-08-06 | 2025-08-06 17:00:00+02 |          22 |          30
 2025-08-06 | 2025-08-06 18:00:00+02 |          29 |          35
 2025-08-06 | 2025-08-06 19:00:00+02 |          28 |          33
 2025-08-06 | 2025-08-06 20:00:00+02 |          27 |          46
 2025-08-06 | 2025-08-06 21:00:00+02 |          46 |          73
 2025-08-06 | 2025-08-06 22:00:00+02 |          73 |         100
 2025-08-06 | 2025-08-06 23:00:00+02 |         100 |         127
```

The following days show a similar output. BUT on weeknds the voc index stays permanently high, heres a sample of it:

```
  voc_date  |         bucket         | voc_minimum | voc_maximum 
------------+------------------------+-------------+-------------
 2025-08-09 | 2025-08-09 00:00:00+02 |         140 |         166
 2025-08-09 | 2025-08-09 01:00:00+02 |         166 |         199
 2025-08-09 | 2025-08-09 02:00:00+02 |         200 |         212
 2025-08-09 | 2025-08-09 03:00:00+02 |         212 |         226
 2025-08-09 | 2025-08-09 04:00:00+02 |         227 |         241
 2025-08-09 | 2025-08-09 05:00:00+02 |         241 |         248
 2025-08-09 | 2025-08-09 06:00:00+02 |         248 |         260
 2025-08-09 | 2025-08-09 07:00:00+02 |         260 |         266
 2025-08-09 | 2025-08-09 08:00:00+02 |         266 |         271
 2025-08-09 | 2025-08-09 09:00:00+02 |         260 |         271
 2025-08-09 | 2025-08-09 10:00:00+02 |         251 |         260
 2025-08-09 | 2025-08-09 11:00:00+02 |         251 |         251
 2025-08-09 | 2025-08-09 12:00:00+02 |         250 |         251
 2025-08-09 | 2025-08-09 13:00:00+02 |         251 |         251
 2025-08-09 | 2025-08-09 14:00:00+02 |         251 |         253
 2025-08-09 | 2025-08-09 15:00:00+02 |         253 |         253
 2025-08-09 | 2025-08-09 16:00:00+02 |         253 |         254
 2025-08-09 | 2025-08-09 17:00:00+02 |         253 |         254
 2025-08-09 | 2025-08-09 18:00:00+02 |         253 |         253
 2025-08-09 | 2025-08-09 19:00:00+02 |         253 |         254
 2025-08-09 | 2025-08-09 20:00:00+02 |         252 |         254
 2025-08-09 | 2025-08-09 21:00:00+02 |         252 |         252
 2025-08-09 | 2025-08-09 22:00:00+02 |         251 |         252
 2025-08-09 | 2025-08-09 23:00:00+02 |         250 |         251
```

 We therefore conclude it doesn't have to do with bad data quality (f.e. in a lack of sensor quality), but it seems like the air quality just turns bad, due to reasons like (disabled vents, etc.) => We could talk about that with the facility management.

 **Except for that no other flaws could be found depending the values.

 ### Timestamp

 When examining the timestamp the same way as in the Values check, we see that there multiple timestamp that differ largely in its id of the datetime around 2036-02-07 07:28:46+01. It seems like there is a bug in the timeline which we could take a look at later. It shouldn't be a hurry since those points are really rare and not concurrent.

 But still a plausibility check should be introduced, especially since problems are already occuring.

 ### Solution Strategy
 We introduce plausibility checks for the technical valid ranges that the sensors produce output for. Other than that we filter timestamp for the range of the start date around 05. August and the todays date (since the bug occurs only for the year 2036 this should be filtered out easily)

 Our checks would therefore filter as following:
 - Temperature: 0 - 50 (plausible with some offset)
 - Humidity: 0 - 100
 - Noise: 0 - 1023
 - Voc: 0 - 500
 - Time: 05. August - NOW()
