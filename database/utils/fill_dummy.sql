-- Noise script script for 10 days
INSERT INTO bronze.noise (time, arduino_id, noise)
SELECT
    date_trunc('second', base_ts + make_interval(secs => offset_sec)),
    CASE
        WHEN n <= 10 THEN 401
        WHEN n > 10 AND n <= 20 THEN 402
        ELSE 403
    END,
    floor(random() * 1029)::smallint
FROM
    generate_series(
        NOW() - interval '10 days',
        NOW(),
        interval '1 minute'
    ) AS timestamps(base_ts)
CROSS JOIN
    generate_series(0, 1) AS time_offsets(offset_sec)
CROSS JOIN
    generate_series(1, 30) AS data_points(n);


-- Temperature script for 10 days
INSERT INTO bronze.temperature (time, arduino_id, temperature)
SELECT
    date_trunc('second', ts),
    CASE
        WHEN (row_num % 3) = 1 THEN 401
        WHEN (row_num % 3) = 2 THEN 402
        ELSE 403
    END,
    random() * 25.0 + 5.0
FROM (
    SELECT
        ts,
        row_number() OVER (ORDER BY ts) as row_num
    FROM
        generate_series(
            NOW() - interval '10 days',
            NOW(),
            interval '30 seconds'
        ) AS timestamps(ts)
) AS generated_series;


-- Humidity script for 10 days
INSERT INTO bronze.humidity (time, arduino_id, humidity)
SELECT
    date_trunc('second', ts),
    CASE
        WHEN (row_num % 3) = 1 THEN 401
        WHEN (row_num % 3) = 2 THEN 402
        ELSE 403
    END,
    random() * 25.0 + 5.0
FROM (
    SELECT
        ts,
        row_number() OVER (ORDER BY ts) as row_num
    FROM
        generate_series(
            NOW() - interval '10 days',
            NOW(),
            interval '30 seconds'
        ) AS timestamps(ts)
) AS generated_series;


-- VOC script for 10 days
INSERT INTO bronze.voc (time, arduino_id, voc)
SELECT
    date_trunc('second', ts),
    CASE
        WHEN (row_num % 3) = 1 THEN 401
        WHEN (row_num % 3) = 2 THEN 402
        ELSE 403
    END,
    random() * 25.0 + 5.0
FROM (
    SELECT
        ts,
        row_number() OVER (ORDER BY ts) as row_num
    FROM
        generate_series(
            NOW() - interval '10 days',
            NOW(),
            interval '30 seconds'
        ) AS timestamps(ts)
) AS generated_series;
