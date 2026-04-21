"""API routes for Auditoria — restricted to Administrador."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_perfil
from app.schemas.auditoria import AuditoriaResponse
from app.schemas.base import PaginatedResponse
from app.services.auditoria_service import AuditoriaService

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR"))],
)


@router.get("", response_model=PaginatedResponse[AuditoriaResponse])
async def list_auditoria(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entidade: str | None = Query(None),
    entidade_id: int | None = Query(None),
    usuario_id: int | None = Query(None),
    data_inicio: datetime | None = Query(None),
    data_fim: datetime | None = Query(None),
):
    """List audit records with optional filters by entidade, entidade_id, usuario and period."""
    service = AuditoriaService(db)
    result = await service.list_auditoria(
        page=page,
        page_size=page_size,
        entidade=entidade,
        entidade_id=entidade_id,
        usuario_id=usuario_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return PaginatedResponse(
        items=[AuditoriaResponse.model_validate(a) for a in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )
