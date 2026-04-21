"""API routes for Propriedade CRUD — restricted to Administrador and Coordenador Operacional."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.propriedade import (
    PropriedadeCreate,
    PropriedadeResponse,
    PropriedadeUpdate,
)
from app.services.propriedade_service import PropriedadeService

router = APIRouter(
    prefix="/propriedades",
    tags=["Propriedades"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=PropriedadeResponse, status_code=201)
async def create_propriedade(
    body: PropriedadeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new property."""
    service = PropriedadeService(db)
    return await service.create_propriedade(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[PropriedadeResponse])
async def list_propriedades(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    cliente_id: int | None = Query(None),
    municipio: str | None = Query(None),
    estado: str | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List properties with pagination and optional filters."""
    service = PropriedadeService(db)
    result = await service.list_propriedades(
        page=page,
        page_size=page_size,
        cliente_id=cliente_id,
        municipio=municipio,
        estado=estado,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[PropriedadeResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{propriedade_id}", response_model=PropriedadeResponse)
async def get_propriedade(
    propriedade_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a property by ID."""
    service = PropriedadeService(db)
    return await service.get_propriedade(propriedade_id)


@router.put("/{propriedade_id}", response_model=PropriedadeResponse)
async def update_propriedade(
    propriedade_id: int,
    body: PropriedadeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a property."""
    service = PropriedadeService(db)
    return await service.update_propriedade(propriedade_id, body, usuario_id=current_user.id)


@router.patch("/{propriedade_id}", response_model=PropriedadeResponse)
async def patch_propriedade(
    propriedade_id: int,
    body: PropriedadeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a property."""
    service = PropriedadeService(db)
    return await service.update_propriedade(propriedade_id, body, usuario_id=current_user.id)


@router.delete("/{propriedade_id}", response_model=PropriedadeResponse)
async def delete_propriedade(
    propriedade_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a property (set ativo=False)."""
    service = PropriedadeService(db)
    return await service.delete_propriedade(propriedade_id, usuario_id=current_user.id)
