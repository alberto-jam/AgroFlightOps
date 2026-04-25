-- Ajuste o database antes de executar: USE agrotech_dev_agras;

CREATE EXTERNAL TABLE IF NOT EXISTS agras_telemetry_jsonl (
  flight_id string,
  `timestamp` string,
  drone_model string,
  drone_serial string,
  pilot_id string,
  latitude double,
  longitude double,
  altitude_m double,
  height_above_ground_m double,
  speed_mps double,
  vertical_speed_mps double,
  heading_deg double,
  pitch_deg double,
  roll_deg double,
  battery_percent int,
  battery_temp_c double,
  gps_satellites int,
  signal_strength_percent int,
  spray_on boolean,
  flow_l_min double,
  tank_level_percent double,
  coverage_width_m double,
  cumulative_distance_m double,
  anomaly_count int,
  anomaly_reasons string,
  mission_score int
)
PARTITIONED BY (dt string, flight_id_part string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://agroflightops-dev-telemetria-processed/telemetry/'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.dt.type'='date',
  'projection.dt.range'='2025-01-01,NOW',
  'projection.dt.format'='yyyy-MM-dd',
  'projection.flight_id_part.type'='injected',
  'storage.location.template'='s3://agroflightops-dev-telemetria-processed/telemetry/dt=${dt}/flight_id=${flight_id_part}/'
)

