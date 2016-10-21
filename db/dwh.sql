-- NSPK DWH star-schema

-- Table: calendar

DROP TABLE IF EXISTS calendar CASCADE;

CREATE TABLE calendar
(
  date date NOT NULL,
  year integer,
  halfyear integer,
  quarter integer,
  month_number integer,
  month text,
  day integer,
  week_number integer,
  week_day text,
  day_number integer,
  CONSTRAINT calendar_pkey PRIMARY KEY (date)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE calendar
  OWNER TO postgres;

SET lc_time TO 'ru_RU.UTF-8';

INSERT INTO calendar
SELECT
	datum AS DATE,
	EXTRACT(YEAR FROM datum) AS YEAR,
	CASE WHEN to_char(datum, 'Q') in ('1','2') THEN 1 ELSE 2 END as halfyear,
	CAST(to_char(datum, 'Q') as INTEGER) AS Quartal,
	-- Localized month name
	EXTRACT(MONTH FROM datum) AS month_number,
	to_char(datum, 'TMMonth') AS month,
	EXTRACT(DAY FROM datum) AS DAY,
	-- ISO calendar week
	EXTRACT(week FROM datum) AS week_number,
	-- Localized weekday
	to_char(datum, 'TMDay') AS week_day,
	EXTRACT(doy FROM datum) AS day_number
FROM (
	SELECT '2006-01-01'::DATE + SEQUENCE.DAY AS datum
	FROM generate_series(0,6000) AS SEQUENCE(DAY)
	GROUP BY SEQUENCE.DAY
     ) DQ
ORDER BY 1;


-- Table: d_time
-- Time dimension

DROP TABLE IF EXISTS d_time CASCADE;

CREATE TABLE d_time
(
  id_time time without time zone NOT NULL,
  time_text character varying,
  hour integer,
  quarterhour character varying,
  minute integer,
  daytimename character varying,
  daynight character varying,
  CONSTRAINT d_time_pkey PRIMARY KEY (id_time)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_time
  OWNER TO postgres;

INSERT INTO d_time
SELECT  (EXTRACT(epoch FROM MINUTE)/60 :: int) as id,
  to_char(MINUTE, 'hh24:mi') AS TimeOfDay,
  -- Hour of the day (0 - 23)
  EXTRACT(HOUR FROM MINUTE) AS HOUR,
  -- Extract and format quarter hours
  to_char(MINUTE - (EXTRACT(MINUTE FROM MINUTE)::INTEGER % 15 || 'minutes')::INTERVAL, 'hh24:mi') ||
  ' – ' ||
  to_char(MINUTE - (EXTRACT(MINUTE FROM MINUTE)::INTEGER % 15 || 'minutes')::INTERVAL + '14 minutes'::INTERVAL, 'hh24:mi')
    AS QuarterHour,
  -- Minute of the day (0 - 1439)
  EXTRACT(HOUR FROM MINUTE)*60 + EXTRACT(MINUTE FROM MINUTE) AS MINUTE,
  -- Names of day periods
  CASE WHEN to_char(MINUTE, 'hh24:mi') BETWEEN '06:00' AND '08:29'
    THEN 'Morning'
       WHEN to_char(MINUTE, 'hh24:mi') BETWEEN '08:30' AND '11:59'
    THEN 'AM'
       WHEN to_char(MINUTE, 'hh24:mi') BETWEEN '12:00' AND '17:59'
    THEN 'PM'
       WHEN to_char(MINUTE, 'hh24:mi') BETWEEN '18:00' AND '22:29'
    THEN 'Evening'
       ELSE 'Night'
  END AS DaytimeName,
  -- Indicator of day or night
  CASE WHEN to_char(MINUTE, 'hh24:mi') BETWEEN '07:00' AND '19:59' THEN 'Day'
       ELSE 'Night'
  END AS DayNight
FROM (SELECT '0:00'::TIME + (SEQUENCE.MINUTE || ' minutes')::INTERVAL AS MINUTE
  FROM generate_series(0,1439) AS SEQUENCE(MINUTE)
  GROUP BY SEQUENCE.MINUTE
     ) DQ
ORDER BY 1;




------PERMISSIONS-------

GRANT SELECT ON ALL TABLES IN SCHEMA public
  TO data_read;

GRANT SELECT ,INSERT , UPDATE , DELETE, TRUNCATE, REFERENCES, TRIGGER
  ON ALL TABLES IN SCHEMA public
  TO data_etl;

GRANT ALL
  ON ALL TABLES IN SCHEMA public
  TO data_root;

GRANT SELECT, UPDATE, USAGE ON ALL SEQUENCES IN SCHEMA public
  TO data_root, data_etl;

GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public
  TO data_read;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public to data_read, data_root, data_etl;