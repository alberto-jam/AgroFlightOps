"""API routes for AI-powered telemetry insights — requires authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.models.models import Usuario
from app.schemas.telemetria import InsightResponse
from app.services.insights_service import BedrockError, InsightsService
from app.services.telemetria_service import TelemetriaService

router = APIRouter(
    prefix="/missoes/{missao_id}/insights",
    tags=["Insights IA"],
)


@router.get("", response_model=InsightResponse)
async def get_insights(
    missao_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Generate AI-powered insights for a mission's telemetry."""
    telemetria_service = TelemetriaService()
    insights_service = InsightsService(telemetria_service)
    try:
        return insights_service.gerar_insight(missao_id)
    except BedrockError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
