
DROP TABLE IF EXISTS calendar CASCADE;
DROP TABLE IF EXISTS d_administrator CASCADE;
DROP TABLE IF EXISTS d_client CASCADE;
DROP TABLE IF EXISTS d_division_owner CASCADE;
DROP TABLE IF EXISTS d_guilty CASCADE;
DROP TABLE IF EXISTS d_host CASCADE;
DROP TABLE IF EXISTS d_os CASCADE;
DROP TABLE IF EXISTS d_period_type CASCADE;
DROP TABLE IF EXISTS d_platform_type CASCADE;
DROP TABLE IF EXISTS d_provider CASCADE;
DROP TABLE IF EXISTS d_purpose CASCADE;
DROP TABLE IF EXISTS d_rfc CASCADE;
DROP TABLE IF EXISTS d_subsystem CASCADE;
DROP TABLE IF EXISTS d_time CASCADE;
DROP TABLE IF EXISTS d_trigger CASCADE;
DROP TABLE IF EXISTS f_channel_connect CASCADE;
DROP TABLE IF EXISTS f_serv_incident CASCADE;


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
  id integer NOT NULL,
  time_text character varying,
  hour integer,
  quarterhour character varying,
  minute integer,
  daytimename character varying,
  daynight character varying,
  CONSTRAINT d_time_pkey PRIMARY KEY (id)
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
  ' � ' ||
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


-- Table: d_client

-- DROP TABLE d_client;

