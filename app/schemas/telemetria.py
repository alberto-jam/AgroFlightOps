"""Pydantic schemas for Telemetria and Insights responses."""

from pydantic import BaseModel


class TelemetriaUploadResponse(BaseModel):
    """Resposta do upload de telemetria."""

    missao_id: int
    s3_key: str
    uploaded_at: str  # ISO 8601


class TelemetriaResumoResponse(BaseModel):
    """Sumário de telemetria de uma missão."""

    flight_id: str
    dt: str  # YYYY-MM-DD
    points: int
    distance_m: float
    avg_score: float
    min_battery: int
    anomaly_points: int


class AnomaliaResponse(BaseModel):
    """Ponto de telemetria com anomalia."""

    timestamp: str  # ISO 8601
    latitude: float
    longitude: float
    speed_mps: float
    battery_percent: int
    height_above_ground_m: float
    gps_satellites: int
    signal_strength_percent: int
    anomaly_reasons: str  # pipe-separated: "VELOCIDADE_EXCESSIVA|BATERIA_BAIXA"
    mission_score: int


class InsightResponse(BaseModel):
    """Resposta de insight gerado por IA."""

    missao_id: int
    insight: str
    model_id: str
    generated_at: str  # ISO 8601
