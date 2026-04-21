"""API routes for Talhao CRUD — restricted to Administrador and Coordenador Operacional."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.talhao import (
    TalhaoCreate,
    TalhaoResponse,
    TalhaoUpdate,
)
from app.services.talhao_service import TalhaoService

router = APIRouter(
    prefix="/talhoes",
    tags=["Talhões"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=TalhaoResponse, status_code=201)
async def create_talhao(
    body: TalhaoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new talhão."""
    service = TalhaoService(db)
    return await service.create_talhao(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[TalhaoResponse])
async def list_talhoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    propriedade_id: int | None = Query(None),
    cultura_id: int | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List talhões with pagination and optional filters."""
    service = TalhaoService(db)
    result = await service.list_talhoes(
        page=page,
        page_size=page_size,
        propriedade_id=propriedade_id,
        cultura_id=cultura_id,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[TalhaoResponse.model_validate(t) for t in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{talhao_id}", response_model=TalhaoResponse)
async def get_talhao(
    talhao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a talhão by ID."""
    service = TalhaoService(db)
    return await service.get_talhao(talhao_id)


@router.put("/{talhao_id}", response_model=TalhaoResponse)
async def update_talhao(
    talhao_id: int,
    body: TalhaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a talhão."""
    service = TalhaoService(db)
    return await service.update_talhao(talhao_id, body, usuario_id=current_user.id)


@router.patch("/{talhao_id}", response_model=TalhaoResponse)
async def patch_talhao(
    talhao_id: int,
    body: TalhaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a talhão."""
    service = TalhaoService(db)
    return await service.update_talhao(talhao_id, body, usuario_id=current_user.id)


@router.delete("/{talhao_id}", response_model=TalhaoResponse)
async def delete_talhao(
    talhao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a talhão (set ativo=False)."""
    service = TalhaoService(db)
    return await service.delete_talhao(talhao_id, usuario_id=current_user.id)