CREATE TABLE d_client
(
  id serial NOT NULL,
  full_name text,
  org_name text,
  address text,
  router_ip text,
  provider text,
  external_id INTEGER,
  CONSTRAINT pk_d_client PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_client
  OWNER TO postgres;
-- Table: d_guilty

-- DROP TABLE d_guilty;

CREATE TABLE d_guilty
(
  id serial NOT NULL,
  name text,
  CONSTRAINT pk_guilty PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_guilty
  OWNER TO postgres;
-- Table: d_host

-- DROP TABLE d_host;

CREATE TABLE d_host
(
  id serial NOT NULL,
  name character varying,
  purpose text,
  department_owner text,
  subsystem text,
  platform_type text,
  os text,
  administrator text,
  external_id integer,
  CONSTRAINT d_host_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_host
  OWNER TO postgres;
-- Table: d_provider

-- DROP TABLE d_provider;

CREATE TABLE d_provider
(
  id serial NOT NULL,
  name text,
  CONSTRAINT pk_provider PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_provider
  OWNER TO postgres;
-- Table: d_rfc

-- DROP TABLE d_rfc;

CREATE TABLE d_rfc
(
  id serial NOT NULL,
  name text,
  CONSTRAINT pk_rfc PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_rfc
  OWNER TO postgres;
-- Table: d_trigger

-- DROP TABLE d_trigger;

CREATE TABLE d_trigger
(
  id serial NOT NULL,
  source_name character varying,
  external_id integer,
  CONSTRAINT d_trigger_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE d_trigger
  OWNER TO postgres;
-- Table: f_channel_connect

-- DROP TABLE f_channel_connect;

CREATE TABLE f_channel_connect
(
  id serial NOT NULL,
  event_start_id INTEGER,
  id_date_start date,
  id_date_end date,
  id_time_start integer,
  id_time_end integer,
  id_client integer,
  id_provider integer,
  id_rfc integer,
  id_guilty integer,
  fact_timedelta integer,
  fact_sla integer,

  CONSTRAINT pk_fact_id PRIMARY KEY (id),
  CONSTRAINT fk_id_client_d_client FOREIGN KEY (id_client)
      REFERENCES d_client (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_id_date_end_calendar FOREIGN KEY (id_date_end)
      REFERENCES calendar (date) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_id_date_start_calendar FOREIGN KEY (id_date_start)
      REFERENCES calendar (date) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
 -- CONSTRAINT fk_id_guilty_d_guilty FOREIGN KEY (id_guilty)
 --     REFERENCES d_guilty (id) MATCH SIMPLE
 --     ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_id_provider_d_provider FOREIGN KEY (id_provider)
      REFERENCES d_provider (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
 -- CONSTRAINT fk_id_rfc_d_rfc FOREIGN KEY (id_rfc)
 --     REFERENCES d_rfc (id) MATCH SIMPLE
 --     ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_time_end_time FOREIGN KEY (id_time_end)
      REFERENCES d_time (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_time_start_time FOREIGN KEY (id_time_start)
      REFERENCES d_time (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE f_channel_connect
  OWNER TO postgres;

-- Index: fki_date_start_calendar

-- DROP INDEX fki_date_start_calendar;

CREATE INDEX fki_date_start_calendar
  ON f_channel_connect
  USING btree
  (id_date_start);

-- Index: fki_id_client_d_client

-- DROP INDEX fki_id_client_d_client;

CREATE INDEX fki_id_client_d_client
  ON f_channel_connect
  USING btree
  (id_client);

-- Index: fki_id_date_end_calendar

-- DROP INDEX fki_id_date_end_calendar;

CREATE INDEX fki_id_date_end_calendar
  ON f_channel_connect
  USING btree
  (id_date_end);

-- Index: fki_id_guilty_d_guilty

-- DROP INDEX fki_id_guilty_d_guilty;

CREATE INDEX fki_id_guilty_d_guilty
  ON f_channel_connect
  USING btree
  (id_guilty);

-- Index: fki_id_provider_d_provider

-- DROP INDEX fki_id_provider_d_provider;

CREATE INDEX fki_id_provider_d_provider
  ON f_channel_connect
  USING btree
  (id_provider);

-- Index: fki_id_rfc_d_rfc

-- DROP INDEX fki_id_rfc_d_rfc;

CREATE INDEX fki_id_rfc_d_rfc
  ON f_channel_connect
  USING btree
  (id_rfc);

-- Index: fki_time_end_time

-- DROP INDEX fki_time_end_time;

CREATE INDEX fki_time_end_time
  ON f_channel_connect
  USING btree
  (id_time_end);

-- Index: fki_time_start_time

-- DROP INDEX fki_time_start_time;

CREATE INDEX fki_time_start_time
  ON f_channel_connect
  USING btree
  (id_time_start);

-- Table: f_serv_incident

-- DROP TABLE f_serv_incident;

CREATE TABLE f_serv_incident
(
  id serial NOT NULL,
  event_start_id INTEGER,
  id_host integer,
  id_date_start date,
  id_date_end date,
  id_time_start integer,
  id_time_end integer,
  id_trigger integer,
  fact_timedelta integer,
  description text,
  CONSTRAINT f_serv_incident_pkey PRIMARY KEY (id),
  CONSTRAINT date_end FOREIGN KEY (id_date_end)
      REFERENCES calendar (date) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT date_start FOREIGN KEY (id_date_start)
      REFERENCES calendar (date) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_id_time_enf_d_time FOREIGN KEY (id_time_end)
      REFERENCES d_time (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_id_time_start_d_time FOREIGN KEY (id_time_start)
      REFERENCES d_time (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT host_serv FOREIGN KEY (id_host)
      REFERENCES d_host (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT trigger_serv FOREIGN KEY (id_trigger)
      REFERENCES d_trigger (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE f_serv_incident
  OWNER TO postgres;

-- Index: fki_date_end_serv

-- DROP INDEX fki_date_end_serv;

CREATE INDEX fki_date_end_serv
  ON f_serv_incident
  USING btree
  (id_date_end);

-- Index: fki_date_start_serv

-- DROP INDEX fki_date_start_serv;

CREATE INDEX fki_date_start_serv
  ON f_serv_incident
  USING btree
  (id_date_start);

-- Index: fki_host_serv

-- DROP INDEX fki_host_serv;

CREATE INDEX fki_host_serv
  ON f_serv_incident
  USING btree
  (id_host);

-- Index: fki_id_time_enf_d_time

-- DROP INDEX fki_id_time_enf_d_time;

CREATE INDEX fki_id_time_enf_d_time
  ON f_serv_incident
  USING btree
  (id_time_end);

-- Index: fki_id_time_start_d_time

-- DROP INDEX fki_id_time_start_d_time;

CREATE INDEX fki_id_time_start_d_time
  ON f_serv_incident
  USING btree
  (id_time_start);

-- Index: fki_trigger_serv

-- DROP INDEX fki_trigger_serv;

CREATE INDEX fki_trigger_serv
  ON f_serv_incident
  USING btree
  (id_trigger);




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