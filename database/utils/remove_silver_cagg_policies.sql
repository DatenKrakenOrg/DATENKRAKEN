--- Created via GPT-5 on 18.08.25
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT format('%I.%I', view_schema, view_name) AS fqname
    FROM timescaledb_information.continuous_aggregates
    WHERE view_schema = 'silver'
  LOOP
    BEGIN
      EXECUTE format('SELECT remove_continuous_aggregate_policy(%L::regclass);', r.fqname);
    EXCEPTION WHEN OTHERS THEN
      NULL;
    END;

    EXECUTE format('DROP MATERIALIZED VIEW IF EXISTS %s CASCADE;', r.fqname);
  END LOOP;
END$$;

--- Check deletion

SELECT view_schema, view_name
FROM timescaledb_information.continuous_aggregates
WHERE view_schema = 'silver';

\dv silver.*

--- Check jobs

SELECT job_id, proc_name, config
FROM timescaledb_information.jobs
WHERE proc_name='policy_refresh_continuous_aggregate';
