"""API routes for Telemetria upload and query — requires authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Usuario
from app.schemas.telemetria import (
    AnomaliaResponse,
    TelemetriaResumoResponse,
    TelemetriaUploadResponse,
)
from app.services.missao_service import MissaoService
from app.services.telemetria_service import TelemetriaService

router = APIRouter(
    prefix="/missoes/{missao_id}/telemetria",
    tags=["Telemetria"],
)


@router.post("", response_model=TelemetriaUploadResponse, status_code=201)
async def upload_telemetria(
    missao_id: int,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Upload a telemetry JSON file for a mission."""
    # Validate mission exists (raises 404 if not found)
    missao_service = MissaoService(db)
    await missao_service.get_missao(missao_id)

    content = await file.read()
    telemetria_service = TelemetriaService()
    return telemetria_service.upload_telemetria(
        missao_id=missao_id,
        file_content=content,
        uploaded_by=current_user.id,
    )


@router.get("/resumo", response_model=TelemetriaResumoResponse)
async def get_resumo(
    missao_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Return the telemetry summary for a mission."""
    telemetria_service = TelemetriaService()
    return telemetria_service.get_resumo(missao_id)


@router.get("/geojson")
async def get_geojson(
    missao_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Return the GeoJSON track for a mission."""
    import json

    telemetria_service = TelemetriaService()
    geojson = telemetria_service.get_geojson(missao_id)
    return Response(
        content=json.dumps(geojson),
        media_type="application/geo+json",
    )


@router.get("/anomalias", response_model=list[AnomaliaResponse])
async def get_anomalias(
    missao_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Return anomaly points for a mission."""
    telemetria_service = TelemetriaService()
    return telemetria_service.get_anomalias(missao_id)
