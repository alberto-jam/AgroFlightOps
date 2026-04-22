"""API routes for TipoOcorrencia CRUD."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.tipo_ocorrencia import TipoOcorrenciaCreate, TipoOcorrenciaResponse, TipoOcorrenciaUpdate
from app.services.tipo_ocorrencia_service import TipoOcorrenciaService

router = APIRouter(
    prefix="/tipos-ocorrencia",
    tags=["Tipos de Ocorrência"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=TipoOcorrenciaResponse, status_code=201)
async def create(
    body: TipoOcorrenciaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = TipoOcorrenciaService(db)
    return await service.create(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[TipoOcorrenciaResponse])
async def list_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ativo: bool | None = Query(None),
):
    service = TipoOcorrenciaService(db)
    result = await service.list(page=page, page_size=page_size, ativo=ativo)
    return PaginatedResponse(
        items=[TipoOcorrenciaResponse.model_validate(t) for t in result.items],
        total=result.total, page=result.page, page_size=result.page_size, pages=result.pages,
    )


@router.get("/{tipo_id}", response_model=TipoOcorrenciaResponse)
async def get(tipo_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    service = TipoOcorrenciaService(db)
    return await service.get(tipo_id)


@router.put("/{tipo_id}", response_model=TipoOcorrenciaResponse)
async def update(
    tipo_id: int, body: TipoOcorrenciaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = TipoOcorrenciaService(db)
    return await service.update(tipo_id, body, usuario_id=current_user.id)


@router.patch("/{tipo_id}", response_model=TipoOcorrenciaResponse)
async def patch(
    tipo_id: int, body: TipoOcorrenciaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = TipoOcorrenciaService(db)
    return await service.update(tipo_id, body, usuario_id=current_user.id)


@router.delete("/{tipo_id}", response_model=TipoOcorrenciaResponse)
async def delete(
    tipo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = TipoOcorrenciaService(db)
    return await service.delete(tipo_id, usuario_id=current_user.id)
