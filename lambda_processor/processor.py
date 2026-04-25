"""
Lambda Processor de Telemetria — AgroFlightOps.

Processa arquivos brutos de telemetria de drones DJI Agras,
normaliza registros, calcula métricas (distância Haversine, score, anomalias),
gera GeoJSON e grava dados particionados no S3 Processed Bucket.

Acionado por EventBridge (S3 Object Created) ou diretamente via S3 Records.
"""

import json
import os
import math
import boto3
from datetime import datetime, timezone
from urllib.parse import unquote_plus

s3 = boto3.client("s3")
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET")


def parse_ts(value: str) -> datetime:
    """Parse ISO 8601 timestamp, tratando sufixo 'Z' como UTC."""
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def haversine_m(lat1, lon1, lat2, lon2):
    """Distância em metros entre dois pontos (lat/lon) usando fórmula de Haversine."""
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def anomaly_reasons(row):
    """Detecta anomalias em um ponto de telemetria com base nos thresholds definidos."""
    reasons = []
    if row.get("speed_mps", 0) > 8:
        reasons.append("VELOCIDADE_EXCESSIVA")
    if row.get("battery_percent", 100) < 20:
        reasons.append("BATERIA_BAIXA")
    if row.get("height_above_ground_m", 99) < 2:
        reasons.append("ALTURA_BAIXA")
    if row.get("height_above_ground_m", 0) > 5:
        reasons.append("ALTURA_ALTA")
    if row.get("gps_satellites", 99) < 10:
        reasons.append("GPS_FRACO")
    if row.get("signal_strength_percent", 100) < 55:
        reasons.append("SINAL_FRACO")
    if row.get("spray_on") and row.get("flow_l_min", 0) <= 0.1:
        reasons.append("PULVERIZACAO_SEM_FLUXO")
    return reasons


def mission_score(row, reasons):
    """Calcula score operacional 0–100 com penalidades por anomalias e bônus por operação ideal."""
    score = 100
    penalties = {
        "VELOCIDADE_EXCESSIVA": 8,
        "BATERIA_BAIXA": 15,
        "ALTURA_BAIXA": 8,
        "ALTURA_ALTA": 6,
        "GPS_FRACO": 8,
        "SINAL_FRACO": 8,
        "PULVERIZACAO_SEM_FLUXO": 20,
    }
    for r in reasons:
        score -= penalties.get(r, 0)
    # Bônus por operação dentro dos parâmetros ideais durante pulverização
    if (
        row.get("spray_on")
        and 3.0 <= row.get("height_above_ground_m", 0) <= 4.0
        and 4.0 <= row.get("speed_mps", 0) <= 6.5
    ):
        score += 3
    return max(0, min(100, score))


def normalize_records(records):
    """Normaliza e enriquece registros brutos de telemetria.

    Calcula distância acumulada (Haversine), detecta anomalias e atribui score.
    """
    output = []
    prev = None
    cumulative_distance = 0.0
    for raw in records:
        ts = parse_ts(raw["timestamp"])
        lat = float(raw["latitude"])
        lon = float(raw["longitude"])
        if prev:
            cumulative_distance += haversine_m(
                prev["latitude"], prev["longitude"], lat, lon
            )
        base = {
            "flight_id": raw["flight_id"],
            "timestamp": ts.isoformat(),
            "dt": ts.date().isoformat(),
            "drone_model": raw.get("drone_model", "DJI Agras"),
            "drone_serial": raw.get("drone_serial", "UNKNOWN"),
            "pilot_id": raw.get("pilot_id", "UNKNOWN"),
            "latitude": lat,
            "longitude": lon,
            "altitude_m": float(raw.get("altitude_m", 0)),
            "height_above_ground_m": float(
                raw.get("height_above_ground_m", raw.get("altitude_m", 0))
            ),
            "speed_mps": float(raw.get("speed_mps", 0)),
            "vertical_speed_mps": float(raw.get("vertical_speed_mps", 0)),
            "heading_deg": float(raw.get("heading_deg", 0)),
            "pitch_deg": float(raw.get("pitch_deg", 0)),
            "roll_deg": float(raw.get("roll_deg", 0)),
            "battery_percent": int(raw.get("battery_percent", raw.get("battery", 0))),
            "battery_temp_c": float(raw.get("battery_temp_c", 0)),
            "gps_satellites": int(raw.get("gps_satellites", 0)),
            "signal_strength_percent": int(raw.get("signal_strength_percent", 0)),
            "spray_on": bool(raw.get("spray_on", False)),
            "flow_l_min": float(raw.get("flow_l_min", 0)),
            "tank_level_percent": float(raw.get("tank_level_percent", 0)),
            "coverage_width_m": float(raw.get("coverage_width_m", 7.0)),
            "cumulative_distance_m": round(cumulative_distance, 2),
        }
        reasons = anomaly_reasons(base)
        base["anomaly_count"] = len(reasons)
        base["anomaly_reasons"] = "|".join(reasons)
        base["mission_score"] = mission_score(base, reasons)
        output.append(base)
        prev = base
    return output


