"""API routes for Bateria CRUD — restricted to Administrador."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import BateriaStatus
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.bateria import BateriaCreate, BateriaResponse, BateriaUpdate
from app.services.bateria_service import BateriaService

router = APIRouter(
    prefix="/baterias",
    tags=["Baterias"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR"))],
)


@router.post("", response_model=BateriaResponse, status_code=201)
async def create_bateria(
    body: BateriaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new bateria."""
    service = BateriaService(db)
    return await service.create_bateria(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[BateriaResponse])
async def list_baterias(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: BateriaStatus | None = Query(None),
    drone_id: int | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List baterias with pagination and optional filters."""
    service = BateriaService(db)
    result = await service.list_baterias(
        page=page,
        page_size=page_size,
        status=status,
        drone_id=drone_id,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[BateriaResponse.model_validate(b) for b in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{bateria_id}", response_model=BateriaResponse)
async def get_bateria(
    bateria_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a bateria by ID."""
    service = BateriaService(db)
    return await service.get_bateria(bateria_id)


@router.put("/{bateria_id}", response_model=BateriaResponse)
async def update_bateria(
    bateria_id: int,
    body: BateriaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a bateria."""
    service = BateriaService(db)
    return await service.update_bateria(bateria_id, body, usuario_id=current_user.id)


@router.patch("/{bateria_id}", response_model=BateriaResponse)
async def patch_bateria(
    bateria_id: int,
    body: BateriaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a bateria."""
    service = BateriaService(db)
    return await service.update_bateria(bateria_id, body, usuario_id=current_user.id)


@router.delete("/{bateria_id}", response_model=BateriaResponse)
async def delete_bateria(
    bateria_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a bateria (set ativo=False)."""
    service = BateriaService(db)
    return await service.delete_bateria(bateria_id, usuario_id=current_user.id)
