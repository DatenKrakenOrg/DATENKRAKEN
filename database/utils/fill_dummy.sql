-- Generated via gemini 2.5 pro and edited to match specifications

-- Noise script for around 5m entries
INSERT INTO bronze.noise (time, arduino_id, noise)
SELECT
    base_ts + (offset_sec || ' seconds')::interval,
    CASE
        WHEN n <= 10 THEN '401'
        WHEN n > 10 AND n <= 20 THEN '402'
        ELSE '403'
    END,
    floor(random() * 1029)::smallint
FROM
    generate_series(
        NOW() - '60 days'::interval,
        NOW(),
        '1 minute'::interval
    ) AS timestamps(base_ts)
CROSS JOIN
    generate_series(0, 1) AS time_offsets(offset_sec)
CROSS JOIN
    generate_series(1, 30) AS data_points(n);

-- Temperature skript for 172k

INSERT INTO bronze.temperature (time, arduino_id, temperature)
SELECT
    ts,
    CASE
        WHEN (row_num % 3) = 1 THEN '401'
        WHEN (row_num % 3) = 2 THEN '402'
        ELSE '403' 
    END,
    random() * 25.0 + 5.0
FROM (
    SELECT
        ts,
        row_number() OVER (ORDER BY ts) as row_num
    FROM
        generate_series(
            NOW() - '60 days'::interval,
            NOW(),
            '30 seconds'::interval
        ) AS timestamps(ts)
) AS generated_series;