def build_geojson(records):
    """Gera FeatureCollection GeoJSON com LineString do trajeto e pontos amostrados."""
    coords = [[r["longitude"], r["latitude"]] for r in records]
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "flight_id": records[0]["flight_id"],
                "points": len(records),
                "avg_score": round(
                    sum(r["mission_score"] for r in records) / len(records), 2
                ),
                "distance_m": records[-1]["cumulative_distance_m"],
            },
        }
    ]
    # Amostra até ~300 pontos para não sobrecarregar o GeoJSON
    for r in records[:: max(1, len(records) // 300)]:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r["longitude"], r["latitude"]],
                },
                "properties": {
                    "timestamp": r["timestamp"],
                    "speed_mps": r["speed_mps"],
                    "battery_percent": r["battery_percent"],
                    "spray_on": r["spray_on"],
                    "mission_score": r["mission_score"],
                    "anomaly_reasons": r["anomaly_reasons"],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def lambda_handler(event, context):
    """Handler principal — suporta eventos EventBridge e formato S3 Records."""
    processed_bucket = PROCESSED_BUCKET
    if not processed_bucket:
        raise RuntimeError("PROCESSED_BUCKET environment variable is required")

    results = []
    event_records = event.get("Records") or []

    # Suporte a eventos EventBridge (S3 Object Created via EventBridge)
    if not event_records and event.get("detail", {}).get("bucket"):
        event_records = [
            {
                "s3": {
                    "bucket": {"name": event["detail"]["bucket"]["name"]},
                    "object": {"key": event["detail"]["object"]["key"]},
                }
            }
        ]

    for rec in event_records:
        bucket = rec["s3"]["bucket"]["name"]
        key = unquote_plus(rec["s3"]["object"]["key"])

        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read().decode("utf-8")
        raw_records = json.loads(body)

        # Suporta tanto lista direta quanto objeto com campo "records"
        if isinstance(raw_records, dict) and "records" in raw_records:
            raw_records = raw_records["records"]

        normalized = normalize_records(raw_records)
        if not normalized:
            continue

        # Extract missao_id from S3 key: incoming/{missao_id}_{timestamp}.json
        missao_id = None
        filename = key.split("/")[-1]  # e.g. "4_20260425T120000Z.json"
        if "_" in filename:
            missao_id = filename.split("_")[0]

        # Override flight_id with missao_id if available
        if missao_id:
            for rec_norm in normalized:
                rec_norm["flight_id"] = missao_id

        dt = normalized[0]["dt"]
        flight_id = normalized[0]["flight_id"]

        # Grava JSONL particionado
        out_prefix = f"telemetry/dt={dt}/flight_id={flight_id}"
        jsonl = (
            "\n".join(json.dumps(r, ensure_ascii=False) for r in normalized) + "\n"
        )
        s3.put_object(
            Bucket=processed_bucket,
            Key=f"{out_prefix}/part-00000.jsonl",
            Body=jsonl.encode("utf-8"),
        )

        # Grava GeoJSON
        geojson = build_geojson(normalized)
        s3.put_object(
            Bucket=processed_bucket,
            Key=f"geojson/dt={dt}/flight_id={flight_id}/track.geojson",
            Body=json.dumps(geojson, ensure_ascii=False).encode("utf-8"),
            ContentType="application/geo+json",
        )

        # Grava sumário
        summary = {
            "flight_id": flight_id,
            "dt": dt,
            "points": len(normalized),
            "distance_m": normalized[-1]["cumulative_distance_m"],
            "avg_score": round(
                sum(r["mission_score"] for r in normalized) / len(normalized), 2
            ),
            "min_battery": min(r["battery_percent"] for r in normalized),
            "anomaly_points": sum(
                1 for r in normalized if r["anomaly_count"] > 0
            ),
        }
        s3.put_object(
            Bucket=processed_bucket,
            Key=f"summary/dt={dt}/flight_id={flight_id}/summary.json",
            Body=json.dumps(summary).encode("utf-8"),
        )

        results.append(summary)

    return {"ok": True, "processed": results}
