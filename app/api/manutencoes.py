"""API routes for Manutencao CRUD — restricted to Administrador and Técnico."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_perfil
from app.schemas.base import PaginatedResponse
from app.schemas.manutencao import ManutencaoCreate, ManutencaoResponse, ManutencaoUpdate
from app.services.manutencao_service import ManutencaoService

router = APIRouter(
    prefix="/manutencoes",
    tags=["Manutenções"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "TECNICO"))],
)


@router.post("", response_model=ManutencaoResponse, status_code=201)
async def create_manutencao(
    body: ManutencaoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new maintenance record."""
    service = ManutencaoService(db)
    return await service.create_manutencao(body)


@router.get("", response_model=PaginatedResponse[ManutencaoResponse])
async def list_manutencoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    drone_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
):
    """List maintenance records with pagination and optional filters."""
    service = ManutencaoService(db)
    result = await service.list_manutencoes(
        page=page,
        page_size=page_size,
        drone_id=drone_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return PaginatedResponse(
        items=[ManutencaoResponse.model_validate(m) for m in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{manutencao_id}", response_model=ManutencaoResponse)
async def get_manutencao(
    manutencao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a maintenance record by ID."""
    service = ManutencaoService(db)
    return await service.get_manutencao(manutencao_id)


@router.put("/{manutencao_id}", response_model=ManutencaoResponse)
async def update_manutencao(
    manutencao_id: int,
    body: ManutencaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a maintenance record."""
    service = ManutencaoService(db)
    return await service.update_manutencao(manutencao_id, body)


@router.patch("/{manutencao_id}", response_model=ManutencaoResponse)
async def patch_manutencao(
    manutencao_id: int,
    body: ManutencaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update a maintenance record."""
    service = ManutencaoService(db)
    return await service.update_manutencao(manutencao_id, body)
