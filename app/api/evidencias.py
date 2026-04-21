"""API routes for Evidencia upload and listing."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.evidencia import EvidenciaResponse
from app.services.evidencia_service import EvidenciaService

router = APIRouter(
    prefix="/evidencias",
    tags=["Evidências"],
    dependencies=[
        Depends(
            require_perfil(
                "ADMINISTRADOR",
                "COORDENADOR_OPERACIONAL",
                "PILOTO",
                "TECNICO",
            )
        )
    ],
)


@router.post("", response_model=EvidenciaResponse, status_code=201)
async def upload_evidencia(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    file: UploadFile = File(...),
    missao_id: int = Form(...),
    latitude: Decimal | None = Form(None),
    longitude: Decimal | None = Form(None),
):
    """Upload an evidence file for a mission."""
    service = EvidenciaService(db)
    evidencia = await service.upload_evidencia(
        missao_id=missao_id,
        file=file,
        enviado_por=current_user.id,
        latitude=latitude,
        longitude=longitude,
    )
    await db.commit()
    return evidencia


@router.get("", response_model=PaginatedResponse[EvidenciaResponse])
async def list_evidencias(
    db: Annotated[AsyncSession, Depends(get_db)],
    missao_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List evidence files with optional mission filter."""
    service = EvidenciaService(db)
    result = await service.list_evidencias(
        missao_id=missao_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )
