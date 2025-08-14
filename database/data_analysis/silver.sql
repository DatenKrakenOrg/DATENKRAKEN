--- Accuracy & Validity
--- Check min, max, then take probes out of that and check a 2 minute time intervall for outliers by hand.
SELECT * FROM bronze.temperature ORDER BY temperature DESC LIMIT 50;
SELECT * FROM bronze.noise ORDER BY noise DESC LIMIT 50;
SELECT * FROM bronze.voc ORDER BY voc DESC LIMIT 50;
SELECT * FROM bronze.humidity ORDER BY humidity DESC LIMIT 50;

SELECT * FROM bronze.temperature ORDER BY temperature ASC LIMIT 50;
SELECT * FROM bronze.noise ORDER BY noise ASC LIMIT 50;
SELECT * FROM bronze.voc ORDER BY voc ASC LIMIT 50;
-- All plausible just voc is extremely high, it seems like between 05 and 08 o' clock it rises in unhealthy levels!
SELECT * FROM bronze.humidity ORDER BY humidity ASC LIMIT 50;

-- Check the hypothesis of voc (raising between 5 and 8)

SELECT time::date as Voc_Date, time_bucket('2 hours', time) as bucket, min(voc) as Voc_Minimum, max(voc) as Voc_Maximum
FROM bronze.voc
WHERE time::date >= '2025-08-06'
  AND time::date <= '2025-08-11'
GROUP BY Voc_Date, bucket
ORDER BY Voc_Maximum DESC;

-- Seems like in the morning and evening the voc index is pretty high -> Vents f.e.

--- Timestamp
SELECT * FROM bronze.temperature ORDER BY time DESC LIMIT 50;
SELECT * FROM bronze.noise ORDER BY time DESC LIMIT 50;
SELECT * FROM bronze.voc ORDER BY time DESC LIMIT 50;
SELECT * FROM bronze.humidity ORDER BY time DESC LIMIT 50;

SELECT * FROM bronze.temperature ORDER BY time ASC LIMIT 50;
SELECT * FROM bronze.noise ORDER BY time ASC LIMIT 50;
SELECT * FROM bronze.voc ORDER BY time ASC LIMIT 50;
SELECT * FROM bronze.humidity ORDER BY time ASC LIMIT 50;

--- Completeness & Timeliness
SELECT *
FROM (
    SELECT 
        id,
        time,
        LAG(time) OVER (ORDER BY time) AS previous_time,
        EXTRACT(EPOCH FROM time - LAG(time) OVER (ORDER BY time)) AS diff_seconds
    FROM bronze.temperature
    WHERE time::date < '2026-01-01'
) AS sub
WHERE diff_seconds > 450;