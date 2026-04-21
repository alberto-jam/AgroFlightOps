"""API routes for Insumo CRUD — restricted to Administrador and Coordenador_Operacional."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.insumo import InsumoCreate, InsumoResponse, InsumoUpdate
from app.services.insumo_service import InsumoService

router = APIRouter(
    prefix="/insumos",
    tags=["Insumos"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=InsumoResponse, status_code=201)
async def create_insumo(
    body: InsumoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new insumo."""
    service = InsumoService(db)
    return await service.create_insumo(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[InsumoResponse])
async def list_insumos(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    nome: str | None = Query(None),
    lote: str | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List insumos with pagination and optional filters."""
    service = InsumoService(db)
    result = await service.list_insumos(
        page=page,
        page_size=page_size,
        nome=nome,
        lote=lote,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[InsumoResponse.model_validate(i) for i in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get an insumo by ID."""
    service = InsumoService(db)
    return await service.get_insumo(insumo_id)


@router.put("/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_id: int,
    body: InsumoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update an insumo."""
    service = InsumoService(db)
    return await service.update_insumo(insumo_id, body, usuario_id=current_user.id)


@router.patch("/{insumo_id}", response_model=InsumoResponse)
async def patch_insumo(
    insumo_id: int,
    body: InsumoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update an insumo."""
    service = InsumoService(db)
    return await service.update_insumo(insumo_id, body, usuario_id=current_user.id)


@router.delete("/{insumo_id}", response_model=InsumoResponse)
async def delete_insumo(
    insumo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete an insumo (set ativo=False)."""
    service = InsumoService(db)
    return await service.delete_insumo(insumo_id, usuario_id=current_user.id)
