"""API routes for Ocorrencia registration and listing."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import Severidade
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse
from app.services.ocorrencia_service import OcorrenciaService

router = APIRouter(
    prefix="/ocorrencias",
    tags=["Ocorrências"],
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


@router.post("", response_model=OcorrenciaResponse, status_code=201)
async def create_ocorrencia(
    payload: OcorrenciaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Registrar uma nova ocorrência em uma missão."""
    service = OcorrenciaService(db)
    ocorrencia = await service.create_ocorrencia(
        missao_id=payload.missao_id,
        tipo_ocorrencia_id=payload.tipo_ocorrencia_id,
        descricao=payload.descricao,
        severidade=payload.severidade,
        registrada_por=current_user.id,
    )
    await db.commit()
    return ocorrencia


@router.get("", response_model=PaginatedResponse[OcorrenciaResponse])
async def list_ocorrencias(
    db: Annotated[AsyncSession, Depends(get_db)],
    missao_id: int | None = Query(None),
    tipo_ocorrencia_id: int | None = Query(None),
    severidade: Severidade | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Listar ocorrências com filtros opcionais e paginação."""
    service = OcorrenciaService(db)
    result = await service.list_ocorrencias(
        missao_id=missao_id,
        tipo_ocorrencia_id=tipo_ocorrencia_id,
        severidade=severidade,
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
