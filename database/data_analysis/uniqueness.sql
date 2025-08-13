-- Uniqueness

-- Temperature cv
\echo TemperatureCV
WITH
params(win) AS (
  -- Bucket intervals
  SELECT unnest(ARRAY[
    interval '1 min',
    interval '2 min',
    interval '4 min',
    interval '5 min',
    interval '15 min',
    interval '30 min',
    interval '1 hour',
    interval '2 hours'
  ])
),
-- 1) Threshhold r of cv
threshold AS (
  SELECT 0.05::double precision AS r
),
-- Temperature for each bucket of day => Cross Joined to combine all params
base AS (
  SELECT
    p.win,
    date_trunc('day', t.time)                AS day_id,
    time_bucket(p.win, t.time)               AS bucket,
    t.temperature
  FROM bronze.temperature t
  CROSS JOIN params p
),
-- Mean and Sample std for each bucket
stats AS (
  SELECT
    win,
    day_id,
    bucket,
    AVG(temperature)              AS mean,
    STDDEV_SAMP(temperature)      AS sd
  FROM base
  GROUP BY win, day_id, bucket
),
-- Variational Coefficient for each bcket
vc AS (
  SELECT
    win,
    day_id,
    bucket,
    -- Just to be safe and not divide by 0 (although it should not be possible on our data)
    CASE WHEN mean = 0 THEN NULL ELSE sd / mean END AS vc
  FROM stats
),
per_win_day AS (
  -- Per Bucket and day get avg vc
  SELECT
    v.win,
    v.day_id,
    AVG(v.vc)                                   AS avg_vc,
    COUNT(*) FILTER (WHERE v.vc IS NOT NULL)    AS bucket_count,
    COUNT(*) FILTER (WHERE v.vc >= th.r)        AS high_vc_count,
    (SELECT r FROM threshold)                    AS r_used
  FROM vc v
  CROSS JOIN threshold th
  GROUP BY v.win, v.day_id
),
per_win_summary AS (
  -- Summary across days per interval (final aggregation level)
  SELECT
    win                                             AS interval_T,
    AVG(avg_vc)                                     AS avg_vc_over_days,
    STDDEV_SAMP(avg_vc)                             AS sd_vc_over_days,
    SUM(bucket_count)                               AS total_bucket_count,
    SUM(high_vc_count)                              AS total_high_vc_count,
    (SUM(high_vc_count)::numeric / NULLIF(SUM(bucket_count), 0))
                                                    AS overall_ratio_cv_ge_r,         
    MIN(r_used)                                     AS r_used                          
  FROM per_win_day
  GROUP BY win
)
-- Final output per interval T (summarized over days)
SELECT
  interval_T,
  avg_vc_over_days,
  sd_vc_over_days,
  total_bucket_count,
  total_high_vc_count,
  overall_ratio_cv_ge_r,
  r_used
FROM per_win_summary
ORDER BY avg_vc_over_days ASC, overall_ratio_cv_ge_r ASC;

--- Humidity CV
\echo HumidityCV
WITH
params(win) AS (
  -- Bucket intervals
  SELECT unnest(ARRAY[
    interval '1 min',
    interval '2 min',
    interval '4 min',
    interval '5 min',
    interval '15 min',
    interval '30 min',
    interval '1 hour',
    interval '2 hours'
  ])
),
-- 1) Threshhold r of cv
threshold AS (
  SELECT 0.05::double precision AS r
),
-- Temperature for each bucket of day => Cross Joined to combine all params
base AS (
  SELECT
    p.win,
    date_trunc('day', t.time)                AS day_id,
    time_bucket(p.win, t.time)               AS bucket,
    t.humidity
  FROM bronze.humidity t
  CROSS JOIN params p
),
-- Mean and Sample std for each bucket
stats AS (
  SELECT
    win,
    day_id,
    bucket,
    AVG(humidity)              AS mean,
    STDDEV_SAMP(humidity)      AS sd
  FROM base
  GROUP BY win, day_id, bucket
),
-- Variational Coefficient for each bcket
vc AS (
  SELECT
    win,
    day_id,
    bucket,
    -- Just to be safe and not divide by 0 (although it should not be possible on our data)
    CASE WHEN mean = 0 THEN NULL ELSE sd / mean END AS vc
  FROM stats
),
per_win_day AS (
  -- Per Bucket and day get avg vc
  SELECT
    v.win,
    v.day_id,
    AVG(v.vc)                                   AS avg_vc,
    COUNT(*) FILTER (WHERE v.vc IS NOT NULL)    AS bucket_count,
    COUNT(*) FILTER (WHERE v.vc >= th.r)        AS high_vc_count,
    (SELECT r FROM threshold)                    AS r_used
  FROM vc v
  CROSS JOIN threshold th
  GROUP BY v.win, v.day_id
),
per_win_summary AS (
  -- Summary across days per interval (final aggregation level)
  SELECT
    win                                             AS interval_T,
    AVG(avg_vc)                                     AS avg_vc_over_days,              
    STDDEV_SAMP(avg_vc)                             AS sd_vc_over_days,               
    SUM(bucket_count)                               AS total_bucket_count,
    SUM(high_vc_count)                              AS total_high_vc_count,
    (SUM(high_vc_count)::numeric / NULLIF(SUM(bucket_count), 0))
                                                    AS overall_ratio_cv_ge_r,
    MIN(r_used)                                     AS r_used
  FROM per_win_day
  GROUP BY win
)
-- Final output per interval T (summarized over days)
SELECT
  interval_T,
  avg_vc_over_days,
  sd_vc_over_days,
  total_bucket_count,
  total_high_vc_count,
  overall_ratio_cv_ge_r,
  r_used
FROM per_win_summary
ORDER BY avg_vc_over_days ASC, overall_ratio_cv_ge_r ASC;

--- Noise VC
\echo NoiseCV
WITH
params(win) AS (
  -- Bucket intervals
  SELECT unnest(ARRAY[
    interval '1 min',
    interval '2 min',
    interval '4 min',
    interval '5 min',
    interval '15 min',
    interval '30 min',
    interval '1 hour',
    interval '2 hours'
  ])
),
-- 1) Threshhold r of cv
threshold AS (
  SELECT 0.05::double precision AS r
),
-- noise for each bucket of day => Cross Joined to combine all params
base AS (
  SELECT
    p.win,
    date_trunc('day', t.time)                AS day_id,
    time_bucket(p.win, t.time)               AS bucket,
    t.noise
  FROM bronze.noise t
  CROSS JOIN params p
),
-- Mean and Sample std for each bucket
stats AS (
  SELECT
    win,
    day_id,
    bucket,
    AVG(noise)              AS mean,
    STDDEV_SAMP(noise)      AS sd
  FROM base
  GROUP BY win, day_id, bucket
),
-- Variational Coefficient for each bcket
vc AS (
  SELECT
    win,
    day_id,
    bucket,
    -- Just to be safe and not divide by 0 (although it should not be possible on our data)
    CASE WHEN mean = 0 THEN NULL ELSE sd / mean END AS vc
  FROM stats
),
per_win_day AS (
  -- Per Bucket and day get avg vc
  SELECT
    v.win,
    v.day_id,
    AVG(v.vc)                                   AS avg_vc,
    COUNT(*) FILTER (WHERE v.vc IS NOT NULL)    AS bucket_count,
    COUNT(*) FILTER (WHERE v.vc >= th.r)        AS high_vc_count,
    (SELECT r FROM threshold)                    AS r_used
  FROM vc v
  CROSS JOIN threshold th
  GROUP BY v.win, v.day_id
),
per_win_summary AS (
  -- Summary across days per interval (final aggregation level)
  SELECT
    win                                             AS interval_T,
    AVG(avg_vc)                                     AS avg_vc_over_days,
    STDDEV_SAMP(avg_vc)                             AS sd_vc_over_days,
    SUM(bucket_count)                               AS total_bucket_count,
    SUM(high_vc_count)                              AS total_high_vc_count,
    (SUM(high_vc_count)::numeric / NULLIF(SUM(bucket_count), 0))
                                                    AS overall_ratio_cv_ge_r,
    MIN(r_used)                                     AS r_used
  FROM per_win_day
  GROUP BY win
)
-- Final output per interval T (summarized over days)
SELECT
  interval_T,
  avg_vc_over_days,
  sd_vc_over_days,
  total_bucket_count,
  total_high_vc_count,
  overall_ratio_cv_ge_r,
  r_used
FROM per_win_summary
ORDER BY avg_vc_over_days ASC, overall_ratio_cv_ge_r ASC;

--- Voc VC
\echo VocCV
WITH
params(win) AS (
  -- Bucket intervals
  SELECT unnest(ARRAY[
    interval '1 min',
    interval '2 min',
    interval '4 min',
    interval '5 min',
    interval '15 min',
    interval '30 min',
    interval '1 hour',
    interval '2 hours'
  ])
),
-- 1) Threshhold r of cv
threshold AS (
  SELECT 0.05::double precision AS r
),
-- Temperature for each bucket of day => Cross Joined to combine all params
base AS (
  SELECT
    p.win,
    date_trunc('day', t.time)                AS day_id,
    time_bucket(p.win, t.time)               AS bucket,
    t.voc
  FROM bronze.voc t
  CROSS JOIN params p
),
-- Mean and Sample std for each bucket
stats AS (
  SELECT
    win,
    day_id,
    bucket,
    AVG(voc)              AS mean,
    STDDEV_SAMP(voc)      AS sd
  FROM base
  GROUP BY win, day_id, bucket
),
-- Variational Coefficient for each bcket
vc AS (
  SELECT
    win,
    day_id,
    bucket,
    -- Just to be safe and not divide by 0 (although it should not be possible on our data)
    CASE WHEN mean = 0 THEN NULL ELSE sd / mean END AS vc
  FROM stats
),
per_win_day AS (
  -- Per Bucket and day get avg vc
  SELECT
    v.win,
    v.day_id,
    AVG(v.vc)                                   AS avg_vc,
    COUNT(*) FILTER (WHERE v.vc IS NOT NULL)    AS bucket_count,
    COUNT(*) FILTER (WHERE v.vc >= th.r)        AS high_vc_count,
    (SELECT r FROM threshold)                    AS r_used
  FROM vc v
  CROSS JOIN threshold th
  GROUP BY v.win, v.day_id
),
per_win_summary AS (
  -- Summary across days per interval (final aggregation level)
  SELECT
    win                                             AS interval_T,
    AVG(avg_vc)                                     AS avg_vc_over_days,
    STDDEV_SAMP(avg_vc)                             AS sd_vc_over_days,
    SUM(bucket_count)                               AS total_bucket_count,
    SUM(high_vc_count)                              AS total_high_vc_count,
    (SUM(high_vc_count)::numeric / NULLIF(SUM(bucket_count), 0))
                                                    AS overall_ratio_cv_ge_r,
    MIN(r_used)                                     AS r_used
  FROM per_win_day
  GROUP BY win
)
-- Final output per interval T (summarized over days)
SELECT
  interval_T,
  avg_vc_over_days,
  sd_vc_over_days,
  total_bucket_count,
  total_high_vc_count,
  overall_ratio_cv_ge_r,
  r_used
FROM per_win_summary
ORDER BY avg_vc_over_days ASC, overall_ratio_cv_ge_r ASC;