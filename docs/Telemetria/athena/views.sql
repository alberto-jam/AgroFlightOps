CREATE OR REPLACE VIEW vw_agras_flight_summary AS
SELECT
  flight_id,
  dt,
  min(timestamp) AS start_time,
  max(timestamp) AS end_time,
  count(*) AS telemetry_points,
  max(cumulative_distance_m) AS distance_m,
  round(avg(speed_mps), 2) AS avg_speed_mps,
  round(avg(CASE WHEN spray_on THEN flow_l_min ELSE NULL END), 2) AS avg_flow_l_min_when_spraying,
  min(battery_percent) AS min_battery_percent,
  max(battery_percent) AS start_battery_percent,
  round(avg(mission_score), 2) AS avg_mission_score,
  sum(CASE WHEN anomaly_count > 0 THEN 1 ELSE 0 END) AS anomaly_points
FROM agras_telemetry_jsonl
GROUP BY flight_id, dt;

CREATE OR REPLACE VIEW vw_agras_anomaly_points AS
SELECT
  flight_id,
  dt,
  timestamp,
  latitude,
  longitude,
  speed_mps,
  battery_percent,
  height_above_ground_m,
  gps_satellites,
  signal_strength_percent,
  anomaly_reasons,
  mission_score
FROM agras_telemetry_jsonl
WHERE anomaly_count > 0;

CREATE OR REPLACE VIEW vw_agras_spray_efficiency AS
SELECT
  flight_id,
  dt,
  count(*) AS total_points,
  sum(CASE WHEN spray_on THEN 1 ELSE 0 END) AS spray_points,
  round(100.0 * sum(CASE WHEN spray_on THEN 1 ELSE 0 END) / count(*), 2) AS spray_time_percent,
  round(avg(CASE WHEN spray_on THEN speed_mps END), 2) AS avg_spray_speed_mps,
  round(avg(CASE WHEN spray_on THEN height_above_ground_m END), 2) AS avg_spray_height_m,
  round(avg(CASE WHEN spray_on THEN mission_score END), 2) AS avg_spray_score
FROM agras_telemetry_jsonl
GROUP BY flight_id, dt;
