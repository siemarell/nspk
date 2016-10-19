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