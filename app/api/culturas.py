"""API routes for Cultura CRUD — restricted to Administrador and Coordenador Operacional."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.cultura import CulturaCreate, CulturaResponse, CulturaUpdate
from app.services.cultura_service import CulturaService

router = APIRouter(
    prefix="/culturas",
    tags=["Culturas"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=CulturaResponse, status_code=201)
async def create_cultura(
    body: CulturaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new cultura."""
    service = CulturaService(db)
    return await service.create_cultura(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[CulturaResponse])
async def list_culturas(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ativo: bool | None = Query(None),
):
    """List culturas with pagination and optional ativo filter."""
    service = CulturaService(db)
    result = await service.list_culturas(
        page=page,
        page_size=page_size,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[CulturaResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{cultura_id}", response_model=CulturaResponse)
async def get_cultura(
    cultura_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a cultura by ID."""
    service = CulturaService(db)
    return await service.get_cultura(cultura_id)


@router.put("/{cultura_id}", response_model=CulturaResponse)
async def update_cultura(
    cultura_id: int,
    body: CulturaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a cultura."""
    service = CulturaService(db)
    return await service.update_cultura(cultura_id, body, usuario_id=current_user.id)


@router.patch("/{cultura_id}", response_model=CulturaResponse)
async def patch_cultura(
    cultura_id: int,
    body: CulturaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a cultura."""
    service = CulturaService(db)
    return await service.update_cultura(cultura_id, body, usuario_id=current_user.id)


@router.delete("/{cultura_id}", response_model=CulturaResponse)
async def delete_cultura(
    cultura_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a cultura (set ativo=False)."""
    service = CulturaService(db)
    return await service.delete_cultura(cultura_id, usuario_id=current_user.id)
