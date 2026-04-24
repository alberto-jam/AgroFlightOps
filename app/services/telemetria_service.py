"""Business logic for Telemetria upload and query operations."""

import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.schemas.telemetria import (
    AnomaliaResponse,
    TelemetriaResumoResponse,
    TelemetriaUploadResponse,
)


class TelemetriaService:
    """Service for uploading raw telemetry and reading processed data from S3."""

    def __init__(self) -> None:
        self.s3 = boto3.client("s3")
        self.raw_bucket = os.environ.get("TELEMETRIA_RAW_BUCKET", "")
        self.processed_bucket = os.environ.get("TELEMETRIA_PROCESSED_BUCKET", "")

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload_telemetria(
        self, missao_id: int, file_content: bytes, uploaded_by: int
    ) -> TelemetriaUploadResponse:
        """Validate JSON payload and store in S3 Raw Bucket."""
        # 1. Parse JSON
        try:
            data = json.loads(file_content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BusinessRuleViolationError(
                "Erro de validação nos dados enviados",
                errors=[{"field": "file", "message": "Arquivo não é JSON válido"}],
            ) from exc

        # 2. Validate "records" field
        if not isinstance(data.get("records"), list):
            raise BusinessRuleViolationError(
                "Erro de validação nos dados enviados",
                errors=[{"field": "records", "message": "Campo 'records' obrigatório"}],
            )

        # 3. Build S3 key and upload
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y%m%dT%H%M%SZ")
        s3_key = f"incoming/{missao_id}_{ts}.json"

        self.s3.put_object(
            Bucket=self.raw_bucket,
            Key=s3_key,
            Body=file_content,
            ContentType="application/json",
            Metadata={
                "missao_id": str(missao_id),
                "uploaded_by": str(uploaded_by),
                "uploaded_at": now.isoformat(),
            },
        )

        return TelemetriaUploadResponse(
            missao_id=missao_id,
            s3_key=s3_key,
            uploaded_at=now.isoformat(),
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def _find_flight_prefix(self, missao_id: int) -> str | None:
        """Discover the ``dt=.../flight_id=...`` prefix for *missao_id*."""
        prefix = f"summary/"
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.processed_bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if f"flight_id={missao_id}/" in key:
                    # Extract dt=.../flight_id=.../
                    parts = key.split("/")
                    for i, part in enumerate(parts):
                        if part.startswith("dt="):
                            dt_part = part
                            fid_part = parts[i + 1] if i + 1 < len(parts) else None
                            if fid_part and fid_part.startswith("flight_id="):
                                return f"{dt_part}/{fid_part}"
        return None

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------

    def get_resumo(self, missao_id: int) -> TelemetriaResumoResponse:
        """Read ``summary.json`` from S3 Processed Bucket."""
        flight_prefix = self._find_flight_prefix(missao_id)
        if flight_prefix is None:
            raise EntityNotFoundError(
                f"Telemetria não encontrada para a missão {missao_id}"
            )

        key = f"summary/{flight_prefix}/summary.json"
        try:
            resp = self.s3.get_object(Bucket=self.processed_bucket, Key=key)
            body = json.loads(resp["Body"].read())
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                raise EntityNotFoundError(
                    f"Telemetria não encontrada para a missão {missao_id}"
                ) from exc
            raise

        return TelemetriaResumoResponse(**body)

    # ------------------------------------------------------------------
    # GeoJSON
    # ------------------------------------------------------------------

    def get_geojson(self, missao_id: int) -> dict:
        """Read ``track.geojson`` from S3 Processed Bucket."""
        flight_prefix = self._find_flight_prefix(missao_id)
        if flight_prefix is None:
            raise EntityNotFoundError(
                f"Telemetria não encontrada para a missão {missao_id}"
            )

        key = f"geojson/{flight_prefix}/track.geojson"
        try:
            resp = self.s3.get_object(Bucket=self.processed_bucket, Key=key)
            return json.loads(resp["Body"].read())
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                raise EntityNotFoundError(
                    f"Telemetria não encontrada para a missão {missao_id}"
                ) from exc
            raise

    # ------------------------------------------------------------------
    # Anomalias
    # ------------------------------------------------------------------

    def get_anomalias(self, missao_id: int) -> list[AnomaliaResponse]:
        """Read JSONL from S3 Processed and filter records with anomaly_count > 0."""
        flight_prefix = self._find_flight_prefix(missao_id)
        if flight_prefix is None:
            raise EntityNotFoundError(
                f"Telemetria não encontrada para a missão {missao_id}"
            )

        key = f"telemetry/{flight_prefix}/part-00000.jsonl"
        try:
            resp = self.s3.get_object(Bucket=self.processed_bucket, Key=key)
            raw = resp["Body"].read().decode("utf-8")
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                raise EntityNotFoundError(
                    f"Telemetria não encontrada para a missão {missao_id}"
                ) from exc
            raise

        anomalias: list[AnomaliaResponse] = []
        for line in raw.strip().splitlines():
            record = json.loads(line)
            if record.get("anomaly_count", 0) > 0:
                anomalias.append(
                    AnomaliaResponse(
                        timestamp=record["timestamp"],
                        latitude=record["latitude"],
                        longitude=record["longitude"],
                        speed_mps=record["speed_mps"],
                        battery_percent=record["battery_percent"],
                        height_above_ground_m=record["height_above_ground_m"],
                        gps_satellites=record["gps_satellites"],
                        signal_strength_percent=record["signal_strength_percent"],
                        anomaly_reasons=record.get("anomaly_reasons", ""),
                        mission_score=record["mission_score"],
                    )
                )

        return anomalias
